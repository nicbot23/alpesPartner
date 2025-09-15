"""
Patrón Outbox para garantizar consistencia eventual
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
import json

from ..dominio.eventos import EventoDominio, EventoIntegracion, DespachadorEventos

@dataclass
class EventoOutbox:
    """
    Representa un evento en la tabla outbox
    Principio de Responsabilidad Única - solo almacenar evento para publicación
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agregado_id: str = ""
    tipo_evento: str = ""
    datos_evento: str = ""  # JSON serializado del evento
    version: int = 1
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_publicacion: Optional[datetime] = None
    estado: str = "pendiente"  # pendiente, publicado, error
    intentos: int = 0
    ultimo_error: str = ""
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None

    @classmethod
    def desde_evento_dominio(cls, evento: EventoDominio, agregado_id: str) -> 'EventoOutbox':
        """Factory method para crear desde evento de dominio"""
        return cls(
            agregado_id=agregado_id,
            tipo_evento=evento.__class__.__name__,
            datos_evento=json.dumps({
                'nombre': evento.nombre,
                'id': str(evento.id),
                'fecha': evento.fecha.isoformat(),
                'correlation_id': evento.correlation_id,
                'causation_id': evento.causation_id,
                'version': getattr(evento, 'version', 1),
                **evento.__dict__
            }),
            correlation_id=evento.correlation_id,
            causation_id=evento.causation_id
        )
    
    def marcar_como_publicado(self):
        """Marca el evento como publicado exitosamente"""
        self.estado = "publicado"
        self.fecha_publicacion = datetime.now()
    
    def marcar_como_error(self, error: str):
        """Marca el evento con error e incrementa intentos"""
        self.estado = "error"
        self.ultimo_error = error
        self.intentos += 1

class RepositorioOutbox(ABC):
    """
    Interface para repositorio de eventos outbox
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def agregar_evento(self, evento_outbox: EventoOutbox) -> None:
        """Agrega un evento al outbox"""
        pass
    
    @abstractmethod
    async def obtener_eventos_pendientes(self, limite: int = 100) -> List[EventoOutbox]:
        """Obtiene eventos pendientes de publicación"""
        pass
    
    @abstractmethod
    async def marcar_como_publicado(self, evento_id: str) -> None:
        """Marca un evento como publicado"""
        pass
    
    @abstractmethod
    async def marcar_como_error(self, evento_id: str, error: str) -> None:
        """Marca un evento con error"""
        pass
    
    @abstractmethod
    async def obtener_eventos_con_error(self, max_intentos: int = 3) -> List[EventoOutbox]:
        """Obtiene eventos que han fallado pero no han excedido el máximo de intentos"""
        pass

class ProcesadorOutbox(ABC):
    """
    Interface para procesar eventos del outbox
    Principio de Segregación de Interfaces
    """
    
    @abstractmethod
    async def procesar_eventos_pendientes(self) -> None:
        """Procesa todos los eventos pendientes"""
        pass
    
    @abstractmethod
    async def reintentar_eventos_con_error(self) -> None:
        """Reintentar eventos que han fallado"""
        pass

class ServicioOutbox:
    """
    Servicio para gestionar el patrón outbox
    Principio de Responsabilidad Única - coordinar outbox
    """
    
    def __init__(
        self, 
        repositorio_outbox: RepositorioOutbox,
        despachador_eventos: DespachadorEventos
    ):
        self._repositorio = repositorio_outbox
        self._despachador = despachador_eventos
    
    async def guardar_eventos_agregado(self, agregado_id: str, eventos: List[EventoDominio]) -> None:
        """
        Guarda eventos de un agregado en el outbox
        Se ejecuta en la misma transacción que el guardado del agregado
        """
        for evento in eventos:
            evento_outbox = EventoOutbox.desde_evento_dominio(evento, agregado_id)
            await self._repositorio.agregar_evento(evento_outbox)
    
    async def publicar_eventos_pendientes(self) -> None:
        """
        Publica eventos pendientes del outbox
        Se ejecuta de forma asíncrona, separada de la transacción principal
        """
        eventos_pendientes = await self._repositorio.obtener_eventos_pendientes()
        
        for evento_outbox in eventos_pendientes:
            try:
                # Convertir EventoOutbox de vuelta a EventoDominio
                datos_evento = json.loads(evento_outbox.datos_evento)
                
                # Crear evento de integración para otros microservicios
                evento_integracion = EventoIntegracion(
                    nombre=datos_evento.get('nombre', ''),
                    correlation_id=evento_outbox.correlation_id,
                    causation_id=evento_outbox.causation_id,
                    source_service="afiliados",
                    destination_services=self._determinar_servicios_destino(evento_outbox.tipo_evento)
                )
                
                await self._despachador.publicar(evento_integracion)
                await self._repositorio.marcar_como_publicado(evento_outbox.id)
                
            except Exception as e:
                await self._repositorio.marcar_como_error(evento_outbox.id, str(e))
    
    def _determinar_servicios_destino(self, tipo_evento: str) -> List[str]:
        """
        Determina qué servicios deben recibir el evento
        Basado en el tipo de evento y la lógica de negocio
        """
        mapping_eventos = {
            "AfiliadoRegistrado": ["marketing"],
            "AfiliadoAprobado": ["marketing", "conversiones"],
            "AfiliadoRechazado": ["marketing"],
            "AfiliadoDesactivado": ["marketing", "conversiones"]
        }
        
        return mapping_eventos.get(tipo_evento, [])

# Interface para inyección de dependencias
class FabricaOutbox(ABC):
    """
    Factory para crear componentes del outbox
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def crear_repositorio_outbox(self) -> RepositorioOutbox:
        """Crea una instancia del repositorio outbox"""
        pass
    
    @abstractmethod
    def crear_servicio_outbox(self) -> ServicioOutbox:
        """Crea una instancia del servicio outbox"""
        pass