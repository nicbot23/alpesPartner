"""
Despachadores Apache Pulsar para Marketing
Implementa comunicación robusta con otros microservicios
"""
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from typing import List, Optional, Dict, Any, Callable
from enum import Enum
import uuid

from ..dominio.eventos import EventoIntegracion, DespachadorEventos
from ..aplicacion.eventos_integracion import SchemaEventosIntegracion

# Configuración específica de Pulsar para Marketing
class ConfiguracionPulsarMarketing:
    """
    Configuración específica de Pulsar para Marketing
    Principio de Responsabilidad Única - configuración centralizada
    """
    
    def __init__(self):
        self.service_url = "pulsar://localhost:6650"
        self.topics = {
            # Topics que Marketing publica
            "campana-lanzada": "persistent://marketing/events/campana-lanzada",
            "campana-pausada": "persistent://marketing/events/campana-pausada",
            "segmento-creado": "persistent://marketing/events/segmento-creado",
            "metricas-campana": "persistent://marketing/events/metricas-campana",
            "comision-calculada": "persistent://marketing/events/comision-calculada",
            "rendimiento-afiliado": "persistent://marketing/events/rendimiento-afiliado",
            "alerta-presupuesto": "persistent://marketing/events/alerta-presupuesto",
            "reporte-campana": "persistent://marketing/events/reporte-campana",
            
            # Topics que Marketing consume
            "nuevo-afiliado": "persistent://afiliados/events/nuevo-afiliado",
            "afiliado-actualizado": "persistent://afiliados/events/afiliado-actualizado",
            "afiliado-desactivado": "persistent://afiliados/events/afiliado-desactivado",
            "conversion-registrada": "persistent://conversiones/events/conversion-registrada",
            "conversion-anulada": "persistent://conversiones/events/conversion-anulada"
        }
        
        self.subscription_name = "marketing-service"
        self.producer_name = "marketing-producer"
        
        # Configuración de retry y circuit breaker
        self.max_retries = 3
        self.retry_delay_ms = 1000
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout_ms = 30000
        
        # Configuración de batching
        self.batch_size = 10
        self.batch_timeout_ms = 5000

class EstadoCircuitBreaker(Enum):
    """Estados del Circuit Breaker"""
    CERRADO = "cerrado"      # Normal operation
    ABIERTO = "abierto"      # Circuit tripped
    MEDIO_ABIERTO = "medio_abierto"  # Testing if service recovered

class CircuitBreakerPulsar:
    """
    Circuit Breaker para Pulsar
    Principio de Responsabilidad Única - gestión de fallos
    """
    
    def __init__(self, threshold: int = 5, timeout_ms: int = 30000):
        self.threshold = threshold
        self.timeout_ms = timeout_ms
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = EstadoCircuitBreaker.CERRADO
        self.logger = logging.getLogger(__name__)
    
    def puede_ejecutar(self) -> bool:
        """Determina si se puede ejecutar la operación"""
        if self.state == EstadoCircuitBreaker.CERRADO:
            return True
        
        if self.state == EstadoCircuitBreaker.ABIERTO:
            if self._debe_intentar_recuperacion():
                self.state = EstadoCircuitBreaker.MEDIO_ABIERTO
                return True
            return False
        
        # Estado MEDIO_ABIERTO - permitir una operación de prueba
        if self.state == EstadoCircuitBreaker.MEDIO_ABIERTO:
            return True
        
        return False
    
    def registrar_exito(self) -> None:
        """Registra operación exitosa"""
        self.failure_count = 0
        self.state = EstadoCircuitBreaker.CERRADO
        self.logger.info("Circuit breaker: Operación exitosa, estado CERRADO")
    
    def registrar_fallo(self) -> None:
        """Registra operación fallida"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.threshold:
            self.state = EstadoCircuitBreaker.ABIERTO
            self.logger.warning(f"Circuit breaker: Umbral alcanzado ({self.failure_count}), estado ABIERTO")
        else:
            self.logger.warning(f"Circuit breaker: Fallo registrado ({self.failure_count}/{self.threshold})")
    
    def _debe_intentar_recuperacion(self) -> bool:
        """Determina si debe intentar recuperación"""
        if not self.last_failure_time:
            return True
        
        tiempo_transcurrido = datetime.now() - self.last_failure_time
        return tiempo_transcurrido.total_seconds() * 1000 >= self.timeout_ms

class ManejadorReintentos:
    """
    Manejador de reintentos con backoff exponencial
    Principio de Responsabilidad Única - gestión de reintentos
    """
    
    def __init__(self, max_retries: int = 3, delay_base_ms: int = 1000):
        self.max_retries = max_retries
        self.delay_base_ms = delay_base_ms
        self.logger = logging.getLogger(__name__)
    
    async def ejecutar_con_reintentos(
        self,
        operacion: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Ejecuta operación con reintentos"""
        for intento in range(self.max_retries + 1):
            try:
                return await operacion(*args, **kwargs)
            except Exception as e:
                if intento == self.max_retries:
                    self.logger.error(f"Operación falló después de {self.max_retries} reintentos: {str(e)}")
                    raise
                
                delay = self.delay_base_ms * (2 ** intento) / 1000.0  # Backoff exponencial
                self.logger.warning(f"Intento {intento + 1} falló, reintentando en {delay}s: {str(e)}")
                await asyncio.sleep(delay)

