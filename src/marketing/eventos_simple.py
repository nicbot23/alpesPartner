"""
Eventos simples para demostración de flujo completo
"""
from pulsar.schema import Record, String, Integer, Float, Long


class CampanaCreada(Record):
    id = String()
    campana_id = String()
    nombre = String()
    descripcion = String()
    tipo_campana = String()
    fecha_inicio = String()
    fecha_fin = String()
    estado = String()
    meta_conversiones = Integer()
    presupuesto = Float()
    created_by = String()
    timestamp = Long()


class ComisionCalculada(Record):
    id = String()
    campana_id = String()
    afiliado_id = String()
    user_id = String()
    conversion_id = String()
    monto_comision = Float()
    porcentaje_comision = Float()
    fecha_calculo = String()
    timestamp = Long()


class NotificacionSolicitada(Record):
    id = String()
    destinatario = String()
    tipo_notificacion = String()
    plantilla = String()
    datos = String()
    prioridad = String()
    timestamp = Long()