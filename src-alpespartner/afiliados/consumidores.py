# afiliados/consumidores.py
import os
import json
import logging
import traceback
import aiopulsar
import _pulsar
from pulsar.schema import AvroSchema, Record, String, Long, Map

from afiliados.modulos.aplicacion.handlers import HandlerComandosAfiliados
from afiliados.despachadores import DespachadorAfiliados

log = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

# ===============================
# Avro schemas (compatibles con el tópico real)
#   Logs del broker mostraron un "envelope" CloudEvents-like:
#   ComandoBuscarAfiliadosElegibles { id, time, ingestion, specversion, type,
#     datacontenttype, service_name, data{...payload...} }
# ===============================

class BuscarAfiliadosElegiblesPayload(Record):
    campania_id = String()          # nullable en el writer -> union(null,string)
    campania_nombre = String()
    tipo_campania = String()
    canal_publicidad = String()
    objetivo_campania = String()
    segmento_audiencia = String()
    # En el writer aparecían como string (no epoch-ms)
    fecha_inicio = String()
    fecha_fin = String()
    criterios_elegibilidad = Map(String())


class ComandoBuscarAfiliadosElegibles(Record):
    # Campos del “sobre” que reportó el broker al validar el schema
    id = String()
    time = Long()
    ingestion = Long()
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = BuscarAfiliadosElegiblesPayload()


def _extraer_payload(cmd: ComandoBuscarAfiliadosElegibles) -> dict:
    """Normaliza el payload a un dict Python desde el envelope."""
    d = getattr(cmd, "data", None)
    if d is None:
        return {}
    return {
        "campania_id": getattr(d, "campania_id", None),
        "campania_nombre": getattr(d, "campania_nombre", None),
        "tipo_campania": getattr(d, "tipo_campania", None),
        "canal_publicidad": getattr(d, "canal_publicidad", None),
        "objetivo_campania": getattr(d, "objetivo_campania", None),
        "segmento_audiencia": getattr(d, "segmento_audiencia", None),
        "fecha_inicio": getattr(d, "fecha_inicio", None),
        "fecha_fin": getattr(d, "fecha_fin", None),
        "criterios_elegibilidad": dict(getattr(d, "criterios_elegibilidad", {}) or {}),
    }


async def suscribirse_a_topico(
    topico: str,
    suscripcion: str,
    pulsar_host: str = "broker",
    tipo_consumidor: _pulsar.ConsumerType = _pulsar.ConsumerType.Shared,
):
    """
    Consumidor principal de Afiliados:
      - Escucha 'comando-buscar-afiliados-elegibles' con el envelope real del tópico
      - Ejecuta lógica dummy de “búsqueda”
      - Publica evento OK/FALLIDO a 'eventos-saga-campania'
    """
    url = f"pulsar://{pulsar_host}:6650"
    desp = DespachadorAfiliados(pulsar_url=url)
    handler = HandlerComandosAfiliados(pulsar_url=url)

    force_fail = os.getenv("AFILIADOS_FORCE_FAIL", "false").lower() in ("1", "true", "yes")

    try:
        async with aiopulsar.connect(url) as cliente:
            async with cliente.subscribe(
                topic=topico,
                subscription_name=suscripcion,
                consumer_type=tipo_consumidor,
                schema=AvroSchema(ComandoBuscarAfiliadosElegibles),
            ) as consumidor:
                log.info("👂 Afiliados suscrito (Avro con envoltura) a %s", topico)

                while True:
                    msg = await consumidor.receive()
                    try:
                        cmd = msg.value()
                        data = _extraer_payload(cmd)

                        # Validación mínima
                        saga_id = data.get("campania_id")
                        if not saga_id:
                            log.error("Mensaje sin campania_id (saga_id): %s", data)
                            await consumidor.acknowledge(msg)
                            continue

                        # Efecto interno (dummy / side effects)
                        await handler.handle_buscar_afiliados_elegibles(data)

                        # Lógica dummy para éxito/fallo
                        seg = (data.get("segmento_audiencia") or "general").lower()
                        if force_fail or seg in {"ninguno", "vacio", "vacío"}:
                            detalle = {"criterios": seg, "encontrados": 0}
                            await desp.publicar_evento_saga_fallido(
                                saga_id=saga_id,
                                paso="solicitar_afiliados_elegibles",
                                motivo="No hay afiliados elegibles",
                                detalle=detalle,
                            )
                        else:
                            afiliados = ["af-001", "af-002", "af-003", "af-004", "af-005"]
                            detalle = {
                                "criterios": seg,
                                "encontrados": len(afiliados),
                                "afiliados": afiliados,
                            }
                            await desp.publicar_evento_saga_ok(
                                saga_id=saga_id,
                                paso="solicitar_afiliados_elegibles",
                                detalle=detalle,
                            )

                        await consumidor.acknowledge(msg)

                    except Exception as e:
                        log.error("Error procesando mensaje de afiliados: %s", e)
                        traceback.print_exc()
                        await consumidor.negative_acknowledge(msg)

    except Exception as e:
        log.error("ERROR suscribiéndose a %s: %s", topico, e)
