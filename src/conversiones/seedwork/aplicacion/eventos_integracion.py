"""
Eventos de integración para comunicación entre microservicios
Conversiones ↔ Marketing ↔ Afiliados
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import uuid
from enum import Enum

# Base para eventos de integración
@dataclass(frozen=True)
class EventoIntegracion(ABC):
    """
    Base abstracta para eventos de integración entre microservicios
    Principio de Responsabilidad Única - comunicación entre bounded contexts
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    microservicio_origen: str = "conversiones"
    microservicio_destino: str = ""
    version: str = "1.0"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadatos: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.correlation_id:
            object.__setattr__(self, 'correlation_id', self.id)

# Tipos de integración
class TipoIntegracion(Enum):
    NOTIFICACION = "notificacion"  # Informar de algo que pasó
    COMANDO = "comando"           # Solicitar que se haga algo
    CONSULTA = "consulta"         # Solicitar información
    RESPUESTA = "respuesta"       # Responder a consulta

# Eventos hacia Marketing
@dataclass(frozen=True)
class ConversionDetectadaIntegracion(EventoIntegracion):
    """
    Evento: Notificar a Marketing que se detectó una conversión
    Para análisis de campañas y optimización
    """
    conversion_id: str = ""
    campana_id: str = ""
    afiliado_id: str = ""
    usuario_id: str = ""
    tipo_conversion: str = ""
    valor_conversion: float = 0.0
    moneda: str = "USD"
    fecha_conversion: datetime = field(default_factory=datetime.now)
    fuente: str = ""
    canal: str = ""
    datos_tracking: Dict[str, Any] = field(default_factory=dict)
    
    # Datos específicos para Marketing
    utm_campaign: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None
    
    # Métricas adicionales
    tiempo_desde_click_ms: Optional[int] = None
    dispositivo: Optional[str] = None
    navegador: Optional[str] = None
    pais: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_destino', 'marketing')

@dataclass(frozen=True)
class ConversionCompletadaIntegracion(EventoIntegracion):
    """
    Evento: Notificar a Marketing que una conversión fue completada
    Para actualizaciones de métricas y ROI
    """
    conversion_id: str = ""
    campana_id: str = ""
    afiliado_id: str = ""
    valor_final: float = 0.0
    moneda: str = "USD"
    fecha_completado: datetime = field(default_factory=datetime.now)
    tiempo_total_procesamiento_ms: int = 0
    
    # Métricas de rendimiento para Marketing
    tasa_conversion: Optional[float] = None
    costo_adquisicion: Optional[float] = None
    valor_vida_cliente_estimado: Optional[float] = None
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_destino', 'marketing')

@dataclass(frozen=True)
class ConversionRechazadaIntegracion(EventoIntegracion):
    """
    Evento: Notificar a Marketing que una conversión fue rechazada
    Para análisis de calidad de tráfico
    """
    conversion_id: str = ""
    campana_id: str = ""
    afiliado_id: str = ""
    razon_rechazo: str = ""
    codigo_rechazo: str = ""
    fecha_rechazo: datetime = field(default_factory=datetime.now)
    
    # Datos para análisis de Marketing
    calidad_trafico_score: Optional[float] = None
    posible_fraude: bool = False
    patron_comportamiento: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_destino', 'marketing')

# Eventos hacia Afiliados
@dataclass(frozen=True)
class ComisionGeneradaIntegracion(EventoIntegracion):
    """
    Evento: Notificar a Afiliados que se generó una comisión
    Para actualización de balances y reportes
    """
    comision_id: str = ""
    conversion_id: str = ""
    afiliado_id: str = ""
    campana_id: str = ""
    monto_comision: float = 0.0
    moneda: str = "USD"
    porcentaje_aplicado: float = 0.0
    fecha_generacion: datetime = field(default_factory=datetime.now)
    
    # Datos adicionales para Afiliados
    tipo_comision: str = "porcentual"
    periodo_pago: str = "mensual"
    referencia_conversion: str = ""
    detalles_calculo: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_destino', 'afiliados')

