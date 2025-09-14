"""
Eventos de dominio y interfaces relacionadas - Seedwork con principios SOLID
"""
from dataclasses import dataclass, field
from datetime import datetime
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion
import uuid
from typing import Optional, TypeVar, Type, List, Protocol
from abc import ABC, abstractmethod

E = TypeVar('E', bound='EventoDominio')

@dataclass(frozen=True)
class EventoDominio:
    """
    Evento de dominio base
    Principio de Responsabilidad Única - solo representa un evento
    """
    nombre: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    fecha: datetime = field(default_factory=datetime.now)
    # Identificador que permite correlacionar una cadena de eventos (trazabilidad end-to-end)
    correlation_id: Optional[str] = None
    # Identificador del evento que causó (directamente) este evento
    causation_id: Optional[str] = None
    # Versión del evento para compatibilidad
    version: int = 1

    @classmethod
    def siguiente_id(cls) -> uuid.UUID:
        return uuid.uuid4()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: uuid.UUID) -> None:
        if not IdEntidadEsInmutable(self).es_valido():
            raise IdDebeSerInmutableExcepcion()
        self._id = self.siguiente_id()

    def encadenar(self: E, nuevo_evento_cls: Type[E], **kwargs) -> E:
        """
        Crea un nuevo evento que desciende de este preservando correlation/causation.
        Principio Abierto/Cerrado - extensible sin modificar
        """
        base_corr = self.correlation_id or str(self.id)
        return nuevo_evento_cls(
            correlation_id=base_corr,
            causation_id=str(self.id),
            **kwargs
        )

# Eventos de integración para comunicación entre bounded contexts
@dataclass(frozen=True)
class EventoIntegracion(EventoDominio):
    """
    Evento de integración para comunicación entre microservicios
    Principio de Segregación de Interfaces - tipo específico
    """
    schema_version: str = "1.0"
    source_service: str = ""
    destination_services: List[str] = field(default_factory=list)

class ManejadorEventos(ABC):
    """
    Interface para manejadores de eventos
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def manejar(self, evento: EventoDominio) -> None:
        """Maneja un evento específico"""
        pass

class DespachadorEventos(ABC):
    """
    Interface para despachador de eventos
    Principio de Segregación de Interfaces
    """
    
    @abstractmethod
    async def publicar(self, evento: EventoDominio) -> None:
        """Publica un evento"""
        pass
    
    @abstractmethod
    async def publicar_eventos(self, eventos: List[EventoDominio]) -> None:
        """Publica múltiples eventos de forma atómica"""
        pass

class RepositorioEventos(ABC):
    """
    Interface para repositorio de eventos (Event Store)
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def guardar_evento(self, evento: EventoDominio) -> None:
        """Guarda un evento en el store"""
        pass
    
    @abstractmethod
    async def obtener_eventos(self, agregado_id: str) -> List[EventoDominio]:
        """Obtiene todos los eventos de un agregado"""
        pass
    
    @abstractmethod
    async def obtener_eventos_desde(self, agregado_id: str, desde_version: int) -> List[EventoDominio]:
        """Obtiene eventos desde una versión específica"""
        pass

# Protocolo para entidades que pueden generar eventos
class GeneradorEventos(Protocol):
    """
    Protocolo para entidades que generan eventos
    Principio de Segregación de Interfaces
    """
    eventos: List[EventoDominio]
    
    def agregar_evento(self, evento: EventoDominio) -> None:
        """Agrega un evento a la entidad"""
        ...
    
    def limpiar_eventos(self) -> None:
        """Limpia los eventos de la entidad"""
        ...