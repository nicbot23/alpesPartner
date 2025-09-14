"""
Router para health check
"""
from fastapi import APIRouter
from conversiones.config import settings
from conversiones.utils import time_millis

router = APIRouter()

@router.get("/")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "service": "conversiones",
        "version": settings.APP_VERSION,
        "timestamp": time_millis()
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check"""
    return {
        "status": "ready",
        "service": "conversiones",
        "database": "connected",  # TODO: verificar conexión real
        "pulsar": "connected",    # TODO: verificar conexión real
        "timestamp": time_millis()
    }

@router.get("/live")
async def liveness_check():
    """Liveness check"""
    return {
        "status": "alive",
        "service": "conversiones",
        "timestamp": time_millis()
    }