@dataclass(frozen=True)
class ComisionAplicadaIntegracion(EventoIntegracion):
    """
    Evento: Notificar a Afiliados que una comisión fue aplicada al balance
    """
    comision_id: str = ""
    afiliado_id: str = ""
    monto_aplicado: float = 0.0
    moneda: str = "USD"
    balance_anterior: float = 0.0
    balance_nuevo: float = 0.0
    fecha_aplicacion: datetime = field(default_factory=datetime.now)
    referencia_transaccion: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_destino', 'afiliados')

@dataclass(frozen=True)
class ComisionCanceladaIntegracion(EventoIntegracion):
    """
    Evento: Notificar a Afiliados que una comisión fue cancelada
    """
    comision_id: str = ""
    conversion_id: str = ""
    afiliado_id: str = ""
    monto_cancelado: float = 0.0
    moneda: str = "USD"
    razon_cancelacion: str = ""
    requiere_ajuste_balance: bool = False
    fecha_cancelacion: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_destino', 'afiliados')

# Eventos de consulta hacia otros microservicios
@dataclass(frozen=True)
class ConsultarCampanaIntegracion(EventoIntegracion):
    """
    Consulta: Solicitar información de campaña a Marketing
    """
    campana_id: str = ""
    campos_solicitados: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_destino', 'marketing')

@dataclass(frozen=True)
class ConsultarAfiliadoIntegracion(EventoIntegracion):
    """
    Consulta: Solicitar información de afiliado a Afiliados
    """
    afiliado_id: str = ""
    campos_solicitados: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_destino', 'afiliados')

# Eventos de respuesta desde otros microservicios
@dataclass(frozen=True)
class RespuestaCampanaIntegracion(EventoIntegracion):
    """
    Respuesta: Información de campaña desde Marketing
    """
    campana_id: str = ""
    datos_campana: Dict[str, Any] = field(default_factory=dict)
    estado_campana: str = ""
    configuracion_comisiones: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_origen', 'marketing')
        object.__setattr__(self, 'microservicio_destino', 'conversiones')

@dataclass(frozen=True)
class RespuestaAfiliadoIntegracion(EventoIntegracion):
    """
    Respuesta: Información de afiliado desde Afiliados
    """
    afiliado_id: str = ""
    datos_afiliado: Dict[str, Any] = field(default_factory=dict)
    estado_afiliado: str = ""
    balance_actual: float = 0.0
    moneda: str = "USD"
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_origen', 'afiliados')
        object.__setattr__(self, 'microservicio_destino', 'conversiones')

# Eventos para auditoría y métricas cross-service
@dataclass(frozen=True)
class MetricasConversionesIntegracion(EventoIntegracion):
    """
    Evento: Métricas agregadas de conversiones para dashboard unificado
    """
    periodo_inicio: datetime = field(default_factory=datetime.now)
    periodo_fin: datetime = field(default_factory=datetime.now)
    
    # Métricas generales
    total_conversiones: int = 0
    valor_total_conversiones: float = 0.0
    tasa_conversion_promedio: float = 0.0
    
    # Métricas por campaña
    metricas_por_campana: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Métricas por afiliado
    metricas_por_afiliado: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Métricas de comisiones
    total_comisiones_generadas: float = 0.0
    promedio_porcentaje_comision: float = 0.0
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'microservicio_destino', 'analytics')

# Manejadores de eventos de integración
class ManejadorEventoIntegracion(ABC):
    """
    Interface base para manejadores de eventos de integración
    """
    
    @abstractmethod
    async def manejar(self, evento: EventoIntegracion) -> None:
        """Maneja el evento de integración"""
        pass
    
    @abstractmethod
    def puede_manejar(self, tipo_evento: type) -> bool:
        """Determina si puede manejar este tipo de evento"""
        pass

