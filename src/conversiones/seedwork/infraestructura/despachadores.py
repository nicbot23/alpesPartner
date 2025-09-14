"""
Despachadores robustos para Apache Pulsar
Comunicación enterprise entre microservicios con resiliencia
"""
import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
import uuid

# Simulación de cliente Pulsar (en producción sería pulsar-client)
class PulsarClient:
    """Simulación del cliente Pulsar"""
    
    def __init__(self, service_url: str):
        self.service_url = service_url
        self.is_connected = True
    
    def create_producer(self, topic: str, **kwargs):
        return PulsarProducer(topic, **kwargs)
    
    def create_consumer(self, topics: Union[str, List[str]], subscription_name: str, **kwargs):
        if isinstance(topics, str):
            topics = [topics]
        return PulsarConsumer(topics, subscription_name, **kwargs)
    
    def close(self):
        self.is_connected = False

class PulsarProducer:
    """Simulación del productor Pulsar"""
    
    def __init__(self, topic: str, **kwargs):
        self.topic = topic
        self.schema = kwargs.get('schema')
        self.properties = kwargs.get('properties', {})
    
    async def send_async(self, content: Any, properties: Dict[str, str] = None):
        # Simulación de envío asíncrono
        await asyncio.sleep(0.01)  # Simular latencia de red
        return f"msg_id_{uuid.uuid4()}"
    
    def close(self):
        pass

class PulsarConsumer:
    """Simulación del consumidor Pulsar"""
    
    def __init__(self, topics: List[str], subscription_name: str, **kwargs):
        self.topics = topics
        self.subscription_name = subscription_name
        self.consumer_type = kwargs.get('consumer_type', 'Exclusive')
    
    async def receive_async(self):
        # Simulación de recepción asíncrona
        await asyncio.sleep(0.1)
        return PulsarMessage(f"msg_id_{uuid.uuid4()}", b'{"test": "message"}')
    
    def acknowledge(self, message):
        pass
    
    def negative_acknowledge(self, message):
        pass
    
    def close(self):
        pass

class PulsarMessage:
    """Simulación del mensaje Pulsar"""
    
    def __init__(self, message_id: str, data: bytes):
        self.message_id = message_id
        self.data = data
        self.properties = {}
        self.publish_timestamp = int(time.time() * 1000)
    
    def value(self):
        return self.data

# Estados del Circuit Breaker
class EstadoCircuitBreaker(Enum):
    CERRADO = "cerrado"          # Funcionando normal
    ABIERTO = "abierto"          # Bloqueando llamadas
    MEDIO_ABIERTO = "medio_abierto"  # Probando recuperación

# Circuit Breaker para Pulsar
@dataclass
class ConfiguracionCircuitBreaker:
    """Configuración del Circuit Breaker para despachadores"""
    umbral_fallos: int = 5
    timeout_segundos: float = 60.0
    umbral_recuperacion: int = 3
    ventana_tiempo_segundos: float = 300.0  # 5 minutos

class CircuitBreakerPulsar:
    """
    Circuit Breaker específico para operaciones Pulsar
    Previene cascada de fallos en comunicación
    """
    
    def __init__(self, config: ConfiguracionCircuitBreaker):
        self.config = config
        self.estado = EstadoCircuitBreaker.CERRADO
        self.contador_fallos = 0
        self.contador_exitos = 0
        self.ultimo_fallo = None
        self.tiempo_apertura = None
        
    async def ejecutar(self, operacion: Callable, *args, **kwargs):
        """Ejecuta operación protegida por circuit breaker"""
        
        if self.estado == EstadoCircuitBreaker.ABIERTO:
            if self._debe_intentar_recuperacion():
                self.estado = EstadoCircuitBreaker.MEDIO_ABIERTO
            else:
                raise Exception("Circuit breaker abierto - operación bloqueada")
        
        try:
            resultado = await operacion(*args, **kwargs)
            self._registrar_exito()
            return resultado
            
        except Exception as e:
            self._registrar_fallo()
            raise e
    
    def _debe_intentar_recuperacion(self) -> bool:
        """Determina si debe intentar recuperación"""
        if not self.tiempo_apertura:
            return False
        return (datetime.now() - self.tiempo_apertura).total_seconds() > self.config.timeout_segundos
    
    def _registrar_exito(self):
        """Registra operación exitosa"""
        if self.estado == EstadoCircuitBreaker.MEDIO_ABIERTO:
            self.contador_exitos += 1
            if self.contador_exitos >= self.config.umbral_recuperacion:
                self.estado = EstadoCircuitBreaker.CERRADO
                self.contador_fallos = 0
                self.contador_exitos = 0
        else:
            self.contador_fallos = 0
    
    def _registrar_fallo(self):
        """Registra operación fallida"""
        self.contador_fallos += 1
        self.ultimo_fallo = datetime.now()
        
        if self.contador_fallos >= self.config.umbral_fallos:
            self.estado = EstadoCircuitBreaker.ABIERTO
            self.tiempo_apertura = datetime.now()
            self.contador_exitos = 0

