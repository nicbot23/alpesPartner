"""
Eventos de dominio para el módulo de Afiliados
Define eventos de integración y eventos internos
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal

from alpespartner.seedwork.dominio.eventos import EventoDominio


# Eventos de integración (publicados fuera del contexto)

@dataclass
class AffiliateCreated(EventoDominio):
    """Evento publicado cuando se crea un afiliado."""
    afiliado_id: str
    tipo_afiliado: str
    email: str
    nombres: str
    apellidos: str
    created_at: datetime
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class AffiliateActivated(EventoDominio):
    """Evento publicado cuando se activa un afiliado."""
    afiliado_id: str
    activated_by: str
    activated_at: datetime
    previous_state: str
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class AffiliateDeactivated(EventoDominio):
    """Evento publicado cuando se desactiva un afiliado."""
    afiliado_id: str
    deactivated_by: str
    deactivated_at: datetime
    reason: str
    previous_state: str
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class AffiliateSuspended(EventoDominio):
    """Evento publicado cuando se suspende un afiliado."""
    afiliado_id: str
    suspended_by: str
    suspended_at: datetime
    reason: str
    suspension_until: Optional[datetime] = None
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class AffiliateBlocked(EventoDominio):
    """Evento publicado cuando se bloquea un afiliado."""
    afiliado_id: str
    blocked_by: str
    blocked_at: datetime
    reason: str
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class AffiliateCommissionConfigUpdated(EventoDominio):
    """Evento publicado cuando se actualiza la configuración de comisiones."""
    afiliado_id: str
    updated_by: str
    updated_at: datetime
    previous_config: Dict[str, Any]
    new_config: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class AffiliateReferralCreated(EventoDominio):
    """Evento publicado cuando un afiliado refiere a otro."""
    afiliado_referente_id: str
    afiliado_referido_id: str
    referral_date: datetime
    referral_code: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()


# Eventos internos (solo dentro del contexto de Afiliados)

@dataclass
class AffiliateValidated(EventoDominio):
    """Evento interno cuando se valida un afiliado."""
    afiliado_id: str
    validated_by: str
    validated_at: datetime
    validation_notes: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class AffiliateBankingDataUpdated(EventoDominio):
    """Evento interno cuando se actualizan datos bancarios."""
    afiliado_id: str
    updated_by: str
    updated_at: datetime
    bank_info: Dict[str, str]
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class AffiliateContactDataUpdated(EventoDominio):
    """Evento interno cuando se actualizan datos de contacto."""
    afiliado_id: str
    updated_by: str
    updated_at: datetime
    contact_changes: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class AffiliateMetadataUpdated(EventoDominio):
    """Evento interno cuando se actualizan metadatos."""
    afiliado_id: str
    updated_by: str
    updated_at: datetime
    metadata_changes: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()