# Despachador de eventos de integración
class DespachadorEventosIntegracion:
    """
    Despachador centralizado de eventos de integración
    Coordina comunicación entre microservicios
    """
    
    def __init__(self):
        self._manejadores: Dict[type, List[ManejadorEventoIntegracion]] = {}
        self._configuracion = ConfiguracionIntegracion()
    
    def registrar_manejador(self, tipo_evento: type, manejador: ManejadorEventoIntegracion) -> None:
        """Registra manejador para tipo de evento de integración"""
        if tipo_evento not in self._manejadores:
            self._manejadores[tipo_evento] = []
        self._manejadores[tipo_evento].append(manejador)
    
    async def despachar(self, evento: EventoIntegracion) -> None:
        """Despacha evento de integración"""
        tipo_evento = type(evento)
        manejadores = self._manejadores.get(tipo_evento, [])
        
        for manejador in manejadores:
            try:
                await manejador.manejar(evento)
            except Exception as e:
                # Log error pero continuar
                print(f"Error manejando evento integración {tipo_evento.__name__}: {str(e)}")

# Factory para crear eventos de integración
class FactoriaEventosIntegracion:
    """
    Factory para crear eventos de integración específicos
    """
    
    @staticmethod
    def crear_conversion_detectada_marketing(conversion_id: str, campana_id: str, 
                                           afiliado_id: str, usuario_id: str,
                                           tipo_conversion: str, valor_conversion: float,
                                           datos_tracking: Dict[str, Any]) -> ConversionDetectadaIntegracion:
        """Crea evento de conversión detectada para Marketing"""
        return ConversionDetectadaIntegracion(
            conversion_id=conversion_id,
            campana_id=campana_id,
            afiliado_id=afiliado_id,
            usuario_id=usuario_id,
            tipo_conversion=tipo_conversion,
            valor_conversion=valor_conversion,
            datos_tracking=datos_tracking,
            utm_campaign=datos_tracking.get('utm_campaign'),
            utm_source=datos_tracking.get('utm_source'),
            utm_medium=datos_tracking.get('utm_medium'),
            utm_content=datos_tracking.get('utm_content'),
            utm_term=datos_tracking.get('utm_term')
        )
    
    @staticmethod
    def crear_comision_generada_afiliados(comision_id: str, conversion_id: str,
                                        afiliado_id: str, campana_id: str,
                                        monto_comision: float, porcentaje_aplicado: float,
                                        tipo_comision: str = "porcentual") -> ComisionGeneradaIntegracion:
        """Crea evento de comisión generada para Afiliados"""
        return ComisionGeneradaIntegracion(
            comision_id=comision_id,
            conversion_id=conversion_id,
            afiliado_id=afiliado_id,
            campana_id=campana_id,
            monto_comision=monto_comision,
            porcentaje_aplicado=porcentaje_aplicado,
            tipo_comision=tipo_comision,
            referencia_conversion=conversion_id
        )
    
    @staticmethod
    def crear_conversion_completada_marketing(conversion_id: str, campana_id: str,
                                            afiliado_id: str, valor_final: float,
                                            tiempo_procesamiento_ms: int) -> ConversionCompletadaIntegracion:
        """Crea evento de conversión completada para Marketing"""
        return ConversionCompletadaIntegracion(
            conversion_id=conversion_id,
            campana_id=campana_id,
            afiliado_id=afiliado_id,
            valor_final=valor_final,
            tiempo_total_procesamiento_ms=tiempo_procesamiento_ms
        )
    
    @staticmethod
    def crear_comision_aplicada_afiliados(comision_id: str, afiliado_id: str,
                                        monto_aplicado: float, balance_anterior: float,
                                        balance_nuevo: float, referencia_transaccion: str) -> ComisionAplicadaIntegracion:
        """Crea evento de comisión aplicada para Afiliados"""
        return ComisionAplicadaIntegracion(
            comision_id=comision_id,
            afiliado_id=afiliado_id,
            monto_aplicado=monto_aplicado,
            balance_anterior=balance_anterior,
            balance_nuevo=balance_nuevo,
            referencia_transaccion=referencia_transaccion
        )

