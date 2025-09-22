from pulsar.schema import *
from campanias.seedwork.infraestructura.schema.v1.mensajes import Mensaje
from campanias.seedwork.infraestructura.utils import time_millis
import uuid

class CrearCampaniaPayload(Record):
    nombre = String()
    descripcion = String()
    tipo = String()
    canal_publicidad = String()
    objetivo = String()
    fecha_inicio = Long()
    fecha_fin = Long()
    presupuesto = Double()
    moneda = String()
    segmento_audiencia = String()

class ComandoCrearCampania(Mensaje):
    # NOTE La librería Record de Pulsar no es capaz de reconocer campos heredados, 
    # por lo que los mensajes al ser codificados pierden sus valores
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = CrearCampaniaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ActivarCampaniaPayload(Record):
    id_campania = String()

class ComandoActivarCampania(Mensaje):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = ActivarCampaniaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class AgregarAfiliadoPayload(Record):
    id_campania = String()
    id_afiliado = String()

class ComandoAgregarAfiliado(Mensaje):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = AgregarAfiliadoPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class LanzarCampaniaCompletaPayload(Record):
    nombre = String()
    descripcion = String()
    tipo = String()
    canal_publicidad = String()
    objetivo = String()
    fecha_inicio = Long()
    fecha_fin = Long()
    presupuesto = Double()
    moneda = String()
    segmento_audiencia = String()

class ComandoLanzarCampaniaCompleta(Mensaje):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = LanzarCampaniaCompletaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CancelarSagaPayload(Record):
    saga_id = String()
    razon = String()

class ComandoCancelarSaga(Mensaje):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = CancelarSagaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)