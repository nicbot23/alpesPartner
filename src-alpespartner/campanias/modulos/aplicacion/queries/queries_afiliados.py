from campanias.seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado
from campanias.seedwork.aplicacion.queries import ejecutar_query as query
from dataclasses import dataclass
from typing import Optional, List, Dict
import uuid

@dataclass
class ObtenerAfiliadosEnCampana(Query):
    """Query para obtener todos los afiliados de una campaña"""
    id_campana: str
    estado: Optional[str] = None  # ACTIVO, INACTIVO, PENDIENTE, RECHAZADO
    tipo_afiliado: Optional[str] = None  # INDIVIDUAL, EMPRESA, INFLUENCER
    limite: Optional[int] = 10
    offset: Optional[int] = 0

@dataclass
class ObtenerAfiliadoPorId(Query):
    """Query para obtener un afiliado específico en una campaña"""
    id_campana: str
    id_afiliado: str

@dataclass
class ObtenerRendimientoAfiliado(Query):
    """Query para obtener métricas de rendimiento de un afiliado"""
    id_campana: str
    id_afiliado: str
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None

@dataclass
class ObtenerTopAfiliados(Query):
    """Query para obtener los mejores afiliados de una campaña"""
    id_campana: str
    metrica: str = "conversiones"  # conversiones, comisiones, clics
    limite: Optional[int] = 10
    periodo_dias: Optional[int] = 30

@dataclass
class ObtenerAfiliadosPendientesValidacion(Query):
    """Query para obtener afiliados que necesitan validación"""
    id_campana: Optional[str] = None  # Si es None, trae de todas las campanias
    limite: Optional[int] = 20
    offset: Optional[int] = 0

@dataclass
class ObtenerCodigosPromocionales(Query):
    """Query para obtener códigos promocionales de un afiliado"""
    id_campana: str
    id_afiliado: str
    estado: Optional[str] = None  # ACTIVO, USADO, EXPIRADO, INVALIDADO

@dataclass
class BuscarAfiliadosPorCriterios(Query):
    """Query para búsqueda avanzada de afiliados"""
    id_campana: Optional[str] = None
    texto_busqueda: Optional[str] = None  # Busca en nombre, email
    nivel_comision: Optional[str] = None  # BASICO, PREMIUM, VIP
    rendimiento_minimo: Optional[float] = None
    fecha_registro_desde: Optional[str] = None
    limite: Optional[int] = 10
    offset: Optional[int] = 0

