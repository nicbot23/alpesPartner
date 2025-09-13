"""
Handlers base del seedwork
"""

from abc import ABC, abstractmethod

class Handler:
    """Clase base para handlers (mantener compatibilidad)"""
    ...

class ManejadorComando(ABC):
    """Clase base abstracta para manejadores de comandos"""
    
    @abstractmethod
    def manejar(self, comando):
        """Maneja la ejecución de un comando específico"""
        raise NotImplementedError()