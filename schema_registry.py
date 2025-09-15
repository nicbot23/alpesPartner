"""
Schema Registry Implementation para Apache Pulsar
Siguiendo patrones del tutorial AeroAlpes para manejo de esquemas Avro

Este módulo proporciona funcionalidades para:
- Registrar esquemas en Schema Registry
- Validar compatibilidad de esquemas
- Gestionar versiones de esquemas
- Integración con patrones comando/evento
"""

import json
import requests
from typing import Dict, Optional, List
import avro.schema
import avro.io
import io
import logging

# Configuración del Schema Registry
SCHEMA_REGISTRY_URL = "http://localhost:8080"  # Pulsar Admin API
ADMIN_ENDPOINT = "/admin/v2/schemas"

logger = logging.getLogger(__name__)

class SchemaRegistryManager:
    """
    Gestor del Schema Registry de Apache Pulsar
    Implementa patrones de AeroAlpes para manejo de esquemas
    """
    
    def __init__(self, registry_url: str = SCHEMA_REGISTRY_URL):
        self.registry_url = registry_url
        self.admin_endpoint = f"{registry_url}{ADMIN_ENDPOINT}"
    
    def consultar_schema_registry(self, topic: str) -> Optional[Dict]:
        """
        Consulta el esquema actual de un topic en Schema Registry
        
        Args:
            topic: Nombre del topic (ej: "evento-campana-creada")
            
        Returns:
            Dict con información del esquema o None si no existe
        """
        try:
            url = f"{self.admin_endpoint}/{topic}/schema"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.info(f"No existe esquema para topic: {topic}")
                return None
            else:
                logger.error(f"Error consultando schema: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error de conexión al Schema Registry: {e}")
            return None
    
    def registrar_schema_si_no_existe(self, topic: str, schema_json: Dict) -> bool:
        """
        Registra un esquema en Schema Registry si no existe
        Siguiendo patrón de AeroAlpes para registro automático
        
        Args:
            topic: Nombre del topic
            schema_json: Esquema Avro en formato JSON
            
        Returns:
            True si se registró exitosamente o ya existía
        """
        try:
            # Verificar si ya existe
            existing_schema = self.consultar_schema_registry(topic)
            if existing_schema:
                logger.info(f"Esquema ya existe para topic: {topic}")
                return True
            
            # Registrar nuevo esquema
            url = f"{self.admin_endpoint}/{topic}/schema"
            payload = {
                "type": "AVRO",
                "schema": json.dumps(schema_json),
                "properties": {}
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code in [200, 201]:
                logger.info(f"Esquema registrado exitosamente para topic: {topic}")
                return True
            else:
                logger.error(f"Error registrando esquema: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error registrando esquema para {topic}: {e}")
            return False
    
    def validar_compatibilidad_schema(self, topic: str, nuevo_schema: Dict) -> Dict:
        """
        Valida compatibilidad de un nuevo esquema con el existente
        Implementa verificación de evolución de esquemas
        
        Args:
            topic: Nombre del topic
            nuevo_schema: Nuevo esquema a validar
            
        Returns:
            Dict con resultado de validación
        """
        try:
            schema_actual = self.consultar_schema_registry(topic)
            
            if not schema_actual:
                return {
                    "compatible": True,
                    "mensaje": "No existe esquema previo, se puede registrar",
                    "cambios": []
                }
            
            # Parsear esquemas
            schema_actual_obj = avro.schema.parse(json.dumps(schema_actual.get("schema", {})))
            nuevo_schema_obj = avro.schema.parse(json.dumps(nuevo_schema))
            
            # Verificar compatibilidad básica
            cambios_detectados = self._detectar_cambios_schema(
                schema_actual.get("schema", {}), 
                nuevo_schema
            )
            
            es_compatible = self._evaluar_compatibilidad(cambios_detectados)
            
            return {
                "compatible": es_compatible,
                "mensaje": "Compatible" if es_compatible else "Cambios incompatibles detectados",
                "cambios": cambios_detectados
            }
            
        except Exception as e:
            logger.error(f"Error validando compatibilidad: {e}")
            return {
                "compatible": False,
                "mensaje": f"Error en validación: {str(e)}",
                "cambios": []
            }
    
    def _detectar_cambios_schema(self, schema_actual: Dict, nuevo_schema: Dict) -> List[Dict]:
        """Detecta cambios entre esquemas"""
        cambios = []
        
        # Comparar campos
        campos_actuales = {f["name"]: f for f in schema_actual.get("fields", [])}
        campos_nuevos = {f["name"]: f for f in nuevo_schema.get("fields", [])}
        
        # Campos eliminados
        for campo in campos_actuales:
            if campo not in campos_nuevos:
                cambios.append({
                    "tipo": "campo_eliminado",
                    "campo": campo,
                    "impacto": "breaking"
                })
        
        # Campos añadidos
        for campo in campos_nuevos:
            if campo not in campos_actuales:
                nuevo_campo = campos_nuevos[campo]
                tiene_default = "default" in nuevo_campo
                cambios.append({
                    "tipo": "campo_añadido",
                    "campo": campo,
                    "impacto": "compatible" if tiene_default else "breaking"
                })
        
        # Campos modificados
        for campo in campos_actuales:
            if campo in campos_nuevos:
                actual = campos_actuales[campo]
                nuevo = campos_nuevos[campo]
                if actual.get("type") != nuevo.get("type"):
                    cambios.append({
                        "tipo": "tipo_cambiado",
                        "campo": campo,
                        "tipo_anterior": actual.get("type"),
                        "tipo_nuevo": nuevo.get("type"),
                        "impacto": "breaking"
                    })
        
        return cambios
    
    def _evaluar_compatibilidad(self, cambios: List[Dict]) -> bool:
        """Evalúa si los cambios son compatibles"""
        for cambio in cambios:
            if cambio.get("impacto") == "breaking":
                return False
        return True
    
    def obtener_schema_avro_de_diccionario(self, mensaje_dict: Dict) -> Dict:
        """
        Genera esquema Avro automáticamente desde un diccionario
        Siguiendo patrón de AeroAlpes para generación automática
        
        Args:
            mensaje_dict: Diccionario con datos del mensaje
            
        Returns:
            Esquema Avro generado
        """
        def inferir_tipo_avro(valor):
            """Infiere tipo Avro desde valor Python"""
            if isinstance(valor, bool):
                return "boolean"
            elif isinstance(valor, int):
                return "long"
            elif isinstance(valor, float):
                return "double"
            elif isinstance(valor, str):
                return "string"
            elif isinstance(valor, list):
                if len(valor) > 0:
                    return {"type": "array", "items": inferir_tipo_avro(valor[0])}
                return {"type": "array", "items": "string"}
            elif isinstance(valor, dict):
                return "record"  # Requiere procesamiento recursivo
            else:
                return "string"  # Fallback
        
        campos = []
        for clave, valor in mensaje_dict.items():
            campo = {
                "name": clave,
                "type": inferir_tipo_avro(valor)
            }
            campos.append(campo)
        
        return {
            "type": "record",
            "name": "MensajeGenerado",
            "fields": campos
        }
    
    def listar_schemas_registrados(self) -> List[str]:
        """
        Lista todos los esquemas registrados en Schema Registry
        
        Returns:
            Lista de nombres de topics con esquemas
        """
        try:
            url = f"{self.admin_endpoint}"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error listando esquemas: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Error listando esquemas: {e}")
            return []

# Utilidades para integración con microservicios
def crear_schema_evento_campana() -> Dict:
    """
    Crea esquema para evento de campaña siguiendo patrón AeroAlpes
    """
    return {
        "type": "record",
        "name": "EventoCampanaCreada",
        "namespace": "alpespartner.eventos",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "nombre", "type": "string"},
            {"name": "descripcion", "type": "string"},
            {"name": "fecha_inicio", "type": "string"},
            {"name": "fecha_fin", "type": "string"},
            {"name": "tipo_campana", "type": "string"},
            {"name": "estado", "type": "string"},
            {"name": "timestamp", "type": "long"},
            {"name": "correlation_id", "type": "string"},
            {"name": "version", "type": "int", "default": 1}
        ]
    }

