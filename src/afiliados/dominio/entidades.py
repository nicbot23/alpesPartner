"""
Entidades del dominio de Afiliados
Implementa principios SOLID y patrones DDD
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum
import uuid

from ..seedwork.dominio.entidades import AgregacionRaiz, EntidadRaiz
from ..seedwork.dominio.eventos import EventoDominio

class EstadoAfiliado(Enum):
    """Estados posibles de un afiliado"""
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"

class TipoDocumento(Enum):
    """Tipos de documento de identidad"""
    CEDULA = "cedula"
    PASAPORTE = "pasaporte"
    CEDULA_EXTRANJERIA = "cedula_extranjeria"

@dataclass
class DocumentoIdentidad:
    """Value Object para documento de identidad"""
    tipo: TipoDocumento
    numero: str
    
    def __post_init__(self):
        if not self.numero or len(self.numero.strip()) == 0:
            raise ValueError("El número de documento no puede estar vacío")
        
        # Validaciones específicas por tipo
        if self.tipo == TipoDocumento.CEDULA and not self.numero.isdigit():
            raise ValueError("El número de cédula debe contener solo dígitos")

@dataclass
class DatosPersonales:
    """Value Object para datos personales del afiliado"""
    nombres: str
    apellidos: str
    email: str
    telefono: str
    fecha_nacimiento: datetime
    
    def __post_init__(self):
        if not self.nombres or len(self.nombres.strip()) == 0:
            raise ValueError("Los nombres son obligatorios")
        
        if not self.apellidos or len(self.apellidos.strip()) == 0:
            raise ValueError("Los apellidos son obligatorios")
        
        if not self.email or "@" not in self.email:
            raise ValueError("Email inválido")
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo"""
        return f"{self.nombres} {self.apellidos}"

@dataclass
class HistorialEstado:
    """Value Object para historial de cambios de estado"""
    estado_anterior: EstadoAfiliado
    estado_nuevo: EstadoAfiliado
    fecha_cambio: datetime
    usuario_responsable: str
    observaciones: str = ""

