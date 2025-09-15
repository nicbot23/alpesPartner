"""
APIs REST del módulo de comisiones - Marketing Microservice
Implementación FastAPI con documentación OpenAPI y validaciones Pydantic
Arquitectura: REST + OpenAPI + Dependency Injection + Error Handling
"""

from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator, ConfigDict
from pydantic.types import UUID4

from ..dominio.entidades import EstadoComision, TipoComision
from ..aplicacion.comandos import *
from ..aplicacion.consultas import *
from ..aplicacion.servicios import CoordinadorComisiones, ExcepcionAplicacion
from ..infraestructura.configuracion import ConfiguracionGlobal

# =============================================================================
# MODELOS PYDANTIC - REQUEST/RESPONSE
# =============================================================================

class EstadoComisionAPI(str, Enum):
    """Estados de comisión para API"""
    PENDIENTE = "pendiente"
    CALCULADA = "calculada"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    PAGADA = "pagada"
    ANULADA = "anulada"

class TipoComisionAPI(str, Enum):
    """Tipos de comisión para API"""
    FIJA = "fija"
    PORCENTUAL = "porcentual"
    ESCALONADA = "escalonada"
    MIXTA = "mixta"

class MontoMonetarioAPI(BaseModel):
    """Modelo para montos monetarios"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "valor": 50000.00,
                "moneda": "COP"
            }
        }
    )
    
    valor: Decimal = Field(..., ge=0, description="Valor del monto")
    moneda: str = Field(..., min_length=3, max_length=3, description="Código de moneda ISO")

# =============================================================================
# REQUEST MODELS - ENTRADA DE DATOS
# =============================================================================

class CrearComisionRequest(BaseModel):
    """Request para crear nueva comisión"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "afiliado_id": "123e4567-e89b-12d3-a456-426614174000",
                "campana_id": "987fcdeb-51a2-43d5-9c7e-123456789abc",
                "conversion_id": "456789ab-cdef-1234-5678-90abcdef1234",
                "monto_base": {
                    "valor": 100000.00,
                    "moneda": "COP"
                },
                "tipo_comision": "porcentual",
                "porcentaje": 15.5,
                "configuracion": {
                    "aplicar_descuentos": True,
                    "incluir_iva": False
                },
                "metadatos": {
                    "canal_origen": "web",
                    "categoria_producto": "premium"
                }
            }
        }
    )
    
    afiliado_id: UUID4 = Field(..., description="ID del afiliado")
    campana_id: UUID4 = Field(..., description="ID de la campaña")
    conversion_id: UUID4 = Field(..., description="ID de la conversión")
    monto_base: MontoMonetarioAPI = Field(..., description="Monto base para cálculo")
    tipo_comision: TipoComisionAPI = Field(..., description="Tipo de comisión")
    porcentaje: Optional[Decimal] = Field(None, ge=0, le=100, description="Porcentaje para comisión porcentual")
    configuracion: Optional[Dict[str, Any]] = Field(None, description="Configuración personalizada")
    metadatos: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    
    @validator('porcentaje')
    def validar_porcentaje_requerido(cls, v, values):
        """Validar que porcentaje sea requerido para comisión porcentual"""
        if values.get('tipo_comision') == TipoComisionAPI.PORCENTUAL and v is None:
            raise ValueError('Porcentaje es requerido para comisión porcentual')
        return v

class ActualizarComisionRequest(BaseModel):
    """Request para actualizar comisión"""
    monto_base: Optional[MontoMonetarioAPI] = Field(None, description="Nuevo monto base")
    porcentaje: Optional[Decimal] = Field(None, ge=0, le=100, description="Nuevo porcentaje")
    configuracion: Optional[Dict[str, Any]] = Field(None, description="Nueva configuración")
    metadatos: Optional[Dict[str, Any]] = Field(None, description="Nuevos metadatos")
    motivo_actualizacion: str = Field(..., min_length=5, description="Motivo de la actualización")

