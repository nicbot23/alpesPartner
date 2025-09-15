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
            import random
            
            # 1️⃣ Crear evento de campaña creada
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
            
            # Publicar evento principal
            await self.publicar_evento_campana_creada(evento_campana_creada)
            logger.info(f"📢 Evento CampanaCreada publicado: {comando.nombre}")
            
            # 2️⃣ Simular múltiples comisiones para diferentes afiliados
            num_afiliados = random.randint(3, 8)
            for i in range(num_afiliados):
                evento_comision = ComisionCalculada(
                    id=f"comision-{comando.id}-af{i+1}",
                    campana_id=comando.id,
                    afiliado_id=f"afiliado-{comando.tipo_campana}-{i+1}",
                    user_id=f"user-{i+1}",
                    conversion_id=f"config-{comando.tipo_campana}-{i+1}",
                    monto_comision=round(random.uniform(50.0, 500.0), 2),
                    porcentaje_comision=round(random.uniform(3.0, 12.0), 1),
                    fecha_calculo=datetime.now().isoformat(),
                    timestamp=comando.timestamp + i
                )
                
                await self.publicar_evento_comision_calculada(evento_comision)
            
            logger.info(f"💰 {num_afiliados} eventos ComisionCalculada publicados")
            
            # 3️⃣ Múltiples notificaciones para diferentes destinatarios
            destinatarios = [
                ("marketing-team@alpes.com", "email", "nueva-campana"),
                ("afiliados-manager@alpes.com", "sms", "nueva-oportunidad"),
                ("analytics@alpes.com", "slack", "nueva-campana-analytics")
            ]
            
            for i, (dest, tipo, plantilla) in enumerate(destinatarios):
                evento_notificacion = NotificacionSolicitada(
                    id=f"notif-{comando.id}-{i+1}",
                    destinatario=dest,
                    tipo_notificacion=tipo,
                    plantilla=plantilla,
                    datos=f'{{"campana": "{comando.nombre}", "presupuesto": {comando.presupuesto}, "tipo": "{comando.tipo_campana}"}}',
                    prioridad="alta" if i == 0 else "media",
                    timestamp=comando.timestamp + i + 100
                )
                
                await self.publicar_evento_notificacion_solicitada(evento_notificacion)
            
            logger.info(f"📧 {len(destinatarios)} eventos NotificacionSolicitada publicados")
            
            # 4️⃣ Log de resumen
            total_eventos = 1 + num_afiliados + len(destinatarios)
            logger.info(f"✅ Campaña {comando.nombre} procesada → {total_eventos} eventos publicados")
            logger.info(f"   📊 Distribución: 1 CampanaCreada + {num_afiliados} Comisiones + {len(destinatarios)} Notificaciones")
            
        except Exception as e:
            logger.error(f"❌ Error procesando comando crear campaña: {e}")
            raise


# Instancia global del despachador
despachador = Despachador()