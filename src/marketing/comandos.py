from uuid import uuid4
from datetime import datetime
from pulsar.schema import Record, String, Integer, Field, Float


class ComandoCrearCampana(Record):
    id = String()
    nombre = String()
    descripcion = String()
    tipo_campana = String()
    fecha_inicio = String()
    fecha_fin = String()
    meta_conversiones = Integer()
    presupuesto = Float()
    created_by = String()
    timestamp = Integer()


class ComandoActivarCampana(Record):
    id = String()
    campana_id = String()
    criterios_segmentacion = String()
    timestamp = Integer()


class ComandoDesactivarCampana(Record):
    id = String()
    campana_id = String()
    razon = String()
    timestamp = Integer()


class ComandoAsignarConversionACampana(Record):
    id = String()
    campana_id = String()
    conversion_id = String()
    user_id = String()
    valor_conversion = Float()
    timestamp = Integer()


class ComandoCalcularComision(Record):
    id = String()
    campana_id = String()
    afiliado_id = String()
    user_id = String()
    conversion_id = String()
    valor_conversion = Float()
    timestamp = Integer()


class ComandoEnviarNotificacion(Record):
    id = String()
    destinatario = String()
    tipo_notificacion = String()
    plantilla = String()
    datos = String()
    prioridad = String()
    timestamp = Integer()