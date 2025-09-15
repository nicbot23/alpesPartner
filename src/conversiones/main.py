"""
Microservicio de Conversiones - Arquitectura DDD
"""
import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from conversiones.config.api import settings
from conversiones.api.v1.conversiones.router import router as conversiones_router
from conversiones.modulos.conversiones.infraestructura.despachadores import DespachadorEventosPulsar
from consumidores import ConversionsEventConsumer
from despachadores import EventDispatcher

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancias globales
despachador_eventos = DespachadorEventosPulsar()
event_dispatcher = EventDispatcher()
event_consumer = ConversionsEventConsumer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando microservicio de Conversiones")
    
    try:
        # Inicializar despachador de eventos
        await despachador_eventos.start()
        
        # Inicializar consumer de eventos
        await event_consumer.start()
        
        # Inicializar dispatcher de eventos
        await event_dispatcher.start()
        
        logger.info("Microservicio de Conversiones iniciado correctamente")
        
    except Exception as e:
        logger.error(f"Error al iniciar microservicio: {e}")
    
    yield
    
    # Shutdown
    logger.info("Deteniendo microservicio de Conversiones")
    
    try:
        await despachador_eventos.stop()
        await event_consumer.stop()
        await event_dispatcher.stop()
    except Exception as e:
        logger.error(f"Error al detener microservicio: {e}")
    
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