"""
Consultas base para el microservicio Marketing
Implementa el lado Query de CQRS con principios SOLID
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
import uuid

# Principio de Responsabilidad Única - Base para todas las consultas
@dataclass
class Consulta(ABC):
    """
    Clase base para todas las consultas (Query pattern)
    Principio de Responsabilidad Única - representa una intención de lectura
    Separación CQRS - consultas separadas de comandos
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    usuario_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.correlation_id:
            self.correlation_id = self.id

@dataclass
class ConsultaConPaginacion(Consulta):
    """Consulta base que incluye parámetros de paginación.
    Se agrega para satisfacer import del seedwork y facilitar queries paginadas.
    """
    pagina: int = 1
    tamaño_pagina: int = 20

@dataclass
class ResultadoPaginado:
    """
    Resultado paginado para consultas
    Principio de Responsabilidad Única - encapsula paginación
    """
    items: List[Dict[str, Any]]
    total: int
    pagina: int
    tamaño_pagina: int
    total_paginas: int
    tiene_siguiente: bool
    tiene_anterior: bool
    
    @classmethod
    def crear(
        cls,
        items: List[Dict[str, Any]],
        total: int,
        pagina: int,
        tamaño_pagina: int
    ) -> 'ResultadoPaginado':
        """Factory method para crear resultado paginado"""
        total_paginas = (total + tamaño_pagina - 1) // tamaño_pagina
        return cls(
            items=items,
            total=total,
            pagina=pagina,
            tamaño_pagina=tamaño_pagina,
            total_paginas=total_paginas,
            tiene_siguiente=pagina < total_paginas,
            tiene_anterior=pagina > 1
        )

# Tipos genéricos para principios SOLID
TConsulta = TypeVar('TConsulta', bound=Consulta)
TResultado = TypeVar('TResultado')

class ManejadorConsulta(ABC, Generic[TConsulta, TResultado]):
    """
    Interface base para manejadores de consultas
    Principio de Responsabilidad Única - un manejador por consulta
    Principio de Inversión de Dependencias - abstracción en lugar de concreción
    Separación CQRS - solo para operaciones de lectura
    """
    
    @abstractmethod
    async def handle(self, consulta: TConsulta) -> TResultado:
        """Maneja la ejecución de la consulta"""
        pass

class BusConsultas(ABC):
    """
    Interface para el bus de consultas
    Principio de Segregación de Interfaces - específico para consultas
    Separación CQRS - bus independiente de comandos
    """
    
    @abstractmethod
    async def ejecutar(self, consulta: TConsulta) -> TResultado:
        """Ejecuta una consulta a través del bus"""
        pass
    
    @abstractmethod
    def registrar_manejador(
        self, 
        tipo_consulta: type, 
        manejador: ManejadorConsulta[TConsulta, TResultado]
    ) -> None:
        """Registra un manejador para un tipo de consulta específico"""
        pass

