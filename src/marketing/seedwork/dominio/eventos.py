"""
Eventos de dominio base para el microservicio Marketing
Implementa principios SOLID y patrones de eventos
"""
from abc import ABC, abstractmethod, Protocol
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, TypeVar
import uuid

# Principio de Responsabilidad Única - Base para todos los eventos
@dataclass
class EventoDominio(ABC):
    """
    Clase base para eventos de dominio
    Principio de Responsabilidad Única - representa algo que ha sucedido
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str = ""
    fecha: datetime = field(default_factory=datetime.now)
    version: int = 1
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.correlation_id:
            self.correlation_id = self.id
        if not self.nombre:
            self.nombre = self.__class__.__name__

@dataclass
class EventoIntegracion(EventoDominio):
    """
    Eventos para comunicación entre microservicios
    Principio de Responsabilidad Única - comunicación entre bounded contexts
    """
    source_service: str = ""
    destination_services: List[str] = field(default_factory=list)
    schema_version: str = "1.0"
    metadatos_marketing: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para serialización"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "fecha": self.fecha.isoformat(),
            "version": self.version,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "source_service": self.source_service,
            "destination_services": self.destination_services,
            "schema_version": self.schema_version,
            "metadatos_marketing": self.metadatos_marketing or {},
            "timestamp": datetime.now().isoformat()
        }

# Protocol para generadores de eventos (Duck typing)
class GeneradorEventos(Protocol):
    """
    Protocol para entidades que generan eventos
    Principio de Segregación de Interfaces - duck typing
    """
    
    def eventos(self) -> List[EventoDominio]:
        """Retorna eventos generados por la entidad"""
        ...
    
    def limpiar_eventos(self) -> None:
        """Limpia eventos después de ser procesados"""
        ...

# Interfaces para manejo de eventos
class DespachadorEventos(ABC):
    """
    Interface para despachar eventos
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def publicar(self, evento: EventoIntegracion) -> None:
        """Publica un evento de integración"""
        pass
    
    @abstractmethod
    async def publicar_lote(self, eventos: List[EventoIntegracion]) -> None:
        """Publica múltiples eventos en lote"""
        pass

