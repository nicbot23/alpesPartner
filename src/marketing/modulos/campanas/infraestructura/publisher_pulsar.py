"""Adaptador de publicación Pulsar para Campañas"""
import os
import json
import logging
import pulsar
from typing import Dict

logger = logging.getLogger(__name__)

class PulsarPublisherCampanas:
    def __init__(self):
        self.client = None
        self.producers = {}
        self._pulsar_url = os.getenv('PULSAR_URL', 'pulsar://pulsar:6650')
        self._marketing_events_topic = os.getenv("MARKETING_EVENTS_TOPIC", "persistent://public/default/marketing.eventos")

    async def inicializar(self):
        if not self.client:
            try:
                self.client = pulsar.Client(self._pulsar_url)
                logger.info(f"[Campañas] Cliente Pulsar inicializado {self._pulsar_url}")
            except Exception as e:
                logger.error(f"Error inicializando Pulsar Campañas: {e}")

    def _get_producer(self, topic: str):
        if topic not in self.producers:
            self.producers[topic] = self.client.create_producer(topic=topic)
        return self.producers[topic]

    async def publicar_campana_creada(self, payload: Dict):
        await self._publicar(self._marketing_events_topic, payload, 'CampanaCreada')

    async def publicar_comision_configurada(self, payload: Dict):
        await self._publicar('comisiones.eventos', payload, 'ComisionCalculada')

    async def publicar_notificacion(self, payload: Dict):
        await self._publicar('sistema.eventos', payload, 'NotificacionSolicitada')

    async def _publicar(self, topic: str, payload: Dict, etiqueta: str):
        try:
            if not self.client:
                await self.inicializar()
            producer = self._get_producer(topic)
            producer.send(json.dumps(payload).encode('utf-8'))
            logger.info(f"📡 [{etiqueta}] publicado en {topic} con correlation_id={payload.get('correlation_id', 'None')}")
        except Exception as e:
            logger.error(f"❌ Error publicando {etiqueta} en {topic}: {e}")

    async def cerrar(self):
        if self.client:
            self.client.close()
            logger.info("Publisher Campañas cerrado")
