from dataclasses import dataclass
from alpespartner.seedwork.aplicacion.queries import Query
from typing import Optional, List, Dict, Any


@dataclass
class GetConversion(Query):
    """Query para obtener una conversión por ID."""
    conversion_id: str


@dataclass
class ListConversions(Query):
    """Query para listar conversiones con filtros opcionales."""
    afiliado_id: Optional[str] = None
    campana_id: Optional[str] = None
    tipo_conversion: Optional[str] = None
    estado: Optional[str] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    page: int = 1
    size: int = 20


@dataclass
class GetConversionsByAfiliado(Query):
    """Query para obtener conversiones de un afiliado específico."""
    afiliado_id: str
    incluir_canceladas: bool = False


@dataclass
class GetConversionsByCampana(Query):
    """Query para obtener conversiones de una campaña específica."""
    campana_id: str
    estado: Optional[str] = None


@dataclass
class GetConversionsStats(Query):
    """Query para obtener estadísticas de conversiones."""
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    agrupado_por: str = "estado"  # estado, tipo, afiliado, campana