from pulsar.schema import *
from campanias.utils import time_millis
import uuid
from typing import Dict, Any, Optional

# ==========================================
# PAYLOADS DE COMANDOS EXTERNOS
# ==========================================

class BuscarAfiliadosElegiblesPayload(Record):
    """Payload para solicitar búsqueda de afiliados elegibles"""
    campania_id = String()
    campania_nombre = String()
    tipo_campania = String()
    canal_publicidad = String()
    objetivo_campania = String()
    segmento_audiencia = String()
    fecha_inicio = String()
    fecha_fin = String()
    criterios_elegibilidad = Map(String())  # Criterios específicos de elegibilidad

class ConfigurarComisionCampaniaPayload(Record):
    """Payload para configurar comisiones de campaña"""
    campania_id = String()
    campania_nombre = String()
    tipo_campania = String()
    presupuesto_total = Double()
    moneda = String()
    estructura_comisiones = Map(String())  # Estructura de comisiones como dict
    fecha_inicio = String()
    fecha_fin = String()

class InicializarTrackingCampaniaPayload(Record):
    """Payload para inicializar tracking de conversiones"""
    campania_id = String()
    campania_nombre = String()
    objetivo_campania = String()
    canal_publicidad = String()
    metricas_objetivo = Array(String())    # Lista de métricas a trackear
    metas_numericas = Map(String())        # Metas numéricas como dict
    fecha_inicio = String()
    fecha_fin = String()

class PrepararNotificacionesCampaniaPayload(Record):
    """Payload para preparar notificaciones de campaña"""
    campania_id = String()
    campania_nombre = String()
    canal_publicidad = String()
    templates_notificacion = Map(String())  # Templates por canal
    contenido_personalizado = Map(String()) # Contenido personalizado
    criterios_envio = Map(String())         # Criterios de envío

class CrearCampaniaExternaPayload(Record):
    """Payload para crear campaña desde otro microservicio"""
    nombre = String()
    descripcion = String()
    tipo_campana = String()
    canal_publicidad = String()
    objetivo_campana = String()
    fecha_inicio = String()
    fecha_fin = String()
    presupuesto = Double()
    moneda = String()
    codigo_campana = String()
    segmento_audiencia = String()
    solicitar_afiliados = Boolean(default=True)
    configurar_comisiones = Boolean(default=True)
    iniciar_tracking = Boolean(default=True)

class ActivarCampaniaExternaPayload(Record):
    """Payload para activar campaña desde otro microservicio"""
    campania_id = String()
    fecha_activacion = String()
    notificar_afiliados = Boolean(default=True)

class AgregarAfiliadoExternoPayload(Record):
    """Payload para agregar afiliado desde otro microservicio"""
    campania_id = String()
    afiliado_id = String()
    configuracion_afiliado = Map(String())
    comision_aplicable = Double()
    fecha_asignacion = String()

# ==========================================
# COMANDOS EXTERNOS (que otros microservicios envían a campanias)
# ==========================================

class ComandoBuscarAfiliadosElegibles(Record):
    """Comando para que AFILIADOS busque afiliados elegibles para una campaña"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoBuscarAfiliadosElegibles")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    data = BuscarAfiliadosElegiblesPayload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoConfigurarComisionCampania(Record):
    """Comando para que COMISIONES configure la estructura de pagos"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoConfigurarComisionCampania")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    data = ConfigurarComisionCampaniaPayload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoInicializarTrackingCampania(Record):
    """Comando para que CONVERSIONES inicialice tracking de métricas"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoInicializarTrackingCampania")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    data = InicializarTrackingCampaniaPayload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoPrepararNotificacionesCampania(Record):
    """Comando para que NOTIFICACIONES prepare las comunicaciones"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoPrepararNotificacionesCampania")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    data = PrepararNotificacionesCampaniaPayload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# ==========================================
# COMANDOS QUE RECIBIMOS (otros microservicios → campanias)
# ==========================================

class ComandoCrearCampania(Record):
    """Comando externo para crear una campaña (ej: desde BFF)"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoCrearCampania")
    datacontenttype = String()
    service_name = String(default="bff.alpespartner")  # Viene del BFF
    data = CrearCampaniaExternaPayload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoActivarCampania(Record):
    """Comando externo para activar una campaña"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoActivarCampania")
    datacontenttype = String()
    service_name = String(default="external.alpespartner")
    data = ActivarCampaniaExternaPayload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoAgregarAfiliado(Record):
    """Comando externo para agregar afiliado a campaña"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoAgregarAfiliado")
    datacontenttype = String()
    service_name = String(default="afiliados.alpespartner")
    data = AgregarAfiliadoExternoPayload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# ==========================================
# COMANDOS DE COMPENSACIÓN (SAGA ROLLBACK)
# ==========================================

class ComandoCancelarBusquedaAfiliados(Record):
    """Comando de compensación para cancelar búsqueda de afiliados"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoCancelarBusquedaAfiliados")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    campania_id = String()
    razon_cancelacion = String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoDesconfigurarComisiones(Record):
    """Comando de compensación para desconfigurar comisiones"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoDesconfigurarComisiones")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    campania_id = String()
    razon_cancelacion = String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoDetenerTracking(Record):
    """Comando de compensación para detener tracking"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoDetenerTracking")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    campania_id = String()
    razon_cancelacion = String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComandoCancelarNotificaciones(Record):
    """Comando de compensación para cancelar notificaciones"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoCancelarNotificaciones")
    datacontenttype = String()
    service_name = String(default="campanias.alpespartner")
    campania_id = String()
    razon_cancelacion = String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# ==========================================
# NUEVOS COMANDOS DESDE BFF (SAGA COMPLETA)
# ==========================================

class LanzarCampaniaCompletaPayload(Record):
    """Payload para lanzar campaña completa desde BFF"""
    comando_id = String()
    campania_nombre = String()
    tipo_campania = String()
    descripcion = String()
    canal_publicidad = String()
    objetivo_campania = String()
    segmento_audiencia = String()
    fecha_inicio = String()
    fecha_fin = String()
    presupuesto = Double()
    moneda = String()
    
    # Configuración de saga
    opciones_saga = Map(String())
    criterios_elegibilidad = Map(String())
    configuracion_comisiones = Map(String())
    preferencias_notificacion = Map(String())
    
    # Metadatos
    origen = String()
    version_bff = String()
    usuario_solicitante = String()


class ComandoLanzarCampaniaCompleta(Record):
    """
    Comando principal del BFF para lanzar una campaña completa.
    Inicia la saga completa de creación, configuración y activación.
    """
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoLanzarCampaniaCompleta")
    datacontenttype = String()
    service_name = String(default="bff.alpespartner")
    data = LanzarCampaniaCompletaPayload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CancelarSagaPayload(Record):
    """Payload para cancelar saga en progreso"""
    comando_id = String()
    saga_id = String()
    razon_cancelacion = String()
    forzar_cancelacion = Boolean()
    origen = String()


class ComandoCancelarSaga(Record):
    """Comando del BFF para cancelar una saga en progreso"""
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v1")
    type = String(default="ComandoCancelarSaga")
    datacontenttype = String()
    service_name = String(default="bff.alpespartner")
    data = CancelarSagaPayload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)