# Política de reintentos
@dataclass
class PoliticaReintentos:
    """Configuración de política de reintentos"""
    max_intentos: int = 3
    delay_inicial_segundos: float = 1.0
    factor_backoff: float = 2.0
    max_delay_segundos: float = 60.0
    jitter: bool = True

class ManejadorReintentos:
    """
    Manejador de reintentos con exponential backoff
    """
    
    def __init__(self, politica: PoliticaReintentos):
        self.politica = politica
    
    async def ejecutar_con_reintentos(self, operacion: Callable, *args, **kwargs):
        """Ejecuta operación con reintentos"""
        ultimo_error = None
        
        for intento in range(self.politica.max_intentos):
            try:
                return await operacion(*args, **kwargs)
                
            except Exception as e:
                ultimo_error = e
                
                if intento == self.politica.max_intentos - 1:
                    break
                
                delay = self._calcular_delay(intento)
                await asyncio.sleep(delay)
        
        raise ultimo_error
    
    def _calcular_delay(self, intento: int) -> float:
        """Calcula delay para reintento con exponential backoff"""
        delay = self.politica.delay_inicial_segundos * (self.politica.factor_backoff ** intento)
        delay = min(delay, self.politica.max_delay_segundos)
        
        if self.politica.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # Jitter ±25%
        
        return delay

# Métricas de despachador
@dataclass
class MetricasDespachador:
    """Métricas del despachador Pulsar"""
    total_mensajes_enviados: int = 0
    total_mensajes_fallidos: int = 0
    total_reintentos: int = 0
    tiempo_promedio_envio_ms: float = 0.0
    ultimo_envio: Optional[datetime] = None
    circuit_breaker_aperturas: int = 0
    mensajes_dead_letter: int = 0

# Dead Letter Queue
class DeadLetterQueue:
    """
    Dead Letter Queue para mensajes que fallan repetidamente
    """
    
    def __init__(self, topico_dlq: str, producer: PulsarProducer):
        self.topico_dlq = topico_dlq
        self.producer = producer
        self.mensajes_dlq: List[Dict[str, Any]] = []
    
    async def enviar_a_dlq(self, mensaje_original: Any, error: Exception, intentos: int):
        """Envía mensaje fallido a Dead Letter Queue"""
        mensaje_dlq = {
            'mensaje_original': mensaje_original,
            'error': str(error),
            'intentos_fallidos': intentos,
            'timestamp_fallo': datetime.now().isoformat(),
            'topico_origen': getattr(mensaje_original, 'topico_origen', 'unknown')
        }
        
        try:
            await self.producer.send_async(
                json.dumps(mensaje_dlq).encode('utf-8'),
                properties={'tipo': 'dead_letter', 'origen': 'conversiones'}
            )
            self.mensajes_dlq.append(mensaje_dlq)
            
        except Exception as e:
            logging.error(f"Error enviando a DLQ: {str(e)}")