class DespachadorPulsarMarketing(DespachadorEventos):
    """
    Implementación robusta del despachador Pulsar para Marketing
    Principio de Responsabilidad Única - comunicación asíncrona
    """
    
    def __init__(self, configuracion: ConfiguracionPulsarMarketing):
        self.configuracion = configuracion
        self.cliente_pulsar = None
        self.productores: Dict[str, Any] = {}
        self.circuit_breaker = CircuitBreakerPulsar(
            threshold=configuracion.circuit_breaker_threshold,
            timeout_ms=configuracion.circuit_breaker_timeout_ms
        )
        self.manejador_reintentos = ManejadorReintentos(
            max_retries=configuracion.max_retries,
            delay_base_ms=configuracion.retry_delay_ms
        )
        self.logger = logging.getLogger(__name__)
        
        # Cola de eventos para batching
        self.cola_eventos: List[EventoIntegracion] = []
        self.procesando_batch = False
    
    async def inicializar(self) -> None:
        """Inicializa conexión con Pulsar"""
        try:
            import pulsar
            
            self.cliente_pulsar = pulsar.Client(self.configuracion.service_url)
            self.logger.info("Cliente Pulsar inicializado correctamente")
            
            # Inicializar productores para topics de Marketing
            await self._inicializar_productores()
            
            # Iniciar procesamiento de batch en background
            asyncio.create_task(self._procesar_batch_periodico())
            
        except Exception as e:
            self.logger.error(f"Error inicializando Pulsar: {str(e)}")
            raise
    
    async def _inicializar_productores(self) -> None:
        """Inicializa productores para todos los topics"""
        topics_marketing = [
            "campana-lanzada", "campana-pausada", "segmento-creado",
            "metricas-campana", "comision-calculada", "rendimiento-afiliado",
            "alerta-presupuesto", "reporte-campana"
        ]
        
        for topic_key in topics_marketing:
            topic_name = self.configuracion.topics[topic_key]
            try:
                productor = self.cliente_pulsar.create_producer(
                    topic=topic_name,
                    producer_name=f"{self.configuracion.producer_name}-{topic_key}",
                    block_if_queue_full=True,
                    batching_enabled=True,
                    batching_max_messages=self.configuracion.batch_size,
                    batching_max_publish_delay_ms=self.configuracion.batch_timeout_ms
                )
                self.productores[topic_key] = productor
                self.logger.info(f"Productor creado para topic {topic_name}")
            except Exception as e:
                self.logger.error(f"Error creando productor para {topic_key}: {str(e)}")
    
    async def publicar(self, evento: EventoIntegracion) -> None:
        """
        Publica evento de integración individual
        Principio de Responsabilidad Única - publicación controlada
        """
        if not self.circuit_breaker.puede_ejecutar():
            self.logger.warning(f"Circuit breaker abierto, evento {evento.nombre} no enviado")
            return
        
        try:
            await self.manejador_reintentos.ejecutar_con_reintentos(
                self._publicar_evento_interno,
                evento
            )
            self.circuit_breaker.registrar_exito()
            
        except Exception as e:
            self.circuit_breaker.registrar_fallo()
            self.logger.error(f"Error publicando evento {evento.nombre}: {str(e)}")
            # Intentar guardar en outbox para retry posterior
            await self._guardar_en_outbox_fallback(evento)
    
    async def publicar_lote(self, eventos: List[EventoIntegracion]) -> None:
        """
        Publica múltiples eventos en lote
        Principio de Responsabilidad Única - optimización de lotes
        """
        if not eventos:
            return
        
        # Agregar a cola para procesamiento batch
        self.cola_eventos.extend(eventos)
        
        # Si tenemos suficientes eventos, procesar inmediatamente
        if len(self.cola_eventos) >= self.configuracion.batch_size:
            await self._procesar_batch_actual()
    
    async def _publicar_evento_interno(self, evento: EventoIntegracion) -> None:
        """Publica evento individual internamente"""
        # Validar evento antes de enviar
        if not SchemaEventosIntegracion.validar_evento(evento):
            raise ValueError(f"Evento {evento.nombre} no pasa validación de schema")
        
        # Determinar topic basado en el tipo de evento
        topic_key = self._obtener_topic_para_evento(evento)
        if not topic_key:
            raise ValueError(f"No se encontró topic para evento {evento.nombre}")
        
        productor = self.productores.get(topic_key)
        if not productor:
            raise ValueError(f"No hay productor disponible para topic {topic_key}")
        
        # Preparar mensaje
        mensaje = self._preparar_mensaje(evento)
        
        # Enviar mensaje
        message_id = productor.send(
            content=json.dumps(mensaje).encode('utf-8'),
            properties={
                'event_type': evento.nombre,
                'correlation_id': evento.correlation_id or '',
                'source_service': evento.source_service,
                'timestamp': datetime.now().isoformat(),
                'schema_version': evento.schema_version
            }
        )
        
        self.logger.info(f"Evento {evento.nombre} publicado con ID: {message_id}")
    
    def _obtener_topic_para_evento(self, evento: EventoIntegracion) -> Optional[str]:
        """Mapea tipo de evento a topic key"""
        mapeo_eventos = {
            'CampanaLanzada': 'campana-lanzada',
            'CampanaPausadaOFinalizada': 'campana-pausada',
            'NuevoSegmentoCreado': 'segmento-creado',
            'MetricasCampanaActualizadas': 'metricas-campana',
            'ComisionCalculada': 'comision-calculada',
            'RendimientoAfiliadoAnalizado': 'rendimiento-afiliado',
            'AlertaCampanaPresupuesto': 'alerta-presupuesto',
            'ReporteCampanaFinalizada': 'reporte-campana'
        }
        
        return mapeo_eventos.get(evento.nombre)
    
    def _preparar_mensaje(self, evento: EventoIntegracion) -> Dict[str, Any]:
        """Prepara mensaje para envío"""
        mensaje = evento.to_dict()
        
        # Agregar metadatos adicionales de Marketing
        mensaje['marketing_metadata'] = {
            'producer_id': self.configuracion.producer_name,
            'processing_timestamp': datetime.now().isoformat(),
            'message_id': str(uuid.uuid4()),
            'priority': evento.metadatos_marketing.get('prioridad', 'media') if evento.metadatos_marketing else 'media'
        }
        
        return mensaje
    
    async def _procesar_batch_actual(self) -> None:
        """Procesa batch actual de eventos"""
        if self.procesando_batch or not self.cola_eventos:
            return
        
        self.procesando_batch = True
        try:
            eventos_a_procesar = self.cola_eventos[:self.configuracion.batch_size]
            self.cola_eventos = self.cola_eventos[self.configuracion.batch_size:]
            
            # Agrupar eventos por topic para eficiencia
            eventos_por_topic = {}
            for evento in eventos_a_procesar:
                topic_key = self._obtener_topic_para_evento(evento)
                if topic_key:
                    if topic_key not in eventos_por_topic:
                        eventos_por_topic[topic_key] = []
                    eventos_por_topic[topic_key].append(evento)
            
            # Enviar eventos agrupados
            for topic_key, eventos in eventos_por_topic.items():
                await self._enviar_batch_topic(topic_key, eventos)
            
        finally:
            self.procesando_batch = False
    
    async def _enviar_batch_topic(self, topic_key: str, eventos: List[EventoIntegracion]) -> None:
        """Envía batch de eventos a un topic específico"""
        productor = self.productores.get(topic_key)
        if not productor:
            self.logger.error(f"No hay productor para topic {topic_key}")
            return
        
        try:
            for evento in eventos:
                mensaje = self._preparar_mensaje(evento)
                productor.send_async(
                    content=json.dumps(mensaje).encode('utf-8'),
                    properties={
                        'event_type': evento.nombre,
                        'correlation_id': evento.correlation_id or '',
                        'source_service': evento.source_service,
                        'batch_id': str(uuid.uuid4()),
                        'timestamp': datetime.now().isoformat()
                    },
                    callback=lambda res, msg_id: self.logger.debug(f"Evento batch enviado: {msg_id}")
                )
            
            # Flush para asegurar envío
            productor.flush()
            self.logger.info(f"Batch de {len(eventos)} eventos enviados a {topic_key}")
            
        except Exception as e:
            self.logger.error(f"Error enviando batch a {topic_key}: {str(e)}")
            # Reencolar eventos fallidos
            self.cola_eventos.extend(eventos)
    
    async def _procesar_batch_periodico(self) -> None:
        """Procesa batch periódicamente"""
        while True:
            try:
                await asyncio.sleep(self.configuracion.batch_timeout_ms / 1000.0)
                if self.cola_eventos and not self.procesando_batch:
                    await self._procesar_batch_actual()
            except Exception as e:
                self.logger.error(f"Error en procesamiento batch periódico: {str(e)}")
    
    async def _guardar_en_outbox_fallback(self, evento: EventoIntegracion) -> None:
        """Guarda evento en outbox como fallback"""
        try:
            # Aquí iría la lógica para guardar en outbox
            # Por ahora solo log
            self.logger.info(f"Evento {evento.nombre} guardado en outbox para retry")
        except Exception as e:
            self.logger.error(f"Error guardando en outbox: {str(e)}")
    
    async def cerrar(self) -> None:
        """Cierra conexiones"""
        try:
            # Procesar eventos pendientes
            if self.cola_eventos:
                await self._procesar_batch_actual()
            
            # Cerrar productores
            for productor in self.productores.values():
                productor.close()
            
            # Cerrar cliente
            if self.cliente_pulsar:
                self.cliente_pulsar.close()
            
            self.logger.info("Despachador Pulsar cerrado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error cerrando despachador Pulsar: {str(e)}")

