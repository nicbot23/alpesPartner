from dataclasses import dataclass, field
from campanias.seedwork.aplicacion.dto import DTO
from typing import Optional

@dataclass(frozen=True)
class CampañaDTO(DTO):
    """DTO para transferir datos de campaña siguiendo patrón AeroAlpes"""
    fecha_creacion: str
    fecha_actualizacion: str
    id: str
    nombre: str
    descripcion: str
    tipo: str
    canal_publicidad: str
    objetivo: str
    fecha_inicio: str
    fecha_fin: str
    presupuesto: float = 0.0
    moneda: str = "USD"
    codigo_campana: Optional[str] = None
    segmento_audiencia: Optional[str] = None
    estado: str = "borrador"  # Por defecto al crear

@dataclass(frozen=True)
class CampañaProductoDTO(DTO):
    id: str
    campaña_id: str
    producto_id: str
    descuento: float
    fecha_creacion: str

@dataclass(frozen=True)
class campaniaservicioDTO(DTO):
    id: str
    campaña_id: str
    servicio_id: str
    descuento: float
    fecha_creacion: str

@dataclass(frozen=True)
class campaniasegmentoDTO(DTO):
    id: str
    campaña_id: str
    segmento_id: str
    fecha_creacion: str

