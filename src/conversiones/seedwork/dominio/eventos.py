"""
Eventos de dominio específicos para el microservicio Conversiones
Implementa Event Sourcing y principios DDD
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, TypeVar, Type
from enum import Enum
import uuid
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion

E = TypeVar('E', bound='EventoDominio')

# Base para eventos de dominio (compatible con versión existente)
@dataclass(frozen=True)
class EventoDominio(ABC):
    """
    Base abstracta para todos los eventos de dominio
    Principio de Responsabilidad Única - representa un cambio en el estado del dominio
    Compatible con interfaz existente pero extendida para enterprise
    """
    nombre: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    fecha: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Extensiones enterprise
    agregado_id: str = ""
    agregado_tipo: str = ""
    version_agregado: int = 1
    metadatos: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def siguiente_id(cls) -> uuid.UUID:
        return uuid.uuid4()

    @property
    def id_str(self) -> str:
        """Retorna el ID como string para compatibilidad"""
        return str(self.id)

    def encadenar(self: E, nuevo_evento_cls: Type[E], **kwargs) -> E:
        """Crea un nuevo evento que desciende de este preservando correlation/causation"""
        base_corr = self.correlation_id or str(self.id)
        return nuevo_evento_cls(
            correlation_id=base_corr,
            causation_id=str(self.id),
            **kwargs
        )

    def __post_init__(self):
        if not self.correlation_id:
            object.__setattr__(self, 'correlation_id', str(self.id))

# Estados específicos para el dominio de Conversiones
class EstadoConversion(Enum):
    PENDIENTE = "pendiente"
    VALIDANDO = "validando"
    VALIDA = "valida"
    RECHAZADA = "rechazada"
    PROCESANDO = "procesando"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

class TipoConversion(Enum):
    VENTA = "venta"
    LEAD = "lead"
    REGISTRO = "registro"
    SUSCRIPCION = "suscripcion"
    DESCARGA = "descarga"

class EstadoComision(Enum):
    PENDIENTE = "pendiente"
    CALCULADA = "calculada"
    APLICADA = "aplicada"
    PAGADA = "pagada"
    CANCELADA = "cancelada"

# Eventos específicos de Conversión
@dataclass(frozen=True)
class ConversionIniciada(EventoDominio):
    """Evento: Se ha iniciado una nueva conversión"""
    conversion_id: str = ""
    campana_id: str = ""
    afiliado_id: str = ""
    usuario_id: str = ""
    tipo_conversion: TipoConversion = TipoConversion.VENTA
    valor_conversion: float = 0.0
    moneda: str = "USD"
    datos_tracking: Dict[str, Any] = field(default_factory=dict)
    fuente: str = ""
    ip_usuario: Optional[str] = None
    user_agent: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'ConversionIniciada')
        object.__setattr__(self, 'agregado_tipo', 'Conversion')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.conversion_id)

@dataclass(frozen=True)
class ConversionValidada(EventoDominio):
    """Evento: La conversión ha sido validada exitosamente"""
    conversion_id: str = ""
    validador_id: str = ""
    reglas_aplicadas: List[str] = field(default_factory=list)
    puntuacion_fraude: float = 0.0
    detalles_validacion: Dict[str, Any] = field(default_factory=dict)
    tiempo_validacion_ms: int = 0
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'ConversionValidada')
        object.__setattr__(self, 'agregado_tipo', 'Conversion')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.conversion_id)

@dataclass(frozen=True)
class ConversionRechazada(EventoDominio):
    """Evento: La conversión ha sido rechazada"""
    conversion_id: str = ""
    razon_rechazo: str = ""
    codigo_rechazo: str = ""
    validador_id: str = ""
    reglas_violadas: List[str] = field(default_factory=list)
    puede_reintentar: bool = False
    detalles_rechazo: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'ConversionRechazada')
        object.__setattr__(self, 'agregado_tipo', 'Conversion')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.conversion_id)

@dataclass(frozen=True)
class ConversionCompletada(EventoDominio):
    """Evento: La conversión se ha completado exitosamente"""
    conversion_id: str = ""
    valor_final: float = 0.0
    fecha_completado: datetime = field(default_factory=datetime.now)
    procesador_id: str = ""
    tiempo_total_procesamiento_ms: int = 0
    estadisticas_procesamiento: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'ConversionCompletada')
        object.__setattr__(self, 'agregado_tipo', 'Conversion')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.conversion_id)

@dataclass(frozen=True)
class ConversionCancelada(EventoDominio):
    """Evento: La conversión ha sido cancelada"""
    conversion_id: str = ""
    razon_cancelacion: str = ""
    cancelado_por: str = ""
    puede_reactivar: bool = False
    datos_cancelacion: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'ConversionCancelada')
        object.__setattr__(self, 'agregado_tipo', 'Conversion')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.conversion_id)

# Eventos específicos de Comisión
@dataclass(frozen=True)
class ComisionCalculada(EventoDominio):
    """Evento: Se ha calculado una comisión para una conversión"""
    comision_id: str = ""
    conversion_id: str = ""
    afiliado_id: str = ""
    campana_id: str = ""
    monto_base: float = 0.0
    porcentaje_comision: float = 0.0
    monto_comision: float = 0.0
    moneda: str = "USD"
    tipo_comision: str = "porcentual"
    reglas_aplicadas: List[str] = field(default_factory=list)
    detalles_calculo: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'ComisionCalculada')
        object.__setattr__(self, 'agregado_tipo', 'Comision')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.comision_id)

@dataclass(frozen=True)
class ComisionAplicada(EventoDominio):
    """Evento: La comisión ha sido aplicada a la cuenta del afiliado"""
    comision_id: str = ""
    afiliado_id: str = ""
    monto_aplicado: float = 0.0
    balance_anterior: float = 0.0
    balance_nuevo: float = 0.0
    fecha_aplicacion: datetime = field(default_factory=datetime.now)
    referencia_transaccion: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'ComisionAplicada')
        object.__setattr__(self, 'agregado_tipo', 'Comision')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.comision_id)

@dataclass(frozen=True)
class ComisionCancelada(EventoDominio):
    """Evento: La comisión ha sido cancelada"""
    comision_id: str = ""
    conversion_id: str = ""
    afiliado_id: str = ""
    monto_cancelado: float = 0.0
    razon_cancelacion: str = ""
    reversar_aplicacion: bool = False
    detalles_cancelacion: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'ComisionCancelada')
        object.__setattr__(self, 'agregado_tipo', 'Comision')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.comision_id)

@dataclass(frozen=True)
class ComisionPagada(EventoDominio):
    """Evento: La comisión ha sido pagada al afiliado"""
    comision_id: str = ""
    afiliado_id: str = ""
    monto_pagado: float = 0.0
    metodo_pago: str = ""
    referencia_pago: str = ""
    fecha_pago: datetime = field(default_factory=datetime.now)
    detalles_pago: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'ComisionPagada')
        object.__setattr__(self, 'agregado_tipo', 'Comision')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.comision_id)

# Eventos de cambio de estado
@dataclass(frozen=True)
class EstadoConversionCambiado(EventoDominio):
    """Evento: El estado de una conversión ha cambiado"""
    conversion_id: str = ""
    estado_anterior: EstadoConversion = EstadoConversion.PENDIENTE
    estado_nuevo: EstadoConversion = EstadoConversion.PENDIENTE
    razon_cambio: str = ""
    cambiado_por: str = ""
    datos_adicionales: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'EstadoConversionCambiado')
        object.__setattr__(self, 'agregado_tipo', 'Conversion')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.conversion_id)

@dataclass(frozen=True)
class EstadoComisionCambiado(EventoDominio):
    """Evento: El estado de una comisión ha cambiado"""
    comision_id: str = ""
    estado_anterior: EstadoComision = EstadoComision.PENDIENTE
    estado_nuevo: EstadoComision = EstadoComision.PENDIENTE
    razon_cambio: str = ""
    cambiado_por: str = ""
    datos_adicionales: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'nombre', 'EstadoComisionCambiado')
        object.__setattr__(self, 'agregado_tipo', 'Comision')
        if not self.agregado_id:
            object.__setattr__(self, 'agregado_id', self.comision_id)

# Interface para manejadores de eventos de dominio
class ManejadorEventoDominio(ABC):
    """Interface base para manejadores de eventos de dominio"""
    
    @abstractmethod
    async def manejar(self, evento: EventoDominio) -> None:
        """Maneja el evento de dominio"""
        pass
    
    @abstractmethod
    def puede_manejar(self, tipo_evento: type) -> bool:
        """Determina si puede manejar este tipo de evento"""
        pass

# Despachador de eventos de dominio
class DespachadorEventosDominio:
    """Despachador centralizado de eventos de dominio"""
    
    def __init__(self):
        self._manejadores: Dict[type, List[ManejadorEventoDominio]] = {}
    
    def registrar_manejador(self, tipo_evento: type, manejador: ManejadorEventoDominio) -> None:
        """Registra manejador para tipo de evento específico"""
        if tipo_evento not in self._manejadores:
            self._manejadores[tipo_evento] = []
        self._manejadores[tipo_evento].append(manejador)
    
    async def despachar(self, evento: EventoDominio) -> None:
        """Despacha evento a todos los manejadores registrados"""
        tipo_evento = type(evento)
        manejadores = self._manejadores.get(tipo_evento, [])
        
        for manejador in manejadores:
            try:
                await manejador.manejar(evento)
            except Exception as e:
                print(f"Error manejando evento {tipo_evento.__name__}: {str(e)}")

# Store de eventos para Event Sourcing
class EventStore(ABC):
    """Interface para almacenar eventos de dominio"""
    
    @abstractmethod
    async def guardar_evento(self, evento: EventoDominio) -> None:
        """Guarda evento en el store"""
        pass
    
    @abstractmethod
    async def obtener_eventos_agregado(self, agregado_id: str, 
                                     desde_version: int = 0) -> List[EventoDominio]:
        """Obtiene eventos de un agregado específico"""
        pass

# Factory para crear eventos
class FactoriaEventosDominio:
    """Factory para crear eventos de dominio específicos"""
    
    @staticmethod
    def crear_conversion_iniciada(conversion_id: str, campana_id: str, afiliado_id: str,
                                usuario_id: str, tipo_conversion: TipoConversion,
                                valor_conversion: float, **kwargs) -> ConversionIniciada:
        """Crea evento ConversionIniciada"""
        return ConversionIniciada(
            conversion_id=conversion_id,
            campana_id=campana_id,
            afiliado_id=afiliado_id,
            usuario_id=usuario_id,
            tipo_conversion=tipo_conversion,
            valor_conversion=valor_conversion,
            **kwargs
        )
    
    @staticmethod
    def crear_comision_calculada(comision_id: str, conversion_id: str, afiliado_id: str,
                               monto_base: float, porcentaje_comision: float,
                               monto_comision: float, **kwargs) -> ComisionCalculada:
        """Crea evento ComisionCalculada"""
        return ComisionCalculada(
            comision_id=comision_id,
            conversion_id=conversion_id,
            afiliado_id=afiliado_id,
            monto_base=monto_base,
            porcentaje_comision=porcentaje_comision,
            monto_comision=monto_comision,
            **kwargs
        )