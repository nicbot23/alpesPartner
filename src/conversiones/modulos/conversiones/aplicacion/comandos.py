"""
Comandos de aplicación para el microservicio Conversiones
"""
from dataclasses import dataclass
from ....seedwork.aplicacion.comandos import Comando


@dataclass(frozen=True)
class DetectarConversion(Comando):
    user_id: str = ""
    tipo_conversion: str = ""
    valor: str = ""
    moneda: str = "USD"
    metadata: str = ""


@dataclass(frozen=True)
class ValidarConversion(Comando):
    conversion_id: str = ""
    user_id: str = ""
    observaciones: str = ""


@dataclass(frozen=True)
class RechazarConversion(Comando):
    conversion_id: str = ""
    user_id: str = ""
    razon_rechazo: str = ""
    observaciones: str = ""


@dataclass(frozen=True)
class ActualizarConversion(Comando):
    conversion_id: str = ""
    user_id: str = ""
    nuevo_valor: str = ""
    tipo_actualizacion: str = ""