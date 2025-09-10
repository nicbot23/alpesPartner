from dataclasses import dataclass, field
from typing import List
from .eventos import EventoDominio

@dataclass
class Entidad: 
    id:str

@dataclass
class RaizAgregado(Entidad):
    _eventos: List[EventoDominio] = field(default_factory=list, init=False, repr=False)
    
    def agregar_evento(self, evt: EventoDominio): 
        self._eventos.append(evt)
    
    def pull_eventos(self)->list[EventoDominio]: 
        ev=list(self._eventos)
        self._eventos.clear()
        return ev
