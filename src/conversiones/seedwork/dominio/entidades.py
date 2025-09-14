"""
Entidades específicas del dominio de Conversiones
Implementa agregados Conversion y Comision con DDD y principios SOLID
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .eventos import (
    EventoDominio, ConversionIniciada, ConversionValidada, ConversionRechazada,
    ConversionCompletada, ConversionCancelada, ComisionCalculada, ComisionAplicada,
    ComisionCancelada, ComisionPagada, EstadoConversionCambiado, EstadoComisionCambiado,
    EstadoConversion, EstadoComision, TipoConversion
)
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion
from datetime import datetime
import uuid
from abc import ABC, abstractmethod
from enum import Enum

@dataclass
class Entidad: 
    """Clase base para todas las entidades del dominio"""
    id: uuid.UUID = field(hash=True)
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    fecha_creacion: datetime = field(default=datetime.now())
    fecha_actualizacion: datetime = field(default=datetime.now())

    @classmethod
    def siguiente_id(cls) -> uuid.UUID:
        return uuid.uuid4()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: uuid.UUID) -> None:
        if not IdEntidadEsInmutable(self).es_valido():
            raise IdDebeSerInmutableExcepcion()
        self._id = self.siguiente_id()

@dataclass
class AgregacionRaiz(Entidad):
    """Clase base para agregados raíz con manejo de eventos"""
    eventos: list[EventoDominio] = field(default_factory=list)
    
    def agregar_evento(self, evento: EventoDominio): 
        self.eventos.append(evento)
    
    def limpiar_eventos(self):
        self.eventos = list()

# Objetos Valor para Conversiones
@dataclass(frozen=True)
class DatosTracking:
    """Objeto valor para datos de tracking de conversiones"""
    ip_usuario: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None
    datos_adicionales: Dict[str, Any] = field(default_factory=dict)
    
    def es_valido(self) -> bool:
        """Valida que los datos de tracking sean coherentes"""
        return self.ip_usuario is not None and len(self.ip_usuario.strip()) > 0

@dataclass(frozen=True)
class ValorMonetario:
    """Objeto valor para representar montos monetarios"""
    monto: float
    moneda: str = "USD"
    
    def __post_init__(self):
        if self.monto < 0:
            raise ValueError("El monto no puede ser negativo")
        if not self.moneda or len(self.moneda) != 3:
            raise ValueError("La moneda debe ser un código ISO de 3 caracteres")
    
    def es_cero(self) -> bool:
        return abs(self.monto) < 0.01
    
    def es_positivo(self) -> bool:
        return self.monto > 0.01
    
    def sumar(self, otro: 'ValorMonetario') -> 'ValorMonetario':
        if self.moneda != otro.moneda:
            raise ValueError("No se pueden sumar montos de diferentes monedas")
        return ValorMonetario(self.monto + otro.monto, self.moneda)
    
    def restar(self, otro: 'ValorMonetario') -> 'ValorMonetario':
        if self.moneda != otro.moneda:
            raise ValueError("No se pueden restar montos de diferentes monedas")
        return ValorMonetario(self.monto - otro.monto, self.moneda)
    
    def multiplicar_por(self, factor: float) -> 'ValorMonetario':
        return ValorMonetario(self.monto * factor, self.moneda)

@dataclass(frozen=True)
class PorcentajeComision:
    """Objeto valor para porcentajes de comisión"""
    valor: float
    
    def __post_init__(self):
        if not (0 <= self.valor <= 100):
            raise ValueError("El porcentaje debe estar entre 0 y 100")
    
    def aplicar_a(self, monto: ValorMonetario) -> ValorMonetario:
        """Aplica el porcentaje al monto dado"""
        factor = self.valor / 100.0
        return monto.multiplicar_por(factor)

@dataclass(frozen=True)
class IdentificadorConversion:
    """Objeto valor para identificadores de conversión"""
    valor: str
    
    def __post_init__(self):
        if not self.valor or not self.valor.strip():
            raise ValueError("El identificador de conversión no puede estar vacío")
        if len(self.valor) > 50:
            raise ValueError("El identificador de conversión no puede exceder 50 caracteres")

@dataclass(frozen=True)
class IdentificadorComision:
    """Objeto valor para identificadores de comisión"""
    valor: str
    
    def __post_init__(self):
        if not self.valor or not self.valor.strip():
            raise ValueError("El identificador de comisión no puede estar vacío")
        if len(self.valor) > 50:
            raise ValueError("El identificador de comisión no puede exceder 50 caracteres")

# Reglas de dominio para Conversiones
class ReglaValidacionConversion(ABC):
    """Interface para reglas de validación de conversiones"""
    
    @abstractmethod
    def es_valida(self, conversion: 'Conversion') -> bool:
        pass
    
    @abstractmethod
    def mensaje_error(self) -> str:
        pass

class ReglaMontoMinimo(ReglaValidacionConversion):
    """Regla: El monto de conversión debe superar un mínimo"""
    
    def __init__(self, monto_minimo: float = 1.0):
        self.monto_minimo = monto_minimo
    
    def es_valida(self, conversion: 'Conversion') -> bool:
        return conversion.valor_conversion.monto >= self.monto_minimo
    
    def mensaje_error(self) -> str:
        return f"El monto de conversión debe ser mayor a {self.monto_minimo}"

class ReglaAfiliadoValido(ReglaValidacionConversion):
    """Regla: El afiliado debe existir y estar activo"""
    
    def __init__(self, afiliados_validos: List[str]):
        self.afiliados_validos = afiliados_validos
    
    def es_valida(self, conversion: 'Conversion') -> bool:
        return conversion.afiliado_id in self.afiliados_validos
    
    def mensaje_error(self) -> str:
        return "El afiliado no es válido o no está activo"

# Agregado Conversion
@dataclass
class Conversion(AgregacionRaiz):
    """
    Agregado raíz para Conversiones
    Encapsula las reglas de negocio y garantiza invariantes
    """
    # Identificadores
    conversion_id: str = ""
    campana_id: str = ""
    afiliado_id: str = ""
    usuario_id: str = ""
    
    # Datos de la conversión
    tipo_conversion: TipoConversion = TipoConversion.VENTA
    valor_conversion: ValorMonetario = field(default_factory=lambda: ValorMonetario(0.0))
    estado: EstadoConversion = EstadoConversion.PENDIENTE
    
    # Datos de tracking
    datos_tracking: DatosTracking = field(default_factory=DatosTracking)
    fuente: str = ""
    
    # Validación y procesamiento
    validada: bool = False
    fecha_validacion: Optional[datetime] = None
    validador_id: Optional[str] = None
    reglas_aplicadas: List[str] = field(default_factory=list)
    
    # Completado
    fecha_completado: Optional[datetime] = None
    procesador_id: Optional[str] = None
    
    # Metadatos
    metadatos: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    
    def iniciar_conversion(self, 
                          conversion_id: str,
                          campana_id: str,
                          afiliado_id: str,
                          usuario_id: str,
                          tipo_conversion: TipoConversion,
                          valor: ValorMonetario,
                          datos_tracking: DatosTracking,
                          fuente: str = "") -> None:
        """Inicia una nueva conversión"""
        
        # Validaciones de negocio
        if not conversion_id or not conversion_id.strip():
            raise ValueError("El ID de conversión es obligatorio")
        
        if not campana_id or not campana_id.strip():
            raise ValueError("El ID de campaña es obligatorio")
        
        if not afiliado_id or not afiliado_id.strip():
            raise ValueError("El ID de afiliado es obligatorio")
        
        if not valor.es_positivo():
            raise ValueError("El valor de conversión debe ser positivo")
        
        if not datos_tracking.es_valido():
            raise ValueError("Los datos de tracking son inválidos")
        
        # Cambiar estado y datos
        self.conversion_id = conversion_id
        self.campana_id = campana_id
        self.afiliado_id = afiliado_id
        self.usuario_id = usuario_id
        self.tipo_conversion = tipo_conversion
        self.valor_conversion = valor
        self.datos_tracking = datos_tracking
        self.fuente = fuente
        self.estado = EstadoConversion.PENDIENTE
        self.fecha_actualizacion = datetime.now()
        
        # Agregar evento de dominio
        evento = ConversionIniciada(
            conversion_id=conversion_id,
            campana_id=campana_id,
            afiliado_id=afiliado_id,
            usuario_id=usuario_id,
            tipo_conversion=tipo_conversion,
            valor_conversion=valor.monto,
            moneda=valor.moneda,
            datos_tracking=datos_tracking.__dict__,
            fuente=fuente,
            ip_usuario=datos_tracking.ip_usuario,
            user_agent=datos_tracking.user_agent
        )
        self.agregar_evento(evento)
    
    def validar(self, validador_id: str, reglas: List[ReglaValidacionConversion]) -> bool:
        """Valida la conversión aplicando reglas de negocio"""
        
        if self.estado != EstadoConversion.PENDIENTE:
            raise ValueError("Solo se pueden validar conversiones pendientes")
        
        # Aplicar reglas de validación
        reglas_violadas = []
        for regla in reglas:
            if not regla.es_valida(self):
                reglas_violadas.append(regla.mensaje_error())
        
        if reglas_violadas:
            # Conversión rechazada
            self.estado = EstadoConversion.RECHAZADA
            self.fecha_actualizacion = datetime.now()
            
            evento = ConversionRechazada(
                conversion_id=self.conversion_id,
                razon_rechazo="Reglas de validación violadas",
                codigo_rechazo="VALIDATION_FAILED",
                validador_id=validador_id,
                reglas_violadas=reglas_violadas,
                puede_reintentar=False
            )
            self.agregar_evento(evento)
            return False
        
        # Conversión validada
        self.validada = True
        self.fecha_validacion = datetime.now()
        self.validador_id = validador_id
        self.reglas_aplicadas = [type(regla).__name__ for regla in reglas]
        self.estado = EstadoConversion.VALIDA
        self.fecha_actualizacion = datetime.now()
        
        evento = ConversionValidada(
            conversion_id=self.conversion_id,
            validador_id=validador_id,
            reglas_aplicadas=self.reglas_aplicadas,
            puntuacion_fraude=0.0,
            tiempo_validacion_ms=0
        )
        self.agregar_evento(evento)
        return True
    
    def completar(self, procesador_id: str, valor_final: Optional[ValorMonetario] = None) -> None:
        """Completa la conversión"""
        
        if self.estado not in [EstadoConversion.VALIDA, EstadoConversion.PROCESANDO]:
            raise ValueError("Solo se pueden completar conversiones válidas o en procesamiento")
        
        valor_utilizado = valor_final or self.valor_conversion
        
        self.estado = EstadoConversion.COMPLETADA
        self.fecha_completado = datetime.now()
        self.procesador_id = procesador_id
        self.valor_conversion = valor_utilizado
        self.fecha_actualizacion = datetime.now()
        
        evento = ConversionCompletada(
            conversion_id=self.conversion_id,
            valor_final=valor_utilizado.monto,
            fecha_completado=self.fecha_completado,
            procesador_id=procesador_id
        )
        self.agregar_evento(evento)
    
    def cancelar(self, razon: str, cancelado_por: str) -> None:
        """Cancela la conversión"""
        
        if self.estado == EstadoConversion.COMPLETADA:
            raise ValueError("No se puede cancelar una conversión completada")
        
        estado_anterior = self.estado
        self.estado = EstadoConversion.CANCELADA
        self.fecha_actualizacion = datetime.now()
        
        evento = ConversionCancelada(
            conversion_id=self.conversion_id,
            razon_cancelacion=razon,
            cancelado_por=cancelado_por,
            puede_reactivar=estado_anterior in [EstadoConversion.PENDIENTE, EstadoConversion.VALIDA]
        )
        self.agregar_evento(evento)
    
    def puede_generar_comision(self) -> bool:
        """Determina si la conversión puede generar comisión"""
        return (self.estado == EstadoConversion.COMPLETADA and 
                self.validada and 
                self.valor_conversion.es_positivo())

# Agregado Comision
@dataclass
class Comision(AgregacionRaiz):
    """
    Agregado raíz para Comisiones
    Maneja el cálculo y aplicación de comisiones
    """
    # Identificadores
    comision_id: str = ""
    conversion_id: str = ""
    afiliado_id: str = ""
    campana_id: str = ""
    
    # Datos de la comisión
    monto_base: ValorMonetario = field(default_factory=lambda: ValorMonetario(0.0))
    porcentaje_comision: PorcentajeComision = field(default_factory=lambda: PorcentajeComision(0.0))
    monto_comision: ValorMonetario = field(default_factory=lambda: ValorMonetario(0.0))
    tipo_comision: str = "porcentual"
    estado: EstadoComision = EstadoComision.PENDIENTE
    
    # Cálculo
    reglas_aplicadas: List[str] = field(default_factory=list)
    fecha_calculo: Optional[datetime] = None
    
    # Aplicación
    fecha_aplicacion: Optional[datetime] = None
    balance_anterior: ValorMonetario = field(default_factory=lambda: ValorMonetario(0.0))
    balance_nuevo: ValorMonetario = field(default_factory=lambda: ValorMonetario(0.0))
    
    # Pago
    fecha_pago: Optional[datetime] = None
    metodo_pago: Optional[str] = None
    referencia_pago: Optional[str] = None
    
    # Metadatos
    metadatos: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    
    def calcular_comision(self,
                         comision_id: str,
                         conversion: Conversion,
                         porcentaje: PorcentajeComision,
                         tipo_comision: str = "porcentual") -> None:
        """Calcula la comisión basada en la conversión"""
        
        if not conversion.puede_generar_comision():
            raise ValueError("La conversión no puede generar comisión")
        
        if not comision_id or not comision_id.strip():
            raise ValueError("El ID de comisión es obligatorio")
        
        # Calcular monto de comisión
        monto_calculado = porcentaje.aplicar_a(conversion.valor_conversion)
        
        # Establecer datos
        self.comision_id = comision_id
        self.conversion_id = conversion.conversion_id
        self.afiliado_id = conversion.afiliado_id
        self.campana_id = conversion.campana_id
        self.monto_base = conversion.valor_conversion
        self.porcentaje_comision = porcentaje
        self.monto_comision = monto_calculado
        self.tipo_comision = tipo_comision
        self.estado = EstadoComision.CALCULADA
        self.fecha_calculo = datetime.now()
        self.fecha_actualizacion = datetime.now()
        
        # Agregar evento
        evento = ComisionCalculada(
            comision_id=comision_id,
            conversion_id=conversion.conversion_id,
            afiliado_id=conversion.afiliado_id,
            campana_id=conversion.campana_id,
            monto_base=conversion.valor_conversion.monto,
            porcentaje_comision=porcentaje.valor,
            monto_comision=monto_calculado.monto,
            moneda=monto_calculado.moneda,
            tipo_comision=tipo_comision
        )
        self.agregar_evento(evento)
    
    def aplicar(self, balance_anterior: ValorMonetario) -> ValorMonetario:
        """Aplica la comisión al balance del afiliado"""
        
        if self.estado != EstadoComision.CALCULADA:
            raise ValueError("Solo se pueden aplicar comisiones calculadas")
        
        if balance_anterior.moneda != self.monto_comision.moneda:
            raise ValueError("Las monedas del balance y comisión deben coincidir")
        
        # Calcular nuevo balance
        nuevo_balance = balance_anterior.sumar(self.monto_comision)
        
        # Actualizar estado
        self.estado = EstadoComision.APLICADA
        self.fecha_aplicacion = datetime.now()
        self.balance_anterior = balance_anterior
        self.balance_nuevo = nuevo_balance
        self.fecha_actualizacion = datetime.now()
        
        # Agregar evento
        evento = ComisionAplicada(
            comision_id=self.comision_id,
            afiliado_id=self.afiliado_id,
            monto_aplicado=self.monto_comision.monto,
            balance_anterior=balance_anterior.monto,
            balance_nuevo=nuevo_balance.monto,
            fecha_aplicacion=self.fecha_aplicacion
        )
        self.agregar_evento(evento)
        
        return nuevo_balance
    
    def marcar_como_pagada(self, metodo_pago: str, referencia_pago: str) -> None:
        """Marca la comisión como pagada"""
        
        if self.estado != EstadoComision.APLICADA:
            raise ValueError("Solo se pueden marcar como pagadas las comisiones aplicadas")
        
        self.estado = EstadoComision.PAGADA
        self.fecha_pago = datetime.now()
        self.metodo_pago = metodo_pago
        self.referencia_pago = referencia_pago
        self.fecha_actualizacion = datetime.now()
        
        evento = ComisionPagada(
            comision_id=self.comision_id,
            afiliado_id=self.afiliado_id,
            monto_pagado=self.monto_comision.monto,
            metodo_pago=metodo_pago,
            referencia_pago=referencia_pago,
            fecha_pago=self.fecha_pago
        )
        self.agregar_evento(evento)
    
    def cancelar(self, razon: str, reversar_aplicacion: bool = False) -> Optional[ValorMonetario]:
        """Cancela la comisión"""
        
        if self.estado == EstadoComision.PAGADA:
            raise ValueError("No se puede cancelar una comisión ya pagada")
        
        estado_anterior = self.estado
        self.estado = EstadoComision.CANCELADA
        self.fecha_actualizacion = datetime.now()
        
        # Si estaba aplicada y se requiere reversar
        balance_revertido = None
        if estado_anterior == EstadoComision.APLICADA and reversar_aplicacion:
            balance_revertido = self.balance_anterior
        
        evento = ComisionCancelada(
            comision_id=self.comision_id,
            conversion_id=self.conversion_id,
            afiliado_id=self.afiliado_id,
            monto_cancelado=self.monto_comision.monto,
            razon_cancelacion=razon,
            reversar_aplicacion=reversar_aplicacion
        )
        self.agregar_evento(evento)
        
        return balance_revertido