"""
DTOs para el microservicio de conversiones con arquitectura DDD
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class ConversionBase(BaseModel):
    user_id: str = Field(..., description="ID único del usuario")
    tipo_conversion: str = Field(..., description="Tipo de conversión (compra, registro, etc.)")
    valor: Decimal = Field(..., description="Valor de la conversión")
    moneda: str = Field(default="USD", description="Moneda de la conversión")
    metadata: str = Field(default="", description="Metadatos adicionales en JSON")


class DetectarConversionRequest(ConversionBase):
    """Request para detectar una nueva conversión"""
    pass


class ConversionCrear(ConversionBase):
    """Alias para compatibilidad"""
    pass


class ConversionActualizar(BaseModel):
    valor: Optional[Decimal] = Field(None, description="Nuevo valor de la conversión")
    tipo_conversion: Optional[str] = Field(None, description="Tipo de conversión")
    metadata: Optional[str] = Field(None, description="Metadatos adicionales")


class ConversionResponse(ConversionBase):
    id: str = Field(..., description="ID único de la conversión")
    estado: str = Field(..., description="Estado de la conversión (detectada, validada, rechazada)")
    fecha_conversion: datetime = Field(..., description="Fecha de conversión")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")
    observaciones: str = Field(default="", description="Observaciones adicionales")

    class Config:
        from_attributes = True


class ConversionListResponse(BaseModel):
    conversiones: List[ConversionResponse]
    total: int
    page: int
    size: int


class ValidarConversionRequest(BaseModel):
    observaciones: str = Field(default="", description="Observaciones para la validación")


class RechazarConversionRequest(BaseModel):
    razon_rechazo: str = Field(..., description="Razón del rechazo")
    observaciones: str = Field(default="", description="Observaciones adicionales")


class ConfirmarConversionRequest(BaseModel):
    """Request para confirmar una conversión"""
    observaciones: str = Field(default="", description="Observaciones para la confirmación")


class CancelarConversionRequest(BaseModel):
    """Request para cancelar una conversión"""
    razon_cancelacion: str = Field(..., description="Razón de la cancelación")
    observaciones: str = Field(default="", description="Observaciones adicionales")


class MessageResponse(BaseModel):
    message: str