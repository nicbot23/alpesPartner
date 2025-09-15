from pulsar.schema import *
from alpespartner.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion
from alpespartner.seedwork.infraestructura.utils import unix_time_millis
import uuid

class ComisionCalculadaPayload(Record):
    commission_id = String()
    occurred_at = Long()

class ComisionAprobadaPayload(Record):
    commission_id = String()
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