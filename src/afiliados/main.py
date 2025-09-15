"""
Microservicio de Afiliados - Arquitectura DDD
"""
import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from afiliados.config.api import config
from afiliados.api.v1.afiliados.router import router as afiliados_router
from consumidores import SUSCRIPCIONES, suscribirse_a_topico
from despachadores import despachador

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando microservicio de Afiliados")
    
    # Inicializar despachador
    await despachador.inicializar()
    
    # Iniciar consumidores async
    tareas_consumidores = []
    for suscripcion in SUSCRIPCIONES:
        tarea = asyncio.create_task(
            suscribirse_a_topico(
                suscripcion['topico'],
                suscripcion['suscripcion'], 
                suscripcion['schema'],
                suscripcion['manejador']
            )
        )
        tareas_consumidores.append(tarea)
        logger.info(f"Iniciado consumidor para {suscripcion['topico']}")
    
    logger.info("Microservicio de Afiliados iniciado correctamente")
    
    yield
    
    # Shutdown
    logger.info("Deteniendo microservicio de Afiliados")
    
    # Cancelar tareas de consumidores
    for tarea in tareas_consumidores:
        tarea.cancel()
    
    # Cerrar despachador
    await despachador.cerrar()
    
    logger.info("Microservicio de Afiliados detenido")

# Crear aplicación FastAPI
app = FastAPI(
    title="Microservicio de Afiliados",
    description="Microservicio para gestionar afiliados con arquitectura DDD",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar routers
app.include_router(afiliados_router, prefix="/api/v1", tags=["afiliados"])

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Microservicio de Afiliados - Arquitectura DDD"}

@app.get("/health")
async def health():
    """Endpoint de salud"""
    return {"status": "healthy", "service": "afiliados"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.app_host,
        port=config.app_port,
        reload=False  # En producción no usar reload
    )