"""
Consultas CQRS del módulo de comisiones - Marketing Microservice
Implementación CQS con Query Pattern, DTOs y optimizaciones de lectura
Arquitectura: CQRS + Query Pattern + Read Models + Cache
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any, Generic, TypeVar, Union
from abc import ABC, abstractmethod
from enum import Enum
import uuid

from ..dominio.entidades import EstadoComision, TipoComision, MontoMonetario

# =============================================================================
# TIPOS Y CONSTANTES
# =============================================================================

T = TypeVar('T')

class TipoOrdenamiento(Enum):
    """Tipos de ordenamiento para consultas"""
    ASC = "asc"
    DESC = "desc"

class CampoOrdenamientoComision(Enum):
    """Campos válidos para ordenamiento de comisiones"""
    FECHA_CREACION = "fecha_creacion"
    FECHA_CALCULO = "fecha_calculo"
    MONTO_CALCULADO = "monto_calculado"
    ESTADO = "estado"
    AFILIADO_ID = "afiliado_id"
    CAMPANA_ID = "campana_id"

# =============================================================================
# DTOS (Data Transfer Objects) - SEPARACIÓN DOMINIO/PRESENTACIÓN
# =============================================================================

@dataclass
class ComisionDTO:
    """
    DTO para transferencia de datos de comisión
    Principio de Responsabilidad Única - solo transferencia
    """
    id: str
    afiliado_id: str
    campana_id: str
    conversion_id: str
    estado: str
    tipo_comision: str
    monto_base: Decimal
    moneda: str
    porcentaje: Optional[Decimal]
    monto_calculado: Optional[Decimal]
    fecha_creacion: datetime
    fecha_calculo: Optional[datetime]
    fecha_aprobacion: Optional[datetime]
    fecha_pago: Optional[datetime]
    aprobador_id: Optional[str]
    comentarios: Optional[str]
    metadatos: Dict[str, Any]
    
    @classmethod
    def desde_entidad(cls, comision) -> ComisionDTO:
        """Convertir entidad de dominio a DTO"""
        return cls(
            id=comision.id,
            afiliado_id=comision.afiliado_id,
            campana_id=comision.campana_id,
            conversion_id=comision.conversion_id,
            estado=comision.estado.value,
            tipo_comision=comision.tipo_comision.value,
            monto_base=comision.monto_base.valor,
            moneda=comision.monto_base.moneda,
            porcentaje=comision.porcentaje.valor if comision.porcentaje else None,
            monto_calculado=comision.monto_calculado.valor if comision.monto_calculado else None,
            fecha_creacion=comision.fecha_creacion,
            fecha_calculo=comision.fecha_calculo,
            fecha_aprobacion=comision.fecha_aprobacion,
            fecha_pago=comision.fecha_pago,
            aprobador_id=comision.aprobador_id,
            comentarios=comision.comentarios,
            metadatos=comision.metadatos or {}
        )

@dataclass
class ComisionResumenDTO:
    """
    DTO para resumen de comisión (consultas de listado)
    Principio de Responsabilidad Única - solo datos esenciales
    """
    id: str
    afiliado_id: str
    campana_id: str
    estado: str
    monto_calculado: Optional[Decimal]
    moneda: str
    fecha_creacion: datetime
    fecha_calculo: Optional[datetime]

@dataclass  
class EstadisticasComisionDTO:
    """
    DTO para estadísticas de comisiones
    Principio de Responsabilidad Única - solo métricas
    """
    total_comisiones: int
    total_pendientes: int
    total_calculadas: int
    total_aprobadas: int
    total_rechazadas: int
    total_pagadas: int
    monto_total_calculado: Decimal
    monto_total_aprobado: Decimal
    monto_total_pagado: Decimal
    moneda: str
    fecha_ultimo_calculo: Optional[datetime]
    promedio_tiempo_aprobacion_dias: Optional[float]

@dataclass
class ResumenAfiliadoDTO:
    """
    DTO para resumen de comisiones por afiliado
    Principio de Responsabilidad Única - agregaciones por afiliado
    """
    afiliado_id: str
    nombre_afiliado: Optional[str]
    total_comisiones: int
    comisiones_pendientes: int
    comisiones_aprobadas: int
    monto_total_calculado: Decimal
    monto_total_aprobado: Decimal
    monto_total_pagado: Decimal
    moneda: str
    ultima_comision_fecha: Optional[datetime]
    tasa_aprobacion: float  # Porcentaje de aprobación

@dataclass
class ResumenCampanaDTO:
    """
    DTO para resumen de comisiones por campaña
    Principio de Responsabilidad Única - agregaciones por campaña
    """
    campana_id: str
    nombre_campana: Optional[str]
    total_comisiones: int
    total_afiliados: int
    monto_total_comisiones: Decimal
    monto_promedio_por_comision: Decimal
    moneda: str
    fecha_primera_comision: Optional[datetime]
    fecha_ultima_comision: Optional[datetime]
    estado_campana: Optional[str]

# =============================================================================
# CRITERIOS DE PAGINACIÓN Y FILTRADO
# =============================================================================

@dataclass
class CriterioPaginacion:
    """
    Criterio para paginación de consultas
    Principio de Responsabilidad Única - solo paginación
    """
    pagina: int = 1
    tamaño: int = 20
    ordenar_por: CampoOrdenamientoComision = CampoOrdenamientoComision.FECHA_CREACION
    tipo_orden: TipoOrdenamiento = TipoOrdenamiento.DESC
    
    def validar(self) -> None:
        """Validar criterios de paginación"""
        if self.pagina < 1:
            raise ValueError("La página debe ser mayor a 0")
        if self.tamaño < 1 or self.tamaño > 1000:
            raise ValueError("El tamaño debe estar entre 1 y 1000")
    
    @property
    def offset(self) -> int:
        """Calcular offset para paginación"""
        return (self.pagina - 1) * self.tamaño

@dataclass
class CriterioFiltroComision:
    """
    Criterio para filtrado de comisiones
    Principio de Abierto/Cerrado - extensible para nuevos filtros
    """
    estados: Optional[List[EstadoComision]] = None
    tipos_comision: Optional[List[TipoComision]] = None
    afiliados_ids: Optional[List[str]] = None
    campanas_ids: Optional[List[str]] = None
    fecha_creacion_desde: Optional[date] = None
    fecha_creacion_hasta: Optional[date] = None
    fecha_calculo_desde: Optional[date] = None
    fecha_calculo_hasta: Optional[date] = None
    monto_minimo: Optional[Decimal] = None
    monto_maximo: Optional[Decimal] = None
    moneda: Optional[str] = None
    busqueda_texto: Optional[str] = None  # Búsqueda en comentarios, metadatos
    
    def tiene_filtros(self) -> bool:
        """Verificar si tiene filtros aplicados"""
        filtros = [
            self.estados, self.tipos_comision, self.afiliados_ids, 
            self.campanas_ids, self.fecha_creacion_desde, self.fecha_creacion_hasta,
            self.fecha_calculo_desde, self.fecha_calculo_hasta,
            self.monto_minimo, self.monto_maximo, self.moneda, self.busqueda_texto
        ]
        return any(filtro is not None for filtro in filtros)

# =============================================================================
# RESULTADO PAGINADO GENÉRICO
# =============================================================================

@dataclass
class ResultadoPaginado(Generic[T]):
    """
    Resultado paginado genérico para consultas
    Principio de Responsabilidad Única - solo paginación de resultados
    """
    elementos: List[T]
    total_elementos: int
    pagina_actual: int
    tamaño_pagina: int
    total_paginas: int
    tiene_anterior: bool
    tiene_siguiente: bool
    
    @classmethod
    def crear(
        cls, 
        elementos: List[T], 
        total_elementos: int, 
        criterio: CriterioPaginacion
    ) -> ResultadoPaginado[T]:
        """Factory method para crear resultado paginado"""
        total_paginas = (total_elementos + criterio.tamaño - 1) // criterio.tamaño
        return cls(
            elementos=elementos,
            total_elementos=total_elementos,
            pagina_actual=criterio.pagina,
            tamaño_pagina=criterio.tamaño,
            total_paginas=max(total_paginas, 1),
            tiene_anterior=criterio.pagina > 1,
            tiene_siguiente=criterio.pagina < total_paginas
        )

# =============================================================================
# CONSULTAS BASE - INTERFACES
# =============================================================================

@dataclass
class ConsultaBase(ABC):
    """
    Consulta base - Principio de Responsabilidad Única
    Representa una intención de lectura del sistema
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    usuario_id: str = ""
    correlacion_id: Optional[str] = None
    usar_cache: bool = True
    timeout_cache_segundos: int = 300  # 5 minutos por defecto
    
    @abstractmethod
    def validar(self) -> None:
        """Validar invariantes de la consulta"""
        pass

