"""
Utilidades para el microservicio Conversiones
"""
import time
import uuid
from typing import Optional

def time_millis() -> int:
    """Obtener timestamp en milisegundos"""
    return int(time.time() * 1000)

def generar_uuid() -> str:
    """Generar UUID único"""
    return str(uuid.uuid4())

def broker_host() -> str:
    """Obtener host del broker"""
    return "pulsar"

def validar_conversion_data(data: dict) -> bool:
    """Validar datos de conversión"""
    required_fields = ['affiliate_id', 'campaign_id', 'user_id', 'conversion_value']
    return all(field in data for field in required_fields)

def calcular_comision(valor_conversion: float, tasa_comision: float) -> float:
    """Calcular comisión basada en valor y tasa"""
    return valor_conversion * (tasa_comision / 100)

def formatear_valor_moneda(valor: float, currency: str = "USD") -> str:
    """Formatear valor como moneda"""
    return f"{currency} {valor:.2f}"