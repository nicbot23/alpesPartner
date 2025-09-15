import time
from uuid import uuid4
from datetime import datetime


def time_millis() -> int:
    """Obtener timestamp actual en milisegundos"""
    return int(time.time() * 1000)


def generar_uuid() -> str:
    """Generar UUID único"""
    return str(uuid4())


def timestamp_utc() -> str:
    """Obtener timestamp UTC formateado"""
    return datetime.utcnow().isoformat()


def formatear_fecha(fecha: datetime) -> str:
    """Formatear fecha a string ISO"""
    if isinstance(fecha, datetime):
        return fecha.isoformat()
    return str(fecha)


def calcular_comision(valor_conversion: float, porcentaje: float = 0.05) -> float:
    """Calcular comisión basada en valor de conversión"""
    return valor_conversion * porcentaje


def validar_fechas_campana(fecha_inicio: str, fecha_fin: str) -> bool:
    """Validar que las fechas de campaña sean correctas"""
    try:
        inicio = datetime.fromisoformat(fecha_inicio)
        fin = datetime.fromisoformat(fecha_fin)
        return inicio < fin and inicio >= datetime.now()
    except:
        return False