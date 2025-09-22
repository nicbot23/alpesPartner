from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from ...modulos.servicios.campanias_service import campanias_service
from ...utils.responses import RespuestaBFF, ManejadorErroresBFF

router = APIRouter(prefix="/bff/campanias", tags=["BFF - campanias"])


# Modelos Pydantic para requests
class LanzarCampaniaCompletaRequest(BaseModel):
    """Request para lanzar una campaña completa (saga)"""
    nombre: str = Field(..., description="Nombre de la campaña")
    descripcion: str = Field(..., description="Descripción de la campaña")
    tipo: str = Field(..., description="Tipo de campaña (DESCUENTO, CASHBACK, etc.)")
    fecha_inicio: datetime = Field(..., description="Fecha de inicio de la campaña")
    fecha_fin: datetime = Field(..., description="Fecha de fin de la campaña")
    presupuesto: float = Field(..., gt=0, description="Presupuesto de la campaña")
    
    # Opciones de la saga
    buscar_afiliados_automatico: bool = Field(True, description="Buscar afiliados automáticamente")
    configurar_comisiones: bool = Field(True, description="Configurar comisiones automáticamente")
    activar_automaticamente: bool = Field(False, description="Activar la campaña automáticamente")
    enviar_notificaciones: bool = Field(True, description="Enviar notificaciones")
    
    # Criterios para búsqueda de afiliados
    criterios_afiliados: Optional[Dict[str, Any]] = Field(None, description="Criterios para selección de afiliados")
    
    # Configuración de comisiones
    tipo_comision: Optional[str] = Field("PORCENTAJE", description="Tipo de comisión")
    valor_comision: Optional[float] = Field(5.0, description="Valor de la comisión")


@router.post("/lanzar-completa", summary="Lanzar campaña completa (Saga)")
async def lanzar_campania_completa(request: LanzarCampaniaCompletaRequest) -> JSONResponse:
    """
    Endpoint principal del BFF para lanzar una campaña completa.
    
    Este endpoint inicia una saga que:
    1. Crea la campaña
    2. Busca afiliados elegibles (opcional)
    3. Configura comisiones (opcional)
    4. Activa la campaña (opcional)
    5. Envía notificaciones (opcional)
    
    Returns: Información de la saga iniciada con URLs para seguimiento
    """
    try:
        # Convertir request a dict para el servicio
        datos_campania = request.dict()
        
        # Validaciones básicas
        if request.fecha_fin <= request.fecha_inicio:
            return ManejadorErroresBFF.error_validacion(
                "fecha_fin", request.fecha_fin, "debe ser posterior a la fecha de inicio"
            )
        
        # Delegar al servicio de campanias
        resultado = await campanias_service.lanzar_campania_completa(datos_campania)
        
        if resultado.get("exito"):
            return RespuestaBFF.saga_iniciada(
                saga_id=resultado.get("comando_id"),  # Usar comando_id como identificador temporal
                campania_id=None,  # Se asignará cuando campanias procese el comando
                mensaje=resultado.get("mensaje", "Comando de campaña completa enviado exitosamente")
            )
        else:
            return RespuestaBFF.error(
                mensaje="Error al lanzar campaña completa",
                detalle=resultado.get("error", "Error desconocido")
            )
            
    except Exception as e:
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")


@router.get("/{campania_id}/estado-completo", summary="Estado completo de campaña")
async def obtener_estado_completo_campania(
    campania_id: str = Path(..., description="ID de la campaña")
) -> JSONResponse:
    """
    Obtiene el estado completo de una campaña agregando información de todos los microservicios.
    
    Incluye:
    - Información básica de la campaña
    - Afiliados asociados
    - Métricas de conversión
    - Resumen de comisiones
    """
    try:
        campania_completa = await campanias_service.obtener_campania_completa(campania_id)
        
        return RespuestaBFF.exitosa(
            datos=campania_completa,
            mensaje="Estado completo de campaña obtenido exitosamente"
        )
        
    except Exception as e:
        if "404" in str(e):
            return RespuestaBFF.error(
                mensaje="Campaña no encontrada",
                detalle=f"No se encontró la campaña con ID: {campania_id}",
                codigo_estado=404
            )
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")


