# Import domain/event logic from campanias and saga orchestration from sagas

# Import saga logger and event classes from campanias and sagas
import logging
import traceback
import pulsar, _pulsar
import aiopulsar
import json
import os
import asyncio
from pulsar.schema import *
from campanias.seedwork.infraestructura import utils
from typing import Optional

from campanias.utils import broker_host, time_millis
from campanias.sagas.saga_logger_v2 import SagaLoggerV2 as SagaLogger, EstadoSaga, EstadoPaso
from campanias.modulos.infraestructura.schema.v1.comandos import ComandoLanzarCampaniaCompleta, ComandoCancelarSaga
#from campanias.modulos.infraestructura.schema.v1.eventos import EventoSagaCampania
from campanias.modulos.infraestructura.schema.v1.comandos import (
    ComandoLanzarCampaniaCompleta, ComandoCancelarSaga
)
from campanias.modulos.aplicacion.handlers import HandlerComandosBFF
from campanias.eventos import EventoSagaCampania
from .sagas.saga_logger_v2 import SagaLoggerV2
log = logging.getLogger(__name__)
#saga_logger = SagaLogger()

# Mapa de normalización a los estados que tu BD acepta
ESTADOS_PERMITIDOS = {
    "OK": "completado",
    "EXITO": "completado",
    "EXITO_OK": "completado",
    "FALLIDO": "fallido",
    "ERROR": "fallido",
    "FAIL": "fallido",
}

def _norm_estado(valor: str) -> str:
    v = (valor or "").strip()
    if not v:
        return "fallido"
    key = v.upper()
    if key in ESTADOS_PERMITIDOS:
        return ESTADOS_PERMITIDOS[key]
    # fallback razonable
    if "OK" in key or "EXITO" in key or "SUCCESS" in key:
        return "completado"
    if "FAIL" in key or "ERROR" in key or "FALL" in key:
        return "fallido"
    # si ya viene en vocabulario interno, respétalo
    v_lower = v.lower()
    if v_lower in {"enviado", "ejecutando", "completado", "fallido", "compensando", "compensada"}:
        return v_lower
    return "fallido"


async def suscribirse_a_topico(topico: str, suscripcion: str, schema: Record, tipo_consumidor:_pulsar.ConsumerType=_pulsar.ConsumerType.Shared):
	SagaLoggerV2.init_db() 
	try:
		async with aiopulsar.connect(f'pulsar://{utils.broker_host()}:6650') as cliente:
			async with cliente.subscribe(
				topic = topico,
				consumer_type=tipo_consumidor,
				subscription_name=suscripcion,
				schema=AvroSchema(schema)
			) as consumidor:
				while True:
					mensaje = await consumidor.receive()
					print(mensaje)
					datos = mensaje.value()
					try:
						print(f'Evento recibido: {datos}')
						# Procesar comando de lanzar campaña completa
						if isinstance(datos, ComandoLanzarCampaniaCompleta):
							print("Procesando comando para lanzar campaña completa...")
							await HandlerComandosBFF.handle_lanzar_campania_completa(datos)
						elif isinstance(datos, ComandoCancelarSaga):
							print("Procesando comando para cancelar saga...")
							await HandlerComandosBFF.handle_cancelar_saga(datos)
						await consumidor.acknowledge(mensaje)
					except Exception as e:
						logging.error(f'Error procesando mensaje: {e}')
						traceback.print_exc()
						await consumidor.negative_acknowledge(mensaje)
	except Exception as e:
		logging.error(f'ERROR: Suscribiendose al tópico de eventos! {e}')


