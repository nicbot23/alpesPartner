"""
Patrón Outbox para el microservicio Marketing
Garantiza consistencia eventual en eventos de marketing
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
import json

from ..dominio.eventos import EventoDominio, EventoIntegracion, DespachadorEventos

class PrioridadEvento(Enum):
    """Enum para prioridades de eventos en outbox"""
    ALTA = 1
    MEDIA = 2
    BAJA = 3

class EstadoEvento(Enum):
    """Enum para estados de eventos en outbox"""
    PENDIENTE = "pendiente"
    PUBLICADO = "publicado"
    ERROR = "error"
    REINTENTANDO = "reintentando"

@dataclass
class EventoOutboxMarketing:
    """
    Representa un evento de marketing en la tabla outbox
    Principio de Responsabilidad Única - almacenar evento para publicación
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agregado_id: str = ""
    tipo_evento: str = ""
    datos_evento: str = ""  # JSON serializado del evento
    contexto_marketing: str = ""  # Contexto específico de marketing
    segmento_objetivo: Optional[str] = None
    campana_id: Optional[str] = None
    version: int = 1
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_publicacion: Optional[datetime] = None
    estado: str = "pendiente"  # pendiente, publicado, error
    intentos: int = 0
    ultimo_error: str = ""
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    prioridad: int = 1  # 1=alta, 2=media, 3=baja

    @classmethod
    def desde_evento_dominio(
        cls, 
        evento: EventoDominio, 
        agregado_id: str,
        contexto_marketing: str = "",
        campana_id: str = None
    ) -> 'EventoOutboxMarketing':
        """Factory method para crear desde evento de dominio de marketing"""
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
            contexto_marketing=contexto_marketing,
            campana_id=campana_id,
            correlation_id=evento.correlation_id,
            causation_id=evento.causation_id,
            prioridad=cls._determinar_prioridad(evento.__class__.__name__)
        )
    
    @staticmethod
    def _determinar_prioridad(tipo_evento: str) -> int:
        """Determina prioridad basada en el tipo de evento"""
        eventos_alta_prioridad = [
            "CampanaActivada", "CampanaDesactivada", 
            "SegmentacionCalculada", "ErrorCriticoMarketing"
        ]
        eventos_media_prioridad = [
            "CampanaCreada", "CampanaModificada",
            "InteraccionRegistrada"
        ]
        
        if tipo_evento in eventos_alta_prioridad:
            return 1
        elif tipo_evento in eventos_media_prioridad:
            return 2
        else:
            return 3
    
    def marcar_como_publicado(self):
        """Marca el evento como publicado exitosamente"""
        self.estado = "publicado"
        self.fecha_publicacion = datetime.now()
    
    def marcar_como_error(self, error: str):
        """Marca el evento con error e incrementa intentos"""
        self.estado = "error"
        self.ultimo_error = error
        self.intentos += 1

