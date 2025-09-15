"""
Router para endpoints de conversiones
"""
from fastapi import APIRouter, status, BackgroundTasks, HTTPException
from conversiones.despachadores import Despachador
from conversiones.comandos import (
    ComandoDetectarConversion, ComandoValidarConversion, ComandoConfirmarConversion,
    ComandoRechazarConversion, ComandoCancelarConversion,
    DetectConversionPayload, ValidateConversionPayload, ConfirmConversionPayload,
    RejectConversionPayload, CancelConversionPayload
)
from conversiones.utils import time_millis, generar_uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from decimal import Decimal
from .dto import (
    ConversionCrear,
    ConversionActualizar,
    ConversionResponse,
    ConversionListResponse,
    ValidarConversionRequest,
    RechazarConversionRequest,
    MessageResponse
)
from ....utils import generar_uuid, time_millis
from ....modulos.conversiones.aplicacion.comandos import DetectarConversion, ValidarConversion, RechazarConversion, ActualizarConversion
from ....modulos.conversiones.aplicacion.manejadores import (
    ManejadorDetectarConversion, ManejadorValidarConversion, 
    ManejadorRechazarConversion, ManejadorActualizarConversion
)
from ....modulos.conversiones.infraestructura.despachadores import despachador_eventos

router = APIRouter()

# Inicializar manejadores
manejador_detectar = ManejadorDetectarConversion(despachador_eventos)
manejador_validar = ManejadorValidarConversion(despachador_eventos)
manejador_rechazar = ManejadorRechazarConversion(despachador_eventos)
manejador_actualizar = ManejadorActualizarConversion(despachador_eventos)

router = APIRouter()

@router.post("/detectar", status_code=status.HTTP_202_ACCEPTED, response_model=ConversionResponse)
async def detectar_conversion(
    request: DetectarConversionRequest, 
    background_tasks: BackgroundTasks
) -> ConversionResponse:
    """Detectar nueva conversión"""
    try:
        conversion_id = generar_uuid()
        
        # Crear payload
        payload = DetectConversionPayload(
            affiliate_id=request.affiliate_id,
            campaign_id=request.campaign_id,
            user_id=request.user_id,
            conversion_value=request.conversion_value,
            conversion_type=request.conversion_type,
            source_url=request.source_url,
            destination_url=request.destination_url
        )
        
        # Crear comando
        comando = ComandoDetectarConversion(
            time=time_millis(),
            ingestion=time_millis(),
            datacontenttype="DetectarConversion",
            data=payload
        )
        
        # Publicar comando de forma asíncrona
        background_tasks.add_task(
            lambda: Despachador().publicar_comando_detectar_conversion(comando)
        )
        
        return ConversionResponse(
            conversion_id=conversion_id,
            status="DETECTING",
            message="Detección de conversión en proceso",
            timestamp=time_millis()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detectando conversión: {str(e)}"
        )

@router.post("/validar", status_code=status.HTTP_202_ACCEPTED, response_model=ConversionResponse)
async def validar_conversion(
    request: ValidarConversionRequest,
    background_tasks: BackgroundTasks
) -> ConversionResponse:
    """Validar conversión existente"""
    try:
        # Crear payload
        payload = ValidateConversionPayload(
            conversion_id=request.conversion_id,
            validation_criteria=request.validation_criteria,
            validator_id=request.validator_id,
            notes=request.notes or ""
        )
        
        # Crear comando
        comando = ComandoValidarConversion(
            time=time_millis(),
            ingestion=time_millis(),
            datacontenttype="ValidarConversion",
            data=payload
        )
        
        # Publicar comando de forma asíncrona
        background_tasks.add_task(
            lambda: Despachador().publicar_comando_validar_conversion(comando)
        )
        
        return ConversionResponse(
            conversion_id=request.conversion_id,
            status="VALIDATING",
            message="Validación de conversión en proceso",
            timestamp=time_millis()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validando conversión: {str(e)}"
        )

@router.post("/confirmar", status_code=status.HTTP_202_ACCEPTED, response_model=ConversionResponse)
async def confirmar_conversion(
    request: ConfirmarConversionRequest,
    background_tasks: BackgroundTasks
) -> ConversionResponse:
    """Confirmar conversión validada"""
    try:
        # Crear payload
        payload = ConfirmConversionPayload(
            conversion_id=request.conversion_id,
            confirmed_value=request.confirmed_value,
            commission_rate=request.commission_rate,
            confirmer_id=request.confirmer_id
        )
        
        # Crear comando
        comando = ComandoConfirmarConversion(
            time=time_millis(),
            ingestion=time_millis(),
            datacontenttype="ConfirmarConversion",
            data=payload
        )
        
        # Publicar comando de forma asíncrona
        background_tasks.add_task(
            lambda: Despachador().publicar_comando_confirmar_conversion(comando)
        )
        
        return ConversionResponse(
            conversion_id=request.conversion_id,
            status="CONFIRMING",
            message="Confirmación de conversión en proceso",
            timestamp=time_millis()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error confirmando conversión: {str(e)}"
        )

@router.post("/rechazar", status_code=status.HTTP_202_ACCEPTED, response_model=ConversionResponse)
async def rechazar_conversion(
    request: RechazarConversionRequest,
    background_tasks: BackgroundTasks
) -> ConversionResponse:
    """Rechazar conversión"""
    try:
        # Crear payload
        payload = RejectConversionPayload(
            conversion_id=request.conversion_id,
            rejection_reason=request.rejection_reason,
            rejected_by=request.rejected_by
        )
        
        # Crear comando
        comando = ComandoRechazarConversion(
            time=time_millis(),
            ingestion=time_millis(),
            datacontenttype="RechazarConversion",
            data=payload
        )
        
        # Publicar comando de forma asíncrona
        background_tasks.add_task(
            lambda: Despachador().publicar_comando_rechazar_conversion(comando)
        )
        
        return ConversionResponse(
            conversion_id=request.conversion_id,
            status="REJECTING",
            message="Rechazo de conversión en proceso",
            timestamp=time_millis()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rechazando conversión: {str(e)}"
        )

@router.post("/cancelar", status_code=status.HTTP_202_ACCEPTED, response_model=ConversionResponse)
async def cancelar_conversion(
    request: CancelarConversionRequest,
    background_tasks: BackgroundTasks
) -> ConversionResponse:
    """Cancelar conversión"""
    try:
        # Crear payload
        payload = CancelConversionPayload(
            conversion_id=request.conversion_id,
            cancellation_reason=request.cancellation_reason,
            cancelled_by=request.cancelled_by
        )
        
        # Crear comando
        comando = ComandoCancelarConversion(
            time=time_millis(),
            ingestion=time_millis(),
            datacontenttype="CancelarConversion",
            data=payload
        )
        
        # Publicar comando de forma asíncrona
        background_tasks.add_task(
            lambda: Despachador().publicar_comando_cancelar_conversion(comando)
        )
        
        return ConversionResponse(
            conversion_id=request.conversion_id,
            status="CANCELLING",
            message="Cancelación de conversión en proceso",
            timestamp=time_millis()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelando conversión: {str(e)}"
        )