from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import List

@dataclass(frozen=True)
class PeriodoVigencia:
    fecha_inicio: datetime
    fecha_fin: datetime
    
    @property
    def duracion_dias(self) -> int:
        return (self.fecha_fin - self.fecha_inicio).days

@dataclass(frozen=True)
class TerminosComision:
    porcentaje: Decimal
    comision_minima: Decimal
    comision_maxima: Decimal = None

@dataclass(frozen=True)
class RestriccionGeografica:
    paises_incluidos: List[str]
    paises_excluidos: List[str]

@dataclass(frozen=True)
class MetadatosCampana:
    canal_origen: str
    audiencia_objetivo: str
    tags: List[str]
