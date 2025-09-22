# Import domain/event logic from campanias and saga orchestration from sagas

# Import saga logger and event classes from campanias and sagas
import logging
import traceback
import pulsar, _pulsar
import aiopulsar
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
#saga_logger = SagaLogger()

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

class SagaEventConsumer:
	"""
	Event consumer for campanias. Listens for saga events and updates saga status using SagaLogger.
	"""
	def __init__(self, saga_logger: Optional[SagaLogger] = None):
		self.saga_logger = saga_logger or SagaLogger()
	


	def listen(self, event)-> None:
		"""
		Main entrypoint for event consumption. Receives an EventoSagaCampania and processes it.
		"""
		saga_id = None
		paso = None
		estado = None
		detalle = None

		try:
			if getattr(event, "saga_completada", None):
				saga_id = event.saga_completada.saga_id
				estado = EstadoSaga.COMPLETADA
			elif getattr(event, "saga_fallida", None):
				saga_id = event.saga_fallida.saga_id
				paso = event.saga_fallida.paso_fallido or "desconocido"
				estado = EstadoPaso.FALLIDO
				detalle = {"error": getattr(event.saga_fallida, "motivo", "Fallo en saga")}
		except Exception:
			pass

# 2) Estilo plano (fallback)
		if not saga_id:
			saga_id = getattr(event, "saga_id", None)
			paso = paso or getattr(event, "paso", None)
			estado = estado or getattr(event, "estado", None)
			detalle = detalle or getattr(event, "detalle", None)

		if not saga_id:
			logging.warning(f"Evento inválido (sin saga_id): {event}")
			return

		try:
			if estado == EstadoSaga.COMPLETADA:
				self.saga_logger.marcar_completada(saga_id)
				logging.info(f"Saga {saga_id} COMPLETADA")
				return

			if estado in (EstadoPaso.FALLIDO, "FALLIDO") or (isinstance(estado, str) and "FALL" in estado.upper()):
				# marca paso como fallido y compensa saga
				if paso:
					self.saga_logger.actualizar_estado_paso(saga_id, paso, EstadoPaso.FALLIDO, detalle)
				self.saga_logger.compensar_saga(saga_id, paso_id=paso, razon="Fallo en paso")
				logging.info(f"Saga {saga_id} COMPENSADA (fallo en paso {paso})")
				return

			# si llega un evento de progreso normal
			if paso and estado:
				self.saga_logger.actualizar_estado_paso(saga_id, paso, estado, detalle)
				# si con este evento queda completa, márcalo explícitamente
				if self.saga_logger.saga_completada(saga_id):
					self.saga_logger.marcar_completada(saga_id)
					logging.info(f"Saga {saga_id} COMPLETADA")
		except Exception as e:
			logging.error(f"Error procesando evento de saga: {e}")
			traceback.print_exc()

		# Detect event type and extract info
		# if event.saga_completada:
		# 	saga_id = event.saga_completada.saga_id
		# 	estado = 'COMPLETADA'
		# elif event.saga_fallida:
		# 	saga_id = event.saga_fallida.saga_id
		# 	estado = 'FALLIDA'
		# 	paso = event.saga_fallida.paso_fallido
		# else:
		# 	print(f"Evento no reconocido: {event}")
		# 	return
		# self.handle_event(saga_id, paso, estado)

# 	def handle_event(self, saga_id, paso, estado):
# 		"""
# 		Updates saga status and triggers closure/compensation if needed.
# 		"""
# 		try:
# 			if estado == 'COMPLETADA':
# 				self.saga_logger.marcar_completada(saga_id)
# 				print(f"Saga {saga_id} COMPLETADA")
# 			elif estado == 'FALLIDA':
# 				self.saga_logger.compensar_saga(saga_id, paso_id=paso)
# 				print(f"Saga {saga_id} COMPENSADA (fallo en paso {paso})")
# 		except Exception as e:
# 			print(f"Error procesando evento saga: {e}")

# class SagaEventConsumer:
# 	"""
# 	Professional event consumer for campanias.
# 	Listens for confirmation/failure events and updates saga status using saga_logger_v2.
# 	"""
# 	def __init__(self, saga_logger=None):
# 		self.saga_logger = saga_logger or SagaLogger()

# 	def listen(self, event):
# 		"""
# 		Main entrypoint for event consumption. Receives an event and processes it.
# 		"""
# 		saga_id = getattr(event, 'saga_id', None)
# 		paso = getattr(event, 'paso', None)
# 		estado = getattr(event, 'estado', None)
# 		if not saga_id or not paso or not estado:
# 			print(f"Evento inválido: {event}")
# 			return
# 		self.handle_event(saga_id, paso, estado)

# 	def handle_event(self, saga_id, paso, estado):
# 		"""
# 		Updates saga step status and triggers closure/compensation if needed.
# 		"""
# 		try:
# 			self.saga_logger.actualizar_estado_paso(saga_id, paso, estado)
# 			if self.saga_logger.saga_completada(saga_id):
# 				self.saga_logger.marcar_completada(saga_id)
# 				print(f"Saga {saga_id} COMPLETADA")
# 			elif estado == 'FALLIDO' or "FALL" in estado:
# 				self.saga_logger.compensar_saga(saga_id)
# 				print(f"Saga {saga_id} COMPENSADA")
# 		except Exception as e:
# 			print(f"Error procesando evento saga: {e}")

