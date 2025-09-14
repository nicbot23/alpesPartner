from uuid import uuid4
from datetime import datetime
from pulsar.schema import Record, String, Integer, Field, Float


class CampanaCreada(Record):
    id = String()
    nombre = String()
    descripcion = String()
    tipo_campana = String()
    fecha_inicio = String()
    fecha_fin = String()
    estado = String()
    meta_conversiones = Integer()
    presupuesto = Float()
    created_by = String()
    timestamp = Integer()


class CampanaActivada(Record):
    id = String()
    campana_id = String()
    fecha_activacion = String()
    criterios_segmentacion = String()
    timestamp = Integer()


class CampanaDesactivada(Record):
    id = String()
    campana_id = String()
    razon = String()
    timestamp = Integer()


class ConversionAsignadaACampana(Record):
    id = String()
    campana_id = String()
    conversion_id = String()
    user_id = String()
    valor_conversion = Float()
    timestamp = Integer()


class ComisionCalculada(Record):
    id = String()
    campana_id = String()
    afiliado_id = String()
    user_id = String()
    conversion_id = String()
    monto_comision = Float()
    porcentaje_comision = Float()
    fecha_calculo = String()
    timestamp = Integer()


class NotificacionSolicitada(Record):
    id = String()
    destinatario = String()
    tipo_notificacion = String()  # email, sms, push
    plantilla = String()
    datos = String()  # JSON con datos para la plantilla
    prioridad = String()  # alta, media, baja
    timestamp = Integer()