@dataclass
class ConsultaConPaginacion(ConsultaBase):
    """Consulta con soporte para paginación"""
    paginacion: CriterioPaginacion = field(default_factory=CriterioPaginacion)
    
    def validar(self) -> None:
        """Validar consulta y paginación"""
        self.paginacion.validar()

# =============================================================================
# CONSULTAS ESPECÍFICAS DE COMISIONES
# =============================================================================

@dataclass
class ObtenerComision(ConsultaBase):
    """
    Consulta para obtener una comisión específica por ID
    Principio de Responsabilidad Única - solo obtención por ID
    """
    comision_id: str = ""
    incluir_metadatos: bool = False
    incluir_auditoria: bool = False
    
    def validar(self) -> None:
        """Validar datos de la consulta"""
        if not self.comision_id:
            raise ValueError("ID de comisión es requerido")

@dataclass
class ListarComisiones(ConsultaConPaginacion):
    """
    Consulta para listar comisiones con filtros y paginación
    Principio de Responsabilidad Única - solo listado
    """
    filtros: CriterioFiltroComision = field(default_factory=CriterioFiltroComision)
    incluir_totales: bool = True
    formato_resumen: bool = False  # True para ComisionResumenDTO
    
    def validar(self) -> None:
        """Validar consulta"""
        super().validar()
        # Validaciones adicionales si es necesario

