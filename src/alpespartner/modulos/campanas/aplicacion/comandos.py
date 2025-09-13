"""
Comandos de Aplicación del Bounded Context Campañas
Siguiendo CQRS y principios DDD
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from alpespartner.seedwork.aplicacion.comandos import ComandoAplicacion


@dataclass(frozen=True)
class CrearCampana(ComandoAplicacion):
    """
    Comando para crear una nueva campaña
    """
    # Metadatos
    nombre: str
    descripcion: str
    marca: str
    categoria: str
    tags: List[str]
    
    # Período de vigencia
    fecha_inicio: datetime
    fecha_fin: datetime
    
    # Términos de comisión
    porcentaje_base: Decimal
    porcentaje_premium: Decimal
    umbral_premium: Decimal
    moneda: str
    
    # Restricciones geográficas
    paises_permitidos: List[str]
    regiones_excluidas: List[str]


@dataclass(frozen=True)
class ActivarCampana(ComandoAplicacion):
    """
    Comando para activar una campaña en estado BORRADOR
    """
    campana_id: str


@dataclass(frozen=True)
class PausarCampana(ComandoAplicacion):
    """
    Comando para pausar una campaña activa
    """
    campana_id: str
    motivo: str = "Pausada manualmente"


@dataclass(frozen=True)
class ModificarTerminosCampana(ComandoAplicacion):
    """
    Comando para modificar términos de comisión de una campaña
    """
    campana_id: str
    porcentaje_base: Decimal
    porcentaje_premium: Decimal
    umbral_premium: Decimal
    motivo: str = "Modificación de términos"


@dataclass(frozen=True)
class ConsultarCampana(ComandoAplicacion):
    """
    Query para consultar una campaña por ID
    """
    campana_id: str


@dataclass(frozen=True)
class ListarCampanasActivas(ComandoAplicacion):
    """
    Query para listar todas las campañas activas
    """
    limite: int = 10
    offset: int = 0
