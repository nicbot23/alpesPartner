"""
Despachadores de eventos del módulo de comisiones - Marketing Microservice
Implementación de comunicación asíncrona y event-driven architecture
Arquitectura: Event-Driven + Message Broker + Async Processing
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Callable, Protocol, Union
from abc import ABC, abstractmethod
import json
import uuid
import asyncio
import logging
from enum import Enum

from ..dominio.entidades import EventoDominio
from .configuracion import ConfiguracionEventos, ConfiguracionGlobal

# =============================================================================
# INTERFACES Y PROTOCOLOS
# =============================================================================

class PublicadorEventos(Protocol):
    """Interfaz para publicadores de eventos"""
    
    async def publicar(self, evento: EventoDominio, topic: str) -> None:
        """Publicar evento en un topic específico"""
        ...
    
    async def publicar_lote(self, eventos: List[EventoDominio], topic: str) -> None:
        """Publicar múltiples eventos en lote"""
        ...

class SuscriptorEventos(Protocol):
    """Interfaz para suscriptores de eventos"""
    
    async def suscribir(self, topic: str, handler: Callable[[EventoDominio], None]) -> None:
        """Suscribir handler a un topic"""
        ...
    
    async def desuscribir(self, topic: str) -> None:
        """Desuscribir de un topic"""
        ...

# =============================================================================
# EVENTOS DE INTEGRACIÓN - ESPECÍFICOS DE COMISIONES
# =============================================================================

@dataclass
class EventoIntegracion(EventoDominio):
    """
    Evento base para integración entre bounded contexts
    Principio de Responsabilidad Única - solo integración
    """
    schema_version: str = "1.0"
    source_service: str = "marketing.comisiones"
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    causation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def a_mensaje(self) -> Dict[str, Any]:
        """Convertir evento a mensaje serializable"""
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "tipo": type(self).__name__,
            "schema_version": self.schema_version,
            "source_service": self.source_service,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "metadata": self.metadata,
            "data": self._obtener_datos_evento()
        }
    
    @abstractmethod
    def _obtener_datos_evento(self) -> Dict[str, Any]:
        """Obtener datos específicos del evento"""
        pass

@dataclass
class ComisionCalculadaIntegracion(EventoIntegracion):
    """Evento de integración: Comisión calculada"""
    comision_id: str = ""
    afiliado_id: str = ""
    campana_id: str = ""
    conversion_id: str = ""
    monto_calculado: float = 0.0
    moneda: str = "COP"
    tipo_comision: str = ""
    fecha_calculo: datetime = field(default_factory=datetime.now)
    
    def _obtener_datos_evento(self) -> Dict[str, Any]:
        return {
            "comision_id": self.comision_id,
            "afiliado_id": self.afiliado_id,
            "campana_id": self.campana_id,
            "conversion_id": self.conversion_id,
            "monto_calculado": self.monto_calculado,
            "moneda": self.moneda,
            "tipo_comision": self.tipo_comision,
            "fecha_calculo": self.fecha_calculo.isoformat()
        }

@dataclass
class ComisionAprobadaIntegracion(EventoIntegracion):
    """Evento de integración: Comisión aprobada"""
    comision_id: str = ""
    afiliado_id: str = ""
    campana_id: str = ""
    monto_aprobado: float = 0.0
    moneda: str = "COP"
    aprobador_id: str = ""
    fecha_aprobacion: datetime = field(default_factory=datetime.now)
    comentarios: Optional[str] = None
    
    def _obtener_datos_evento(self) -> Dict[str, Any]:
        return {
            "comision_id": self.comision_id,
            "afiliado_id": self.afiliado_id,
            "campana_id": self.campana_id,
            "monto_aprobado": self.monto_aprobado,
            "moneda": self.moneda,
            "aprobador_id": self.aprobador_id,
            "fecha_aprobacion": self.fecha_aprobacion.isoformat(),
            "comentarios": self.comentarios
        }

@dataclass
class ComisionRechazadaIntegracion(EventoIntegracion):
    """Evento de integración: Comisión rechazada"""
    comision_id: str = ""
    afiliado_id: str = ""
    campana_id: str = ""
    rechazador_id: str = ""
    motivo_rechazo: str = ""
    fecha_rechazo: datetime = field(default_factory=datetime.now)
    comentarios: Optional[str] = None
    
    def _obtener_datos_evento(self) -> Dict[str, Any]:
        return {
            "comision_id": self.comision_id,
            "afiliado_id": self.afiliado_id,
            "campana_id": self.campana_id,
            "rechazador_id": self.rechazador_id,
            "motivo_rechazo": self.motivo_rechazo,
            "fecha_rechazo": self.fecha_rechazo.isoformat(),
            "comentarios": self.comentarios
        }

@dataclass
class ComisionPagadaIntegracion(EventoIntegracion):
    """Evento de integración: Comisión pagada"""
    comision_id: str = ""
    afiliado_id: str = ""
    monto_pagado: float = 0.0
    moneda: str = "COP"
    metodo_pago: str = ""
    referencia_pago: str = ""
    fecha_pago: datetime = field(default_factory=datetime.now)
    
    def _obtener_datos_evento(self) -> Dict[str, Any]:
        return {
            "comision_id": self.comision_id,
            "afiliado_id": self.afiliado_id,
            "monto_pagado": self.monto_pagado,
            "moneda": self.moneda,
            "metodo_pago": self.metodo_pago,
            "referencia_pago": self.referencia_pago,
            "fecha_pago": self.fecha_pago.isoformat()
        }

# =============================================================================
# PUBLICADOR PULSAR - IMPLEMENTACIÓN ESPECÍFICA
# =============================================================================

class PublicadorEventosPulsar:
    """
    Publicador de eventos usando Apache Pulsar
    Principio de Responsabilidad Única - solo publicación Pulsar
    """
    
    def __init__(self, config: ConfiguracionEventos, logger: Optional[logging.Logger] = None):
        self._config = config
        self._logger = logger or logging.getLogger(__name__)
        self._client = None
        self._producers: Dict[str, Any] = {}
        self._conectado = False
    
    async def conectar(self) -> None:
        """Establecer conexión con Pulsar"""
        try:
            # En implementación real, usar pulsar-client
            # import pulsar
            # self._client = pulsar.Client(self._config.url_pulsar)
            
            # Mock para este ejemplo
            self._client = MockPulsarClient(self._config.url_pulsar)
            self._conectado = True
            self._logger.info("Conectado a Pulsar exitosamente")
            
        except Exception as ex:
            self._logger.error(f"Error al conectar con Pulsar: {ex}")
            raise
    
    async def desconectar(self) -> None:
        """Cerrar conexión con Pulsar"""
        try:
            if self._client:
                for producer in self._producers.values():
                    await producer.close()
                await self._client.close()
                self._conectado = False
                self._logger.info("Desconectado de Pulsar")
        except Exception as ex:
            self._logger.error(f"Error al desconectar de Pulsar: {ex}")
    
    async def publicar(self, evento: EventoIntegracion, topic: str) -> None:
        """Publicar evento individual"""
        try:
            if not self._conectado:
                await self.conectar()
            
            # Obtener o crear producer para el topic
            producer = await self._obtener_producer(topic)
            
            # Convertir evento a mensaje
            mensaje = evento.a_mensaje()
            mensaje_json = json.dumps(mensaje, ensure_ascii=False)
            
            # Publicar mensaje
            await producer.send(
                content=mensaje_json.encode('utf-8'),
                properties={
                    'event_type': type(evento).__name__,
                    'correlation_id': evento.correlation_id,
                    'source_service': evento.source_service,
                    'schema_version': evento.schema_version
                }
            )
            
            self._logger.info(f"Evento publicado: {type(evento).__name__} en topic {topic}")
            
        except Exception as ex:
            self._logger.error(f"Error al publicar evento: {ex}")
            raise
    
    async def publicar_lote(self, eventos: List[EventoIntegracion], topic: str) -> None:
        """Publicar múltiples eventos en lote"""
        try:
            for evento in eventos:
                await self.publicar(evento, topic)
            
            self._logger.info(f"Lote de {len(eventos)} eventos publicado en topic {topic}")
            
        except Exception as ex:
            self._logger.error(f"Error al publicar lote de eventos: {ex}")
            raise
    
    async def _obtener_producer(self, topic: str) -> Any:
        """Obtener o crear producer para topic"""
        if topic not in self._producers:
            topic_completo = f"{self._config.namespace_pulsar}/{topic}"
            
            # En implementación real:
            # producer = self._client.create_producer(
            #     topic=topic_completo,
            #     **self._config.obtener_configuracion_productor()
            # )
            
            # Mock para este ejemplo
            producer = MockPulsarProducer(topic_completo)
            self._producers[topic] = producer
        
        return self._producers[topic]

# =============================================================================
# SUSCRIPTOR PULSAR - IMPLEMENTACIÓN ESPECÍFICA
# =============================================================================

class SuscriptorEventosPulsar:
    """
    Suscriptor de eventos usando Apache Pulsar
    Principio de Responsabilidad Única - solo suscripción Pulsar
    """
    
    def __init__(self, config: ConfiguracionEventos, logger: Optional[logging.Logger] = None):
        self._config = config
        self._logger = logger or logging.getLogger(__name__)
        self._client = None
        self._consumers: Dict[str, Any] = {}
        self._handlers: Dict[str, Callable] = {}
        self._conectado = False
    
    async def conectar(self) -> None:
        """Establecer conexión con Pulsar"""
        try:
            # Mock para este ejemplo
            self._client = MockPulsarClient(self._config.url_pulsar)
            self._conectado = True
            self._logger.info("Suscriptor conectado a Pulsar")
        except Exception as ex:
            self._logger.error(f"Error al conectar suscriptor: {ex}")
            raise
    
    async def suscribir(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Suscribir handler a un topic"""
        try:
            if not self._conectado:
                await self.conectar()
            
            topic_completo = f"{self._config.namespace_pulsar}/{topic}"
            
            # En implementación real:
            # consumer = self._client.subscribe(
            #     topic=topic_completo,
            #     subscription_name=self._config.subscription_name,
            #     **self._config.obtener_configuracion_consumidor()
            # )
            
            # Mock para este ejemplo
            consumer = MockPulsarConsumer(topic_completo, self._config.subscription_name)
            
            self._consumers[topic] = consumer
            self._handlers[topic] = handler
            
            # Iniciar procesamiento de mensajes
            asyncio.create_task(self._procesar_mensajes(topic, consumer, handler))
            
            self._logger.info(f"Suscrito a topic {topic}")
            
        except Exception as ex:
            self._logger.error(f"Error al suscribir a topic {topic}: {ex}")
            raise
    
    async def desuscribir(self, topic: str) -> None:
        """Desuscribir de un topic"""
        try:
            if topic in self._consumers:
                consumer = self._consumers[topic]
                await consumer.close()
                del self._consumers[topic]
                del self._handlers[topic]
                self._logger.info(f"Desuscrito de topic {topic}")
        except Exception as ex:
            self._logger.error(f"Error al desuscribir de topic {topic}: {ex}")
    
    async def _procesar_mensajes(self, topic: str, consumer: Any, handler: Callable) -> None:
        """Procesar mensajes de un consumer"""
        while topic in self._consumers:
            try:
                # En implementación real:
                # msg = await consumer.receive()
                # data = json.loads(msg.data().decode('utf-8'))
                # await handler(data)
                # await consumer.acknowledge(msg)
                
                # Mock para este ejemplo
                await asyncio.sleep(1)  # Simular espera por mensajes
                
            except Exception as ex:
                self._logger.error(f"Error procesando mensaje en topic {topic}: {ex}")
                await asyncio.sleep(1)

