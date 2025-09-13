"""
Eventos del Bounded Context Campañas
Siguiendo principios DDD estrictos
"""

from dataclasses import dataclass
from datetime import datetime
from alpespartner.seedwork.dominio.eventos import EventoDominio


@dataclass(frozen=True)
class CampanaCreada(EventoDominio):
    """Evento emitido cuando se crea una nueva campaña"""
    nombre: str = ""
    campana_id: str = ""
    marca: str = ""
    occurred_at: datetime = None
    
    def __post_init__(self):
        if not self.occurred_at:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True) 
class CampanaActivada(EventoDominio):
    """Evento emitido cuando una campaña es activada"""
    nombre: str = ""
    campana_id: str = ""
    fecha_inicio: datetime = None
    fecha_fin: datetime = None
    occurred_at: datetime = None
    
    def __post_init__(self):
        if not self.occurred_at:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True)
class CampanaDesactivada(EventoDominio):
    """Evento emitido cuando una campaña es desactivada"""
    nombre: str = ""
    campana_id: str = ""
    motivo: str = ""
    occurred_at: datetime = None
    
    def __post_init__(self):
        if not self.occurred_at:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True)
class TerminosModificados(EventoDominio):
    """Evento emitido cuando se modifican los términos de comisión"""
    nombre: str = ""
    campana_id: str = ""
    porcentaje_anterior: str = ""
    porcentaje_nuevo: str = ""
    occurred_at: datetime = None
    
    def __post_init__(self):
        if not self.occurred_at:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())
