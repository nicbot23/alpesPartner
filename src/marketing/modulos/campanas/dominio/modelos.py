"""Dominio específico de Campañas (wrapper sobre seedwork si se requiere extender)
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from ....seedwork.dominio.entidades import Campana as CampanaEntidad, TipoCampana, EstadoCampana, ConfiguracionCampana

@dataclass
class Campana(CampanaEntidad):
    """Extensión ligera de la entidad base para permitir futuras reglas de contexto específico."""
    pass

__all__ = [
    "Campana",
    "TipoCampana",
    "EstadoCampana",
    "ConfiguracionCampana"
]