# Base del despachador
class DespachadorPulsarBase(ABC):
    """
    Base abstracta para despachadores Pulsar
    Implementa patrón Template Method
    """
    
    def __init__(self, topico: str, cliente_pulsar: PulsarClient,
                 config_circuit_breaker: ConfiguracionCircuitBreaker = None,
                 politica_reintentos: PoliticaReintentos = None):
        self.topico = topico
        self.cliente_pulsar = cliente_pulsar
        self.circuit_breaker = CircuitBreakerPulsar(
            config_circuit_breaker or ConfiguracionCircuitBreaker()
        )
        self.manejador_reintentos = ManejadorReintentos(
            politica_reintentos or PoliticaReintentos()
        )
        self.metricas = MetricasDespachador()
        self.producer = None
        self.dlq = None
        self._configurar_dead_letter_queue()
    
    def _configurar_dead_letter_queue(self):
        """Configura Dead Letter Queue"""
        topico_dlq = f"{self.topico}-dlq"
        producer_dlq = self.cliente_pulsar.create_producer(topico_dlq)
        self.dlq = DeadLetterQueue(topico_dlq, producer_dlq)
    
    async def inicializar(self):
        """Inicializa el despachador"""
        self.producer = self.cliente_pulsar.create_producer(
            self.topico,
            properties={'microservicio': 'conversiones'}
        )
    
    @abstractmethod
    async def procesar_mensaje(self, mensaje: Any) -> Dict[str, Any]:
        """Procesa mensaje específico - implementar en subclases"""
        pass
    
    async def enviar(self, mensaje: Any) -> str:
        """
        Envía mensaje con circuit breaker y reintentos
        Template Method pattern
        """
        inicio = time.time()
        
        try:
            # Preparar mensaje
            mensaje_procesado = await self.procesar_mensaje(mensaje)
            
            # Enviar con protecciones
            mensaje_id = await self.circuit_breaker.ejecutar(
                self.manejador_reintentos.ejecutar_con_reintentos,
                self._enviar_mensaje_interno,
                mensaje_procesado
            )
            
            # Actualizar métricas
            self._actualizar_metricas_exito(inicio)
            return mensaje_id
            
        except Exception as e:
            # Manejar fallo
            await self._manejar_fallo(mensaje, e)
            self._actualizar_metricas_fallo()
            raise e
    
    async def _enviar_mensaje_interno(self, mensaje_procesado: Dict[str, Any]) -> str:
        """Envío interno del mensaje"""
        contenido = json.dumps(mensaje_procesado).encode('utf-8')
        propiedades = {
            'microservicio_origen': 'conversiones',
            'timestamp': str(int(time.time() * 1000)),
            'correlation_id': mensaje_procesado.get('correlation_id', str(uuid.uuid4()))
        }
        
        return await self.producer.send_async(contenido, properties=propiedades)
    
    async def _manejar_fallo(self, mensaje: Any, error: Exception):
        """Maneja fallos de envío"""
        logging.error(f"Error enviando mensaje a {self.topico}: {str(error)}")
        
        # Enviar a Dead Letter Queue si se agotaron reintentos
        if self.manejador_reintentos.politica.max_intentos > 0:
            await self.dlq.enviar_a_dlq(
                mensaje, 
                error, 
                self.manejador_reintentos.politica.max_intentos
            )
    
    def _actualizar_metricas_exito(self, inicio: float):
        """Actualiza métricas de envío exitoso"""
        self.metricas.total_mensajes_enviados += 1
        self.metricas.ultimo_envio = datetime.now()
        
        tiempo_envio = (time.time() - inicio) * 1000  # ms
        if self.metricas.total_mensajes_enviados == 1:
            self.metricas.tiempo_promedio_envio_ms = tiempo_envio
        else:
            # Media móvil
            self.metricas.tiempo_promedio_envio_ms = (
                self.metricas.tiempo_promedio_envio_ms * 0.9 + tiempo_envio * 0.1
            )
    
    def _actualizar_metricas_fallo(self):
        """Actualiza métricas de fallo"""
        self.metricas.total_mensajes_fallidos += 1
        if self.circuit_breaker.estado == EstadoCircuitBreaker.ABIERTO:
            self.metricas.circuit_breaker_aperturas += 1

# Despachador para eventos de integración
class DespachadorEventosIntegracion(DespachadorPulsarBase):
    """
    Despachador específico para eventos de integración
    """
    
    def __init__(self, cliente_pulsar: PulsarClient):
        super().__init__(
            "persistent://public/default/conversiones-integracion",
            cliente_pulsar,
            ConfiguracionCircuitBreaker(umbral_fallos=3, timeout_segundos=30),
            PoliticaReintentos(max_intentos=3, delay_inicial_segundos=1.0)
        )
    
    async def procesar_mensaje(self, evento) -> Dict[str, Any]:
        """Procesa evento de integración"""
        from ..aplicacion.eventos_integracion import SerializadorEventosIntegracion
        
        # Serializar evento
        mensaje = SerializadorEventosIntegracion.serializar(evento)
        
        # Agregar metadatos de routing
        mensaje['routing'] = {
            'microservicio_destino': evento.microservicio_destino,
            'tipo_evento': evento.__class__.__name__,
            'prioridad': self._determinar_prioridad(evento)
        }
        
        return mensaje
    
    def _determinar_prioridad(self, evento) -> str:
        """Determina prioridad del evento"""
        # Eventos críticos para balance de afiliados
        eventos_alta_prioridad = [
            'ComisionGeneradaIntegracion',
            'ComisionAplicadaIntegracion',
            'ComisionCanceladaIntegracion'
        ]
        
        if evento.__class__.__name__ in eventos_alta_prioridad:
            return 'alta'
        
        return 'normal'

