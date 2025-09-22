
from campanias.seedwork.dominio.objetos_valor import ObjetoValor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

@dataclass(frozen=True)
class Locacion(ObjetoValor):
    latitud: float
    longitud: float
    direccion: str

class EstadoCampana(str, Enum):
    ACTIVA = "Activa"
    PAUSADA = "Pausada"
    FINALIZADA = "Finalizada"
    BORRADOR = "Borrador"
    CANCELADA = "Cancelada"

class TipoCampana(str, Enum):
    PROMOCIONAL = "Promocional"
    DESCUENTO = "Descuento"
    CASHBACK = "Cashback"
    PUNTOS = "Puntos"
    BANNER = "Banner"

class CanalPublicidad(str, Enum):
    EMAIL = "Email"
    REDES_SOCIALES = "Redes_Sociales"
    WEB = "Web"
    MOBILE = "Mobile"
    DISPLAY = "Display"
    SEARCH = "Search"

class ObjetivoCampana(str, Enum):
    CONVERSIONES = "Conversiones"
    TRAFICO = "Trafico"
    RECONOCIMIENTO = "Reconocimiento"
    VENTAS = "Ventas"
    ENGAGEMENT = "Engagement"

@dataclass(frozen=True)
class NombreCampaña(ObjetoValor):
    nombre: str

@dataclass(frozen=True)
class DescripcionCampaña(ObjetoValor):
    descripcion: str

@dataclass(frozen=True)
class FechaInicio(ObjetoValor):
    fecha_inicio: datetime   

@dataclass(frozen=True)
class FechaFin(ObjetoValor):
    fecha_fin: datetime

@dataclass(frozen=True)
class FechaCreacion(ObjetoValor):
    fecha_creacion: datetime 

@dataclass(frozen=True)
class FechaModificacion(ObjetoValor):
    fecha_modificacion: datetime

@dataclass(frozen=True)
class FechaEliminacion(ObjetoValor):
    fecha_eliminacion: datetime  

@dataclass(frozen=True)
class Activo(ObjetoValor):
    activo: bool    

@dataclass(frozen=True)
class Presupuesto(ObjetoValor):
    presupuesto: float

@dataclass(frozen=True)
class Moneda(ObjetoValor):
    moneda: str

@dataclass(frozen=True)
class CodigoCampana(ObjetoValor):
    codigo_campana: str

@dataclass(frozen=True)
class SegmentoAudiencia(ObjetoValor):
    segmento_audiencia: str
    