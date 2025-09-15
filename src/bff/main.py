import os
import json
import logging
from datetime import datetime
import uuid
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import pulsar

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

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://pulsar:6650")
CAMPANAS_COMMANDS_TOPIC = os.getenv("CAMPANAS_COMMANDS_TOPIC", "persistent://public/default/marketing.campanas.comandos")

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

@app.get("/health")
def health():
    return {"status": "healthy", "service": "bff", "timestamp": datetime.utcnow().isoformat()}

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

@app.on_event("shutdown")
def shutdown():
    publisher.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=False)
