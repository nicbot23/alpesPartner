from campanias.seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado
from campanias.seedwork.aplicacion.queries import ejecutar_query as query
from dataclasses import dataclass
from typing import Optional, List, Dict
import uuid

@dataclass
class ObtenerConversionesPorCampana(Query):
    """Query para obtener conversiones de una campaña"""
    id_campana: str
    estado: Optional[str] = None  # REGISTRADA, VALIDADA, CONFIRMADA, RECHAZADA, REVERTIDA
    tipo_conversion: Optional[str] = None  # VENTA, LEAD, CLICK, IMPRESION, DESCARGA
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    limite: Optional[int] = 10
    offset: Optional[int] = 0

@dataclass
class ObtenerConversionesPorAfiliado(Query):
    """Query para obtener conversiones de un afiliado específico"""
    id_afiliado: str
    id_campana: Optional[str] = None
    estado: Optional[str] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    limite: Optional[int] = 10
    offset: Optional[int] = 0

@dataclass
class ObtenerConversion(Query):
    """Query para obtener una conversión específica"""
    id_conversion: str

@dataclass
class ObtenerConversionesPendientesValidacion(Query):
    """Query para obtener conversiones que requieren validación"""
    id_campana: Optional[str] = None
    dias_pendientes: Optional[int] = None
    valor_minimo: Optional[float] = None
    fuente_sospechosa: Optional[bool] = None
    limite: Optional[int] = 20
    offset: Optional[int] = 0

@dataclass
class ObtenerConversionesDuplicadas(Query):
    """Query para obtener conversiones marcadas como duplicadas"""
    id_campana: Optional[str] = None
    id_afiliado: Optional[str] = None
    fecha_desde: Optional[str] = None
    limite: Optional[int] = 10
    offset: Optional[int] = 0

@dataclass
class ObtenerMetricasConversionCampana(Query):
    """Query para obtener métricas de conversión de una campaña"""
    id_campana: str
    periodo: Optional[str] = "mes"  # semana, mes, trimestre
    agrupar_por: Optional[str] = "dia"  # dia, semana, mes, afiliado, tipo

@dataclass
class ObtenerFunnelConversion(Query):
    """Query para obtener funnel de conversión de una campaña"""
    id_campana: str
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    segmentar_por: Optional[str] = None  # afiliado, fuente, tipo_cliente

@dataclass
class ObtenerTendenciasConversion(Query):
    """Query para obtener tendencias de conversión"""
    id_campana: Optional[str] = None
    periodo_analisis: str = "30_dias"  # 7_dias, 30_dias, 90_dias
    comparar_con_periodo_anterior: bool = True
    segmentar_por: Optional[str] = None

@dataclass
class BuscarConversionesPorCriterios(Query):
    """Query para búsqueda avanzada de conversiones"""
    codigo_promocional: Optional[str] = None
    rango_monto: Optional[List[float]] = None  # [min, max]
    ip_usuario: Optional[str] = None
    id_cliente: Optional[str] = None
    fuente_conversion: Optional[str] = None
    user_agent_contiene: Optional[str] = None
    limite: Optional[int] = 10
    offset: Optional[int] = 0

