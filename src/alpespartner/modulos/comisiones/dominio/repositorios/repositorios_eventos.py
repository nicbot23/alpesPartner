"""Interfaces para repositorios de eventos del dominio de comisiones

En este archivo usted encontrará las diferentes interfaces para repositorios
de eventos del dominio de comisiones

"""

from abc import ABC, abstractmethod
from alpespartner.modulos.comisiones.dominio.eventos import EventoComision

class RepositorioEventosComision(ABC):
    @abstractmethod
    def agregar(self, evento: EventoComision):
        ...
