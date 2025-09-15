import asyncio
import logging
from dataclasses import dataclass, field
from pulsar.schema import AvroSchema
import pulsar
from .config.api import config
from .comandos import ComandoRegistrarAfiliado, ComandoActualizarAfiliado, ComandoDesactivarAfiliado, ComandoValidarAfiliado
from .eventos import AfiliadoRegistrado, AfiliadoActualizado, AfiliadoDesactivado, AfiliadoValidado
from .utils import time_millis, generar_uuid, timestamp_utc
from .despachadores import despachador

# Definir localmente eventos de otros microservicios que consumimos
@dataclass
class CampanaCreada:
    """Evento de campaña creada desde marketing microservice"""
    campana_id: str = ""
    nombre: str = ""
    descripcion: str = ""
    fecha_inicio: str = ""
    fecha_fin: str = ""
    tipo_campana: str = ""
    metadatos: dict = field(default_factory=dict)

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
    
    try:
        # Crear evento de afiliado registrado
        evento = AfiliadoRegistrado(
            id=generar_uuid(),
            user_id=comando.user_id,
            email=comando.email,
            nombre=comando.nombre,
            apellido=comando.apellido,
            numero_documento=comando.numero_documento,
            tipo_documento=comando.tipo_documento,
            telefono=comando.telefono,
            fecha_afiliacion=timestamp_utc(),
            estado="activo",
            timestamp=time_millis()
        )
        
        # Publicar evento
        await despachador.publicar_evento_afiliado_registrado(evento)
        logger.info(f"✅ Evento AfiliadoRegistrado publicado para {comando.user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error procesando comando registrar afiliado: {e}")


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


async def consumir_evento_campana_creada(evento: CampanaCreada):
    """Procesar evento de campaña creada desde marketing"""
    logger.info(f"🔥 Evento recibido: Campaña creada '{evento.nombre}' (ID: {evento.id})")
    
    try:
        # Crear afiliado automático para la campaña
        comando_registro = ComandoRegistrarAfiliado(
            id=generar_uuid(),
            user_id=f"afiliado-auto-{evento.id}",
            email=f"afiliado-{evento.id}@alpes.com",
            nombre=f"Afiliado Auto {evento.nombre}",
            apellido="Sistema",
            numero_documento=f"AUTO{evento.id[:8]}",
            tipo_documento="CC",
            telefono="+571234567890",
            timestamp=time_millis()
        )
        
        # Procesar el comando de registro
        await consumir_comando_registrar_afiliado(comando_registro)
        
        logger.info(f"✅ Afiliado automático creado para campaña {evento.nombre}")
        
    except Exception as e:
        logger.error(f"❌ Error creando afiliado automático para campaña {evento.id}: {e}")


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
    # 🔥 Nueva suscripción para eventos de marketing
    {
        'topico': 'persistent://public/default/marketing.eventos',
        'suscripcion': 'afiliados-marketing-eventos-sub',
        'schema': CampanaCreada,
        'manejador': consumir_evento_campana_creada
    }
]