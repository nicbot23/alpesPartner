from fastapi import APIRouter
from .afiliados import router as afiliados_router

router = APIRouter(prefix="/v1")

router.include_router(afiliados_router, prefix="/afiliados", tags=["afiliados"])