"""
Eventos de dominio para el microservicio Conversiones
Eventos de integración para comunicación descentralizada con otros microservicios
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from ....seedwork.dominio.eventos import EventoDominio


@dataclass(frozen=True)
class ConversionDetectada(EventoDominio):
    """Evento de integración - Una nueva conversión ha sido detectada"""
    nombre: str = "conversion.detectada"
    conversion_id: str = ""
    user_id: str = ""
    tipo_conversion: str = ""
    valor: str = ""  # String para evitar problemas serialización
    moneda: str = "USD"
    metadata: str = ""
    fecha_conversion: datetime = None
    
    def __post_init__(self):
        if not self.fecha_conversion:
            object.__setattr__(self, 'fecha_conversion', datetime.utcnow())


@dataclass(frozen=True)
class ConversionValidada(EventoDominio):
    """Evento de integración - Conversión validada, lista para comisión"""
    nombre: str = "conversion.validada"
    conversion_id: str = ""
    user_id: str = ""
    estado_validacion: str = ""
    valor_validado: str = ""
    observaciones: str = ""
    fecha_validacion: datetime = None
    
    def __post_init__(self):
        if not self.fecha_validacion:
            object.__setattr__(self, 'fecha_validacion', datetime.utcnow())


@dataclass(frozen=True)
class ConversionRechazada(EventoDominio):
    """Evento de integración - Conversión rechazada por validación"""
    nombre: str = "conversion.rechazada"
    conversion_id: str = ""
    user_id: str = ""
    razon_rechazo: str = ""
    observaciones: str = ""
    fecha_rechazo: datetime = None
    
    def __post_init__(self):
        if not self.fecha_rechazo:
            object.__setattr__(self, 'fecha_rechazo', datetime.utcnow())


@dataclass(frozen=True)
class ConversionActualizada(EventoDominio):
    """Evento de integración - Conversión actualizada"""
    nombre: str = "conversion.actualizada"
    conversion_id: str = ""
    user_id: str = ""
    valor_anterior: str = ""
    valor_nuevo: str = ""
    tipo_actualizacion: str = ""
    fecha_actualizacion: datetime = None
    
    def __post_init__(self):
        if not self.fecha_actualizacion:
            object.__setattr__(self, 'fecha_actualizacion', datetime.utcnow())