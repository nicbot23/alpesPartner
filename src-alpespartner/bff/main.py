import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.api import configurar_api
from .config import config
from .api.v1.campanias import router as campanias_router
from .api.v1.sagas import router as sagas_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida del BFF
    """
    logger.info("🚀 Iniciando BFF AlpesPartner...")
    logger.info(f"📍 Configuración:")
    logger.info(f"   - Puerto: {config.puerto}")
    logger.info(f"   - URL campanias: {config.url_campanias}")
    logger.info(f"   - URL Afiliados: {config.url_afiliados}")
    logger.info(f"   - URL Comisiones: {config.url_comisiones}")
    logger.info(f"   - URL Conversiones: {config.url_conversiones}")
    logger.info(f"   - URL Notificaciones: {config.url_notificaciones}")
    logger.info(f"   - Timeout HTTP: {config.timeout_segundos}s")
    logger.info(f"   - Reintentos HTTP: {config.reintentos}")
    
    # Inicialización
    try:
        # Verificar conectividad con microservicios principales
        await verificar_microservicios()
        logger.info("✅ BFF iniciado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error al iniciar BFF: {e}")
        # No fallar el inicio, pero registrar el error
    
    yield
    
    # Limpieza al cerrar
    logger.info("🛑 Cerrando BFF AlpesPartner...")
    
    # Limpiar cache de sagas
    try:
        from .modulos.servicios.sagas_service import sagas_service
        sagas_service.limpiar_cache()
        logger.info("✅ Cache limpiado")
    except:
        pass
    
    logger.info("✅ BFF cerrado exitosamente")


async def verificar_microservicios():
    """
    Verifica la conectividad con los microservicios principales
    """
    try:
        from .modulos.clientes.campanias_cliente import cliente_campanias
        
        # Intentar una llamada simple al microservicio de campanias
        # Esto es opcional - no fallar si no está disponible
        try:
            await cliente_campanias.listar_campanias()
            logger.info("✅ Microservicio de campanias: CONECTADO")
        except Exception as e:
            logger.warning(f"⚠️ Microservicio de campanias: NO DISPONIBLE ({e})")
            
    except Exception as e:
        logger.warning(f"⚠️ Error al verificar microservicios: {e}")


# Crear aplicación FastAPI
app = configurar_api()
app.router.lifespan_context = lifespan

# Incluir routers
app.include_router(campanias_router)
app.include_router(sagas_router)


# Endpoints de salud y información
@app.get("/bff/health")
async def health_check():
    """Endpoint de salud del BFF"""
    return {
        "servicio": "AlpesPartner BFF",
        "estado": "saludable",
        "version": "1.0.0",
        "timestamp": asyncio.get_event_loop().time()
    }


@app.get("/bff/info")
async def info():
    """Información del BFF y microservicios"""
    return {
        "servicio": "AlpesPartner BFF",
        "descripcion": "Backend For Frontend - Simple orquestador para campanias",
        "version": "1.0.0",
        "arquitectura": "Enfoque A - Simple orquestador",
        "microservicios": {
            "campanias": config.url_campanias,
            "afiliados": config.url_afiliados,
            "comisiones": config.url_comisiones,
            "conversiones": config.url_conversiones,
            "notificaciones": config.url_notificaciones
        },
        "endpoints_principales": {
            "lanzar_campania_completa": "/bff/campanias/lanzar-completa",
            "estado_campania": "/bff/campanias/{id}/estado-completo",
            "estado_saga": "/bff/sagas/{saga_id}/estado",
            "progreso_saga": "/bff/sagas/{saga_id}/progreso",
            "dashboard": "/bff/campanias/dashboard"
        }
    }


@app.get("/bff")
async def root():
    """Endpoint raíz del BFF"""
    return {
        "mensaje": "Bienvenido al BFF de AlpesPartner",
        "documentacion": "/bff/docs",
        "salud": "/bff/health",
        "informacion": "/bff/info"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.puerto,
        reload=True,
        log_level="info"
    )