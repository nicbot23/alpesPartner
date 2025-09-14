"""
Eventos simplificados del microservicio Conversiones
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class ConversionDetected:
    """Evento: Conversión detectada"""
    id: str
    conversion_id: str
    affiliate_id: str
    campaign_id: str
    user_id: str
    conversion_value: float
    conversion_type: str
    source_url: str
    destination_url: str
    timestamp: int
    
@dataclass 
class ConversionValidated:
    """Evento: Conversión validada"""
    id: str
    conversion_id: str
    validation_status: str
    validated_by: str
    validation_notes: str
    timestamp: int

@dataclass
class ConversionConfirmed:
    """Evento: Conversión confirmada"""
    id: str
    conversion_id: str
    confirmed_value: float
    confirmed_by: str
    commission_rate: float
    commission_amount: float
    confirmation_timestamp: int

@dataclass
class ConversionRejected:
    """Evento: Conversión rechazada"""
    id: str
    conversion_id: str
    rejection_reason: str
    rejected_by: str
    rejection_timestamp: int

@dataclass
class ConversionCancelled:
    """Evento: Conversión cancelada"""
    id: str
    conversion_id: str
    cancellation_reason: str
    cancelled_by: str
    cancellation_date: int

@dataclass
class EventoConversion:
    """Evento wrapper para conversiones"""
    time: int
    ingestion: int
    datacontenttype: str
    conversion_detected: Optional[ConversionDetected] = None
    conversion_validated: Optional[ConversionValidated] = None
    conversion_confirmed: Optional[ConversionConfirmed] = None
    conversion_rejected: Optional[ConversionRejected] = None
    conversion_cancelled: Optional[ConversionCancelled] = None