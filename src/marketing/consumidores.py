import asyncio
import logging
from dataclasses import dataclass, field
from pulsar.schema import AvroSchema
import pulsar
from .config.api import config
from .comandos import (
    ComandoCrearCampana, ComandoActivarCampana, ComandoDesactivarCampana,
    ComandoAsignarConversionACampana, ComandoCalcularComision, ComandoEnviarNotificacion
)
from .eventos import (
    CampanaCreada, CampanaActivada, CampanaDesactivada, ConversionAsignadaACampana,
    ComisionCalculada, NotificacionSolicitada
)
from .utils import time_millis, generar_uuid, calcular_comision, timestamp_utc
from .despachadores import despachador

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


async def consumir_comando_crear_campana(comando: ComandoCrearCampana):
    """Procesar comando de creación de campaña"""
    logger.info(f"Procesando comando crear campaña: {comando.nombre}")
    
    # Crear evento de campaña creada
    evento = CampanaCreada(
        id=generar_uuid(),
        nombre=comando.nombre,
        descripcion=comando.descripcion,
        tipo_campana=comando.tipo_campana,
        fecha_inicio=comando.fecha_inicio,
        fecha_fin=comando.fecha_fin,
        estado="creada",
        meta_conversiones=comando.meta_conversiones,
        presupuesto=comando.presupuesto,
        created_by=comando.created_by,
        timestamp=time_millis()
    )
    
    await despachador.publicar_evento_campana_creada(evento)
    logger.info(f"Campaña creada: {comando.nombre}")


async def consumir_comando_activar_campana(comando: ComandoActivarCampana):
    """Procesar comando de activación de campaña"""
    logger.info(f"Procesando comando activar campaña: {comando.campana_id}")
    
    # Crear evento de campaña activada
    evento = CampanaActivada(
        id=generar_uuid(),
        campana_id=comando.campana_id,
        fecha_activacion=time_millis(),
        criterios_segmentacion=comando.criterios_segmentacion,
        timestamp=time_millis()
    )
    
    await despachador.publicar_evento_campana_activada(evento)
    logger.info(f"Campaña activada: {comando.campana_id}")


async def consumir_comando_asignar_conversion(comando: ComandoAsignarConversionACampana):
    """Procesar comando de asignación de conversión a campaña"""
    logger.info(f"Procesando asignación conversión {comando.conversion_id} a campaña {comando.campana_id}")
    
    # Crear evento de conversión asignada
    evento = ConversionAsignadaACampana(
        id=generar_uuid(),
        campana_id=comando.campana_id,
        conversion_id=comando.conversion_id,
        user_id=comando.user_id,
        valor_conversion=comando.valor_conversion,
        timestamp=time_millis()
    )
    
    await despachador.publicar_evento_conversion_asignada(evento)
    
    # Calcular comisión automáticamente
    await procesar_calculo_comision(comando.campana_id, comando.user_id, comando.conversion_id, comando.valor_conversion)


async def procesar_calculo_comision(campana_id: str, user_id: str, conversion_id: str, valor_conversion: float):
    """Calcular comisión para una conversión"""
    logger.info(f"Calculando comisión para conversión {conversion_id}")
    
    # Calcular comisión (5% por defecto)
    monto_comision = calcular_comision(valor_conversion)
    
    # Crear evento de comisión calculada
    evento = ComisionCalculada(
        id=generar_uuid(),
        campana_id=campana_id,
        afiliado_id=user_id,  # Asumimos que user_id es el afiliado
        user_id=user_id,
        conversion_id=conversion_id,
        monto_comision=monto_comision,
        porcentaje_comision=0.05,
        fecha_calculo=timestamp_utc(),
        timestamp=time_millis()
    )
    
    await despachador.publicar_evento_comision_calculada(evento)
    
    # Solicitar notificación al afiliado
    await solicitar_notificacion_comision(user_id, monto_comision, conversion_id)


async def solicitar_notificacion_comision(user_id: str, monto_comision: float, conversion_id: str):
    """Solicitar notificación de comisión"""
    evento = NotificacionSolicitada(
        id=generar_uuid(),
        destinatario=user_id,
        tipo_notificacion="email",
        plantilla="comision_calculada",
        datos=f'{{"monto": {monto_comision}, "conversion_id": "{conversion_id}"}}',
        prioridad="media",
        timestamp=time_millis()
    )
    
    await despachador.publicar_evento_notificacion_solicitada(evento)


