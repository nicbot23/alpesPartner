from campanias.seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado
from campanias.seedwork.aplicacion.queries import ejecutar_query as query
from dataclasses import dataclass
from typing import Optional, List, Dict
import uuid

@dataclass
class ObtenerCampana(Query):
    """Query para obtener una campaña específica por ID"""
    id_campana: str

@dataclass 
class ObtenerTodasCampanas(Query):
    """Query para obtener todas las campanias con filtros opcionales"""
    estado: Optional[str] = None  # ACTIVA, PAUSADA, TERMINADA, CANCELADA
    tipo_campana: Optional[str] = None  # EMAIL, SOCIAL_MEDIA, etc.
    fecha_inicio_desde: Optional[str] = None
    fecha_inicio_hasta: Optional[str] = None
    limite: Optional[int] = 10
    offset: Optional[int] = 0

@dataclass
class ObtenerCampanasPorResponsable(Query):
    """Query para obtener campanias de un responsable específico"""
    email_responsable: str
    estado: Optional[str] = None
    limite: Optional[int] = 10
    offset: Optional[int] = 0

@dataclass
class ObtenerCampanasActivas(Query):
    """Query para obtener campanias activas en el momento actual"""
    tipo_campana: Optional[str] = None
    limite: Optional[int] = 20
    offset: Optional[int] = 0

@dataclass
class ObtenerMetricasCampana(Query):
    """Query para obtener métricas de rendimiento de una campaña"""
    id_campana: str
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None

@dataclass
class BuscarCampanasPorCriterios(Query):
    """Query para búsqueda avanzada de campanias"""
    texto_busqueda: Optional[str] = None  # Busca en nombre, descripción
    presupuesto_minimo: Optional[float] = None
    presupuesto_maximo: Optional[float] = None
    canal_marketing: Optional[str] = None
    segmento_audiencia: Optional[str] = None
    limite: Optional[int] = 10
    offset: Optional[int] = 0

class ObtenerCampanaHandler(QueryHandler):
    def handle(self, query: ObtenerCampana) -> QueryResultado:
        """Obtiene una campaña específica con todos sus detalles"""
        try:
            # TODO: Obtener campaña del repositorio
            # TODO: Incluir métricas básicas
            # TODO: Incluir estado de afiliados
            
            resultado = {
                "id": query.id_campana,
                "nombre": "Campaña ejemplo",
                "estado": "ACTIVA",
                # ... más campos
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerTodasCampanasHandler(QueryHandler):
    def handle(self, query: ObtenerTodasCampanas) -> QueryResultado:
        """Obtiene lista paginada de campanias con filtros"""
        try:
            # TODO: Aplicar filtros de estado, tipo, fechas
            # TODO: Implementar paginación
            # TODO: Incluir métricas resumidas
            
            resultado = {
                "campangas": [],
                "total": 0,
                "limite": query.limite,
                "offset": query.offset
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerCampanasPorResponsableHandler(QueryHandler):
    def handle(self, query: ObtenerCampanasPorResponsable) -> QueryResultado:
        """Obtiene campanias asignadas a un responsable específico"""
        try:
            # TODO: Filtrar por email_responsable
            # TODO: Aplicar filtros adicionales
            # TODO: Ordenar por fecha_creacion DESC
            
            resultado = {
                "campangas": [],
                "responsable": query.email_responsable,
                "total": 0
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerCampanasActivasHandler(QueryHandler):
    def handle(self, query: ObtenerCampanasActivas) -> QueryResultado:
        """Obtiene campanias que están activas actualmente"""
        try:
            # TODO: Filtrar por estado ACTIVA
            # TODO: Verificar que fecha actual esté dentro del período
            # TODO: Incluir información de afiliados activos
            
            resultado = {
                "campangas_activas": [],
                "total": 0,
                "fecha_consulta": "2025-09-16T10:00:00Z"
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class ObtenerMetricasCampanaHandler(QueryHandler):
    def handle(self, query: ObtenerMetricasCampana) -> QueryResultado:
        """Obtiene métricas de rendimiento de una campaña"""
        try:
            # TODO: Calcular métricas de conversiones
            # TODO: Calcular ROI y performance
            # TODO: Obtener estadísticas de afiliados
            # TODO: Incluir datos de comisiones
            
            resultado = {
                "id_campana": query.id_campana,
                "metricas": {
                    "total_conversiones": 0,
                    "monto_total_conversiones": 0.0,
                    "total_afiliados_activos": 0,
                    "comisiones_pagadas": 0.0,
                    "comisiones_pendientes": 0.0,
                    "roi": 0.0,
                    "costo_por_conversion": 0.0
                },
                "periodo": {
                    "fecha_desde": query.fecha_desde,
                    "fecha_hasta": query.fecha_hasta
                }
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

class BuscarCampanasPorCriteriosHandler(QueryHandler):
    def handle(self, query: BuscarCampanasPorCriterios) -> QueryResultado:
        """Búsqueda avanzada de campanias por múltiples criterios"""
        try:
            # TODO: Implementar búsqueda por texto en nombre/descripción
            # TODO: Filtrar por rango de presupuesto
            # TODO: Filtrar por canal y segmento
            # TODO: Aplicar ordenamiento y paginación
            
            resultado = {
                "campangas": [],
                "criterios_busqueda": {
                    "texto": query.texto_busqueda,
                    "presupuesto_rango": [query.presupuesto_minimo, query.presupuesto_maximo],
                    "canal": query.canal_marketing,
                    "segmento": query.segmento_audiencia
                },
                "total_encontrados": 0,
                "limite": query.limite,
                "offset": query.offset
            }
            
            return QueryResultado(resultado=resultado)
            
        except Exception as e:
            raise e

# Registrar todos los handlers de queries
@query.register(ObtenerCampana)
def ejecutar_obtener_campana(query: ObtenerCampana):
    handler = ObtenerCampanaHandler()
    return handler.handle(query)

@query.register(ObtenerTodasCampanas)
def ejecutar_obtener_todas_campanas(query: ObtenerTodasCampanas):
    handler = ObtenerTodasCampanasHandler()
    return handler.handle(query)

@query.register(ObtenerCampanasPorResponsable)
def ejecutar_obtener_campanas_responsable(query: ObtenerCampanasPorResponsable):
    handler = ObtenerCampanasPorResponsableHandler()
    return handler.handle(query)

@query.register(ObtenerCampanasActivas)
def ejecutar_obtener_campanas_activas(query: ObtenerCampanasActivas):
    handler = ObtenerCampanasActivasHandler()
    return handler.handle(query)

@query.register(ObtenerMetricasCampana)
def ejecutar_obtener_metricas_campana(query: ObtenerMetricasCampana):
    handler = ObtenerMetricasCampanaHandler()
    return handler.handle(query)

@query.register(BuscarCampanasPorCriterios)
def ejecutar_buscar_campanas(query: BuscarCampanasPorCriterios):
    handler = BuscarCampanasPorCriteriosHandler()
    return handler.handle(query)