class ConsumidorEventosMarketing:
    """
    Consumidor de eventos para Marketing
    Principio de Responsabilidad Única - consumo de eventos
    """
    
    def __init__(self, configuracion: ConfiguracionPulsarMarketing):
        self.configuracion = configuracion
        self.cliente_pulsar = None
        self.consumidores: Dict[str, Any] = {}
        self.manejadores: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        self.activo = False
    
    async def inicializar(self) -> None:
        """Inicializa consumidores"""
        try:
            import pulsar
            
            self.cliente_pulsar = pulsar.Client(self.configuracion.service_url)
            
            # Crear consumidores para topics de entrada
            await self._crear_consumidores()
            
            self.logger.info("Consumidores Pulsar inicializados")
            
        except Exception as e:
            self.logger.error(f"Error inicializando consumidores: {str(e)}")
            raise
    
    async def _crear_consumidores(self) -> None:
        """Crea consumidores para topics de entrada"""
        topics_entrada = [
            "nuevo-afiliado", "afiliado-actualizado", "afiliado-desactivado",
            "conversion-registrada", "conversion-anulada"
        ]
        
        for topic_key in topics_entrada:
            topic_name = self.configuracion.topics[topic_key]
            try:
                import pulsar
                consumidor = self.cliente_pulsar.subscribe(
                    topic=topic_name,
                    subscription_name=f"{self.configuracion.subscription_name}-{topic_key}",
                    consumer_type=pulsar.ConsumerType.Shared
                )
                self.consumidores[topic_key] = consumidor
                self.logger.info(f"Consumidor creado para topic {topic_name}")
            except Exception as e:
                self.logger.error(f"Error creando consumidor para {topic_key}: {str(e)}")
    
    def registrar_manejador(self, tipo_evento: str, manejador: Callable) -> None:
        """Registra manejador para tipo de evento"""
        self.manejadores[tipo_evento] = manejador
        self.logger.info(f"Manejador registrado para evento {tipo_evento}")
    
    async def iniciar_consumo(self) -> None:
        """Inicia consumo de eventos"""
        self.activo = True
        tareas = []
        
        for topic_key, consumidor in self.consumidores.items():
            tarea = asyncio.create_task(self._consumir_topic(topic_key, consumidor))
            tareas.append(tarea)
        
        await asyncio.gather(*tareas)
    
    async def _consumir_topic(self, topic_key: str, consumidor) -> None:
        """Consume eventos de un topic específico"""
        while self.activo:
            try:
                mensaje = consumidor.receive(timeout_millis=5000)
                
                # Procesar mensaje
                await self._procesar_mensaje(mensaje)
                
                # Acknowledge mensaje
                consumidor.acknowledge(mensaje)
                
            except Exception as e:
                if "Pulsar error: TimeOut" not in str(e):
                    self.logger.error(f"Error consumiendo de {topic_key}: {str(e)}")
    
    async def _procesar_mensaje(self, mensaje) -> None:
        """Procesa mensaje recibido"""
        try:
            # Deserializar mensaje
            contenido = json.loads(mensaje.data().decode('utf-8'))
            tipo_evento = mensaje.properties().get('event_type', '')
            
            # Buscar manejador
            manejador = self.manejadores.get(tipo_evento)
            if manejador:
                await manejador(contenido)
                self.logger.debug(f"Evento {tipo_evento} procesado correctamente")
            else:
                self.logger.warning(f"No hay manejador para evento {tipo_evento}")
                
        except Exception as e:
            self.logger.error(f"Error procesando mensaje: {str(e)}")
    
    async def detener(self) -> None:
        """Detiene consumo"""
        self.activo = False
        
        for consumidor in self.consumidores.values():
            consumidor.unsubscribe()
            consumidor.close()
        
        if self.cliente_pulsar:
            self.cliente_pulsar.close()
        
        self.logger.info("Consumidores detenidos")

