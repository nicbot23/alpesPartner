"""
Despachadores robustos para Apache Pulsar
Implementa patrones de resiliencia y manejo de errores
"""
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import uuid

from ..seedwork.dominio.eventos import EventoIntegracion, DespachadorEventos
from ..seedwork.infraestructura import AdaptadorMensajeria, ServicioLogging, ServicioMetricas

class EstadoMensaje(Enum):
    """Estados de un mensaje en procesamiento"""
    PENDIENTE = "pendiente"
    ENVIANDO = "enviando"
    ENVIADO = "enviado"
    ERROR = "error"
    ERROR_FATAL = "error_fatal"

@dataclass
class ConfiguracionReintento:
    """Configuración para reintentos de mensajes"""
    max_intentos: int = 3
    delay_inicial: float = 1.0
    factor_backoff: float = 2.0
    delay_maximo: float = 30.0
    jitter: bool = True

@dataclass
class ResultadoEnvio:
    """Resultado del envío de un mensaje"""
    exitoso: bool
    mensaje_id: str
    error: Optional[str] = None
    tiempo_procesamiento: Optional[float] = None
    intento: int = 1

class DespachadorPulsarResilient(DespachadorEventos):
    """
    Despachador robusto para Apache Pulsar
    Implementa patrones de resiliencia: circuit breaker, retry, dead letter queue
    """
    
    def __init__(
        self,
        adaptador_pulsar: AdaptadorMensajeria,
        logger: ServicioLogging,
        metricas: ServicioMetricas,
        config_reintento: ConfiguracionReintento = None
    ):
        self._adaptador = adaptador_pulsar
        self._logger = logger
        self._metricas = metricas
        self._config_reintento = config_reintento or ConfiguracionReintento()
        self._circuit_breaker = CircuitBreaker()
        self._cola_dead_letter: List[Dict[str, Any]] = []
        self._activo = True
    
    async def publicar(self, evento: EventoIntegracion) -> ResultadoEnvio:
        """
        Publica evento con manejo robusto de errores
        Implementa circuit breaker y reintentos automáticos
        """
        mensaje_id = str(uuid.uuid4())
        inicio_tiempo = datetime.now()
        
        try:
            # Verificar circuit breaker
            if not self._circuit_breaker.puede_ejecutar():
                raise Exception("Circuit breaker abierto - servicio no disponible")
            
            # Preparar mensaje
            mensaje = self._preparar_mensaje(evento, mensaje_id)
            topico = self._determinar_topico(evento)
            
            # Intentar envío con reintentos
            resultado = await self._enviar_con_reintentos(
                topico=topico,
                mensaje=mensaje,
                mensaje_id=mensaje_id
            )
            
            # Registrar éxito
            if resultado.exitoso:
                self._circuit_breaker.registrar_exito()
                self._metricas.incrementar_contador(
                    "afiliados_eventos_enviados_total",
                    {"tipo_evento": evento.nombre, "topico": topico}
                )
                
                self._logger.info(
                    f"Evento enviado exitosamente",
                    contexto={
                        "mensaje_id": mensaje_id,
                        "tipo_evento": evento.nombre,
                        "topico": topico,
                        "correlation_id": evento.correlation_id
                    }
                )
            else:
                self._circuit_breaker.registrar_fallo()
                await self._manejar_mensaje_fallido(mensaje, resultado.error)
            
            # Registrar métricas de tiempo
            tiempo_procesamiento = (datetime.now() - inicio_tiempo).total_seconds()
            self._metricas.registrar_histograma(
                "afiliados_tiempo_envio_eventos",
                tiempo_procesamiento,
                {"tipo_evento": evento.nombre}
            )
            
            resultado.tiempo_procesamiento = tiempo_procesamiento
            return resultado
            
        except Exception as e:
            self._circuit_breaker.registrar_fallo()
            
            error_msg = f"Error fatal enviando evento: {str(e)}"
            self._logger.error(
                error_msg,
                excepcion=e,
                contexto={
                    "mensaje_id": mensaje_id,
                    "tipo_evento": evento.nombre,
                    "correlation_id": evento.correlation_id
                }
            )
            
            self._metricas.incrementar_contador(
                "afiliados_eventos_error_total",
                {"tipo_evento": evento.nombre, "error": "fatal"}
            )
            
            return ResultadoEnvio(
                exitoso=False,
                mensaje_id=mensaje_id,
                error=error_msg
            )
    
    async def _enviar_con_reintentos(
        self,
        topico: str,
        mensaje: Dict[str, Any],
        mensaje_id: str
    ) -> ResultadoEnvio:
        """Envía mensaje con estrategia de reintentos"""
        
        for intento in range(1, self._config_reintento.max_intentos + 1):
            try:
                await self._adaptador.publicar(
                    topico=topico,
                    mensaje=mensaje,
                    headers={
                        "mensaje_id": mensaje_id,
                        "intento": str(intento),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                return ResultadoEnvio(
                    exitoso=True,
                    mensaje_id=mensaje_id,
                    intento=intento
                )
                
            except Exception as e:
                error_msg = f"Error en intento {intento}: {str(e)}"
                
                self._logger.advertencia(
                    error_msg,
                    contexto={
                        "mensaje_id": mensaje_id,
                        "intento": intento,
                        "max_intentos": self._config_reintento.max_intentos
                    }
                )
                
                # Si no es el último intento, esperar antes del siguiente
                if intento < self._config_reintento.max_intentos:
                    delay = self._calcular_delay_reintento(intento)
                    await asyncio.sleep(delay)
                else:
                    # Último intento fallido
                    return ResultadoEnvio(
                        exitoso=False,
                        mensaje_id=mensaje_id,
                        error=error_msg,
                        intento=intento
                    )
        
        # No debería llegar aquí, pero por seguridad
        return ResultadoEnvio(
            exitoso=False,
            mensaje_id=mensaje_id,
            error="Todos los intentos fallaron"
        )
    
    def _calcular_delay_reintento(self, intento: int) -> float:
        """Calcula delay para reintento con backoff exponencial"""
        delay = self._config_reintento.delay_inicial * (
            self._config_reintento.factor_backoff ** (intento - 1)
        )
        
        delay = min(delay, self._config_reintento.delay_maximo)
        
        # Agregar jitter para evitar thundering herd
        if self._config_reintento.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def _preparar_mensaje(self, evento: EventoIntegracion, mensaje_id: str) -> Dict[str, Any]:
        """Prepara mensaje para envío"""
        return {
            "mensaje_id": mensaje_id,
            "tipo_evento": evento.nombre,
            "datos": evento.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "source_service": evento.source_service,
            "destination_services": evento.destination_services,
            "correlation_id": evento.correlation_id,
            "causation_id": evento.causation_id
        }
    
    def _determinar_topico(self, evento: EventoIntegracion) -> str:
        """Determina el tópico basado en el tipo de evento"""
        topicos_mapping = {
            "AfiliadoAprobadoIntegracion": "afiliados.aprobado",
            "AfiliadoDesactivadoIntegracion": "afiliados.desactivado",
            "DatosAfiliadoActualizadosIntegracion": "afiliados.datos_actualizados"
        }
        
        return topicos_mapping.get(evento.nombre, "afiliados.eventos")
    
    async def _manejar_mensaje_fallido(self, mensaje: Dict[str, Any], error: str) -> None:
        """Maneja mensajes que no pudieron ser enviados"""
        mensaje_dlq = {
            **mensaje,
            "error": error,
            "fecha_error": datetime.now().isoformat(),
            "procesado": False
        }
        
        self._cola_dead_letter.append(mensaje_dlq)
        
        self._logger.error(
            "Mensaje enviado a Dead Letter Queue",
            contexto={
                "mensaje_id": mensaje.get("mensaje_id"),
                "error": error,
                "cola_dlq_tamaño": len(self._cola_dead_letter)
            }
        )
        
        # Alertar si la cola DLQ está creciendo mucho
        if len(self._cola_dead_letter) > 100:
            self._metricas.incrementar_contador(
                "afiliados_dlq_sobrecarga",
                {"tamaño": str(len(self._cola_dead_letter))}
            )
    
    async def procesar_cola_dead_letter(self) -> None:
        """Procesa mensajes en la cola de dead letter"""
        mensajes_procesados = 0
        
        for mensaje in self._cola_dead_letter.copy():
            if mensaje["procesado"]:
                continue
            
            try:
                # Intentar reenviar mensaje
                topico = mensaje.get("topico", "afiliados.eventos")
                await self._adaptador.publicar(topico=topico, mensaje=mensaje)
                
                mensaje["procesado"] = True
                mensajes_procesados += 1
                
                self._logger.info(
                    "Mensaje de DLQ reprocesado exitosamente",
                    contexto={"mensaje_id": mensaje.get("mensaje_id")}
                )
                
            except Exception as e:
                self._logger.error(
                    "Error reprocesando mensaje de DLQ",
                    excepcion=e,
                    contexto={"mensaje_id": mensaje.get("mensaje_id")}
                )
        
        # Limpiar mensajes procesados
        self._cola_dead_letter = [
            msg for msg in self._cola_dead_letter if not msg["procesado"]
        ]
        
        if mensajes_procesados > 0:
            self._logger.info(
                f"Reprocesados {mensajes_procesados} mensajes de DLQ"
            )
    
    async def obtener_estado_salud(self) -> Dict[str, Any]:
        """Obtiene estado de salud del despachador"""
        return {
            "activo": self._activo,
            "circuit_breaker_estado": self._circuit_breaker.estado,
            "mensajes_dlq": len(self._cola_dead_letter),
            "ultimo_check": datetime.now().isoformat()
        }

class CircuitBreaker:
    """
    Implementación de Circuit Breaker pattern
    Previene cascadas de fallos
    """
    
    def __init__(
        self,
        umbral_fallos: int = 5,
        timeout_segundos: int = 60,
        umbral_exito: int = 3
    ):
        self.umbral_fallos = umbral_fallos
        self.timeout_segundos = timeout_segundos
        self.umbral_exito = umbral_exito
        
        self.fallos = 0
        self.exitos_consecutivos = 0
        self.ultimo_fallo = None
        self.estado = "CERRADO"  # CERRADO, ABIERTO, MEDIO_ABIERTO
    
    def puede_ejecutar(self) -> bool:
        """Determina si se puede ejecutar una operación"""
        if self.estado == "CERRADO":
            return True
        
        if self.estado == "ABIERTO":
            if self._timeout_expirado():
                self.estado = "MEDIO_ABIERTO"
                return True
            return False
        
        if self.estado == "MEDIO_ABIERTO":
            return True
        
        return False
    
    def registrar_exito(self) -> None:
        """Registra una operación exitosa"""
        if self.estado == "MEDIO_ABIERTO":
            self.exitos_consecutivos += 1
            if self.exitos_consecutivos >= self.umbral_exito:
                self._cerrar_circuito()
        elif self.estado == "CERRADO":
            self.fallos = 0
    
    def registrar_fallo(self) -> None:
        """Registra una operación fallida"""
        self.fallos += 1
        self.ultimo_fallo = datetime.now()
        self.exitos_consecutivos = 0
        
        if self.fallos >= self.umbral_fallos:
            self.estado = "ABIERTO"
    
    def _timeout_expirado(self) -> bool:
        """Verifica si el timeout del circuit breaker ha expirado"""
        if not self.ultimo_fallo:
            return False
        
        tiempo_transcurrido = (datetime.now() - self.ultimo_fallo).total_seconds()
        return tiempo_transcurrido >= self.timeout_segundos
    
    def _cerrar_circuito(self) -> None:
        """Cierra el circuit breaker"""
        self.estado = "CERRADO"
        self.fallos = 0
        self.exitos_consecutivos = 0

class ConsumidorEventosRobust:
    """
    Consumidor robusto de eventos de Apache Pulsar
    Maneja errores, reintentos y dead letter queues
    """
    
    def __init__(
        self,
        adaptador_pulsar: AdaptadorMensajeria,
        logger: ServicioLogging,
        metricas: ServicioMetricas
    ):
        self._adaptador = adaptador_pulsar
        self._logger = logger
        self._metricas = metricas
        self._manejadores: Dict[str, Callable] = {}
        self._activo = False
    
    def registrar_manejador(self, tipo_evento: str, manejador: Callable) -> None:
        """Registra un manejador para un tipo de evento específico"""
        self._manejadores[tipo_evento] = manejador
        self._logger.info(f"Manejador registrado para evento: {tipo_evento}")
    
    async def iniciar_consumo(self, topicos: List[str], grupo_consumidor: str) -> None:
        """Inicia el consumo de eventos de los tópicos especificados"""
        self._activo = True
        
        for topico in topicos:
            await self._adaptador.suscribirse(
                topico=topico,
                grupo_consumidor=grupo_consumidor,
                manejador=self._procesar_mensaje
            )
        
        self._logger.info(
            f"Consumidor iniciado para tópicos: {topicos}",
            contexto={"grupo_consumidor": grupo_consumidor}
        )
    
    async def _procesar_mensaje(self, mensaje: Dict[str, Any]) -> None:
        """Procesa un mensaje recibido"""
        mensaje_id = mensaje.get("mensaje_id", "unknown")
        tipo_evento = mensaje.get("tipo_evento", "unknown")
        
        try:
            # Buscar manejador
            manejador = self._manejadores.get(tipo_evento)
            if not manejador:
                self._logger.advertencia(
                    f"No hay manejador para evento: {tipo_evento}",
                    contexto={"mensaje_id": mensaje_id}
                )
                return
            
            # Procesar mensaje
            await manejador(mensaje)
            
            # Registrar éxito
            self._metricas.incrementar_contador(
                "afiliados_eventos_procesados_total",
                {"tipo_evento": tipo_evento, "estado": "exitoso"}
            )
            
            self._logger.info(
                f"Evento procesado exitosamente: {tipo_evento}",
                contexto={"mensaje_id": mensaje_id}
            )
            
        except Exception as e:
            self._logger.error(
                f"Error procesando evento: {tipo_evento}",
                excepcion=e,
                contexto={"mensaje_id": mensaje_id}
            )
            
            self._metricas.incrementar_contador(
                "afiliados_eventos_procesados_total",
                {"tipo_evento": tipo_evento, "estado": "error"}
            )
    
    async def detener_consumo(self) -> None:
        """Detiene el consumo de eventos"""
        self._activo = False
        await self._adaptador.cerrar_conexion()
        self._logger.info("Consumidor de eventos detenido")