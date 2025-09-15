from pulsar.schema import *
from alpespartner.seedwork.infraestructura.schema.v2.eventos import EventoIntegracion
from alpespartner.seedwork.infraestructura.utils import unix_time_millis
import uuid

from pulsar.schema import Record
from alpespartner.seedwork.infraestructura.schema.v1.mensajes import Mensaje

class ComisionCalculadaPayload(Record):
    commission_id = str()
    conversion_id = str()
    affiliate_id = str()
    campaign_id = str()
    gross_amount = str()  # JSON serialized amount object
    percentage = float()
    net_amount = str()   # JSON serialized amount object
    occurred_at = int()

class ComisionAprobadaPayload(Record):
    commission_id = str()
    conversion_id = str()
    affiliate_id = str()
    campaign_id = str()
    approved_at = int()

class EventoComisionCalculada(Mensaje):
    data: ComisionCalculadaPayload = None

class EventoComisionAprobada(Mensaje):
    data: ComisionAprobadaPayload = None

class ComisionAprobadaPayload(Record):
    commission_id = String()
    conversion_id = String()
    affiliate_id = String()
    campaign_id = String()
    approved_at = Long()

class EventoComisionCalculada(EventoIntegracion):
    # NOTE La librería Record de Pulsar no es capaz de reconocer campos heredados, 
    # por lo que los mensajes al ser codificados pierden sus valores
    # Dupliqué los cambios que ya se encuentran en la clase Mensaje
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=unix_time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = ComisionCalculadaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class EventoComisionAprobada(EventoIntegracion):
    # NOTE La librería Record de Pulsar no es capaz de reconocer campos heredados, 
    # por lo que los mensajes al ser codificados pierden sus valores
    # Dupliqué los cambios que ya se encuentran en la clase Mensaje
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=unix_time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = ComisionAprobadaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
