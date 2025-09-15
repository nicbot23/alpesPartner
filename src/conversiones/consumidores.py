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
<<<<<<< HEAD
        elif "afiliados.eventos" in topico:
            await procesar_evento_afiliado_registrado(datos)
=======
        elif "marketing.eventos" in topico:
            await procesar_evento_marketing(datos)
>>>>>>> entrega4-nicolas-feature
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

<<<<<<< HEAD
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
=======

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
    try:
        await asyncio.gather(*tareas)
    except Exception as e:
        logging.error(f"❌ Error en consumidores: {e}")


async def iniciar_consumidores_background():
    """Iniciar consumidores en background tasks"""
    for config in SUSCRIPCIONES:
        asyncio.create_task(
            suscribirse_a_topico(
                config['topico'],
                config['suscripcion'], 
                config['schema']
            )
        )
        logging.info(f"🔄 Consumidor iniciado en background: {config['topico']}")
>>>>>>> entrega4-nicolas-feature