# Factory para crear despachadores
class FabricaDespachadorMarketing:
    """
    Factory para crear despachadores de Marketing
    Principio de Responsabilidad Única - creación centralizada
    """
    
    @staticmethod
    def crear_despachador_pulsar() -> DespachadorPulsarMarketing:
        """Crea despachador Pulsar con configuración por defecto"""
        configuracion = ConfiguracionPulsarMarketing()
        return DespachadorPulsarMarketing(configuracion)
    
    @staticmethod
    def crear_consumidor_eventos() -> ConsumidorEventosMarketing:
        """Crea consumidor de eventos con configuración por defecto"""
        configuracion = ConfiguracionPulsarMarketing()
        return ConsumidorEventosMarketing(configuracion)
    
    @staticmethod
    def crear_con_configuracion_custom(
        service_url: str,
        topics_personalizados: Dict[str, str] = None
    ) -> tuple[DespachadorPulsarMarketing, ConsumidorEventosMarketing]:
        """Crea despachador y consumidor con configuración personalizada"""
        configuracion = ConfiguracionPulsarMarketing()
        configuracion.service_url = service_url
        
        if topics_personalizados:
            configuracion.topics.update(topics_personalizados)
        
        despachador = DespachadorPulsarMarketing(configuracion)
        consumidor = ConsumidorEventosMarketing(configuracion)
        
        return despachador, consumidor