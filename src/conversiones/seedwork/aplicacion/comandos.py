"""
Comandos base para el microservicio Conversiones
Implementa principios SOLID y patrón Command con CQRS
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable, Union
import uuid

# Principio de Responsabilidad Única - Base para todos los comandos
@dataclass(frozen=True)
class Comando(ABC):
    """
    Base abstracta para todos los comandos
    Principio de Responsabilidad Única - representa una intención de cambio
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha_creacion: datetime = field(default_factory=datetime.now)
    usuario_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadatos: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.correlation_id:
            object.__setattr__(self, 'correlation_id', self.id)

# Comandos con respuesta específica
TRespuesta = TypeVar('TRespuesta')

@dataclass(frozen=True)
class ComandoConRespuesta(Comando, Generic[TRespuesta]):
    """
    Base para comandos que retornan una respuesta específica
    Principio de Responsabilidad Única - comando con resultado tipado
    """
    pass

# Interfaces para manejadores (Principio de Inversión de Dependencias)
TComando = TypeVar('TComando', bound=Comando)

class ManejadorComando(ABC, Generic[TComando, TRespuesta]):
    """
    Interface base para manejadores de comandos
    Principio de Responsabilidad Única - un manejador por tipo de comando
    """
    
    @abstractmethod
    async def manejar(self, comando: TComando) -> TRespuesta:
        """Maneja el comando y retorna resultado"""
        pass

# Validadores de comandos (Principio de Segregación de Interfaces)
class ValidadorComando(ABC, Generic[TComando]):
    """
    Interface para validadores de comandos
    Principio de Responsabilidad Única - validación específica
    """
    
    @abstractmethod
    async def validar(self, comando: TComando) -> List[str]:
        """Valida comando y retorna lista de errores"""
        pass

# Interceptores (Principio Abierto/Cerrado)
class InterceptorComando(ABC, Generic[TComando]):
    """
    Interface para interceptores de comandos
    Principio de Responsabilidad Única - aspecto transversal
    """
    
    @abstractmethod
    async def antes_de_ejecutar(self, comando: TComando) -> TComando:
        """Procesa comando antes de ejecución"""
        pass
    
    @abstractmethod
    async def despues_de_ejecutar(self, comando: TComando, resultado: Any) -> Any:
        """Procesa resultado después de ejecución"""
        pass
    
    @abstractmethod
    async def en_error(self, comando: TComando, excepcion: Exception) -> None:
        """Maneja errores durante ejecución"""
        pass

