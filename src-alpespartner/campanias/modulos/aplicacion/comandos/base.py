from abc import ABC, abstractmethod
from campanias.seedwork.aplicacion.comandos import ComandoHandler
from campanias.modulos.infraestructura.fabricas import FabricaRepositorios, FabricaCampanias

class CrearCampaniaBaseHandler(ComandoHandler, ABC):
    """Handler base para operaciones con campanias siguiendo el patrón AeroAlpes"""
    
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorios = FabricaRepositorios()
        self._fabrica_campanias: FabricaCampanias = FabricaCampanias()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio

    @property
    def fabrica_campanias(self):
        return self._fabrica_campanias

    @abstractmethod
    def handle(self, comando):
        """Método abstracto que deben implementar los handlers específicos"""
        raise NotImplementedError()