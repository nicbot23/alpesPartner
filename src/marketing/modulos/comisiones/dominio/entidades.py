"""
Entidades del módulo de comisiones - Marketing Microservice
Implementación DDD con agregados, entidades, objetos de valor y servicios de dominio
Arquitectura: Domain-Driven Design + SOLID Principles
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import List, Optional, Dict, Set, Union, Any
from abc import ABC, abstractmethod
import uuid

# Clases base locales para evitar problemas de importación
@dataclass
class EventoDominio(ABC):
    """Evento de dominio base"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha: datetime = field(default_factory=datetime.now)

class ExcepcionDominio(Exception):
    """Excepción de dominio base"""
    pass

@dataclass  
class Entidad(ABC):
    """Entidad base"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    version: int = 1

@dataclass
class RaizAgregado(Entidad):
    """Raíz de agregado"""
    _eventos: List[EventoDominio] = field(default_factory=list, init=False)
    
    def agregar_evento(self, evento: EventoDominio):
        self._eventos.append(evento)
    
    def obtener_eventos(self) -> List[EventoDominio]:
        return self._eventos.copy()
    
    def limpiar_eventos(self):
        self._eventos.clear()

# Enums del dominio
class EstadoComision(Enum):
from typing import List, Optional, Dict, Set, Union, Any
from abc import ABC, abstractmethod
import uuid

# Clases base locales para evitar problemas de importación
@dataclass
class EventoDominio(ABC):
    """Evento de dominio base"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha: datetime = field(default_factory=datetime.now)

class ExcepcionDominio(Exception):
    """Excepción de dominio base"""
    pass