async def suscribirse_eventos_saga(
    topico: str = "eventos-saga-campania",
    suscripcion: str = "campanias-saga-listener",
    pulsar_host: str = "broker",
    tipo_consumidor: _pulsar.ConsumerType = _pulsar.ConsumerType.Shared,
):
    url = f"pulsar://{pulsar_host}:6650"
    logger = SagaLoggerV2(storage_type=os.getenv("SAGAS_STORAGE_TYPE", "sqlite"))

    try:
        async with aiopulsar.connect(url) as cliente:
            async with cliente.subscribe(
                topic=topico,
                subscription_name=suscripcion,
                consumer_type=tipo_consumidor
            ) as consumidor:

                log.info("📥 Campañas escuchando %s", topico)

                while True:
                    msg = await consumidor.receive()
                    try:
                        evt = json.loads(msg.data().decode("utf-8"))
                        saga_id = evt.get("saga_id")
                        paso = evt.get("paso")
                        estado_in = evt.get("estado")
                        detalle = evt.get("detalle") or {}

                        estado_norm = _norm_estado(estado_in)

                        logger.actualizar_estado_paso(saga_id, paso, estado_norm, detalle)

                        # Si solo usas el paso de Afiliados y quieres cerrar la saga aquí:
                        if estado_norm == "completado":
                            logger.actualizar_estado_saga(saga_id, EstadoSaga.COMPLETADA, "Afiliados completado")
                        elif estado_norm == "fallido":
                            logger.actualizar_estado_saga(saga_id, EstadoSaga.FALLIDA, "Afiliados fallido")

                        await consumidor.acknowledge(msg)

                    except Exception as e:
                        log.error("Error procesando evento saga: %s", e)
                        traceback.print_exc()
                        await consumidor.negative_acknowledge(msg)

    except Exception as e:
        log.error("ERROR suscribiéndose a %s: %s", topico, e)



class SagaEventConsumer:
	"""
	Event consumer for campanias. Listens for saga events and updates saga status using SagaLogger.
	"""
	def __init__(self, saga_logger: Optional[SagaLogger] = None):
		self.saga_logger = saga_logger or SagaLogger()
	
	def listen(self, event) -> None:
		"""
		Recibe un JSON publicado por Afiliados en 'eventos-saga-campania':
		{
			"saga_id": "...",
			"paso": "solicitar_afiliados_elegibles",
			"estado": "OK" | "FALLIDO",
			"detalle": {...}
		}
		"""
		saga_id = event.get("saga_id")
		paso    = event.get("paso")
		estado  = event.get("estado")
		detalle = event.get("detalle")

		if not saga_id:
			logging.warning(f"Evento inválido (sin saga_id): {event}")
			return

		try:
			# Si Afiliados falla => marca paso FALLIDO y compensa/ciérralo como FALLIDA o COMPENSADA (según tu política)
			if str(estado).upper() in ("FALLIDO", "FAIL", "ERROR"):
				try:
					# si tu logger tiene esta firma, úsala; si no, quita la línea
					self.saga_logger.registrar_paso(
						saga_id=saga_id,
						paso_numero=1,
						nombre_paso=paso or "solicitar_afiliados_elegibles",
						servicio="afiliados",
						comando="comando-buscar-afiliados-elegibles",
						estado="FALLIDO",
						response_data=None,
						error_mensaje=(detalle or {}).get("motivo") if isinstance(detalle, dict) else str(detalle),
					)
				except Exception:
					pass
				self.saga_logger.actualizar_estado_saga(
					saga_id, "FALLIDA", error="Fallo en Afiliados"
				)
				logging.info(f"Saga {saga_id} marcada FALLIDA por Afiliados")
				return

			# Si Afiliados OK => cierra la saga (como en este escenario sólo hay este paso)
			if str(estado).upper() in ("OK", "COMPLETADO", "COMPLETADA"):
				try:
					self.saga_logger.registrar_paso(
						saga_id=saga_id,
						paso_numero=1,
						nombre_paso=paso or "solicitar_afiliados_elegibles",
						servicio="afiliados",
						comando="comando-buscar-afiliados-elegibles",
						estado="OK",
						response_data=detalle if isinstance(detalle, dict) else None,
					)
				except Exception:
					pass
				self.saga_logger.actualizar_estado_saga(
					saga_id, "COMPLETADA", resultado={"afiliados": detalle}
				)
				logging.info(f"Saga {saga_id} COMPLETADA por respuesta de Afiliados")
				return

			# Cualquier otro estado: deja trazabilidad del paso y mantén EN_PROGRESO
			try:
				self.saga_logger.registrar_paso(
					saga_id=saga_id,
					paso_numero=1,
					nombre_paso=paso or "solicitar_afiliados_elegibles",
					servicio="afiliados",
					comando="comando-buscar-afiliados-elegibles",
					estado=str(estado).upper() if estado else "PENDIENTE",
					response_data=detalle if isinstance(detalle, dict) else None,
				)
			except Exception:
				pass
			self.saga_logger.actualizar_estado_saga(saga_id, "EN_PROGRESO")
		except Exception as e:
			logging.error(f"Error procesando evento de saga: {e}")
			traceback.print_exc()



