from abc import ABC, abstractmethod
class Repositorio(ABC):
    @abstractmethod
    def agregar(self, agregado): ...
