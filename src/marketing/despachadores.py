import asyncio
import logging
from datetime import datetime
from uuid import uuid4
from pulsar.schema import AvroSchema
import pulsar
from .config.api import config
from .eventos import (
    CampanaCreada, CampanaActivada, CampanaDesactivada, ConversionAsignadaACampana,
    ComisionCalculada, NotificacionSolicitada
)

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
    
    async def publicar_evento_campana_creada(self, evento: CampanaCreada):
        """Publicar evento de campaña creada"""
        await self.publicar_mensaje('marketing.eventos', evento, CampanaCreada)
    
    async def publicar_evento_campana_activada(self, evento: CampanaActivada):
        """Publicar evento de campaña activada"""
        await self.publicar_mensaje('marketing.eventos', evento, CampanaActivada)
    
    async def publicar_evento_campana_desactivada(self, evento: CampanaDesactivada):
        """Publicar evento de campaña desactivada"""
        await self.publicar_mensaje('marketing.eventos', evento, CampanaDesactivada)
    
    async def publicar_evento_conversion_asignada(self, evento: ConversionAsignadaACampana):
        """Publicar evento de conversión asignada a campaña"""
        await self.publicar_mensaje('marketing.eventos', evento, ConversionAsignadaACampana)
    
    async def publicar_evento_comision_calculada(self, evento: ComisionCalculada):
        """Publicar evento de comisión calculada"""
        await self.publicar_mensaje('comisiones.eventos', evento, ComisionCalculada)
    
    async def publicar_evento_notificacion_solicitada(self, evento: NotificacionSolicitada):
        """Publicar evento de notificación solicitada"""
        await self.publicar_mensaje('sistema.eventos', evento, NotificacionSolicitada)

    async def publicar_comando_crear_campana(self, comando):
        """Publicar comando para crear campaña - esto generará eventos automáticamente"""
        try:
            # Simular procesamiento del comando y generar eventos correspondientes
            from .eventos import CampanaCreada, ComisionCalculada, NotificacionSolicitada
            
            # Crear eventos basados en el comando
            evento_campana_creada = CampanaCreada(
                id=comando.id,
                campana_id=comando.id,
                nombre=comando.nombre,
                descripcion=comando.descripcion,
                tipo_campana=comando.tipo_campana,
                fecha_inicio=comando.fecha_inicio,
                fecha_fin=comando.fecha_fin,
                estado="creada",
                meta_conversiones=comando.meta_conversiones,
                presupuesto=comando.presupuesto,
                created_by=comando.created_by,
                timestamp=comando.timestamp
            )
            
            # Publicar evento de campaña creada
            await self.publicar_evento_campana_creada(evento_campana_creada)
            
            # Simular configuración de comisiones
            evento_comision = ComisionCalculada(
                id=f"comision-{comando.id}",
                campana_id=comando.id,
                afiliado_id="afiliado-default",
                user_id="system",
                conversion_id="config-inicial",
                monto_comision=0.0,
                porcentaje_comision=5.0,
                fecha_calculo=datetime.now().isoformat(),
                timestamp=comando.timestamp
            )
            
            await self.publicar_evento_comision_calculada(evento_comision)
            
            # Evento de notificación
            evento_notificacion = NotificacionSolicitada(
                id=f"notif-{comando.id}",
                destinatario="marketing-team@alpes.com",
                tipo_notificacion="email",
                plantilla="nueva-campana",
                datos=f'{{"campana": "{comando.nombre}", "presupuesto": {comando.presupuesto}}}',
                prioridad="alta",
                timestamp=comando.timestamp
            )
            
            await self.publicar_evento_notificacion_solicitada(evento_notificacion)
            
            logger.info(f"✅ Comando procesado: Campaña {comando.nombre} creada con eventos publicados")
            
        except Exception as e:
            logger.error(f"Error procesando comando crear campaña: {e}")


# Instancia global del despachador
despachador = Despachador()