@dataclass  
class Entidad(ABC):
    """Entidad base"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    version: int = 1

@dataclass
class RaizAgregado(Entidad):
    """Raíz de agregado"""
    _eventos: List[EventoDominio] = field(default_factory=list, init=False)
    
    def agregar_evento(self, evento: EventoDominio):
        self._eventos.append(evento)
    
    def obtener_eventos(self) -> List[EventoDominio]:
        return self._eventos.copy()
    
    def limpiar_eventos(self):
        self._eventos.clear()
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional, Any
# Enums del dominio
class EstadoComision(Enum):
    PENDIENTE = "pendiente"
    CALCULADA = "calculada"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    PAGADA = "pagada"
    CANCELADA = "cancelada"

class TipoComision(Enum):
    PORCENTUAL = "porcentual"
    FIJA = "fija"
    ESCALONADA = "escalonada"
    HIBRIDA = "hibrida"

class MetodoCalculo(Enum):
    VALOR_BRUTO = "valor_bruto"
    VALOR_NETO = "valor_neto"
    MARGEN_CONTRIBUCION = "margen_contribucion"

class NivelAfiliado(Enum):
    BRONCE = "bronce"
    PLATA = "plata"
    ORO = "oro"
    PLATINO = "platino"
    DIAMANTE = "diamante"

# Excepciones del dominio
class ExcepcionComision(ExcepcionDominio):
    pass

class ComisionYaCalculada(ExcepcionComision):
    def __init__(self, comision_id: str):
        super().__init__(f"La comisión {comision_id} ya fue calculada")

class ComisionYaAprobada(ExcepcionComision):
    def __init__(self, comision_id: str):
        super().__init__(f"La comisión {comision_id} ya fue aprobada")

class MontoInvalido(ExcepcionComision):
    def __init__(self, monto: Decimal):
        super().__init__(f"Monto inválido: {monto}")

class PorcentajeInvalido(ExcepcionComision):
    def __init__(self, porcentaje: Decimal):
        super().__init__(f"Porcentaje inválido: {porcentaje}%")

class CampanaInactiva(ExcepcionComision):
    def __init__(self, campana_id: str):
        super().__init__(f"La campaña {campana_id} no está activa")

class AfiliadoInhabilitado(ExcepcionComision):
    def __init__(self, afiliado_id: str):
        super().__init__(f"El afiliado {afiliado_id} está inhabilitado")

# Objetos valor
@dataclass(frozen=True)
class MontoMonetario:
    """Objeto valor para representar montos monetarios"""
    valor: Decimal
    moneda: str = "USD"
    
    def __post_init__(self):
        if self.valor < 0:
            raise MontoInvalido(self.valor)
        if not self.moneda or len(self.moneda) != 3:
            raise ValueError("Moneda debe ser código ISO de 3 caracteres")
    
    @classmethod
    def cero(cls, moneda: str = "USD") -> 'MontoMonetario':
        return cls(Decimal("0.00"), moneda)
    
    @classmethod
    def desde_float(cls, valor: float, moneda: str = "USD") -> 'MontoMonetario':
        return cls(Decimal(str(valor)), moneda)
    
    def sumar(self, otro: 'MontoMonetario') -> 'MontoMonetario':
        if self.moneda != otro.moneda:
            raise ValueError("No se pueden sumar montos de diferentes monedas")
        return MontoMonetario(self.valor + otro.valor, self.moneda)
    
    def restar(self, otro: 'MontoMonetario') -> 'MontoMonetario':
        if self.moneda != otro.moneda:
            raise ValueError("No se pueden restar montos de diferentes monedas")
        resultado = self.valor - otro.valor
        if resultado < 0:
            raise MontoInvalido(resultado)
        return MontoMonetario(resultado, self.moneda)
    
    def multiplicar_por_porcentaje(self, porcentaje: Decimal) -> 'MontoMonetario':
        resultado = self.valor * (porcentaje / Decimal("100"))
        return MontoMonetario(resultado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), self.moneda)
    
    def es_mayor_que(self, otro: 'MontoMonetario') -> bool:
        if self.moneda != otro.moneda:
            raise ValueError("No se pueden comparar montos de diferentes monedas")
        return self.valor > otro.valor
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "valor": float(self.valor),
            "moneda": self.moneda
        }

@dataclass(frozen=True)
class PorcentajeComision:
    """Objeto valor para porcentajes de comisión"""
    valor: Decimal
    
    def __post_init__(self):
        if self.valor < 0 or self.valor > 100:
            raise PorcentajeInvalido(self.valor)
    
    @classmethod
    def desde_float(cls, valor: float) -> 'PorcentajeComision':
        return cls(Decimal(str(valor)))
    
    def aplicar_a_monto(self, monto: MontoMonetario) -> MontoMonetario:
        return monto.multiplicar_por_porcentaje(self.valor)
    
    def to_float(self) -> float:
        return float(self.valor)

@dataclass(frozen=True)
class ConfiguracionComision:
    """Configuración de comisión para una campaña"""
    tipo: TipoComision
    porcentaje_base: PorcentajeComision
    monto_fijo: Optional[MontoMonetario] = None
    metodo_calculo: MetodoCalculo = MetodoCalculo.VALOR_BRUTO
    monto_minimo: Optional[MontoMonetario] = None
    monto_maximo: Optional[MontoMonetario] = None
    escalones: Optional[List['EscalonComision']] = None
    
    def __post_init__(self):
        if self.tipo == TipoComision.FIJA and not self.monto_fijo:
            raise ValueError("Comisión fija requiere monto_fijo")
        if self.tipo == TipoComision.ESCALONADA and not self.escalones:
            raise ValueError("Comisión escalonada requiere escalones")

@dataclass(frozen=True)
class EscalonComision:
    """Escalón de comisión para comisiones escalonadas"""
    monto_desde: MontoMonetario
    monto_hasta: Optional[MontoMonetario]
    porcentaje: PorcentajeComision
    
    def aplica_para_monto(self, monto: MontoMonetario) -> bool:
        """Verifica si este escalón aplica para el monto dado"""
        if monto.moneda != self.monto_desde.moneda:
            return False
        
        if monto.valor < self.monto_desde.valor:
            return False
        
        if self.monto_hasta and monto.valor > self.monto_hasta.valor:
            return False
        
        return True

@dataclass(frozen=True)
class DatosConversion:
    """Datos de la conversión para calcular comisión"""
    id: str
    monto_bruto: MontoMonetario
    monto_neto: Optional[MontoMonetario] = None
    fecha_conversion: datetime = field(default_factory=datetime.now)
    metadatos: Dict[str, Any] = field(default_factory=dict)
    
    def obtener_monto_para_calculo(self, metodo: MetodoCalculo) -> MontoMonetario:
        """Obtiene el monto correcto según el método de cálculo"""
        if metodo == MetodoCalculo.VALOR_BRUTO:
            return self.monto_bruto
        elif metodo == MetodoCalculo.VALOR_NETO:
            return self.monto_neto or self.monto_bruto
        elif metodo == MetodoCalculo.MARGEN_CONTRIBUCION:
            margen = self.metadatos.get('margen_contribucion')
            if margen:
                return MontoMonetario.desde_float(margen, self.monto_bruto.moneda)
            return self.monto_bruto
        else:
            return self.monto_bruto

@dataclass(frozen=True)
class DatosAfiliado:
    """Datos del afiliado para calcular comisión"""
    id: str
    nivel: NivelAfiliado
    activo: bool
    fecha_registro: datetime
    configuracion_especial: Optional[ConfiguracionComision] = None
    multiplicador_nivel: Decimal = field(default_factory=lambda: Decimal("1.0"))
    
    def puede_recibir_comisiones(self) -> bool:
        """Verifica si el afiliado puede recibir comisiones"""
        return self.activo
    
    def obtener_multiplicador(self) -> Decimal:
        """Obtiene multiplicador según nivel del afiliado"""
        multiplicadores = {
            NivelAfiliado.BRONCE: Decimal("1.0"),
            NivelAfiliado.PLATA: Decimal("1.1"),
            NivelAfiliado.ORO: Decimal("1.25"),
            NivelAfiliado.PLATINO: Decimal("1.5"),
            NivelAfiliado.DIAMANTE: Decimal("2.0")
        }
        return multiplicadores.get(self.nivel, Decimal("1.0")) * self.multiplicador_nivel

# Eventos del dominio
@dataclass(frozen=True)
class ComisionCalculada(EventoDominio):
    comision_id: str
    campana_id: str
    afiliado_id: str
    conversion_id: str
    monto_comision: MontoMonetario
    porcentaje_aplicado: PorcentajeComision
    fecha_calculo: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "comision_id": self.comision_id,
            "campana_id": self.campana_id,
            "afiliado_id": self.afiliado_id,
            "conversion_id": self.conversion_id,
            "monto_comision": self.monto_comision.to_dict(),
            "porcentaje_aplicado": self.porcentaje_aplicado.to_float(),
            "fecha_calculo": self.fecha_calculo.isoformat()
        }

@dataclass(frozen=True)
class ComisionAprobada(EventoDominio):
    comision_id: str
    aprobada_por: str
    monto_final: MontoMonetario
    fecha_aprobacion: datetime = field(default_factory=datetime.now)
    comentarios: Optional[str] = None

@dataclass(frozen=True)
class ComisionRechazada(EventoDominio):
    comision_id: str
    rechazada_por: str
    motivo: str
    fecha_rechazo: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class ComisionPagada(EventoDominio):
    comision_id: str
    afiliado_id: str
    monto_pagado: MontoMonetario
    referencia_pago: str
    fecha_pago: datetime = field(default_factory=datetime.now)

# Servicios del dominio
class CalculadorComision:
    """Servicio de dominio para calcular comisiones"""
    
    @staticmethod
    def calcular(
        configuracion: ConfiguracionComision,
        datos_conversion: DatosConversion,
        datos_afiliado: DatosAfiliado
    ) -> MontoMonetario:
        """Calcula el monto de comisión"""
        
        # Verificar si el afiliado puede recibir comisiones
        if not datos_afiliado.puede_recibir_comisiones():
            raise AfiliadoInhabilitado(datos_afiliado.id)
        
        # Obtener monto base para cálculo
        monto_base = datos_conversion.obtener_monto_para_calculo(configuracion.metodo_calculo)
        
        # Calcular según tipo de comisión
        if configuracion.tipo == TipoComision.PORCENTUAL:
            monto_comision = configuracion.porcentaje_base.aplicar_a_monto(monto_base)
        
        elif configuracion.tipo == TipoComision.FIJA:
            monto_comision = configuracion.monto_fijo
        
        elif configuracion.tipo == TipoComision.ESCALONADA:
            monto_comision = CalculadorComision._calcular_escalonada(
                configuracion.escalones, monto_base
            )
        
        elif configuracion.tipo == TipoComision.HIBRIDA:
            # Combina porcentual + fijo
            monto_porcentual = configuracion.porcentaje_base.aplicar_a_monto(monto_base)
            monto_comision = monto_porcentual.sumar(configuracion.monto_fijo)
        
        else:
            raise ValueError(f"Tipo de comisión no soportado: {configuracion.tipo}")
        
        # Aplicar multiplicador por nivel de afiliado
        multiplicador = datos_afiliado.obtener_multiplicador()
        if multiplicador != Decimal("1.0"):
            monto_final = MontoMonetario(
                monto_comision.valor * multiplicador,
                monto_comision.moneda
            )
        else:
            monto_final = monto_comision
        
        # Aplicar límites mínimos y máximos
        if configuracion.monto_minimo and monto_final.valor < configuracion.monto_minimo.valor:
            monto_final = configuracion.monto_minimo
        
        if configuracion.monto_maximo and monto_final.valor > configuracion.monto_maximo.valor:
            monto_final = configuracion.monto_maximo
        
        return monto_final
    
    @staticmethod
    def _calcular_escalonada(escalones: List[EscalonComision], monto: MontoMonetario) -> MontoMonetario:
        """Calcula comisión escalonada"""
        for escalon in escalones:
            if escalon.aplica_para_monto(monto):
                return escalon.porcentaje.aplicar_a_monto(monto)
        
        # Si no encuentra escalón aplicable, usar el último
        if escalones:
            return escalones[-1].porcentaje.aplicar_a_monto(monto)
        
        return MontoMonetario.cero(monto.moneda)

class ValidadorComision:
    """Servicio de dominio para validar comisiones"""
    
    @staticmethod
    def validar_calculo(
        configuracion: ConfiguracionComision,
        datos_conversion: DatosConversion,
        datos_afiliado: DatosAfiliado
    ) -> List[str]:
        """Valida si se puede calcular la comisión"""
        errores = []
        
        if not datos_afiliado.activo:
            errores.append(f"Afiliado {datos_afiliado.id} no está activo")
        
        if datos_conversion.monto_bruto.valor <= 0:
            errores.append("Monto de conversión debe ser positivo")
        
        if configuracion.tipo == TipoComision.FIJA and not configuracion.monto_fijo:
            errores.append("Configuración de comisión fija requiere monto fijo")
        
        if configuracion.tipo == TipoComision.ESCALONADA and not configuracion.escalones:
            errores.append("Configuración escalonada requiere definir escalones")
        
        return errores

# Agregado Comision
@dataclass
class Comision(RaizAgregado):
    """Agregado raíz para comisiones"""
    
    # Datos de identificación
    campana_id: str
    afiliado_id: str
    conversion_id: str
    
    # Configuración y datos de cálculo
    configuracion: ConfiguracionComision
    datos_conversion: DatosConversion
    datos_afiliado: DatosAfiliado
    
    # Estado y cálculo
    estado: EstadoComision = EstadoComision.PENDIENTE
    monto_calculado: Optional[MontoMonetario] = None
    porcentaje_aplicado: Optional[PorcentajeComision] = None
    
    # Metadatos de procesamiento
    fecha_calculo: Optional[datetime] = None
    fecha_aprobacion: Optional[datetime] = None
    fecha_rechazo: Optional[datetime] = None
    fecha_pago: Optional[datetime] = None
    
    # Información de auditoría
    calculada_por: Optional[str] = None
    aprobada_por: Optional[str] = None
    rechazada_por: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    referencia_pago: Optional[str] = None
    
    # Observaciones y metadatos
    observaciones: Optional[str] = None
    metadatos: Dict[str, Any] = field(default_factory=dict)
    
    def calcular(self, calculada_por: str) -> None:
        """Calcula la comisión"""
        if self.estado != EstadoComision.PENDIENTE:
            raise ComisionYaCalculada(self.id)
        
        # Validar antes de calcular
        errores = ValidadorComision.validar_calculo(
            self.configuracion, self.datos_conversion, self.datos_afiliado
        )
        if errores:
            raise ExcepcionComision(f"Errores en validación: {', '.join(errores)}")
        
        # Calcular monto
        self.monto_calculado = CalculadorComision.calcular(
            self.configuracion, self.datos_conversion, self.datos_afiliado
        )
        
        # Determinar porcentaje aplicado
        if self.configuracion.tipo == TipoComision.PORCENTUAL:
            self.porcentaje_aplicado = self.configuracion.porcentaje_base
        else:
            # Para otros tipos, calcular porcentaje equivalente
            monto_base = self.datos_conversion.obtener_monto_para_calculo(
                self.configuracion.metodo_calculo
            )
            porcentaje_equiv = (self.monto_calculado.valor / monto_base.valor) * 100
            self.porcentaje_aplicado = PorcentajeComision(porcentaje_equiv)
        
        # Actualizar estado
        self.estado = EstadoComision.CALCULADA
        self.fecha_calculo = datetime.now()
        self.calculada_por = calculada_por
        
        # Agregar evento
        evento = ComisionCalculada(
            comision_id=self.id,
            campana_id=self.campana_id,
            afiliado_id=self.afiliado_id,
            conversion_id=self.conversion_id,
            monto_comision=self.monto_calculado,
            porcentaje_aplicado=self.porcentaje_aplicado,
            fecha_calculo=self.fecha_calculo
        )
        self.agregar_evento(evento)
    
    def aprobar(self, aprobada_por: str, monto_final: Optional[MontoMonetario] = None, 
                comentarios: Optional[str] = None) -> None:
        """Aprueba la comisión"""
        if self.estado != EstadoComision.CALCULADA:
            if self.estado == EstadoComision.APROBADA:
                raise ComisionYaAprobada(self.id)
            raise ExcepcionComision(f"Comisión debe estar calculada para aprobar. Estado actual: {self.estado}")
        
        # Usar monto calculado o monto ajustado
        monto_aprobado = monto_final or self.monto_calculado
        
        # Actualizar estado
        self.estado = EstadoComision.APROBADA
        self.fecha_aprobacion = datetime.now()
        self.aprobada_por = aprobada_por
        self.monto_calculado = monto_aprobado  # Actualizar con monto final
        if comentarios:
            self.observaciones = comentarios
        
        # Agregar evento
        evento = ComisionAprobada(
            comision_id=self.id,
            aprobada_por=aprobada_por,
            monto_final=monto_aprobado,
            fecha_aprobacion=self.fecha_aprobacion,
            comentarios=comentarios
        )
        self.agregar_evento(evento)
    
    def rechazar(self, rechazada_por: str, motivo: str) -> None:
        """Rechaza la comisión"""
        if self.estado not in [EstadoComision.CALCULADA, EstadoComision.PENDIENTE]:
            raise ExcepcionComision(f"No se puede rechazar comisión en estado {self.estado}")
        
        # Actualizar estado
        self.estado = EstadoComision.RECHAZADA
        self.fecha_rechazo = datetime.now()
        self.rechazada_por = rechazada_por
        self.motivo_rechazo = motivo
        
        # Agregar evento
        evento = ComisionRechazada(
            comision_id=self.id,
            rechazada_por=rechazada_por,
            motivo=motivo,
            fecha_rechazo=self.fecha_rechazo
        )
        self.agregar_evento(evento)
    
    def marcar_como_pagada(self, referencia_pago: str) -> None:
        """Marca la comisión como pagada"""
        if self.estado != EstadoComision.APROBADA:
            raise ExcepcionComision(f"Solo se pueden pagar comisiones aprobadas. Estado actual: {self.estado}")
        
        # Actualizar estado
        self.estado = EstadoComision.PAGADA
        self.fecha_pago = datetime.now()
        self.referencia_pago = referencia_pago
        
        # Agregar evento
        evento = ComisionPagada(
            comision_id=self.id,
            afiliado_id=self.afiliado_id,
            monto_pagado=self.monto_calculado,
            referencia_pago=referencia_pago,
            fecha_pago=self.fecha_pago
        )
        self.agregar_evento(evento)
    
    def cancelar(self, motivo: str) -> None:
        """Cancela la comisión"""
        if self.estado == EstadoComision.PAGADA:
            raise ExcepcionComision("No se puede cancelar una comisión ya pagada")
        
        self.estado = EstadoComision.CANCELADA
        self.motivo_rechazo = motivo
    
    def puede_ser_modificada(self) -> bool:
        """Verifica si la comisión puede ser modificada"""
        return self.estado in [EstadoComision.PENDIENTE, EstadoComision.CALCULADA]
    
    def obtener_resumen(self) -> Dict[str, Any]:
        """Obtiene resumen de la comisión"""
        return {
            "id": self.id,
            "campana_id": self.campana_id,
            "afiliado_id": self.afiliado_id,
            "conversion_id": self.conversion_id,
            "estado": self.estado.value,
            "monto_calculado": self.monto_calculado.to_dict() if self.monto_calculado else None,
            "porcentaje_aplicado": self.porcentaje_aplicado.to_float() if self.porcentaje_aplicado else None,
            "fecha_calculo": self.fecha_calculo.isoformat() if self.fecha_calculo else None,
            "fecha_aprobacion": self.fecha_aprobacion.isoformat() if self.fecha_aprobacion else None,
            "puede_ser_modificada": self.puede_ser_modificada()
        }

# Factory para crear comisiones
class ComisionFactory:
    """Factory para crear comisiones"""
    
    @staticmethod
    def crear_comision(
        campana_id: str,
        afiliado_id: str,
        conversion_id: str,
        configuracion: ConfiguracionComision,
        datos_conversion: DatosConversion,
        datos_afiliado: DatosAfiliado,
        observaciones: Optional[str] = None
    ) -> Comision:
        """Crea nueva comisión"""
        
        comision_id = str(uuid.uuid4())
        
        return Comision(
            id=comision_id,
            campana_id=campana_id,
            afiliado_id=afiliado_id,
            conversion_id=conversion_id,
            configuracion=configuracion,
            datos_conversion=datos_conversion,
            datos_afiliado=datos_afiliado,
            observaciones=observaciones,
            fecha_creacion=datetime.now(),
            fecha_actualizacion=datetime.now()
        )

# Repositorio de comisiones (interface)
class RepositorioComisiones(ABC):
    """Repositorio abstracto para comisiones"""
    
    @abstractmethod
    async def obtener_por_id(self, comision_id: str) -> Optional[Comision]:
        pass
    
    @abstractmethod
    async def obtener_por_conversion(self, conversion_id: str) -> Optional[Comision]:
        pass
    
    @abstractmethod
    async def obtener_por_afiliado(self, afiliado_id: str, 
                                  limite: int = 10, offset: int = 0) -> List[Comision]:
        pass
    
    @abstractmethod
    async def obtener_por_campana(self, campana_id: str,
                                 limite: int = 10, offset: int = 0) -> List[Comision]:
        pass
    
    @abstractmethod
    async def guardar(self, comision: Comision) -> None:
        pass
    
    @abstractmethod
    async def actualizar(self, comision: Comision) -> None:
        pass