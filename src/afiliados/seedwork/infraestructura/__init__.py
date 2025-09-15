"""
Interfaces de infraestructura para el microservicio Afiliados
Implementa principios SOLID y patrones de arquitectura
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from datetime import datetime

from ..dominio.entidades import EntidadRaiz, AgregacionRaiz, UnidadDeTrabajo
from ..aplicacion.comandos import Comando, ResultadoComando
from ..aplicacion.consultas import Consulta, ResultadoPaginado

T = TypeVar('T', bound=EntidadRaiz)
TAgregado = TypeVar('TAgregado', bound=AgregacionRaiz)
TComando = TypeVar('TComando', bound=Comando)
TConsulta = TypeVar('TConsulta', bound=Consulta)

class Mapeador(ABC, Generic[T]):
    """
    Interface base para mapeadores (Mapper pattern)
    Principio de Responsabilidad Única - convertir entre modelos
    """
    
    @abstractmethod
    def entidad_a_dto(self, entidad: T) -> Dict[str, Any]:
        """Convierte entidad de dominio a DTO"""
        pass
    
    @abstractmethod
    def dto_a_entidad(self, dto: Dict[str, Any]) -> T:
        """Convierte DTO a entidad de dominio"""
        pass

class MapeadorConsulta(ABC, Generic[T]):
    """
    Interface para mapeadores específicos de consultas
    Principio de Segregación de Interfaces
    """
    
    @abstractmethod
    def entidad_a_dto_lectura(self, entidad: T) -> Dict[str, Any]:
        """Convierte entidad a DTO optimizado para lectura"""
        pass
    
    @abstractmethod
    def resultado_query_a_dto(self, resultado: Any) -> Dict[str, Any]:
        """Convierte resultado de query de base de datos a DTO"""
        pass

class RepositorioSQL(ABC, Generic[TAgregado]):
    """
    Interface específica para repositorios SQL
    Implementa Repository pattern con operaciones específicas de SQL
    """
    
    @abstractmethod
    async def iniciar_transaccion(self) -> UnidadDeTrabajo:
        """Inicia una nueva transacción"""
        pass
    
    @abstractmethod
    async def ejecutar_sql(self, query: str, parametros: Dict[str, Any] = None) -> Any:
        """Ejecuta una consulta SQL directa"""
        pass
    
    @abstractmethod
    async def ejecutar_sql_bulk(self, queries: List[tuple]) -> None:
        """Ejecuta múltiples consultas en lote"""
        pass

class CacheRepositorio(ABC, Generic[T]):
    """
    Interface para repositorio con cache
    Principio de Segregación de Interfaces
    """
    
    @abstractmethod
    async def obtener_desde_cache(self, clave: str) -> Optional[T]:
        """Obtiene entidad desde cache"""
        pass
    
    @abstractmethod
    async def guardar_en_cache(self, clave: str, entidad: T, ttl: int = 300) -> None:
        """Guarda entidad en cache con TTL"""
        pass
    
    @abstractmethod
    async def invalidar_cache(self, clave: str) -> None:
        """Invalida entrada del cache"""
        pass
    
    @abstractmethod
    async def invalidar_cache_patron(self, patron: str) -> None:
        """Invalida entradas del cache que coincidan con un patrón"""
        pass

class FabricaRepositorio(ABC):
    """
    Factory para crear repositorios
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def crear_repositorio_afiliados(self):
        """Crea repositorio de afiliados"""
        pass
    
    @abstractmethod
    def crear_repositorio_consultas_afiliados(self):
        """Crea repositorio de consultas de afiliados"""
        pass

class ConexionBaseDatos(ABC):
    """
    Interface para manejo de conexiones a base de datos
    Principio de Responsabilidad Única
    """
    
    @abstractmethod
    async def conectar(self) -> None:
        """Establece conexión con la base de datos"""
        pass
    
    @abstractmethod
    async def desconectar(self) -> None:
        """Cierra conexión con la base de datos"""
        pass
    
    @abstractmethod
    async def obtener_sesion(self) -> Any:
        """Obtiene sesión de base de datos"""
        pass
    
    @abstractmethod
    async def validar_conexion(self) -> bool:
        """Valida si la conexión está activa"""
        pass

