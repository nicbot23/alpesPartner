"""
Manejadores base para comandos del seedwork
"""
from abc import ABC, abstractmethod

class ManejadorComandoBase(ABC):
    """Manejador base para comandos"""
    
    @abstractmethod
    async def handle(self, comando):
        """Maneja un comando"""
        pass