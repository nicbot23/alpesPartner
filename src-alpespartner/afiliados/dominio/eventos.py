from dataclasses import dataclass
from afiliados.seedwork.dominio.eventos import EventoDominio

@dataclass
class AfiliadoCreado(EventoDominio):
    id_afiliado: str
    nombre: str
    email: str
    tipo_afiliado: str
    nivel_comision: str
    fecha_registro: str

@dataclass
class AfiliadoActualizado(EventoDominio):
    id_afiliado: str
    cambios: dict

@dataclass
class AfiliadoActivado(EventoDominio):
    id_afiliado: str
    fecha_activacion: str

@dataclass
class AfiliadoDesactivado(EventoDominio):
    id_afiliado: str
    razon: str
    fecha_desactivacion: str
