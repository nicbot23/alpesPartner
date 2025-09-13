"""
Objetos Valor del Bounded Context Campañas
Siguiendo principios DDD estrictos
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from alpespartner.seedwork.dominio.objetos_valor import ObjetoValor

@dataclass(frozen=True)
class PeriodoVigencia(ObjetoValor):
    """Periodo durante el cual una campaña está activa"""
    inicio: datetime
    fin: datetime
    
    def __post_init__(self):
        if self.inicio >= self.fin:
            raise ValueError("Fecha de inicio debe ser anterior a fecha fin")
    
    def esta_vigente(self, fecha: datetime = None) -> bool:
        """Verifica si la campaña está vigente en una fecha dada"""
        fecha = fecha or datetime.utcnow()
        return self.inicio <= fecha <= self.fin
    
    def dias_restantes(self) -> int:
        """Calcula días restantes de vigencia"""
        ahora = datetime.utcnow()
        if ahora > self.fin:
            return 0
        return (self.fin - ahora).days

@dataclass(frozen=True)
class TerminosComision(ObjetoValor):
    """Términos específicos de comisión para una campaña"""
    porcentaje_base: Decimal
    porcentaje_premium: Decimal
    umbral_premium: Decimal  # Monto mínimo para porcentaje premium
    moneda: str
    
    def __post_init__(self):
        if self.porcentaje_base < 0 or self.porcentaje_premium < 0:
            raise ValueError("Porcentajes no pueden ser negativos")
        if self.umbral_premium < 0:
            raise ValueError("Umbral premium no puede ser negativo")
        
    def calcular_porcentaje(self, monto: Decimal) -> Decimal:
        """Determina qué porcentaje aplicar según el monto"""
        if monto >= self.umbral_premium:
            return self.porcentaje_premium
        return self.porcentaje_base

@dataclass(frozen=True)
class RestriccionGeografica(ObjetoValor):
    """Restricciones geográficas de la campaña"""
    paises_permitidos: List[str]
    regiones_excluidas: List[str]
    
    def es_ubicacion_valida(self, pais: str, region: str = None) -> bool:
        """Verifica si una ubicación es válida para la campaña"""
        if pais not in self.paises_permitidos:
            return False
        if region and region in self.regiones_excluidas:
            return False
        return True

@dataclass(frozen=True)
class MetadatosCampana(ObjetoValor):
    """Metadatos adicionales de la campaña"""
    nombre: str
    descripcion: str
    marca: str
    categoria: str
    tags: List[str]
    
    def __post_init__(self):
        if not self.nombre or not self.marca:
            raise ValueError("Nombre y marca son obligatorios")
