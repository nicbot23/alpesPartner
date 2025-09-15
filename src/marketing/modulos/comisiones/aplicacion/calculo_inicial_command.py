"""Comando para cálculo inicial de comisión disparado desde Campañas"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

@dataclass
class CalcularComisionInicialCommand:
    campana_id: str
    afiliado_id: str = "afiliado-default"
    conversion_id: str = "config-inicial"
    monto_base: float = 0.0
    porcentaje: float = 0.0
    moneda: str = "COP"
    correlation_id: Optional[str] = None

    def ensure(self):
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())

@dataclass
class ResultadoCalculoInicial:
    comision_id: str
    publicado: bool
    persisted: bool
    correlation_id: str
    fecha_calculo: str
