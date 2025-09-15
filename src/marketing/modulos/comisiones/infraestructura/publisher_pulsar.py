"""Publisher Pulsar especializado para Comisiones"""
import os
import json
import logging
import pulsar
from typing import Dict

logger = logging.getLogger(__name__)

class PulsarPublisherComisiones:
    def __init__(self) -> None:
        self._url = os.getenv('PULSAR_URL', 'pulsar://pulsar:6650')
        self._client = None
        self._producers = {}
        # Permite alinear nombre de tópico con docker-compose (marketing.comisiones.eventos)
        self._topic_comisiones = os.getenv('COMISIONES_EVENTS_TOPIC', 'persistent://public/default/marketing.comisiones.eventos')

    async def inicializar(self):
        if not self._client:
            try:
                self._client = pulsar.Client(self._url)
                logger.info(f"[Comisiones] Cliente Pulsar inicializado {self._url}")
            except Exception as e:
                logger.error(f"Error init Pulsar Comisiones: {e}")

    def _producer(self, topic: str):
        if topic not in self._producers:
            self._producers[topic] = self._client.create_producer(topic=topic)
        return self._producers[topic]

    async def publicar_comision_calculada(self, payload: Dict):
        # Usar tópico configurado en entorno (fallback a marketing.comisiones.eventos)
        await self._publicar(self._topic_comisiones, payload, 'ComisionCalculada')

    async def _publicar(self, topic: str, payload: Dict, etiqueta: str):
        try:
            if not self._client:
                await self.inicializar()
            prod = self._producer(topic)
            prod.send(json.dumps(payload).encode('utf-8'))
            logger.info(f"📡 [{etiqueta}] publicado en {topic}")
        except Exception as e:
            logger.error(f"❌ Error publicando {etiqueta}: {e}")
            raise

    async def cerrar(self):
        if self._client:
            self._client.close()
            logger.info('[Comisiones] Publisher cerrado')
