# afiliados/modulos/infraestructura/schema/v1/comandos.py
from pulsar.schema import Record, String, Long


class ComandoBuscarAfiliadosElegibles(Record):
    campania_id = String()
    campania_nombre = String()
    tipo_campania = String()
    canal_publicidad = String()
    objetivo_campania = String()
    segmento_audiencia = String()
    fecha_inicio = Long()  # epoch ms
    fecha_fin = Long()     # epoch ms
    # Nota: saga_id viaja fuera del Avro en tu orquestador actual (parte del JSON).
    # Si más adelante lo incluyes formalmente, agrégalo aquí como String().
