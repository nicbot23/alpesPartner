"""
DTOs para el microservicio de afiliados con arquitectura DDD
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AfiliadoBase(BaseModel):
    nombre: str = Field(..., description="Nombre del afiliado")
    tipo_afiliacion: str = Field(..., description="Tipo de afiliación (individual, empresa, etc.)")
    email: str = Field(..., description="Email del afiliado")
    telefono: str = Field(default="", description="Teléfono del afiliado")
    direccion: str = Field(default="", description="Dirección del afiliado")


class RegistrarAfiliadoRequest(AfiliadoBase):
    """Request para registrar un nuevo afiliado"""
    pass


class AprobarAfiliadoRequest(BaseModel):
    """Request para aprobar un afiliado"""
    aprobado_por: str = Field(..., description="ID del usuario que aprueba")
    observaciones: str = Field(default="", description="Observaciones para la aprobación")


class RechazarAfiliadoRequest(BaseModel):
    """Request para rechazar un afiliado"""
    rechazado_por: str = Field(..., description="ID del usuario que rechaza")
    razon_rechazo: str = Field(..., description="Razón del rechazo")


class ActualizarAfiliadoRequest(BaseModel):
    """Request para actualizar datos de un afiliado"""
    actualizado_por: str = Field(..., description="ID del usuario que actualiza")
    nombre: Optional[str] = Field(None, description="Nuevo nombre del afiliado")
    telefono: Optional[str] = Field(None, description="Nuevo teléfono del afiliado")
    direccion: Optional[str] = Field(None, description="Nueva dirección del afiliado")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")


class DesactivarAfiliadoRequest(BaseModel):
    """Request para desactivar un afiliado"""
    desactivado_por: str = Field(..., description="ID del usuario que desactiva")
    razon_desactivacion: str = Field(..., description="Razón de la desactivación")


class AfiliadoResponse(AfiliadoBase):
    """Response para un afiliado"""
    id: str = Field(..., description="ID único del afiliado")
    estado: str = Field(..., description="Estado del afiliado (pendiente, aprobado, rechazado, desactivado)")
    fecha_registro: datetime = Field(..., description="Fecha de registro")
    fecha_aprobacion: Optional[datetime] = Field(None, description="Fecha de aprobación")
    observaciones: str = Field(default="", description="Observaciones adicionales")

    class Config:
        from_attributes = True


class AfiliadoListResponse(BaseModel):
    """Response para lista de afiliados"""
    afiliados: List[AfiliadoResponse]
    total: int
    page: int
    size: int


class MessageResponse(BaseModel):
    """Response genérico con mensaje"""
    message: str