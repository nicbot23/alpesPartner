"""
Consultas específicas del microservicio Afiliados
Implementa el lado Query de CQRS
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List

from ..seedwork.aplicacion.consultas import Consulta, ManejadorConsulta, ResultadoPaginado
from ..dominio.repositorios import RepositorioConsultasAfiliados

# Consultas

@dataclass
class BuscarAfiliados(Consulta):
    """Consulta para buscar afiliados con filtros"""
    nombre: Optional[str] = None
    documento: Optional[str] = None
    email: Optional[str] = None
    estado: Optional[str] = None
    fecha_afiliacion_desde: Optional[datetime] = None
    fecha_afiliacion_hasta: Optional[datetime] = None
    pagina: int = 1
    tamaño_pagina: int = 20

@dataclass
class ObtenerDetalleAfiliado(Consulta):
    """Consulta para obtener detalle completo de un afiliado"""
    afiliado_id: str

@dataclass
class ListarAfiliadosActivos(Consulta):
    """Consulta para listar afiliados activos"""
    pagina: int = 1
    tamaño_pagina: int = 20

@dataclass
class ObtenerEstadisticasAfiliacion(Consulta):
    """Consulta para obtener estadísticas de afiliación"""
    fecha_inicio: datetime
    fecha_fin: datetime

@dataclass
class BuscarAfiliadosPorTexto(Consulta):
    """Consulta para búsqueda de texto libre"""
    texto_busqueda: str
    pagina: int = 1
    tamaño_pagina: int = 20

@dataclass
class ListarAfiliadosRecientes(Consulta):
    """Consulta para listar afiliados recientes"""
    dias: int = 7
    pagina: int = 1
    tamaño_pagina: int = 20

@dataclass
class ObtenerHistorialEstados(Consulta):
    """Consulta para obtener historial de estados de un afiliado"""
    afiliado_id: str

# Manejadores de consultas

class ManejadorBuscarAfiliados(ManejadorConsulta[BuscarAfiliados, ResultadoPaginado]):
    """
    Manejador para búsqueda de afiliados con filtros
    Principio de Responsabilidad Única
    """
    
    def __init__(self, repositorio_consultas: RepositorioConsultasAfiliados):
        self._repositorio = repositorio_consultas
    
    async def handle(self, consulta: BuscarAfiliados) -> ResultadoPaginado:
        """Maneja la búsqueda de afiliados"""
        
        # Construir filtros
        filtros = {}
        if consulta.nombre:
            filtros['nombre'] = consulta.nombre
        if consulta.documento:
            filtros['documento'] = consulta.documento
        if consulta.email:
            filtros['email'] = consulta.email
        if consulta.estado:
            filtros['estado'] = consulta.estado
        if consulta.fecha_afiliacion_desde:
            filtros['fecha_afiliacion_desde'] = consulta.fecha_afiliacion_desde
        if consulta.fecha_afiliacion_hasta:
            filtros['fecha_afiliacion_hasta'] = consulta.fecha_afiliacion_hasta
        
        return await self._repositorio.buscar_afiliados(
            filtros=filtros,
            pagina=consulta.pagina,
            tamaño_pagina=consulta.tamaño_pagina
        )

class ManejadorObtenerDetalleAfiliado(ManejadorConsulta[ObtenerDetalleAfiliado, Optional[Dict[str, Any]]]):
    """
    Manejador para obtener detalle de afiliado
    Principio de Responsabilidad Única
    """
    
    def __init__(self, repositorio_consultas: RepositorioConsultasAfiliados):
        self._repositorio = repositorio_consultas
    
    async def handle(self, consulta: ObtenerDetalleAfiliado) -> Optional[Dict[str, Any]]:
        """Maneja la obtención de detalle de afiliado"""
        return await self._repositorio.obtener_afiliado_detalle(consulta.afiliado_id)

class ManejadorListarAfiliadosActivos(ManejadorConsulta[ListarAfiliadosActivos, ResultadoPaginado]):
    """
    Manejador para listar afiliados activos
    Principio de Responsabilidad Única
    """
    
    def __init__(self, repositorio_consultas: RepositorioConsultasAfiliados):
        self._repositorio = repositorio_consultas
    
    async def handle(self, consulta: ListarAfiliadosActivos) -> ResultadoPaginado:
        """Maneja el listado de afiliados activos"""
        return await self._repositorio.listar_afiliados_activos(
            pagina=consulta.pagina,
            tamaño_pagina=consulta.tamaño_pagina
        )

class ManejadorObtenerEstadisticasAfiliacion(ManejadorConsulta[ObtenerEstadisticasAfiliacion, Dict[str, Any]]):
    """
    Manejador para obtener estadísticas de afiliación
    Principio de Responsabilidad Única
    """
    
    def __init__(self, repositorio_consultas: RepositorioConsultasAfiliados):
        self._repositorio = repositorio_consultas
    
    async def handle(self, consulta: ObtenerEstadisticasAfiliacion) -> Dict[str, Any]:
        """Maneja la obtención de estadísticas"""
        return await self._repositorio.obtener_estadisticas_afiliacion(
            fecha_inicio=consulta.fecha_inicio,
            fecha_fin=consulta.fecha_fin
        )

class ManejadorBuscarAfiliadosPorTexto(ManejadorConsulta[BuscarAfiliadosPorTexto, ResultadoPaginado]):
    """
    Manejador para búsqueda de texto libre
    Principio de Responsabilidad Única
    """
    
    def __init__(self, repositorio_consultas: RepositorioConsultasAfiliados):
        self._repositorio = repositorio_consultas
    
    async def handle(self, consulta: BuscarAfiliadosPorTexto) -> ResultadoPaginado:
        """Maneja la búsqueda por texto"""
        return await self._repositorio.buscar_afiliados_por_texto(
            texto_busqueda=consulta.texto_busqueda,
            pagina=consulta.pagina,
            tamaño_pagina=consulta.tamaño_pagina
        )

class ManejadorListarAfiliadosRecientes(ManejadorConsulta[ListarAfiliadosRecientes, ResultadoPaginado]):
    """
    Manejador para listar afiliados recientes
    Principio de Responsabilidad Única
    """
    
    def __init__(self, repositorio_consultas: RepositorioConsultasAfiliados):
        self._repositorio = repositorio_consultas
    
    async def handle(self, consulta: ListarAfiliadosRecientes) -> ResultadoPaginado:
        """Maneja el listado de afiliados recientes"""
        return await self._repositorio.listar_afiliados_recientes(
            dias=consulta.dias,
            pagina=consulta.pagina,
            tamaño_pagina=consulta.tamaño_pagina
        )

class ManejadorObtenerHistorialEstados(ManejadorConsulta[ObtenerHistorialEstados, List[Dict[str, Any]]]):
    """
    Manejador para obtener historial de estados
    Principio de Responsabilidad Única
    """
    
    def __init__(self, repositorio_consultas: RepositorioConsultasAfiliados):
        self._repositorio = repositorio_consultas
    
    async def handle(self, consulta: ObtenerHistorialEstados) -> List[Dict[str, Any]]:
        """Maneja la obtención del historial de estados"""
        return await self._repositorio.obtener_historial_estados(consulta.afiliado_id)