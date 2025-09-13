from alpespartner.seedwork.aplicacion.handlers import ManejadorQuery
from alpespartner.modulos.conversiones.aplicacion.queries import (
    GetConversion, ListConversions, GetConversionsByAfiliado, 
    GetConversionsByCampana, GetConversionsStats
)
from alpespartner.modulos.conversiones.dominio.repositorios import RepositorioConversiones
from alpespartner.modulos.conversiones.infraestructura.mapeadores import MapeadorConversiones
from alpespartner.seedwork.dominio.excepciones import ReglaNegocioException
from datetime import datetime
from typing import Dict, List, Any
import logging


logger = logging.getLogger(__name__)


class GetConversionHandler(ManejadorQuery):
    """Handler para obtener una conversión específica."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, query: GetConversion) -> Dict[str, Any]:
        """Obtiene una conversión por ID."""
        try:
            conversion = self._repositorio.obtener_por_id(query.conversion_id)
            if not conversion:
                raise ReglaNegocioException(f"Conversión no encontrada: {query.conversion_id}")
            
            # Convertir a diccionario para respuesta
            return MapeadorConversiones.entidad_a_dict(conversion)
            
        except Exception as e:
            logger.error(f"Error obteniendo conversión {query.conversion_id}: {e}")
            raise


class ListConversionsHandler(ManejadorQuery):
    """Handler para listar conversiones con filtros."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, query: ListConversions) -> Dict[str, Any]:
        """Lista conversiones con filtros y paginación."""
        try:
            # Construir filtros
            filtros = {}
            if query.afiliado_id:
                filtros['afiliado_id'] = query.afiliado_id
            if query.campana_id:
                filtros['campana_id'] = query.campana_id
            if query.tipo_conversion:
                filtros['tipo_conversion'] = query.tipo_conversion
            if query.estado:
                filtros['estado'] = query.estado
            if query.fecha_desde:
                filtros['fecha_desde'] = datetime.fromisoformat(query.fecha_desde)
            if query.fecha_hasta:
                filtros['fecha_hasta'] = datetime.fromisoformat(query.fecha_hasta)
            
            # Obtener conversiones
            conversiones = self._repositorio.buscar_con_filtros(
                filtros=filtros,
                page=query.page,
                size=query.size
            )
            
            # Obtener total para paginación
            total = self._repositorio.contar_con_filtros(filtros)
            
            # Convertir a diccionarios
            resultado = {
                'conversiones': [MapeadorConversiones.entidad_a_dict(c) for c in conversiones],
                'paginacion': {
                    'page': query.page,
                    'size': query.size,
                    'total': total,
                    'pages': (total + query.size - 1) // query.size
                }
            }
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error listando conversiones: {e}")
            raise


class GetConversionsByAfiliadoHandler(ManejadorQuery):
    """Handler para obtener conversiones de un afiliado."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, query: GetConversionsByAfiliado) -> List[Dict[str, Any]]:
        """Obtiene conversiones de un afiliado específico."""
        try:
            conversiones = self._repositorio.obtener_por_afiliado(
                query.afiliado_id,
                incluir_canceladas=query.incluir_canceladas
            )
            
            return [MapeadorConversiones.entidad_a_dict(c) for c in conversiones]
            
        except Exception as e:
            logger.error(f"Error obteniendo conversiones del afiliado {query.afiliado_id}: {e}")
            raise


class GetConversionsByCampanaHandler(ManejadorQuery):
    """Handler para obtener conversiones de una campaña."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, query: GetConversionsByCampana) -> List[Dict[str, Any]]:
        """Obtiene conversiones de una campaña específica."""
        try:
            conversiones = self._repositorio.obtener_por_campana(
                query.campana_id,
                estado=query.estado
            )
            
            return [MapeadorConversiones.entidad_a_dict(c) for c in conversiones]
            
        except Exception as e:
            logger.error(f"Error obteniendo conversiones de la campaña {query.campana_id}: {e}")
            raise


class GetConversionsStatsHandler(ManejadorQuery):
    """Handler para obtener estadísticas de conversiones."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, query: GetConversionsStats) -> Dict[str, Any]:
        """Obtiene estadísticas de conversiones."""
        try:
            fecha_desde = None
            fecha_hasta = None
            
            if query.fecha_desde:
                fecha_desde = datetime.fromisoformat(query.fecha_desde)
            if query.fecha_hasta:
                fecha_hasta = datetime.fromisoformat(query.fecha_hasta)
            
            stats = self._repositorio.obtener_estadisticas(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                agrupado_por=query.agrupado_por
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de conversiones: {e}")
            raise