class ConfiguracionInfraestructura(ABC):
    """
    Interface para configuración de infraestructura
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def obtener_configuracion_bd(self) -> Dict[str, Any]:
        """Obtiene configuración de base de datos"""
        pass
    
    @abstractmethod
    def obtener_configuracion_cache(self) -> Dict[str, Any]:
        """Obtiene configuración de cache"""
        pass
    
    @abstractmethod
    def obtener_configuracion_pulsar(self) -> Dict[str, Any]:
        """Obtiene configuración de Apache Pulsar"""
        pass
    
    @abstractmethod
    def obtener_configuracion_observabilidad(self) -> Dict[str, Any]:
        """Obtiene configuración de logging y métricas"""
        pass

class ServicioLogging(ABC):
    """
    Interface para servicio de logging
    Principio de Segregación de Interfaces
    """
    
    @abstractmethod
    def info(self, mensaje: str, contexto: Dict[str, Any] = None) -> None:
        """Log nivel info"""
        pass
    
    @abstractmethod
    def advertencia(self, mensaje: str, contexto: Dict[str, Any] = None) -> None:
        """Log nivel advertencia"""
        pass
    
    @abstractmethod
    def error(self, mensaje: str, excepcion: Exception = None, contexto: Dict[str, Any] = None) -> None:
        """Log nivel error"""
        pass
    
    @abstractmethod
    def debug(self, mensaje: str, contexto: Dict[str, Any] = None) -> None:
        """Log nivel debug"""
        pass

class ServicioMetricas(ABC):
    """
    Interface para métricas y observabilidad
    Principio de Responsabilidad Única
    """
    
    @abstractmethod
    def incrementar_contador(self, nombre: str, etiquetas: Dict[str, str] = None) -> None:
        """Incrementa un contador"""
        pass
    
    @abstractmethod
    def registrar_gauge(self, nombre: str, valor: float, etiquetas: Dict[str, str] = None) -> None:
        """Registra un gauge"""
        pass
    
    @abstractmethod
    def registrar_histograma(self, nombre: str, valor: float, etiquetas: Dict[str, str] = None) -> None:
        """Registra valor en histograma"""
        pass
    
    @abstractmethod
    def medir_tiempo(self, nombre: str, etiquetas: Dict[str, str] = None):
        """Context manager para medir tiempo de ejecución"""
        pass

class ManejadorExcepciones(ABC):
    """
    Interface para manejo centralizado de excepciones
    Principio de Responsabilidad Única
    """
    
    @abstractmethod
    async def manejar_excepcion_dominio(self, excepcion: Exception, contexto: Dict[str, Any]) -> None:
        """Maneja excepciones de dominio"""
        pass
    
    @abstractmethod
    async def manejar_excepcion_infraestructura(self, excepcion: Exception, contexto: Dict[str, Any]) -> None:
        """Maneja excepciones de infraestructura"""
        pass
    
    @abstractmethod
    async def manejar_excepcion_aplicacion(self, excepcion: Exception, contexto: Dict[str, Any]) -> None:
        """Maneja excepciones de aplicación"""
        pass

class ValidadorEsquemas(ABC):
    """
    Interface para validación de esquemas
    Principio de Segregación de Interfaces
    """
    
    @abstractmethod
    def validar_comando(self, comando: TComando) -> List[str]:
        """Valida estructura de comando"""
        pass
    
    @abstractmethod
    def validar_consulta(self, consulta: TConsulta) -> List[str]:
        """Valida estructura de consulta"""
        pass
    
    @abstractmethod
    def validar_dto(self, dto: Dict[str, Any], esquema: str) -> List[str]:
        """Valida DTO contra esquema"""
        pass

class AdaptadorMensajeria(ABC):
    """
    Interface para adaptador de mensajería (Apache Pulsar)
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def publicar(self, topico: str, mensaje: Dict[str, Any], headers: Dict[str, str] = None) -> None:
        """Publica mensaje en tópico"""
        pass
    
    @abstractmethod
    async def suscribirse(self, topico: str, grupo_consumidor: str, manejador) -> None:
        """Se suscribe a un tópico con un manejador"""
        pass
    
    @abstractmethod
    async def crear_topico(self, nombre: str, particiones: int = 1) -> None:
        """Crea un nuevo tópico"""
        pass
    
    @abstractmethod
    async def cerrar_conexion(self) -> None:
        """Cierra conexiones de mensajería"""
        pass