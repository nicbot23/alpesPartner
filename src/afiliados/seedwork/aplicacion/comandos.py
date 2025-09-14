"""
Comandos y manejadores base para aplicación - Seedwork con principios SOLID
"""
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Dict
import uuid
from datetime import datetime

# Tipo genérico para comandos
TComando = TypeVar('TComando', bound='Comando')
TResultado = TypeVar('TResultado')

@dataclass(frozen=True)
class Comando:
    """Comando base - Principio de Responsabilidad Única"""
    id: str = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.id is None:
            object.__setattr__(self, 'id', str(uuid.uuid4()))
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.now())

# Alias para compatibilidad
ComandoAplicacion = Comando

class ManejadorComando(ABC, Generic[TComando, TResultado]):
    """
    Manejador base abstracto para comandos
    Principio de Inversión de Dependencias - depende de abstracciones
    """
    
    @abstractmethod
    async def manejar(self, comando: TComando) -> TResultado:
        """Maneja la ejecución de un comando específico"""
        pass

class BusComandos(ABC):
    """
    Interface para bus de comandos
    Principio de Segregación de Interfaces - interface específica
    """
    
    @abstractmethod
    async def enviar(self, comando: Comando) -> Any:
        """Envía un comando al manejador apropiado"""
        pass

class RepositorioComandos(ABC):
    """
    Interface para persistir comandos (para auditoría)
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def guardar_comando(self, comando: Comando) -> None:
        """Guarda un comando para auditoría"""
        pass
    
    @abstractmethod
    async def obtener_comando(self, comando_id: str) -> Comando:
        """Obtiene un comando por ID"""
        pass