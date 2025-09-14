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