class AprobarComisionRequest(BaseModel):
    """Request para aprobar comisión"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "comentarios": "Comisión aprobada según criterios establecidos",
                "metadatos_aprobacion": {
                    "nivel_aprobacion": "supervisor",
                    "politica_aplicada": "estandar"
                }
            }
        }
    )
    
    comentarios: Optional[str] = Field(None, description="Comentarios de aprobación")
    metadatos_aprobacion: Optional[Dict[str, Any]] = Field(None, description="Metadatos de aprobación")

class RechazarComisionRequest(BaseModel):
    """Request para rechazar comisión"""
    motivo_rechazo: str = Field(..., min_length=5, description="Motivo del rechazo")
    comentarios: Optional[str] = Field(None, description="Comentarios adicionales")
    metadatos_rechazo: Optional[Dict[str, Any]] = Field(None, description="Metadatos de rechazo")

class PagarComisionRequest(BaseModel):
    """Request para marcar comisión como pagada"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metodo_pago": "transferencia_bancaria",
                "referencia_pago": "TXN-202312-001234",
                "monto_pagado": {
                    "valor": 15750.00,
                    "moneda": "COP"
                },
                "metadatos_pago": {
                    "banco": "Banco Nacional",
                    "cuenta_destino": "*****1234"
                }
            }
        }
    )
    
    metodo_pago: str = Field(..., min_length=3, description="Método de pago utilizado")
    referencia_pago: str = Field(..., min_length=5, description="Referencia del pago")
    fecha_pago: Optional[datetime] = Field(None, description="Fecha del pago")
    monto_pagado: Optional[MontoMonetarioAPI] = Field(None, description="Monto realmente pagado")
    metadatos_pago: Optional[Dict[str, Any]] = Field(None, description="Metadatos del pago")

# =============================================================================
# RESPONSE MODELS - SALIDA DE DATOS
# =============================================================================

class ComisionResponse(BaseModel):
    """Response completo de comisión"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "afiliado_id": "987fcdeb-51a2-43d5-9c7e-123456789abc",
                "campana_id": "456789ab-cdef-1234-5678-90abcdef1234",
                "conversion_id": "789abcde-f123-4567-890a-bcdef1234567",
                "estado": "aprobada",
                "tipo_comision": "porcentual",
                "monto_base": {
                    "valor": 100000.00,
                    "moneda": "COP"
                },
                "porcentaje": 15.5,
                "monto_calculado": {
                    "valor": 15500.00,
                    "moneda": "COP"
                },
                "fecha_creacion": "2023-12-15T10:30:00Z",
                "fecha_calculo": "2023-12-15T10:31:00Z",
                "fecha_aprobacion": "2023-12-15T14:20:00Z",
                "aprobador_id": "admin-001",
                "comentarios": "Aprobada automáticamente"
            }
        }
    )
    
    id: UUID4
    afiliado_id: UUID4
    campana_id: UUID4
    conversion_id: UUID4
    estado: EstadoComisionAPI
    tipo_comision: TipoComisionAPI
    monto_base: MontoMonetarioAPI
    porcentaje: Optional[Decimal]
    monto_calculado: Optional[MontoMonetarioAPI]
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_calculo: Optional[datetime]
    fecha_aprobacion: Optional[datetime]
    fecha_pago: Optional[datetime]
    aprobador_id: Optional[str]
    comentarios: Optional[str]
    metadatos: Optional[Dict[str, Any]]

class ComisionResumenResponse(BaseModel):
    """Response resumido de comisión para listados"""
    id: UUID4
    afiliado_id: UUID4
    campana_id: UUID4
    estado: EstadoComisionAPI
    monto_calculado: Optional[MontoMonetarioAPI]
    fecha_creacion: datetime
    fecha_calculo: Optional[datetime]

class CrearComisionResponse(BaseModel):
    """Response de creación de comisión"""
    comision_id: UUID4 = Field(..., description="ID de la comisión creada")
    estado: EstadoComisionAPI = Field(..., description="Estado inicial")
    monto_calculado: Optional[MontoMonetarioAPI] = Field(None, description="Monto calculado si está disponible")
    mensaje: str = Field(..., description="Mensaje de resultado")
    eventos_generados: List[str] = Field(..., description="Eventos generados")

class ResultadoPaginadoResponse(BaseModel):
    """Response paginado genérico"""
    elementos: List[Any] = Field(..., description="Elementos de la página actual")
    total_elementos: int = Field(..., description="Total de elementos")
    pagina_actual: int = Field(..., description="Página actual")
    tamaño_pagina: int = Field(..., description="Tamaño de página")
    total_paginas: int = Field(..., description="Total de páginas")
    tiene_anterior: bool = Field(..., description="Tiene página anterior")
    tiene_siguiente: bool = Field(..., description="Tiene página siguiente")

class EstadisticasComisionResponse(BaseModel):
    """Response de estadísticas de comisiones"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_comisiones": 1250,
                "total_pendientes": 45,
                "total_calculadas": 120,
                "total_aprobadas": 980,
                "total_pagadas": 850,
                "monto_total_calculado": {
                    "valor": 15750000.00,
                    "moneda": "COP"
                },
                "monto_total_aprobado": {
                    "valor": 14200000.00,
                    "moneda": "COP"
                },
                "promedio_tiempo_aprobacion_dias": 2.3
            }
        }
    )
    
    total_comisiones: int
    total_pendientes: int
    total_calculadas: int
    total_aprobadas: int
    total_rechazadas: int
    total_pagadas: int
    monto_total_calculado: MontoMonetarioAPI
    monto_total_aprobado: MontoMonetarioAPI
    monto_total_pagado: MontoMonetarioAPI
    fecha_ultimo_calculo: Optional[datetime]
    promedio_tiempo_aprobacion_dias: Optional[float]

