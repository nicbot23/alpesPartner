from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class Comando: 
    pass

# Alias para compatibilidad
ComandoAplicacion = Comando

class ManejadorComando(ABC):
    """Clase base abstracta para manejadores de comandos"""
    
    @abstractmethod
    def manejar(self, comando: Comando):
        """Maneja la ejecución de un comando específico"""
        raise NotImplementedError()