class RepositorioEventos(ABC):
    """
    Interface para persistir eventos (Event Store)
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def guardar_evento(self, evento: EventoDominio) -> None:
        """Guarda evento en el store"""
        pass
    
    @abstractmethod
    async def obtener_eventos_por_agregado(self, agregado_id: str) -> List[EventoDominio]:
        """Obtiene eventos de un agregado específico"""
        pass
    
    @abstractmethod
    async def obtener_eventos_por_tipo(self, tipo_evento: str) -> List[EventoDominio]:
        """Obtiene eventos de un tipo específico"""
        pass
    
    @abstractmethod
    async def obtener_eventos_desde(self, fecha: datetime) -> List[EventoDominio]:
        """Obtiene eventos desde una fecha específica"""
        pass

class ManejadorEvento(ABC):
    """
    Interface base para manejadores de eventos
    Principio de Responsabilidad Única - un manejador por tipo de evento
    """
    
    @abstractmethod
    async def manejar(self, evento: EventoDominio) -> None:
        """Maneja un evento específico"""
        pass
    
    @abstractmethod
    def puede_manejar(self, evento: EventoDominio) -> bool:
        """Determina si puede manejar el evento"""
        pass

class BusEventos(ABC):
    """
    Interface para el bus de eventos
    Principio de Segregación de Interfaces - específico para eventos
    """
    
    @abstractmethod
    async def publicar_evento_dominio(self, evento: EventoDominio) -> None:
        """Publica evento de dominio internamente"""
        pass
    
    @abstractmethod
    async def publicar_evento_integracion(self, evento: EventoIntegracion) -> None:
        """Publica evento de integración externamente"""
        pass
    
    @abstractmethod
    def suscribir_manejador(self, tipo_evento: str, manejador: ManejadorEvento) -> None:
        """Suscribe manejador a un tipo de evento"""
        pass

class BusEventosImplementacion(BusEventos):
    """
    Implementación del bus de eventos
    Principio de Responsabilidad Única - coordinar eventos
    """
    
    def __init__(
        self,
        repositorio_eventos: Optional[RepositorioEventos] = None,
        despachador_eventos: Optional[DespachadorEventos] = None
    ):
        self._manejadores: Dict[str, List[ManejadorEvento]] = {}
        self._repositorio = repositorio_eventos
        self._despachador = despachador_eventos
    
    def suscribir_manejador(self, tipo_evento: str, manejador: ManejadorEvento) -> None:
        """Suscribe manejador siguiendo principio Abierto/Cerrado"""
        if tipo_evento not in self._manejadores:
            self._manejadores[tipo_evento] = []
        self._manejadores[tipo_evento].append(manejador)
    
    async def publicar_evento_dominio(self, evento: EventoDominio) -> None:
        """
        Publica evento de dominio internamente
        1. Guarda en repositorio (si existe)
        2. Notifica a manejadores suscritos
        """
        try:
            # Guardar en repositorio de eventos
            if self._repositorio:
                await self._repositorio.guardar_evento(evento)
            
            # Notificar manejadores suscritos
            manejadores = self._manejadores.get(evento.nombre, [])
            for manejador in manejadores:
                if manejador.puede_manejar(evento):
                    await manejador.manejar(evento)
                    
        except Exception as e:
            # Log error pero no propagar para no afectar transacción principal
            print(f"Error publicando evento dominio {evento.nombre}: {str(e)}")
    
    async def publicar_evento_integracion(self, evento: EventoIntegracion) -> None:
        """
        Publica evento de integración externamente
        Usa el despachador para enviar a otros microservicios
        """
        if self._despachador:
            await self._despachador.publicar(evento)
        else:
            print(f"No hay despachador configurado para evento {evento.nombre}")

# Decorador para manejadores de eventos
class manejador_evento:
    """
    Decorador para registrar manejadores de eventos
    Principio de Inversión de Control
    """
    
    def __init__(self, nombre_evento: str):
        self.nombre_evento = nombre_evento
    
    def __call__(self, clase_manejador):
        # Registrar manejador en el bus global
        # (implementación específica dependería del contenedor de IoC)
        return clase_manejador

# Factory para crear instancias
class FabricaBusEventos(ABC):
    """
    Factory para crear bus de eventos
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def crear_bus_eventos(self) -> BusEventos:
        """Crea instancia del bus de eventos"""
        pass
    
    @abstractmethod
    def crear_repositorio_eventos(self) -> RepositorioEventos:
        """Crea instancia del repositorio de eventos"""
        pass
    
    @abstractmethod
    def crear_despachador_eventos(self) -> DespachadorEventos:
        """Crea instancia del despachador de eventos"""
        pass

# Tipos específicos para eventos de Marketing
TEvento = TypeVar('TEvento', bound=EventoDominio)

class EventoMarketingBase(EventoDominio):
    """
    Base para eventos específicos de marketing
    Principio de Responsabilidad Única - eventos del dominio marketing
    """
    campana_id: Optional[str] = None
    segmento_id: Optional[str] = None
    usuario_id: Optional[str] = None
    metadatos: Dict[str, Any] = field(default_factory=dict)

# Patrón Observer para eventos síncronos
class ObservadorEventos(ABC):
    """
    Interface para observadores de eventos síncronos
    Principio de Segregación de Interfaces
    """
    
    @abstractmethod
    def notificar(self, evento: EventoDominio) -> None:
        """Notifica de forma síncrona sobre un evento"""
        pass

class PublicadorEventos:
    """
    Publicador de eventos con patrón Observer
    Principio de Responsabilidad Única - coordinar notificaciones
    """
    
    def __init__(self):
        self._observadores: List[ObservadorEventos] = []
    
    def agregar_observador(self, observador: ObservadorEventos) -> None:
        """Agrega observador siguiendo principio Abierto/Cerrado"""
        self._observadores.append(observador)
    
    def remover_observador(self, observador: ObservadorEventos) -> None:
        """Remueve observador"""
        if observador in self._observadores:
            self._observadores.remove(observador)
    
    def notificar_evento(self, evento: EventoDominio) -> None:
        """Notifica a todos los observadores"""
        for observador in self._observadores:
            try:
                observador.notificar(evento)
            except Exception as e:
                print(f"Error notificando observador: {str(e)}")
                # No propagar error para no afectar otros observadores