"""
Comandos CQRS del módulo de comisiones - Marketing Microservice
Implementación SOLID con Command Pattern y validaciones enterprise
Arquitectura: CQRS + Domain-Driven Design + Command Pattern
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import uuid

from ..dominio.entidades import (
    Comision, EstadoComision, TipoComision, MontoMonetario, 
    PorcentajeComision, ConfiguracionComision, MetodoCalculo,
    ExcepcionDominio, EventoDominio
)

# =============================================================================
# EXCEPCIONES DE COMANDOS
# =============================================================================

class ExcepcionComando(ExcepcionDominio):
    """Excepción base para comandos de comisiones"""
    pass

class ComandoInvalidoError(ExcepcionComando):
    """Error cuando un comando tiene datos inválidos"""
    pass

class ComisionNoExisteError(ExcepcionComando):
    """Error cuando se intenta operar sobre comisión inexistente"""
    pass

class EstadoComisionInvalidoError(ExcepcionComando):
    """Error cuando el estado de la comisión no permite la operación"""
    pass

class PermisosInsuficientesError(ExcepcionComando):
    """Error cuando el usuario no tiene permisos para la operación"""
    pass

# =============================================================================
# INTERFACES DE COMANDOS - PRINCIPIO DE SEGREGACIÓN DE INTERFACES
# =============================================================================

@dataclass
class ComandoBase(ABC):
    """
    Comando base - Principio de Responsabilidad Única
    Representa una intención de cambio en el sistema
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    usuario_id: str = ""
    correlacion_id: Optional[str] = None
    
    @abstractmethod
    def validar(self) -> None:
        """Validar invariantes del comando"""
        pass

@dataclass
class ComandoConRespuesta(ComandoBase):
    """Comando que espera respuesta"""
    
    @abstractmethod
    def obtener_tipo_respuesta(self) -> type:
        """Tipo de respuesta esperada"""
        pass

# =============================================================================
# COMANDOS ESPECÍFICOS DE COMISIONES
# =============================================================================

@dataclass
class CrearComision(ComandoConRespuesta):
    """
    Comando para crear nueva comisión
    Principio de Responsabilidad Única - solo creación
    """
    afiliado_id: str = ""
    campana_id: str = ""
    conversion_id: str = ""
    monto_base: Decimal = field(default_factory=lambda: Decimal('0'))
    moneda: str = "COP"
    tipo_comision: TipoComision = TipoComision.FIJA
    porcentaje: Optional[Decimal] = None
    configuracion: Optional[Dict[str, Any]] = None
    metadatos: Dict[str, Any] = field(default_factory=dict)
    
    def validar(self) -> None:
        """Validar datos del comando"""
        if not self.afiliado_id:
            raise ComandoInvalidoError("ID del afiliado es requerido")
        
        if not self.campana_id:
            raise ComandoInvalidoError("ID de la campaña es requerido")
            
        if not self.conversion_id:
            raise ComandoInvalidoError("ID de conversión es requerido")
            
        if self.monto_base <= 0:
            raise ComandoInvalidoError("Monto base debe ser mayor a cero")
            
        if self.tipo_comision == TipoComision.PORCENTUAL and not self.porcentaje:
            raise ComandoInvalidoError("Porcentaje es requerido para comisión porcentual")
            
        if self.porcentaje and (self.porcentaje < 0 or self.porcentaje > 100):
            raise ComandoInvalidoError("Porcentaje debe estar entre 0 y 100")
    
    def obtener_tipo_respuesta(self) -> type:
        return str  # ID de la comisión creada

