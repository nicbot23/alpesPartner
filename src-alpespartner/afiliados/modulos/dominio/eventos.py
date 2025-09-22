# afiliados/dominio/eventos.py
# Hoy los eventos de saga los emitimos en JSON para compatibilidad directa
# con campanias.SagaEventConsumer (que acepta plano). Si más tarde quieres Avro:

from pulsar.schema import Record, String


class EventoSagaAfiliados(Record):
    saga_id = String()
    paso = String()
    estado = String()  # "OK" | "FALLIDO"
    detalle = String() # JSON-encoded string; mantenlo si quieres estricto Avro

# from dataclasses import dataclass
# from afiliados.seedwork.dominio.eventos import EventoDominio

# @dataclass
# class AfiliadoCreado(EventoDominio):
#     id_afiliado: str
#     nombre: str
#     email: str
#     tipo_afiliado: str
#     nivel_comision: str
#     fecha_registro: str

# @dataclass
# class AfiliadoActualizado(EventoDominio):
#     id_afiliado: str
#     cambios: dict

# @dataclass
# class AfiliadoActivado(EventoDominio):
#     id_afiliado: str
#     fecha_activacion: str

# @dataclass
# class AfiliadoDesactivado(EventoDominio):
#     id_afiliado: str
#     razon: str
#     fecha_desactivacion: str
