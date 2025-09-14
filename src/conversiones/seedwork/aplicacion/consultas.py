"""
Consultas base para el microservicio Conversiones
Implementa principios SOLID y patrón Query con CQRS
Separación total de comandos y consultas (CQS)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable, Union
import uuid

# Principio de Responsabilidad Única - Base para todas las consultas
@dataclass(frozen=True)
class Consulta(ABC):
    """
    Base abstracta para todas las consultas
    Principio de Responsabilidad Única - representa una solicitud de información
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha_creacion: datetime = field(default_factory=datetime.now)
    usuario_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadatos: Dict[str, Any] = field(default_factory=dict)
    
    # Configuración de consulta
    paginacion: Optional[Dict[str, Any]] = None
    filtros: Dict[str, Any] = field(default_factory=dict)
    ordenamiento: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if not self.correlation_id:
            object.__setattr__(self, 'correlation_id', self.id)

# Consultas con respuesta específica
TResultado = TypeVar('TResultado')

@dataclass(frozen=True)
class ConsultaConResultado(Consulta, Generic[TResultado]):
    """
    Base para consultas que retornan un resultado específico
    Principio de Responsabilidad Única - consulta con resultado tipado
    """
    pass

# Interfaces para manejadores (Principio de Inversión de Dependencias)
TConsulta = TypeVar('TConsulta', bound=Consulta)

class ManejadorConsulta(ABC, Generic[TConsulta, TResultado]):
    """
    Interface base para manejadores de consultas
    Principio de Responsabilidad Única - un manejador por tipo de consulta
    """
    
    @abstractmethod
    async def manejar(self, consulta: TConsulta) -> TResultado:
        """Maneja la consulta y retorna resultado"""
        pass

# Validadores de consultas (Principio de Segregación de Interfaces)
class ValidadorConsulta(ABC, Generic[TConsulta]):
    """
    Interface para validadores de consultas
    Principio de Responsabilidad Única - validación específica
    """
    
    @abstractmethod
    async def validar(self, consulta: TConsulta) -> List[str]:
        """Valida consulta y retorna lista de errores"""
        pass

# Interceptores para consultas (Principio Abierto/Cerrado)
class InterceptorConsulta(ABC, Generic[TConsulta]):
    """
    Interface para interceptores de consultas
    Principio de Responsabilidad Única - aspecto transversal
    """
    
    @abstractmethod
    async def antes_de_ejecutar(self, consulta: TConsulta) -> TConsulta:
        """Procesa consulta antes de ejecución"""
        pass
    
    @abstractmethod
    async def despues_de_ejecutar(self, consulta: TConsulta, resultado: Any) -> Any:
        """Procesa resultado después de ejecución"""
        pass
    
    @abstractmethod
    async def en_error(self, consulta: TConsulta, excepcion: Exception) -> None:
        """Maneja errores durante ejecución"""
        pass

# Bus de consultas principal
class BusConsultas(ABC):
    """
    Interface para el bus de consultas
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def ejecutar(self, consulta: Consulta) -> Any:
        """Ejecuta consulta a través del bus"""
        pass
    
    @abstractmethod
    def registrar_manejador(self, tipo_consulta: type, manejador: ManejadorConsulta) -> None:
        """Registra manejador para tipo de consulta"""
        pass
    
    @abstractmethod
    def registrar_validador(self, tipo_consulta: type, validador: ValidadorConsulta) -> None:
        """Registra validador para tipo de consulta"""
        pass
    
    @abstractmethod
    def registrar_interceptor(self, interceptor: InterceptorConsulta) -> None:
        """Registra interceptor global"""
        pass

# Repositorio de consultas para auditoría y caching
class RepositorioConsultas(ABC):
    """
    Interface para auditar y cachear consultas ejecutadas
    Principio de Inversión de Dependencias - auditoría y cache de consultas
    """
    
    @abstractmethod
    async def guardar_consulta(self, consulta: Consulta, resultado: Any, tiempo_ejecucion: float) -> None:
        """Guarda consulta ejecutada"""
        pass
    
    @abstractmethod
    async def obtener_cache(self, clave_cache: str) -> Optional[Any]:
        """Obtiene resultado en cache"""
        pass
    
    @abstractmethod
    async def guardar_cache(self, clave_cache: str, resultado: Any, ttl_segundos: int = 300) -> None:
        """Guarda resultado en cache"""
        pass
    
    @abstractmethod
    async def obtener_estadisticas_consultas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de consultas"""
        pass