@dataclass
class ActualizarComision(ComandoConRespuesta):
    """
    Comando para actualizar comisión existente
    Principio de Responsabilidad Única - solo actualización
    """
    comision_id: str = ""
    monto_base: Optional[Decimal] = None
    porcentaje: Optional[Decimal] = None
    configuracion: Optional[Dict[str, Any]] = None
    metadatos: Optional[Dict[str, Any]] = None
    motivo_actualizacion: str = ""
    
    def validar(self) -> None:
        """Validar datos del comando"""
        if not self.comision_id:
            raise ComandoInvalidoError("ID de comisión es requerido")
            
        if not self.motivo_actualizacion:
            raise ComandoInvalidoError("Motivo de actualización es requerido")
            
        # Validar que al menos un campo sea actualizado
        campos_actualizacion = [
            self.monto_base, self.porcentaje, 
            self.configuracion, self.metadatos
        ]
        if all(campo is None for campo in campos_actualizacion):
            raise ComandoInvalidoError("Debe especificar al menos un campo para actualizar")
            
        if self.monto_base and self.monto_base <= 0:
            raise ComandoInvalidoError("Monto base debe ser mayor a cero")
            
        if self.porcentaje and (self.porcentaje < 0 or self.porcentaje > 100):
            raise ComandoInvalidoError("Porcentaje debe estar entre 0 y 100")
    
    def obtener_tipo_respuesta(self) -> type:
        return bool  # Éxito de la actualización

@dataclass
class CalcularComision(ComandoConRespuesta):
    """
    Comando para calcular monto de comisión
    Principio de Responsabilidad Única - solo cálculo
    """
    comision_id: str = ""
    forzar_recalculo: bool = False
    configuracion_personalizada: Optional[ConfiguracionComision] = None
    
    def validar(self) -> None:
        """Validar datos del comando"""
        if not self.comision_id:
            raise ComandoInvalidoError("ID de comisión es requerido")
    
    def obtener_tipo_respuesta(self) -> type:
        return MontoMonetario  # Monto calculado

@dataclass  
class AprobarComision(ComandoConRespuesta):
    """
    Comando para aprobar comisión calculada
    Principio de Responsabilidad Única - solo aprobación
    """
    comision_id: str = ""
    aprobador_id: str = ""
    comentarios: str = ""
    metadatos_aprobacion: Dict[str, Any] = field(default_factory=dict)
    
    def validar(self) -> None:
        """Validar datos del comando"""
        if not self.comision_id:
            raise ComandoInvalidoError("ID de comisión es requerido")
            
        if not self.aprobador_id:
            raise ComandoInvalidoError("ID del aprobador es requerido")
    
    def obtener_tipo_respuesta(self) -> type:
        return bool  # Éxito de la aprobación

@dataclass
class RechazarComision(ComandoConRespuesta):
    """
    Comando para rechazar comisión
    Principio de Responsabilidad Única - solo rechazo
    """
    comision_id: str = ""
    rechazador_id: str = ""
    motivo_rechazo: str = ""
    comentarios: str = ""
    metadatos_rechazo: Dict[str, Any] = field(default_factory=dict)
    
    def validar(self) -> None:
        """Validar datos del comando"""
        if not self.comision_id:
            raise ComandoInvalidoError("ID de comisión es requerido")
            
        if not self.rechazador_id:
            raise ComandoInvalidoError("ID del rechazador es requerido")
            
        if not self.motivo_rechazo:
            raise ComandoInvalidoError("Motivo de rechazo es requerido")
    
    def obtener_tipo_respuesta(self) -> type:
        return bool  # Éxito del rechazo

@dataclass
class PagarComision(ComandoConRespuesta):
    """
    Comando para marcar comisión como pagada
    Principio de Responsabilidad Única - solo pago
    """
    comision_id: str = ""
    metodo_pago: str = ""
    referencia_pago: str = ""
    fecha_pago: Optional[datetime] = None
    monto_pagado: Optional[Decimal] = None
    moneda_pago: str = "COP"
    metadatos_pago: Dict[str, Any] = field(default_factory=dict)
    
    def validar(self) -> None:
        """Validar datos del comando"""
        if not self.comision_id:
            raise ComandoInvalidoError("ID de comisión es requerido")
            
        if not self.metodo_pago:
            raise ComandoInvalidoError("Método de pago es requerido")
            
        if not self.referencia_pago:
            raise ComandoInvalidoError("Referencia de pago es requerida")
            
        if self.monto_pagado and self.monto_pagado <= 0:
            raise ComandoInvalidoError("Monto pagado debe ser mayor a cero")
    
    def obtener_tipo_respuesta(self) -> type:
        return bool  # Éxito del pago

