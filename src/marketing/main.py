import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config.api import config
from .api.v1.router import router as v1_router
from .consumidores import iniciar_consumidores
from .despachadores import despachador

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🔥 Iniciando servicio de marketing...")
    
    # Inicializar despachador
    await despachador.inicializar()
    
    # Iniciar consumidores de eventos
    tareas_consumidores = await iniciar_consumidores()
    
    logger.info("🚀 Servicio de marketing iniciado correctamente")
    
    yield
    
    # Shutdown
    logger.info("Cerrando servicio de marketing...")
    
    # Cancelar tareas de consumidores
    for tarea in tareas_consumidores:
        tarea.cancel()
    
    # Cerrar despachador
    await despachador.cerrar()
    
    logger.info("Servicio de marketing cerrado")


# Crear aplicación FastAPI
app = FastAPI(
    title="Servicio de Marketing",
    description="Microservicio coordinador de campañas y comisiones en AlpesPartner",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(v1_router, prefix="/api")


@app.get("/")
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "message": "Servicio de Marketing - AlpesPartner",
        "version": "1.0.0",
        "description": "Microservicio coordinador de campañas y comisiones",
        "bounded_contexts": [
            "campañas",
            "comisiones"
        ],
        "apis_disponibles": {
            "campañas": "/api/v1/campanas",
            "comisiones": "/api/v1/comisiones",
            "documentacion": "/docs",
            "health": "/health"
        },
        "arquitectura": "DDD + CQRS + Event-Driven + Enterprise Patterns"
    }


@app.get("/health")
async def health():
    """Health check detallado"""
    return {
        "status": "healthy",
        "service": "marketing",
        "version": "1.0.0",
        "bounded_contexts": {
            "campañas": "activo",
            "comisiones": "activo"
        },
        "apis": {
            "campañas": "disponible",
            "comisiones": "disponible"
        },
        "timestamp": "2023-12-15T10:30:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.app_host,
        port=config.app_port,
        reload=True
    )