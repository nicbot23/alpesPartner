from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from .dto import (
    CampanaCrear,
    CampanaActualizar,
    CampanaResponse,
    CampanaListResponse,
    ActivarCampanaRequest,
    ComisionResponse,
    ComisionListResponse,
    EstadisticasCampanaResponse,
    MessageResponse
)
from ....utils import generar_uuid, time_millis, validar_fechas_campana
from ....comandos import ComandoCrearCampana, ComandoActivarCampana, ComandoDesactivarCampana
from ....despachadores import despachador

router = APIRouter()


@router.post("", response_model=MessageResponse, status_code=201)
async def crear_campana(campana: CampanaCrear):
    """Crear una nueva campaña de marketing"""
    try:
        # Validar fechas
        if not validar_fechas_campana(campana.fecha_inicio, campana.fecha_fin):
            raise HTTPException(status_code=400, detail="Fechas de campaña inválidas")
        
        comando_id = generar_uuid()
        comando = ComandoCrearCampana(
            id=comando_id,
            nombre=campana.nombre,
            descripcion=campana.descripcion,
            tipo_campana=campana.tipo_campana,
            fecha_inicio=campana.fecha_inicio,
            fecha_fin=campana.fecha_fin,
            meta_conversiones=campana.meta_conversiones,
            presupuesto=campana.presupuesto,
            created_by=campana.created_by,
            timestamp=time_millis()
        )
        
        await despachador.publicar_mensaje('comandos-crear-campana', comando, ComandoCrearCampana)
        
        return MessageResponse(message=f"Comando de creación de campaña enviado con ID: {comando_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando campaña: {str(e)}")


@router.get("", response_model=CampanaListResponse)
async def listar_campanas(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    tipo_campana: Optional[str] = Query(None, description="Filtrar por tipo"),
    created_by: Optional[str] = Query(None, description="Filtrar por creador")
):
    """Listar campañas con paginación y filtros"""
    try:
        # Implementar lógica de consulta real
        # Por ahora retornamos lista vacía
        return CampanaListResponse(
            campanas=[],
            total=0,
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando campañas: {str(e)}")


@router.get("/{campana_id}", response_model=CampanaResponse)
async def obtener_campana(
    campana_id: str = Path(..., description="ID de la campaña")
):
    """Obtener campaña por ID"""
    try:
        # Implementar lógica de consulta real
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo campaña: {str(e)}")


@router.put("/{campana_id}", response_model=MessageResponse)
async def actualizar_campana(
    campana_id: str = Path(..., description="ID de la campaña"),
    campana: CampanaActualizar = None
):
    """Actualizar datos de una campaña"""
    try:
        # En un caso real, aquí se actualizaría la base de datos
        # y se emitiría un evento de campaña actualizada
        return MessageResponse(message=f"Campaña {campana_id} actualizada")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando campaña: {str(e)}")


@router.post("/{campana_id}/activar", response_model=MessageResponse)
async def activar_campana(
    campana_id: str = Path(..., description="ID de la campaña"),
    request: ActivarCampanaRequest = None
):
    """Activar una campaña"""
    try:
        comando_id = generar_uuid()
        comando = ComandoActivarCampana(
            id=comando_id,
            campana_id=campana_id,
            criterios_segmentacion=request.criterios_segmentacion if request else "{}",
            timestamp=time_millis()
        )
        
        await despachador.publicar_mensaje('comandos-activar-campana', comando, ComandoActivarCampana)
        
        return MessageResponse(message=f"Comando de activación enviado con ID: {comando_id}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error activando campaña: {str(e)}")


@router.post("/{campana_id}/desactivar", response_model=MessageResponse)
async def desactivar_campana(
    campana_id: str = Path(..., description="ID de la campaña"),
    razon: str = Query("", description="Razón de desactivación")
):
    """Desactivar una campaña"""
    try:
        comando_id = generar_uuid()
        comando = ComandoDesactivarCampana(
            id=comando_id,
            campana_id=campana_id,
            razon=razon or "Sin razón especificada",
            timestamp=time_millis()
        )
        
        await despachador.publicar_mensaje('comandos-desactivar-campana', comando, ComandoDesactivarCampana)
        
        return MessageResponse(message=f"Comando de desactivación enviado con ID: {comando_id}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error desactivando campaña: {str(e)}")


@router.get("/{campana_id}/comisiones", response_model=ComisionListResponse)
async def listar_comisiones_campana(
    campana_id: str = Path(..., description="ID de la campaña"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página")
):
    """Listar comisiones de una campaña"""
    try:
        # Implementar lógica de consulta real
        return ComisionListResponse(
            comisiones=[],
            total=0,
            total_monto=0.0,
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando comisiones: {str(e)}")


@router.get("/{campana_id}/estadisticas", response_model=EstadisticasCampanaResponse)
async def obtener_estadisticas_campana(
    campana_id: str = Path(..., description="ID de la campaña")
):
    """Obtener estadísticas de una campaña"""
    try:
        # Implementar lógica de consulta real
        return EstadisticasCampanaResponse(
            campana_id=campana_id,
            total_conversiones=0,
            total_comisiones=0.0,
            valor_total_conversiones=0.0,
            afiliados_participantes=0,
            tasa_conversion=0.0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@router.get("/health", response_model=MessageResponse)
async def health_check():
    """Health check del servicio de marketing"""
    return MessageResponse(message="Servicio de marketing funcionando correctamente")