@dataclass
class AnularComision(ComandoConRespuesta):
    """
    Comando para anular comisión
    Principio de Responsabilidad Única - solo anulación
    """
    comision_id: str = ""
    motivo_anulacion: str = ""
    anulador_id: str = ""
    revertir_pago: bool = False
    metadatos_anulacion: Dict[str, Any] = field(default_factory=dict)
    
    def validar(self) -> None:
        """Validar datos del comando"""
        if not self.comision_id:
            raise ComandoInvalidoError("ID de comisión es requerido")
            
        if not self.motivo_anulacion:
            raise ComandoInvalidoError("Motivo de anulación es requerido")
            
        if not self.anulador_id:
            raise ComandoInvalidoError("ID del anulador es requerido")
    
    def obtener_tipo_respuesta(self) -> type:
        return bool  # Éxito de la anulación

# =============================================================================
# COMANDOS DE LOTE - OPERACIONES MASIVAS
# =============================================================================

@dataclass
class ProcesarComisionesLote(ComandoConRespuesta):
    """
    Comando para procesar múltiples comisiones en lote
    Principio de Abierto/Cerrado - extensible para diferentes tipos de lote
    """
    campana_id: Optional[str] = None
    afiliado_id: Optional[str] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    tipo_procesamiento: str = "calculo"  # calculo, aprobacion, pago
    configuracion_lote: Dict[str, Any] = field(default_factory=dict)
    
    def validar(self) -> None:
        """Validar datos del comando"""
        # Validar que al menos un filtro esté presente
        filtros = [self.campana_id, self.afiliado_id, self.fecha_desde, self.fecha_hasta]
        if all(filtro is None for filtro in filtros):
            raise ComandoInvalidoError("Debe especificar al menos un filtro para el lote")
            
        if self.tipo_procesamiento not in ["calculo", "aprobacion", "pago"]:
            raise ComandoInvalidoError("Tipo de procesamiento inválido")
            
        if self.fecha_desde and self.fecha_hasta and self.fecha_desde > self.fecha_hasta:
            raise ComandoInvalidoError("Fecha desde debe ser menor o igual a fecha hasta")
    
    def obtener_tipo_respuesta(self) -> type:
        return Dict[str, Any]  # Resultado del procesamiento en lote

# =============================================================================
# MANEJADORES DE COMANDOS - PRINCIPIO DE RESPONSABILIDAD ÚNICA
# =============================================================================

class ManejadorComando(ABC):
    """
    Interfaz para manejadores de comandos
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def manejar(self, comando: ComandoBase) -> Any:
        """Manejar el comando específico"""
        pass
    
    @abstractmethod
    def puede_manejar(self, comando: ComandoBase) -> bool:
        """Verificar si puede manejar el comando"""
        pass

class ValidadorComando(ABC):
    """
    Interfaz para validadores de comandos
    Principio de Segregación de Interfaces
    """
    
    @abstractmethod
    def validar(self, comando: ComandoBase) -> None:
        """Validar comando específico"""
        pass

# =============================================================================
# BUS DE COMANDOS - PATRÓN MEDIATOR
# =============================================================================

class BusComandos(ABC):
    """
    Interfaz del bus de comandos
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def ejecutar(self, comando: ComandoBase) -> Any:
        """Ejecutar comando a través del bus"""
        pass
    
    @abstractmethod
    def registrar_manejador(self, tipo_comando: type, manejador: ManejadorComando) -> None:
        """Registrar manejador para tipo de comando"""
        pass

