"""
Repositorios robustos para el microservicio Conversiones
Implementa patrones Repository, DTO, Mapper con circuit breaker y retry policies
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import asyncio
import time
from enum import Enum
import uuid

# Circuit Breaker para resiliencia
class EstadoCircuitBreaker(Enum):
    CERRADO = "cerrado"
    ABIERTO = "abierto"
    MEDIO_ABIERTO = "medio_abierto"

class CircuitBreaker:
    """
    Circuit Breaker para proteger llamadas a infraestructura externa
    Principio de Responsabilidad Única - manejo de fallos de infraestructura
    """
    
    def __init__(self, 
                 limite_fallos: int = 5,
                 timeout_segundos: int = 60,
                 timeout_operacion: int = 30):
        self.limite_fallos = limite_fallos
        self.timeout_segundos = timeout_segundos
        self.timeout_operacion = timeout_operacion
        self.contador_fallos = 0
        self.ultimo_fallo = None
        self.estado = EstadoCircuitBreaker.CERRADO
    
    async def ejecutar(self, operacion, *args, **kwargs):
        """Ejecuta operación con circuit breaker"""
        
        if self.estado == EstadoCircuitBreaker.ABIERTO:
            if self._debe_intentar_cerrar():
                self.estado = EstadoCircuitBreaker.MEDIO_ABIERTO
            else:
                raise Exception("Circuit breaker abierto - operación no permitida")
        
        try:
            # Ejecutar con timeout
            resultado = await asyncio.wait_for(
                operacion(*args, **kwargs),
                timeout=self.timeout_operacion
            )
            
            # Operación exitosa
            if self.estado == EstadoCircuitBreaker.MEDIO_ABIERTO:
                self.estado = EstadoCircuitBreaker.CERRADO
                self.contador_fallos = 0
            
            return resultado
            
        except Exception as e:
            self.contador_fallos += 1
            self.ultimo_fallo = datetime.now()
            
            if self.contador_fallos >= self.limite_fallos:
                self.estado = EstadoCircuitBreaker.ABIERTO
            
            raise e
    
    def _debe_intentar_cerrar(self) -> bool:
        """Determina si debe intentar cerrar el circuit breaker"""
        if not self.ultimo_fallo:
            return True
        
        tiempo_transcurrido = (datetime.now() - self.ultimo_fallo).total_seconds()
        return tiempo_transcurrido >= self.timeout_segundos

# Retry Policy para operaciones transitorias
class RetryPolicy:
    """
    Política de reintentos con backoff exponencial
    Principio de Responsabilidad Única - manejo de reintentos
    """
    
    def __init__(self, 
                 max_intentos: int = 3,
                 delay_inicial: float = 1.0,
                 backoff_factor: float = 2.0,
                 max_delay: float = 60.0):
        self.max_intentos = max_intentos
        self.delay_inicial = delay_inicial
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
    
    async def ejecutar(self, operacion, *args, **kwargs):
        """Ejecuta operación con política de reintentos"""
        ultimo_error = None
        
        for intento in range(self.max_intentos):
            try:
                return await operacion(*args, **kwargs)
            except Exception as e:
                ultimo_error = e
                
                if intento < self.max_intentos - 1:
                    delay = min(
                        self.delay_inicial * (self.backoff_factor ** intento),
                        self.max_delay
                    )
                    await asyncio.sleep(delay)
                else:
                    raise ultimo_error

# DTOs para transferencia de datos
@dataclass
class ConversionDTO:
    """DTO para transferir datos de conversiones"""
    id: str
    conversion_id: str
    campana_id: str
    afiliado_id: str
    usuario_id: str
    tipo_conversion: str
    valor_conversion: float
    moneda: str
    estado: str
    validada: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_validacion: Optional[datetime] = None
    fecha_completado: Optional[datetime] = None
    validador_id: Optional[str] = None
    procesador_id: Optional[str] = None
    reglas_aplicadas: List[str] = field(default_factory=list)
    datos_tracking: Dict[str, Any] = field(default_factory=dict)
    fuente: str = ""
    metadatos: Dict[str, Any] = field(default_factory=dict)
    version: int = 1

@dataclass
class ComisionDTO:
    """DTO para transferir datos de comisiones"""
    id: str
    comision_id: str
    conversion_id: str
    afiliado_id: str
    campana_id: str
    monto_base: float
    porcentaje_comision: float
    monto_comision: float
    moneda: str
    tipo_comision: str
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_calculo: Optional[datetime] = None
    fecha_aplicacion: Optional[datetime] = None
    fecha_pago: Optional[datetime] = None
    balance_anterior: Optional[float] = None
    balance_nuevo: Optional[float] = None
    metodo_pago: Optional[str] = None
    referencia_pago: Optional[str] = None
    reglas_aplicadas: List[str] = field(default_factory=list)
    metadatos: Dict[str, Any] = field(default_factory=dict)
    version: int = 1

# Mappers para conversión entre entidades y DTOs
class ConversionMapper:
    """
    Mapper para convertir entre Conversion y ConversionDTO
    Principio de Responsabilidad Única - conversión de datos
    """
    
    @staticmethod
    def entidad_a_dto(conversion) -> ConversionDTO:
        """Convierte entidad Conversion a DTO"""
        from ..dominio.entidades import Conversion
        
        return ConversionDTO(
            id=str(conversion.id),
            conversion_id=conversion.conversion_id,
            campana_id=conversion.campana_id,
            afiliado_id=conversion.afiliado_id,
            usuario_id=conversion.usuario_id,
            tipo_conversion=conversion.tipo_conversion.value,
            valor_conversion=conversion.valor_conversion.monto,
            moneda=conversion.valor_conversion.moneda,
            estado=conversion.estado.value,
            validada=conversion.validada,
            fecha_creacion=conversion.fecha_creacion,
            fecha_actualizacion=conversion.fecha_actualizacion,
            fecha_validacion=conversion.fecha_validacion,
            fecha_completado=conversion.fecha_completado,
            validador_id=conversion.validador_id,
            procesador_id=conversion.procesador_id,
            reglas_aplicadas=conversion.reglas_aplicadas,
            datos_tracking=conversion.datos_tracking.__dict__,
            fuente=conversion.fuente,
            metadatos=conversion.metadatos,
            version=conversion.version
        )
    
    @staticmethod
    def dto_a_entidad(dto: ConversionDTO):
        """Convierte DTO a entidad Conversion"""
        from ..dominio.entidades import Conversion, ValorMonetario, DatosTracking
        from ..dominio.eventos import TipoConversion, EstadoConversion
        
        conversion = Conversion()
        conversion._id = uuid.UUID(dto.id)
        conversion.conversion_id = dto.conversion_id
        conversion.campana_id = dto.campana_id
        conversion.afiliado_id = dto.afiliado_id
        conversion.usuario_id = dto.usuario_id
        conversion.tipo_conversion = TipoConversion(dto.tipo_conversion)
        conversion.valor_conversion = ValorMonetario(dto.valor_conversion, dto.moneda)
        conversion.estado = EstadoConversion(dto.estado)
        conversion.validada = dto.validada
        conversion.fecha_creacion = dto.fecha_creacion
        conversion.fecha_actualizacion = dto.fecha_actualizacion
        conversion.fecha_validacion = dto.fecha_validacion
        conversion.fecha_completado = dto.fecha_completado
        conversion.validador_id = dto.validador_id
        conversion.procesador_id = dto.procesador_id
        conversion.reglas_aplicadas = dto.reglas_aplicadas
        conversion.datos_tracking = DatosTracking(**dto.datos_tracking)
        conversion.fuente = dto.fuente
        conversion.metadatos = dto.metadatos
        conversion.version = dto.version
        
        return conversion

class ComisionMapper:
    """
    Mapper para convertir entre Comision y ComisionDTO
    Principio de Responsabilidad Única - conversión de datos
    """
    
    @staticmethod
    def entidad_a_dto(comision) -> ComisionDTO:
        """Convierte entidad Comision a DTO"""
        return ComisionDTO(
            id=str(comision.id),
            comision_id=comision.comision_id,
            conversion_id=comision.conversion_id,
            afiliado_id=comision.afiliado_id,
            campana_id=comision.campana_id,
            monto_base=comision.monto_base.monto,
            porcentaje_comision=comision.porcentaje_comision.valor,
            monto_comision=comision.monto_comision.monto,
            moneda=comision.monto_comision.moneda,
            tipo_comision=comision.tipo_comision,
            estado=comision.estado.value,
            fecha_creacion=comision.fecha_creacion,
            fecha_actualizacion=comision.fecha_actualizacion,
            fecha_calculo=comision.fecha_calculo,
            fecha_aplicacion=comision.fecha_aplicacion,
            fecha_pago=comision.fecha_pago,
            balance_anterior=comision.balance_anterior.monto if comision.balance_anterior else None,
            balance_nuevo=comision.balance_nuevo.monto if comision.balance_nuevo else None,
            metodo_pago=comision.metodo_pago,
            referencia_pago=comision.referencia_pago,
            reglas_aplicadas=comision.reglas_aplicadas,
            metadatos=comision.metadatos,
            version=comision.version
        )
    
    @staticmethod
    def dto_a_entidad(dto: ComisionDTO):
        """Convierte DTO a entidad Comision"""
        from ..dominio.entidades import Comision, ValorMonetario, PorcentajeComision
        from ..dominio.eventos import EstadoComision
        
        comision = Comision()
        comision._id = uuid.UUID(dto.id)
        comision.comision_id = dto.comision_id
        comision.conversion_id = dto.conversion_id
        comision.afiliado_id = dto.afiliado_id
        comision.campana_id = dto.campana_id
        comision.monto_base = ValorMonetario(dto.monto_base, dto.moneda)
        comision.porcentaje_comision = PorcentajeComision(dto.porcentaje_comision)
        comision.monto_comision = ValorMonetario(dto.monto_comision, dto.moneda)
        comision.tipo_comision = dto.tipo_comision
        comision.estado = EstadoComision(dto.estado)
        comision.fecha_creacion = dto.fecha_creacion
        comision.fecha_actualizacion = dto.fecha_actualizacion
        comision.fecha_calculo = dto.fecha_calculo
        comision.fecha_aplicacion = dto.fecha_aplicacion
        comision.fecha_pago = dto.fecha_pago
        comision.metodo_pago = dto.metodo_pago
        comision.referencia_pago = dto.referencia_pago
        comision.reglas_aplicadas = dto.reglas_aplicadas
        comision.metadatos = dto.metadatos
        comision.version = dto.version
        
        if dto.balance_anterior is not None:
            comision.balance_anterior = ValorMonetario(dto.balance_anterior, dto.moneda)
        if dto.balance_nuevo is not None:
            comision.balance_nuevo = ValorMonetario(dto.balance_nuevo, dto.moneda)
        
        return comision

# Interfaces de repositorios
class RepositorioConversiones(ABC):
    """
    Interface para el repositorio de conversiones
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def guardar(self, conversion) -> None:
        """Guarda una conversión"""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, conversion_id: str):
        """Obtiene conversión por ID"""
        pass
    
    @abstractmethod
    async def obtener_por_campana(self, campana_id: str, 
                                limite: int = 100, 
                                offset: int = 0) -> List:
        """Obtiene conversiones por campaña"""
        pass
    
    @abstractmethod
    async def obtener_por_afiliado(self, afiliado_id: str,
                                 limite: int = 100,
                                 offset: int = 0) -> List:
        """Obtiene conversiones por afiliado"""
        pass
    
    @abstractmethod
    async def obtener_por_estado(self, estado: str,
                               limite: int = 100,
                               offset: int = 0) -> List:
        """Obtiene conversiones por estado"""
        pass
    
    @abstractmethod
    async def actualizar(self, conversion) -> None:
        """Actualiza una conversión"""
        pass
    
    @abstractmethod
    async def eliminar(self, conversion_id: str) -> None:
        """Elimina una conversión"""
        pass