# Escuchar eventos de otros microservicios
async def consumir_evento_conversion_detectada(evento):
    """Procesar evento de conversión detectada desde microservicio de conversiones"""
    logger.info(f"🔥 Conversión detectada: {evento.user_id}, valor: {evento.conversion_value}")
    
    try:
        # Asignar conversión a campaña apropiada
        comando = ComandoAsignarConversionACampana(
            id=generar_uuid(),
            campana_id=getattr(evento, 'campaign_id', 'campana-default'),
            conversion_id=evento.conversion_id,
            user_id=evento.user_id,
            valor_conversion=evento.conversion_value,
            timestamp=time_millis()
        )
        
        await consumir_comando_asignar_conversion(comando)
        logger.info(f"✅ Conversión {evento.conversion_id} procesada automáticamente")
        
    except Exception as e:
        logger.error(f"❌ Error procesando conversión detectada: {e}")


async def consumir_evento_afiliado_registrado(evento):
    """Procesar evento de afiliado registrado"""
    logger.info(f"Afiliado registrado: {evento.user_id}")
    
    # Solicitar notificación de bienvenida
    notificacion = NotificacionSolicitada(
        id=generar_uuid(),
        destinatario=evento.user_id,
        tipo_notificacion="email",
        plantilla="bienvenida_afiliado",
        datos=f'{{"nombre": "{evento.nombre}", "email": "{evento.email}"}}',
        prioridad="alta",
        timestamp=time_millis()
    )
    
    await despachador.publicar_evento_notificacion_solicitada(notificacion)


# Importar eventos de otros microservicios - definir aquí mismo para evitar imports complejos
@dataclass
class ConversionDetected:
    """Evento de conversión detectada desde conversiones microservice"""
    conversion_id: str = ""
    afiliado_id: str = ""
    campana_id: str = ""
    monto: float = 0.0
    fecha_conversion: str = ""
    metadatos: dict = field(default_factory=dict)

@dataclass  
class AfiliadoRegistrado:
    """Evento de afiliado registrado desde afiliados microservice"""
    afiliado_id: str = ""
    nombre: str = ""
    email: str = ""
    fecha_registro: str = ""
    nivel: str = "BRONCE"
    metadatos: dict = field(default_factory=dict)

# Configuración de suscripciones
SUSCRIPCIONES = [
    {
        'topico': 'comandos-crear-campana',
        'suscripcion': 'marketing-crear-campana-sub',
        'schema': ComandoCrearCampana,
        'manejador': consumir_comando_crear_campana
    },
    {
        'topico': 'comandos-activar-campana',
        'suscripcion': 'marketing-activar-campana-sub',
        'schema': ComandoActivarCampana,
        'manejador': consumir_comando_activar_campana
    },
    {
        'topico': 'persistent://public/default/conversiones.eventos',
        'suscripcion': 'marketing-conversiones-eventos-sub',
        'schema': ConversionDetected,
        'manejador': consumir_evento_conversion_detectada
    },
    {
        'topico': 'persistent://public/default/afiliados.eventos',
        'suscripcion': 'marketing-afiliados-eventos-sub',
        'schema': AfiliadoRegistrado,
        'manejador': consumir_evento_afiliado_registrado
    }
]


async def iniciar_consumidores():
    """Inicializar todos los consumidores de eventos para marketing"""
    logger.info("🔥 Iniciando consumidores de eventos para microservicio Marketing")
    
    # Por ahora, solo iniciar consumidores que tienen schemas válidos
    tareas = []
    for config_sub in SUSCRIPCIONES:
        if isinstance(config_sub['schema'], str):
            logger.info(f"   ⚠️ Saltando {config_sub['topico']} - schema pendiente de implementar")
            continue
            
        tarea = asyncio.create_task(
            suscribirse_a_topico(
                config_sub['topico'],
                config_sub['suscripcion'],
                config_sub['schema'],
                config_sub['manejador']
            )
        )
        tareas.append(tarea)
        logger.info(f"   ✅ Consumidor iniciado para tópico: {config_sub['topico']}")
    
    logger.info("🚀 Consumidores de marketing iniciados (algunos pendientes)")
    return tareas