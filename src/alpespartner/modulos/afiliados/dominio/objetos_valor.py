"""
Objetos de valor para el dominio de Afiliados
Define los tipos de datos inmutables y validaciones de negocio
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime


class TipoAfiliado(Enum):
    """Tipos de afiliado en la plataforma AlpesPartner."""
    INFLUENCER = "INFLUENCER"
    EMPRESA = "EMPRESA"
    INDIVIDUAL = "INDIVIDUAL"
    PREMIUM = "PREMIUM"


class EstadoAfiliado(Enum):
    """Estados posibles de un afiliado."""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    PENDIENTE_VERIFICACION = "PENDIENTE_VERIFICACION"
    BLOQUEADO = "BLOQUEADO"


class TipoDocumento(Enum):
    """Tipos de documento de identificación."""
    CEDULA = "CEDULA"
    PASAPORTE = "PASAPORTE"
    NIT = "NIT"
    RUT = "RUT"


@dataclass(frozen=True)
class DatosPersonales:
    """Datos personales del afiliado."""
    nombres: str
    apellidos: str
    fecha_nacimiento: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.nombres or not self.nombres.strip():
            raise ValueError("Los nombres son obligatorios")
        if not self.apellidos or not self.apellidos.strip():
            raise ValueError("Los apellidos son obligatorios")
        if self.fecha_nacimiento and self.fecha_nacimiento > datetime.now():
            raise ValueError("La fecha de nacimiento no puede ser futura")


@dataclass(frozen=True)
class DocumentoIdentidad:
    """Documento de identidad del afiliado."""
    tipo: TipoDocumento
    numero: str
    fecha_expedicion: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.numero or not self.numero.strip():
            raise ValueError("El número de documento es obligatorio")
        if len(self.numero.strip()) < 3:
            raise ValueError("El número de documento debe tener al menos 3 caracteres")


@dataclass(frozen=True)
class DatosContacto:
    """Datos de contacto del afiliado."""
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    
    def __post_init__(self):
        if not self.email or "@" not in self.email:
            raise ValueError("Email inválido")


@dataclass(frozen=True)
class DatosBancarios:
    """Datos bancarios para pagos de comisiones."""
    banco: str
    tipo_cuenta: str  # AHORROS, CORRIENTE
    numero_cuenta: str
    titular: str
    
    def __post_init__(self):
        if not all([self.banco, self.tipo_cuenta, self.numero_cuenta, self.titular]):
            raise ValueError("Todos los datos bancarios son obligatorios")
        if self.tipo_cuenta not in ["AHORROS", "CORRIENTE"]:
            raise ValueError("Tipo de cuenta debe ser AHORROS o CORRIENTE")


@dataclass(frozen=True)
class ConfiguracionComisiones:
    """Configuración de comisiones del afiliado."""
    porcentaje_base: Decimal
    porcentaje_premium: Optional[Decimal] = None
    monto_minimo: Optional[Decimal] = None
    
    def __post_init__(self):
        if self.porcentaje_base < 0 or self.porcentaje_base > 100:
            raise ValueError("El porcentaje base debe estar entre 0 y 100")
        if self.porcentaje_premium and (self.porcentaje_premium < 0 or self.porcentaje_premium > 100):
            raise ValueError("El porcentaje premium debe estar entre 0 y 100")
        if self.monto_minimo and self.monto_minimo < 0:
            raise ValueError("El monto mínimo no puede ser negativo")


@dataclass(frozen=True)
class MetadatosAfiliado:
    """Metadatos adicionales del afiliado."""
    datos: Dict[str, Any]
    
    def __post_init__(self):
        if not isinstance(self.datos, dict):
            raise ValueError("Los metadatos deben ser un diccionario")


@dataclass(frozen=True)
class Referencia:
    """Referencia de afiliado a otro afiliado."""
    afiliado_referido_id: str
    fecha_referencia: datetime
    estado: str  # ACTIVO, INACTIVO
    
    def __post_init__(self):
        if not self.afiliado_referido_id:
            raise ValueError("ID del afiliado referido es obligatorio")
        if self.estado not in ["ACTIVO", "INACTIVO"]:
            raise ValueError("Estado de referencia debe ser ACTIVO o INACTIVO")