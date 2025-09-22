# afiliados/main.py
from fastapi import FastAPI
import asyncio
import os

from afiliados.consumidores import suscribirse_a_topico

app = FastAPI(title="Afiliados", version="1.0.0")

TOPICO = os.getenv("AFILIADOS_TOPICO", "comando-buscar-afiliados-elegibles")
SUSCRIPCION = os.getenv("AFILIADOS_SUBSCRIPCION", "afiliados-buscar-elegibles")
PULSAR_HOST = os.getenv("PULSAR_BROKER", "broker")

@app.get("/health")
def health():
    return {"status": "ok", "topic": TOPICO, "broker": PULSAR_HOST}

@app.on_event("startup")
async def on_startup():
    # lanza el consumidor en background
    app.state.consumer_task = asyncio.create_task(
        suscribirse_a_topico(
            topico=TOPICO,
            suscripcion=SUSCRIPCION,
            pulsar_host=PULSAR_HOST,
        )
    )

@app.on_event("shutdown")
async def on_shutdown():
    task = getattr(app.state, "consumer_task", None)
    if task:
        task.cancel()
        try:
            await task
        except Exception:
            pass
