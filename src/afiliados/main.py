"""
Microservicio de Afiliados - Arquitectura DDD
"""
import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from afiliados.config.api import config
from afiliados.api.v1.afiliados.router import router as afiliados_router
from afiliados.modulos.afiliados.infraestructura.despachadores import DespachadorEventosPulsar
from consumidores import iniciar_consumidores

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancias globales
despachador_eventos = DespachadorEventosPulsar()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🔥 Iniciando microservicio de Afiliados")
    
    try:
        # Inicializar despachador de eventos
        await despachador_eventos.start()
        
        # Inicializar consumidores de eventos
        consumidores_tareas = await iniciar_consumidores()
        
        logger.info("🚀 Microservicio de Afiliados iniciado correctamente")
        
        yield
        
    except Exception as e:
        logger.error(f"Error durante startup de Afiliados: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Deteniendo microservicio de Afiliados")
        
        try:
            # Detener despachador
            await despachador_eventos.stop()
            
        except Exception as e:
            logger.error(f"Error durante shutdown de Afiliados: {e}")

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