class ObtenerAfiliadosEnCampanaHandler(QueryHandler):
    def handle(self, query: ObtenerAfiliadosEnCampana) -> QueryResultado:
        """Obtiene lista de afiliados de una campaña con filtros"""
        try:
            # TODO: Obtener afiliados del repositorio
            # TODO: Aplicar filtros de estado y tipo
            # TODO: Incluir métricas básicas de cada afiliado
            # TODO: Implementar paginación
            
            resultado = {
                "afiliados": [],
                "id_campana": query.id_campana,
                "filtros": {
                    "estado": query.estado,
                    "tipo": query.tipo_afiliado
                },
                "total": 0,
                "limite": query.limite,
                "offset": query.offset
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerAfiliadoPorIdHandler(QueryHandler):
    def handle(self, query: ObtenerAfiliadoPorId) -> QueryResultado:
        """Obtiene detalles completos de un afiliado específico"""
        try:
            # TODO: Obtener datos completos del afiliado
            # TODO: Incluir historial de conversiones
            # TODO: Incluir códigos promocionales
            # TODO: Incluir balance de comisiones
            
            resultado = {
                "afiliado": {
                    "id": query.id_afiliado,
                    "id_campana": query.id_campana,
                    "nombre": "Nombre del afiliado",
                    "email": "afiliado@ejemplo.com",
                    "estado": "ACTIVO",
                    "tipo": "INDIVIDUAL",
                    "nivel_comision": "PREMIUM",
                    "fecha_registro": "2025-09-01T10:00:00Z",
                    "metricas_resumen": {
                        "total_conversiones": 0,
                        "monto_total_generado": 0.0,
                        "comisiones_ganadas": 0.0,
                        "tasa_conversion": 0.0
                    }
                }
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerRendimientoAfiliadoHandler(QueryHandler):
    def handle(self, query: ObtenerRendimientoAfiliado) -> QueryResultado:
        """Obtiene métricas detalladas de rendimiento del afiliado"""
        try:
            # TODO: Calcular métricas de conversiones en el período
            # TODO: Calcular tasa de conversión
            # TODO: Obtener trending de performance
            # TODO: Comparar con promedio de la campaña
            
            resultado = {
                "id_afiliado": query.id_afiliado,
                "id_campana": query.id_campana,
                "periodo": {
                    "fecha_desde": query.fecha_desde,
                    "fecha_hasta": query.fecha_hasta
                },
                "metricas": {
                    "conversiones": {
                        "total": 0,
                        "por_tipo": {},
                        "trending_diario": []
                    },
                    "comisiones": {
                        "ganadas": 0.0,
                        "pendientes": 0.0,
                        "pagadas": 0.0
                    },
                    "trafico": {
                        "clics": 0,
                        "impresiones": 0,
                        "tasa_clic": 0.0,
                        "tasa_conversion": 0.0
                    },
                    "comparativa": {
                        "vs_promedio_campana": 0.0,
                        "ranking_en_campana": 0
                    }
                }
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerTopAfiliadosHandler(QueryHandler):
    def handle(self, query: ObtenerTopAfiliados) -> QueryResultado:
        """Obtiene ranking de mejores afiliados según métrica especificada"""
        try:
            # TODO: Ordenar afiliados por métrica especificada
            # TODO: Calcular período según periodo_dias
            # TODO: Incluir datos comparativos
            
            resultado = {
                "id_campana": query.id_campana,
                "metrica_ordenamiento": query.metrica,
                "periodo_dias": query.periodo_dias,
                "top_afiliados": [],
                "estadisticas": {
                    "total_afiliados_evaluados": 0,
                    "promedio_metrica": 0.0,
                    "mejor_performance": 0.0
                }
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerAfiliadosPendientesValidacionHandler(QueryHandler):
    def handle(self, query: ObtenerAfiliadosPendientesValidacion) -> QueryResultado:
        """Obtiene afiliados que requieren validación manual"""
        try:
            # TODO: Filtrar afiliados con estado PENDIENTE
            # TODO: Ordenar por fecha de registro
            # TODO: Incluir información relevante para validación
            
            resultado = {
                "afiliados_pendientes": [],
                "id_campana": query.id_campana,
                "total_pendientes": 0,
                "tiempo_promedio_validacion": "2 días",
                "limite": query.limite,
                "offset": query.offset
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerCodigosPromocionalesHandler(QueryHandler):
    def handle(self, query: ObtenerCodigosPromocionales) -> QueryResultado:
        """Obtiene códigos promocionales de un afiliado"""
        try:
            # TODO: Obtener códigos del afiliado
            # TODO: Incluir estadísticas de uso
            # TODO: Filtrar por estado si se especifica
            
            resultado = {
                "id_afiliado": query.id_afiliado,
                "id_campana": query.id_campana,
                "codigos": [],
                "estadisticas": {
                    "total_codigos": 0,
                    "codigos_activos": 0,
                    "codigos_usados": 0,
                    "tasa_uso": 0.0
                }
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class BuscarAfiliadosPorCriteriosHandler(QueryHandler):
    def handle(self, query: BuscarAfiliadosPorCriterios) -> QueryResultado:
        """Búsqueda avanzada de afiliados por múltiples criterios"""
        try:
            # TODO: Implementar búsqueda por texto
            # TODO: Filtrar por nivel de comisión
            # TODO: Filtrar por rendimiento mínimo
            # TODO: Aplicar filtros de fecha
            
            resultado = {
                "afiliados": [],
                "criterios_busqueda": {
                    "texto": query.texto_busqueda,
                    "nivel_comision": query.nivel_comision,
                    "rendimiento_minimo": query.rendimiento_minimo,
                    "fecha_desde": query.fecha_registro_desde
                },
                "total_encontrados": 0,
                "limite": query.limite,
                "offset": query.offset
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

# Registrar todos los handlers
@query.register(ObtenerAfiliadosEnCampana)
def ejecutar_obtener_afiliados_campana(query: ObtenerAfiliadosEnCampana):
    handler = ObtenerAfiliadosEnCampanaHandler()
    return handler.handle(query)

@query.register(ObtenerAfiliadoPorId)
def ejecutar_obtener_afiliado_id(query: ObtenerAfiliadoPorId):
    handler = ObtenerAfiliadoPorIdHandler()
    return handler.handle(query)

@query.register(ObtenerRendimientoAfiliado)
def ejecutar_obtener_rendimiento_afiliado(query: ObtenerRendimientoAfiliado):
    handler = ObtenerRendimientoAfiliadoHandler()
    return handler.handle(query)

@query.register(ObtenerTopAfiliados)
def ejecutar_obtener_top_afiliados(query: ObtenerTopAfiliados):
    handler = ObtenerTopAfiliadosHandler()
    return handler.handle(query)

@query.register(ObtenerAfiliadosPendientesValidacion)
def ejecutar_obtener_afiliados_pendientes(query: ObtenerAfiliadosPendientesValidacion):
    handler = ObtenerAfiliadosPendientesValidacionHandler()
    return handler.handle(query)

@query.register(ObtenerCodigosPromocionales)
def ejecutar_obtener_codigos_promocionales(query: ObtenerCodigosPromocionales):
    handler = ObtenerCodigosPromocionalesHandler()
    return handler.handle(query)

@query.register(BuscarAfiliadosPorCriterios)
def ejecutar_buscar_afiliados(query: BuscarAfiliadosPorCriterios):
    handler = BuscarAfiliadosPorCriteriosHandler()
    return handler.handle(query)