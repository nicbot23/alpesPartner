"""
Eventos específicos del microservicio Conversiones
"""
from dataclasses import dataclass, field
from typing import Optional
from pulsar.schema import Record, String, Integer, Float, Boolean

@dataclass
class ConversionDetected(Record):
    """Evento: Conversión detectada"""
    id: str = String()
    conversion_id: str = String()
    affiliate_id: str = String()
    campaign_id: str = String()
    user_id: str = String()
    conversion_value: float = Float()
    conversion_type: str = String()
    source_url: str = String()
    destination_url: str = String()
    timestamp: int = Integer()
    
@dataclass 
class ConversionValidated(Record):
    """Evento: Conversión validada"""
    id: str = String()
    conversion_id: str = String()
    validation_status: str = String()
    validated_by: str = String()
    validation_notes: str = String()
    timestamp: int = Integer()

@dataclass
class ConversionConfirmed(Record):
    """Evento: Conversión confirmada"""
    id: str = String()
    conversion_id: str = String()
    confirmed_value: float = Float()
    commission_amount: float = Float()
    confirmation_date: int = Integer()
    
@dataclass
class ConversionRejected(Record):
    """Evento: Conversión rechazada"""
    id: str = String()
    conversion_id: str = String()
    rejection_reason: str = String()
    rejected_by: str = String()
    rejection_date: int = Integer()

@dataclass
class ConversionCancelled(Record):
    """Evento: Conversión cancelada"""
    id: str = String()
    conversion_id: str = String()
    cancellation_reason: str = String()
    cancelled_by: str = String()
    cancellation_date: int = Integer()

# Evento wrapper principal
@dataclass
class EventoConversion(Record):
    """Evento wrapper para conversiones"""
    time: int = Integer()
    ingestion: int = Integer()
    datacontenttype: str = String()
    conversion_detected: Optional[ConversionDetected] = field(default_factory=lambda: ConversionDetected.schema())
    conversion_validated: Optional[ConversionValidated] = field(default_factory=lambda: ConversionValidated.schema())
    conversion_confirmed: Optional[ConversionConfirmed] = field(default_factory=lambda: ConversionConfirmed.schema())
    conversion_rejected: Optional[ConversionRejected] = field(default_factory=lambda: ConversionRejected.schema())
    conversion_cancelled: Optional[ConversionCancelled] = field(default_factory=lambda: ConversionCancelled.schema())