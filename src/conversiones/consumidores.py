"""
Consumidores asíncronos para el microservicio Conversiones
"""
import logging
import traceback
import pulsar
import _pulsar
import aiopulsar
import asyncio
from pulsar.schema import *
from conversiones.config import settings

async def suscribirse_a_topico(topico: str, suscripcion: str, schema: Record, tipo_consumidor:_pulsar.ConsumerType=_pulsar.ConsumerType.Shared):
    """
    Suscribirse a un tópico específico de forma asíncrona
    """
    try:
        async with aiopulsar.connect(settings.PULSAR_URL) as cliente:
            async with cliente.subscribe(
                topico, 
                consumer_type=tipo_consumidor,
                subscription_name=suscripcion, 
                schema=AvroSchema(schema)
            ) as consumidor:
                logging.info(f"🔗 Suscrito a tópico: {topico} con suscripción: {suscripcion}")
                
                while True:
                    try:
                        mensaje = await consumidor.receive()
                        datos = mensaje.value()
                        
                        # Procesar el mensaje basado en el tipo de evento/comando
                        await procesar_mensaje(datos, topico)
                        
                        await consumidor.acknowledge(mensaje)
                        logging.info(f"✅ Mensaje procesado exitosamente de {topico}")
                        
                    except Exception as e:
                        logging.error(f"❌ Error procesando mensaje de {topico}: {str(e)}")
                        await consumidor.negative_acknowledge(mensaje)

    except Exception as e:
        logging.error(f'❌ ERROR: Suscribiéndose al tópico! {topico}, {suscripcion}, {schema}')
        logging.error(f"Detalles del error: {str(e)}")
        traceback.print_exc()

async def procesar_mensaje(datos, topico: str):
    """
    Procesar mensajes recibidos según el tópico
    """
    try:
        if "evento-conversion" in topico:
            await procesar_evento_conversion(datos)
        elif "comando-detectar-conversion" in topico:
            await procesar_comando_detectar_conversion(datos)
        elif "comando-validar-conversion" in topico:
            await procesar_comando_validar_conversion(datos)
        elif "comando-confirmar-conversion" in topico:
            await procesar_comando_confirmar_conversion(datos)
        elif "comando-rechazar-conversion" in topico:
            await procesar_comando_rechazar_conversion(datos)
        elif "comando-cancelar-conversion" in topico:
            await procesar_comando_cancelar_conversion(datos)
        else:
            logging.warning(f"⚠️ Tipo de tópico no reconocido: {topico}")
            
    except Exception as e:
        logging.error(f"❌ Error procesando mensaje: {str(e)}")
        raise

async def procesar_evento_conversion(datos):
    """Procesar eventos de conversión"""
    logging.info(f"📊 Procesando evento de conversión: {datos}")
    # TODO: Implementar lógica específica para eventos de conversión
    
async def procesar_comando_detectar_conversion(datos):
    """Procesar comando detectar conversión"""
    logging.info(f"🔍 Procesando comando detectar conversión: {datos}")
    # TODO: Implementar lógica para detectar conversión
    
async def procesar_comando_validar_conversion(datos):
    """Procesar comando validar conversión"""
    logging.info(f"✓ Procesando comando validar conversión: {datos}")
    # TODO: Implementar lógica para validar conversión
    
async def procesar_comando_confirmar_conversion(datos):
    """Procesar comando confirmar conversión"""
    logging.info(f"☑️ Procesando comando confirmar conversión: {datos}")
    # TODO: Implementar lógica para confirmar conversión
    
async def procesar_comando_rechazar_conversion(datos):
    """Procesar comando rechazar conversión"""
    logging.info(f"❌ Procesando comando rechazar conversión: {datos}")
    # TODO: Implementar lógica para rechazar conversión
    
async def procesar_comando_cancelar_conversion(datos):
    """Procesar comando cancelar conversión"""
    logging.info(f"🚫 Procesando comando cancelar conversión: {datos}")
    # TODO: Implementar lógica para cancelar conversión