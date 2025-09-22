from pulsar.schema import *
from campanias.utils import time_millis
import uuid
from typing import Optional

# ==========================================
# PAYLOADS DE EVENTOS DE OTROS MICROSERVICIOS
# ==========================================

class AfiliadoRegistradoPayload(Record):
    """Payload cuando se registra un nuevo afiliado"""
    afiliado_id = String()
    nombre = String()
    email = String()
    segmento = String()
    nivel = String()
    canales_disponibles = Array(String())
    fecha_registro = String()
    estado = String()

class AfiliadoActualizadoPayload(Record):
    """Payload cuando se actualiza un afiliado"""
    afiliado_id = String()
    campos_actualizados = Array(String())
    nuevo_segmento = String()
    nuevos_canales = Array(String())
    fecha_actualizacion = String()

class AfiliadoDesactivadoPayload(Record):
    """Payload cuando se desactiva un afiliado"""
    afiliado_id = String()
    razon_desactivacion = String()
    fecha_desactivacion = String()
    campanias_activas = Array(String())  # IDs de campanias donde participaba

class AfiliadosElegiblesEncontradosPayload(Record):
    """Payload con afiliados elegibles encontrados"""
    campania_id = String()
    afiliados_elegibles = Array(String())  # IDs de afiliados
    criterios_aplicados = Map(String())
    total_encontrados = Integer()
    fecha_busqueda = String()

class ComisionCalculadaPayload(Record):
    """Payload cuando se calcula una comisión"""
    comision_id = String()
    campania_id = String()
    afiliado_id = String()
    monto_comision = Double()
    porcentaje_aplicado = Double()
    conversion_id = String()
    fecha_calculo = String()

class ComisionPagadaPayload(Record):
    """Payload cuando se paga una comisión"""
    comision_id = String()
    campania_id = String()
    afiliado_id = String()
    monto_pagado = Double()
    metodo_pago = String()
    fecha_pago = String()

class EstructuraComisionConfiguradaPayload(Record):
    """Payload cuando se configura estructura de comisión para campaña"""
    campania_id = String()
    configuracion_id = String()
    porcentaje_base = Double()
    bonificaciones = Map(String())
    limite_maximo = Double()
    fecha_configuracion = String()

class ConversionRegistradaPayload(Record):
    """Payload cuando se registra una conversión"""
    conversion_id = String()
    campania_id = String()
    afiliado_id = String()
    usuario_id = String()
    valor_conversion = Double()
    tipo_conversion = String()
    canal = String()
    fecha_conversion = String()

class MetaAlcanzadaPayload(Record):
    """Payload cuando se alcanza una meta de campaña"""
    campania_id = String()
    tipo_meta = String()  # conversiones, ingresos, etc.
    valor_meta = Double()
    valor_actual = Double()
    porcentaje_cumplimiento = Double()
    fecha_alcance = String()

class TrackingInicializadoPayload(Record):
    """Payload cuando se inicializa tracking para campaña"""
    campania_id = String()
    tracking_id = String()
    metricas_configuradas = Array(String())
    metas_establecidas = Map(String())
    fecha_inicio = String()

class NotificacionEnviadaPayload(Record):
    """Payload cuando se envía una notificación"""
    notificacion_id = String()
    campania_id = String()
    afiliado_id = String()
    canal_envio = String()
    tipo_notificacion = String()
    estado_envio = String()
    fecha_envio = String()

class NotificacionFallidaPayload(Record):
    """Payload cuando falla una notificación"""
    notificacion_id = String()
    campania_id = String()
    afiliado_id = String()
    canal_envio = String()
    razon_fallo = String()
    reintento_programado = Boolean()
    fecha_fallo = String()

class NotificacionesPreparadasPayload(Record):
    """Payload cuando se preparan notificaciones para campaña"""
    campania_id = String()
    total_notificaciones = Integer()
    canales_configurados = Array(String())
    templates_preparados = Map(String())
    fecha_preparacion = String()

