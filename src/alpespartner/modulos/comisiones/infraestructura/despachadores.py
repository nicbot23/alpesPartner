import json
import pulsar
from typing import Optional
import traceback
from alpespartner.seedwork.infraestructura.dispatchers import Dispatcher
from alpespartner.modulos.comisiones.infraestructura.mapeadores.mapeadores import MapeadorEventosComision
from alpespartner.modulos.comisiones.dominio.eventos import EventoComision

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Funciones de compatibilidad para comandos básicos
import os
PULSAR_URL = os.getenv('PULSAR_URL', 'pulsar://localhost:6650')
TOPIC_CMDS = os.getenv('TOPIC_CMDS', 'persistent://public/default/commands')

def publicar_comando_integracion(tipo: str, payload: dict):
    client = pulsar.Client(PULSAR_URL)
    try:
        producer = client.create_producer(TOPIC_CMDS)
        producer.send(json.dumps({'type': tipo, 'payload': payload}).encode('utf-8'))
    finally:
        client.close()


class DespachadorComisionPulsar(Dispatcher):
    """
    Despachador de eventos de comision usando Apache Pulsar
    Basado en los patrones de tut-6 para CDC
    """
    
    def __init__(self, pulsar_client: pulsar.Client = None):
        if pulsar_client is None:
            self.pulsar_client = pulsar.Client('pulsar://localhost:6650')
        else:
            self.pulsar_client = pulsar_client
            
        self.mapeador = MapeadorEventosComision()
        self.topic = 'public/alpespartner/comisiones'
        
    def _publicar_mensaje(self, mensaje: dict, topico: str):
        """Publica un mensaje en Pulsar"""
        try:
            producer = self.pulsar_client.create_producer(topico)
            producer.send(json.dumps(mensaje).encode('utf-8'))
            producer.close()
            logger.info(f"Mensaje enviado exitosamente al topic {topico}")
        except Exception as e:
            logger.error(f"Error enviando mensaje a topic {topico}: {str(e)}")
            raise
            
    def publicar_evento(self, evento: EventoComision, version: str = None) -> None:
        """
        Publica un evento de comision convertido al formato Pulsar/CloudEvents
        """
        try:
            if version is None:
                version = self.mapeador.LATEST_VERSION
                
            # Mapear evento a formato de integración
            evento_integracion = self.mapeador.entidad_a_dto(evento, version=version)
            
            # Convertir a diccionario para serialización
            mensaje = {
                'id': evento_integracion.id,
                'time': evento_integracion.time,
                'specversion': evento_integracion.specversion,
                'type': evento_integracion.type,
                'datacontenttype': evento_integracion.datacontenttype,
                'service_name': evento_integracion.service_name,
                'data': self._payload_a_dict(evento_integracion.data)
            }
            
            # Publicar al topic correspondiente
            topic_version = f"{self.topic}-{version}"
            self._publicar_mensaje(mensaje, topic_version)
            
            logger.info(f"Evento {evento.__class__.__name__} publicado en {topic_version}")
            
        except Exception as e:
            logger.error(f"Error publicando evento {evento.__class__.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
            
    def _payload_a_dict(self, payload):
        """Convierte el payload a diccionario para serialización JSON"""
        if hasattr(payload, '__dict__'):
            return payload.__dict__
        elif hasattr(payload, '_asdict'):
            return payload._asdict()
        else:
            # Para clases Record de Pulsar
            result = {}
            for attr in dir(payload):
                if not attr.startswith('_'):
                    value = getattr(payload, attr)
                    if not callable(value):
                        result[attr] = value
            return result