class RepositorioOutboxMarketing(ABC):
    """
    Interface para repositorio de eventos outbox de Marketing
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def agregar_evento(self, evento_outbox: EventoOutboxMarketing) -> None:
        """Agrega un evento al outbox de marketing"""
        pass
    
    @abstractmethod
    async def obtener_eventos_pendientes(
        self, 
        limite: int = 100,
        prioridad_maxima: int = 3
    ) -> List[EventoOutboxMarketing]:
        """Obtiene eventos pendientes ordenados por prioridad"""
        pass
    
    @abstractmethod
    async def obtener_eventos_por_campana(self, campana_id: str) -> List[EventoOutboxMarketing]:
        """Obtiene eventos relacionados con una campaña específica"""
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
    async def obtener_eventos_con_error(self, max_intentos: int = 3) -> List[EventoOutboxMarketing]:
        """Obtiene eventos que han fallado pero no han excedido el máximo de intentos"""
        pass
    
    @abstractmethod
    async def limpiar_eventos_antiguos(self, dias: int = 30) -> int:
        """Limpia eventos publicados exitosamente más antiguos que X días"""
        pass

class ProcesadorOutboxMarketing(ABC):
    """
    Interface para procesar eventos del outbox de Marketing
    Principio de Segregación de Interfaces
    """
    
    @abstractmethod
    async def procesar_eventos_pendientes(self) -> None:
        """Procesa todos los eventos pendientes por prioridad"""
        pass
    
    @abstractmethod
    async def procesar_eventos_campana(self, campana_id: str) -> None:
        """Procesa eventos específicos de una campaña"""
        pass
    
    @abstractmethod
    async def reintentar_eventos_con_error(self) -> None:
        """Reintentar eventos que han fallado"""
        pass

class ServicioOutboxMarketing:
    """
    Servicio para gestionar el patrón outbox específico de Marketing
    Principio de Responsabilidad Única - coordinar outbox de marketing
    """
    
    def __init__(
        self, 
        repositorio_outbox: RepositorioOutboxMarketing,
        despachador_eventos: 'DespachadorEventos'
    ):
        self._repositorio = repositorio_outbox
        self._despachador = despachador_eventos
    
    async def guardar_eventos_campana(
        self, 
        campana_id: str, 
        eventos: List[EventoDominio],
        contexto_marketing: str = ""
    ) -> None:
        """
        Guarda eventos relacionados con campañas en el outbox
        Se ejecuta en la misma transacción que el guardado de la campaña
        """
        for evento in eventos:
            evento_outbox = EventoOutboxMarketing.desde_evento_dominio(
                evento, 
                campana_id,
                contexto_marketing,
                campana_id
            )
            await self._repositorio.agregar_evento(evento_outbox)
    
    async def guardar_eventos_segmentacion(
        self, 
        segmento_id: str, 
        eventos: List[EventoDominio]
    ) -> None:
        """
        Guarda eventos relacionados con segmentación
        """
        for evento in eventos:
            evento_outbox = EventoOutboxMarketing.desde_evento_dominio(
                evento, 
                segmento_id,
                "segmentacion"
            )
            await self._repositorio.agregar_evento(evento_outbox)
    
    async def publicar_eventos_pendientes(self, procesar_solo_alta_prioridad: bool = False) -> None:
        """
        Publica eventos pendientes del outbox priorizando por urgencia
        Se ejecuta de forma asíncrona, separada de la transacción principal
        """
        prioridad_maxima = 1 if procesar_solo_alta_prioridad else 3
        eventos_pendientes = await self._repositorio.obtener_eventos_pendientes(
            prioridad_maxima=prioridad_maxima
        )
        
        for evento_outbox in eventos_pendientes:
            try:
                # Convertir EventoOutbox de vuelta a EventoDominio
                datos_evento = json.loads(evento_outbox.datos_evento)
                
                # Crear evento de integración para otros microservicios
                evento_integracion = EventoIntegracion(
                    nombre=datos_evento.get('nombre', ''),
                    correlation_id=evento_outbox.correlation_id,
                    causation_id=evento_outbox.causation_id,
                    source_service="marketing",
                    destination_services=self._determinar_servicios_destino(
                        evento_outbox.tipo_evento,
                        evento_outbox.contexto_marketing
                    )
                )
                
                # Agregar metadatos específicos de marketing
                evento_integracion.metadatos_marketing = {
                    "campana_id": evento_outbox.campana_id,
                    "segmento_objetivo": evento_outbox.segmento_objetivo,
                    "contexto": evento_outbox.contexto_marketing,
                    "prioridad": evento_outbox.prioridad
                }
                
                await self._despachador.publicar(evento_integracion)
                await self._repositorio.marcar_como_publicado(evento_outbox.id)
                
            except Exception as e:
                await self._repositorio.marcar_como_error(evento_outbox.id, str(e))
    
    async def publicar_eventos_campana_urgente(self, campana_id: str) -> None:
        """
        Publica inmediatamente todos los eventos pendientes de una campaña específica
        Útil para campañas de alta prioridad o eventos críticos
        """
        eventos_campana = await self._repositorio.obtener_eventos_por_campana(campana_id)
        eventos_pendientes = [e for e in eventos_campana if e.estado == "pendiente"]
        
        for evento_outbox in eventos_pendientes:
            try:
                datos_evento = json.loads(evento_outbox.datos_evento)
                
                evento_integracion = EventoIntegracion(
                    nombre=datos_evento.get('nombre', ''),
                    correlation_id=evento_outbox.correlation_id,
                    causation_id=evento_outbox.causation_id,
                    source_service="marketing",
                    destination_services=self._determinar_servicios_destino(
                        evento_outbox.tipo_evento,
                        evento_outbox.contexto_marketing
                    )
                )
                
                evento_integracion.metadatos_marketing = {
                    "campana_id": evento_outbox.campana_id,
                    "procesamiento": "urgente",
                    "contexto": evento_outbox.contexto_marketing
                }
                
                await self._despachador.publicar(evento_integracion)
                await self._repositorio.marcar_como_publicado(evento_outbox.id)
                
            except Exception as e:
                await self._repositorio.marcar_como_error(evento_outbox.id, str(e))
    
    def _determinar_servicios_destino(
        self, 
        tipo_evento: str, 
        contexto_marketing: str
    ) -> List[str]:
        """
        Determina qué servicios deben recibir el evento basado en el contexto de marketing
        """
        mapping_eventos = {
            # Eventos de campaña
            "CampanaCreada": ["conversiones"],
            "CampanaActivada": ["afiliados", "conversiones"],
            "CampanaDesactivada": ["afiliados", "conversiones"],
            "CampanaModificada": ["conversiones"],
            
            # Eventos de segmentación
            "SegmentacionCalculada": ["afiliados"],
            "SegmentoCreado": ["afiliados"],
            "SegmentoActualizado": ["afiliados"],
            
            # Eventos de interacción
            "InteraccionRegistrada": ["conversiones"],
            "ConversionAtribuida": ["conversiones"],
            
            # Eventos críticos
            "ErrorCriticoMarketing": ["afiliados", "conversiones"],
            "AlertaRendimientoCampana": ["conversiones"]
        }
        
        servicios_base = mapping_eventos.get(tipo_evento, [])
        
        # Agregar servicios específicos basados en contexto
        if contexto_marketing == "segmentacion" and "afiliados" not in servicios_base:
            servicios_base.append("afiliados")
        elif contexto_marketing == "conversion_tracking" and "conversiones" not in servicios_base:
            servicios_base.append("conversiones")
        
        return servicios_base

# Interface para inyección de dependencias
class FabricaOutboxMarketing(ABC):
    """
    Factory para crear componentes del outbox de Marketing
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def crear_repositorio_outbox(self) -> RepositorioOutboxMarketing:
        """Crea una instancia del repositorio outbox de marketing"""
        pass
    
    @abstractmethod
    def crear_servicio_outbox(self) -> ServicioOutboxMarketing:
        """Crea una instancia del servicio outbox de marketing"""
        pass
    
    @abstractmethod
    def crear_procesador_outbox(self) -> ProcesadorOutboxMarketing:
        """Crea una instancia del procesador outbox de marketing"""
        pass