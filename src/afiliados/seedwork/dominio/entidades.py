"""
Entidades base de dominio con principios SOLID
"""
from dataclasses import dataclass, field
from typing import List, Protocol, Optional
from .eventos import EventoDominio, GeneradorEventos
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion
from datetime import datetime
import uuid
from abc import ABC, abstractmethod

@dataclass
class Entidad: 
    """
    Entidad base de dominio
    Principio de Responsabilidad Única - identidad única
    """
    id: uuid.UUID = field(hash=True)
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)

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
    
    def marcar_como_modificada(self):
        """Marca la entidad como modificada actualizando timestamp"""
        self.fecha_actualizacion = datetime.now()

@dataclass
class AgregacionRaiz(Entidad):
    """
    Agregación raíz base
    Principio de Responsabilidad Única - coordina eventos y consistencia
    """
    eventos: List[EventoDominio] = field(default_factory=list)
    version: int = field(default=1)
    
    def agregar_evento(self, evento: EventoDominio) -> None:
        """Agrega un evento de dominio al agregado"""
        self.eventos.append(evento)
        self.marcar_como_modificada()
    
    def limpiar_eventos(self) -> None:
        """Limpia los eventos del agregado después de ser publicados"""
        self.eventos = []
    
    def incrementar_version(self) -> None:
        """Incrementa la versión del agregado para control de concurrencia optimista"""
        self.version += 1

# Interfaces para repositorios siguiendo principios SOLID

class RepositorioLectura(ABC, Protocol):
    """
    Interface para operaciones de lectura
    Principio de Segregación de Interfaces - solo lectura
    """
    
    @abstractmethod
    async def obtener_por_id(self, id: uuid.UUID) -> Optional[Entidad]:
        """Obtiene una entidad por su ID"""
        pass

class RepositorioEscritura(ABC, Protocol):
    """
    Interface para operaciones de escritura
    Principio de Segregación de Interfaces - solo escritura
    """
    
    @abstractmethod
    async def agregar(self, entidad: Entidad) -> None:
        """Agrega una nueva entidad"""
        pass
    
    @abstractmethod
    async def actualizar(self, entidad: Entidad) -> None:
        """Actualiza una entidad existente"""
        pass
    
    @abstractmethod
    async def eliminar(self, id: uuid.UUID) -> None:
        """Elimina una entidad por ID"""
        pass

class RepositorioAgregado(RepositorioLectura, RepositorioEscritura, ABC):
    """
    Interface completa para repositorios de agregados
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def obtener_agregado(self, id: uuid.UUID) -> Optional[AgregacionRaiz]:
        """Obtiene un agregado completo con sus eventos"""
        pass
    
    @abstractmethod
    async def guardar_agregado(self, agregado: AgregacionRaiz) -> None:
        """Guarda un agregado y publica sus eventos"""
        pass

class UnidadDeTrabajo(ABC):
    """
    Interface para patrón Unit of Work
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def commit(self) -> None:
        """Confirma todos los cambios de la unidad de trabajo"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Revierte todos los cambios de la unidad de trabajo"""
        pass
    
    @abstractmethod
    def agregar_agregado(self, agregado: AgregacionRaiz) -> None:
        """Agrega un agregado a la unidad de trabajo"""
        pass

# Especificaciones para consultas complejas

class Especificacion(ABC):
    """
    Interface para patrón Specification
    Principio Abierto/Cerrado - extensible para nuevos criterios
    """
    
    @abstractmethod
    def es_satisfecha_por(self, entidad: Entidad) -> bool:
        """Determina si una entidad satisface la especificación"""
        pass
    
    def y(self, otra: 'Especificacion') -> 'EspecificacionY':
        """Combina especificaciones con AND"""
        return EspecificacionY(self, otra)
    
    def o(self, otra: 'Especificacion') -> 'EspecificacionO':
        """Combina especificaciones con OR"""
        return EspecificacionO(self, otra)
    
    def no(self) -> 'EspecificacionNo':
        """Niega la especificación"""
        return EspecificacionNo(self)

class EspecificacionY(Especificacion):
    """Especificación compuesta con AND"""
    
    def __init__(self, izquierda: Especificacion, derecha: Especificacion):
        self.izquierda = izquierda
        self.derecha = derecha
    
    def es_satisfecha_por(self, entidad: Entidad) -> bool:
        return (self.izquierda.es_satisfecha_por(entidad) and 
                self.derecha.es_satisfecha_por(entidad))

class EspecificacionO(Especificacion):
    """Especificación compuesta con OR"""
    
    def __init__(self, izquierda: Especificacion, derecha: Especificacion):
        self.izquierda = izquierda
        self.derecha = derecha
    
    def es_satisfecha_por(self, entidad: Entidad) -> bool:
        return (self.izquierda.es_satisfecha_por(entidad) or 
                self.derecha.es_satisfecha_por(entidad))

class EspecificacionNo(Especificacion):
    """Especificación negada"""
    
    def __init__(self, especificacion: Especificacion):
        self.especificacion = especificacion
    
    def es_satisfecha_por(self, entidad: Entidad) -> bool:
        return not self.especificacion.es_satisfecha_por(entidad)