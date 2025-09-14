"""
Router principal v1 para el microservicio Conversiones
"""
from fastapi import APIRouter
from .conversiones.router import router as conversiones_router
from .health.router import router as health_router

router = APIRouter()

# Incluir routers específicos
router.include_router(conversiones_router, prefix="/conversiones", tags=["Conversiones"])
router.include_router(health_router, prefix="/health", tags=["Health"])