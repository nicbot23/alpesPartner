"""
Eventos de dominio para el contexto Conversiones
Eventos de integración para comunicación descentralizada con otros microservicios
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from alpespartner.seedwork.dominio.eventos import EventoDominio


@dataclass(frozen=True)
class ConversionCreated(EventoDominio):
    """Evento de integración - Una nueva conversión ha sido registrada"""
    conversion_id: str = ""
    affiliate_id: str = ""
    campaign_id: str = ""
    conversion_type: str = ""
    gross_amount: str = ""  # String para evitar problemas serialización
    currency: str = ""
    transaction_id: Optional[str] = None
    occurred_at: datetime = None
    
    def __post_init__(self):
        if not self.occurred_at:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True)
class ConversionConfirmed(EventoDominio):
    """Evento de integración - Conversión confirmada, lista para comisión"""
    conversion_id: str = ""
    affiliate_id: str = ""
    campaign_id: str = ""
    gross_amount: str = ""
    currency: str = ""
    confirmed_at: datetime = None
    
    def __post_init__(self):
        if not self.confirmed_at:
            object.__setattr__(self, 'confirmed_at', datetime.utcnow())


@dataclass(frozen=True)
class ConversionRejected(EventoDominio):
    """Evento de integración - Conversión rechazada por validación"""
    conversion_id: str = ""
    affiliate_id: str = ""
    campaign_id: str = ""
    rejection_reason: str = ""
    rejected_at: datetime = None
    
    def __post_init__(self):
        if not self.rejected_at:
            object.__setattr__(self, 'rejected_at', datetime.utcnow())


@dataclass(frozen=True)
class ConversionCancelled(EventoDominio):
    """Evento de integración - Conversión cancelada (ej. refund)"""
    conversion_id: str = ""
    affiliate_id: str = ""
    campaign_id: str = ""
    cancellation_reason: str = ""
    cancelled_at: datetime = None
    
    def __post_init__(self):
        if not self.cancelled_at:
            object.__setattr__(self, 'cancelled_at', datetime.utcnow())


# Eventos internos (dominio)
@dataclass(frozen=True) 
class ConversionValidated(EventoDominio):
    """Evento interno - Conversión pasó validaciones técnicas"""
    conversion_id: str = ""
    validation_score: float = 0.0
    validated_at: datetime = None
    
    def __post_init__(self):
        if not self.validated_at:
            object.__setattr__(self, 'validated_at', datetime.utcnow())


@dataclass(frozen=True)
class ConversionAttributed(EventoDominio):
    """Evento interno - Atribución a afiliado completada"""
    conversion_id: str = ""
    affiliate_id: str = ""
    attribution_model: str = "LAST_CLICK"
    attributed_at: datetime = None
    
    def __post_init__(self):
        if not self.attributed_at:
            object.__setattr__(self, 'attributed_at', datetime.utcnow())