"""
Comandos del módulo de afiliados
"""
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from typing import Optional

@dataclass(frozen=True)
class RegistrarAfiliado(Comando):
    """Comando para registrar un nuevo afiliado"""
    nombre: str
    tipo_afiliacion: str
    email: str
    telefono: str = ""
    direccion: str = ""

@dataclass(frozen=True)
class AprobarAfiliado(Comando):
    """Comando para aprobar un afiliado"""
    afiliado_id: str
    aprobado_por: str
    observaciones: str = ""

@dataclass(frozen=True)
class RechazarAfiliado(Comando):
    """Comando para rechazar un afiliado"""
    afiliado_id: str
    rechazado_por: str
    razon_rechazo: str

@dataclass(frozen=True)
class ActualizarAfiliado(Comando):
    """Comando para actualizar datos de un afiliado"""
    afiliado_id: str
    actualizado_por: str
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    observaciones: Optional[str] = None

@dataclass(frozen=True)
class DesactivarAfiliado(Comando):
    """Comando para desactivar un afiliado"""
    afiliado_id: str
    desactivado_por: str
    razon_desactivacion: str