class ErrorResponse(BaseModel):
    """Response de error estándar"""
    error: str = Field(..., description="Tipo de error")
    mensaje: str = Field(..., description="Mensaje descriptivo")
    detalles: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID de la request")

# =============================================================================
# PARÁMETROS DE CONSULTA
# =============================================================================

class ParametrosPaginacion(BaseModel):
    """Parámetros de paginación para consultas"""
    pagina: int = Field(1, ge=1, description="Número de página")
    tamaño: int = Field(20, ge=1, le=1000, description="Elementos por página")

class ParametrosFiltroComision(BaseModel):
    """Parámetros de filtro para comisiones"""
    estados: Optional[List[EstadoComisionAPI]] = None
    tipos: Optional[List[TipoComisionAPI]] = None
    afiliados_ids: Optional[List[UUID4]] = None
    campanas_ids: Optional[List[UUID4]] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    monto_minimo: Optional[Decimal] = Field(None, ge=0)
    monto_maximo: Optional[Decimal] = Field(None, ge=0)

# =============================================================================
# DEPENDENCIAS - DEPENDENCY INJECTION
# =============================================================================

async def obtener_coordinador_comisiones() -> CoordinadorComisiones:
    """Dependency para obtener coordinador de comisiones"""
    # En implementación real, esto vendría del container de DI
    # Por ahora, mock para completar la estructura
    from ..infraestructura.repositorios import FabricaInfraestructuraComisiones
    from ..aplicacion.servicios import FabricaServiciosComisiones
    from ..dominio.entidades import CalculadorComision, ValidadorComision
    
    # Mock para este ejemplo
    class MockRepositorio:
        pass
    
    class MockCalculador:
        pass
    
    class MockValidador:
        pass
    
    return None  # En producción retornaría el coordinador real

async def obtener_usuario_actual() -> str:
    """Dependency para obtener usuario actual"""
    # En implementación real, extraería del token JWT
    return "sistema"

async def validar_permisos_comision(accion: str, usuario: str = Depends(obtener_usuario_actual)) -> bool:
    """Dependency para validar permisos de usuario"""
    # En implementación real, validaría permisos específicos
    return True

# =============================================================================
# ROUTER PRINCIPAL - ENDPOINTS
# =============================================================================

router = APIRouter(
    prefix="/comisiones",
    tags=["Comisiones"],
    responses={
        400: {"model": ErrorResponse, "description": "Error de validación"},
        401: {"model": ErrorResponse, "description": "No autorizado"},
        403: {"model": ErrorResponse, "description": "Permisos insuficientes"},
        404: {"model": ErrorResponse, "description": "Recurso no encontrado"},
        500: {"model": ErrorResponse, "description": "Error interno"}
    }
)

# =============================================================================
# ENDPOINTS DE COMANDOS (ESCRITURA)
# =============================================================================

