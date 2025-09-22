from afiliados.seedwork.aplicacion.comandos import Comando
from dataclasses import dataclass
from typing import Optional

@dataclass
class CrearAfiliado(Comando):
    id_afiliado: str
    nombre: str
    email: str
    tipo_afiliado: str  # INDIVIDUAL, EMPRESA, INFLUENCER
    nivel_comision: str  # BASICO, PREMIUM, VIP
    fecha_registro: Optional[str] = None
    condiciones_especiales: Optional[str] = None

@dataclass
class ActualizarAfiliado(Comando):
    id_afiliado: str
    nombre: Optional[str] = None
    email: Optional[str] = None
    tipo_afiliado: Optional[str] = None
    nivel_comision: Optional[str] = None
    condiciones_especiales: Optional[str] = None

@dataclass
class ActivarAfiliado(Comando):
    id_afiliado: str
    fecha_activacion: Optional[str] = None

@dataclass
class DesactivarAfiliado(Comando):
    id_afiliado: str
    razon: str
    fecha_desactivacion: Optional[str] = None