class Afiliado(AgregacionRaiz):
    """
    Agregado raíz para Afiliado
    Implementa principios SOLID y DDD
    """
    
    def __init__(
        self,
        documento: DocumentoIdentidad,
        datos_personales: DatosPersonales,
        afiliado_id: str = None
    ):
        super().__init__(afiliado_id or str(uuid.uuid4()))
        self._documento = documento
        self._datos_personales = datos_personales
        self._estado = EstadoAfiliado.PENDIENTE
        self._fecha_afiliacion = datetime.now()
        self._historial_estados: List[HistorialEstado] = []
        
        # Evento de dominio: afiliado registrado
        from .eventos import AfiliadoRegistrado
        self._agregar_evento(AfiliadoRegistrado(
            afiliado_id=self.id,
            documento=documento,
            datos_personales=datos_personales
        ))
    
    @property
    def documento(self) -> DocumentoIdentidad:
        """Documento de identidad del afiliado"""
        return self._documento
    
    @property
    def datos_personales(self) -> DatosPersonales:
        """Datos personales del afiliado"""
        return self._datos_personales
    
    @property
    def estado(self) -> EstadoAfiliado:
        """Estado actual del afiliado"""
        return self._estado
    
    @property
    def fecha_afiliacion(self) -> datetime:
        """Fecha de afiliación"""
        return self._fecha_afiliacion
    
    @property
    def historial_estados(self) -> List[HistorialEstado]:
        """Historial de cambios de estado"""
        return self._historial_estados.copy()
    
    def aprobar(self, usuario_responsable: str, observaciones: str = "") -> None:
        """
        Aprueba el afiliado
        Regla de negocio: solo se pueden aprobar afiliados pendientes
        """
        if self._estado != EstadoAfiliado.PENDIENTE:
            raise ValueError(f"No se puede aprobar un afiliado en estado {self._estado.value}")
        
        self._cambiar_estado(
            EstadoAfiliado.APROBADO,
            usuario_responsable,
            observaciones
        )
        
        # Evento de dominio: afiliado aprobado
        from .eventos import AfiliadoAprobado
        self._agregar_evento(AfiliadoAprobado(
            afiliado_id=self.id,
            fecha_aprobacion=datetime.now(),
            usuario_responsable=usuario_responsable
        ))
    
    def rechazar(self, usuario_responsable: str, motivo: str) -> None:
        """
        Rechaza el afiliado
        Regla de negocio: solo se pueden rechazar afiliados pendientes
        """
        if self._estado != EstadoAfiliado.PENDIENTE:
            raise ValueError(f"No se puede rechazar un afiliado en estado {self._estado.value}")
        
        if not motivo or len(motivo.strip()) == 0:
            raise ValueError("El motivo de rechazo es obligatorio")
        
        self._cambiar_estado(
            EstadoAfiliado.RECHAZADO,
            usuario_responsable,
            motivo
        )
        
        # Evento de dominio: afiliado rechazado
        from .eventos import AfiliadoRechazado
        self._agregar_evento(AfiliadoRechazado(
            afiliado_id=self.id,
            motivo_rechazo=motivo,
            fecha_rechazo=datetime.now(),
            usuario_responsable=usuario_responsable
        ))
    
    def activar(self, usuario_responsable: str) -> None:
        """
        Activa el afiliado
        Regla de negocio: solo se pueden activar afiliados aprobados o inactivos
        """
        if self._estado not in [EstadoAfiliado.APROBADO, EstadoAfiliado.INACTIVO]:
            raise ValueError(f"No se puede activar un afiliado en estado {self._estado.value}")
        
        self._cambiar_estado(
            EstadoAfiliado.ACTIVO,
            usuario_responsable,
            "Afiliado activado"
        )
        
        # Evento de dominio: afiliado activado
        from .eventos import AfiliadoActivado
        self._agregar_evento(AfiliadoActivado(
            afiliado_id=self.id,
            fecha_activacion=datetime.now(),
            usuario_responsable=usuario_responsable
        ))
    
    def desactivar(self, usuario_responsable: str, motivo: str = "") -> None:
        """
        Desactiva el afiliado
        Regla de negocio: solo se pueden desactivar afiliados activos
        """
        if self._estado != EstadoAfiliado.ACTIVO:
            raise ValueError(f"No se puede desactivar un afiliado en estado {self._estado.value}")
        
        self._cambiar_estado(
            EstadoAfiliado.INACTIVO,
            usuario_responsable,
            motivo or "Afiliado desactivado"
        )
        
        # Evento de dominio: afiliado desactivado
        from .eventos import AfiliadoDesactivado
        self._agregar_evento(AfiliadoDesactivado(
            afiliado_id=self.id,
            motivo=motivo,
            fecha_desactivacion=datetime.now(),
            usuario_responsable=usuario_responsable
        ))
    
    def actualizar_datos_personales(
        self, 
        nuevos_datos: DatosPersonales,
        usuario_responsable: str
    ) -> None:
        """
        Actualiza los datos personales del afiliado
        Regla de negocio: solo se pueden actualizar afiliados activos o aprobados
        """
        if self._estado not in [EstadoAfiliado.ACTIVO, EstadoAfiliado.APROBADO]:
            raise ValueError(f"No se pueden actualizar datos de un afiliado en estado {self._estado.value}")
        
        datos_anteriores = self._datos_personales
        self._datos_personales = nuevos_datos
        
        # Evento de dominio: datos actualizados
        from .eventos import DatosAfiliadoActualizados
        self._agregar_evento(DatosAfiliadoActualizados(
            afiliado_id=self.id,
            datos_anteriores=datos_anteriores,
            datos_nuevos=nuevos_datos,
            fecha_actualizacion=datetime.now(),
            usuario_responsable=usuario_responsable
        ))
    
    def puede_realizar_conversiones(self) -> bool:
        """
        Determina si el afiliado puede realizar conversiones
        Regla de negocio: solo afiliados activos pueden realizar conversiones
        """
        return self._estado == EstadoAfiliado.ACTIVO
    
    def _cambiar_estado(
        self, 
        nuevo_estado: EstadoAfiliado, 
        usuario_responsable: str,
        observaciones: str
    ) -> None:
        """Método privado para cambiar estado y mantener historial"""
        historial = HistorialEstado(
            estado_anterior=self._estado,
            estado_nuevo=nuevo_estado,
            fecha_cambio=datetime.now(),
            usuario_responsable=usuario_responsable,
            observaciones=observaciones
        )
        
        self._estado = nuevo_estado
        self._historial_estados.append(historial)
        self._incrementar_version()
    
    def __str__(self) -> str:
        return f"Afiliado({self.id}, {self._datos_personales.nombre_completo}, {self._estado.value})"