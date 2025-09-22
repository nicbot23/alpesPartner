from pulsar.schema import *
from dataclasses import dataclass, field
from campanias.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion
from campanias.seedwork.infraestructura.utils import time_millis
from campanias.modulos.infraestructura.v1 import TipoCampaña
import uuid

class CampañaRegistrada(Record):
    id = String()
    nombre = String()
    descripcion = String()
    tipo_campaña = TipoCampaña
    afiliado_id = String()
    conversion_id = String()
    comision_id = String()
    fecha_creacion = Long()

class CampañaActualizada(Record):
    id = String()
    nombre = String()
    descripcion = String()
    tipo_campaña = TipoCampaña
    fecha_actualizacion = Long()

class CampañaEliminada(Record):
    id = String()
    fecha_eliminacion = Long()

class EventoCampaña(EventoIntegracion):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="EventoCampaña")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    campaña_registrada = CampañaRegistrada
    campaña_actualizada = CampañaActualizada
    campaña_eliminada = CampañaEliminada

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)