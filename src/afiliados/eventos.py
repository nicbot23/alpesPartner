from uuid import uuid4
from datetime import datetime
from pulsar.schema import Record, String, Integer, Field


class AfiliadoRegistrado(Record):
    id = String()
    user_id = String() 
    email = String()
    nombre = String()
    apellido = String()
    numero_documento = String()
    tipo_documento = String()
    telefono = String()
    fecha_afiliacion = String()
    estado = String()
    timestamp = Integer()


class AfiliadoActualizado(Record):
    id = String()
    user_id = String()
    email = String() 
    nombre = String()
    apellido = String()
    numero_documento = String()
    tipo_documento = String()
    telefono = String()
    estado = String()
    timestamp = Integer()


class AfiliadoDesactivado(Record):
    id = String()
    user_id = String()
    razon = String()
    timestamp = Integer()


class AfiliadoValidado(Record):
    id = String()
    user_id = String()
    estado_validacion = String()
    timestamp = Integer()