from pulsar.schema import *
from alpespartner.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion
from alpespartner.seedwork.infraestructura.utils import time_millis
import uuid
from dataclasses import dataclass

# class ComissionCalculatedPayload(Record):
#     id_conversion_comission = String()
#     #id_cliente = String()
#     estado = String()
#     fecha_creacion = Long()

# class EventoComissionCalculated(EventoIntegracion):
#     # NOTE La librería Record de Pulsar no es capaz de reconocer campos heredados, 
#     # por lo que los mensajes al ser codificados pierden sus valores
#     # Dupliqué el los cambios que ya se encuentran en la clase Mensaje
#     id = String(default=str(uuid.uuid4()))
#     time = Long()
#     ingestion = Long(default=time_millis())
#     specversion = String()
#     type = String()
#     datacontenttype = String()
#     service_name = String()
#     data = ComissionCalculatedPayload()

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

@dataclass
class ComisionCalculadaPayload:
    commission_id: str
    occurred_at: int

@dataclass  
class ComisionAprobadaPayload:
    commission_id: str
    approved_at: int

@dataclass
class EventoComisionCalculada(EventoIntegracion):
    data: ComisionCalculadaPayload = None

@dataclass
class EventoComisionAprobada(EventoIntegracion):
    data: ComisionAprobadaPayload = None