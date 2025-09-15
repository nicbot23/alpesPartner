"""
Router para el microservicio de afiliados con arquitectura DDD
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from .dto import (
    RegistrarAfiliadoRequest,
    AfiliadoResponse,
    AfiliadoListResponse,
    AprobarAfiliadoRequest,
    RechazarAfiliadoRequest,
    ActualizarAfiliadoRequest,
    DesactivarAfiliadoRequest,
    MessageResponse
)
from afiliados.modulos.afiliados.aplicacion.comandos import (
    RegistrarAfiliado, AprobarAfiliado, RechazarAfiliado, 
    ActualizarAfiliado, DesactivarAfiliado
)
from afiliados.modulos.afiliados.aplicacion.manejadores import (
    ManejadorRegistrarAfiliado, ManejadorAprobarAfiliado, ManejadorRechazarAfiliado,
    ManejadorActualizarAfiliado, ManejadorDesactivarAfiliado
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Instanciar manejadores
manejador_registrar = ManejadorRegistrarAfiliado()
manejador_aprobar = ManejadorAprobarAfiliado()
manejador_rechazar = ManejadorRechazarAfiliado()
manejador_actualizar = ManejadorActualizarAfiliado()
manejador_desactivar = ManejadorDesactivarAfiliado()

@router.post("", response_model=MessageResponse, status_code=201)
async def registrar_afiliado(request: RegistrarAfiliadoRequest):
    """Registrar un nuevo afiliado"""
    try:
        comando = RegistrarAfiliado(
            nombre=request.nombre,
            tipo_afiliacion=request.tipo_afiliacion,
            email=request.email,
            telefono=request.telefono,
            direccion=request.direccion
        )
        
        resultado = manejador_registrar.manejar(comando)
        
        return MessageResponse(message=resultado["message"])
        
    except Exception as e:
        logger.error(f"Error registrando afiliado: {e}")
        raise HTTPException(status_code=500, detail=f"Error registrando afiliado: {str(e)}")

@router.put("/{afiliado_id}/aprobar", response_model=MessageResponse)
async def aprobar_afiliado(
    afiliado_id: str = Path(..., description="ID del afiliado"),
    request: Optional[AprobarAfiliadoRequest] = None
):
    """Aprobar un afiliado"""
    try:
        comando = AprobarAfiliado(
            afiliado_id=afiliado_id,
            aprobado_por=request.aprobado_por if request else "sistema",
            observaciones=request.observaciones if request else ""
        )
        
        resultado = manejador_aprobar.manejar(comando)
        
        return MessageResponse(message=resultado["message"])
        
    except Exception as e:
        logger.error(f"Error aprobando afiliado: {e}")
        raise HTTPException(status_code=500, detail=f"Error aprobando afiliado: {str(e)}")

@router.put("/{afiliado_id}/rechazar", response_model=MessageResponse)
async def rechazar_afiliado(
    request: RechazarAfiliadoRequest,
    afiliado_id: str = Path(..., description="ID del afiliado")
):
    """Rechazar un afiliado"""
    try:
        comando = RechazarAfiliado(
            afiliado_id=afiliado_id,
            rechazado_por=request.rechazado_por,
            razon_rechazo=request.razon_rechazo
        )
        
        resultado = manejador_rechazar.manejar(comando)
        
        return MessageResponse(message=resultado["message"])
        
    except Exception as e:
        logger.error(f"Error rechazando afiliado: {e}")
        raise HTTPException(status_code=500, detail=f"Error rechazando afiliado: {str(e)}")

@router.put("/{afiliado_id}", response_model=MessageResponse)
async def actualizar_afiliado(
    request: ActualizarAfiliadoRequest,
    afiliado_id: str = Path(..., description="ID del afiliado")
):
    """Actualizar datos de un afiliado"""
    try:
        comando = ActualizarAfiliado(
            afiliado_id=afiliado_id,
            actualizado_por=request.actualizado_por,
            nombre=request.nombre,
            telefono=request.telefono,
            direccion=request.direccion,
            observaciones=request.observaciones
        )
        
        resultado = manejador_actualizar.manejar(comando)
        
        return MessageResponse(message=resultado["message"])
        
    except Exception as e:
        logger.error(f"Error actualizando afiliado: {e}")
        raise HTTPException(status_code=500, detail=f"Error actualizando afiliado: {str(e)}")

@router.delete("/{afiliado_id}", response_model=MessageResponse)
async def desactivar_afiliado(
    request: DesactivarAfiliadoRequest,
    afiliado_id: str = Path(..., description="ID del afiliado")
):
    """Desactivar un afiliado"""
    try:
        comando = DesactivarAfiliado(
            afiliado_id=afiliado_id,
            desactivado_por=request.desactivado_por,
            razon_desactivacion=request.razon_desactivacion
        )
        
        resultado = manejador_desactivar.manejar(comando)
        
        return MessageResponse(message=resultado["message"])
        
    except Exception as e:
        logger.error(f"Error desactivando afiliado: {e}")
        raise HTTPException(status_code=500, detail=f"Error desactivando afiliado: {str(e)}")

@router.get("", response_model=AfiliadoListResponse)
async def listar_afiliados(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    email: Optional[str] = Query(None, description="Filtrar por email"),
    estado: Optional[str] = Query(None, description="Filtrar por estado")
):
    """Listar afiliados con paginación y filtros"""
    try:
        # Aquí se implementaría la consulta real con repositorio
        # Por ahora retornamos una lista vacía
        afiliados = []
        
        return AfiliadoListResponse(
            afiliados=afiliados,
            total=0,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"Error listando afiliados: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando afiliados: {str(e)}")

@router.get("/{afiliado_id}", response_model=AfiliadoResponse)
async def obtener_afiliado(afiliado_id: str = Path(..., description="ID del afiliado")):
    """Obtener un afiliado por ID"""
    try:
        # Aquí se implementaría la consulta real con repositorio
        # Por ahora simulamos que no existe
        raise HTTPException(status_code=404, detail="Afiliado no encontrado")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo afiliado: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo afiliado: {str(e)}")