# Despachador para eventos de dominio
class DespachadorEventosDominio(DespachadorPulsarBase):
    """
    Despachador específico para eventos de dominio
    """
    
    def __init__(self, cliente_pulsar: PulsarClient):
        super().__init__(
            "persistent://public/default/conversiones-dominio",
            cliente_pulsar,
            ConfiguracionCircuitBreaker(umbral_fallos=5, timeout_segundos=60),
            PoliticaReintentos(max_intentos=5, delay_inicial_segundos=0.5)
        )
    
    async def procesar_mensaje(self, evento) -> Dict[str, Any]:
        """Procesa evento de dominio"""
        from ..dominio.eventos import SerializadorEventosDominio
        
        # Serializar evento de dominio
        mensaje = SerializadorEventosDominio.serializar(evento)
        
        # Agregar contexto de dominio
        mensaje['contexto_dominio'] = {
            'agregado_id': getattr(evento, 'agregado_id', None),
            'agregado_tipo': getattr(evento, 'agregado_tipo', 'Conversion'),
            'version_evento': getattr(evento, 'version', 1)
        }
        
        return mensaje

# Despachador para outbox
class DespachadorOutbox(DespachadorPulsarBase):
    """
    Despachador específico para patrón Outbox
    """
    
    def __init__(self, cliente_pulsar: PulsarClient):
        super().__init__(
            "persistent://public/default/conversiones-outbox",
            cliente_pulsar,
            ConfiguracionCircuitBreaker(umbral_fallos=2, timeout_segundos=30),
            PoliticaReintentos(max_intentos=10, delay_inicial_segundos=2.0)
        )
    
    async def procesar_mensaje(self, entrada_outbox) -> Dict[str, Any]:
        """Procesa entrada del outbox"""
        
        mensaje = {
            'id_entrada': entrada_outbox.id,
            'tipo_evento': entrada_outbox.tipo_evento.value,
            'datos_evento': entrada_outbox.datos_evento,
            'fecha_creacion': entrada_outbox.fecha_creacion.isoformat(),
            'intentos_procesamiento': entrada_outbox.intentos_procesamiento,
            'estado': entrada_outbox.estado.value
        }
        
        # Metadatos de outbox
        mensaje['outbox_metadata'] = {
            'correlacion_id': entrada_outbox.correlation_id,
            'causacion_id': entrada_outbox.causation_id,
            'topico_destino': entrada_outbox.topico_destino,
            'requerire_confirmacion': entrada_outbox.requiere_confirmacion
        }
        
        return mensaje

# Factory para despachadores
class FabricaDespachadores:
    """
    Factory para crear despachadores Pulsar específicos
    """
    
    def __init__(self, url_pulsar: str = "pulsar://localhost:6650"):
        self.cliente_pulsar = PulsarClient(url_pulsar)
        self._despachadores: Dict[str, DespachadorPulsarBase] = {}
    
    async def obtener_despachador_integracion(self) -> DespachadorEventosIntegracion:
        """Obtiene despachador para eventos de integración"""
        if 'integracion' not in self._despachadores:
            despachador = DespachadorEventosIntegracion(self.cliente_pulsar)
            await despachador.inicializar()
            self._despachadores['integracion'] = despachador
        
        return self._despachadores['integracion']
    
    async def obtener_despachador_dominio(self) -> DespachadorEventosDominio:
        """Obtiene despachador para eventos de dominio"""
        if 'dominio' not in self._despachadores:
            despachador = DespachadorEventosDominio(self.cliente_pulsar)
            await despachador.inicializar()
            self._despachadores['dominio'] = despachador
        
        return self._despachadores['dominio']
    
    async def obtener_despachador_outbox(self) -> DespachadorOutbox:
        """Obtiene despachador para outbox"""
        if 'outbox' not in self._despachadores:
            despachador = DespachadorOutbox(self.cliente_pulsar)
            await despachador.inicializar()
            self._despachadores['outbox'] = despachador
        
        return self._despachadores['outbox']
    
    def obtener_metricas_globales(self) -> Dict[str, MetricasDespachador]:
        """Obtiene métricas de todos los despachadores"""
        return {
            nombre: despachador.metricas 
            for nombre, despachador in self._despachadores.items()
        }
    
    async def cerrar_todos(self):
        """Cierra todos los despachadores"""
        for despachador in self._despachadores.values():
            if despachador.producer:
                despachador.producer.close()
        
        self.cliente_pulsar.close()
        self._despachadores.clear()

