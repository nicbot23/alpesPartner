from dataclasses import dataclass
from alpespartner.seedwork.aplicacion.comandos import Comando
from alpespartner.modulos.conversiones.dominio.objetos_valor import TipoConversion
from decimal import Decimal
from typing import Optional


@dataclass
class CreateConversion(Comando):
    """Comando para crear una nueva conversión."""
    afiliado_id: str
    campana_id: str
    tipo_conversion: str  # Se convierte a TipoConversion en el handler
    monto_transaccion: Decimal
    fecha_conversion: str  # ISO format, se convierte a datetime en handler
    metadata: Optional[dict] = None


@dataclass 
class ValidateConversion(Comando):
    """Comando para validar una conversión existente."""
    conversion_id: str
    validado_por: str
    notas_validacion: Optional[str] = None


@dataclass
class ConfirmConversion(Comando):
    """Comando para confirmar manualmente una conversión."""
    conversion_id: str
    confirmado_por: str
    notas_confirmacion: Optional[str] = None


@dataclass
class RejectConversion(Comando):
    """Comando para rechazar una conversión."""
    conversion_id: str
    rechazado_por: str
    motivo_rechazo: str


@dataclass
class CancelConversion(Comando):
    """Comando para cancelar una conversión."""
    conversion_id: str
    cancelado_por: str
    motivo_cancelacion: str


@dataclass
class AttributeConversion(Comando):
    """Comando para atribuir una comisión a una conversión."""
    conversion_id: str
    comision_id: str
    monto_comision: Decimal
    atribuido_por: str