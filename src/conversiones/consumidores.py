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
        elif "marketing.eventos" in topico:
            await procesar_evento_marketing(datos)
        else:
            logging.warning(f"⚠️ Tipo de tópico no reconocido: {topico}")
            
    except Exception as e:
        logging.error(f"❌ Error procesando mensaje: {str(e)}")
        raise


async def procesar_evento_marketing(datos):
    """Procesar eventos del microservicio de marketing"""
    try:
        # Detectar tipo de evento
        if hasattr(datos, 'tipo_campana') or 'campaña' in str(datos).lower():
            await procesar_evento_campana_creada(datos)
        else:
            logging.info(f"📊 Evento de marketing recibido: {datos}")
    except Exception as e:
        logging.error(f"❌ Error procesando evento de marketing: {e}")


async def procesar_evento_campana_creada(evento):
    """Procesar evento de campaña creada - activar detección automática de conversiones"""
    logging.info(f"🎯 Campaña detectada en Conversiones: {getattr(evento, 'nombre', 'Unknown')}")
    logging.info(f"   📊 Meta conversiones: {getattr(evento, 'meta_conversiones', 0)}")
    logging.info(f"   💰 Presupuesto: ${getattr(evento, 'presupuesto', 0)}")
    
    # Activar detección automática de conversiones para esta campaña
    # En un escenario real, aquí se implementaría:
    # 1. Configurar reglas de detección específicas para la campaña
    # 2. Activar monitoreo en tiempo real
    # 3. Configurar umbrales y parámetros de conversión
    
    # Simulación de activación de detección automática
    campana_id = getattr(evento, 'id', 'unknown')
    meta_conversiones = getattr(evento, 'meta_conversiones', 100)
    
    # Simular conversiones automáticas para la campaña
    conversiones_simuladas = [
        {
            "user_id": f"user-conv-{i}",
            "valor": 500 + (i * 100),
            "campana_id": campana_id,
            "tipo": "AUTO_DETECTION"
        }
        for i in range(1, min(4, meta_conversiones // 50 + 1))  # Simular algunas conversiones
    ]
    
    for conversion in conversiones_simuladas:
        logging.info(f"   💰 Auto-conversión detectada: ${conversion['valor']} para {conversion['user_id']}")
        
        # En un escenario real, aquí se crearían eventos de ConversionDetectada
        # await publicar_evento_conversion_detectada(conversion)
    
    logging.info(f"🚀 Detección automática activada para campaña {campana_id}")
    logging.info(f"   📈 {len(conversiones_simuladas)} conversiones automáticas generadas")

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


# Configuración de suscripciones para Conversiones
SUSCRIPCIONES = [
    {
        'topico': 'marketing.eventos',
        'suscripcion': 'conversiones-campana-creada-sub',
        'schema': 'CampanaCreada',  # Schema del microservicio de marketing
        'manejador': procesar_evento_marketing
    },
    {
        'topico': 'comandos-detectar-conversion',
        'suscripcion': 'conversiones-detectar-sub',
        'schema': 'ComandoDetectarConversion',
        'manejador': procesar_comando_detectar_conversion
    },
    {
        'topico': 'comandos-validar-conversion',
        'suscripcion': 'conversiones-validar-sub',
        'schema': 'ComandoValidarConversion',
        'manejador': procesar_comando_validar_conversion
    }
]


async def iniciar_consumidores():
    """Iniciar todos los consumidores de eventos"""
    tareas = []
    
    for config in SUSCRIPCIONES:
        tarea = asyncio.create_task(
            suscribirse_a_topico(
                config['topico'],
                config['suscripcion'], 
                config['schema']
            )
        )
        tareas.append(tarea)
        logging.info(f"🔄 Iniciando consumidor para {config['topico']}")
    
    # Ejecutar todos los consumidores concurrentemente
    await asyncio.gather(*tareas)