@router.post(
    "/",
    response_model=CrearComisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva comisión",
    description="Crea una nueva comisión para un afiliado basada en una conversión",
    response_description="Comisión creada exitosamente"
)
async def crear_comision(
    request: CrearComisionRequest,
    coordinador: CoordinadorComisiones = Depends(obtener_coordinador_comisiones),
    usuario: str = Depends(obtener_usuario_actual),
    _: bool = Depends(lambda: validar_permisos_comision("crear"))
) -> CrearComisionResponse:
    """
    Crear una nueva comisión:
    
    - **afiliado_id**: ID del afiliado que generó la conversión
    - **campana_id**: ID de la campaña asociada
    - **conversion_id**: ID único de la conversión
    - **monto_base**: Monto base para el cálculo de comisión
    - **tipo_comision**: Tipo de comisión (fija, porcentual, escalonada, mixta)
    - **porcentaje**: Porcentaje para comisiones porcentuales
    - **configuracion**: Configuración personalizada de cálculo
    - **metadatos**: Información adicional contextual
    """
    try:
        # Crear comando
        comando = CrearComision(
            afiliado_id=str(request.afiliado_id),
            campana_id=str(request.campana_id),
            conversion_id=str(request.conversion_id),
            monto_base=request.monto_base.valor,
            moneda=request.monto_base.moneda,
            tipo_comision=TipoComision(request.tipo_comision.value),
            porcentaje=request.porcentaje,
            configuracion=request.configuracion,
            metadatos=request.metadatos,
            usuario_id=usuario
        )
        
        # Ejecutar caso de uso
        resultado = coordinador.crear_comision(comando)
        
        # Convertir respuesta
        response = CrearComisionResponse(
            comision_id=resultado.comision_id,
            estado=EstadoComisionAPI(resultado.estado.value),
            monto_calculado=MontoMonetarioAPI(
                valor=resultado.monto_calculado.valor,
                moneda=resultado.monto_calculado.moneda
            ) if resultado.monto_calculado else None,
            mensaje=resultado.mensaje,
            eventos_generados=resultado.eventos_generados
        )
        
        return response
        
    except ExcepcionAplicacion as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error="ValidationError",
                mensaje=str(ex)
            ).model_dump()
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="InternalError",
                mensaje="Error interno del servidor"
            ).model_dump()
        )

