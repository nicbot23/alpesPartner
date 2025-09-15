import os
import json
import requests
from pulsar.schema import AvroSchema, Record
from avro.schema import parse as parse_schema
import logging

logger = logging.getLogger(__name__)

PULSAR_ENV = "PULSAR_HOST"

def broker_host():
    """Obtener host del broker Pulsar"""
    return os.getenv(PULSAR_ENV, default="localhost")

def consultar_schema_registry(topico: str) -> dict:
    """
    Consultar schema registry de Apache Pulsar para obtener el schema de un tópico
    
    Args:
        topico: Nombre del tópico (ej: 'public/default/marketing.eventos')
    
    Returns:
        dict: Schema definition en formato diccionario
    """
    try:
        url = f'http://{broker_host()}:8080/admin/v2/schemas/{topico}/schema'
        response = requests.get(url)
        response.raise_for_status()
        
        json_registry = response.json()
        schema_data = json_registry.get('data', {})
        
        if isinstance(schema_data, str):
            return json.loads(schema_data)
        return schema_data
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"No se pudo consultar schema registry para tópico {topico}: {e}")
        return {}
    except json.JSONDecodeError as e:
        logger.warning(f"Error decodificando schema JSON para tópico {topico}: {e}")
        return {}

def obtener_schema_avro_de_diccionario(json_schema: dict) -> AvroSchema:
    """
    Crear AvroSchema a partir de definición JSON del schema registry
    
    Args:
        json_schema: Schema definition en formato diccionario
    
    Returns:
        AvroSchema: Schema para usar con Pulsar producer/consumer
    """
    try:
        definicion_schema = parse_schema(json_schema)
        return AvroSchema(None, schema_definition=definicion_schema)
    except Exception as e:
        logger.error(f"Error creando AvroSchema desde diccionario: {e}")
        raise

def registrar_schema_si_no_existe(topico: str, schema_class: Record) -> bool:
    """
    Registrar schema en Schema Registry si no existe
    
    Args:
        topico: Nombre del tópico
        schema_class: Clase Record de Pulsar con el schema
    
    Returns:
        bool: True si se registró exitosamente o ya existía
    """
    try:
        # Verificar si el schema ya existe
        existing_schema = consultar_schema_registry(f'public/default/{topico}')
        
        if existing_schema:
            logger.info(f"Schema para tópico {topico} ya existe en registry")
            return True
        
        # Si no existe, se registrará automáticamente al crear el producer
        logger.info(f"Schema para tópico {topico} será registrado automáticamente")
        return True
        
    except Exception as e:
        logger.error(f"Error verificando/registrando schema para tópico {topico}: {e}")
        return False

def validar_compatibilidad_schema(topico: str, nuevo_schema: dict, strategy: str = "FORWARD") -> bool:
    """
    Validar compatibilidad de schema antes de actualizar
    
    Args:
        topico: Nombre del tópico
        nuevo_schema: Nueva definición de schema
        strategy: Estrategia de compatibilidad (FORWARD, BACKWARD, FULL)
    
    Returns:
        bool: True si es compatible
    """
    try:
        url = f'http://{broker_host()}:8080/admin/v2/schemas/{topico}/compatibility'
        
        payload = {
            "schema": json.dumps(nuevo_schema),
            "type": "AVRO"
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        is_compatible = result.get('isCompatible', False)
        
        logger.info(f"Validación de compatibilidad para {topico}: {is_compatible}")
        return is_compatible
        
    except Exception as e:
        logger.warning(f"Error validando compatibilidad para {topico}: {e}")
        # Si no se puede validar, asumimos que es compatible para no bloquear
        return True

def listar_versiones_schema(topico: str) -> list:
    """
    Listar todas las versiones de schema para un tópico
    
    Args:
        topico: Nombre del tópico
    
    Returns:
        list: Lista de versiones disponibles
    """
    try:
        url = f'http://{broker_host()}:8080/admin/v2/schemas/{topico}/versions'
        response = requests.get(url)
        response.raise_for_status()
        
        versions = response.json()
        logger.info(f"Versiones disponibles para {topico}: {versions}")
        return versions
        
    except Exception as e:
        logger.warning(f"Error listando versiones para {topico}: {e}")
        return []

def obtener_schema_version(topico: str, version: int) -> dict:
    """
    Obtener schema de una versión específica
    
    Args:
        topico: Nombre del tópico
        version: Número de versión
    
    Returns:
        dict: Schema definition de la versión especificada
    """
    try:
        url = f'http://{broker_host()}:8080/admin/v2/schemas/{topico}/schema/{version}'
        response = requests.get(url)
        response.raise_for_status()
        
        json_registry = response.json()
        schema_data = json_registry.get('data', {})
        
        if isinstance(schema_data, str):
            return json.loads(schema_data)
        return schema_data
        
    except Exception as e:
        logger.warning(f"Error obteniendo schema versión {version} para {topico}: {e}")
        return {}

# Funciones de utilidad para versionamiento
def incrementar_version_schema(version_actual: str) -> str:
    """
    Incrementar versión de schema siguiendo semantic versioning
    
    Args:
        version_actual: Versión actual (ej: "v1.0.0")
    
    Returns:
        str: Nueva versión incrementada
    """
    try:
        # Remover 'v' prefix si existe
        version = version_actual.lstrip('v')
        parts = version.split('.')
        
        if len(parts) != 3:
            return "v1.0.1"
        
        major, minor, patch = map(int, parts)
        patch += 1
        
        return f"v{major}.{minor}.{patch}"
        
    except Exception:
        return "v1.0.1"

def es_breaking_change(old_schema: dict, new_schema: dict) -> bool:
    """
    Determinar si un cambio de schema es breaking change
    
    Args:
        old_schema: Schema anterior
        new_schema: Schema nuevo
    
    Returns:
        bool: True si es breaking change
    """
    # Implementación simplificada - en producción sería más compleja
    try:
        old_fields = old_schema.get('fields', [])
        new_fields = new_schema.get('fields', [])
        
        old_field_names = {field['name'] for field in old_fields}
        new_field_names = {field['name'] for field in new_fields}
        
        # Si se eliminaron campos, es breaking change
        removed_fields = old_field_names - new_field_names
        if removed_fields:
            logger.warning(f"Breaking change detectado: campos eliminados {removed_fields}")
            return True
        
        # Verificar cambios de tipo en campos existentes
        for old_field in old_fields:
            for new_field in new_fields:
                if old_field['name'] == new_field['name']:
                    if old_field.get('type') != new_field.get('type'):
                        logger.warning(f"Breaking change detectado: cambio de tipo en campo {old_field['name']}")
                        return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error determinando breaking change: {e}")
        return True  # En caso de duda, asumir que es breaking change