class RepositorioConsultas(ABC):
    """
    Interface base para repositorios de consultas (Read-only)
    Principio de Inversión de Dependencias
    Separación CQRS - solo operaciones de lectura optimizadas
    """
    
    @abstractmethod
    async def ejecutar_sql(self, query: str, parametros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Ejecuta consulta SQL optimizada para lectura"""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Obtiene entidad por ID optimizada para lectura"""
        pass
    
    @abstractmethod
    async def listar_paginado(
        self,
        filtros: Dict[str, Any] = None,
        ordenamiento: str = None,
        pagina: int = 1,
        tamaño_pagina: int = 20
    ) -> ResultadoPaginado:
        """Lista entidades con paginación optimizada"""
        pass

class CacheConsultas(ABC):
    """
    Interface para cache de consultas
    Principio de Segregación de Interfaces - específico para cache de lectura
    """
    
    @abstractmethod
    async def obtener(self, clave: str) -> Optional[Any]:
        """Obtiene resultado desde cache"""
        pass
    
    @abstractmethod
    async def guardar(self, clave: str, valor: Any, ttl: int = 300) -> None:
        """Guarda resultado en cache con TTL"""
        pass
    
    @abstractmethod
    async def invalidar(self, patron: str) -> None:
        """Invalida cache por patrón"""
        pass

class ValidadorConsulta(ABC, Generic[TConsulta]):
    """
    Interface para validadores de consultas
    Principio de Responsabilidad Única - separar validación de ejecución
    """
    
    @abstractmethod
    async def validar(self, consulta: TConsulta) -> List[str]:
        """
        Valida una consulta y retorna lista de errores
        Lista vacía significa consulta válida
        """
        pass

class InterceptorConsulta(ABC):
    """
    Interface para interceptors de consultas (Cross-cutting concerns)
    Principio de Responsabilidad Única - aspectos transversales
    """
    
    @abstractmethod
    async def antes_ejecutar(self, consulta: Consulta) -> None:
        """Se ejecuta antes de la consulta"""
        pass
    
    @abstractmethod
    async def despues_ejecutar(self, consulta: Consulta, resultado: Any) -> None:
        """Se ejecuta después de la consulta"""
        pass
    
    @abstractmethod
    async def en_error(self, consulta: Consulta, error: Exception) -> None:
        """Se ejecuta cuando hay error en la consulta"""
        pass

class BusConsultasImplementacion(BusConsultas):
    """
    Implementación concreta del bus de consultas
    Principio de Responsabilidad Única - orquestar ejecución de consultas
    Separación CQRS - independiente del bus de comandos
    """
    
    def __init__(
        self,
        cache: Optional[CacheConsultas] = None,
        interceptors: List[InterceptorConsulta] = None
    ):
        self._manejadores: Dict[type, ManejadorConsulta] = {}
        self._validadores: Dict[type, List[ValidadorConsulta]] = {}
        self._cache = cache
        self._interceptors = interceptors or []
    
    def registrar_manejador(
        self, 
        tipo_consulta: type, 
        manejador: ManejadorConsulta[TConsulta, TResultado]
    ) -> None:
        """Registra manejador siguiendo principio Abierto/Cerrado"""
        self._manejadores[tipo_consulta] = manejador
    
    def registrar_validador(
        self,
        tipo_consulta: type,
        validador: ValidadorConsulta[TConsulta]
    ) -> None:
        """Registra validador para un tipo de consulta"""
        if tipo_consulta not in self._validadores:
            self._validadores[tipo_consulta] = []
        self._validadores[tipo_consulta].append(validador)
    
    def agregar_interceptor(self, interceptor: InterceptorConsulta) -> None:
        """Agrega interceptor siguiendo principio Abierto/Cerrado"""
        self._interceptors.append(interceptor)
    
    async def ejecutar(self, consulta: TConsulta) -> TResultado:
        """
        Ejecuta consulta con pipeline optimizado para lectura:
        1. Interceptors (antes)
        2. Validación
        3. Verificar cache
        4. Ejecución del manejador
        5. Guardar en cache
        6. Interceptors (después)
        """
        tipo_consulta = type(consulta)
        
        try:
            # 1. Ejecutar interceptors antes
            for interceptor in self._interceptors:
                await interceptor.antes_ejecutar(consulta)
            
            # 2. Validar consulta
            errores = await self._validar_consulta(consulta)
            if errores:
                raise ValueError(f"Errores de validación: {errores}")
            
            # 3. Verificar cache
            if self._cache:
                clave_cache = self._generar_clave_cache(consulta)
                resultado_cache = await self._cache.obtener(clave_cache)
                if resultado_cache is not None:
                    return resultado_cache
            
            # 4. Obtener y ejecutar manejador
            if tipo_consulta not in self._manejadores:
                raise ValueError(f"No hay manejador registrado para {tipo_consulta}")
            
            manejador = self._manejadores[tipo_consulta]
            resultado = await manejador.handle(consulta)
            
            # 5. Guardar en cache
            if self._cache and resultado:
                clave_cache = self._generar_clave_cache(consulta)
                await self._cache.guardar(clave_cache, resultado)
            
            # 6. Ejecutar interceptors después
            for interceptor in self._interceptors:
                await interceptor.despues_ejecutar(consulta, resultado)
            
            return resultado
            
        except Exception as e:
            # Ejecutar interceptors de error
            for interceptor in self._interceptors:
                await interceptor.en_error(consulta, e)
            raise
    
    async def _validar_consulta(self, consulta: TConsulta) -> List[str]:
        """Ejecuta todos los validadores para la consulta"""
        tipo_consulta = type(consulta)
        errores = []
        
        validadores = self._validadores.get(tipo_consulta, [])
        for validador in validadores:
            errores_validador = await validador.validar(consulta)
            errores.extend(errores_validador)
        
        return errores
    
    def _generar_clave_cache(self, consulta: Consulta) -> str:
        """Genera clave de cache basada en la consulta"""
        import hashlib
        import json
        
        # Crear representación serializable de la consulta
        consulta_dict = {
            'tipo': type(consulta).__name__,
            'datos': consulta.__dict__
        }
        
        # Generar hash para usar como clave
        consulta_json = json.dumps(consulta_dict, sort_keys=True, default=str)
        return hashlib.md5(consulta_json.encode()).hexdigest()

# Factory para crear instancias siguiendo principio de Inversión de Dependencias
class FabricaBusConsultas(ABC):
    """
    Factory para crear bus de consultas
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    def crear_bus_consultas(self) -> BusConsultas:
        """Crea una instancia del bus de consultas"""
        pass
    
    @abstractmethod
    def crear_cache_consultas(self) -> CacheConsultas:
        """Crea una instancia del cache de consultas"""
        pass
    
    @abstractmethod
    def crear_repositorio_consultas(self) -> RepositorioConsultas:
        """Crea una instancia del repositorio de consultas"""
        pass