@router.put(
    "/{comision_id}",
    response_model=Dict[str, str],
    summary="Actualizar comisión",
    description="Actualiza los datos de una comisión existente"
)
async def actualizar_comision(
    comision_id: UUID4 = Path(..., description="ID de la comisión"),
    request: ActualizarComisionRequest = Body(...),
    coordinador: CoordinadorComisiones = Depends(obtener_coordinador_comisiones),
    usuario: str = Depends(obtener_usuario_actual),
    _: bool = Depends(lambda: validar_permisos_comision("actualizar"))
):
    """Actualizar datos de comisión existente"""
    try:
        comando = ActualizarComision(
            comision_id=str(comision_id),
            monto_base=request.monto_base.valor if request.monto_base else None,
            porcentaje=request.porcentaje,
            configuracion=request.configuracion,
            metadatos=request.metadatos,
            motivo_actualizacion=request.motivo_actualizacion,
            usuario_id=usuario
        )
        
        resultado = coordinador.ejecutar_comando(comando)
        
        return {"mensaje": "Comisión actualizada exitosamente"}
        
    except ExcepcionAplicacion as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.post(
    "/{comision_id}/calcular",
    response_model=Dict[str, Any],
    summary="Calcular comisión",
    description="Calcula el monto de comisión basado en configuración"
)
async def calcular_comision(
    comision_id: UUID4 = Path(..., description="ID de la comisión"),
    forzar_recalculo: bool = Query(False, description="Forzar recálculo"),
    coordinador: CoordinadorComisiones = Depends(obtener_coordinador_comisiones),
    usuario: str = Depends(obtener_usuario_actual),
    _: bool = Depends(lambda: validar_permisos_comision("calcular"))
):
    """Calcular monto de comisión"""
    try:
        comando = CalcularComision(
            comision_id=str(comision_id),
            forzar_recalculo=forzar_recalculo,
            usuario_id=usuario
        )
        
        resultado = coordinador.calcular_comision(comando)
        
        return {
            "comision_id": resultado.comision_id,
            "monto_calculado": {
                "valor": resultado.monto_calculado.valor,
                "moneda": resultado.monto_calculado.moneda
            },
            "fecha_calculo": resultado.fecha_calculo.isoformat(),
            "metodo_calculo": resultado.metodo_calculo
        }
        
    except ExcepcionAplicacion as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.post(
    "/{comision_id}/aprobar",
    response_model=Dict[str, str],
    summary="Aprobar comisión",
    description="Aprobar comisión calculada"
)
async def aprobar_comision(
    comision_id: UUID4 = Path(..., description="ID de la comisión"),
    request: AprobarComisionRequest = Body(...),
    coordinador: CoordinadorComisiones = Depends(obtener_coordinador_comisiones),
    usuario: str = Depends(obtener_usuario_actual),
    _: bool = Depends(lambda: validar_permisos_comision("aprobar"))
):
    """Aprobar comisión calculada"""
    try:
        comando = AprobarComision(
            comision_id=str(comision_id),
            aprobador_id=usuario,
            comentarios=request.comentarios or "",
            metadatos_aprobacion=request.metadatos_aprobacion or {},
            usuario_id=usuario
        )
        
        resultado = coordinador.aprobar_comision(comando)
        
        return {"mensaje": resultado.mensaje}
        
    except ExcepcionAplicacion as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.post(
    "/{comision_id}/rechazar",
    response_model=Dict[str, str],
    summary="Rechazar comisión",
    description="Rechazar comisión con motivo"
)
async def rechazar_comision(
    comision_id: UUID4 = Path(..., description="ID de la comisión"),
    request: RechazarComisionRequest = Body(...),
    coordinador: CoordinadorComisiones = Depends(obtener_coordinador_comisiones),
    usuario: str = Depends(obtener_usuario_actual),
    _: bool = Depends(lambda: validar_permisos_comision("rechazar"))
):
    """Rechazar comisión con motivo específico"""
    try:
        comando = RechazarComision(
            comision_id=str(comision_id),
            rechazador_id=usuario,
            motivo_rechazo=request.motivo_rechazo,
            comentarios=request.comentarios or "",
            metadatos_rechazo=request.metadatos_rechazo or {},
            usuario_id=usuario
        )
        
        resultado = coordinador.rechazar_comision(comando)
        
        return {"mensaje": resultado.mensaje}
        
    except ExcepcionAplicacion as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.post(
    "/{comision_id}/pagar",
    response_model=Dict[str, str],
    summary="Marcar como pagada",
    description="Marcar comisión como pagada con detalles de pago"
)
async def pagar_comision(
    comision_id: UUID4 = Path(..., description="ID de la comisión"),
    request: PagarComisionRequest = Body(...),
    coordinador: CoordinadorComisiones = Depends(obtener_coordinador_comisiones),
    usuario: str = Depends(obtener_usuario_actual),
    _: bool = Depends(lambda: validar_permisos_comision("pagar"))
):
    """Marcar comisión como pagada"""
    try:
        comando = PagarComision(
            comision_id=str(comision_id),
            metodo_pago=request.metodo_pago,
            referencia_pago=request.referencia_pago,
            fecha_pago=request.fecha_pago,
            monto_pagado=request.monto_pagado.valor if request.monto_pagado else None,
            moneda_pago=request.monto_pagado.moneda if request.monto_pagado else "COP",
            metadatos_pago=request.metadatos_pago or {},
            usuario_id=usuario
        )
        
        resultado = coordinador.ejecutar_comando(comando)
        
        return {"mensaje": "Comisión marcada como pagada"}
        
    except ExcepcionAplicacion as ex:
        raise HTTPException(status_code=400, detail=str(ex))

# =============================================================================
# ENDPOINTS DE CONSULTAS (LECTURA)
# =============================================================================

