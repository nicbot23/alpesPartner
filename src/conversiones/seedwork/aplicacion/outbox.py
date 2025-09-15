"""
Patrón Outbox específico para el microservicio Conversiones
Garantiza consistencia eventual con eventos de dominio e integración
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import uuid
import json

# Estados del Outbox
class EstadoOutbox(Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    REINTENTANDO = "reintentando"

# Tipos de eventos específicos para Conversiones
class TipoEventoConversion(Enum):
    # Eventos de dominio
    CONVERSION_INICIADA = "conversion_iniciada"
    CONVERSION_VALIDADA = "conversion_validada"
    CONVERSION_COMPLETADA = "conversion_completada"
    CONVERSION_RECHAZADA = "conversion_rechazada"
    COMISION_CALCULADA = "comision_calculada"
    COMISION_APLICADA = "comision_aplicada"
    
    # Eventos de integración
    CONVERSION_DETECTADA_INTEGRACION = "conversion_detectada_integracion"
    COMISION_GENERADA_INTEGRACION = "comision_generada_integracion"
    NOTIFICAR_MARKETING_CONVERSION = "notificar_marketing_conversion"
    NOTIFICAR_AFILIADOS_COMISION = "notificar_afiliados_comision"

@dataclass(frozen=True)
class EntradaOutbox:
    """
    Entrada del Outbox para eventos de Conversiones
    Principio de Responsabilidad Única - representa un evento pendiente de publicar
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agregado_id: str = ""  # ID de Conversión o Comisión
    agregado_tipo: str = ""  # "Conversion" o "Comision"
    tipo_evento: TipoEventoConversion = TipoEventoConversion.CONVERSION_INICIADA
    datos_evento: Dict[str, Any] = field(default_factory=dict)
    metadatos: Dict[str, Any] = field(default_factory=dict)
    
    # Estado y control
    estado: EstadoOutbox = EstadoOutbox.PENDIENTE
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_procesamiento: Optional[datetime] = None
    fecha_completado: Optional[datetime] = None
    
    # Control de reintentos
    intentos: int = 0
    max_intentos: int = 5
    proximo_intento: Optional[datetime] = None
    
    # Información de error
    ultimo_error: Optional[str] = None
    
    # Información de routing para Pulsar
    topico_destino: str = ""
    clave_particion: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Configuración específica
    es_evento_dominio: bool = True  # False para eventos de integración
    requiere_orden: bool = False  # True para eventos que deben procesarse en orden
    prioridad: int = 5  # 1 = alta, 5 = normal, 10 = baja

    def to_dict(self) -> Dict[str, Any]:
        """Convierte entrada a diccionario para persistencia"""
        return {
            "id": self.id,
            "agregado_id": self.agregado_id,
            "agregado_tipo": self.agregado_tipo,
            "tipo_evento": self.tipo_evento.value,
            "datos_evento": self.datos_evento,
            "metadatos": self.metadatos,
            "estado": self.estado.value,
            "fecha_creacion": self.fecha_creacion.isoformat(),
            "fecha_procesamiento": self.fecha_procesamiento.isoformat() if self.fecha_procesamiento else None,
            "fecha_completado": self.fecha_completado.isoformat() if self.fecha_completado else None,
            "intentos": self.intentos,
            "max_intentos": self.max_intentos,
            "proximo_intento": self.proximo_intento.isoformat() if self.proximo_intento else None,
            "ultimo_error": self.ultimo_error,
            "topico_destino": self.topico_destino,
            "clave_particion": self.clave_particion,
            "headers": self.headers,
            "es_evento_dominio": self.es_evento_dominio,
            "requiere_orden": self.requiere_orden,
            "prioridad": self.prioridad
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntradaOutbox':
        """Crea entrada desde diccionario"""
        return cls(
            id=data["id"],
            agregado_id=data["agregado_id"],
            agregado_tipo=data["agregado_tipo"],
            tipo_evento=TipoEventoConversion(data["tipo_evento"]),
            datos_evento=data["datos_evento"],
            metadatos=data["metadatos"],
            estado=EstadoOutbox(data["estado"]),
            fecha_creacion=datetime.fromisoformat(data["fecha_creacion"]),
            fecha_procesamiento=datetime.fromisoformat(data["fecha_procesamiento"]) if data["fecha_procesamiento"] else None,
            fecha_completado=datetime.fromisoformat(data["fecha_completado"]) if data["fecha_completado"] else None,
            intentos=data["intentos"],
            max_intentos=data["max_intentos"],
            proximo_intento=datetime.fromisoformat(data["proximo_intento"]) if data["proximo_intento"] else None,
            ultimo_error=data["ultimo_error"],
            topico_destino=data["topico_destino"],
            clave_particion=data["clave_particion"],
            headers=data["headers"],
            es_evento_dominio=data["es_evento_dominio"],
            requiere_orden=data["requiere_orden"],
            prioridad=data["prioridad"]
        )

# Interface del repositorio Outbox
class RepositorioOutbox(ABC):
    """
    Interface para el repositorio del patrón Outbox
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def guardar(self, entrada: EntradaOutbox) -> None:
        """Guarda entrada en el outbox"""
        pass
    
    @abstractmethod
    async def obtener_pendientes(self, limite: int = 100, solo_disponibles: bool = True) -> List[EntradaOutbox]:
        """Obtiene entradas pendientes de procesar"""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, entrada_id: str) -> Optional[EntradaOutbox]:
        """Obtiene entrada por ID"""
        pass
    
    @abstractmethod
    async def obtener_por_agregado(self, agregado_id: str, agregado_tipo: str) -> List[EntradaOutbox]:
        """Obtiene entradas por agregado"""
        pass
    
    @abstractmethod
    async def marcar_procesando(self, entrada_id: str) -> None:
        """Marca entrada como procesándose"""
        pass
    
    @abstractmethod
    async def marcar_completado(self, entrada_id: str) -> None:
        """Marca entrada como completada"""
        pass
    
    @abstractmethod
    async def marcar_fallido(self, entrada_id: str, error: str, incrementar_intentos: bool = True) -> None:
        """Marca entrada como fallida"""
        pass
    
    @abstractmethod
    async def limpiar_completados(self, dias_antiguedad: int = 7) -> int:
        """Limpia entradas completadas antiguas"""
        pass
    
    @abstractmethod
    async def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del outbox"""
        pass

# Procesador de eventos Outbox
class ProcesadorOutbox(ABC):
    """
    Interface para procesar eventos del Outbox
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def procesar_entrada(self, entrada: EntradaOutbox) -> bool:
        """Procesa una entrada del outbox. Retorna True si fue exitoso"""
        pass
    
    @abstractmethod
    def puede_procesar(self, tipo_evento: TipoEventoConversion) -> bool:
        """Determina si puede procesar este tipo de evento"""
        pass

# Servicio Outbox principal
class ServicioOutbox:
    """
    Servicio principal para manejar el patrón Outbox en Conversiones
    Principio de Responsabilidad Única - coordinación del outbox
    """
    
    def __init__(self, 
                 repositorio: RepositorioOutbox,
                 procesadores: List[ProcesadorOutbox]):
        self.repositorio = repositorio
        self.procesadores = procesadores
        self._configuracion = ConfiguracionOutbox()
    
    async def publicar_evento_dominio(self, 
                                    agregado_id: str,
                                    agregado_tipo: str,
                                    tipo_evento: TipoEventoConversion,
                                    datos_evento: Dict[str, Any],
                                    metadatos: Optional[Dict[str, Any]] = None) -> str:
        """Publica evento de dominio al outbox"""
        entrada = self._crear_entrada_evento(
            agregado_id=agregado_id,
            agregado_tipo=agregado_tipo,
            tipo_evento=tipo_evento,
            datos_evento=datos_evento,
            metadatos=metadatos or {},
            es_evento_dominio=True
        )
        
        await self.repositorio.guardar(entrada)
        return entrada.id
    
    async def publicar_evento_integracion(self,
                                        agregado_id: str,
                                        agregado_tipo: str,
                                        tipo_evento: TipoEventoConversion,
                                        datos_evento: Dict[str, Any],
                                        topico_destino: str,
                                        metadatos: Optional[Dict[str, Any]] = None) -> str:
        """Publica evento de integración al outbox"""
        entrada = self._crear_entrada_evento(
            agregado_id=agregado_id,
            agregado_tipo=agregado_tipo,
            tipo_evento=tipo_evento,
            datos_evento=datos_evento,
            metadatos=metadatos or {},
            es_evento_dominio=False,
            topico_destino=topico_destino
        )
        
        await self.repositorio.guardar(entrada)
        return entrada.id
    
    async def procesar_pendientes(self) -> Dict[str, Any]:
        """Procesa entradas pendientes del outbox"""
        estadisticas = {
            "procesados": 0,
            "exitosos": 0,
            "fallidos": 0,
            "errores": []
        }
        
        entradas = await self.repositorio.obtener_pendientes(
            limite=self._configuracion.lote_procesamiento
        )
        
        for entrada in entradas:
            estadisticas["procesados"] += 1
            
            try:
                await self.repositorio.marcar_procesando(entrada.id)
                
                procesador = self._obtener_procesador(entrada.tipo_evento)
                if not procesador:
                    raise ValueError(f"No hay procesador para evento {entrada.tipo_evento}")
                
                exitoso = await procesador.procesar_entrada(entrada)
                
                if exitoso:
                    await self.repositorio.marcar_completado(entrada.id)
                    estadisticas["exitosos"] += 1
                else:
                    await self.repositorio.marcar_fallido(entrada.id, "Procesamiento falló")
                    estadisticas["fallidos"] += 1
                    
            except Exception as e:
                error_msg = str(e)
                await self.repositorio.marcar_fallido(entrada.id, error_msg)
                estadisticas["fallidos"] += 1
                estadisticas["errores"].append({
                    "entrada_id": entrada.id,
                    "error": error_msg
                })
        
        return estadisticas
    
    def _crear_entrada_evento(self, 
                            agregado_id: str,
                            agregado_tipo: str,
                            tipo_evento: TipoEventoConversion,
                            datos_evento: Dict[str, Any],
                            metadatos: Dict[str, Any],
                            es_evento_dominio: bool,
                            topico_destino: str = "") -> EntradaOutbox:
        """Crea entrada de outbox"""
        
        # Configurar tópico destino basado en tipo de evento
        if not topico_destino:
            topico_destino = self._obtener_topico_por_evento(tipo_evento)
        
        # Configurar prioridad
        prioridad = self._obtener_prioridad_evento(tipo_evento)
        
        # Configurar si requiere orden
        requiere_orden = tipo_evento in [
            TipoEventoConversion.CONVERSION_INICIADA,
            TipoEventoConversion.CONVERSION_COMPLETADA,
            TipoEventoConversion.COMISION_CALCULADA
        ]
        
        return EntradaOutbox(
            agregado_id=agregado_id,
            agregado_tipo=agregado_tipo,
            tipo_evento=tipo_evento,
            datos_evento=datos_evento,
            metadatos=metadatos,
            topico_destino=topico_destino,
            clave_particion=agregado_id,  # Usar agregado_id como clave de partición
            es_evento_dominio=es_evento_dominio,
            requiere_orden=requiere_orden,
            prioridad=prioridad,
            headers={
                "evento_tipo": tipo_evento.value,
                "agregado_tipo": agregado_tipo,
                "microservicio": "conversiones",
                "version": "1.0"
            }
        )
    
    def _obtener_procesador(self, tipo_evento: TipoEventoConversion) -> Optional[ProcesadorOutbox]:
        """Obtiene procesador apropiado para tipo de evento"""
        for procesador in self.procesadores:
            if procesador.puede_procesar(tipo_evento):
                return procesador
        return None
    
    def _obtener_topico_por_evento(self, tipo_evento: TipoEventoConversion) -> str:
        """Mapea tipo de evento a tópico de Pulsar"""
        mapeo_topicos = {
            # Eventos de dominio
            TipoEventoConversion.CONVERSION_INICIADA: "persistent://public/default/conversiones-dominio",
            TipoEventoConversion.CONVERSION_VALIDADA: "persistent://public/default/conversiones-dominio",
            TipoEventoConversion.CONVERSION_COMPLETADA: "persistent://public/default/conversiones-dominio",
            TipoEventoConversion.CONVERSION_RECHAZADA: "persistent://public/default/conversiones-dominio",
            TipoEventoConversion.COMISION_CALCULADA: "persistent://public/default/conversiones-dominio",
            TipoEventoConversion.COMISION_APLICADA: "persistent://public/default/conversiones-dominio",
            
            # Eventos de integración
            TipoEventoConversion.CONVERSION_DETECTADA_INTEGRACION: "persistent://public/default/integracion-conversiones",
            TipoEventoConversion.COMISION_GENERADA_INTEGRACION: "persistent://public/default/integracion-conversiones",
            TipoEventoConversion.NOTIFICAR_MARKETING_CONVERSION: "persistent://public/default/marketing-notificaciones",
            TipoEventoConversion.NOTIFICAR_AFILIADOS_COMISION: "persistent://public/default/afiliados-notificaciones"
        }
        
        return mapeo_topicos.get(tipo_evento, "persistent://public/default/conversiones-eventos")
    
    def _obtener_prioridad_evento(self, tipo_evento: TipoEventoConversion) -> int:
        """Determina prioridad del evento"""
        prioridades_altas = [
            TipoEventoConversion.CONVERSION_COMPLETADA,
            TipoEventoConversion.COMISION_APLICADA
        ]
        
        prioridades_bajas = [
            TipoEventoConversion.CONVERSION_INICIADA
        ]
        
        if tipo_evento in prioridades_altas:
            return 1  # Alta prioridad
        elif tipo_evento in prioridades_bajas:
            return 10  # Baja prioridad
        else:
            return 5  # Prioridad normal

# Configuración del Outbox
@dataclass
class ConfiguracionOutbox:
    """Configuración para el servicio Outbox"""
    lote_procesamiento: int = 100
    intervalo_procesamiento_segundos: int = 30
    max_intentos_default: int = 5
    dias_retencion_completados: int = 7
    timeout_procesamiento_segundos: int = 300

# Factory para crear servicio Outbox
class FabricaServicioOutbox:
    """
    Factory para crear instancias del servicio Outbox
    Principio de Responsabilidad Única - creación centralizada
    """
    
    @staticmethod
    def crear_servicio(repositorio: RepositorioOutbox,
                      procesadores: List[ProcesadorOutbox]) -> ServicioOutbox:
        """Crea servicio Outbox con configuración estándar"""
        return ServicioOutbox(repositorio, procesadores)
    
    @staticmethod
    def crear_servicio_con_configuracion(repositorio: RepositorioOutbox,
                                        procesadores: List[ProcesadorOutbox],
                                        configuracion: ConfiguracionOutbox) -> ServicioOutbox:
        """Crea servicio Outbox con configuración personalizada"""
        servicio = ServicioOutbox(repositorio, procesadores)
        servicio._configuracion = configuracion
        return servicio

# Helpers para crear eventos específicos de Conversiones
class FactoriaEventosConversion:
    """
    Factory para crear eventos específicos de Conversiones
    Principio de Responsabilidad Única - creación de eventos
    """
    
    @staticmethod
    def crear_evento_conversion_iniciada(conversion_id: str, datos_conversion: Dict[str, Any]) -> Dict[str, Any]:
        """Crea evento de conversión iniciada"""
        return {
            "conversion_id": conversion_id,
            "timestamp": datetime.now().isoformat(),
            "datos_conversion": datos_conversion,
            "version": "1.0"
        }
    
    @staticmethod
    def crear_evento_comision_calculada(conversion_id: str, comision_id: str, 
                                      monto_comision: float, porcentaje: float) -> Dict[str, Any]:
        """Crea evento de comisión calculada"""
        return {
            "conversion_id": conversion_id,
            "comision_id": comision_id,
            "monto_comision": monto_comision,
            "porcentaje": porcentaje,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    @staticmethod
    def crear_evento_integracion_marketing(conversion_id: str, campana_id: str,
                                         datos_conversion: Dict[str, Any]) -> Dict[str, Any]:
        """Crea evento de integración con Marketing"""
        return {
            "conversion_id": conversion_id,
            "campana_id": campana_id,
            "datos_conversion": datos_conversion,
            "timestamp": datetime.now().isoformat(),
            "microservicio_origen": "conversiones",
            "version": "1.0"
        }
    
    @staticmethod
    def crear_evento_integracion_afiliados(comision_id: str, afiliado_id: str,
                                         monto_comision: float) -> Dict[str, Any]:
        """Crea evento de integración con Afiliados"""
        return {
            "comision_id": comision_id,
            "afiliado_id": afiliado_id,
            "monto_comision": monto_comision,
            "timestamp": datetime.now().isoformat(),
            "microservicio_origen": "conversiones",
            "version": "1.0"
        }