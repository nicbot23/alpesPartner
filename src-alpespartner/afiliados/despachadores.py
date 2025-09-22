# afiliados/despachadores.py
import json
import logging
from typing import Any, Dict

import pulsar
from pulsar.schema import Record, AvroSchema

log = logging.getLogger(__name__)
from afiliados.utils import broker_host


class DespachadorAfiliados:
    """
    Productor Pulsar alineado al patrón de Campañas:
      - publica Avro si recibe un Record
      - si recibe dict -> publica JSON
    """
    def __init__(self, pulsar_url: str):
        self.url = pulsar_url or f"pulsar://{broker_host()}:6650"
        self.topico_eventos_saga = "eventos-saga-campania"
        self.log = logging.getLogger(__name__)

    # ----- util interna -----
    def _send_avro(self, cliente: pulsar.Client, topico: str, mensaje: Record):
        productor = cliente.create_producer(topico, schema=AvroSchema(mensaje.__class__))
        productor.send(mensaje)

    # def _send_json(self, cliente: pulsar.Client, topico: str, payload: Dict[str, Any]):
    #     productor = cliente.create_producer(topico)  # sin schema
    #     productor.send(json.dumps(payload).encode("utf-8"))

    def _send_json(self, topico: str, payload: dict):
        cli = pulsar.Client(self.url)
        try:
            prod = cli.create_producer(topico)  # SIN schema => bytes/JSON
            prod.send(json.dumps(payload).encode("utf-8"))
            self.log.info("📤 Publicado en %s", topico)
        finally:
            cli.close()

    def publicar_mensaje(self, mensaje: Any, topico: str):
        cliente = None
        try:
            cliente = pulsar.Client(self.url)  # <-- usar self.url
            if isinstance(mensaje, Record):
                self._send_avro(cliente, topico, mensaje)
            elif isinstance(mensaje, dict):
                # si prefieres unificar, puedes llamar _send_json(topico, mensaje) y cerrar aquí
                prod = cliente.create_producer(topico)
                prod.send(json.dumps(mensaje).encode("utf-8"))
            else:
                prod = cliente.create_producer(topico)
                prod.send(json.dumps({"payload": str(mensaje)}).encode("utf-8"))
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
        self._send_json(self.topico_eventos_saga, evento)

    async def publicar_evento_saga_fallido(self, saga_id: str, paso: str, motivo: str, detalle: Dict[str, Any] | None = None):
        evento = {
            "saga_id": saga_id,
            "paso": paso,
            "estado": "FALLIDO",
            "detalle": {"motivo": motivo, **(detalle or {})},
        }
        self._send_json(self.topico_eventos_saga, evento)
