from uuid import uuid4
from datetime import datetime
from pulsar.schema import Record, String, Integer, Field


class ComandoRegistrarAfiliado(Record):
    id = String()
    user_id = String()
    email = String()
    nombre = String()
    apellido = String()
    numero_documento = String()
    tipo_documento = String()
    telefono = String()
    timestamp = Integer()


class ComandoActualizarAfiliado(Record):
    id = String()
    user_id = String()
    email = String()
    nombre = String()
    apellido = String()
    numero_documento = String()
    tipo_documento = String()
    telefono = String()
    timestamp = Integer()


class ComandoDesactivarAfiliado(Record):
    id = String()
    user_id = String()
    razon = String()
    timestamp = Integer()


class ComandoValidarAfiliado(Record):
    id = String()
    user_id = String()
    timestamp = Integer()