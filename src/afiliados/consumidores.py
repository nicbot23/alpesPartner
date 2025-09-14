import asyncio
import logging
from pulsar.schema import AvroSchema
import pulsar
from .config.api import config
from .comandos import ComandoRegistrarAfiliado, ComandoActualizarAfiliado, ComandoDesactivarAfiliado, ComandoValidarAfiliado
from .eventos import AfiliadoRegistrado, AfiliadoActualizado, AfiliadoDesactivado, AfiliadoValidado
from .utils import time_millis

logger = logging.getLogger(__name__)


async def suscribirse_a_topico(topico: str, suscripcion: str, schema, manejador):
    """Crear suscripción async a un tópico de Pulsar"""
    try:
        client = pulsar.Client(f'pulsar://{config.pulsar_host}:{config.pulsar_port}')
        consumer = client.subscribe(
            topic=topico,
            subscription_name=suscripcion,
            schema=AvroSchema(schema)
        )
        
        logger.info(f"Suscrito a tópico {topico} con suscripción {suscripcion}")
        
        while True:
            try:
                mensaje = consumer.receive(timeout_millis=1000)
                await manejador(mensaje.value())
                consumer.acknowledge(mensaje)
                await asyncio.sleep(0.1)
            except Exception as e:
                if "Timeout" not in str(e):
                    logger.error(f"Error procesando mensaje: {e}")
                await asyncio.sleep(0.1)
                
    except Exception as e:
        logger.error(f"Error en suscripción a {topico}: {e}")


async def consumir_comando_registrar_afiliado(comando: ComandoRegistrarAfiliado):
    """Procesar comando de registro de afiliado"""
    logger.info(f"Procesando comando registrar afiliado: {comando.user_id}")
    # Lógica de registro
    # Emitir evento AfiliadoRegistrado


async def consumir_comando_actualizar_afiliado(comando: ComandoActualizarAfiliado):
    """Procesar comando de actualización de afiliado"""
    logger.info(f"Procesando comando actualizar afiliado: {comando.user_id}")
    # Lógica de actualización
    # Emitir evento AfiliadoActualizado


async def consumir_comando_desactivar_afiliado(comando: ComandoDesactivarAfiliado):
    """Procesar comando de desactivación de afiliado"""
    logger.info(f"Procesando comando desactivar afiliado: {comando.user_id}")
    # Lógica de desactivación
    # Emitir evento AfiliadoDesactivado


async def consumir_comando_validar_afiliado(comando: ComandoValidarAfiliado):
    """Procesar comando de validación de afiliado"""
    logger.info(f"Procesando comando validar afiliado: {comando.user_id}")
    # Lógica de validación
    # Emitir evento AfiliadoValidado


# Configuración de suscripciones
SUSCRIPCIONES = [
    {
        'topico': 'comandos-registrar-afiliado',
        'suscripcion': 'afiliados-registrar-sub',
        'schema': ComandoRegistrarAfiliado,
        'manejador': consumir_comando_registrar_afiliado
    },
    {
        'topico': 'comandos-actualizar-afiliado', 
        'suscripcion': 'afiliados-actualizar-sub',
        'schema': ComandoActualizarAfiliado,
        'manejador': consumir_comando_actualizar_afiliado
    },
    {
        'topico': 'comandos-desactivar-afiliado',
        'suscripcion': 'afiliados-desactivar-sub', 
        'schema': ComandoDesactivarAfiliado,
        'manejador': consumir_comando_desactivar_afiliado
    },
    {
        'topico': 'comandos-validar-afiliado',
        'suscripcion': 'afiliados-validar-sub',
        'schema': ComandoValidarAfiliado,
        'manejador': consumir_comando_validar_afiliado
    }
]