# ==========================================
# EVENTOS DE AFILIADOS
# ==========================================

class EventoAfiliado(Record):
    """Evento general del microservicio de afiliados"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="EventoAfiliado")
    datacontenttype = String()
    service_name = String(default="afiliados.alpespartner")
    
    # Diferentes tipos de eventos de afiliados
    afiliado_registrado = AfiliadoRegistradoPayload()
    afiliado_actualizado = AfiliadoActualizadoPayload()
    afiliado_desactivado = AfiliadoDesactivadoPayload()
    afiliados_elegibles_encontrados = AfiliadosElegiblesEncontradosPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# ==========================================
# EVENTOS DE COMISIONES
# ==========================================

class EventoComision(Record):
    """Evento general del microservicio de comisiones"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="EventoComision")
    datacontenttype = String()
    service_name = String(default="comisiones.alpespartner")
    
    # Diferentes tipos de eventos de comisiones
    comision_calculada = ComisionCalculadaPayload()
    comision_pagada = ComisionPagadaPayload()
    estructura_comision_configurada = EstructuraComisionConfiguradaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# ==========================================
# EVENTOS DE CONVERSIONES
# ==========================================

class EventoConversion(Record):
    """Evento general del microservicio de conversiones"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="EventoConversion")
    datacontenttype = String()
    service_name = String(default="conversiones.alpespartner")
    
    # Diferentes tipos de eventos de conversiones
    conversion_registrada = ConversionRegistradaPayload()
    meta_alcanzada = MetaAlcanzadaPayload()
    tracking_inicializado = TrackingInicializadoPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# ==========================================
# EVENTOS DE NOTIFICACIONES
# ==========================================

class EventoNotificacion(Record):
    """Evento general del microservicio de notificaciones"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="EventoNotificacion")
    datacontenttype = String()
    service_name = String(default="notificaciones.alpespartner")
    
    # Diferentes tipos de eventos de notificaciones
    notificacion_enviada = NotificacionEnviadaPayload()
    notificacion_fallida = NotificacionFallidaPayload()
    notificaciones_preparadas = NotificacionesPreparadasPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# ==========================================
# EVENTOS DE SAGA (COORDINACIÓN)
# ==========================================

class SagaCampaniaIniciadaPayload(Record):
    """Payload cuando se inicia una saga de campaña"""
    saga_id = String()
    campania_id = String()
    pasos_pendientes = Array(String())
    timestamp_inicio = String()

class SagaCampaniaCompletadaPayload(Record):
    """Payload cuando se completa una saga de campaña"""
    saga_id = String()
    campania_id = String()
    pasos_completados = Array(String())
    timestamp_completado = String()

class SagaCampaniaFallidaPayload(Record):
    """Payload cuando falla una saga de campaña"""
    saga_id = String()
    campania_id = String()
    paso_fallido = String()
    razon_fallo = String()
    compensacion_requerida = Boolean()
    timestamp_fallo = String()

class EventoSagaCampania(Record):
    """Evento de coordinación de saga de campaña"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="EventoSagaCampania")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    
    # Estados de saga
    saga_iniciada = SagaCampaniaIniciadaPayload()
    saga_completada = SagaCampaniaCompletadaPayload()
    saga_fallida = SagaCampaniaFallidaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# ==========================================
# EVENTOS DE COMPENSACIÓN (ROLLBACK)
# ==========================================

class CompensacionEjecutadaPayload(Record):
    """Payload cuando se ejecuta una compensación"""
    compensacion_id = String()
    saga_id = String()
    campania_id = String()
    accion_compensada = String()
    servicio_compensado = String()
    resultado = String()
    timestamp_compensacion = String()

class EventoCompensacion(Record):
    """Evento de compensación de saga"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="EventoCompensacion")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    
    compensacion_ejecutada = CompensacionEjecutadaPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)