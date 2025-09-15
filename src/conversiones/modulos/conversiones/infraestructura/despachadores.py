"""
Despachador de eventos para comunicación con otros microservicios
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from ....seedwork.dominio.eventos import EventoDominio
import pulsar
from pulsar.schema import AvroSchema
from ....config.api import settings

logger = logging.getLogger(__name__)


class DespachadorEventos(ABC):
    """Interfaz para despachador de eventos"""
    
    @abstractmethod
    def publicar_evento(self, evento: EventoDominio):
        """Publicar evento de dominio"""
        pass


class DespachadorEventosPulsar(DespachadorEventos):
    """Implementación de despachador usando Apache Pulsar"""
    
    def __init__(self):
        self.client = None
        self.producers = {}
    
    async def inicializar(self):
        """Inicializar cliente Pulsar"""
        try:
            self.client = pulsar.Client(f'pulsar://{settings.pulsar_host}:{settings.pulsar_port}')
            logger.info("Cliente Pulsar inicializado")
        except Exception as e:
            logger.error(f"Error inicializando cliente Pulsar: {e}")
    
    async def cerrar(self):
        """Cerrar cliente Pulsar"""
        if self.client:
            self.client.close()
            logger.info("Cliente Pulsar cerrado")
    
    def publicar_evento(self, evento: EventoDominio):
        """Publicar evento de dominio en Pulsar"""
        try:
            # Determinar tópico basado en el nombre del evento
            topico = f"eventos-{evento.nombre.replace('.', '-')}"
            
            if topico not in self.producers:
                # Crear productor para el tópico si no existe
                # En una implementación real, necesitaríamos el schema apropiado
                self.producers[topico] = self.client.create_producer(
                    topic=topico,
                    # schema=AvroSchema(type(evento))  # Necesitaría adaptación para Pulsar
                )
            
            producer = self.producers[topico]
            
            # Convertir evento a formato JSON para envío
            evento_data = {
                "id": str(evento.id),
                "nombre": evento.nombre,
                "fecha": evento.fecha.isoformat(),
                "correlation_id": evento.correlation_id,
                "causation_id": evento.causation_id,
                # Agregar campos específicos del evento
                **{k: v for k, v in evento.__dict__.items() 
                   if not k.startswith('_') and k not in ['id', 'nombre', 'fecha', 'correlation_id', 'causation_id']}
            }
            
            producer.send(str(evento_data).encode('utf-8'))
            logger.info(f"Evento {evento.nombre} publicado en tópico {topico}")
            
        except Exception as e:
            logger.error(f"Error publicando evento {evento.nombre}: {e}")


# Instancia global del despachador
despachador_eventos = DespachadorEventosPulsar()