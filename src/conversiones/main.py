"""
Microservicio de Conversiones - Arquitectura DDD
"""
import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from conversiones.config.api import settings
from conversiones.api.v1.conversiones.router import router as conversiones_router
from conversiones.consumidores import SUSCRIPCIONES, suscribirse_a_topico
from conversiones.despachadores import despachador

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando microservicio de Conversiones")
    
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
    
    logger.info("Microservicio de Conversiones iniciado correctamente")
    
    yield
    
    # Shutdown
    logger.info("Deteniendo microservicio de Conversiones")
    
    # Cancelar tareas de consumidores
    for tarea in tareas_consumidores:
        tarea.cancel()
    
    # Cerrar despachador
    await despachador.cerrar()
    
    logger.info("Microservicio de Conversiones detenido")

# Crear aplicación FastAPI
app = FastAPI(
    title="Microservicio de Conversiones",
    description="Microservicio para gestionar conversiones con arquitectura DDD",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar routers
app.include_router(conversiones_router, prefix="/api/v1", tags=["conversiones"])

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Microservicio de Conversiones - Arquitectura DDD"}

@app.get("/health")
async def health():
    """Endpoint de salud"""
    return {"status": "healthy", "service": "conversiones"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=False  # En producción no usar reload
    )