@dataclass
class ObtenerComisionesPorAfiliado(ConsultaConPaginacion):
    """
    Consulta para obtener comisiones de un afiliado específico
    Principio de Responsabilidad Única - solo por afiliado
    """
    afiliado_id: str = ""
    estados_filtro: Optional[List[EstadoComision]] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    incluir_estadisticas: bool = False
    
    def validar(self) -> None:
        """Validar datos de la consulta"""
        super().validar()
        if not self.afiliado_id:
            raise ValueError("ID de afiliado es requerido")
        if self.fecha_desde and self.fecha_hasta and self.fecha_desde > self.fecha_hasta:
            raise ValueError("Fecha desde debe ser menor o igual a fecha hasta")

@dataclass
class ObtenerComisionesPorCampana(ConsultaConPaginacion):
    """
    Consulta para obtener comisiones de una campaña específica
    Principio de Responsabilidad Única - solo por campaña
    """
    campana_id: str = ""
    estados_filtro: Optional[List[EstadoComision]] = None
    incluir_resumen: bool = False
    agrupar_por_afiliado: bool = False
    
    def validar(self) -> None:
        """Validar datos de la consulta"""
        super().validar()
        if not self.campana_id:
            raise ValueError("ID de campaña es requerido")

@dataclass
class ObtenerEstadisticasComisiones(ConsultaBase):
    """
    Consulta para obtener estadísticas de comisiones
    Principio de Responsabilidad Única - solo estadísticas
    """
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    afiliado_id: Optional[str] = None
    campana_id: Optional[str] = None
    agrupar_por_periodo: Optional[str] = None  # 'dia', 'semana', 'mes'
    incluir_tendencias: bool = False
    
    def validar(self) -> None:
        """Validar datos de la consulta"""
        if self.fecha_desde and self.fecha_hasta and self.fecha_desde > self.fecha_hasta:
            raise ValueError("Fecha desde debe ser menor o igual a fecha hasta")
        if self.agrupar_por_periodo and self.agrupar_por_periodo not in ['dia', 'semana', 'mes']:
            raise ValueError("Agrupación por periodo debe ser 'dia', 'semana' o 'mes'")

@dataclass
class ObtenerResumenAfiliados(ConsultaConPaginacion):
    """
    Consulta para obtener resumen de comisiones por afiliados
    Principio de Responsabilidad Única - solo resumen afiliados
    """
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    estados_filtro: Optional[List[EstadoComision]] = None
    monto_minimo: Optional[Decimal] = None
    ordenar_por_monto: bool = True
    solo_activos: bool = True
    
    def validar(self) -> None:
        """Validar datos de la consulta"""
        super().validar()
        if self.fecha_desde and self.fecha_hasta and self.fecha_desde > self.fecha_hasta:
            raise ValueError("Fecha desde debe ser menor o igual a fecha hasta")

