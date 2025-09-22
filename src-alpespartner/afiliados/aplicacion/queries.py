from afiliados.seedwork.aplicacion.queries import Query
from dataclasses import dataclass
from typing import Optional

@dataclass
class ObtenerAfiliadoPorId(Query):
    id_afiliado: str

@dataclass
class ObtenerAfiliados(Query):
    estado: Optional[str] = None  # ACTIVO, INACTIVO, PENDIENTE, RECHAZADO
    tipo_afiliado: Optional[str] = None  # INDIVIDUAL, EMPRESA, INFLUENCER
    limite: Optional[int] = 10
    offset: Optional[int] = 0

@dataclass
class ObtenerRendimientoAfiliado(Query):
    id_afiliado: str
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
