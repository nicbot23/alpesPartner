"""
Manejadores de eventos de integración para comunicación entre bounded contexts
Arquitectura: Event Handlers + Domain Events + Apache Pulsar + Async Processing
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import asyncio
import logging
import uuid

from ...seedwork.dominio.eventos import EventoDominio
from ..infraestructura.despachadores import DespachadorEventosComisiones
from .eventos import (
    EventoIntegracionComision, ComisionCreada, ComisionCalculada, 
    ComisionAprobada, ComisionRechazada, ComisionPagada, ComisionAnulada,
    SolicitudValidacionAfiliado, SolicitudVerificacionConversion,
    NotificacionEstadoComision, RegistroEventosIntegracion
)

# =============================================================================
# INTERFACES - CONTRATOS
# =============================================================================

class ManejadorEventoIntegracion(ABC):
    """Interfaz base para manejadores de eventos de integración"""
    
    @abstractmethod
    async def manejar(self, evento: EventoDominio) -> Dict[str, Any]:
        """Manejar evento de integración"""
        pass
    
    @abstractmethod
    def puede_manejar(self, evento: EventoDominio) -> bool:
        """Verificar si puede manejar el evento"""
        pass
    
    @abstractmethod
    def obtener_eventos_soportados(self) -> List[str]:
        """Obtener lista de eventos que puede manejar"""
        pass

class RepositorioEventosIntegracion(ABC):
    """Interfaz para persistir eventos de integración"""
    
    @abstractmethod
    async def guardar_evento(self, evento: EventoDominio, metadata: Dict[str, Any]) -> str:
        """Guardar evento con metadatos"""
        pass
    
    @abstractmethod
    async def obtener_historial_eventos(self, comision_id: str) -> List[Dict[str, Any]]:
        """Obtener historial de eventos de una comisión"""
        pass
    
    @abstractmethod
    async def marcar_evento_procesado(self, evento_id: str, resultado: Dict[str, Any]) -> None:
        """Marcar evento como procesado"""
        pass

# =============================================================================
# MANEJADORES ESPECÍFICOS DE EVENTOS
# =============================================================================

class ManejadorComisionCreada(ManejadorEventoIntegracion):
    """Manejador para eventos de comisión creada"""
    
    def __init__(self, despachador: DespachadorEventosComisiones):
        self.despachador = despachador
        self.logger = logging.getLogger(__name__)
    
    async def manejar(self, evento: ComisionCreada) -> Dict[str, Any]:
        """Procesar evento de comisión creada"""
        try:
            # 1. Validar datos del evento
            self._validar_evento(evento)
            
            # 2. Solicitar validación del afiliado
            await self._solicitar_validacion_afiliado(evento)
            
            # 3. Solicitar verificación de conversión
            await self._solicitar_verificacion_conversion(evento)
            
            # 4. Publicar notificación
            await self._publicar_notificacion_creacion(evento)
            
            # 5. Programar cálculo automático si aplica
            await self._programar_calculo_automatico(evento)
            
            self.logger.info(f"Evento ComisionCreada procesado: {evento.comision_id}")
            
            return {
                "estado": "procesado_exitosamente",
                "comision_id": evento.comision_id,
                "acciones_ejecutadas": [
                    "validacion_afiliado_solicitada",
                    "verificacion_conversion_solicitada", 
                    "notificacion_publicada",
                    "calculo_programado"
                ]
            }
            
        except Exception as ex:
            self.logger.error(f"Error procesando ComisionCreada: {ex}")
            return {
                "estado": "error",
                "mensaje": str(ex),
                "comision_id": evento.comision_id
            }
    
    def puede_manejar(self, evento: EventoDominio) -> bool:
        """Verificar si puede manejar el evento"""
        return isinstance(evento, ComisionCreada)
    
    def obtener_eventos_soportados(self) -> List[str]:
        """Eventos soportados"""
        return ["ComisionCreada"]
    
    def _validar_evento(self, evento: ComisionCreada) -> None:
        """Validar datos del evento"""
        if not evento.comision_id or not evento.afiliado_id or not evento.campana_id:
            raise ValueError("Datos requeridos faltantes en evento ComisionCreada")
    
    async def _solicitar_validacion_afiliado(self, evento: ComisionCreada) -> None:
        """Solicitar validación del afiliado"""
        solicitud = SolicitudValidacionAfiliado(
            afiliado_id=evento.afiliado_id,
            comision_id=evento.comision_id,
            criterios_validacion=["estado_activo", "documentos_validos", "sin_restricciones"]
        )
        await self.despachador.publicar_evento(solicitud)
    
    async def _solicitar_verificacion_conversion(self, evento: ComisionCreada) -> None:
        """Solicitar verificación de conversión"""
        solicitud = SolicitudVerificacionConversion(
            conversion_id=evento.conversion_id,
            comision_id=evento.comision_id,
            campana_id=evento.campana_id,
            datos_requeridos=["monto_verificado", "fecha_valida", "campana_activa"]
        )
        await self.despachador.publicar_evento(solicitud)
    
    async def _publicar_notificacion_creacion(self, evento: ComisionCreada) -> None:
        """Publicar notificación de creación"""
        notificacion = NotificacionEstadoComision(
            comision_id=evento.comision_id,
            afiliado_id=evento.afiliado_id,
            estado_anterior="inexistente",
            estado_nuevo="pendiente",
            usuario_responsable=evento.usuario_creador,
            detalles_cambio={
                "tipo_comision": evento.tipo_comision,
                "monto_base": float(evento.monto_base),
                "fecha_creacion": evento.fecha_evento.isoformat()
            }
        )
        await self.despachador.publicar_evento(notificacion)
    
    async def _programar_calculo_automatico(self, evento: ComisionCreada) -> None:
        """Programar cálculo automático si aplica"""
        # En implementación real, esto programaría una tarea para cálculo automático
        self.logger.info(f"Cálculo automático programado para comisión: {evento.comision_id}")

class ManejadorComisionCalculada(ManejadorEventoIntegracion):
    """Manejador para eventos de comisión calculada"""
    
    def __init__(self, despachador: DespachadorEventosComisiones):
        self.despachador = despachador
        self.logger = logging.getLogger(__name__)
    
    async def manejar(self, evento: ComisionCalculada) -> Dict[str, Any]:
        """Procesar evento de comisión calculada"""
        try:
            # 1. Validar cálculo
            self._validar_calculo(evento)
            
            # 2. Verificar límites y políticas
            await self._verificar_politicas_aprobacion(evento)
            
            # 3. Notificar al afiliado
            await self._notificar_calculo_completado(evento)
            
            # 4. Programar aprobación automática si aplica
            await self._evaluar_aprobacion_automatica(evento)
            
            self.logger.info(f"Evento ComisionCalculada procesado: {evento.comision_id}")
            
            return {
                "estado": "procesado_exitosamente",
                "comision_id": evento.comision_id,
                "monto_calculado": float(evento.monto_calculado),
                "requiere_aprobacion_manual": await self._requiere_aprobacion_manual(evento)
            }
            
        except Exception as ex:
            self.logger.error(f"Error procesando ComisionCalculada: {ex}")
            return {
                "estado": "error",
                "mensaje": str(ex),
                "comision_id": evento.comision_id
            }
    
    def puede_manejar(self, evento: EventoDominio) -> bool:
        return isinstance(evento, ComisionCalculada)
    
    def obtener_eventos_soportados(self) -> List[str]:
        return ["ComisionCalculada"]
    
    def _validar_calculo(self, evento: ComisionCalculada) -> None:
        """Validar que el cálculo sea correcto"""
        if evento.monto_calculado <= 0:
            raise ValueError("Monto calculado debe ser mayor a cero")
        
        if evento.monto_calculado > evento.monto_base:
            raise ValueError("Monto calculado no puede ser mayor al monto base")
    
    async def _verificar_politicas_aprobacion(self, evento: ComisionCalculada) -> None:
        """Verificar políticas de aprobación"""
        # En implementación real, verificaría políticas específicas
        pass
    
    async def _notificar_calculo_completado(self, evento: ComisionCalculada) -> None:
        """Notificar cálculo completado"""
        notificacion = NotificacionEstadoComision(
            comision_id=evento.comision_id,
            afiliado_id=evento.afiliado_id,
            estado_anterior="pendiente",
            estado_nuevo="calculada",
            usuario_responsable="sistema",
            detalles_cambio={
                "monto_calculado": float(evento.monto_calculado),
                "metodo_calculo": evento.metodo_calculo,
                "fecha_calculo": evento.fecha_calculo.isoformat()
            }
        )
        await self.despachador.publicar_evento(notificacion)
    
    async def _evaluar_aprobacion_automatica(self, evento: ComisionCalculada) -> None:
        """Evaluar si se puede aprobar automáticamente"""
        # Lógica de aprobación automática basada en reglas de negocio
        if await self._cumple_criterios_auto_aprobacion(evento):
            self.logger.info(f"Comisión elegible para aprobación automática: {evento.comision_id}")
    
    async def _requiere_aprobacion_manual(self, evento: ComisionCalculada) -> bool:
        """Verificar si requiere aprobación manual"""
        # En implementación real, verificaría reglas específicas
        return evento.monto_calculado > 100000  # Umbral ejemplo
    
    async def _cumple_criterios_auto_aprobacion(self, evento: ComisionCalculada) -> bool:
        """Verificar criterios para aprobación automática"""
        # Criterios ejemplo
        return (evento.monto_calculado <= 50000 and 
                evento.metodo_calculo == "automatico" and
                not evento.descuentos_aplicados)

class ManejadorComisionAprobada(ManejadorEventoIntegracion):
    """Manejador para eventos de comisión aprobada"""
    
    def __init__(self, despachador: DespachadorEventosComisiones):
        self.despachador = despachador
        self.logger = logging.getLogger(__name__)
    
    async def manejar(self, evento: ComisionAprobada) -> Dict[str, Any]:
        """Procesar evento de comisión aprobada"""
        try:
            # 1. Registrar aprobación
            await self._registrar_aprobacion(evento)
            
            # 2. Programar pago
            await self._programar_procesamiento_pago(evento)
            
            # 3. Notificar al afiliado
            await self._notificar_aprobacion(evento)
            
            # 4. Actualizar métricas
            await self._actualizar_metricas_aprobacion(evento)
            
            self.logger.info(f"Evento ComisionAprobada procesado: {evento.comision_id}")
            
            return {
                "estado": "procesado_exitosamente",
                "comision_id": evento.comision_id,
                "monto_aprobado": float(evento.monto_aprobado),
                "programado_para_pago": True
            }
            
        except Exception as ex:
            self.logger.error(f"Error procesando ComisionAprobada: {ex}")
            return {
                "estado": "error",
                "mensaje": str(ex),
                "comision_id": evento.comision_id
            }
    
    def puede_manejar(self, evento: EventoDominio) -> bool:
        return isinstance(evento, ComisionAprobada)
    
    def obtener_eventos_soportados(self) -> List[str]:
        return ["ComisionAprobada"]
    
    async def _registrar_aprobacion(self, evento: ComisionAprobada) -> None:
        """Registrar la aprobación en auditoría"""
        # En implementación real, registraría en sistema de auditoría
        pass
    
    async def _programar_procesamiento_pago(self, evento: ComisionAprobada) -> None:
        """Programar el procesamiento del pago"""
        # En implementación real, programaría en cola de pagos
        self.logger.info(f"Pago programado para comisión: {evento.comision_id}")
    
    async def _notificar_aprobacion(self, evento: ComisionAprobada) -> None:
        """Notificar aprobación al afiliado"""
        notificacion = NotificacionEstadoComision(
            comision_id=evento.comision_id,
            afiliado_id=evento.afiliado_id,
            estado_anterior="calculada",
            estado_nuevo="aprobada",
            usuario_responsable=evento.aprobador_id,
            detalles_cambio={
                "monto_aprobado": float(evento.monto_aprobado),
                "nivel_aprobacion": evento.nivel_aprobacion,
                "comentarios": evento.comentarios,
                "fecha_aprobacion": evento.fecha_aprobacion.isoformat()
            }
        )
        await self.despachador.publicar_evento(notificacion)
    
    async def _actualizar_metricas_aprobacion(self, evento: ComisionAprobada) -> None:
        """Actualizar métricas de aprobación"""
        # En implementación real, actualizaría métricas en tiempo real
        pass

# =============================================================================
# COORDINADOR DE EVENTOS - EVENT COORDINATOR
# =============================================================================

class CoordinadorEventosIntegracion:
    """Coordinador central para eventos de integración"""
    
    def __init__(self, despachador: DespachadorEventosComisiones):
        self.despachador = despachador
        self.manejadores: Dict[str, ManejadorEventoIntegracion] = {}
        self.logger = logging.getLogger(__name__)
        self._configurar_manejadores()
    
    def _configurar_manejadores(self) -> None:
        """Configurar manejadores de eventos"""
        self.manejadores.update({
            "ComisionCreada": ManejadorComisionCreada(self.despachador),
            "ComisionCalculada": ManejadorComisionCalculada(self.despachador),
            "ComisionAprobada": ManejadorComisionAprobada(self.despachador),
            # Otros manejadores...
        })
    
    async def procesar_evento(self, evento: EventoDominio) -> Dict[str, Any]:
        """Procesar evento de integración"""
        try:
            nombre_evento = self._obtener_nombre_evento(evento)
            
            if nombre_evento not in self.manejadores:
                self.logger.warning(f"No hay manejador para evento: {nombre_evento}")
                return {
                    "estado": "no_procesado",
                    "motivo": "manejador_no_encontrado",
                    "evento": nombre_evento
                }
            
            manejador = self.manejadores[nombre_evento]
            resultado = await manejador.manejar(evento)
            
            self.logger.info(f"Evento procesado exitosamente: {nombre_evento}")
            return resultado
            
        except Exception as ex:
            self.logger.error(f"Error procesando evento: {ex}")
            return {
                "estado": "error",
                "mensaje": str(ex),
                "evento": self._obtener_nombre_evento(evento)
            }
    
    async def procesar_eventos_lote(self, eventos: List[EventoDominio]) -> List[Dict[str, Any]]:
        """Procesar múltiples eventos en lote"""
        resultados = []
        
        for evento in eventos:
            resultado = await self.procesar_evento(evento)
            resultados.append(resultado)
        
        return resultados
    
    def registrar_manejador(self, nombre_evento: str, manejador: ManejadorEventoIntegracion) -> None:
        """Registrar nuevo manejador de evento"""
        self.manejadores[nombre_evento] = manejador
        self.logger.info(f"Manejador registrado para evento: {nombre_evento}")
    
    def obtener_manejadores_disponibles(self) -> Dict[str, List[str]]:
        """Obtener manejadores disponibles"""
        return {
            nombre: manejador.obtener_eventos_soportados()
            for nombre, manejador in self.manejadores.items()
        }
    
    def _obtener_nombre_evento(self, evento: EventoDominio) -> str:
        """Obtener nombre del evento"""
        return evento.__class__.__name__

# =============================================================================
# SERVICIO DE INTEGRACIÓN - INTEGRATION SERVICE
# =============================================================================

class ServicioIntegracionComisiones:
    """Servicio principal para integración con otros bounded contexts"""
    
    def __init__(
        self, 
        coordinador: CoordinadorEventosIntegracion,
        repositorio_eventos: RepositorioEventosIntegracion
    ):
        self.coordinador = coordinador
        self.repositorio_eventos = repositorio_eventos
        self.logger = logging.getLogger(__name__)
    
    async def publicar_evento_integracion(
        self, 
        evento: EventoDominio,
        metadatos_adicionales: Dict[str, Any] = None
    ) -> str:
        """Publicar evento de integración"""
        try:
            # 1. Generar metadatos del evento
            metadatos = self._generar_metadatos_evento(evento, metadatos_adicionales)
            
            # 2. Guardar evento en repositorio
            evento_id = await self.repositorio_eventos.guardar_evento(evento, metadatos)
            
            # 3. Procesar evento
            resultado = await self.coordinador.procesar_evento(evento)
            
            # 4. Marcar como procesado
            await self.repositorio_eventos.marcar_evento_procesado(evento_id, resultado)
            
            self.logger.info(f"Evento de integración publicado: {evento_id}")
            return evento_id
            
        except Exception as ex:
            self.logger.error(f"Error publicando evento de integración: {ex}")
            raise
    
    async def obtener_historial_integracion(self, comision_id: str) -> List[Dict[str, Any]]:
        """Obtener historial de eventos de integración de una comisión"""
        return await self.repositorio_eventos.obtener_historial_eventos(comision_id)
    
    async def reenviar_evento(self, evento_id: str) -> Dict[str, Any]:
        """Reenviar evento de integración"""
        # En implementación real, recuperaría el evento y lo reenviaría
        self.logger.info(f"Reenviando evento: {evento_id}")
        return {"estado": "reenviado", "evento_id": evento_id}
    
    def _generar_metadatos_evento(
        self, 
        evento: EventoDominio, 
        metadatos_adicionales: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generar metadatos del evento"""
        metadatos = {
            "evento_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "contexto_origen": "marketing.comisiones",
            "tipo_evento": evento.__class__.__name__
        }
        
        if metadatos_adicionales:
            metadatos.update(metadatos_adicionales)
        
        return metadatos