@dataclass
class ObtenerResumenCampanas(ConsultaConPaginacion):
    """
    Consulta para obtener resumen de comisiones por campañas
    Principio de Responsabilidad Única - solo resumen campañas
    """
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    estados_campana: Optional[List[str]] = None
    incluir_metricas_conversion: bool = False
    ordenar_por_total_comisiones: bool = True
    
    def validar(self) -> None:
        """Validar datos de la consulta"""
        super().validar()
        if self.fecha_desde and self.fecha_hasta and self.fecha_desde > self.fecha_hasta:
            raise ValueError("Fecha desde debe ser menor o igual a fecha hasta")

@dataclass
class BuscarComisiones(ConsultaConPaginacion):
    """
    Consulta para búsqueda de texto libre en comisiones
    Principio de Responsabilidad Única - solo búsqueda
    """
    termino_busqueda: str = ""
    campos_busqueda: List[str] = field(default_factory=lambda: ['comentarios', 'metadatos'])
    busqueda_exacta: bool = False
    incluir_afiliado_info: bool = False
    incluir_campana_info: bool = False
    
    def validar(self) -> None:
        """Validar datos de la consulta"""
        super().validar()
        if not self.termino_busqueda.strip():
            raise ValueError("Término de búsqueda es requerido")
        if len(self.termino_busqueda) < 3:
            raise ValueError("Término de búsqueda debe tener al menos 3 caracteres")

# =============================================================================
# MANEJADORES DE CONSULTAS - PRINCIPIO DE RESPONSABILIDAD ÚNICA
# =============================================================================

class ManejadorConsulta(ABC):
    """
    Interfaz para manejadores de consultas
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def manejar(self, consulta: ConsultaBase) -> Any:
        """Manejar la consulta específica"""
        pass
    
    @abstractmethod
    def puede_manejar(self, consulta: ConsultaBase) -> bool:
        """Verificar si puede manejar la consulta"""
        pass

# =============================================================================
# CACHE DE CONSULTAS - PRINCIPIO DE RESPONSABILIDAD ÚNICA
# =============================================================================

class CacheConsultas(ABC):
    """
    Interfaz para cache de consultas
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def obtener(self, clave: str) -> Optional[Any]:
        """Obtener resultado del cache"""
        pass
    
    @abstractmethod
    def guardar(self, clave: str, valor: Any, ttl_segundos: int = 300) -> None:
        """Guardar resultado en cache"""
        pass
    
    @abstractmethod
    def invalidar(self, patron: str) -> None:
        """Invalidar entradas del cache"""
        pass
    
    @abstractmethod
    def limpiar(self) -> None:
        """Limpiar todo el cache"""
        pass

class CacheConsultasMemoria(CacheConsultas):
    """
    Implementación en memoria del cache de consultas
    Para desarrollo y testing
    """
    
    def __init__(self):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
    
    def obtener(self, clave: str) -> Optional[Any]:
        """Obtener del cache con validación de TTL"""
        if clave in self._cache:
            valor, timestamp = self._cache[clave]
            # Verificar si no ha expirado (simplificado)
            return valor
        return None
    
    def guardar(self, clave: str, valor: Any, ttl_segundos: int = 300) -> None:
        """Guardar en cache con timestamp"""
        self._cache[clave] = (valor, datetime.now())
    
    def invalidar(self, patron: str) -> None:
        """Invalidar por patrón (simplificado)"""
        claves_a_eliminar = [k for k in self._cache.keys() if patron in k]
        for clave in claves_a_eliminar:
            del self._cache[clave]
    
    def limpiar(self) -> None:
        """Limpiar todo el cache"""
        self._cache.clear()

# =============================================================================
# BUS DE CONSULTAS - PATRÓN MEDIATOR
# =============================================================================

