"""
Eventos de dominio específicos del microservicio Afiliados
Implementa eventos para comunicación entre bounded contexts
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any

from ..seedwork.dominio.eventos import EventoDominio, EventoIntegracion
from .entidades import DocumentoIdentidad, DatosPersonales, EstadoAfiliado

@dataclass
class AfiliadoRegistrado(EventoDominio):
    """Evento cuando un afiliado se registra en el sistema"""
    afiliado_id: str
    documento: DocumentoIdentidad
    datos_personales: DatosPersonales
    
    def __post_init__(self):
        super().__init__(nombre="AfiliadoRegistrado")

@dataclass  
class AfiliadoAprobado(EventoDominio):
    """Evento cuando un afiliado es aprobado"""
    afiliado_id: str
    fecha_aprobacion: datetime
    usuario_responsable: str
    
    def __post_init__(self):
        super().__init__(nombre="AfiliadoAprobado")

@dataclass
class AfiliadoRechazado(EventoDominio):
    """Evento cuando un afiliado es rechazado"""
    afiliado_id: str
    motivo_rechazo: str
    fecha_rechazo: datetime
    usuario_responsable: str
    
    def __post_init__(self):
        super().__init__(nombre="AfiliadoRechazado")

@dataclass
class AfiliadoActivado(EventoDominio):
    """Evento cuando un afiliado es activado"""
    afiliado_id: str
    fecha_activacion: datetime
    usuario_responsable: str
    
    def __post_init__(self):
        super().__init__(nombre="AfiliadoActivado")

@dataclass
class AfiliadoDesactivado(EventoDominio):
    """Evento cuando un afiliado es desactivado"""
    afiliado_id: str
    motivo: str
    fecha_desactivacion: datetime
    usuario_responsable: str
    
    def __post_init__(self):
        super().__init__(nombre="AfiliadoDesactivado")

@dataclass
class DatosAfiliadoActualizados(EventoDominio):
    """Evento cuando se actualizan los datos de un afiliado"""
    afiliado_id: str
    datos_anteriores: DatosPersonales
    datos_nuevos: DatosPersonales
    fecha_actualizacion: datetime
    usuario_responsable: str
    
    def __post_init__(self):
        super().__init__(nombre="DatosAfiliadoActualizados")

# Eventos de integración para comunicación con otros microservicios

@dataclass
class AfiliadoAprobadoIntegracion(EventoIntegracion):
    """
    Evento de integración cuando un afiliado es aprobado
    Se envía a Marketing y Conversiones
    """
    afiliado_id: str
    documento_numero: str
    nombre_completo: str
    email: str
    fecha_aprobacion: datetime
    
    def __post_init__(self):
        super().__init__(
            nombre="AfiliadoAprobadoIntegracion",
            source_service="afiliados",
            destination_services=["marketing", "conversiones"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para serialización"""
        return {
            "afiliado_id": self.afiliado_id,
            "documento_numero": self.documento_numero,
            "nombre_completo": self.nombre_completo,
            "email": self.email,
            "fecha_aprobacion": self.fecha_aprobacion.isoformat(),
            "source_service": self.source_service,
            "destination_services": self.destination_services,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class AfiliadoDesactivadoIntegracion(EventoIntegracion):
    """
    Evento de integración cuando un afiliado es desactivado
    Se envía a Marketing y Conversiones para detener actividades
    """
    afiliado_id: str
    documento_numero: str
    motivo: str
    fecha_desactivacion: datetime
    
    def __post_init__(self):
        super().__init__(
            nombre="AfiliadoDesactivadoIntegracion",
            source_service="afiliados",
            destination_services=["marketing", "conversiones"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para serialización"""
        return {
            "afiliado_id": self.afiliado_id,
            "documento_numero": self.documento_numero,
            "motivo": self.motivo,
            "fecha_desactivacion": self.fecha_desactivacion.isoformat(),
            "source_service": self.source_service,
            "destination_services": self.destination_services,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class DatosAfiliadoActualizadosIntegracion(EventoIntegracion):
    """
    Evento de integración cuando se actualizan datos de afiliado
    Se envía a Marketing para actualizar campañas
    """
    afiliado_id: str
    documento_numero: str
    email_anterior: str
    email_nuevo: str
    nombre_completo_nuevo: str
    fecha_actualizacion: datetime
    
    def __post_init__(self):
        super().__init__(
            nombre="DatosAfiliadoActualizadosIntegracion",
            source_service="afiliados",
            destination_services=["marketing"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para serialización"""
        return {
            "afiliado_id": self.afiliado_id,
            "documento_numero": self.documento_numero,
            "email_anterior": self.email_anterior,
            "email_nuevo": self.email_nuevo,
            "nombre_completo_nuevo": self.nombre_completo_nuevo,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat(),
            "source_service": self.source_service,
            "destination_services": self.destination_services,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "timestamp": self.timestamp.isoformat()
        }