# =============================================================================
# DESPACHADOR DE EVENTOS - COORDINADOR PRINCIPAL
# =============================================================================

class DespachadorEventosComisiones:
    """
    Despachador principal de eventos de comisiones
    Facade Pattern - coordina publicación y suscripción de eventos
    """
    
    def __init__(
        self,
        publicador: PublicadorEventos,
        suscriptor: Optional[SuscriptorEventos] = None,
        config: Optional[ConfiguracionEventos] = None,
        logger: Optional[logging.Logger] = None
    ):
        self._publicador = publicador
        self._suscriptor = suscriptor
        self._config = config or ConfiguracionGlobal.obtener().eventos
        self._logger = logger or logging.getLogger(__name__)
        self._handlers_registrados: Dict[str, List[Callable]] = {}
    
    async def publicar_comision_calculada(self, evento: ComisionCalculadaIntegracion) -> None:
        """Publicar evento de comisión calculada"""
        await self._publicador.publicar(evento, self._config.topic_comision_calculada)
    
    async def publicar_comision_aprobada(self, evento: ComisionAprobadaIntegracion) -> None:
        """Publicar evento de comisión aprobada"""
        await self._publicador.publicar(evento, self._config.topic_comision_aprobada)
    
    async def publicar_comision_rechazada(self, evento: ComisionRechazadaIntegracion) -> None:
        """Publicar evento de comisión rechazada"""
        await self._publicador.publicar(evento, self._config.topic_comision_rechazada)
    
    async def publicar_comision_pagada(self, evento: ComisionPagadaIntegracion) -> None:
        """Publicar evento de comisión pagada"""
        await self._publicador.publicar(evento, self._config.topic_comision_pagada)
    
    async def suscribir_a_eventos_comisiones(self, handler: Callable[[EventoIntegracion], None]) -> None:
        """Suscribir handler a todos los eventos de comisiones"""
        if self._suscriptor:
            topics = [
                self._config.topic_comision_calculada,
                self._config.topic_comision_aprobada,
                self._config.topic_comision_rechazada,
                self._config.topic_comision_pagada
            ]
            
            for topic in topics:
                await self._suscriptor.suscribir(topic, handler)
    
    def registrar_handler(self, tipo_evento: str, handler: Callable) -> None:
        """Registrar handler para tipo específico de evento"""
        if tipo_evento not in self._handlers_registrados:
            self._handlers_registrados[tipo_evento] = []
        self._handlers_registrados[tipo_evento].append(handler)
    
    async def procesar_evento_entrante(self, mensaje: Dict[str, Any]) -> None:
        """Procesar evento entrante desde el broker"""
        try:
            tipo_evento = mensaje.get('tipo', '')
            
            if tipo_evento in self._handlers_registrados:
                for handler in self._handlers_registrados[tipo_evento]:
                    try:
                        await handler(mensaje)
                    except Exception as ex:
                        self._logger.error(f"Error en handler para {tipo_evento}: {ex}")
            
        except Exception as ex:
            self._logger.error(f"Error procesando evento entrante: {ex}")

