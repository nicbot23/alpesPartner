"""
Objetos Valor del dominio Conversiones
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime
from enum import Enum


class TipoConversion(Enum):
    CLICK = "CLICK"
    IMPRESSION = "IMPRESSION" 
    PURCHASE = "PURCHASE"
    SIGNUP = "SIGNUP"


class EstadoConversion(Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    RECHAZADA = "RECHAZADA"
    CANCELADA = "CANCELADA"


@dataclass(frozen=True)
class DatosAfiliado:
    """Datos del afiliado que generó la conversión"""
    affiliate_id: str
    affiliate_type: str  # INFLUENCER, BRAND, AGENCY
    tier_level: str = "STANDARD"  # STANDARD, PREMIUM, VIP


@dataclass(frozen=True)
class DatosCampana:
    """Referencia a la campaña asociada"""
    campaign_id: str
    campaign_name: str
    brand: str


@dataclass(frozen=True)
class DatosTransaccion:
    """Información financiera de la conversión"""
    gross_amount: Decimal
    currency: str
    transaction_id: Optional[str] = None
    payment_method: Optional[str] = None
    
    def __post_init__(self):
        if self.gross_amount < 0:
            raise ValueError("Monto bruto no puede ser negativo")


@dataclass(frozen=True)
class MetadatosConversion:
    """Metadatos de seguimiento y atribución"""
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    device_type: Optional[str] = None
    geo_country: Optional[str] = None
    geo_region: Optional[str] = None