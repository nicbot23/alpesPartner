"""
Configuración de Topología Descentralizada
Implementa comunicación asíncrona entre microservicios usando Apache Pulsar

Siguiendo recomendaciones de entrega4:
- Comunicación descentralizada vía eventos
- Patrones comando/evento separados
- Schema Registry para evolución de esquemas
- Event Sourcing para comunicación inter-servicios
"""

import json
from typing import Dict, List
from enum import Enum

class TipoEvento(Enum):
    """Tipos de eventos en el ecosistema"""
    COMANDO = "comando"
    EVENTO = "evento"
    QUERY = "query"

class MicroservicioTopologia:
    """Configuración de topología para cada microservicio"""
    
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.eventos_publicados = []
        self.eventos_suscritos = []
        self.comandos_publicados = []
        self.comandos_procesados = []

# Configuración de topología descentralizada
TOPOLOGIA_MICROSERVICIOS = {
    "marketing": {
        "eventos_publicados": [
            "evento-campana-creada",
            "evento-campana-activada", 
            "evento-campana-desactivada",
            "evento-conversion-asignada-campana",
            "evento-comision-calculada"
        ],
        "eventos_suscritos": [
            "evento-conversion-detectada",
            "evento-conversion-confirmada",
            "evento-afiliado-registrado"
        ],
        "comandos_publicados": [
            "comando-calcular-comision",
            "comando-asignar-conversion"
        ],
        "comandos_procesados": [
            "comando-crear-campana",
            "comando-activar-campana",
            "comando-desactivar-campana"
        ]
    },
    
    "conversiones": {
        "eventos_publicados": [
            "evento-conversion-detectada",
            "evento-conversion-validada",
            "evento-conversion-confirmada",
            "evento-conversion-rechazada"
        ],
        "eventos_suscritos": [
            "evento-campana-creada",
            "evento-campana-activada",
            "evento-afiliado-registrado"
        ],
        "comandos_publicados": [
            "comando-validar-conversion",
            "comando-confirmar-conversion"
        ],
        "comandos_procesados": [
            "comando-detectar-conversion",
            "comando-procesar-conversion"
        ]
    },
    
    "afiliados": {
        "eventos_publicados": [
            "evento-afiliado-registrado",
            "evento-afiliado-actualizado", 
            "evento-afiliado-desactivado",
            "evento-afiliado-validado"
        ],
        "eventos_suscritos": [
            "evento-conversion-confirmada",
            "evento-comision-calculada"
        ],
        "comandos_publicados": [
            "comando-validar-afiliado",
            "comando-actualizar-estadisticas"
        ],
        "comandos_procesados": [
            "comando-registrar-afiliado",
            "comando-actualizar-afiliado",
            "comando-desactivar-afiliado"
        ]
    }
}

# Patrones de comunicación asíncrona
PATRONES_COMUNICACION = {
    "creacion_campana": {
        "descripcion": "Flujo completo de creación de campaña",
        "pasos": [
            {
                "paso": 1,
                "microservicio": "marketing",
                "accion": "comando-crear-campana",
                "tipo": TipoEvento.COMANDO.value
            },
            {
                "paso": 2, 
                "microservicio": "marketing",
                "accion": "evento-campana-creada",
                "tipo": TipoEvento.EVENTO.value,
                "suscriptores": ["conversiones", "afiliados"]
            }
        ]
    },
    
    "procesamiento_conversion": {
        "descripcion": "Flujo de detección y procesamiento de conversión",
        "pasos": [
            {
                "paso": 1,
                "microservicio": "conversiones", 
                "accion": "evento-conversion-detectada",
                "tipo": TipoEvento.EVENTO.value,
                "suscriptores": ["marketing"]
            },
            {
                "paso": 2,
                "microservicio": "conversiones",
                "accion": "evento-conversion-confirmada", 
                "tipo": TipoEvento.EVENTO.value,
                "suscriptores": ["marketing", "afiliados"]
            },
            {
                "paso": 3,
                "microservicio": "marketing",
                "accion": "evento-comision-calculada",
                "tipo": TipoEvento.EVENTO.value,
                "suscriptores": ["afiliados"]
            }
        ]
    },
    
    "registro_afiliado": {
        "descripcion": "Flujo de registro y activación de afiliado",
        "pasos": [
            {
                "paso": 1,
                "microservicio": "afiliados",
                "accion": "comando-registrar-afiliado",
                "tipo": TipoEvento.COMANDO.value
            },
            {
                "paso": 2,
                "microservicio": "afiliados", 
                "accion": "evento-afiliado-registrado",
                "tipo": TipoEvento.EVENTO.value,
                "suscriptores": ["marketing", "conversiones"]
            }
        ]
    }
}

# Configuración de topics Pulsar
CONFIGURACION_TOPICS = {
    "tenant": "alpespartner",
    "namespace": "eventos",
    "persistence": "persistent",
    "partitions": 3,
    "retention": {
        "time": "7d",
        "size": "1GB"
    },
    "topics": {
        # Topics de eventos (publicación/suscripción)
        "eventos": [
            "persistent://alpespartner/eventos/evento-campana-creada",
            "persistent://alpespartner/eventos/evento-campana-activada",
            "persistent://alpespartner/eventos/evento-conversion-detectada",
            "persistent://alpespartner/eventos/evento-conversion-confirmada",
            "persistent://alpespartner/eventos/evento-afiliado-registrado",
            "persistent://alpespartner/eventos/evento-comision-calculada"
        ],
        
        # Topics de comandos (point-to-point)
        "comandos": [
            "persistent://alpespartner/comandos/comando-crear-campana",
            "persistent://alpespartner/comandos/comando-detectar-conversion",
            "persistent://alpespartner/comandos/comando-registrar-afiliado",
            "persistent://alpespartner/comandos/comando-calcular-comision"
        ]
    }
}