# =============================================================================
# FACTORY DE DESPACHADORES
# =============================================================================

class FabricaDespachadores:
    """
    Factory para crear despachadores según configuración
    Principio de Responsabilidad Única - solo creación de despachadores
    """
    
    @staticmethod
    async def crear_despachador_pulsar(
        config: Optional[ConfiguracionEventos] = None
    ) -> DespachadorEventosComisiones:
        """Crear despachador usando Pulsar"""
        config = config or ConfiguracionGlobal.obtener().eventos
        
        publicador = PublicadorEventosPulsar(config)
        await publicador.conectar()
        
        suscriptor = SuscriptorEventosPulsar(config)
        await suscriptor.conectar()
        
        return DespachadorEventosComisiones(
            publicador=publicador,
            suscriptor=suscriptor,
            config=config
        )
    
    @staticmethod
    def crear_despachador_mock() -> DespachadorEventosComisiones:
        """Crear despachador mock para pruebas"""
        publicador = PublicadorEventosMock()
        return DespachadorEventosComisiones(publicador=publicador)

# =============================================================================
# IMPLEMENTACIONES MOCK PARA DESARROLLO Y PRUEBAS
# =============================================================================

class MockPulsarClient:
    """Cliente Pulsar mock para desarrollo"""
    def __init__(self, url: str):
        self.url = url
    
    async def close(self):
        pass

class MockPulsarProducer:
    """Producer Pulsar mock"""
    def __init__(self, topic: str):
        self.topic = topic
    
    async def send(self, content: bytes, properties: Dict[str, str] = None):
        print(f"[MOCK] Enviando mensaje a {self.topic}: {content.decode('utf-8')[:100]}...")
    
    async def close(self):
        pass

class MockPulsarConsumer:
    """Consumer Pulsar mock"""
    def __init__(self, topic: str, subscription: str):
        self.topic = topic
        self.subscription = subscription
    
    async def close(self):
        pass

class PublicadorEventosMock:
    """Publicador mock para pruebas"""
    def __init__(self):
        self.eventos_publicados: List[tuple[EventoIntegracion, str]] = []
    
    async def publicar(self, evento: EventoIntegracion, topic: str) -> None:
        self.eventos_publicados.append((evento, topic))
        print(f"[MOCK] Evento publicado: {type(evento).__name__} en {topic}")
    
    async def publicar_lote(self, eventos: List[EventoIntegracion], topic: str) -> None:
        for evento in eventos:
            await self.publicar(evento, topic)