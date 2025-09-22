from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel, Field

from ...modulos.servicios.sagas_service import sagas_service
from ...utils.responses import RespuestaBFF, ManejadorErroresBFF

router = APIRouter(prefix="/bff/sagas", tags=["BFF - Sagas"])


class CancelarSagaRequest(BaseModel):
    """Request para cancelar una saga"""
    razon: Optional[str] = Field(None, description="Razón de la cancelación")


@router.get("/{saga_id}/estado", summary="Estado de saga")
async def obtener_estado_saga(
    saga_id: str = Path(..., description="ID de la saga"),
    usar_cache: bool = Query(True, description="Usar cache para mejorar rendimiento")
) -> JSONResponse:
    """
    Obtiene el estado actual de una saga.
    
    El estado puede ser:
    - INICIADA: La saga ha comenzado
    - EN_PROGRESO: La saga está ejecutándose
    - COMPLETADA: La saga terminó exitosamente
    - FALLIDA: La saga falló
    - CANCELADA: La saga fue cancelada
    """
    try:
        estado = await sagas_service.obtener_estado_saga(saga_id, usar_cache=usar_cache)
        
        return RespuestaBFF.saga_estado(
            saga_id=saga_id,
            estado=estado.get("estado", "DESCONOCIDO"),
            progreso=estado.get("progreso_porcentaje"),
            detalles=estado
        )
        
    except Exception as e:
        if "404" in str(e) or "no encontrada" in str(e).lower():
            return ManejadorErroresBFF.error_saga_no_encontrada(saga_id)
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")


@router.get("/{saga_id}/progreso", summary="Progreso detallado de saga")
async def obtener_progreso_saga(
    saga_id: str = Path(..., description="ID de la saga")
) -> JSONResponse:
    """
    Obtiene el progreso detallado de una saga con información de cada paso.
    
    Incluye:
    - Lista de pasos de la saga
    - Tiempo transcurrido por paso
    - Porcentaje de completitud
    - Tiempo estimado restante
    """
    try:
        progreso = await sagas_service.obtener_progreso_detallado(saga_id)
        
        return RespuestaBFF.exitosa(
            datos=progreso,
            mensaje="Progreso de saga obtenido exitosamente"
        )
        
    except Exception as e:
        if "404" in str(e) or "no encontrada" in str(e).lower():
            return ManejadorErroresBFF.error_saga_no_encontrada(saga_id)
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")


@router.post("/{saga_id}/cancelar", summary="Cancelar saga")
async def cancelar_saga(
    saga_id: str = Path(..., description="ID de la saga"),
    request: CancelarSagaRequest = CancelarSagaRequest()
) -> JSONResponse:
    """
    Cancela una saga en progreso.
    
    La cancelación iniciará el proceso de compensación para deshacer
    los cambios realizados hasta el momento.
    """
    try:
        resultado = await sagas_service.cancelar_saga(saga_id, request.razon)
        
        if resultado.get("exito"):
            return RespuestaBFF.exitosa(
                datos=resultado,
                mensaje="Saga cancelada exitosamente"
            )
        else:
            return RespuestaBFF.error(
                mensaje="Error al cancelar saga",
                detalle=resultado.get("error", "Error desconocido")
            )
            
    except Exception as e:
        if "404" in str(e) or "no encontrada" in str(e).lower():
            return ManejadorErroresBFF.error_saga_no_encontrada(saga_id)
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")


@router.get("/", summary="Listar sagas activas")
async def listar_sagas_activas(
    pagina: int = Query(1, ge=1, description="Número de página"),
    tamanio_pagina: int = Query(10, ge=1, le=100, description="Tamaño de página")
) -> JSONResponse:
    """
    Lista todas las sagas activas en el sistema.
    
    Útil para monitoreo y administración de sagas en progreso.
    """
    try:
        resultado = await sagas_service.listar_sagas_activas()
        
        sagas = resultado.get("sagas", [])
        total = resultado.get("total", 0)
        
        # Aplicar paginación
        inicio = (pagina - 1) * tamanio_pagina
        fin = inicio + tamanio_pagina
        sagas_paginadas = sagas[inicio:fin]
        
        return RespuestaBFF.lista_paginada(
            elementos=sagas_paginadas,
            total=total,
            pagina=pagina,
            tamanio_pagina=tamanio_pagina,
            mensaje="Sagas activas obtenidas exitosamente"
        )
        
    except Exception as e:
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")


@router.get("/{saga_id}/monitorear", summary="Monitorear saga hasta completación")
async def monitorear_saga(
    saga_id: str = Path(..., description="ID de la saga"),
    timeout_segundos: int = Query(300, ge=30, le=600, description="Timeout en segundos")
) -> JSONResponse:
    """
    Monitorea una saga hasta su completación o timeout.
    
    Este endpoint mantiene la conexión hasta que la saga termine
    o se alcance el timeout. Útil para casos donde el frontend
    necesita esperar el resultado completo.
    
    ⚠️ ADVERTENCIA: Este endpoint puede tomar varios minutos en responder.
    """
    try:
        resultado = await sagas_service.monitorear_saga(
            saga_id=saga_id,
            timeout_segundos=timeout_segundos
        )
        
        if resultado.get("exito"):
            return RespuestaBFF.exitosa(
                datos=resultado,
                mensaje=f"Saga completada: {resultado.get('estado_final')}"
            )
        else:
            return RespuestaBFF.error(
                mensaje=f"Saga no completada: {resultado.get('estado_final')}",
                detalle=resultado.get("mensaje", "Error desconocido"),
                datos_adicionales=resultado
            )
            
    except Exception as e:
        if "404" in str(e) or "no encontrada" in str(e).lower():
            return ManejadorErroresBFF.error_saga_no_encontrada(saga_id)
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")


@router.delete("/cache", summary="Limpiar cache de sagas")
async def limpiar_cache_sagas() -> JSONResponse:
    """
    Limpia el cache de estados de saga.
    
    Útil para forzar la obtención de estados frescos desde
    el microservicio de campanias.
    """
    try:
        sagas_service.limpiar_cache()
        
        return RespuestaBFF.exitosa(
            datos={"cache_limpiado": True},
            mensaje="Cache de sagas limpiado exitosamente"
        )
        
    except Exception as e:
        return RespuestaBFF.error(
            mensaje="Error al limpiar cache",
            detalle=str(e)
        )