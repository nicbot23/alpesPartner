"""Objetos valor reusables parte del seedwork del proyecto

En este archivo usted encontrará los objetos valor reusables parte del seedwork del proyecto

"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum
import re

@dataclass(frozen=True)
class ObjetoValor:
    """Clase base para todos los objetos valor"""
    pass

@dataclass(frozen=True)
class Codigo(ObjetoValor):
    """Código genérico para identificadores"""
    codigo: str
    
    def __post_init__(self):
        if not self.codigo or not self.codigo.strip():
            raise ValueError("El código no puede estar vacío")
        if len(self.codigo) > 20:
            raise ValueError("El código no puede tener más de 20 caracteres")

@dataclass(frozen=True)
class Email(ObjetoValor):
    """Email válido para contacto"""
    email: str
    
    def __post_init__(self):
        if not self.email or not self.email.strip():
            raise ValueError("El email no puede estar vacío")
        
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, self.email):
            raise ValueError("El email no tiene un formato válido")
    
    def dominio(self) -> str:
        """Retorna el dominio del email"""
        return self.email.split('@')[1]

@dataclass(frozen=True)
class Presupuesto(ObjetoValor):
    """Presupuesto con moneda"""
    monto: float
    moneda: str = "USD"
    
    def __post_init__(self):
        if self.monto < 0:
            raise ValueError("El presupuesto no puede ser negativo")
        if not self.moneda or len(self.moneda) != 3:
            raise ValueError("La moneda debe tener 3 caracteres")

@dataclass(frozen=True)
class PeriodoCampana(ObjetoValor):
    """Período de duración de una campaña"""
    fecha_inicio: datetime
    fecha_fin: datetime
    
    def __post_init__(self):
        if self.fecha_inicio >= self.fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
    
    def duracion_dias(self) -> int:
        """Retorna la duración en días"""
        return (self.fecha_fin - self.fecha_inicio).days
    
    def esta_activa(self, fecha_actual: Optional[datetime] = None) -> bool:
        """Verifica si la campaña está activa en una fecha"""
        if fecha_actual is None:
            fecha_actual = datetime.now()
        return self.fecha_inicio <= fecha_actual <= self.fecha_fin

@dataclass(frozen=True)
class SegmentoAudiencia(ObjetoValor):
    """Segmento de audiencia objetivo"""
    nombre: str
    descripcion: Optional[str] = None
    
    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del segmento no puede estar vacío")
        if len(self.nombre) > 50:
            raise ValueError("El nombre del segmento no puede tener más de 50 caracteres")

class TipoCampana(Enum):
    """Tipos de campaña de marketing"""
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    DISPLAY = "display"
    SEARCH = "search"
    VIDEO = "video"
    INFLUENCER = "influencer"

@dataclass(frozen=True)
class Canal(ObjetoValor):
    """Canal de marketing"""
    tipo: TipoCampana
    nombre: str
    configuracion: Optional[str] = None
    
    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del canal no puede estar vacío")

@dataclass(frozen=True)
class MetricaObjetivo(ObjetoValor):
    """Métrica objetivo de la campaña"""
    nombre: str
    valor_objetivo: float
    unidad: str
    
    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la métrica no puede estar vacío")
        if self.valor_objetivo < 0:
            raise ValueError("El valor objetivo no puede ser negativo")
        if not self.unidad or not self.unidad.strip():
            raise ValueError("La unidad no puede estar vacía")


