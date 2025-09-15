"""Fábricas abstractas para la creación de objetos complejos

En este archivo usted encontrará las diferentes interfaces para fábricas
que permiten crear objetos complejos

"""

from abc import ABC, abstractmethod

class Fabrica(ABC):
    @abstractmethod
    def crear_objeto(self, obj: any, mapeador: any = None) -> any:
        ...