# Configuración global de despachadores
@dataclass
class ConfiguracionDespachadores:
    """Configuración global para despachadores Pulsar"""
    
    # Configuración Pulsar
    url_pulsar: str = "pulsar://localhost:6650"
    tenant: str = "public"
    namespace: str = "default"
    
    # Timeouts
    timeout_conexion_segundos: int = 30
    timeout_operacion_segundos: int = 10
    
    # Configuración de reintentos por defecto
    max_reintentos_por_defecto: int = 3
    delay_inicial_por_defecto: float = 1.0
    
    # Configuración circuit breaker por defecto
    umbral_fallos_por_defecto: int = 5
    timeout_circuit_breaker_segundos: float = 60.0
    
    # Configuración Dead Letter Queue
    habilitar_dlq: bool = True
    max_mensajes_dlq: int = 1000
    
    # Monitoreo
    habilitar_metricas: bool = True
    intervalo_metricas_segundos: int = 60

# Servicio de configuración
class ServicioConfiguracionDespachadores:
    """
    Servicio para configurar despachadores según ambiente
    """
    
    @staticmethod
    def obtener_configuracion_desarrollo() -> ConfiguracionDespachadores:
        """Configuración para desarrollo"""
        return ConfiguracionDespachadores(
            url_pulsar="pulsar://localhost:6650",
            max_reintentos_por_defecto=2,
            umbral_fallos_por_defecto=3,
            timeout_circuit_breaker_segundos=30.0
        )
    
    @staticmethod
    def obtener_configuracion_produccion() -> ConfiguracionDespachadores:
        """Configuración para producción"""
        return ConfiguracionDespachadores(
            url_pulsar="pulsar://pulsar-cluster:6650",
            max_reintentos_por_defecto=5,
            umbral_fallos_por_defecto=10,
            timeout_circuit_breaker_segundos=120.0,
            max_mensajes_dlq=10000
        )
    
    @staticmethod
    def obtener_configuracion_testing() -> ConfiguracionDespachadores:
        """Configuración para testing"""
        return ConfiguracionDespachadores(
            url_pulsar="pulsar://test-pulsar:6650",
            max_reintentos_por_defecto=1,
            umbral_fallos_por_defecto=2,
            timeout_circuit_breaker_segundos=10.0,
            habilitar_dlq=False
        )

# Monitor de salud de despachadores
class MonitorSaludDespachadores:
    """
    Monitor de salud para despachadores Pulsar
    """
    
    def __init__(self, fabrica: FabricaDespachadores):
        self.fabrica = fabrica
        self.umbral_latencia_ms = 1000  # 1 segundo
        self.umbral_tasa_error = 0.05   # 5%
    
    async def verificar_salud(self) -> Dict[str, Any]:
        """Verifica salud de todos los despachadores"""
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'estado_general': 'saludable',
            'despachadores': {},
            'alertas': []
        }
        
        metricas = self.fabrica.obtener_metricas_globales()
        
        for nombre, metrica in metricas.items():
            estado_despachador = self._verificar_despachador(nombre, metrica)
            resultado['despachadores'][nombre] = estado_despachador
            
            if estado_despachador['estado'] != 'saludable':
                resultado['estado_general'] = 'degradado'
                resultado['alertas'].extend(estado_despachador['alertas'])
        
        return resultado
    
    def _verificar_despachador(self, nombre: str, metrica: MetricasDespachador) -> Dict[str, Any]:
        """Verifica salud de un despachador específico"""
        estado = {
            'nombre': nombre,
            'estado': 'saludable',
            'alertas': [],
            'metricas': {
                'mensajes_enviados': metrica.total_mensajes_enviados,
                'mensajes_fallidos': metrica.total_mensajes_fallidos,
                'tiempo_promedio_ms': metrica.tiempo_promedio_envio_ms,
                'ultimo_envio': metrica.ultimo_envio.isoformat() if metrica.ultimo_envio else None
            }
        }
        
        # Verificar tasa de error
        if metrica.total_mensajes_enviados > 0:
            tasa_error = metrica.total_mensajes_fallidos / metrica.total_mensajes_enviados
            if tasa_error > self.umbral_tasa_error:
                estado['estado'] = 'degradado'
                estado['alertas'].append(f"Tasa de error alta: {tasa_error:.2%}")
        
        # Verificar latencia
        if metrica.tiempo_promedio_envio_ms > self.umbral_latencia_ms:
            estado['estado'] = 'degradado'
            estado['alertas'].append(f"Latencia alta: {metrica.tiempo_promedio_envio_ms:.2f}ms")
        
        # Verificar actividad reciente
        if metrica.ultimo_envio:
            tiempo_inactivo = datetime.now() - metrica.ultimo_envio
            if tiempo_inactivo > timedelta(minutes=10):
                estado['alertas'].append(f"Sin actividad por {tiempo_inactivo}")
        
        return estado