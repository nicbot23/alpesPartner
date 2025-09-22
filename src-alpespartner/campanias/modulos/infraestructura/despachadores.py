import pulsar
import logging
from pulsar.schema import AvroSchema
from typing import Any, Optional

from campanias.seedwork.infraestructura import utils

from campanias.modulos.infraestructura.schema.v1.comandos import (
    ComandoBuscarAfiliadosElegibles,
    BuscarAfiliadosElegiblesPayload,
)

logger = logging.getLogger(__name__)

class Despachador:
    def __init__(self):
        self.cliente: Optional[pulsar.Client] = None
        self._productores = {}
    
    def _obtener_cliente(self):
        if self.cliente is None:
            try:
                self.cliente = pulsar.Client(
                    f'pulsar://{utils.broker_host()}:6650',
                    operation_timeout_seconds=30,
                    connection_timeout_seconds=10
                )
                logger.info("Cliente Pulsar conectado exitosamente")
            except Exception as e:
                logger.error(f"Error conectando a Pulsar: {e}")
                raise
        return self.cliente
    
    def _obtener_productor(self, topico: str, schema_class):
        key = f"{topico}_{schema_class.__name__}"
        if key not in self._productores:
            try:
                cliente = self._obtener_cliente()
                self._productores[key] = cliente.create_producer(
                    topico,
                    schema=AvroSchema(schema_class),
                    send_timeout_millis=10000,
                    batching_enabled=True,
                    batching_max_messages=100,
                    batching_max_publish_delay_millis=1000
                )
                logger.info(f"Productor creado para tópico: {topico}")
            except Exception as e:
                logger.error(f"Error creando productor para {topico}: {e}")
                raise
        return self._productores[key]

    async def publicar_mensaje(self, mensaje: Any, topico: str):
        try:
            productor = self._obtener_productor(topico, mensaje.__class__)
            # Usar send_async para operaciones no bloqueantes
            future = productor.send_async(mensaje)
            # Opcionalmente esperar confirmación
            # message_id = await future
            logger.debug(f"Mensaje enviado a {topico}: {type(mensaje).__name__}")
        except Exception as e:
            logger.error(f"Error publicando mensaje en {topico}: {e}")
            raise

    async def publicar_evento(self, evento: Any, topico: str):
        logger.info(f"Publicando evento {type(evento).__name__} en {topico}")
        await self.publicar_mensaje(evento, topico)
    
    async def publicar_comando(self, comando: Any, topico: str):
        logger.info(f"Publicando comando {type(comando).__name__} en {topico}")
        await self.publicar_mensaje(comando, topico)

    async def publicar_query(self, query: Any, topico: str):
        logger.info(f"Publicando query {type(query).__name__} en {topico}")
        await self.publicar_mensaje(query, topico)
    
    def cerrar(self):
        """Cierra todas las conexiones de manera limpia"""
        try:
            for productor in self._productores.values():
                productor.close()
            if self.cliente:
                self.cliente.close()
            logger.info("Despachador cerrado correctamente")
        except Exception as e:
            logger.error(f"Error cerrando despachador: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar()
    
    