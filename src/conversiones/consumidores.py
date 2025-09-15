"""
Consumidores asíncronos para el microservicio Conversiones
"""
import logging
import traceback
import pulsar
import _pulsar
import asyncio
from dataclasses import dataclass
from pulsar.schema import *
from conversiones.config import settings

logger = logging.getLogger(__name__)

# Definiciones locales de eventos para mantener independencia de microservicios
@dataclass
class AfiliadoRegistrado:
    """Evento local para afiliado registrado (recibido de afiliados.eventos)"""
    user_id: str
    email: str
    nombre: str
    apellido: str
    estado: str
    fecha_registro: str

async def suscribirse_a_topico(topico: str, suscripcion: str, schema, manejador):
    """Crear suscripción async a un tópico de Pulsar"""
    try:
        client = pulsar.Client(f'pulsar://{settings.PULSAR_URL.replace("pulsar://", "")}')
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
        elif "afiliados.eventos" in topico:
            await procesar_evento_afiliado_registrado(datos)
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

async def procesar_evento_afiliado_registrado(datos):
    """Procesar evento de afiliado registrado desde microservicio de afiliados"""
    logging.info(f"🔥 Evento recibido: Afiliado registrado {datos}")
    
    try:
        # Verificar que es un evento de afiliado registrado
        if hasattr(datos, 'user_id') and hasattr(datos, 'estado'):
            if datos.estado == "activo":
                # Generar conversión automática para el afiliado
                import random
                from datetime import datetime
                
                conversion_data = {
                    "user_id": datos.user_id,
                    "afiliado_id": datos.user_id,
                    "valor_conversion": round(random.uniform(100, 1000), 2),
                    "tipo_conversion": "registro_automatico",
                    "fecha_conversion": datetime.now().isoformat(),
                    "automatica": True,
                    "metadata": {
                        "generado_por": "evento_afiliado",
                        "email_afiliado": getattr(datos, 'email', ''),
                        "nombre_afiliado": f"{getattr(datos, 'nombre', '')} {getattr(datos, 'apellido', '')}"
                    }
                }
                
                logging.info(f"🎯 Generando conversión automática para afiliado {datos.user_id}")
                
                # TODO: Publicar evento ConversionRegistrada usando el despachador
                # await despachador.publicar_evento_conversion_registrada(conversion_data)
                
                logging.info(f"✅ Conversión automática generada para afiliado {datos.user_id}")
        else:
            logging.warning(f"⚠️ Evento de afiliado incompleto: {datos}")
            
    except Exception as e:
        logging.error(f"❌ Error procesando evento de afiliado registrado: {e}")

# Configuración de suscripciones
SUSCRIPCIONES = [
    {
        'topico': 'afiliados.eventos',
        'suscripcion': 'conversiones-afiliados-eventos',
        'schema': AfiliadoRegistrado,
        'manejador': procesar_evento_afiliado_registrado
    },
    # Agregar más suscripciones según necesidad
]