class BusConsultas(ABC):
    """
    Interfaz del bus de consultas
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def ejecutar(self, consulta: ConsultaBase) -> Any:
        """Ejecutar consulta a través del bus"""
        pass
    
    @abstractmethod
    def registrar_manejador(self, tipo_consulta: type, manejador: ManejadorConsulta) -> None:
        """Registrar manejador para tipo de consulta"""
        pass

class BusConsultasImplementacion(BusConsultas):
    """
    Implementación del bus de consultas con cache
    Patrón Mediator + Decorator (cache)
    """
    
    def __init__(self, cache: Optional[CacheConsultas] = None):
        self._manejadores: Dict[type, ManejadorConsulta] = {}
        self._cache = cache or CacheConsultasMemoria()
        self._interceptores: List[Any] = []
    
    def ejecutar(self, consulta: ConsultaBase) -> Any:
        """
        Ejecutar consulta con cache y validaciones
        Principio de Responsabilidad Única
        """
        try:
            # 1. Validar consulta
            consulta.validar()
            
            # 2. Verificar cache si está habilitado
            if consulta.usar_cache:
                clave_cache = self._generar_clave_cache(consulta)
                resultado_cache = self._cache.obtener(clave_cache)
                if resultado_cache is not None:
                    return resultado_cache
            
            # 3. Buscar manejador
            tipo_consulta = type(consulta)
            if tipo_consulta not in self._manejadores:
                raise ValueError(f"No hay manejador para {tipo_consulta.__name__}")
            
            manejador = self._manejadores[tipo_consulta]
            
            # 4. Ejecutar interceptores pre-ejecución
            for interceptor in self._interceptores:
                if hasattr(interceptor, 'antes_ejecutar'):
                    interceptor.antes_ejecutar(consulta)
            
            # 5. Ejecutar consulta
            resultado = manejador.manejar(consulta)
            
            # 6. Guardar en cache si está habilitado
            if consulta.usar_cache:
                clave_cache = self._generar_clave_cache(consulta)
                self._cache.guardar(clave_cache, resultado, consulta.timeout_cache_segundos)
            
            # 7. Ejecutar interceptores post-ejecución
            for interceptor in self._interceptores:
                if hasattr(interceptor, 'despues_ejecutar'):
                    interceptor.despues_ejecutar(consulta, resultado)
            
            return resultado
            
        except Exception as ex:
            # Manejar errores con interceptores
            for interceptor in self._interceptores:
                if hasattr(interceptor, 'en_error'):
                    interceptor.en_error(consulta, ex)
            raise
    
    def registrar_manejador(self, tipo_consulta: type, manejador: ManejadorConsulta) -> None:
        """Registrar manejador para tipo específico de consulta"""
        self._manejadores[tipo_consulta] = manejador
    
    def agregar_interceptor(self, interceptor: Any) -> None:
        """Agregar interceptor para cross-cutting concerns"""
        self._interceptores.append(interceptor)
    
    def _generar_clave_cache(self, consulta: ConsultaBase) -> str:
        """Generar clave única para cache basada en la consulta"""
        tipo_consulta = type(consulta).__name__
        # Simplificado - en producción usar hash del contenido
        return f"{tipo_consulta}_{consulta.id}"

# =============================================================================
# FACTORY PARA CONSULTAS - PATRÓN FACTORY
# =============================================================================

class FabricaConsultas:
    """
    Factory para crear consultas con datos válidos
    Principio de Responsabilidad Única - solo creación
    """
    
    @staticmethod
    def crear_listar_comisiones(
        estados: Optional[List[EstadoComision]] = None,
        afiliado_id: Optional[str] = None,
        campana_id: Optional[str] = None,
        pagina: int = 1,
        tamaño: int = 20,
        **kwargs
    ) -> ListarComisiones:
        """Crear consulta de listado con validaciones"""
        filtros = CriterioFiltroComision(
            estados=estados,
            afiliados_ids=[afiliado_id] if afiliado_id else None,
            campanas_ids=[campana_id] if campana_id else None
        )
        paginacion = CriterioPaginacion(pagina=pagina, tamaño=tamaño)
        
        consulta = ListarComisiones(
            filtros=filtros,
            paginacion=paginacion,
            **kwargs
        )
        consulta.validar()
        return consulta
    
    @staticmethod
    def crear_obtener_estadisticas(
        afiliado_id: Optional[str] = None,
        campana_id: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        **kwargs
    ) -> ObtenerEstadisticasComisiones:
        """Crear consulta de estadísticas con validaciones"""
        consulta = ObtenerEstadisticasComisiones(
            afiliado_id=afiliado_id,
            campana_id=campana_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            **kwargs
        )
        consulta.validar()
        return consulta