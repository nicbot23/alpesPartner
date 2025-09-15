"""
Configuración de infraestructura del módulo de comisiones - Marketing Microservice
Configuración de base de datos, conexiones y servicios enterprise
Arquitectura: Configuration Pattern + Dependency Injection + Environment Management
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
from urllib.parse import quote_plus

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================

@dataclass
class ConfiguracionBaseDatos:
    """
    Configuración de base de datos para comisiones
    Principio de Responsabilidad Única - solo configuración DB
    """
    # Conexión principal
    host: str = "localhost"
    puerto: int = 5432
    nombre_bd: str = "marketing_comisiones"
    usuario: str = "marketing_user"
    password: str = ""
    esquema: str = "comisiones"
    
    # Pool de conexiones
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # Configuración SQLAlchemy
    echo_sql: bool = False
    autocommit: bool = False
    autoflush: bool = True
    
    # SSL y seguridad
    ssl_mode: str = "prefer"
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    
    def obtener_url_conexion(self) -> str:
        """Generar URL de conexión PostgreSQL"""
        password_encoded = quote_plus(self.password) if self.password else ""
        
        if password_encoded:
            auth = f"{self.usuario}:{password_encoded}@"
        else:
            auth = f"{self.usuario}@" if self.usuario else ""
        
        url = f"postgresql://{auth}{self.host}:{self.puerto}/{self.nombre_bd}"
        
        # Agregar parámetros SSL si están configurados
        params = []
        if self.ssl_mode != "prefer":
            params.append(f"sslmode={self.ssl_mode}")
        if self.ssl_cert_path:
            params.append(f"sslcert={self.ssl_cert_path}")
        if self.ssl_key_path:
            params.append(f"sslkey={self.ssl_key_path}")
        if self.ssl_ca_path:
            params.append(f"sslrootcert={self.ssl_ca_path}")
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    def obtener_configuracion_engine(self) -> Dict[str, Any]:
        """Obtener configuración para SQLAlchemy Engine"""
        return {
            "echo": self.echo_sql,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "pool_pre_ping": True,  # Verificar conexiones antes de usar
        }

# =============================================================================
# CONFIGURACIÓN DE CACHE
# =============================================================================

@dataclass
class ConfiguracionCache:
    """
    Configuración de cache para consultas de comisiones
    Principio de Responsabilidad Única - solo configuración cache
    """
    # Tipo de cache
    tipo: str = "redis"  # redis, memory, disabled
    
    # Conexión Redis
    host_redis: str = "localhost"
    puerto_redis: int = 6379
    bd_redis: int = 0
    password_redis: Optional[str] = None
    
    # Configuración de cache
    ttl_por_defecto: int = 300  # 5 minutos
    ttl_consultas_estaticas: int = 3600  # 1 hora
    ttl_estadisticas: int = 900  # 15 minutos
    
    # Prefijos para claves
    prefijo_comisiones: str = "marketing:comisiones:"
    prefijo_estadisticas: str = "marketing:stats:"
    prefijo_consultas: str = "marketing:query:"
    
    # Limites
    max_memoria_mb: int = 512
    max_claves: int = 100000
    
    def obtener_url_redis(self) -> str:
        """Generar URL de conexión Redis"""
        if self.password_redis:
            auth = f":{self.password_redis}@"
        else:
            auth = ""
        
        return f"redis://{auth}{self.host_redis}:{self.puerto_redis}/{self.bd_redis}"

# =============================================================================
# CONFIGURACIÓN DE EVENTOS Y MENSAJERÍA
# =============================================================================

@dataclass
class ConfiguracionEventos:
    """
    Configuración de eventos y mensajería
    Principio de Responsabilidad Única - solo configuración eventos
    """
    # Broker de mensajes
    tipo_broker: str = "pulsar"  # pulsar, rabbitmq, kafka
    
    # Conexión Pulsar
    url_pulsar: str = "pulsar://localhost:6650"
    namespace_pulsar: str = "marketing/comisiones"
    
    # Topics de eventos
    topic_comision_calculada: str = "comision-calculada"
    topic_comision_aprobada: str = "comision-aprobada"
    topic_comision_rechazada: str = "comision-rechazada"
    topic_comision_pagada: str = "comision-pagada"
    
    # Configuración de productores
    timeout_envio_ms: int = 5000
    reintentos_envio: int = 3
    batch_size: int = 100
    
    # Configuración de consumidores
    subscription_name: str = "marketing-comisiones-consumer"
    consumer_name: str = "comisiones-handler"
    ack_timeout_ms: int = 30000
    
    # Configuración de retry y dead letter
    max_reintentos_procesamiento: int = 3
    delay_retry_ms: int = 1000
    topic_dead_letter: str = "comisiones-dead-letter"
    
    def obtener_configuracion_productor(self) -> Dict[str, Any]:
        """Obtener configuración para productor de eventos"""
        return {
            "send_timeout_millis": self.timeout_envio_ms,
            "max_pending_messages": self.batch_size,
            "batching_enabled": True,
            "batching_max_messages": self.batch_size,
            "batching_max_allowed_size_in_bytes": 128 * 1024,  # 128KB
        }
    
    def obtener_configuracion_consumidor(self) -> Dict[str, Any]:
        """Obtener configuración para consumidor de eventos"""
        return {
            "subscription_name": self.subscription_name,
            "consumer_name": self.consumer_name,
            "ack_timeout_millis": self.ack_timeout_ms,
            "negative_ack_redelivery_delay_millis": self.delay_retry_ms,
        }

# =============================================================================
# CONFIGURACIÓN DE MONITOREO Y OBSERVABILIDAD
# =============================================================================

@dataclass
class ConfiguracionMonitoreo:
    """
    Configuración de monitoreo, logging y métricas
    Principio de Responsabilidad Única - solo configuración observabilidad
    """
    # Logging
    nivel_log: str = "INFO"
    formato_log: str = "json"
    archivo_log: Optional[str] = None
    rotar_logs: bool = True
    max_size_mb: int = 100
    backup_count: int = 5
    
    # Métricas
    habilitar_metricas: bool = True
    puerto_metricas: int = 8090
    ruta_metricas: str = "/metrics"
    namespace_metricas: str = "marketing_comisiones"
    
    # Tracing distribuido
    habilitar_tracing: bool = True
    jaeger_endpoint: Optional[str] = None
    sample_rate: float = 0.1  # 10% de trazas
    
    # Health checks
    puerto_health: int = 8091
    ruta_health: str = "/health"
    timeout_health_check_ms: int = 5000
    
    def obtener_configuracion_logging(self) -> Dict[str, Any]:
        """Obtener configuración para logging"""
        config = {
            "level": self.nivel_log,
            "format": self.formato_log,
            "handlers": []
        }
        
        if self.archivo_log:
            config["handlers"].append({
                "type": "file",
                "filename": self.archivo_log,
                "max_bytes": self.max_size_mb * 1024 * 1024,
                "backup_count": self.backup_count if self.rotar_logs else 0
            })
        else:
            config["handlers"].append({"type": "console"})
        
        return config

# =============================================================================
# CONFIGURACIÓN PRINCIPAL
# =============================================================================

@dataclass
class ConfiguracionComisiones:
    """
    Configuración principal del módulo de comisiones
    Aggregation Pattern - agrupa todas las configuraciones
    """
    base_datos: ConfiguracionBaseDatos = field(default_factory=ConfiguracionBaseDatos)
    cache: ConfiguracionCache = field(default_factory=ConfiguracionCache)
    eventos: ConfiguracionEventos = field(default_factory=ConfiguracionEventos)
    monitoreo: ConfiguracionMonitoreo = field(default_factory=ConfiguracionMonitoreo)
    
    # Configuración del módulo
    ambiente: str = "desarrollo"  # desarrollo, pruebas, produccion
    debug: bool = True
    version: str = "1.0.0"
    
    # Limites operacionales
    max_comisiones_por_lote: int = 1000
    timeout_operacion_ms: int = 30000
    max_reintentos_operacion: int = 3
    
    # Configuración de negocio
    moneda_por_defecto: str = "COP"
    porcentaje_maximo: float = 50.0
    monto_minimo_comision: float = 1000.0
    
    @classmethod
    def desde_variables_entorno(cls) -> 'ConfiguracionComisiones':
        """Crear configuración desde variables de entorno"""
        config = cls()
        
        # Base de datos
        config.base_datos.host = os.getenv("COMISIONES_DB_HOST", config.base_datos.host)
        config.base_datos.puerto = int(os.getenv("COMISIONES_DB_PORT", str(config.base_datos.puerto)))
        config.base_datos.nombre_bd = os.getenv("COMISIONES_DB_NAME", config.base_datos.nombre_bd)
        config.base_datos.usuario = os.getenv("COMISIONES_DB_USER", config.base_datos.usuario)
        config.base_datos.password = os.getenv("COMISIONES_DB_PASSWORD", config.base_datos.password)
        config.base_datos.echo_sql = os.getenv("COMISIONES_DB_ECHO", "false").lower() == "true"
        
        # Cache
        config.cache.tipo = os.getenv("COMISIONES_CACHE_TYPE", config.cache.tipo)
        config.cache.host_redis = os.getenv("COMISIONES_REDIS_HOST", config.cache.host_redis)
        config.cache.puerto_redis = int(os.getenv("COMISIONES_REDIS_PORT", str(config.cache.puerto_redis)))
        config.cache.password_redis = os.getenv("COMISIONES_REDIS_PASSWORD")
        
        # Eventos
        config.eventos.url_pulsar = os.getenv("COMISIONES_PULSAR_URL", config.eventos.url_pulsar)
        config.eventos.namespace_pulsar = os.getenv("COMISIONES_PULSAR_NAMESPACE", config.eventos.namespace_pulsar)
        
        # General
        config.ambiente = os.getenv("COMISIONES_ENVIRONMENT", config.ambiente)
        config.debug = os.getenv("COMISIONES_DEBUG", "true").lower() == "true"
        
        return config
    
    def validar(self) -> None:
        """Validar configuración"""
        if not self.base_datos.host:
            raise ValueError("Host de base de datos es requerido")
        
        if not self.base_datos.nombre_bd:
            raise ValueError("Nombre de base de datos es requerido")
        
        if self.base_datos.puerto <= 0 or self.base_datos.puerto > 65535:
            raise ValueError("Puerto de base de datos inválido")
        
        if self.cache.tipo not in ["redis", "memory", "disabled"]:
            raise ValueError("Tipo de cache inválido")
        
        if self.eventos.tipo_broker not in ["pulsar", "rabbitmq", "kafka"]:
            raise ValueError("Tipo de broker inválido")
        
        if self.ambiente not in ["desarrollo", "pruebas", "produccion"]:
            raise ValueError("Ambiente inválido")
    
    def es_produccion(self) -> bool:
        """Verificar si está en ambiente de producción"""
        return self.ambiente == "produccion"
    
    def es_desarrollo(self) -> bool:
        """Verificar si está en ambiente de desarrollo"""
        return self.ambiente == "desarrollo"

# =============================================================================
# FACTORY DE CONFIGURACIÓN
# =============================================================================

class FabricaConfiguracion:
    """
    Factory para crear configuraciones según el ambiente
    Principio de Responsabilidad Única - solo creación de configuración
    """
    
    @staticmethod
    def crear_desarrollo() -> ConfiguracionComisiones:
        """Crear configuración para desarrollo"""
        config = ConfiguracionComisiones()
        config.ambiente = "desarrollo"
        config.debug = True
        config.base_datos.echo_sql = True
        config.cache.tipo = "memory"
        config.monitoreo.nivel_log = "DEBUG"
        return config
    
    @staticmethod
    def crear_pruebas() -> ConfiguracionComisiones:
        """Crear configuración para pruebas"""
        config = ConfiguracionComisiones()
        config.ambiente = "pruebas"
        config.debug = False
        config.base_datos.nombre_bd = "marketing_comisiones_test"
        config.cache.tipo = "memory"
        config.eventos.tipo_broker = "memory"  # Mock para pruebas
        config.monitoreo.nivel_log = "WARNING"
        return config
    
    @staticmethod
    def crear_produccion() -> ConfiguracionComisiones:
        """Crear configuración para producción"""
        config = ConfiguracionComisiones.desde_variables_entorno()
        config.ambiente = "produccion"
        config.debug = False
        config.base_datos.echo_sql = False
        config.cache.tipo = "redis"
        config.monitoreo.nivel_log = "INFO"
        config.monitoreo.habilitar_metricas = True
        config.monitoreo.habilitar_tracing = True
        return config
    
    @staticmethod
    def crear_por_ambiente(ambiente: str) -> ConfiguracionComisiones:
        """Crear configuración según ambiente especificado"""
        if ambiente == "desarrollo":
            return FabricaConfiguracion.crear_desarrollo()
        elif ambiente == "pruebas":
            return FabricaConfiguracion.crear_pruebas()
        elif ambiente == "produccion":
            return FabricaConfiguracion.crear_produccion()
        else:
            raise ValueError(f"Ambiente desconocido: {ambiente}")

# =============================================================================
# SINGLETON DE CONFIGURACIÓN GLOBAL
# =============================================================================

class ConfiguracionGlobal:
    """
    Singleton para configuración global del módulo
    Singleton Pattern - una sola instancia de configuración
    """
    _instancia: Optional[ConfiguracionComisiones] = None
    
    @classmethod
    def obtener(cls) -> ConfiguracionComisiones:
        """Obtener instancia de configuración"""
        if cls._instancia is None:
            ambiente = os.getenv("COMISIONES_ENVIRONMENT", "desarrollo")
            cls._instancia = FabricaConfiguracion.crear_por_ambiente(ambiente)
            cls._instancia.validar()
        
        return cls._instancia
    
    @classmethod
    def establecer(cls, config: ConfiguracionComisiones) -> None:
        """Establecer configuración personalizada"""
        config.validar()
        cls._instancia = config
    
    @classmethod
    def reiniciar(cls) -> None:
        """Reiniciar configuración (útil para pruebas)"""
        cls._instancia = None