# Configuración de integración
@dataclass
class ConfiguracionIntegracion:
    """Configuración para eventos de integración"""
    
    # Timeouts
    timeout_consulta_segundos: int = 30
    timeout_notificacion_segundos: int = 10
    
    # Reintentos
    max_reintentos_evento: int = 3
    delay_reintento_segundos: float = 1.0
    
    # Rutas de integración
    topico_marketing: str = "persistent://public/default/marketing-integracion"
    topico_afiliados: str = "persistent://public/default/afiliados-integracion"
    topico_analytics: str = "persistent://public/default/analytics-integracion"
    
    # Configuración de respuestas
    esperar_respuesta_consultas: bool = True
    timeout_respuesta_segundos: int = 60

# Validador de eventos de integración
class ValidadorEventosIntegracion:
    """
    Valida eventos de integración antes de envío
    """
    
    @staticmethod
    def validar_evento_marketing(evento: EventoIntegracion) -> List[str]:
        """Valida eventos dirigidos a Marketing"""
        errores = []
        
        if hasattr(evento, 'campana_id') and not evento.campana_id:
            errores.append("campana_id es obligatorio para eventos de Marketing")
        
        if hasattr(evento, 'valor_conversion') and evento.valor_conversion <= 0:
            errores.append("valor_conversion debe ser positivo")
        
        return errores
    
    @staticmethod
    def validar_evento_afiliados(evento: EventoIntegracion) -> List[str]:
        """Valida eventos dirigidos a Afiliados"""
        errores = []
        
        if hasattr(evento, 'afiliado_id') and not evento.afiliado_id:
            errores.append("afiliado_id es obligatorio para eventos de Afiliados")
        
        if hasattr(evento, 'monto_comision') and evento.monto_comision <= 0:
            errores.append("monto_comision debe ser positivo")
        
        return errores

# Serializador de eventos de integración
class SerializadorEventosIntegracion:
    """
    Serializa eventos de integración para transporte
    """
    
    @staticmethod
    def serializar(evento: EventoIntegracion) -> Dict[str, Any]:
        """Serializa evento de integración"""
        from dataclasses import asdict
        datos = asdict(evento)
        datos['tipo_evento'] = evento.__class__.__name__
        datos['schema_version'] = "1.0"
        return datos
    
    @staticmethod
    def deserializar(datos: Dict[str, Any]) -> EventoIntegracion:
        """Deserializa evento de integración"""
        tipo_evento = datos.pop('tipo_evento')
        datos.pop('schema_version', None)
        
        # Mapeo de tipos
        tipos_eventos = {
            'ConversionDetectadaIntegracion': ConversionDetectadaIntegracion,
            'ConversionCompletadaIntegracion': ConversionCompletadaIntegracion,
            'ConversionRechazadaIntegracion': ConversionRechazadaIntegracion,
            'ComisionGeneradaIntegracion': ComisionGeneradaIntegracion,
            'ComisionAplicadaIntegracion': ComisionAplicadaIntegracion,
            'ComisionCanceladaIntegracion': ComisionCanceladaIntegracion,
            'ConsultarCampanaIntegracion': ConsultarCampanaIntegracion,
            'ConsultarAfiliadoIntegracion': ConsultarAfiliadoIntegracion,
            'RespuestaCampanaIntegracion': RespuestaCampanaIntegracion,
            'RespuestaAfiliadoIntegracion': RespuestaAfiliadoIntegracion,
            'MetricasConversionesIntegracion': MetricasConversionesIntegracion
        }
        
        clase_evento = tipos_eventos.get(tipo_evento)
        if not clase_evento:
            raise ValueError(f"Tipo de evento de integración desconocido: {tipo_evento}")
        
        # Convertir fechas
        for campo in ['timestamp', 'fecha_conversion', 'fecha_completado', 'fecha_rechazo',
                     'fecha_generacion', 'fecha_aplicacion', 'fecha_cancelacion',
                     'periodo_inicio', 'periodo_fin']:
            if campo in datos and isinstance(datos[campo], str):
                datos[campo] = datetime.fromisoformat(datos[campo])
        
        return clase_evento(**datos)