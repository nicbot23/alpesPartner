# afiliados/despachadores.py
import json
import logging
from typing import Any, Dict

import pulsar
from pulsar.schema import Record, AvroSchema

log = logging.getLogger(__name__)


class DespachadorAfiliados:
    """
    Productor Pulsar alineado al patrón de Campañas:
      - publica Avro si recibe un Record
      - si recibe dict -> publica JSON
    """
    def __init__(self, pulsar_url: str):
        self.pulsar_url = pulsar_url
        self.topico_eventos_saga = "eventos-saga-campania"

    # ----- util interna -----
    def _send_avro(self, cliente: pulsar.Client, topico: str, mensaje: Record):
        productor = cliente.create_producer(topico, schema=AvroSchema(mensaje.__class__))
        productor.send(mensaje)

    def _send_json(self, cliente: pulsar.Client, topico: str, payload: Dict[str, Any]):
        productor = cliente.create_producer(topico)  # sin schema
        productor.send(json.dumps(payload).encode("utf-8"))

    def publicar_mensaje(self, mensaje: Any, topico: str):
        cliente = None
        try:
            cliente = pulsar.Client(self.pulsar_url)
            if isinstance(mensaje, Record):
                self._send_avro(cliente, topico, mensaje)
            elif isinstance(mensaje, dict):
                self._send_json(cliente, topico, mensaje)
            else:
                # Fallback prudente
                self._send_json(cliente, topico, {"payload": str(mensaje)})
            log.info("📤 Publicado en %s", topico)
        finally:
            if cliente:
                cliente.close()

    # ----- API de eventos de SAGA (JSON simple por compatibilidad) -----
    async def publicar_evento_saga_ok(self, saga_id: str, paso: str, detalle: Dict[str, Any]):
        evento = {
            "saga_id": saga_id,
            "paso": paso,
            "estado": "OK",
            "detalle": detalle,
        }
        self.publicar_mensaje(evento, self.topico_eventos_saga)

    async def publicar_evento_saga_fallido(self, saga_id: str, paso: str, motivo: str, detalle: Dict[str, Any] | None = None):
        evento = {
            "saga_id": saga_id,
            "paso": paso,
            "estado": "FALLIDO",
            "detalle": {"motivo": motivo, **(detalle or {})},
        }
        self.publicar_mensaje(evento, self.topico_eventos_saga)