class RepositorioComisiones(ABC):
    """
    Interface para el repositorio de comisiones
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def guardar(self, comision) -> None:
        """Guarda una comisión"""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, comision_id: str):
        """Obtiene comisión por ID"""
        pass
    
    @abstractmethod
    async def obtener_por_conversion(self, conversion_id: str) -> List:
        """Obtiene comisiones por conversión"""
        pass
    
    @abstractmethod
    async def obtener_por_afiliado(self, afiliado_id: str,
                                 limite: int = 100,
                                 offset: int = 0) -> List:
        """Obtiene comisiones por afiliado"""
        pass
    
    @abstractmethod
    async def obtener_por_estado(self, estado: str,
                               limite: int = 100,
                               offset: int = 0) -> List:
        """Obtiene comisiones por estado"""
        pass
    
    @abstractmethod
    async def actualizar(self, comision) -> None:
        """Actualiza una comisión"""
        pass
    
    @abstractmethod
    async def eliminar(self, comision_id: str) -> None:
        """Elimina una comisión"""
        pass

# Implementación con MySQL y resiliencia
class RepositorioConversionesMySQL(RepositorioConversiones):
    """
    Implementación MySQL del repositorio de conversiones
    Con circuit breaker y retry policies
    """
    
    def __init__(self, conexion_db, logger=None):
        self.conexion = conexion_db
        self.circuit_breaker = CircuitBreaker()
        self.retry_policy = RetryPolicy()
        self.logger = logger
        
    async def guardar(self, conversion) -> None:
        """Guarda conversión con resiliencia"""
        dto = ConversionMapper.entidad_a_dto(conversion)
        
        async def operacion():
            query = """
            INSERT INTO conversiones (
                id, conversion_id, campana_id, afiliado_id, usuario_id,
                tipo_conversion, valor_conversion, moneda, estado, validada,
                fecha_creacion, fecha_actualizacion, fecha_validacion, 
                fecha_completado, validador_id, procesador_id, reglas_aplicadas,
                datos_tracking, fuente, metadatos, version
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            import json
            params = (
                dto.id, dto.conversion_id, dto.campana_id, dto.afiliado_id, dto.usuario_id,
                dto.tipo_conversion, dto.valor_conversion, dto.moneda, dto.estado, dto.validada,
                dto.fecha_creacion, dto.fecha_actualizacion, dto.fecha_validacion,
                dto.fecha_completado, dto.validador_id, dto.procesador_id, 
                json.dumps(dto.reglas_aplicadas), json.dumps(dto.datos_tracking),
                dto.fuente, json.dumps(dto.metadatos), dto.version
            )
            
            await self.conexion.execute(query, params)
        
        await self.circuit_breaker.ejecutar(
            self.retry_policy.ejecutar, operacion
        )
    
    async def obtener_por_id(self, conversion_id: str):
        """Obtiene conversión por ID con resiliencia"""
        
        async def operacion():
            query = """
            SELECT * FROM conversiones WHERE conversion_id = %s
            """
            
            resultado = await self.conexion.fetch_one(query, (conversion_id,))
            if not resultado:
                return None
            
            dto = self._fila_a_dto_conversion(resultado)
            return ConversionMapper.dto_a_entidad(dto)
        
        return await self.circuit_breaker.ejecutar(
            self.retry_policy.ejecutar, operacion
        )
    
    async def obtener_por_campana(self, campana_id: str, 
                                limite: int = 100, 
                                offset: int = 0) -> List:
        """Obtiene conversiones por campaña"""
        
        async def operacion():
            query = """
            SELECT * FROM conversiones 
            WHERE campana_id = %s 
            ORDER BY fecha_creacion DESC 
            LIMIT %s OFFSET %s
            """
            
            resultados = await self.conexion.fetch_all(query, (campana_id, limite, offset))
            
            conversiones = []
            for fila in resultados:
                dto = self._fila_a_dto_conversion(fila)
                conversion = ConversionMapper.dto_a_entidad(dto)
                conversiones.append(conversion)
            
            return conversiones
        
        return await self.circuit_breaker.ejecutar(
            self.retry_policy.ejecutar, operacion
        )
    
    async def obtener_por_afiliado(self, afiliado_id: str,
                                 limite: int = 100,
                                 offset: int = 0) -> List:
        """Obtiene conversiones por afiliado"""
        
        async def operacion():
            query = """
            SELECT * FROM conversiones 
            WHERE afiliado_id = %s 
            ORDER BY fecha_creacion DESC 
            LIMIT %s OFFSET %s
            """
            
            resultados = await self.conexion.fetch_all(query, (afiliado_id, limite, offset))
            
            conversiones = []
            for fila in resultados:
                dto = self._fila_a_dto_conversion(fila)
                conversion = ConversionMapper.dto_a_entidad(dto)
                conversiones.append(conversion)
            
            return conversiones
        
        return await self.circuit_breaker.ejecutar(
            self.retry_policy.ejecutar, operacion
        )
    
    async def obtener_por_estado(self, estado: str,
                               limite: int = 100,
                               offset: int = 0) -> List:
        """Obtiene conversiones por estado"""
        
        async def operacion():
            query = """
            SELECT * FROM conversiones 
            WHERE estado = %s 
            ORDER BY fecha_creacion DESC 
            LIMIT %s OFFSET %s
            """
            
            resultados = await self.conexion.fetch_all(query, (estado, limite, offset))
            
            conversiones = []
            for fila in resultados:
                dto = self._fila_a_dto_conversion(fila)
                conversion = ConversionMapper.dto_a_entidad(dto)
                conversiones.append(conversion)
            
            return conversiones
        
        return await self.circuit_breaker.ejecutar(
            self.retry_policy.ejecutar, operacion
        )
    
    async def actualizar(self, conversion) -> None:
        """Actualiza conversión"""
        dto = ConversionMapper.entidad_a_dto(conversion)
        
        async def operacion():
            query = """
            UPDATE conversiones SET
                tipo_conversion = %s, valor_conversion = %s, moneda = %s,
                estado = %s, validada = %s, fecha_actualizacion = %s,
                fecha_validacion = %s, fecha_completado = %s,
                validador_id = %s, procesador_id = %s, reglas_aplicadas = %s,
                datos_tracking = %s, fuente = %s, metadatos = %s, version = %s
            WHERE conversion_id = %s
            """
            
            import json
            params = (
                dto.tipo_conversion, dto.valor_conversion, dto.moneda,
                dto.estado, dto.validada, dto.fecha_actualizacion,
                dto.fecha_validacion, dto.fecha_completado,
                dto.validador_id, dto.procesador_id, json.dumps(dto.reglas_aplicadas),
                json.dumps(dto.datos_tracking), dto.fuente, json.dumps(dto.metadatos),
                dto.version, dto.conversion_id
            )
            
            await self.conexion.execute(query, params)
        
        await self.circuit_breaker.ejecutar(
            self.retry_policy.ejecutar, operacion
        )
    
    async def eliminar(self, conversion_id: str) -> None:
        """Elimina conversión"""
        
        async def operacion():
            query = "DELETE FROM conversiones WHERE conversion_id = %s"
            await self.conexion.execute(query, (conversion_id,))
        
        await self.circuit_breaker.ejecutar(
            self.retry_policy.ejecutar, operacion
        )
    
    def _fila_a_dto_conversion(self, fila) -> ConversionDTO:
        """Convierte fila de base de datos a DTO"""
        import json
        
        return ConversionDTO(
            id=fila['id'],
            conversion_id=fila['conversion_id'],
            campana_id=fila['campana_id'],
            afiliado_id=fila['afiliado_id'],
            usuario_id=fila['usuario_id'],
            tipo_conversion=fila['tipo_conversion'],
            valor_conversion=float(fila['valor_conversion']),
            moneda=fila['moneda'],
            estado=fila['estado'],
            validada=bool(fila['validada']),
            fecha_creacion=fila['fecha_creacion'],
            fecha_actualizacion=fila['fecha_actualizacion'],
            fecha_validacion=fila['fecha_validacion'],
            fecha_completado=fila['fecha_completado'],
            validador_id=fila['validador_id'],
            procesador_id=fila['procesador_id'],
            reglas_aplicadas=json.loads(fila['reglas_aplicadas']) if fila['reglas_aplicadas'] else [],
            datos_tracking=json.loads(fila['datos_tracking']) if fila['datos_tracking'] else {},
            fuente=fila['fuente'] or "",
            metadatos=json.loads(fila['metadatos']) if fila['metadatos'] else {},
            version=int(fila['version'])
        )

# Factory para crear repositorios
class FabricaRepositorios:
    """
    Factory para crear instancias de repositorios
    Principio de Responsabilidad Única - creación centralizada
    """
    
    @staticmethod
    def crear_repositorio_conversiones_mysql(conexion_db, logger=None) -> RepositorioConversiones:
        """Crea repositorio MySQL para conversiones"""
        return RepositorioConversionesMySQL(conexion_db, logger)
    
    @staticmethod
    def crear_repositorio_comisiones_mysql(conexion_db, logger=None) -> RepositorioComisiones:
        """Crea repositorio MySQL para comisiones"""
        # Implementación similar a ConversionesMySQL
        pass

# Configuración de infraestructura
@dataclass
class ConfiguracionInfraestructura:
    """Configuración para componentes de infraestructura"""
    # Circuit breaker
    circuit_breaker_limite_fallos: int = 5
    circuit_breaker_timeout_segundos: int = 60
    circuit_breaker_timeout_operacion: int = 30
    
    # Retry policy
    retry_max_intentos: int = 3
    retry_delay_inicial: float = 1.0
    retry_backoff_factor: float = 2.0
    retry_max_delay: float = 60.0
    
    # Base de datos
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "conversiones"
    db_user: str = "root"
    db_password: str = ""
    db_pool_size: int = 10
    db_max_overflow: int = 20