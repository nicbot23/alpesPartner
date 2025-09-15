"""
Comandos base para el microservicio Marketing
Implementa principios SOLID y CQRS
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
import uuid

# Principio de Responsabilidad Única - Base para todos los comandos
@dataclass
class Comando(ABC):
    """
    Clase base para todos los comandos (Command pattern)
    Principio de Responsabilidad Única - representa una intención de cambio
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    usuario_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.correlation_id:
            self.correlation_id = self.id

@dataclass
class ResultadoComando:
    """
    Resultado de la ejecución de un comando
    Principio de Responsabilidad Única - encapsula el resultado
    """
    exitoso: bool
    mensaje: str = ""
    datos: Optional[Dict[str, Any]] = None
    errores: List[str] = field(default_factory=list)

# Tipos genéricos para principios SOLID
TComando = TypeVar('TComando', bound=Comando)
TResultado = TypeVar('TResultado', bound=ResultadoComando)

class ManejadorComando(ABC, Generic[TComando, TResultado]):
    """
    Interface base para manejadores de comandos
    Principio de Responsabilidad Única - un manejador por comando
    Principio de Inversión de Dependencias - abstracción en lugar de concreción
    """
    
    @abstractmethod
    async def handle(self, comando: TComando) -> TResultado:
        """Maneja la ejecución del comando"""
        pass

class BusComandos(ABC):
    """
    Interface para el bus de comandos
    Principio de Segregación de Interfaces - específico para comandos
    Principio de Abierto/Cerrado - extensible para nuevos comandos
    """
    
    @abstractmethod
    async def ejecutar(self, comando: TComando) -> TResultado:
        """Ejecuta un comando a través del bus"""
        pass
    
    @abstractmethod
    def registrar_manejador(
        self, 
        tipo_comando: type, 
        manejador: ManejadorComando[TComando, TResultado]
    ) -> None:
        """Registra un manejador para un tipo de comando específico"""
        pass

class RepositorioComandos(ABC):
    """
    Interface para repositorio de comandos (Command Sourcing)
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def guardar_comando(self, comando: Comando) -> None:
        """Guarda comando para auditoría/replay"""
        pass
    
    @abstractmethod
    async def obtener_comandos_por_correlacion(self, correlation_id: str) -> List[Comando]:
        """Obtiene comandos por correlation_id"""
        pass
    
    @abstractmethod
    async def obtener_historial_comandos(
        self, 
        entidad_id: str, 
        desde: datetime = None,
        hasta: datetime = None
    ) -> List[Comando]:
        """Obtiene historial de comandos para una entidad"""
        pass

class ValidadorComando(ABC, Generic[TComando]):
    """
    Interface para validadores de comandos
    Principio de Responsabilidad Única - separar validación de ejecución
    """
    
    @abstractmethod
    async def validar(self, comando: TComando) -> List[str]:
        """
        Valida un comando y retorna lista de errores
        Lista vacía significa comando válido
        """
        pass

class InterceptorComando(ABC):
    """
    Interface para interceptors de comandos (Cross-cutting concerns)
    Principio de Responsabilidad Única - aspectos transversales
    """
    
    @abstractmethod
    async def antes_ejecutar(self, comando: Comando) -> None:
        """Se ejecuta antes del comando"""
        pass
    
    @abstractmethod
    async def despues_ejecutar(self, comando: Comando, resultado: ResultadoComando) -> None:
        """Se ejecuta después del comando"""
        pass
    
    @abstractmethod
    async def en_error(self, comando: Comando, error: Exception) -> None:
        """Se ejecuta cuando hay error en el comando"""
        pass

@dataclass
class ComandoConRespuesta(Comando):
    """Comando que espera un resultado específico.
    Se mantiene para compatibilidad con imports existentes.
    """
    # Puede ampliarse con campos adicionales si se requiere
    pass

class BusComandosImplemetacion(BusComandos):
    """
    Implementación concreta del bus de comandos
    Principio de Responsabilidad Única - orquestar ejecución de comandos
    """
    
    def __init__(
        self,
        repositorio_comandos: Optional[RepositorioComandos] = None,
        interceptors: List[InterceptorComando] = None
    ):
        self._manejadores: Dict[type, ManejadorComando] = {}
        self._validadores: Dict[type, List[ValidadorComando]] = {}
        self._repositorio = repositorio_comandos
        self._interceptors = interceptors or []
    
    def registrar_manejador(
        self, 
        tipo_comando: type, 
        manejador: ManejadorComando[TComando, TResultado]
    ) -> None:
        """Registra manejador siguiendo principio Abierto/Cerrado"""
        self._manejadores[tipo_comando] = manejador
    
    def registrar_validador(
        self,
        tipo_comando: type,
        validador: ValidadorComando[TComando]
    ) -> None:
        """Registra validador para un tipo de comando"""
        if tipo_comando not in self._validadores:
            self._validadores[tipo_comando] = []
        self._validadores[tipo_comando].append(validador)
    
    def agregar_interceptor(self, interceptor: InterceptorComando) -> None:
        """Agrega interceptor siguiendo principio Abierto/Cerrado"""
        self._interceptors.append(interceptor)
    
    async def ejecutar(self, comando: TComando) -> TResultado:
        """
        Ejecuta comando con pipeline completo:
        1. Interceptors (antes)
        2. Validación
        3. Guardado (si hay repositorio)
        4. Ejecución del manejador
        5. Interceptors (después)
        """
        tipo_comando = type(comando)
        
        try:
            # 1. Ejecutar interceptors antes
            for interceptor in self._interceptors:
                await interceptor.antes_ejecutar(comando)
            
            # 2. Validar comando
            errores = await self._validar_comando(comando)
            if errores:
                return TResultado(
                    exitoso=False,
                    mensaje="Errores de validación",
                    errores=errores
                )
            
            # 3. Guardar comando (Command Sourcing)
            if self._repositorio:
                await self._repositorio.guardar_comando(comando)
            
            # 4. Obtener y ejecutar manejador
            if tipo_comando not in self._manejadores:
                raise ValueError(f"No hay manejador registrado para {tipo_comando}")
            
            manejador = self._manejadores[tipo_comando]
            resultado = await manejador.handle(comando)
            
            # 5. Ejecutar interceptors después
            for interceptor in self._interceptors:
                await interceptor.despues_ejecutar(comando, resultado)
            
            return resultado
            
        except Exception as e:
            # Ejecutar interceptors de error
            for interceptor in self._interceptors:
                await interceptor.en_error(comando, e)
            
            return TResultado(
                exitoso=False,
                mensaje=f"Error ejecutando comando: {str(e)}",
                errores=[str(e)]
            )
    
    async def _validar_comando(self, comando: TComando) -> List[str]:
        """Ejecuta todos los validadores para el comando"""
        tipo_comando = type(comando)
        errores = []
        
        validadores = self._validadores.get(tipo_comando, [])
        for validador in validadores:
            errores_validador = await validador.validar(comando)
            errores.extend(errores_validador)
        
        return errores

# Factory para crear instancias siguiendo principio de Inversión de Dependencias
class FabricaBusComandos(ABC):
    """
    Factory para crear bus de comandos
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def crear_bus_comandos(self) -> BusComandos:
        """Crea una instancia del bus de comandos"""
        pass
    
    @abstractmethod
    def crear_repositorio_comandos(self) -> RepositorioComandos:
        """Crea una instancia del repositorio de comandos"""
        pass

# Alias para mantener nombre usado en __init__ (corrección de typo)
BusComandosImplementacion = BusComandosImplemetacion