def crear_schema_comando_crear_campana() -> Dict:
    """
    Crea esquema para comando de crear campaña
    Separación comando/evento siguiendo AeroAlpes
    """
    return {
        "type": "record",
        "name": "ComandoCrearCampana",
        "namespace": "alpespartner.comandos",
        "fields": [
            {"name": "nombre", "type": "string"},
            {"name": "descripcion", "type": "string"},
            {"name": "fecha_inicio", "type": "string"},
            {"name": "fecha_fin", "type": "string"},
            {"name": "tipo_campana", "type": "string"},
            {"name": "parametros", "type": ["null", "string"], "default": None},
            {"name": "correlation_id", "type": "string"},
            {"name": "timestamp", "type": "long"}
        ]
    }

# Instancia global para uso en microservicios
schema_manager = SchemaRegistryManager()

if __name__ == "__main__":
    # Ejemplo de uso
    manager = SchemaRegistryManager()
    
    # Registrar esquemas principales
    schema_evento = crear_schema_evento_campana()
    schema_comando = crear_schema_comando_crear_campana()
    
    print("Registrando esquemas...")
    manager.registrar_schema_si_no_existe("evento-campana-creada", schema_evento)
    manager.registrar_schema_si_no_existe("comando-crear-campana", schema_comando)
    
    print("Esquemas registrados:", manager.listar_schemas_registrados())