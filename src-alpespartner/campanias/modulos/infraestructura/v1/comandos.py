from pulsar.schema import *
from dataclasses import dataclass, field
from campanias.seedwork.infraestructura.schema.v1.comandos import (ComandoIntegracion)
from campanias.seedwork.infraestructura.utils import time_millis
from campanias.modulos.infraestructura.v1 import TipoCampana
import uuid

class RegistrarCampaña(Record):
    nombre = String()
    descripcion = String()
    tipo_campaña = TipoCampana
    afiliado_id = String()
    conversion_id = String()
    comision_id = String()
    fecha_creacion = Long()

class ActualizarCampaña(Record):
    id = String()
    nombre = String()
    descripcion = String()
    tipo_campaña = TipoCampana
    fecha_actualizacion = Long()

class EliminarCampaña(Record):
    id = String()
    fecha_eliminacion = Long()

class ComandoRegistrarCampaña(ComandoIntegracion):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="RegistrarCampaña")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    data = RegistrarCampaña

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoActualizarCampaña(ComandoIntegracion):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ActualizarCampaña")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    data = ActualizarCampaña

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoEliminarCampaña(ComandoIntegracion):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="EliminarCampaña")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    data = EliminarCampaña

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoNotificarCampaña(ComandoIntegracion):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="NotificarCampaña")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    data = EliminarCampaña

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoFinalizarCampaña(ComandoIntegracion):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="FinalizarCampaña")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    data = EliminarCampaña

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)