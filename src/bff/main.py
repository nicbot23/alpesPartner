import os
import json
import logging
from datetime import datetime
import uuid
from fastapi import FastAPI, Body, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import pulsar
import httpx
from typing import Optional
from fastapi.responses import StreamingResponse
import asyncio
import time
from starlette.responses import StreamingResponse
from fastapi import Request

MARKETING_EVENTS_TOPIC = os.getenv(
    "MARKETING_EVENTS_TOPIC",
    "persistent://public/default/marketing.eventos"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bff")

app = FastAPI(
    title="AlpesPartner BFF",
    version="1.0.0",
    description="Backend For Frontend que expone endpoints unificados y envía comandos event-driven"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# Variables de configuración
PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://pulsar:6650")
CAMPANAS_COMMANDS_TOPIC = os.getenv("CAMPANAS_COMMANDS_TOPIC", "persistent://public/default/marketing.campanas.comandos")
MARKETING_URL = os.getenv("MARKETING_URL", "http://marketing:8000")

class CommandPublisher:
    def __init__(self, url: str):
        self._url = url
        self._client = None
        self._producer_cache = {}

    def _ensure(self):
        if not self._client:
            self._client = pulsar.Client(self._url)

    def _producer(self, topic: str):
        if topic not in self._producer_cache:
            self._producer_cache[topic] = self._client.create_producer(topic)
        return self._producer_cache[topic]

    def publish(self, topic: str, message: dict):
        self._ensure()
        prod = self._producer(topic)
        prod.send(json.dumps(message).encode("utf-8"))
        logger.info(f"[BFF] Comando publicado en {topic}: {message.get('tipo')}")

    def close(self):
        if self._client:
            self._client.close()

publisher = CommandPublisher(PULSAR_URL)

def pulsar_stream(correlation_id: str):
    topics = [
        "persistent://public/default/marketing.eventos",
        "persistent://public/default/afiliados.eventos",
        "persistent://public/default/conversiones.eventos",
    ]
    client = pulsar.Client(PULSAR_URL)
    consumer = client.subscribe(
        topics=topics,
        subscription_name=f"bff-sse-{correlation_id}",
        consumer_type=pulsar.ConsumerType.Shared,
        initial_position=pulsar.InitialPosition.Latest
    )
    try:
        while True:
            try:
                msg = consumer.receive(timeout_millis=1000)
            except pulsar.Timeout:
                # keep-alive para SSE
                yield ": ping\n\n"
                continue

            raw = msg.data()
            try:
                data = json.loads(raw.decode("utf-8"))
            except Exception:
                consumer.acknowledge(msg)
                continue

            cid = (
                data.get("correlation_id")
                or data.get("metadata", {}).get("correlation_id")
                or data.get("context", {}).get("correlation_id")
            )

            if cid == correlation_id:
                yield f"data: {json.dumps(data)}\n\n"

            consumer.acknowledge(msg)
    finally:
        consumer.close()
        client.close()


@app.get("/health")
def health():
    return {"ok": True, "service": "bff", "timestamp": datetime.utcnow().isoformat()}

@app.post("/campanas", status_code=202)
def crear_campana(payload: dict = Body(...)):
    """Endpoint BFF para crear campaña: genera un comando asíncrono.
    No espera la materialización; devuelve correlation_id para seguimiento.
    """
    correlation_id = payload.get("correlation_id") or str(uuid.uuid4())

    command_message = {
        "tipo": "CrearCampanaCommand",
        "command": "CrearCampana",
        "schema_version": "1.0",
        "issued_at": datetime.utcnow().isoformat(),
        "correlation_id": correlation_id,
        "payload": {
            "nombre": payload.get("nombre", "Campaña Sin Nombre"),
            "descripcion": payload.get("descripcion", ""),
            "tipo_campana": payload.get("tipo_campana", "PROMOCIONAL"),
            "fecha_inicio": payload.get("fecha_inicio", datetime.utcnow().date().isoformat()),
            "fecha_fin": payload.get("fecha_fin", datetime.utcnow().date().isoformat()),
            "meta_conversiones": payload.get("meta_conversiones", 0),
            "presupuesto": float(payload.get("presupuesto", 0.0)),
            "comision_porcentaje": float(payload.get("comision_porcentaje", 0.05)),
            "marca": payload.get("marca", "ALPES"),
            "categoria": payload.get("categoria", "MARKETING"),
            "tags": payload.get("tags", []),
            "afiliados": payload.get("afiliados", [])
        }
    }

    publisher.publish(CAMPANAS_COMMANDS_TOPIC, command_message)

    return {
        "accepted": True,
        "correlation_id": correlation_id,
        "command": "CrearCampana",
        "tracking": {
            "events_topic": os.getenv("MARKETING_EVENTS_TOPIC", "persistent://public/default/marketing.eventos"),
            "comisiones_topic": os.getenv("COMISIONES_EVENTS_TOPIC", "persistent://public/default/marketing.comisiones.eventos")
        },
        "message": "Comando CrearCampana aceptado y publicado"
    }

@app.post("/campaigns")
async def forward_campaigns(
    request: Request,
    payload: dict = Body(...),
    x_trace_id: Optional[str] = Header(None)
):
    """
    Endpoint que reenvía la solicitud al microservicio de marketing.
    Usa un trace_id para seguimiento entre servicios.
    """
    # Generar trace_id si no se proporcionó
    trace_id = x_trace_id or str(uuid.uuid4())
    logger.info(f"[BFF] Reenviando solicitud a marketing, trace_id: {trace_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            # Preparar headers con trace_id
            headers = {"x-trace-id": trace_id}
            
            # Reenviar la petición al servicio de marketing
            response = await client.post(
                f"{MARKETING_URL}/api/v1/campanas",
                json=payload,
                headers=headers,
                timeout=10.0
            )
            
            # Devolver la respuesta del servicio de marketing
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"[BFF] Error al comunicarse con el servicio de marketing: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Error al comunicarse con el servicio de marketing: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[BFF] Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )

@app.get("/stream/{correlation_id}")
async def stream_events(correlation_id: str, request: Request):
    """
    SSE que lee eventos desde Pulsar y solo reenvía los que tengan el correlation_id indicado.
    """
    topic = os.getenv("MARKETING_EVENTS_TOPIC", "persistent://public/default/marketing.eventos")

    async def gen():
        client = pulsar.Client(os.getenv("PULSAR_URL", "pulsar://pulsar:6650"))
        consumer = client.subscribe(
            topic,
            subscription_name=f"bff-sse-{correlation_id}-{uuid.uuid4()}",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Shared,
        )
        last_ping = time.time()
        try:
            while True:
                if await request.is_disconnected():
                    break

                # intenta leer un mensaje sin bloquear el loop
                try:
                    msg = consumer.receive(timeout_millis=800)
                except pulsar.Timeout:
                    msg = None

                if msg is not None:
                    raw = msg.data().decode("utf-8")

                    # parsea JSON si puede; si no, reenvía crudo
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        data = {"raw": raw}

                    # busca correlation_id con varios nombres posibles
                    cid = (
                        data.get("correlation_id")
                        or data.get("id_correlacion")
                        or data.get("metadata", {}).get("correlation_id")
                    )

                    # siempre ACK para que no se reprocesen
                    consumer.acknowledge(msg)

                    # solo emitimos si coincide el CID
                    if cid == correlation_id:
                        yield f"data: {json.dumps(data)}\n\n"

                # mantén viva la conexión
                if time.time() - last_ping >= 10:
                    yield ": ping\n\n"
                    last_ping = time.time()

                await asyncio.sleep(0.05)
        finally:
            try:
                consumer.close()
            finally:
                client.close()

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(gen(), media_type="text/event-stream", headers=headers)

@app.get("/stream/{correlation_id}")
async def stream_events(correlation_id: str):
    """
    SSE: escucha Pulsar y envía por el stream los eventos cuyo correlation_id == {correlation_id}
    """
    async def event_generator():
        client = None
        consumer = None
        try:
            # Cliente y consumidor Pulsar
            client = pulsar.Client(PULSAR_URL)
            consumer = client.subscribe(
                MARKETING_EVENTS_TOPIC,
                subscription_name=f"bff-stream-{correlation_id}",
                consumer_type=pulsar.ConsumerType.Exclusive,
                initial_position=pulsar.InitialPosition.Latest  # escucha desde "ahora"
            )
            logger.info(f"[BFF] SSE suscrito a {MARKETING_EVENTS_TOPIC} con cid={correlation_id}")

            while True:
                try:
                    # Espera un mensaje máximo 1s; si no llega, envia ping
                    msg = consumer.receive(timeout_millis=1000)
                    raw = msg.data()
                    consumer.acknowledge(msg)

                    try:
                        evt = json.loads(raw.decode("utf-8"))
                    except Exception:
                        logger.debug("[BFF] Evento no JSON, ignorando")
                        continue

                    cid = str(evt.get("correlation_id") or evt.get("correlacion_id") or "")
                    if cid == correlation_id:
                        payload = json.dumps(evt)
                        logger.info(f"[BFF] SSE match cid={cid} tipo={evt.get('tipo')}")
                        yield f"data: {payload}\n\n"
                    # Si no coincide, lo ignoramos silenciosamente
                except Exception:
                    # Timeout u otro error “blando”: mantenemos la conexión viva
                    yield ": ping\n\n"

                await asyncio.sleep(0)  # cede control al loop

        finally:
            if consumer:
                consumer.close()
            if client:
                client.close()
            logger.info(f"[BFF] SSE cerrado cid={correlation_id}")

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.on_event("shutdown")
def shutdown():
    publisher.close()

@app.get("/stream/{correlation_id}")
def stream(correlation_id: str, x_api_key: Optional[str] = Header(None)):
    # auth simple opcional
    if os.getenv("BFF_API_KEY") and x_api_key != os.getenv("BFF_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return StreamingResponse(pulsar_stream(correlation_id), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=False)
