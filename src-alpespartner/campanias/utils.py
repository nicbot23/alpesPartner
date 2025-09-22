import time
import os
import datetime
import requests
import json
from fastavro.schema import parse_schema
from pulsar.schema import *

epoch = datetime.datetime.utcfromtimestamp(0)
PULSAR_ENV: str = 'BROKER_HOST'

def time_millis():
    """Retorna timestamp actual en milisegundos"""
    return int(time.time() * 1000)

def unix_time_millis(dt):
    """Convierte datetime a milisegundos Unix"""
    return (dt - epoch).total_seconds() * 1000.0

def broker_host():
    """
    Obtiene host del broker Pulsar:
    1) BROKER_HOST (preferido)
    2) PULSAR_HOST
    3) PULSAR_ADDRESS
    4) 'localhost' (fallback)
    """
    return (
        os.getenv('BROKER_HOST')
        or os.getenv('PULSAR_HOST')
        or os.getenv('PULSAR_ADDRESS')
        or "localhost"
    )

def millis_a_datetime(millis):
    """Convierte milisegundos a datetime"""
    return datetime.datetime.fromtimestamp(millis/1000.0)

# def broker_host():
#     """Obtiene host del broker Pulsar desde variable de entorno"""
#     return os.getenv(PULSAR_ENV, default="localhost")

def consultar_schema_registry(topico: str) -> dict:
    """Consulta schema registry para obtener schema de un tópico"""
    try:
        json_registry = requests.get(f'http://{broker_host()}:8080/admin/v2/schemas/{topico}/schema').json()
        return json.loads(json_registry.get('data', {}))
    except Exception as e:
        print(f"Error consultando schema registry para {topico}: {e}")
        return {}

def obtener_schema_avro_de_diccionario(json_schema: dict) -> AvroSchema:
    """Convierte schema JSON a AvroSchema"""
    definicion_schema = parse_schema(json_schema)
    return AvroSchema(None, definicion_schema)

def generar_id_saga():
    """Genera ID único para saga"""
    import uuid
    return f"saga-{str(uuid.uuid4())[:8]}"

def generar_id_correlacion():
    """Genera ID de correlación para tracking"""
    import uuid
    return f"corr-{str(uuid.uuid4())[:12]}"

def formatear_fecha_iso(fecha):
    """Formatea fecha a ISO string"""
    if isinstance(fecha, datetime.datetime):
        return fecha.isoformat()
    elif isinstance(fecha, str):
        return fecha
    else:
        return datetime.datetime.now().isoformat()

def parsear_fecha_iso(fecha_iso: str) -> datetime.datetime:
    """Parsea fecha ISO string a datetime"""
    try:
        return datetime.datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
    except:
        return datetime.datetime.now()

def calcular_duracion_campania(fecha_inicio: str, fecha_fin: str) -> int:
    """Calcula duración de campaña en días"""
    try:
        inicio = parsear_fecha_iso(fecha_inicio)
        fin = parsear_fecha_iso(fecha_fin)
        return (fin - inicio).days
    except:
        return 30  # Default 30 días

def validar_presupuesto(presupuesto: float, moneda: str = "USD") -> bool:
    """Valida que el presupuesto sea válido"""
    if presupuesto < 0:
        return False
    
    # Límites por moneda
    limites = {
        "USD": 1000000,  # 1M USD
        "EUR": 900000,   # 900K EUR
        "COP": 4000000000  # 4B COP
    }
    
    return presupuesto <= limites.get(moneda, 1000000)

def calcular_roi_estimado(presupuesto: float, tipo_campania: str) -> float:
    """Calcula ROI estimado según tipo de campaña"""
    multiplicadores = {
        "promocional": 2.5,
        "descuento": 3.0,
        "cashback": 2.8,
        "fidelizacion": 4.0
    }
    
    return presupuesto * multiplicadores.get(tipo_campania, 2.5)

def obtener_configuracion_microservicio():
    """Obtiene configuración del microservicio desde variables de entorno"""
    return {
        "nombre_servicio": os.getenv("SERVICE_NAME", "campanias"),
        "version": os.getenv("SERVICE_VERSION", "1.0.0"),
        "entorno": os.getenv("ENVIRONMENT", "development"),
        "puerto": int(os.getenv("PORT", "8000")),
        "broker_host": broker_host(),
        "debug": os.getenv("DEBUG", "false").lower() == "true"
    }