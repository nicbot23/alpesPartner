from pulsar.schema import *
from campanias.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion
from campanias.seedwork.infraestructura.utils import time_millis
import uuid

class CampaniaCreadaPayload(Record):
    id_campania = String()
    nombre = String()
    descripcion = String()
    estado = String()
    tipo = String()
    canal_publicidad = String()
    objetivo = String()
    fecha_inicio = Long()
    fecha_fin = Long()
    fecha_creacion = Long()
    presupuesto = Double()
    moneda = String()
    codigo_campania = String()
    segmento_audiencia = String()
    activo = Boolean()

class EventoCampaniaCreada(EventoIntegracion):
    # NOTE La librería Record de Pulsar no es capaz de reconocer campos heredados, 
    # por lo que los mensajes al ser codificados pierden sus valores
    # Dupliqué el los cambios que ya se encuentran en la clase Mensaje
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = CampaniaCreadaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CampaniaActivadaPayload(Record):
    id_campania = String()
    fecha_activacion = Long()

class EventoCampaniaActivada(EventoIntegracion):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = CampaniaActivadaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class AfiliadoAgregadoPayload(Record):
    id_campania = String()
    id_afiliado = String()
    fecha_agregado = Long()

class EventoAfiliadoAgregado(EventoIntegracion):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = AfiliadoAgregadoPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)