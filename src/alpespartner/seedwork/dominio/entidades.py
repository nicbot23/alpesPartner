from dataclasses import dataclass, field
from typing import List
from .eventos import EventoDominio
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion
from datetime import datetime
import uuid

@dataclass
class Entidad: 
    id: uuid.UUID = field(hash=True)
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    fecha_creacion: datetime = field(default=datetime.now())
    fecha_actualizacion: datetime = field(default=datetime.now())

    @classmethod
    def siguiente_id(cls) -> uuid.UUID:
        return uuid.uuid4()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: uuid.UUID) -> None:
        if not IdEntidadEsInmutable(self).es_valido():
            raise IdDebeSerInmutableExcepcion()
        self._id = self.siguiente_id()

@dataclass
class AgregacionRaiz(Entidad):
    eventos: list[EventoDominio] = field(default_factory=list)
    
    def agregar_evento(self, evento: EventoDominio): 
        self.eventos.append(evento)
    
    def limpiar_eventos(self):
        self.eventos = list()

# Mantener compatibilidad hacia atrás
@dataclass
class RaizAgregado(AgregacionRaiz):
    """Deprecated: Use AgregacionRaiz instead"""
    _eventos: List[EventoDominio] = field(default_factory=list, init=False, repr=False)
    
    def agregar_evento(self, evt: EventoDominio): 
        super().agregar_evento(evt)
        self._eventos.append(evt)
    
    def pull_eventos(self)->list[EventoDominio]: 
        ev=list(self._eventos)
        self._eventos.clear()
        return ev