class BusComandosImplementacion(BusComandos):
    """
    Implementación del bus de comandos
    Patrón Mediator + Registry
    """
    
    def __init__(self):
        self._manejadores: Dict[type, ManejadorComando] = {}
        self._validadores: List[ValidadorComando] = []
        self._interceptores: List[Any] = []  # Para logging, métricas, etc.
    
    def ejecutar(self, comando: ComandoBase) -> Any:
        """
        Ejecutar comando con validaciones e interceptores
        Principio de Responsabilidad Única
        """
        try:
            # 1. Validar comando
            comando.validar()
            
            # 2. Validaciones adicionales
            for validador in self._validadores:
                validador.validar(comando)
            
            # 3. Buscar manejador
            tipo_comando = type(comando)
            if tipo_comando not in self._manejadores:
                raise ComandoInvalidoError(f"No hay manejador para {tipo_comando.__name__}")
            
            manejador = self._manejadores[tipo_comando]
            
            # 4. Ejecutar interceptores pre-ejecución
            for interceptor in self._interceptores:
                if hasattr(interceptor, 'antes_ejecutar'):
                    interceptor.antes_ejecutar(comando)
            
            # 5. Ejecutar comando
            resultado = manejador.manejar(comando)
            
            # 6. Ejecutar interceptores post-ejecución
            for interceptor in self._interceptores:
                if hasattr(interceptor, 'despues_ejecutar'):
                    interceptor.despues_ejecutar(comando, resultado)
            
            return resultado
            
        except Exception as ex:
            # Manejar errores con interceptores
            for interceptor in self._interceptores:
                if hasattr(interceptor, 'en_error'):
                    interceptor.en_error(comando, ex)
            raise
    
    def registrar_manejador(self, tipo_comando: type, manejador: ManejadorComando) -> None:
        """Registrar manejador para tipo específico de comando"""
        self._manejadores[tipo_comando] = manejador
    
    def agregar_validador(self, validador: ValidadorComando) -> None:
        """Agregar validador global"""
        self._validadores.append(validador)
    
    def agregar_interceptor(self, interceptor: Any) -> None:
        """Agregar interceptor para cross-cutting concerns"""
        self._interceptores.append(interceptor)

# =============================================================================
# FACTORY PARA COMANDOS - PATRÓN FACTORY
# =============================================================================

class FabricaComandos:
    """
    Factory para crear comandos con datos válidos
    Principio de Responsabilidad Única - solo creación
    """
    
    @staticmethod
    def crear_comando_crear_comision(
        afiliado_id: str,
        campana_id: str, 
        conversion_id: str,
        monto_base: Decimal,
        tipo_comision: TipoComision,
        porcentaje: Optional[Decimal] = None,
        usuario_id: str = "",
        **kwargs
    ) -> CrearComision:
        """Crear comando de creación con validaciones"""
        comando = CrearComision(
            afiliado_id=afiliado_id,
            campana_id=campana_id,
            conversion_id=conversion_id,
            monto_base=monto_base,
            tipo_comision=tipo_comision,
            porcentaje=porcentaje,
            usuario_id=usuario_id,
            **kwargs
        )
        comando.validar()
        return comando
    
    @staticmethod
    def crear_comando_aprobar_comision(
        comision_id: str,
        aprobador_id: str,
        comentarios: str = "",
        **kwargs
    ) -> AprobarComision:
        """Crear comando de aprobación con validaciones"""
        comando = AprobarComision(
            comision_id=comision_id,
            aprobador_id=aprobador_id,
            comentarios=comentarios,
            **kwargs
        )
        comando.validar()
        return comando

# =============================================================================
# EVENTOS DE COMANDOS EJECUTADOS
# =============================================================================

@dataclass
class ComandoEjecutado(EventoDominio):
    """Evento cuando un comando es ejecutado exitosamente"""
    comando_tipo: str = ""
    comando_id: str = ""
    resultado: Any = None
    duracion_ms: int = 0

@dataclass
class ComandoFallo(EventoDominio):
    """Evento cuando un comando falla"""
    comando_tipo: str = ""
    comando_id: str = ""
    error: str = ""
    stack_trace: Optional[str] = None