# Configuración de suscripciones
CONFIGURACION_SUSCRIPCIONES = {
    "marketing-service": {
        "suscripciones": [
            {
                "topic": "persistent://alpespartner/eventos/evento-conversion-detectada",
                "subscription": "marketing-conversion-processor",
                "type": "Shared"
            },
            {
                "topic": "persistent://alpespartner/eventos/evento-afiliado-registrado", 
                "subscription": "marketing-affiliate-processor",
                "type": "Shared"
            }
        ]
    },
    
    "conversiones-service": {
        "suscripciones": [
            {
                "topic": "persistent://alpespartner/eventos/evento-campana-activada",
                "subscription": "conversiones-campaign-processor", 
                "type": "Shared"
            }
        ]
    },
    
    "afiliados-service": {
        "suscripciones": [
            {
                "topic": "persistent://alpespartner/eventos/evento-comision-calculada",
                "subscription": "afiliados-commission-processor",
                "type": "Shared"
            }
        ]
    }
}

def generar_configuracion_docker_compose():
    """
    Genera configuración Docker Compose para topología descentralizada
    """
    return {
        "version": "3.8",
        "services": {
            "pulsar": {
                "image": "apachepulsar/pulsar:3.1.2",
                "container_name": "pulsar-standalone",
                "command": "bin/pulsar standalone",
                "ports": [
                    "6650:6650",  # Pulsar broker
                    "8080:8080"   # Admin API
                ],
                "environment": {
                    "PULSAR_MEM": "-Xms512m -Xmx512m -XX:MaxDirectMemorySize=256m"
                }
            },
            
            "pulsar-manager": {
                "image": "apachepulsar/pulsar-manager:latest",
                "container_name": "pulsar-manager",
                "ports": ["9527:9527"],
                "depends_on": ["pulsar"],
                "environment": {
                    "SPRING_CONFIGURATION_FILE": "/pulsar-manager/pulsar-manager/application.properties"
                }
            }
        }
    }

def validar_topologia():
    """
    Valida que la configuración de topología sea consistente
    """
    errores = []
    
    # Verificar que cada evento publicado tenga al menos un suscriptor
    todos_eventos_publicados = set()
    todos_eventos_suscritos = set()
    
    for servicio, config in TOPOLOGIA_MICROSERVICIOS.items():
        todos_eventos_publicados.update(config["eventos_publicados"])
        todos_eventos_suscritos.update(config["eventos_suscritos"])
    
    eventos_sin_suscriptores = todos_eventos_publicados - todos_eventos_suscritos
    if eventos_sin_suscriptores:
        errores.append(f"Eventos sin suscriptores: {eventos_sin_suscriptores}")
    
    # Verificar que no haya dependencias circulares directas
    for servicio, config in TOPOLOGIA_MICROSERVICIOS.items():
        for evento in config["eventos_publicados"]:
            for otro_servicio, otra_config in TOPOLOGIA_MICROSERVICIOS.items():
                if servicio != otro_servicio and evento in otra_config["eventos_suscritos"]:
                    # Verificar si hay dependencia circular
                    for evento_otro in otra_config["eventos_publicados"]:
                        if evento_otro in config["eventos_suscritos"]:
                            errores.append(f"Posible dependencia circular entre {servicio} y {otro_servicio}")
    
    return errores

def obtener_grafo_eventos():
    """
    Genera representación de grafo de eventos para análisis
    """
    grafo = {"nodos": [], "aristas": []}
    
    # Agregar nodos (microservicios)
    for servicio in TOPOLOGIA_MICROSERVICIOS.keys():
        grafo["nodos"].append({"id": servicio, "tipo": "microservicio"})
    
    # Agregar aristas (comunicación por eventos)
    for servicio, config in TOPOLOGIA_MICROSERVICIOS.items():
        for evento in config["eventos_publicados"]:
            for otro_servicio, otra_config in TOPOLOGIA_MICROSERVICIOS.items():
                if servicio != otro_servicio and evento in otra_config["eventos_suscritos"]:
                    grafo["aristas"].append({
                        "origen": servicio,
                        "destino": otro_servicio, 
                        "evento": evento,
                        "tipo": "asincrono"
                    })
    
    return grafo

if __name__ == "__main__":
    print("=== Configuración de Topología Descentralizada ===")
    print(json.dumps(TOPOLOGIA_MICROSERVICIOS, indent=2))
    
    print("\n=== Validación de Topología ===")
    errores = validar_topologia()
    if errores:
        print("Errores encontrados:")
        for error in errores:
            print(f"- {error}")
    else:
        print("✓ Topología válida")
    
    print("\n=== Grafo de Eventos ===")
    grafo = obtener_grafo_eventos()
    print(json.dumps(grafo, indent=2))