@router.get(
    "/{comision_id}",
    response_model=ComisionResponse,
    summary="Obtener comisión",
    description="Obtener detalles completos de una comisión específica"
)
async def obtener_comision(
    comision_id: UUID4 = Path(..., description="ID de la comisión"),
    incluir_metadatos: bool = Query(False, description="Incluir metadatos detallados"),
    coordinador: CoordinadorComisiones = Depends(obtener_coordinador_comisiones)
) -> ComisionResponse:
    """Obtener comisión específica por ID"""
    try:
        consulta = ObtenerComision(
            comision_id=str(comision_id),
            incluir_metadatos=incluir_metadatos
        )
        
        dto = coordinador.obtener_comision(consulta)
        
        if not dto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comisión no encontrada"
            )
        
        # Convertir DTO a response
        response = ComisionResponse(
            id=dto.id,
            afiliado_id=dto.afiliado_id,
            campana_id=dto.campana_id,
            conversion_id=dto.conversion_id,
            estado=EstadoComisionAPI(dto.estado),
            tipo_comision=TipoComisionAPI(dto.tipo_comision),
            monto_base=MontoMonetarioAPI(valor=dto.monto_base, moneda=dto.moneda),
            porcentaje=dto.porcentaje,
            monto_calculado=MontoMonetarioAPI(
                valor=dto.monto_calculado, 
                moneda=dto.moneda
            ) if dto.monto_calculado else None,
            fecha_creacion=dto.fecha_creacion,
            fecha_actualizacion=dto.fecha_creacion,  # Mock
            fecha_calculo=dto.fecha_calculo,
            fecha_aprobacion=dto.fecha_aprobacion,
            fecha_pago=dto.fecha_pago,
            aprobador_id=dto.aprobador_id,
            comentarios=dto.comentarios,
            metadatos=dto.metadatos
        )
        
        return response
        
    except ExcepcionAplicacion as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.get(
    "/",
    response_model=ResultadoPaginadoResponse,
    summary="Listar comisiones",
    description="Listar comisiones con filtros y paginación"
)
async def listar_comisiones(
    # Parámetros de paginación
    pagina: int = Query(1, ge=1, description="Número de página"),
    tamaño: int = Query(20, ge=1, le=1000, description="Elementos por página"),
    
    # Filtros
    estados: Optional[List[EstadoComisionAPI]] = Query(None, description="Filtrar por estados"),
    tipos: Optional[List[TipoComisionAPI]] = Query(None, description="Filtrar por tipos"),
    afiliado_id: Optional[UUID4] = Query(None, description="Filtrar por afiliado"),
    campana_id: Optional[UUID4] = Query(None, description="Filtrar por campaña"),
    fecha_desde: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    
    # Configuración
    formato_resumen: bool = Query(True, description="Usar formato resumido"),
    
    coordinador: CoordinadorComisiones = Depends(obtener_coordinador_comisiones)
) -> ResultadoPaginadoResponse:
    """
    Listar comisiones con filtros avanzados:
    
    - Paginación configurable
    - Filtros por estado, tipo, afiliado, campaña
    - Filtros por rango de fechas
    - Formato completo o resumido
    """
    try:
        # Preparar filtros
        filtros = CriterioFiltroComision(
            estados=[EstadoComision(e.value) for e in estados] if estados else None,
            tipos_comision=[TipoComision(t.value) for t in tipos] if tipos else None,
            afiliados_ids=[str(afiliado_id)] if afiliado_id else None,
            campanas_ids=[str(campana_id)] if campana_id else None,
            fecha_creacion_desde=fecha_desde,
            fecha_creacion_hasta=fecha_hasta
        )
        
        # Preparar paginación
        paginacion = CriterioPaginacion(pagina=pagina, tamaño=tamaño)
        
        # Crear consulta
        consulta = ListarComisiones(
            filtros=filtros,
            paginacion=paginacion,
            formato_resumen=formato_resumen
        )
        
        # Ejecutar consulta
        resultado = coordinador.ejecutar_consulta(consulta)
        
        # Convertir a response
        response = ResultadoPaginadoResponse(
            elementos=resultado.elementos,  # Ya son DTOs
            total_elementos=resultado.total_elementos,
            pagina_actual=resultado.pagina_actual,
            tamaño_pagina=resultado.tamaño_pagina,
            total_paginas=resultado.total_paginas,
            tiene_anterior=resultado.tiene_anterior,
            tiene_siguiente=resultado.tiene_siguiente
        )
        
        return response
        
    except ExcepcionAplicacion as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.get(
    "/afiliado/{afiliado_id}",
    response_model=ResultadoPaginadoResponse,
    summary="Comisiones por afiliado",
    description="Obtener comisiones de un afiliado específico"
)
async def listar_comisiones_afiliado(
    afiliado_id: UUID4 = Path(..., description="ID del afiliado"),
    pagina: int = Query(1, ge=1),
    tamaño: int = Query(20, ge=1, le=100),
    estados: Optional[List[EstadoComisionAPI]] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    incluir_estadisticas: bool = Query(False, description="Incluir estadísticas del afiliado"),
    coordinador: CoordinadorComisiones = Depends(obtener_coordinador_comisiones)
) -> ResultadoPaginadoResponse:
    """Obtener comisiones de un afiliado específico con estadísticas opcionales"""
    try:
        consulta = ObtenerComisionesPorAfiliado(
            afiliado_id=str(afiliado_id),
            estados_filtro=[EstadoComision(e.value) for e in estados] if estados else None,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            incluir_estadisticas=incluir_estadisticas,
            paginacion=CriterioPaginacion(pagina=pagina, tamaño=tamaño)
        )
        
        resultado = coordinador.listar_comisiones_afiliado(consulta)
        
        return ResultadoPaginadoResponse(
            elementos=[dto.model_dump() for dto in resultado.elementos],
            total_elementos=resultado.total_elementos,
            pagina_actual=resultado.pagina_actual,
            tamaño_pagina=resultado.tamaño_pagina,
            total_paginas=resultado.total_paginas,
            tiene_anterior=resultado.tiene_anterior,
            tiene_siguiente=resultado.tiene_siguiente
        )
        
    except ExcepcionAplicacion as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.get(
    "/estadisticas",
    response_model=EstadisticasComisionResponse,
    summary="Estadísticas de comisiones",
    description="Obtener estadísticas agregadas de comisiones"
)
async def obtener_estadisticas(
    fecha_desde: Optional[date] = Query(None, description="Fecha inicio para estadísticas"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha fin para estadísticas"),
    afiliado_id: Optional[UUID4] = Query(None, description="Estadísticas de afiliado específico"),
    campana_id: Optional[UUID4] = Query(None, description="Estadísticas de campaña específica"),
    incluir_tendencias: bool = Query(False, description="Incluir análisis de tendencias"),
    coordinador: CoordinadorComisiones = Depends(obtener_coordinador_comisiones)
) -> EstadisticasComisionResponse:
    """
    Obtener estadísticas agregadas de comisiones:
    
    - Conteos por estado
    - Montos totales por tipo
    - Métricas de tiempo promedio
    - Análisis de tendencias (opcional)
    """
    try:
        consulta = ObtenerEstadisticasComisiones(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            afiliado_id=str(afiliado_id) if afiliado_id else None,
            campana_id=str(campana_id) if campana_id else None,
            incluir_tendencias=incluir_tendencias
        )
        
        estadisticas = coordinador.ejecutar_consulta(consulta)
        
        return EstadisticasComisionResponse(
            total_comisiones=estadisticas.total_comisiones,
            total_pendientes=estadisticas.total_pendientes,
            total_calculadas=estadisticas.total_calculadas,
            total_aprobadas=estadisticas.total_aprobadas,
            total_rechazadas=estadisticas.total_rechazadas,
            total_pagadas=estadisticas.total_pagadas,
            monto_total_calculado=MontoMonetarioAPI(
                valor=estadisticas.monto_total_calculado,
                moneda=estadisticas.moneda
            ),
            monto_total_aprobado=MontoMonetarioAPI(
                valor=estadisticas.monto_total_aprobado,
                moneda=estadisticas.moneda
            ),
            monto_total_pagado=MontoMonetarioAPI(
                valor=estadisticas.monto_total_pagado,
                moneda=estadisticas.moneda
            ),
            fecha_ultimo_calculo=estadisticas.fecha_ultimo_calculo,
            promedio_tiempo_aprobacion_dias=estadisticas.promedio_tiempo_aprobacion_dias
        )
        
    except ExcepcionAplicacion as ex:
        raise HTTPException(status_code=400, detail=str(ex))

# =============================================================================
# HEALTH CHECK
# =============================================================================

@router.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Verificar estado del servicio de comisiones"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "marketing.comisiones",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }