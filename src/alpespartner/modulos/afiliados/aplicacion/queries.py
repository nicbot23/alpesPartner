"""
Queries para el módulo de Afiliados
Representan consultas de información sin cambio de estado
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime

from alpespartner.seedwork.aplicacion.queries import Query


@dataclass(frozen=True)
class QueryObtenerAfiliado(Query):
    """Query para obtener un afiliado por ID."""
    
    afiliado_id: str


@dataclass(frozen=True)
class QueryObtenerAfiliadoPorDocumento(Query):
    """Query para obtener un afiliado por documento."""
    
    tipo_documento: str
    numero_documento: str


@dataclass(frozen=True)
class QueryObtenerAfiliadoPorEmail(Query):
    """Query para obtener un afiliado por email."""
    
    email: str


@dataclass(frozen=True)
class QueryObtenerAfiliadoPorCodigoReferencia(Query):
    """Query para obtener un afiliado por código de referencia."""
    
    codigo_referencia: str


@dataclass(frozen=True)
class QueryBuscarAfiliados(Query):
    """Query para buscar afiliados con filtros."""
    
    # Filtros de búsqueda
    estado: Optional[str] = None
    tipo_afiliado: Optional[str] = None
    email_like: Optional[str] = None
    nombres_like: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    afiliado_referente_id: Optional[str] = None
    
    # Parámetros de paginación y ordenamiento
    ordenar_por: str = 'fecha_creacion'
    orden_desc: bool = True
    limite: int = 100
    offset: int = 0


@dataclass(frozen=True)
class QueryObtenerReferidosActivos(Query):
    """Query para obtener afiliados referidos activos."""
    
    afiliado_referente_id: str


@dataclass(frozen=True)
class QueryObtenerEstadisticasAfiliados(Query):
    """Query para obtener estadísticas de afiliados."""
    
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None


@dataclass(frozen=True)
class QueryValidarDisponibilidadDocumento(Query):
    """Query para validar si un documento está disponible."""
    
    tipo_documento: str
    numero_documento: str
    excluir_afiliado_id: Optional[str] = None


@dataclass(frozen=True)
class QueryValidarDisponibilidadEmail(Query):
    """Query para validar si un email está disponible."""
    
    email: str
    excluir_afiliado_id: Optional[str] = None


@dataclass(frozen=True)
class QueryCalcularComisiones(Query):
    """Query para calcular comisiones de un afiliado."""
    
    afiliado_id: str
    monto_transaccion: str  # Como string para evitar problemas de serialización
    incluir_comision_referencia: bool = True


@dataclass(frozen=True)
class QueryObtenerHistorialEstados(Query):
    """Query para obtener historial de cambios de estado."""
    
    afiliado_id: str
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None


@dataclass(frozen=True)
class QueryObtenerReporteAfiliados(Query):
    """Query para generar reporte de afiliados."""
    
    formato: str = 'json'  # json, csv, excel
    filtros: Optional[Dict[str, Any]] = None
    incluir_estadisticas: bool = True
    incluir_referencias: bool = True