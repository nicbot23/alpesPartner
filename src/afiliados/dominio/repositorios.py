"""
Interfaces de repositorio específicas para el dominio de Afiliados
Implementa principios SOLID y Repository Pattern
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..seedwork.dominio.entidades import RepositorioEscritura, RepositorioLectura, RepositorioAgregado
from ..seedwork.aplicacion.consultas import RepositorioConsultas, ResultadoPaginado
from .entidades import Afiliado, EstadoAfiliado, DocumentoIdentidad

class RepositorioAfiliados(RepositorioAgregado[Afiliado]):
    """
    Interface específica para repositorio de Afiliados
    Extiende el repositorio base con operaciones específicas del dominio
    """
    
    @abstractmethod
    async def obtener_por_documento(self, documento: DocumentoIdentidad) -> Optional[Afiliado]:
        """Obtiene un afiliado por su documento de identidad"""
        pass
    
    @abstractmethod
    async def obtener_por_email(self, email: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su email"""
        pass
    
    @abstractmethod
    async def listar_por_estado(self, estado: EstadoAfiliado) -> List[Afiliado]:
        """Lista afiliados por estado"""
        pass
    
    @abstractmethod
    async def contar_por_estado(self, estado: EstadoAfiliado) -> int:
        """Cuenta afiliados por estado"""
        pass
    
    @abstractmethod
    async def existe_documento(self, documento: DocumentoIdentidad) -> bool:
        """Verifica si ya existe un afiliado con ese documento"""
        pass
    
    @abstractmethod
    async def existe_email(self, email: str) -> bool:
        """Verifica si ya existe un afiliado con ese email"""
        pass

class RepositorioConsultasAfiliados(RepositorioConsultas):
    """
    Interface para consultas optimizadas de Afiliados (lado Query de CQRS)
    Principio de Segregación de Interfaces
    """
    
    @abstractmethod
    async def buscar_afiliados(
        self,
        filtros: Dict[str, Any],
        pagina: int = 1,
        tamaño_pagina: int = 20
    ) -> ResultadoPaginado:
        """
        Busca afiliados con filtros complejos
        Soporta filtros por: nombre, documento, email, estado, fecha_afiliacion
        """
        pass
    
    @abstractmethod
    async def obtener_afiliado_detalle(self, afiliado_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene detalle completo de un afiliado incluyendo historial"""
        pass
    
    @abstractmethod
    async def listar_afiliados_activos(
        self,
        pagina: int = 1,
        tamaño_pagina: int = 20
    ) -> ResultadoPaginado:
        """Lista afiliados activos paginados"""
        pass
    
    @abstractmethod
    async def obtener_estadisticas_afiliacion(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de afiliación por periodo
        Retorna: total por estado, afiliaciones por día, etc.
        """
        pass
    
    @abstractmethod
    async def buscar_afiliados_por_texto(
        self,
        texto_busqueda: str,
        pagina: int = 1,
        tamaño_pagina: int = 20
    ) -> ResultadoPaginado:
        """
        Búsqueda de texto libre en nombre, documento, email
        """
        pass
    
    @abstractmethod
    async def listar_afiliados_recientes(
        self,
        dias: int = 7,
        pagina: int = 1,
        tamaño_pagina: int = 20
    ) -> ResultadoPaginado:
        """Lista afiliados registrados en los últimos N días"""
        pass
    
    @abstractmethod
    async def obtener_historial_estados(
        self,
        afiliado_id: str
    ) -> List[Dict[str, Any]]:
        """Obtiene historial de cambios de estado de un afiliado"""
        pass