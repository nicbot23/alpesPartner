import asyncio
import logging
from pulsar.schema import AvroSchema
import pulsar
from .config.api import config
from .comandos import ComandoRegistrarAfiliado, ComandoActualizarAfiliado, ComandoDesactivarAfiliado, ComandoValidarAfiliado
from .eventos import AfiliadoRegistrado, AfiliadoActualizado, AfiliadoDesactivado, AfiliadoValidado
from .utils import time_millis, generar_uuid

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


async def consumir_evento_campana_creada(evento):
    """Procesar evento de campaña creada - crear afiliaciones automáticamente"""
    logger.info(f"🎯 Campaña creada detectada: {evento.nombre}")
    logger.info(f"   📊 Meta conversiones: {evento.meta_conversiones}")
    logger.info(f"   💰 Presupuesto: ${evento.presupuesto}")
    
    # En un escenario real, aquí se implementaría:
    # 1. Buscar usuarios elegibles para afiliación según criterios de la campaña
    # 2. Crear afiliaciones automáticamente
    # 3. Enviar notificaciones de invitación
    
    # Simulación de creación automática de afiliaciones
    usuarios_potenciales = [
        {"user_id": f"auto-afiliado-{i}", "email": f"user{i}@example.com", "score": 85 + i}
        for i in range(1, 4)  # Simular 3 usuarios potenciales
    ]
    
    for usuario in usuarios_potenciales:
        logger.info(f"   ✅ Auto-afiliando usuario: {usuario['user_id']}")
        
        # Crear comando de registro automático
        comando_registro = ComandoRegistrarAfiliado(
            id=generar_uuid(),
            user_id=usuario['user_id'],
            email=usuario['email'],
            campana_origen=evento.id,
            tipo_afiliacion="AUTO_CAMPANA",
            timestamp=time_millis()
        )
        
        # Procesar registro automáticamente
        await consumir_comando_registrar_afiliado(comando_registro)
    
    logger.info(f"🚀 Procesamiento automático de campaña {evento.nombre} completado")


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
    },
    {
        'topico': 'marketing.eventos',
        'suscripcion': 'afiliados-campana-creada-sub',
        'schema': 'CampanaCreada',  # Schema del microservicio de marketing
        'manejador': consumir_evento_campana_creada
    }
]


async def iniciar_consumidores():
    """Inicializar todos los consumidores de eventos para afiliados"""
    logger.info("🔥 Iniciando consumidores de eventos para microservicio Afiliados")
    
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
    
    logger.info("🚀 Consumidores de afiliados iniciados (algunos pendientes)")
    return tareas