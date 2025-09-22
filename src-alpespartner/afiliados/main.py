# afiliados/main.py
from fastapi import FastAPI
import asyncio
import os

from afiliados.consumidores import suscribirse_a_topico

app = FastAPI(title="Afiliados", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    """
    Arranca el consumidor principal de Afiliados.
    Lee el comando 'comando-buscar-afiliados-elegibles'
    que publica Campañas/Despachador.
    """
    pulsar_host = os.getenv("PULSAR_HOST", "broker")
    topico_comando = os.getenv(
        "TOPICO_COMANDO_AFILIADOS", "comando-buscar-afiliados-elegibles"
    )

    # El consumidor corre en background para no bloquear FastAPI
    asyncio.create_task(
        suscribirse_a_topico(
            topico=topico_comando,
            suscripcion="afiliados-sub",
            pulsar_host=pulsar_host,
        )
    )