# Implementación concreta del bus
class BusConsultasImplementacion(BusConsultas):
    """
    Implementación concreta del bus de consultas
    Principio de Responsabilidad Única - coordinación de consultas
    """
    
    def __init__(self, repositorio_consultas: Optional[RepositorioConsultas] = None):
        self._manejadores: Dict[type, ManejadorConsulta] = {}
        self._validadores: Dict[type, List[ValidadorConsulta]] = {}
        self._interceptores: List[InterceptorConsulta] = []
        self._repositorio = repositorio_consultas
        self._cache_habilitado = True
    
    def registrar_manejador(self, tipo_consulta: type, manejador: ManejadorConsulta) -> None:
        """Registra manejador siguiendo principio Abierto/Cerrado"""
        self._manejadores[tipo_consulta] = manejador
    
    def registrar_validador(self, tipo_consulta: type, validador: ValidadorConsulta) -> None:
        """Registra validador específico para tipo de consulta"""
        if tipo_consulta not in self._validadores:
            self._validadores[tipo_consulta] = []
        self._validadores[tipo_consulta].append(validador)
    
    def registrar_interceptor(self, interceptor: InterceptorConsulta) -> None:
        """Registra interceptor global"""
        self._interceptores.append(interceptor)
    
    async def ejecutar(self, consulta: Consulta) -> Any:
        """
        Ejecuta consulta con pipeline completo
        1. Validación
        2. Cache check
        3. Interceptores (before)
        4. Ejecución
        5. Interceptores (after)
        6. Cache save
        7. Auditoría
        """
        consulta_procesada = consulta
        resultado = None
        tiempo_inicio = datetime.now()
        
        try:
            # 1. Validación
            await self._validar_consulta(consulta_procesada)
            
            # 2. Verificar cache
            if self._cache_habilitado and self._repositorio:
                clave_cache = self._generar_clave_cache(consulta_procesada)
                resultado_cache = await self._repositorio.obtener_cache(clave_cache)
                if resultado_cache is not None:
                    return resultado_cache
            
            # 3. Interceptores - antes
            for interceptor in self._interceptores:
                consulta_procesada = await interceptor.antes_de_ejecutar(consulta_procesada)
            
            # 4. Ejecución principal
            manejador = self._obtener_manejador(type(consulta_procesada))
            resultado = await manejador.manejar(consulta_procesada)
            
            # 5. Interceptores - después
            for interceptor in self._interceptores:
                resultado = await interceptor.despues_de_ejecutar(consulta_procesada, resultado)
            
            # 6. Guardar en cache
            if self._cache_habilitado and self._repositorio and resultado is not None:
                clave_cache = self._generar_clave_cache(consulta_procesada)
                ttl = self._obtener_ttl_cache(consulta_procesada)
                await self._repositorio.guardar_cache(clave_cache, resultado, ttl)
            
            return resultado
            
        except Exception as e:
            # Notificar interceptores del error
            for interceptor in self._interceptores:
                try:
                    await interceptor.en_error(consulta_procesada, e)
                except:
                    pass  # No propagar errores de interceptores
            
            raise e
            
        finally:
            # 7. Auditoría
            if self._repositorio:
                try:
                    tiempo_ejecucion = (datetime.now() - tiempo_inicio).total_seconds()
                    await self._repositorio.guardar_consulta(consulta_procesada, resultado, tiempo_ejecucion)
                except:
                    pass  # No fallar por errores de auditoría
    
    async def _validar_consulta(self, consulta: Consulta) -> None:
        """Valida consulta usando validadores registrados"""
        tipo_consulta = type(consulta)
        validadores = self._validadores.get(tipo_consulta, [])
        
        errores = []
        for validador in validadores:
            errores_validador = await validador.validar(consulta)
            errores.extend(errores_validador)
        
        if errores:
            raise ValueError(f"Errores de validación: {', '.join(errores)}")
    
    def _obtener_manejador(self, tipo_consulta: type) -> ManejadorConsulta:
        """Obtiene manejador registrado para tipo de consulta"""
        manejador = self._manejadores.get(tipo_consulta)
        if not manejador:
            raise ValueError(f"No hay manejador registrado para consulta {tipo_consulta.__name__}")
        return manejador
    
    def _generar_clave_cache(self, consulta: Consulta) -> str:
        """Genera clave única para cache"""
        import hashlib
        import json
        
        datos_consulta = {
            "tipo": consulta.__class__.__name__,
            "filtros": consulta.filtros,
            "paginacion": consulta.paginacion,
            "ordenamiento": consulta.ordenamiento,
            "usuario_id": consulta.usuario_id
        }
        
        json_str = json.dumps(datos_consulta, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def _obtener_ttl_cache(self, consulta: Consulta) -> int:
        """Obtiene TTL en segundos para cache según tipo de consulta"""
        # TTL diferenciado por tipo de consulta
        ttl_map = {
            "ConsultarConversiones": 300,  # 5 minutos
            "ConsultarComisiones": 600,    # 10 minutos
            "ConsultarEstadisticas": 120,  # 2 minutos
        }
        
        return ttl_map.get(consulta.__class__.__name__, 300)

# Interceptores predefinidos para consultas
class InterceptorLoggingConsultas(InterceptorConsulta):
    """
    Interceptor para logging de consultas
    Principio de Responsabilidad Única - logging
    """
    
    def __init__(self, logger=None):
        import logging
        self.logger = logger or logging.getLogger(__name__)
    
    async def antes_de_ejecutar(self, consulta: Consulta) -> Consulta:
        """Log antes de ejecutar"""
        self.logger.info(f"Ejecutando consulta {consulta.__class__.__name__} (ID: {consulta.id})")
        return consulta
    
    async def despues_de_ejecutar(self, consulta: Consulta, resultado: Any) -> Any:
        """Log después de ejecutar"""
        count = len(resultado) if isinstance(resultado, (list, tuple)) else 1
        self.logger.info(f"Consulta {consulta.__class__.__name__} ejecutada - {count} resultados")
        return resultado
    
    async def en_error(self, consulta: Consulta, excepcion: Exception) -> None:
        """Log en caso de error"""
        self.logger.error(f"Error ejecutando consulta {consulta.__class__.__name__}: {str(excepcion)}")

class InterceptorMetricasConsultas(InterceptorConsulta):
    """
    Interceptor para métricas de consultas
    Principio de Responsabilidad Única - telemetría
    """
    
    def __init__(self):
        self.metricas = {}
    
    async def antes_de_ejecutar(self, consulta: Consulta) -> Consulta:
        """Registra inicio de ejecución"""
        nombre_consulta = consulta.__class__.__name__
        if nombre_consulta not in self.metricas:
            self.metricas[nombre_consulta] = {
                "total": 0, 
                "errores": 0, 
                "tiempo_total": 0,
                "resultados_promedio": 0,
                "cache_hits": 0
            }
        
        consulta.metadatos["tiempo_inicio"] = datetime.now()
        return consulta
    
    async def despues_de_ejecutar(self, consulta: Consulta, resultado: Any) -> Any:
        """Registra ejecución exitosa"""
        nombre_consulta = consulta.__class__.__name__
        tiempo_inicio = consulta.metadatos.get("tiempo_inicio")
        
        if tiempo_inicio:
            duracion = (datetime.now() - tiempo_inicio).total_seconds()
            self.metricas[nombre_consulta]["total"] += 1
            self.metricas[nombre_consulta]["tiempo_total"] += duracion
            
            # Registrar cantidad de resultados
            count = len(resultado) if isinstance(resultado, (list, tuple)) else 1
            total_ejecuciones = self.metricas[nombre_consulta]["total"]
            promedio_anterior = self.metricas[nombre_consulta]["resultados_promedio"]
            nuevo_promedio = ((promedio_anterior * (total_ejecuciones - 1)) + count) / total_ejecuciones
            self.metricas[nombre_consulta]["resultados_promedio"] = nuevo_promedio
        
        return resultado
    
    async def en_error(self, consulta: Consulta, excepcion: Exception) -> None:
        """Registra error"""
        nombre_consulta = consulta.__class__.__name__
        self.metricas[nombre_consulta]["errores"] += 1
    
    def registrar_cache_hit(self, nombre_consulta: str) -> None:
        """Registra uso exitoso de cache"""
        if nombre_consulta in self.metricas:
            self.metricas[nombre_consulta]["cache_hits"] += 1
    
    def obtener_metricas(self) -> Dict[str, Any]:
        """Obtiene métricas consolidadas"""
        return self.metricas.copy()

# Validadores específicos para Conversiones
class ValidadorConsultaConversion(ValidadorConsulta):
    """
    Validador base para consultas de conversiones
    Principio de Responsabilidad Única - validación específica de consultas
    """
    
    async def validar(self, consulta: Consulta) -> List[str]:
        """Validaciones base para consultas de conversiones"""
        errores = []
        
        # Validar paginación si está presente
        if consulta.paginacion:
            if "limite" in consulta.paginacion:
                limite = consulta.paginacion["limite"]
                if not isinstance(limite, int) or limite <= 0 or limite > 1000:
                    errores.append("limite debe ser un entero entre 1 y 1000")
            
            if "offset" in consulta.paginacion:
                offset = consulta.paginacion["offset"]
                if not isinstance(offset, int) or offset < 0:
                    errores.append("offset debe ser un entero no negativo")
        
        # Validar filtros de fecha
        for campo_fecha in ["fecha_desde", "fecha_hasta"]:
            if campo_fecha in consulta.filtros:
                valor = consulta.filtros[campo_fecha]
                if not isinstance(valor, (str, datetime)):
                    errores.append(f"{campo_fecha} debe ser string o datetime")
        
        return errores

# Factory para crear bus de consultas
class FabricaBusConsultas:
    """
    Factory para crear instancias del bus de consultas
    Principio de Responsabilidad Única - creación centralizada
    """
    
    @staticmethod
    def crear_bus_basico() -> BusConsultas:
        """Crea bus básico sin cache ni auditoría"""
        return BusConsultasImplementacion()
    
    @staticmethod
    def crear_bus_con_logging() -> BusConsultas:
        """Crea bus con logging"""
        bus = BusConsultasImplementacion()
        bus.registrar_interceptor(InterceptorLoggingConsultas())
        return bus
    
    @staticmethod
    def crear_bus_completo(repositorio_consultas: RepositorioConsultas) -> BusConsultas:
        """Crea bus completo con cache, auditoría, logging y métricas"""
        bus = BusConsultasImplementacion(repositorio_consultas)
        bus.registrar_interceptor(InterceptorLoggingConsultas())
        bus.registrar_interceptor(InterceptorMetricasConsultas())
        return bus

# Decorador para registro automático de manejadores
def manejador_consulta(tipo_consulta: type):
    """
    Decorador para registro automático de manejadores de consultas
    Principio de Inversión de Control
    """
    def decorador(clase_manejador):
        # Aquí iría lógica para registro automático
        # Por ahora solo marcar la clase
        clase_manejador._tipo_consulta = tipo_consulta
        return clase_manejador
    return decorador

# Helpers para construcción de consultas
class ConstructorConsulta:
    """
    Builder para construir consultas complejas
    Principio de Responsabilidad Única - construcción fluida
    """
    
    def __init__(self, tipo_consulta: type):
        self.tipo_consulta = tipo_consulta
        self._filtros = {}
        self._paginacion = None
        self._ordenamiento = None
        self._usuario_id = None
        self._metadatos = {}
    
    def con_filtro(self, campo: str, valor: Any) -> 'ConstructorConsulta':
        """Añade filtro"""
        self._filtros[campo] = valor
        return self
    
    def con_paginacion(self, limite: int, offset: int = 0) -> 'ConstructorConsulta':
        """Configura paginación"""
        self._paginacion = {"limite": limite, "offset": offset}
        return self
    
    def ordenado_por(self, campo: str, direccion: str = "ASC") -> 'ConstructorConsulta':
        """Configura ordenamiento"""
        self._ordenamiento = {"campo": campo, "direccion": direccion}
        return self
    
    def para_usuario(self, usuario_id: str) -> 'ConstructorConsulta':
        """Configura usuario"""
        self._usuario_id = usuario_id
        return self
    
    def con_metadatos(self, **metadatos) -> 'ConstructorConsulta':
        """Añade metadatos"""
        self._metadatos.update(metadatos)
        return self
    
    def construir(self) -> Consulta:
        """Construye la consulta final"""
        return self.tipo_consulta(
            filtros=self._filtros,
            paginacion=self._paginacion,
            ordenamiento=self._ordenamiento,
            usuario_id=self._usuario_id,
            metadatos=self._metadatos
        )