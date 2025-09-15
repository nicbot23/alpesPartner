"""
Eventos de integración para comunicación entre bounded contexts
Arquitectura: Event-Driven + Domain Events + Apache Pulsar + Async Messaging
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
import uuid

from ...seedwork.dominio.eventos import EventoDominio
from ..dominio.entidades import EstadoComision, TipoComision

# =============================================================================
# EVENTOS DE INTEGRACIÓN - DOMAIN EVENTS
# =============================================================================

@dataclass(frozen=True)
class EventoIntegracionComision(EventoDominio):
    """Evento base para integración de comisiones"""
    comision_id: str
    afiliado_id: str
    campana_id: str
    conversion_id: str
    estado: str
    tipo_comision: str
    monto_base: Decimal
    moneda: str
    fecha_evento: datetime = field(default_factory=datetime.now)
    version_evento: str = "1.0"
    contexto_origen: str = "marketing.comisiones"
    metadatos: Dict[str, Any] = field(default_factory=dict)
    
    def obtener_tipo_evento(self) -> str:
        return f"ComisionIntegracion.{self.__class__.__name__}"
    
    def obtener_datos_evento(self) -> Dict[str, Any]:
        return {
            "comision_id": self.comision_id,
            "afiliado_id": self.afiliado_id,
            "campana_id": self.campana_id,
            "conversion_id": self.conversion_id,
            "estado": self.estado,
            "tipo_comision": self.tipo_comision,
            "monto_base": float(self.monto_base),
            "moneda": self.moneda,
            "fecha_evento": self.fecha_evento.isoformat(),
            "version_evento": self.version_evento,
            "contexto_origen": self.contexto_origen,
            "metadatos": self.metadatos
        }

@dataclass(frozen=True)
class ComisionCreada(EventoIntegracionComision):
    """Evento: Nueva comisión creada en el sistema"""
    usuario_creador: str
    configuracion_inicial: Dict[str, Any] = field(default_factory=dict)
    
    def obtener_datos_evento(self) -> Dict[str, Any]:
        datos = super().obtener_datos_evento()
        datos.update({
            "usuario_creador": self.usuario_creador,
            "configuracion_inicial": self.configuracion_inicial,
            "descripcion_evento": "Nueva comisión creada en el sistema",
            "impacto_negocio": "Comisión pendiente de cálculo"
        })
        return datos

@dataclass(frozen=True)
class ComisionCalculada(EventoIntegracionComision):
    """Evento: Comisión calculada exitosamente"""
    monto_calculado: Decimal
    fecha_calculo: datetime
    metodo_calculo: str
    porcentaje_aplicado: Optional[Decimal] = None
    descuentos_aplicados: Dict[str, Any] = field(default_factory=dict)
    
    def obtener_datos_evento(self) -> Dict[str, Any]:
        datos = super().obtener_datos_evento()
        datos.update({
            "monto_calculado": float(self.monto_calculado),
            "fecha_calculo": self.fecha_calculo.isoformat(),
            "metodo_calculo": self.metodo_calculo,
            "porcentaje_aplicado": float(self.porcentaje_aplicado) if self.porcentaje_aplicado else None,
            "descuentos_aplicados": self.descuentos_aplicados,
            "descripcion_evento": "Comisión calculada y lista para aprobación",
            "impacto_negocio": "Monto de comisión definido"
        })
        return datos

@dataclass(frozen=True)
class ComisionAprobada(EventoIntegracionComision):
    """Evento: Comisión aprobada para pago"""
    monto_aprobado: Decimal
    fecha_aprobacion: datetime
    aprobador_id: str
    nivel_aprobacion: str
    comentarios: str
    politica_aplicada: Optional[str] = None
    
    def obtener_datos_evento(self) -> Dict[str, Any]:
        datos = super().obtener_datos_evento()
        datos.update({
            "monto_aprobado": float(self.monto_aprobado),
            "fecha_aprobacion": self.fecha_aprobacion.isoformat(),
            "aprobador_id": self.aprobador_id,
            "nivel_aprobacion": self.nivel_aprobacion,
            "comentarios": self.comentarios,
            "politica_aplicada": self.politica_aplicada,
            "descripcion_evento": "Comisión aprobada y autorizada para pago",
            "impacto_negocio": "Comisión lista para procesamiento de pagos"
        })
        return datos

@dataclass(frozen=True)
class ComisionRechazada(EventoIntegracionComision):
    """Evento: Comisión rechazada"""
    fecha_rechazo: datetime
    rechazador_id: str
    motivo_rechazo: str
    categoria_rechazo: str
    requiere_revision: bool = False
    comentarios_adicionales: Optional[str] = None
    
    def obtener_datos_evento(self) -> Dict[str, Any]:
        datos = super().obtener_datos_evento()
        datos.update({
            "fecha_rechazo": self.fecha_rechazo.isoformat(),
            "rechazador_id": self.rechazador_id,
            "motivo_rechazo": self.motivo_rechazo,
            "categoria_rechazo": self.categoria_rechazo,
            "requiere_revision": self.requiere_revision,
            "comentarios_adicionales": self.comentarios_adicionales,
            "descripcion_evento": "Comisión rechazada por incumplimiento de criterios",
            "impacto_negocio": "Comisión excluida del procesamiento de pagos"
        })
        return datos

@dataclass(frozen=True)
class ComisionPagada(EventoIntegracionComision):
    """Evento: Comisión pagada exitosamente"""
    monto_pagado: Decimal
    fecha_pago: datetime
    metodo_pago: str
    referencia_pago: str
    proveedor_pago: str
    cuenta_destino: str
    comision_bancaria: Optional[Decimal] = None
    
    def obtener_datos_evento(self) -> Dict[str, Any]:
        datos = super().obtener_datos_evento()
        datos.update({
            "monto_pagado": float(self.monto_pagado),
            "fecha_pago": self.fecha_pago.isoformat(),
            "metodo_pago": self.metodo_pago,
            "referencia_pago": self.referencia_pago,
            "proveedor_pago": self.proveedor_pago,
            "cuenta_destino": self.cuenta_destino,
            "comision_bancaria": float(self.comision_bancaria) if self.comision_bancaria else None,
            "descripcion_evento": "Comisión pagada exitosamente al afiliado",
            "impacto_negocio": "Ciclo de comisión completado"
        })
        return datos

@dataclass(frozen=True)
class ComisionAnulada(EventoIntegracionComision):
    """Evento: Comisión anulada"""
    fecha_anulacion: datetime
    anulador_id: str
    motivo_anulacion: str
    tipo_anulacion: str  # 'administrativa', 'fraude', 'error_sistema'
    es_reversible: bool = True
    requiere_reembolso: bool = False
    
    def obtener_datos_evento(self) -> Dict[str, Any]:
        datos = super().obtener_datos_evento()
        datos.update({
            "fecha_anulacion": self.fecha_anulacion.isoformat(),
            "anulador_id": self.anulador_id,
            "motivo_anulacion": self.motivo_anulacion,
            "tipo_anulacion": self.tipo_anulacion,
            "es_reversible": self.es_reversible,
            "requiere_reembolso": self.requiere_reembolso,
            "descripcion_evento": "Comisión anulada por razones administrativas o técnicas",
            "impacto_negocio": "Reversión de comisión procesada"
        })
        return datos

# =============================================================================
# EVENTOS DE SINCRONIZACIÓN CON OTROS BOUNDED CONTEXTS
# =============================================================================

@dataclass(frozen=True)
class SolicitudValidacionAfiliado(EventoDominio):
    """Solicitud para validar estado del afiliado"""
    afiliado_id: str
    comision_id: str
    fecha_solicitud: datetime = field(default_factory=datetime.now)
    criterios_validacion: List[str] = field(default_factory=list)
    
    def obtener_tipo_evento(self) -> str:
        return "Afiliados.SolicitudValidacion"
    
    def obtener_datos_evento(self) -> Dict[str, Any]:
        return {
            "afiliado_id": self.afiliado_id,
            "comision_id": self.comision_id,
            "fecha_solicitud": self.fecha_solicitud.isoformat(),
            "criterios_validacion": self.criterios_validacion,
            "contexto_origen": "marketing.comisiones",
            "descripcion": "Solicitud de validación de estado del afiliado"
        }

@dataclass(frozen=True)
class SolicitudVerificacionConversion(EventoDominio):
    """Solicitud para verificar datos de conversión"""
    conversion_id: str
    comision_id: str
    campana_id: str
    fecha_solicitud: datetime = field(default_factory=datetime.now)
    datos_requeridos: List[str] = field(default_factory=list)
    
    def obtener_tipo_evento(self) -> str:
        return "Conversiones.SolicitudVerificacion"
    
    def obtener_datos_evento(self) -> Dict[str, Any]:
        return {
            "conversion_id": self.conversion_id,
            "comision_id": self.comision_id,
            "campana_id": self.campana_id,
            "fecha_solicitud": self.fecha_solicitud.isoformat(),
            "datos_requeridos": self.datos_requeridos,
            "contexto_origen": "marketing.comisiones",
            "descripcion": "Solicitud de verificación de datos de conversión"
        }

@dataclass(frozen=True)
class NotificacionEstadoComision(EventoDominio):
    """Notificación de cambio de estado de comisión"""
    comision_id: str
    afiliado_id: str
    estado_anterior: str
    estado_nuevo: str
    fecha_cambio: datetime = field(default_factory=datetime.now)
    usuario_responsable: str
    detalles_cambio: Dict[str, Any] = field(default_factory=dict)
    
    def obtener_tipo_evento(self) -> str:
        return "Notificaciones.CambioEstadoComision"
    
    def obtener_datos_evento(self) -> Dict[str, Any]:
        return {
            "comision_id": self.comision_id,
            "afiliado_id": self.afiliado_id,
            "estado_anterior": self.estado_anterior,
            "estado_nuevo": self.estado_nuevo,
            "fecha_cambio": self.fecha_cambio.isoformat(),
            "usuario_responsable": self.usuario_responsable,
            "detalles_cambio": self.detalles_cambio,
            "contexto_origen": "marketing.comisiones",
            "descripcion": "Notificación de cambio de estado de comisión"
        }

# =============================================================================
# FACTORY DE EVENTOS
# =============================================================================

class FabricaEventosIntegracion:
    """Factory para crear eventos de integración"""
    
    @staticmethod
    def crear_comision_creada(
        comision_id: str,
        afiliado_id: str, 
        campana_id: str,
        conversion_id: str,
        tipo_comision: TipoComision,
        monto_base: Decimal,
        moneda: str,
        usuario_creador: str,
        configuracion: Dict[str, Any] = None,
        metadatos: Dict[str, Any] = None
    ) -> ComisionCreada:
        """Crear evento de comisión creada"""
        return ComisionCreada(
            comision_id=comision_id,
            afiliado_id=afiliado_id,
            campana_id=campana_id,
            conversion_id=conversion_id,
            estado=EstadoComision.PENDIENTE.value,
            tipo_comision=tipo_comision.value,
            monto_base=monto_base,
            moneda=moneda,
            usuario_creador=usuario_creador,
            configuracion_inicial=configuracion or {},
            metadatos=metadatos or {}
        )
    
    @staticmethod
    def crear_comision_calculada(
        comision_id: str,
        afiliado_id: str,
        campana_id: str,
        conversion_id: str,
        tipo_comision: TipoComision,
        monto_base: Decimal,
        monto_calculado: Decimal,
        moneda: str,
        metodo_calculo: str,
        porcentaje_aplicado: Decimal = None,
        descuentos: Dict[str, Any] = None,
        metadatos: Dict[str, Any] = None
    ) -> ComisionCalculada:
        """Crear evento de comisión calculada"""
        return ComisionCalculada(
            comision_id=comision_id,
            afiliado_id=afiliado_id,
            campana_id=campana_id,
            conversion_id=conversion_id,
            estado=EstadoComision.CALCULADA.value,
            tipo_comision=tipo_comision.value,
            monto_base=monto_base,
            moneda=moneda,
            monto_calculado=monto_calculado,
            fecha_calculo=datetime.now(),
            metodo_calculo=metodo_calculo,
            porcentaje_aplicado=porcentaje_aplicado,
            descuentos_aplicados=descuentos or {},
            metadatos=metadatos or {}
        )
    
    @staticmethod
    def crear_comision_aprobada(
        comision_id: str,
        afiliado_id: str,
        campana_id: str,
        conversion_id: str,
        tipo_comision: TipoComision,
        monto_base: Decimal,
        monto_aprobado: Decimal,
        moneda: str,
        aprobador_id: str,
        nivel_aprobacion: str,
        comentarios: str,
        politica: str = None,
        metadatos: Dict[str, Any] = None
    ) -> ComisionAprobada:
        """Crear evento de comisión aprobada"""
        return ComisionAprobada(
            comision_id=comision_id,
            afiliado_id=afiliado_id,
            campana_id=campana_id,
            conversion_id=conversion_id,
            estado=EstadoComision.APROBADA.value,
            tipo_comision=tipo_comision.value,
            monto_base=monto_base,
            moneda=moneda,
            monto_aprobado=monto_aprobado,
            fecha_aprobacion=datetime.now(),
            aprobador_id=aprobador_id,
            nivel_aprobacion=nivel_aprobacion,
            comentarios=comentarios,
            politica_aplicada=politica,
            metadatos=metadatos or {}
        )
    
    @staticmethod
    def crear_comision_pagada(
        comision_id: str,
        afiliado_id: str,
        campana_id: str,
        conversion_id: str,
        tipo_comision: TipoComision,
        monto_base: Decimal,
        monto_pagado: Decimal,
        moneda: str,
        metodo_pago: str,
        referencia_pago: str,
        proveedor_pago: str,
        cuenta_destino: str,
        comision_bancaria: Decimal = None,
        metadatos: Dict[str, Any] = None
    ) -> ComisionPagada:
        """Crear evento de comisión pagada"""
        return ComisionPagada(
            comision_id=comision_id,
            afiliado_id=afiliado_id,
            campana_id=campana_id,
            conversion_id=conversion_id,
            estado=EstadoComision.PAGADA.value,
            tipo_comision=tipo_comision.value,
            monto_base=monto_base,
            moneda=moneda,
            monto_pagado=monto_pagado,
            fecha_pago=datetime.now(),
            metodo_pago=metodo_pago,
            referencia_pago=referencia_pago,
            proveedor_pago=proveedor_pago,
            cuenta_destino=cuenta_destino,
            comision_bancaria=comision_bancaria,
            metadatos=metadatos or {}
        )

# =============================================================================
# REGISTRO DE EVENTOS - EVENT REGISTRY
# =============================================================================

class RegistroEventosIntegracion:
    """Registro centralizado de eventos de integración"""
    
    EVENTOS_DISPONIBLES = {
        'ComisionCreada': ComisionCreada,
        'ComisionCalculada': ComisionCalculada,
        'ComisionAprobada': ComisionAprobada,
        'ComisionRechazada': ComisionRechazada,
        'ComisionPagada': ComisionPagada,
        'ComisionAnulada': ComisionAnulada,
        'SolicitudValidacionAfiliado': SolicitudValidacionAfiliado,
        'SolicitudVerificacionConversion': SolicitudVerificacionConversion,
        'NotificacionEstadoComision': NotificacionEstadoComision
    }
    
    @classmethod
    def obtener_evento_por_nombre(cls, nombre: str):
        """Obtener clase de evento por nombre"""
        return cls.EVENTOS_DISPONIBLES.get(nombre)
    
    @classmethod
    def listar_eventos_disponibles(cls) -> List[str]:
        """Listar todos los eventos disponibles"""
        return list(cls.EVENTOS_DISPONIBLES.keys())
    
    @classmethod
    def es_evento_valido(cls, nombre: str) -> bool:
        """Verificar si un evento es válido"""
        return nombre in cls.EVENTOS_DISPONIBLES
    
    @classmethod
    def obtener_metadatos_evento(cls, nombre: str) -> Dict[str, Any]:
        """Obtener metadatos de un evento"""
        if not cls.es_evento_valido(nombre):
            return {}
        
        evento_clase = cls.EVENTOS_DISPONIBLES[nombre]
        return {
            "nombre": nombre,
            "clase": evento_clase.__name__,
            "modulo": evento_clase.__module__,
            "campos": list(evento_clase.__dataclass_fields__.keys()),
            "es_evento_integracion": issubclass(evento_clase, EventoIntegracionComision),
            "contexto_origen": "marketing.comisiones"
        }