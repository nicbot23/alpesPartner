# afiliados/consumidores.py
import os
import json
import logging
import traceback
import aiopulsar
import _pulsar
from pulsar.schema import AvroSchema, Record, String, Long

from afiliados.despachadores import DespachadorAfiliados

log = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


# ======= Avro del comando (coincide con el que emite Campañas) =======
# Más adelante, cuando hagamos "aplicacion/comandos", moveremos esta clase allí:
# afiliados/modulos/infraestructura/schema/v1/comandos.py
class ComandoBuscarAfiliadosElegibles(Record):
    campania_id = String()
    campania_nombre = String()
    tipo_campania = String()
    canal_publicidad = String()
    objetivo_campania = String()
    segmento_audiencia = String()
    fecha_inicio = Long()  # epoch ms
    fecha_fin = Long()     # epoch ms
    # En el orquestador actual, se incluye saga_id en el payload de entrada
    # (visto en /progreso). Si no viniera, usaremos campania_id como fallback.
    # Para simplicidad no lo declaramos aquí (puede llegar por JSON extra).


async def suscribirse_a_topico(
    topico: str,
    suscripcion: str,
    pulsar_host: str = "broker",
    tipo_consumidor: _pulsar.ConsumerType = _pulsar.ConsumerType.Shared,
):
    """
    Consumidor principal de Afiliados:
      - Escucha 'comando-buscar-afiliados-elegibles'
      - Ejecuta una lógica mínima (dummy) de búsqueda
      - Publica evento de saga (OK/FALLIDO) a 'eventos-saga-campania'
    """
    url = f"pulsar://{pulsar_host}:6650"
    desp = DespachadorAfiliados(pulsar_url=url)

    # Permite forzar fallo para probar compensación
    force_fail = os.getenv("AFILIADOS_FORCE_FAIL", "false").lower() in ("1", "true", "yes")

    try:
        async with aiopulsar.connect(url) as cliente:
            # Intentamos Avro primero (patrón Campañas). Si no cuadra, caemos a bytes/JSON.
            try:
                consumidor = await cliente.subscribe(
                    topic=topico,
                    subscription_name=suscripcion,
                    consumer_type=tipo_consumidor,
                    schema=AvroSchema(ComandoBuscarAfiliadosElegibles),
                )
                avro = True
                log.info("👂 Afiliados suscrito con Avro a %s", topico)
            except Exception:
                consumidor = await cliente.subscribe(
                    topic=topico,
                    subscription_name=suscripcion,
                    consumer_type=tipo_consumidor,
                )
                avro = False
                log.warning("👂 Afiliados suscrito en %s sin Avro (fallback JSON).", topico)

            while True:
                msg = await consumidor.receive()
                try:
                    if avro:
                        m = msg.value()
                        data = {
                            "campania_id": m.campania_id,
                            "campania_nombre": m.campania_nombre,
                            "tipo_campania": m.tipo_campania,
                            "canal_publicidad": m.canal_publicidad,
                            "objetivo_campania": m.objetivo_campania,
                            "segmento_audiencia": m.segmento_audiencia,
                            "fecha_inicio": m.fecha_inicio,
                            "fecha_fin": m.fecha_fin,
                        }
                    else:
                        body = msg.data().decode("utf-8")
                        data = json.loads(body)

                    # Normalizamos saga_id (el despachador de Campañas lo manda en el payload)
                    saga_id = str(data.get("saga_id") or data.get("campania_id"))
                    if not saga_id:
                        log.error("Mensaje sin saga_id/campania_id: %s", data)
                        await consumidor.acknowledge(msg)
                        continue

                    # ====== Lógica mínima de búsqueda (dummy) ======
                    seg = (data.get("segmento_audiencia") or "general").lower()
                    # Regla simple: si AFILIADOS_FORCE_FAIL=true o segmento 'vacío' => FALLIDO
                    if force_fail or seg in {"ninguno", "vacio", "vacío"}:
                        detalle = {"criterios": seg, "encontrados": 0}
                        await desp.publicar_evento_saga_fallido(
                            saga_id=saga_id,
                            paso="solicitar_afiliados_elegibles",
                            motivo="No hay afiliados elegibles",
                            detalle=detalle,
                        )
                    else:
                        # Simulamos afiliados elegibles
                        base = ["af-001", "af-002", "af-003", "af-004", "af-005"]
                        detalle = {
                            "criterios": seg,
                            "encontrados": len(base),
                            "afiliados": base,
                        }
                        await desp.publicar_evento_saga_ok(
                            saga_id=saga_id,
                            paso="solicitar_afiliados_elegibles",
                            detalle=detalle,
                        )

                    await consumidor.acknowledge(msg)

                except Exception as e:
                    log.error("Error procesando mensaje afiliados: %s", e)
                    traceback.print_exc()
                    await consumidor.negative_acknowledge(msg)

    except Exception as e:
        log.error("ERROR suscribiéndose a %s: %s", topico, e)
