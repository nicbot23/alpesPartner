import asyncio
import logging
from datetime import datetime
from uuid import uuid4
from pulsar.schema import AvroSchema
import pulsar
from .config.api import config
from .eventos import AfiliadoRegistrado, AfiliadoActualizado, AfiliadoDesactivado, AfiliadoValidado

logger = logging.getLogger(__name__)


class Despachador:
    def __init__(self):
        self.client = None
        self.producers = {}
    
    async def inicializar(self):
        """Inicializar cliente Pulsar"""
        try:
            self.client = pulsar.Client(f'pulsar://{config.pulsar_host}:{config.pulsar_port}')
            logger.info("Cliente Pulsar inicializado")
        except Exception as e:
            logger.error(f"Error inicializando cliente Pulsar: {e}")
    
    async def cerrar(self):
        """Cerrar cliente Pulsar"""
        if self.client:
            self.client.close()
            logger.info("Cliente Pulsar cerrado")
    
    async def publicar_mensaje(self, topico: str, mensaje, schema):
        """Publicar mensaje en un tópico específico"""
        try:
            if topico not in self.producers:
                self.producers[topico] = self.client.create_producer(
                    topic=topico,
                    schema=AvroSchema(schema)
                )
            
            producer = self.producers[topico]
            producer.send(mensaje)
            logger.info(f"Mensaje publicado en tópico {topico}")
            
        except Exception as e:
            logger.error(f"Error publicando mensaje en {topico}: {e}")
    
    async def publicar_evento_afiliado_registrado(self, evento: AfiliadoRegistrado):
        """Publicar evento de afiliado registrado"""
        await self.publicar_mensaje('eventos-afiliado-registrado', evento, AfiliadoRegistrado)
    
    async def publicar_evento_afiliado_actualizado(self, evento: AfiliadoActualizado):
        """Publicar evento de afiliado actualizado"""
        await self.publicar_mensaje('eventos-afiliado-actualizado', evento, AfiliadoActualizado)
    
    async def publicar_evento_afiliado_desactivado(self, evento: AfiliadoDesactivado):
        """Publicar evento de afiliado desactivado"""
        await self.publicar_mensaje('eventos-afiliado-desactivado', evento, AfiliadoDesactivado)
    
    async def publicar_evento_afiliado_validado(self, evento: AfiliadoValidado):
        """Publicar evento de afiliado validado"""
        await self.publicar_mensaje('eventos-afiliado-validado', evento, AfiliadoValidado)


# Instancia global del despachador
despachador = Despachador()