class ObtenerConversionesPorCampanaHandler(QueryHandler):
    def handle(self, query: ObtenerConversionesPorCampana) -> QueryResultado:
        """Obtiene conversiones de una campaña con filtros"""
        try:
            # TODO: Obtener conversiones del repositorio
            # TODO: Aplicar filtros de estado, tipo, fechas
            # TODO: Incluir datos del afiliado y cliente
            # TODO: Calcular métricas agregadas
            
            resultado = {
                "conversiones": [],
                "id_campana": query.id_campana,
                "filtros": {
                    "estado": query.estado,
                    "tipo": query.tipo_conversion,
                    "periodo": [query.fecha_desde, query.fecha_hasta]
                },
                "metricas": {
                    "total_conversiones": 0,
                    "monto_total": 0.0,
                    "conversion_promedio": 0.0,
                    "tasa_confirmacion": 0.0
                },
                "limite": query.limite,
                "offset": query.offset
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerConversionesPorAfiliadoHandler(QueryHandler):
    def handle(self, query: ObtenerConversionesPorAfiliado) -> QueryResultado:
        """Obtiene conversiones de un afiliado específico"""
        try:
            # TODO: Filtrar conversiones por afiliado
            # TODO: Incluir datos de campaña si no se especifica
            # TODO: Calcular métricas de rendimiento del afiliado
            # TODO: Identificar patrones de conversión
            
            resultado = {
                "conversiones": [],
                "id_afiliado": query.id_afiliado,
                "filtros": {
                    "campana": query.id_campana,
                    "estado": query.estado,
                    "periodo": [query.fecha_desde, query.fecha_hasta]
                },
                "rendimiento": {
                    "total_conversiones": 0,
                    "monto_total_generado": 0.0,
                    "conversion_promedio": 0.0,
                    "mejores_horas": [],
                    "mejores_dias": [],
                    "tipos_conversion_mas_exitosos": []
                },
                "limite": query.limite,
                "offset": query.offset
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerConversionHandler(QueryHandler):
    def handle(self, query: ObtenerConversion) -> QueryResultado:
        """Obtiene detalles completos de una conversión específica"""
        try:
            # TODO: Obtener conversión del repositorio
            # TODO: Incluir historial de cambios de estado
            # TODO: Incluir datos de comisión asociada
            # TODO: Incluir información de validación
            
            resultado = {
                "conversion": {
                    "id": query.id_conversion,
                    "id_campana": "uuid-campana",
                    "id_afiliado": "uuid-afiliado", 
                    "codigo_promocional": "PROMO123",
                    "tipo_conversion": "VENTA",
                    "monto_conversion": 0.0,
                    "moneda": "USD",
                    "estado": "CONFIRMADA",
                    "fecha_conversion": "2025-09-16T14:30:00Z",
                    "datos_conversion": {},
                    "fuente_conversion": "WEB",
                    "ip_usuario": "192.168.1.1",
                    "user_agent": "Mozilla/5.0...",
                    "id_cliente": "uuid-cliente",
                    "validaciones": {
                        "anti_fraude": "APROBADA",
                        "duplicado": "NO_DUPLICADO",
                        "cliente_valido": "VERIFICADO"
                    },
                    "comision_asociada": {
                        "id_comision": "uuid-comision",
                        "monto": 0.0,
                        "estado": "CALCULADA"
                    },
                    "historial_estados": []
                }
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerConversionesPendientesValidacionHandler(QueryHandler):
    def handle(self, query: ObtenerConversionesPendientesValidacion) -> QueryResultado:
        """Obtiene conversiones que requieren validación manual"""
        try:
            # TODO: Filtrar conversiones con estado REGISTRADA
            # TODO: Aplicar filtros de tiempo pendiente y valor
            # TODO: Priorizar por riesgo y monto
            # TODO: Incluir indicadores de riesgo
            
            resultado = {
                "conversiones_pendientes": [],
                "filtros": {
                    "campana": query.id_campana,
                    "dias_pendientes": query.dias_pendientes,
                    "valor_minimo": query.valor_minimo,
                    "fuente_sospechosa": query.fuente_sospechosa
                },
                "estadisticas": {
                    "total_pendientes": 0,
                    "valor_total_pendiente": 0.0,
                    "tiempo_promedio_validacion": "4 horas",
                    "conversiones_alto_riesgo": 0
                },
                "indicadores_riesgo": {
                    "ips_sospechosas": [],
                    "afiliados_con_patrones_extraños": [],
                    "valores_atipicos": []
                },
                "limite": query.limite,
                "offset": query.offset
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerConversionesDuplicadasHandler(QueryHandler):
    def handle(self, query: ObtenerConversionesDuplicadas) -> QueryResultado:
        """Obtiene conversiones identificadas como duplicadas"""
        try:
            # TODO: Obtener conversiones marcadas como duplicadas
            # TODO: Incluir información de la conversión original
            # TODO: Mostrar criterios de detección de duplicado
            # TODO: Calcular impacto en comisiones
            
            resultado = {
                "conversiones_duplicadas": [],
                "filtros": {
                    "campana": query.id_campana,
                    "afiliado": query.id_afiliado,
                    "fecha_desde": query.fecha_desde
                },
                "estadisticas": {
                    "total_duplicadas": 0,
                    "impacto_comisiones": 0.0,
                    "criterios_deteccion_mas_comunes": [],
                    "afiliados_con_mas_duplicadas": []
                },
                "acciones_sugeridas": [],
                "limite": query.limite,
                "offset": query.offset
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerMetricasConversionCampanaHandler(QueryHandler):
    def handle(self, query: ObtenerMetricasConversionCampana) -> QueryResultado:
        """Obtiene métricas agregadas de conversión de una campaña"""
        try:
            # TODO: Calcular métricas por período especificado
            # TODO: Agrupar según criterio seleccionado
            # TODO: Calcular tasas de conversión y performance
            # TODO: Generar comparativas con objetivos
            
            resultado = {
                "id_campana": query.id_campana,
                "periodo": query.periodo,
                "agrupacion": query.agrupar_por,
                "metricas_globales": {
                    "total_conversiones": 0,
                    "monto_total": 0.0,
                    "conversion_promedio": 0.0,
                    "tasa_conversion_global": 0.0,
                    "crecimiento_vs_periodo_anterior": 0.0
                },
                "metricas_por_tipo": {},
                "tendencias": [],
                "distribucion_temporal": [],
                "top_performers": {
                    "afiliados": [],
                    "codigos_promocionales": [],
                    "fuentes_trafico": []
                },
                "alertas": []
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerFunnelConversionHandler(QueryHandler):
    def handle(self, query: ObtenerFunnelConversion) -> QueryResultado:
        """Obtiene análisis de funnel de conversión"""
        try:
            # TODO: Calcular pasos del funnel desde impresión hasta conversión
            # TODO: Identificar puntos de abandono
            # TODO: Segmentar según criterio especificado
            # TODO: Calcular tasas de conversión por paso
            
            resultado = {
                "id_campana": query.id_campana,
                "periodo": [query.fecha_desde, query.fecha_hasta],
                "segmentacion": query.segmentar_por,
                "funnel": {
                    "impresiones": 0,
                    "clics": 0,
                    "visitas_landing": 0,
                    "conversiones_iniciadas": 0,
                    "conversiones_completadas": 0
                },
                "tasas_conversion": {
                    "clic_impresion": 0.0,
                    "visita_clic": 0.0,
                    "conversion_visita": 0.0,
                    "completacion_inicio": 0.0
                },
                "puntos_abandono": [],
                "segmentos": [],
                "recomendaciones": []
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerTendenciasConversionHandler(QueryHandler):
    def handle(self, query: ObtenerTendenciasConversion) -> QueryResultado:
        """Obtiene análisis de tendencias de conversión"""
        try:
            # TODO: Analizar tendencias en el período especificado
            # TODO: Comparar con período anterior si se solicita
            # TODO: Detectar patrones estacionales
            # TODO: Identificar anomalías
            
            resultado = {
                "periodo_analisis": query.periodo_analisis,
                "campana": query.id_campana,
                "segmentacion": query.segmentar_por,
                "tendencias": {
                    "conversion_diaria": [],
                    "patrones_semanales": {},
                    "patrones_horarios": {},
                    "tendencia_general": "CRECIENTE"  # CRECIENTE, DECRECIENTE, ESTABLE
                },
                "comparativa": {
                    "periodo_anterior": {
                        "habilitada": query.comparar_con_periodo_anterior,
                        "cambio_porcentual": 0.0,
                        "significancia_estadistica": False
                    }
                },
                "anomalias_detectadas": [],
                "proyecciones": {
                    "proximos_7_dias": {},
                    "fin_campana": {}
                },
                "insights": []
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class BuscarConversionesPorCriteriosHandler(QueryHandler):
    def handle(self, query: BuscarConversionesPorCriterios) -> QueryResultado:
        """Búsqueda forense/avanzada de conversiones"""
        try:
            # TODO: Implementar búsqueda por múltiples criterios
            # TODO: Aplicar filtros de código promocional, IP, cliente
            # TODO: Buscar patrones en user agents
            # TODO: Filtrar por rangos de monto
            
            resultado = {
                "conversiones_encontradas": [],
                "criterios_busqueda": {
                    "codigo_promocional": query.codigo_promocional,
                    "rango_monto": query.rango_monto,
                    "ip_usuario": query.ip_usuario,
                    "id_cliente": query.id_cliente,
                    "fuente": query.fuente_conversion,
                    "user_agent_filtro": query.user_agent_contiene
                },
                "estadisticas": {
                    "total_encontradas": 0,
                    "monto_total": 0.0,
                    "ips_unicas": 0,
                    "clientes_unicos": 0,
                    "patrones_detectados": []
                },
                "alertas_seguridad": [],
                "limite": query.limite,
                "offset": query.offset
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

# Registrar todos los handlers
@query.register(ObtenerConversionesPorCampana)
def ejecutar_obtener_conversiones_campana(query: ObtenerConversionesPorCampana):
    handler = ObtenerConversionesPorCampanaHandler()
    return handler.handle(query)

@query.register(ObtenerConversionesPorAfiliado)
def ejecutar_obtener_conversiones_afiliado(query: ObtenerConversionesPorAfiliado):
    handler = ObtenerConversionesPorAfiliadoHandler()
    return handler.handle(query)

@query.register(ObtenerConversion)
def ejecutar_obtener_conversion(query: ObtenerConversion):
    handler = ObtenerConversionHandler()
    return handler.handle(query)

@query.register(ObtenerConversionesPendientesValidacion)
def ejecutar_obtener_conversiones_pendientes(query: ObtenerConversionesPendientesValidacion):
    handler = ObtenerConversionesPendientesValidacionHandler()
    return handler.handle(query)

@query.register(ObtenerConversionesDuplicadas)
def ejecutar_obtener_conversiones_duplicadas(query: ObtenerConversionesDuplicadas):
    handler = ObtenerConversionesDuplicadasHandler()
    return handler.handle(query)

@query.register(ObtenerMetricasConversionCampana)
def ejecutar_obtener_metricas_conversion(query: ObtenerMetricasConversionCampana):
    handler = ObtenerMetricasConversionCampanaHandler()
    return handler.handle(query)

@query.register(ObtenerFunnelConversion)
def ejecutar_obtener_funnel_conversion(query: ObtenerFunnelConversion):
    handler = ObtenerFunnelConversionHandler()
    return handler.handle(query)

@query.register(ObtenerTendenciasConversion)
def ejecutar_obtener_tendencias_conversion(query: ObtenerTendenciasConversion):
    handler = ObtenerTendenciasConversionHandler()
    return handler.handle(query)

@query.register(BuscarConversionesPorCriterios)
def ejecutar_buscar_conversiones(query: BuscarConversionesPorCriterios):
    handler = BuscarConversionesPorCriteriosHandler()
    return handler.handle(query)