@router.get("/", summary="Listar campanias con resumen")
async def listar_campanias_con_resumen(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    incluir_metricas: bool = Query(True, description="Incluir métricas de cada campaña"),
    pagina: int = Query(1, ge=1, description="Número de página"),
    tamanio_pagina: int = Query(10, ge=1, le=100, description="Tamaño de página")
) -> JSONResponse:
    """
    Lista campanias con resumen de métricas agregadas de múltiples microservicios.
    
    Permite filtrar por estado y tipo, e incluir métricas de conversión.
    """
    try:
        resultado = await campanias_service.listar_campanias_con_resumen(
            estado=estado,
            tipo=tipo,
            incluir_metricas=incluir_metricas
        )
        
        campanias = resultado.get("campanias", [])
        total = resultado.get("total", 0)
        
        # Aplicar paginación
        inicio = (pagina - 1) * tamanio_pagina
        fin = inicio + tamanio_pagina
        campanias_paginadas = campanias[inicio:fin]
        
        return RespuestaBFF.lista_paginada(
            elementos=campanias_paginadas,
            total=total,
            pagina=pagina,
            tamanio_pagina=tamanio_pagina,
            mensaje="campanias con resumen obtenidas exitosamente"
        )
        
    except Exception as e:
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")


@router.get("/dashboard", summary="Dashboard de campanias")
async def obtener_dashboard_campanias() -> JSONResponse:
    """
    Obtiene un dashboard completo con métricas agregadas de campanias.
    
    Incluye:
    - Resumen general (campanias activas, total, afiliados)
    - campanias recientes
    - Estadísticas de rendimiento
    """
    try:
        dashboard = await campanias_service.obtener_dashboard_resumen()
        
        return RespuestaBFF.dashboard(
            resumen=dashboard.get("resumen", {}),
            datos_principales={
                "campanias_recientes": dashboard.get("campanias_recientes", []),
                "timestamp": dashboard.get("timestamp")
            },
            mensaje="Dashboard obtenido exitosamente"
        )
        
    except Exception as e:
        return ManejadorErroresBFF.procesar_error_microservicio(e, "múltiples microservicios")


# Endpoints de gestión básica que delegan al microservicio
@router.put("/{campania_id}/activar", summary="Activar campaña")
async def activar_campania(
    campania_id: str = Path(..., description="ID de la campaña")
) -> JSONResponse:
    """Activa una campaña específica"""
    try:
        from ...modulos.clientes.campanias_cliente import cliente_campanias
        resultado = await cliente_campanias.activar_campania(campania_id)
        
        return RespuestaBFF.exitosa(
            datos=resultado,
            mensaje="Campaña activada exitosamente"
        )
        
    except Exception as e:
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")


@router.put("/{campania_id}/pausar", summary="Pausar campaña")
async def pausar_campania(
    campania_id: str = Path(..., description="ID de la campaña")
) -> JSONResponse:
    """Pausa una campaña específica"""
    try:
        from ...modulos.clientes.campanias_cliente import cliente_campanias
        resultado = await cliente_campanias.pausar_campania(campania_id)
        
        return RespuestaBFF.exitosa(
            datos=resultado,
            mensaje="Campaña pausada exitosamente"
        )
        
    except Exception as e:
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")


@router.put("/{campania_id}/finalizar", summary="Finalizar campaña")
async def finalizar_campania(
    campania_id: str = Path(..., description="ID de la campaña")
) -> JSONResponse:
    """Finaliza una campaña específica"""
    try:
        from ...modulos.clientes.campanias_cliente import cliente_campanias
        resultado = await cliente_campanias.finalizar_campania(campania_id)
        
        return RespuestaBFF.exitosa(
            datos=resultado,
            mensaje="Campaña finalizada exitosamente"
        )
        
    except Exception as e:
        return ManejadorErroresBFF.procesar_error_microservicio(e, "campanias")