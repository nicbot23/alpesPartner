"""
Comandos para el módulo de Afiliados
Representan las intenciones de cambio en el dominio
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from alpespartner.seedwork.aplicacion.comandos import ComandoIntegracion


@dataclass(frozen=True)
class ComandoCrearAfiliado(ComandoIntegracion):
    """Comando para crear un nuevo afiliado."""
    
    # Datos personales
    nombres: str
    apellidos: str
    fecha_nacimiento: Optional[datetime] = None
    
    # Documento de identidad
    tipo_documento: str  # CEDULA, PASAPORTE, NIT, RUT
    numero_documento: str
    fecha_expedicion_documento: Optional[datetime] = None
    
    # Datos de contacto
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    
    # Configuración de negocio
    tipo_afiliado: str  # INFLUENCER, EMPRESA, INDIVIDUAL, PREMIUM
    porcentaje_comision_base: Decimal
    porcentaje_comision_premium: Optional[Decimal] = None
    monto_minimo_comision: Optional[Decimal] = None
    
    # Sistema de referencias
    afiliado_referente_id: Optional[str] = None
    
    # Metadatos adicionales
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class ComandoActivarAfiliado(ComandoIntegracion):
    """Comando para activar un afiliado."""
    
    afiliado_id: str
    codigo_referencia: Optional[str] = None


@dataclass(frozen=True)
class ComandoDesactivarAfiliado(ComandoIntegracion):
    """Comando para desactivar un afiliado."""
    
    afiliado_id: str
    motivo: Optional[str] = None


@dataclass(frozen=True)
class ComandoSuspenderAfiliado(ComandoIntegracion):
    """Comando para suspender un afiliado."""
    
    afiliado_id: str
    motivo: str
    fecha_suspension: Optional[datetime] = None


@dataclass(frozen=True)
class ComandoBloquearAfiliado(ComandoIntegracion):
    """Comando para bloquear un afiliado."""
    
    afiliado_id: str
    motivo: str
    fecha_bloqueo: Optional[datetime] = None


@dataclass(frozen=True)
class ComandoActualizarDatosBancarios(ComandoIntegracion):
    """Comando para actualizar datos bancarios de un afiliado."""
    
    afiliado_id: str
    banco: str
    tipo_cuenta: str
    numero_cuenta: str
    titular_cuenta: str


@dataclass(frozen=True)
class ComandoActualizarConfiguracionComisiones(ComandoIntegracion):
    """Comando para actualizar la configuración de comisiones."""
    
    afiliado_id: str
    porcentaje_comision_base: Optional[Decimal] = None
    porcentaje_comision_premium: Optional[Decimal] = None
    monto_minimo_comision: Optional[Decimal] = None


@dataclass(frozen=True)
class ComandoAgregarReferencia(ComandoIntegracion):
    """Comando para agregar una referencia entre afiliados."""
    
    afiliado_referente_id: str
    afiliado_referido_id: str
    fecha_referencia: Optional[datetime] = None


@dataclass(frozen=True)
class ComandoActualizarDatosPersonales(ComandoIntegracion):
    """Comando para actualizar datos personales de un afiliado."""
    
    afiliado_id: str
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None


@dataclass(frozen=True)
class ComandoActualizarMetadatos(ComandoIntegracion):
    """Comando para actualizar metadatos de un afiliado."""
    
    afiliado_id: str
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class ComandoValidarAfiliado(ComandoIntegracion):
    """Comando para validar datos de un afiliado."""
    
    afiliado_id: str
    validaciones: Dict[str, bool]  # {'documentos': True, 'datos_bancarios': False, etc.}
    observaciones: Optional[str] = None