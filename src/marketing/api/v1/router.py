from fastapi import APIRouter
from .campanas.router import router as campanas_router
from ...modulos.comisiones.api.router import router as comisiones_router

router = APIRouter(prefix="/v1")

router.include_router(campanas_router, prefix="/campanas", tags=["campanas"])
router.include_router(comisiones_router, prefix="/comisiones", tags=["comisiones"])