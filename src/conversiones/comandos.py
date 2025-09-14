"""
Comandos específicos del microservicio Conversiones
"""
from dataclasses import dataclass, field
from typing import Optional
from pulsar.schema import Record, String, Integer, Float, Boolean

@dataclass
class DetectConversionPayload(Record):
    """Payload para detectar conversión"""
    affiliate_id: str = String()
    campaign_id: str = String()
    user_id: str = String()
    conversion_value: float = Float()
    conversion_type: str = String()
    source_url: str = String()
    destination_url: str = String()

@dataclass
class ValidateConversionPayload(Record):
    """Payload para validar conversión"""
    conversion_id: str = String()
    validation_criteria: str = String()
    validator_id: str = String()
    notes: str = String()

@dataclass
class ConfirmConversionPayload(Record):
    """Payload para confirmar conversión"""
    conversion_id: str = String()
    confirmed_value: float = Float()
    commission_rate: float = Float()
    confirmer_id: str = String()

@dataclass
class RejectConversionPayload(Record):
    """Payload para rechazar conversión"""
    conversion_id: str = String()
    rejection_reason: str = String()
    rejected_by: str = String()

@dataclass
class CancelConversionPayload(Record):
    """Payload para cancelar conversión"""
    conversion_id: str = String()
    cancellation_reason: str = String()
    cancelled_by: str = String()

# Comandos principales
@dataclass
class ComandoDetectarConversion(Record):
    """Comando: Detectar conversión"""
    time: int = Integer()
    ingestion: int = Integer()
    datacontenttype: str = String()
    data: DetectConversionPayload = field(default_factory=lambda: DetectConversionPayload.schema())

@dataclass
class ComandoValidarConversion(Record):
    """Comando: Validar conversión"""
    time: int = Integer()
    ingestion: int = Integer()
    datacontenttype: str = String()
    data: ValidateConversionPayload = field(default_factory=lambda: ValidateConversionPayload.schema())

@dataclass
class ComandoConfirmarConversion(Record):
    """Comando: Confirmar conversión"""
    time: int = Integer()
    ingestion: int = Integer()
    datacontenttype: str = String()
    data: ConfirmConversionPayload = field(default_factory=lambda: ConfirmConversionPayload.schema())

@dataclass
class ComandoRechazarConversion(Record):
    """Comando: Rechazar conversión"""
    time: int = Integer()
    ingestion: int = Integer()
    datacontenttype: str = String()
    data: RejectConversionPayload = field(default_factory=lambda: RejectConversionPayload.schema())

@dataclass
class ComandoCancelarConversion(Record):
    """Comando: Cancelar conversión"""
    time: int = Integer()
    ingestion: int = Integer()
    datacontenttype: str = String()
    data: CancelConversionPayload = field(default_factory=lambda: CancelConversionPayload.schema())