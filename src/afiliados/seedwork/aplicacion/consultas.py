"""
Consultas y manejadores base para aplicación - CQRS con principios SOLID
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Tipos genéricos para consultas
TConsulta = TypeVar('TConsulta', bound='Consulta')
TResultado = TypeVar('TResultado')

@dataclass(frozen=True)
class Consulta:
    """Consulta base - Principio de Responsabilidad Única"""
    id: str = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.id is None:
            import uuid
            object.__setattr__(self, 'id', str(uuid.uuid4()))
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.now())

@dataclass(frozen=True)
class Filtro:
    """Filtro base para consultas paginadas"""
    page: int = 1
    size: int = 10
    sort_by: str = "id"
    sort_order: str = "asc"  # asc o desc

@dataclass(frozen=True)
class ResultadoPaginado(Generic[TResultado]):
    """Resultado paginado genérico"""
    items: List[TResultado]
    total: int
    page: int
    size: int
    total_pages: int

class ManejadorConsulta(ABC, Generic[TConsulta, TResultado]):
    """
    Manejador base abstracto para consultas
    Principio de Inversión de Dependencias - depende de abstracciones
    """
    
    @abstractmethod
    async def manejar(self, consulta: TConsulta) -> TResultado:
        """Maneja la ejecución de una consulta específica"""
        pass

class BusConsultas(ABC):
    """
    Interface para bus de consultas
    Principio de Segregación de Interfaces - separado del bus de comandos
    """
    
    @abstractmethod
    async def ejecutar(self, consulta: Consulta) -> Any:
        """Ejecuta una consulta usando el manejador apropiado"""
        pass

class RepositorioConsultas(ABC, Generic[TResultado]):
    """
    Interface base para repositorios de consulta (solo lectura)
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def obtener_por_id(self, id: str) -> Optional[TResultado]:
        """Obtiene una entidad por ID"""
        pass
    
    @abstractmethod
    async def listar_con_filtro(self, filtro: Filtro) -> ResultadoPaginado[TResultado]:
        """Lista entidades con filtros y paginación"""
        pass
    
    @abstractmethod
    async def buscar(self, criterios: dict) -> List[TResultado]:
        """Busca entidades por criterios específicos"""
        pass