# Bus de comandos principal
class BusComandos(ABC):
    """
    Interface para el bus de comandos
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def ejecutar(self, comando: Comando) -> Any:
        """Ejecuta comando a través del bus"""
        pass
    
    @abstractmethod
    def registrar_manejador(self, tipo_comando: type, manejador: ManejadorComando) -> None:
        """Registra manejador para tipo de comando"""
        pass
    
    @abstractmethod
    def registrar_validador(self, tipo_comando: type, validador: ValidadorComando) -> None:
        """Registra validador para tipo de comando"""
        pass
    
    @abstractmethod
    def registrar_interceptor(self, interceptor: InterceptorComando) -> None:
        """Registra interceptor global"""
        pass

# Repositorio de comandos para auditoría
class RepositorioComandos(ABC):
    """
    Interface para persistir comandos ejecutados
    Principio de Inversión de Dependencias - auditoría de comandos
    """
    
    @abstractmethod
    async def guardar_comando(self, comando: Comando, resultado: Any, error: Optional[str] = None) -> None:
        """Guarda comando ejecutado"""
        pass
    
    @abstractmethod
    async def obtener_comandos_por_usuario(self, usuario_id: str) -> List[Dict[str, Any]]:
        """Obtiene comandos ejecutados por usuario"""
        pass
    
    @abstractmethod
    async def obtener_comandos_por_correlacion(self, correlation_id: str) -> List[Dict[str, Any]]:
        """Obtiene comandos por correlation ID"""
        pass

# Implementación concreta del bus
class BusComandosImplementacion(BusComandos):
    """
    Implementación concreta del bus de comandos
    Principio de Responsabilidad Única - coordinación de comandos
    """
    
    def __init__(self, repositorio_comandos: Optional[RepositorioComandos] = None):
        self._manejadores: Dict[type, ManejadorComando] = {}
        self._validadores: Dict[type, List[ValidadorComando]] = {}
        self._interceptores: List[InterceptorComando] = []
        self._repositorio = repositorio_comandos
    
    def registrar_manejador(self, tipo_comando: type, manejador: ManejadorComando) -> None:
        """Registra manejador siguiendo principio Abierto/Cerrado"""
        self._manejadores[tipo_comando] = manejador
    
    def registrar_validador(self, tipo_comando: type, validador: ValidadorComando) -> None:
        """Registra validador específico para tipo de comando"""
        if tipo_comando not in self._validadores:
            self._validadores[tipo_comando] = []
        self._validadores[tipo_comando].append(validador)
    
    def registrar_interceptor(self, interceptor: InterceptorComando) -> None:
        """Registra interceptor global"""
        self._interceptores.append(interceptor)
    
    async def ejecutar(self, comando: Comando) -> Any:
        """
        Ejecuta comando con pipeline completo
        1. Validación
        2. Interceptores (before)
        3. Ejecución
        4. Interceptores (after)
        5. Auditoría
        """
        comando_procesado = comando
        resultado = None
        error = None
        
        try:
            # 1. Validación
            await self._validar_comando(comando_procesado)
            
            # 2. Interceptores - antes
            for interceptor in self._interceptores:
                comando_procesado = await interceptor.antes_de_ejecutar(comando_procesado)
            
            # 3. Ejecución principal
            manejador = self._obtener_manejador(type(comando_procesado))
            resultado = await manejador.manejar(comando_procesado)
            
            # 4. Interceptores - después
            for interceptor in self._interceptores:
                resultado = await interceptor.despues_de_ejecutar(comando_procesado, resultado)
            
            return resultado
            
        except Exception as e:
            error = str(e)
            
            # Notificar interceptores del error
            for interceptor in self._interceptores:
                try:
                    await interceptor.en_error(comando_procesado, e)
                except:
                    pass  # No propagar errores de interceptores
            
            raise e
            
        finally:
            # 5. Auditoría
            if self._repositorio:
                try:
                    await self._repositorio.guardar_comando(comando_procesado, resultado, error)
                except:
                    pass  # No fallar por errores de auditoría
    
    async def _validar_comando(self, comando: Comando) -> None:
        """Valida comando usando validadores registrados"""
        tipo_comando = type(comando)
        validadores = self._validadores.get(tipo_comando, [])
        
        errores = []
        for validador in validadores:
            errores_validador = await validador.validar(comando)
            errores.extend(errores_validador)
        
        if errores:
            raise ValueError(f"Errores de validación: {', '.join(errores)}")
    
    def _obtener_manejador(self, tipo_comando: type) -> ManejadorComando:
        """Obtiene manejador registrado para tipo de comando"""
        manejador = self._manejadores.get(tipo_comando)
        if not manejador:
            raise ValueError(f"No hay manejador registrado para comando {tipo_comando.__name__}")
        return manejador

# Interceptores predefinidos
class InterceptorLogging(InterceptorComando):
    """
    Interceptor para logging de comandos
    Principio de Responsabilidad Única - logging
    """
    
    def __init__(self, logger=None):
        import logging
        self.logger = logger or logging.getLogger(__name__)
    
    async def antes_de_ejecutar(self, comando: Comando) -> Comando:
        """Log antes de ejecutar"""
        self.logger.info(f"Ejecutando comando {comando.__class__.__name__} (ID: {comando.id})")
        return comando
    
    async def despues_de_ejecutar(self, comando: Comando, resultado: Any) -> Any:
        """Log después de ejecutar"""
        self.logger.info(f"Comando {comando.__class__.__name__} ejecutado exitosamente")
        return resultado
    
    async def en_error(self, comando: Comando, excepcion: Exception) -> None:
        """Log en caso de error"""
        self.logger.error(f"Error ejecutando comando {comando.__class__.__name__}: {str(excepcion)}")

class InterceptorMetricas(InterceptorComando):
    """
    Interceptor para métricas de comandos
    Principio de Responsabilidad Única - telemetría
    """
    
    def __init__(self):
        self.metricas = {}
    
    async def antes_de_ejecutar(self, comando: Comando) -> Comando:
        """Registra inicio de ejecución"""
        nombre_comando = comando.__class__.__name__
        if nombre_comando not in self.metricas:
            self.metricas[nombre_comando] = {"total": 0, "errores": 0, "tiempo_total": 0}
        
        comando.metadatos["tiempo_inicio"] = datetime.now()
        return comando
    
    async def despues_de_ejecutar(self, comando: Comando, resultado: Any) -> Any:
        """Registra ejecución exitosa"""
        nombre_comando = comando.__class__.__name__
        tiempo_inicio = comando.metadatos.get("tiempo_inicio")
        
        if tiempo_inicio:
            duracion = (datetime.now() - tiempo_inicio).total_seconds()
            self.metricas[nombre_comando]["total"] += 1
            self.metricas[nombre_comando]["tiempo_total"] += duracion
        
        return resultado
    
    async def en_error(self, comando: Comando, excepcion: Exception) -> None:
        """Registra error"""
        nombre_comando = comando.__class__.__name__
        self.metricas[nombre_comando]["errores"] += 1
    
    def obtener_metricas(self) -> Dict[str, Any]:
        """Obtiene métricas consolidadas"""
        return self.metricas.copy()

# Validadores específicos para Conversiones
class ValidadorComandoConversion(ValidadorComando):
    """
    Validador base para comandos de conversiones
    Principio de Responsabilidad Única - validación específica de conversiones
    """
    
    async def validar(self, comando: Comando) -> List[str]:
        """Validaciones base para conversiones"""
        errores = []
        
        # Validar usuario_id obligatorio
        if not comando.usuario_id or not comando.usuario_id.strip():
            errores.append("usuario_id es obligatorio")
        
        # Validar correlation_id
        if not comando.correlation_id:
            errores.append("correlation_id es obligatorio")
        
        return errores

# Factory para crear bus de comandos
class FabricaBusComandos:
    """
    Factory para crear instancias del bus de comandos
    Principio de Responsabilidad Única - creación centralizada
    """
    
    @staticmethod
    def crear_bus_basico() -> BusComandos:
        """Crea bus básico sin auditoría"""
        return BusComandosImplementacion()
    
    @staticmethod
    def crear_bus_con_logging() -> BusComandos:
        """Crea bus con logging"""
        bus = BusComandosImplementacion()
        bus.registrar_interceptor(InterceptorLogging())
        return bus
    
    @staticmethod
    def crear_bus_completo(repositorio_comandos: RepositorioComandos) -> BusComandos:
        """Crea bus completo con auditoría, logging y métricas"""
        bus = BusComandosImplementacion(repositorio_comandos)
        bus.registrar_interceptor(InterceptorLogging())
        bus.registrar_interceptor(InterceptorMetricas())
        return bus

# Alias para compatibilidad
ComandoAplicacion = Comando

# Decorador para registro automático de manejadores
def manejador_comando(tipo_comando: type):
    """
    Decorador para registro automático de manejadores
    Principio de Inversión de Control
    """
    def decorador(clase_manejador):
        # Aquí iría lógica para registro automático
        # Por ahora solo marcar la clase
        clase_manejador._tipo_comando = tipo_comando
        return clase_manejador
    return decorador