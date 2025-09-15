"""
Eventos de dominio del módulo de afiliados
"""
from dataclasses import dataclass
from afiliados.seedwork.dominio.eventos import EventoDominio
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class AfiliadoRegistrado(EventoDominio):
    """Evento que indica que un afiliado ha sido registrado en el sistema"""
    nombre: str = ""
    tipo_afiliacion: str = ""  # individual, empresa, etc.
    email: str = ""
    telefono: str = ""
    direccion: str = ""
    
    def __init__(self, nombre: str, tipo_afiliacion: str, email: str, telefono: str = "", direccion: str = "", **kwargs):
        super().__init__(nombre="AfiliadoRegistrado", **kwargs)
        object.__setattr__(self, 'nombre', nombre)
        object.__setattr__(self, 'tipo_afiliacion', tipo_afiliacion)
        object.__setattr__(self, 'email', email)
        object.__setattr__(self, 'telefono', telefono)
        object.__setattr__(self, 'direccion', direccion)

@dataclass(frozen=True)
class AfiliadoAprobado(EventoDominio):
    """Evento que indica que un afiliado ha sido aprobado"""
    afiliado_id: str = ""
    fecha_aprobacion: Optional[datetime] = None
    aprobado_por: str = ""
    observaciones: str = ""
    
    def __init__(self, afiliado_id: str, aprobado_por: str, observaciones: str = "", **kwargs):
        super().__init__(nombre="AfiliadoAprobado", **kwargs)
        object.__setattr__(self, 'afiliado_id', afiliado_id)
        object.__setattr__(self, 'fecha_aprobacion', datetime.now())
        object.__setattr__(self, 'aprobado_por', aprobado_por)
        object.__setattr__(self, 'observaciones', observaciones)

@dataclass(frozen=True)
class AfiliadoRechazado(EventoDominio):
    """Evento que indica que un afiliado ha sido rechazado"""
    afiliado_id: str = ""
    fecha_rechazo: Optional[datetime] = None
    rechazado_por: str = ""
    razon_rechazo: str = ""
    
    def __init__(self, afiliado_id: str, rechazado_por: str, razon_rechazo: str, **kwargs):
        super().__init__(nombre="AfiliadoRechazado", **kwargs)
        object.__setattr__(self, 'afiliado_id', afiliado_id)
        object.__setattr__(self, 'fecha_rechazo', datetime.now())
        object.__setattr__(self, 'rechazado_por', rechazado_por)
        object.__setattr__(self, 'razon_rechazo', razon_rechazo)

@dataclass(frozen=True)
class AfiliadoActualizado(EventoDominio):
    """Evento que indica que los datos de un afiliado han sido actualizados"""
    afiliado_id: str = ""
    campos_actualizados: str = ""  # JSON con los campos que cambiaron
    actualizado_por: str = ""
    
    def __init__(self, afiliado_id: str, campos_actualizados: str, actualizado_por: str, **kwargs):
        super().__init__(nombre="AfiliadoActualizado", **kwargs)
        object.__setattr__(self, 'afiliado_id', afiliado_id)
        object.__setattr__(self, 'campos_actualizados', campos_actualizados)
        object.__setattr__(self, 'actualizado_por', actualizado_por)

@dataclass(frozen=True)
class AfiliadoDesactivado(EventoDominio):
    """Evento que indica que un afiliado ha sido desactivado"""
    afiliado_id: str = ""
    fecha_desactivacion: Optional[datetime] = None
    desactivado_por: str = ""
    razon_desactivacion: str = ""
    
    def __init__(self, afiliado_id: str, desactivado_por: str, razon_desactivacion: str, **kwargs):
        super().__init__(nombre="AfiliadoDesactivado", **kwargs)
        object.__setattr__(self, 'afiliado_id', afiliado_id)
        object.__setattr__(self, 'fecha_desactivacion', datetime.now())
        object.__setattr__(self, 'desactivado_por', desactivado_por)
        object.__setattr__(self, 'razon_desactivacion', razon_desactivacion)