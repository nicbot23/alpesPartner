import json
import pulsar
import traceback
from typing import Callable, Dict
from alpespartner.modulos.comisiones.infraestructura.mapeadores.mapeadores import MapeadorEventosComision
from alpespartner.modulos.comisiones.dominio.eventos import EventoComision, ComisionCalculada, ComisionAprobada

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsumidorComisionPulsar:
    """
    Consumidor de eventos de comision desde Apache Pulsar
    Basado en los patrones de tut-6 para CDC
    """
    
    def __init__(self, pulsar_client: pulsar.Client = None):
        if pulsar_client is None:
            self.pulsar_client = pulsar.Client('pulsar://localhost:6650')
        else:
            self.pulsar_client = pulsar_client
            
        self.mapeador = MapeadorEventosComision()
        self.manejadores: Dict[str, Callable] = {}
        
    def registrar_manejador(self, tipo_evento: str, manejador: Callable):
        """Registra un manejador para un tipo específico de evento"""
        self.manejadores[tipo_evento] = manejador
        logger.info(f"Manejador registrado para tipo de evento: {tipo_evento}")
        
    def consumir_eventos(self, topic: str, subscription_name: str = 'alpespartner-comisiones'):
        """
        Inicia el consumo de eventos desde un topic específico
        """
        try:
            consumer = self.pulsar_client.subscribe(
                topic=topic,
                subscription_name=subscription_name,
                consumer_type=pulsar.ConsumerType.Shared
            )
            
            logger.info(f"Iniciando consumo desde topic: {topic}")
            
            while True:
                try:
                    msg = consumer.receive()
                    self._procesar_mensaje(msg)
                    consumer.acknowledge(msg)
                    
                except Exception as e:
                    logger.error(f"Error procesando mensaje: {str(e)}")
                    logger.error(traceback.format_exc())
                    consumer.negative_acknowledge(msg)
                    
        except Exception as e:
            logger.error(f"Error en consumidor: {str(e)}")
            raise
            
    def _procesar_mensaje(self, msg):
        """Procesa un mensaje recibido desde Pulsar"""
        try:
            # Decodificar mensaje JSON
            mensaje_dict = json.loads(msg.data().decode('utf-8'))
            
            # Extraer tipo de evento
            tipo_evento = mensaje_dict.get('type')
            if not tipo_evento:
                logger.warning("Mensaje sin tipo de evento, omitiendo...")
                return
                
            # Buscar manejador registrado
            manejador = self.manejadores.get(tipo_evento)
            if not manejador:
                logger.warning(f"No hay manejador registrado para el tipo: {tipo_evento}")
                return
                
            # Convertir a objeto de dominio
            evento_dominio = self._dict_a_evento_dominio(mensaje_dict)
            
            # Ejecutar manejador
            manejador(evento_dominio)
            
            logger.info(f"Evento {tipo_evento} procesado exitosamente")
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")
            raise
            
    def _dict_a_evento_dominio(self, mensaje_dict: dict) -> EventoComision:
        """Convierte un diccionario de mensaje a evento de dominio"""
        tipo_evento = mensaje_dict.get('type')
        data = mensaje_dict.get('data', {})
        
        # Mapear según el tipo de evento
        if tipo_evento == 'ComisionCalculada':
            return ComisionCalculada(
                commission_id=data.get('commission_id'),
                occurred_at=data.get('occurred_at')
            )
        elif tipo_evento == 'ComisionAprobada':
            return ComisionAprobada(
                commission_id=data.get('commission_id'),
                occurred_at=data.get('approved_at')
            )
        else:
            raise ValueError(f"Tipo de evento no soportado: {tipo_evento}")


class ConsumidorEventosIntegracion:
    """
    Consumidor genérico para eventos de integración con múltiples versiones
    """
    
    def __init__(self, pulsar_client: pulsar.Client = None):
        if pulsar_client is None:
            self.pulsar_client = pulsar.Client('pulsar://localhost:6650')
        else:
            self.pulsar_client = pulsar_client
            
        self.mapeador = MapeadorEventosComision()
        self.manejadores_v1: Dict[str, Callable] = {}
        self.manejadores_v2: Dict[str, Callable] = {}
        
    def registrar_manejador_v1(self, tipo_evento: str, manejador: Callable):
        """Registra un manejador para eventos v1"""
        self.manejadores_v1[tipo_evento] = manejador
        
    def registrar_manejador_v2(self, tipo_evento: str, manejador: Callable):
        """Registra un manejador para eventos v2"""
        self.manejadores_v2[tipo_evento] = manejador
        
    def consumir_todos_los_topics(self, base_topic: str = 'public/alpespartner/comisiones'):
        """Consume eventos de todos los topics versionados"""
        topics = [f"{base_topic}-v1", f"{base_topic}-v2"]
        
        for topic in topics:
            # En una implementación real, esto debería ser asíncrono
            logger.info(f"Configurando consumidor para topic: {topic}")
            # self.consumir_eventos(topic, f"consumer-{topic.split('-')[-1]}")
            
    def procesar_evento_versionado(self, mensaje_dict: dict, version: str):
        """Procesa un evento según su versión"""
        tipo_evento = mensaje_dict.get('type')
        
        if version == 'v1':
            manejador = self.manejadores_v1.get(tipo_evento)
        elif version == 'v2':
            manejador = self.manejadores_v2.get(tipo_evento)
        else:
            logger.warning(f"Versión no soportada: {version}")
            return
            
        if manejador:
            evento_dominio = self._dict_a_evento_dominio(mensaje_dict)
            manejador(evento_dominio)
        else:
            logger.warning(f"No hay manejador para {tipo_evento} v{version}")
            
    def _dict_a_evento_dominio(self, mensaje_dict: dict) -> EventoComision:
        """Convierte mensaje a evento de dominio"""
        # Implementación similar al consumidor básico
        tipo_evento = mensaje_dict.get('type')
        data = mensaje_dict.get('data', {})
        
        if tipo_evento == 'ComisionCalculada':
            return ComisionCalculada(
                commission_id=data.get('commission_id'),
                occurred_at=data.get('occurred_at')
            )
        elif tipo_evento == 'ComisionAprobada':
            return ComisionAprobada(
                commission_id=data.get('commission_id'),
                occurred_at=data.get('approved_at')
            )
        else:
            raise ValueError(f"Tipo de evento no soportado: {tipo_evento}")
