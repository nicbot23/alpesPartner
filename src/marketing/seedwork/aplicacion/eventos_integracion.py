"""
Eventos de integración específicos para Marketing
Comunicación con microservicios Afiliados y Conversiones
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal

from ..dominio.eventos import EventoIntegracion

# Eventos de integración para comunicación con Afiliados
@dataclass
class NuevoAfiliadoDisponible(EventoIntegracion):
    """
    Evento: Nuevo afiliado disponible para campañas
    Origen: Microservicio Afiliados → Destino: Marketing
    """
    afiliado_id: str = ""
    nombre_empresa: str = ""
    categoria: str = ""
    ubicacion: str = ""
    comision_base: float = 0.0
    fecha_afiliacion: Optional[str] = None
    metadatos_afiliacion: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "NuevoAfiliadoDisponible"
        self.source_service = "afiliados"
        self.destination_services = ["marketing"]
        self.metadatos_marketing = {
            "tipo_evento": "afiliacion",
            "requiere_procesamiento": True,
            "prioridad": "media"
        }

@dataclass
class AfiliadoActualizado(EventoIntegracion):
    """
    Evento: Información de afiliado actualizada
    Origen: Microservicio Afiliados → Destino: Marketing
    """
    afiliado_id: str = ""
    cambios: Dict[str, Any] = field(default_factory=dict)
    version_anterior: int = 0
    version_nueva: int = 0
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "AfiliadoActualizado"
        self.source_service = "afiliados"
        self.destination_services = ["marketing"]
        self.metadatos_marketing = {
            "tipo_evento": "actualizacion",
            "requiere_procesamiento": True,
            "prioridad": "baja"
        }

@dataclass
class AfiliadoDesactivado(EventoIntegracion):
    """
    Evento: Afiliado desactivado o suspendido
    Origen: Microservicio Afiliados → Destino: Marketing
    """
    afiliado_id: str = ""
    razon_desactivacion: str = ""
    fecha_desactivacion: Optional[str] = None
    temporal: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "AfiliadoDesactivado"
        self.source_service = "afiliados"
        self.destination_services = ["marketing"]
        self.metadatos_marketing = {
            "tipo_evento": "desactivacion",
            "requiere_procesamiento": True,
            "prioridad": "alta"  # Alta prioridad para pausar campañas
        }

# Eventos de integración para comunicación con Conversiones
@dataclass
class ConversionRegistrada(EventoIntegracion):
    """
    Evento: Nueva conversión registrada
    Origen: Microservicio Conversiones → Destino: Marketing
    """
    conversion_id: str = ""
    afiliado_id: str = ""
    usuario_id: str = ""
    campana_id: Optional[str] = None
    valor_conversion: float = 0.0
    moneda: str = "USD"
    fecha_conversion: Optional[str] = None
    canal_origen: str = ""
    metadatos_conversion: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "ConversionRegistrada"
        self.source_service = "conversiones"
        self.destination_services = ["marketing"]
        self.metadatos_marketing = {
            "tipo_evento": "conversion",
            "requiere_procesamiento": True,
            "prioridad": "alta",  # Alta prioridad para tracking en tiempo real
            "actualizar_metricas": True
        }

@dataclass
class ConversionAnulada(EventoIntegracion):
    """
    Evento: Conversión anulada o revertida
    Origen: Microservicio Conversiones → Destino: Marketing
    """
    conversion_id: str = ""
    conversion_original_id: str = ""
    razon_anulacion: str = ""
    valor_anulado: float = 0.0
    campana_afectada: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "ConversionAnulada"
        self.source_service = "conversiones"
        self.destination_services = ["marketing"]
        self.metadatos_marketing = {
            "tipo_evento": "anulacion",
            "requiere_procesamiento": True,
            "prioridad": "alta",
            "revertir_metricas": True
        }

# Eventos que Marketing envía a otros microservicios
@dataclass
class CampanaLanzada(EventoIntegracion):
    """
    Evento: Campaña lanzada, disponible para afiliados
    Origen: Marketing → Destino: Afiliados, Conversiones
    """
    campana_id: str = ""
    nombre_campana: str = ""
    tipo_campana: str = ""
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    presupuesto_total: float = 0.0
    comision_ofrecida: float = 0.0
    segmentos_objetivo: List[str] = field(default_factory=list)
    canales_habilitados: List[str] = field(default_factory=list)
    criterios_afiliados: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "CampanaLanzada"
        self.source_service = "marketing"
        self.destination_services = ["afiliados", "conversiones"]
        self.metadatos_marketing = {
            "tipo_evento": "lanzamiento",
            "prioridad": "alta",
            "notificar_afiliados": True
        }

@dataclass
class CampanaPausadaOFinalizada(EventoIntegracion):
    """
    Evento: Campaña pausada o finalizada
    Origen: Marketing → Destino: Afiliados, Conversiones
    """
    campana_id: str = ""
    estado_anterior: str = ""
    estado_nuevo: str = ""
    razon_cambio: str = ""
    fecha_cambio: Optional[str] = None
    impacto_afiliados: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "CampanaPausadaOFinalizada"
        self.source_service = "marketing"
        self.destination_services = ["afiliados", "conversiones"]
        self.metadatos_marketing = {
            "tipo_evento": "cambio_estado",
            "prioridad": "alta",
            "detener_promocion": True
        }

@dataclass
class NuevoSegmentoCreado(EventoIntegracion):
    """
    Evento: Nuevo segmento de usuarios creado
    Origen: Marketing → Destino: Afiliados (para targeting)
    """
    segmento_id: str = ""
    nombre_segmento: str = ""
    tipo_segmento: str = ""
    criterios_resumen: Dict[str, Any] = field(default_factory=dict)
    usuarios_estimados: int = 0
    activo: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "NuevoSegmentoCreado"
        self.source_service = "marketing"
        self.destination_services = ["afiliados"]
        self.metadatos_marketing = {
            "tipo_evento": "segmentacion",
            "prioridad": "media",
            "actualizar_targeting": True
        }

@dataclass
class MetricasCampanaActualizadas(EventoIntegracion):
    """
    Evento: Métricas de campaña actualizadas
    Origen: Marketing → Destino: Afiliados (para optimización)
    """
    campana_id: str = ""
    periodo_inicio: Optional[str] = None
    periodo_fin: Optional[str] = None
    conversiones_periodo: int = 0
    valor_total_conversiones: float = 0.0
    costo_por_conversion: float = 0.0
    roi_estimado: float = 0.0
    rendimiento_por_canal: Dict[str, Any] = field(default_factory=dict)
    recomendaciones: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "MetricasCampanaActualizadas"
        self.source_service = "marketing"
        self.destination_services = ["afiliados"]
        self.metadatos_marketing = {
            "tipo_evento": "metricas",
            "prioridad": "baja",
            "optimizacion": True
        }

# Eventos para comunicación interna con otros bounded contexts
@dataclass
class ComisionCalculada(EventoIntegracion):
    """
    Evento: Comisión calculada para una conversión
    Origen: Marketing → Destino: Afiliados, Conversiones
    """
    conversion_id: str = ""
    afiliado_id: str = ""
    campana_id: str = ""
    comision_base: float = 0.0
    bonificaciones: float = 0.0
    comision_total: float = 0.0
    metodo_calculo: str = ""
    fecha_calculo: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "ComisionCalculada"
        self.source_service = "marketing"
        self.destination_services = ["afiliados", "conversiones"]
        self.metadatos_marketing = {
            "tipo_evento": "comision",
            "prioridad": "alta",
            "procesamiento_pago": True
        }

@dataclass
class RendimientoAfiliadoAnalizado(EventoIntegracion):
    """
    Evento: Análisis de rendimiento de afiliado completado
    Origen: Marketing → Destino: Afiliados
    """
    afiliado_id: str = ""
    periodo_analisis: str = ""
    conversiones_total: int = 0
    valor_generado: float = 0.0
    ranking_rendimiento: int = 0
    areas_mejora: List[str] = field(default_factory=list)
    recomendaciones: List[str] = field(default_factory=list)
    eligible_bonificaciones: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "RendimientoAfiliadoAnalizado"
        self.source_service = "marketing"
        self.destination_services = ["afiliados"]
        self.metadatos_marketing = {
            "tipo_evento": "analisis",
            "prioridad": "baja",
            "optimizacion_rendimiento": True
        }

# Eventos de sistema y monitoring
@dataclass
class AlertaCampanaPresupuesto(EventoIntegracion):
    """
    Evento: Alerta por presupuesto de campaña
    Origen: Marketing → Destino: Sistema de notificaciones
    """
    campana_id: str = ""
    presupuesto_total: float = 0.0
    presupuesto_utilizado: float = 0.0
    porcentaje_utilizado: float = 0.0
    umbral_alerta: float = 0.8  # 80% por defecto
    tiempo_estimado_agotamiento: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "AlertaCampanaPresupuesto"
        self.source_service = "marketing"
        self.destination_services = ["notificaciones"]
        self.metadatos_marketing = {
            "tipo_evento": "alerta",
            "prioridad": "alta",
            "requiere_atencion": True
        }

@dataclass
class ReporteCampanaFinalizada(EventoIntegracion):
    """
    Evento: Reporte final de campaña completada
    Origen: Marketing → Destino: Afiliados, Sistema de reportes
    """
    campana_id: str = ""
    fecha_inicio_real: Optional[str] = None
    fecha_fin_real: Optional[str] = None
    duracion_dias: int = 0
    presupuesto_utilizado: float = 0.0
    conversiones_total: int = 0
    valor_total_generado: float = 0.0
    roi_final: float = 0.0
    afiliados_participantes: int = 0
    canales_mas_efectivos: List[str] = field(default_factory=list)
    lecciones_aprendidas: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "ReporteCampanaFinalizada"
        self.source_service = "marketing"
        self.destination_services = ["afiliados", "reportes"]
        self.metadatos_marketing = {
            "tipo_evento": "reporte",
            "prioridad": "media",
            "archivar": True
        }

# Schema Registry para validación de eventos
class SchemaEventosIntegracion:
    """
    Registro de schemas para validación de eventos
    Principio de Responsabilidad Única - validación centralizada
    """
    
    SCHEMAS = {
        "NuevoAfiliadoDisponible": {
            "required_fields": ["afiliado_id", "nombre_empresa", "categoria"],
            "field_types": {
                "afiliado_id": str,
                "nombre_empresa": str,
                "categoria": str,
                "comision_base": float
            }
        },
        "ConversionRegistrada": {
            "required_fields": ["conversion_id", "afiliado_id", "usuario_id", "valor_conversion"],
            "field_types": {
                "conversion_id": str,
                "afiliado_id": str,
                "usuario_id": str,
                "valor_conversion": float
            }
        },
        "CampanaLanzada": {
            "required_fields": ["campana_id", "nombre_campana", "tipo_campana"],
            "field_types": {
                "campana_id": str,
                "nombre_campana": str,
                "tipo_campana": str,
                "presupuesto_total": float
            }
        }
    }
    
    @classmethod
    def validar_evento(cls, evento: EventoIntegracion) -> bool:
        """Valida estructura de evento de integración"""
        nombre_evento = evento.__class__.__name__
        
        if nombre_evento not in cls.SCHEMAS:
            return True  # No hay schema definido, asumir válido
        
        schema = cls.SCHEMAS[nombre_evento]
        
        # Verificar campos requeridos
        for campo in schema["required_fields"]:
            if not hasattr(evento, campo):
                return False
            valor = getattr(evento, campo)
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                return False
        
        # Verificar tipos de datos
        for campo, tipo_esperado in schema["field_types"].items():
            if hasattr(evento, campo):
                valor = getattr(evento, campo)
                if valor is not None and not isinstance(valor, tipo_esperado):
                    return False
        
        return True