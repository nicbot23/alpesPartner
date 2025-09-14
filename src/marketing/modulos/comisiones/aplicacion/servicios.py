"""
Servicios de Aplicación del módulo de comisiones - Marketing Microservice
Coordinación de casos de uso, orchestración de dominio e infraestructura
Arquitectura: Application Services + Use Cases + Enterprise Patterns
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any, Protocol, Union
from abc import ABC, abstractmethod
import uuid
import logging

from ..dominio.entidades import (
    Comision, EstadoComision, TipoComision, MontoMonetario,
    PorcentajeComision, ConfiguracionComision, CalculadorComision,
    ValidadorComision, RepositorioComisiones, ExcepcionDominio
)
from .comandos import *
from .consultas import *

# =============================================================================
# INTERFACES DE SERVICIOS - PRINCIPIO DE INVERSIÓN DE DEPENDENCIAS  
# =============================================================================

class RepositorioComisiones(Protocol):
    """Interfaz del repositorio de comisiones para la capa de aplicación"""
    
    def obtener_por_id(self, comision_id: str) -> Optional[Comision]:
        """Obtener comisión por ID"""
        ...
    
    def guardar(self, comision: Comision) -> None:
        """Guardar comisión"""
        ...
    
    def listar_por_afiliado(self, afiliado_id: str, estados: Optional[List[EstadoComision]] = None) -> List[Comision]:
        """Listar comisiones por afiliado"""
        ...
    
    def listar_por_campana(self, campana_id: str, estados: Optional[List[EstadoComision]] = None) -> List[Comision]:
        """Listar comisiones por campaña"""
        ...
    
    def existe_por_conversion(self, conversion_id: str) -> bool:
        """Verificar si existe comisión para conversión"""
        ...

class RepositorioEventos(Protocol):
    """Interfaz del repositorio de eventos"""
    
    def guardar_evento(self, evento: EventoDominio) -> None:
        """Guardar evento de dominio"""
        ...
    
    def obtener_eventos_por_agregado(self, agregado_id: str) -> List[EventoDominio]:
        """Obtener eventos por agregado"""
        ...

class ServicioNotificaciones(Protocol):
    """Interfaz del servicio de notificaciones"""
    
    def notificar_comision_calculada(self, comision: Comision) -> None:
        """Notificar comisión calculada"""
        ...
    
    def notificar_comision_aprobada(self, comision: Comision) -> None:
        """Notificar comisión aprobada"""
        ...
    
    def notificar_comision_rechazada(self, comision: Comision, motivo: str) -> None:
        """Notificar comisión rechazada"""
        ...

class ServicioAuditoria(Protocol):
    """Interfaz del servicio de auditoría"""
    
    def registrar_accion(self, usuario_id: str, accion: str, detalles: Dict[str, Any]) -> None:
        """Registrar acción de usuario"""
        ...

# =============================================================================
# EXCEPCIONES DE APLICACIÓN
# =============================================================================

class ExcepcionAplicacion(Exception):
    """Excepción base de la capa de aplicación"""
    pass

class ComisionNoEncontradaError(ExcepcionAplicacion):
    """Error cuando no se encuentra la comisión"""
    pass

class ComisionYaExisteError(ExcepcionAplicacion):
    """Error cuando la comisión ya existe para la conversión"""
    pass

class OperacionNoPermitidaError(ExcepcionAplicacion):
    """Error cuando la operación no está permitida"""
    pass

class ValidacionFallidaError(ExcepcionAplicacion):
    """Error de validación en la aplicación"""
    pass

# =============================================================================
# RESULTADOS DE CASOS DE USO
# =============================================================================

@dataclass
class ResultadoCreacionComision:
    """Resultado del caso de uso de creación de comisión"""
    comision_id: str
    estado: EstadoComision
    monto_calculado: Optional[MontoMonetario]
    eventos_generados: List[str]
    exitoso: bool
    mensaje: str

@dataclass
class ResultadoCalculoComision:
    """Resultado del caso de uso de cálculo de comisión"""
    comision_id: str
    monto_calculado: MontoMonetario
    metodo_calculo: str
    fecha_calculo: datetime
    detalles_calculo: Dict[str, Any]
    exitoso: bool

@dataclass
class ResultadoAprobacionComision:
    """Resultado del caso de uso de aprobación"""
    comision_id: str
    estado_anterior: EstadoComision
    estado_nuevo: EstadoComision
    aprobador_id: str
    fecha_aprobacion: datetime
    exitoso: bool
    mensaje: str

# =============================================================================
# SERVICIOS DE APLICACIÓN - CASOS DE USO
# =============================================================================

class ServicioComisiones:
    """
    Servicio principal de comisiones - Coordinador de casos de uso
    Principio de Responsabilidad Única - orchestración de casos de uso
    """
    
    def __init__(
        self,
        repositorio_comisiones: RepositorioComisiones,
        repositorio_eventos: RepositorioEventos,
        calculador_comision: CalculadorComision,
        validador_comision: ValidadorComision,
        servicio_notificaciones: Optional[ServicioNotificaciones] = None,
        servicio_auditoria: Optional[ServicioAuditoria] = None,
        logger: Optional[logging.Logger] = None
    ):
        self._repositorio_comisiones = repositorio_comisiones
        self._repositorio_eventos = repositorio_eventos
        self._calculador_comision = calculador_comision
        self._validador_comision = validador_comision
        self._servicio_notificaciones = servicio_notificaciones
        self._servicio_auditoria = servicio_auditoria
        self._logger = logger or logging.getLogger(__name__)
    
    def crear_comision(self, comando: CrearComision) -> ResultadoCreacionComision:
        """
        Caso de uso: Crear nueva comisión
        Principio de Responsabilidad Única - solo creación
        """
        try:
            self._logger.info(f"Iniciando creación de comisión para conversión {comando.conversion_id}")
            
            # 1. Validar que no exista comisión para la conversión
            if self._repositorio_comisiones.existe_por_conversion(comando.conversion_id):
                raise ComisionYaExisteError(f"Ya existe comisión para conversión {comando.conversion_id}")
            
            # 2. Crear objetos de valor
            monto_base = MontoMonetario(valor=comando.monto_base, moneda=comando.moneda)
            porcentaje = PorcentajeComision(valor=comando.porcentaje) if comando.porcentaje else None
            
            # 3. Crear entidad de comisión
            comision = Comision.crear(
                afiliado_id=comando.afiliado_id,
                campana_id=comando.campana_id,
                conversion_id=comando.conversion_id,
                monto_base=monto_base,
                tipo_comision=comando.tipo_comision,
                porcentaje=porcentaje,
                metadatos=comando.metadatos or {}
            )
            
            # 4. Validar reglas de negocio
            self._validador_comision.validar_creacion(comision)
            
            # 5. Calcular comisión automáticamente si es posible
            monto_calculado = None
            if comando.tipo_comision in [TipoComision.FIJA, TipoComision.PORCENTUAL]:
                try:
                    configuracion = ConfiguracionComision.desde_dict(comando.configuracion or {})
                    monto_calculado = self._calculador_comision.calcular(comision, configuracion)
                    comision.establecer_monto_calculado(monto_calculado)
                except Exception as ex:
                    self._logger.warning(f"No se pudo calcular comisión automáticamente: {ex}")
            
            # 6. Guardar comisión
            self._repositorio_comisiones.guardar(comision)
            
            # 7. Guardar eventos
            eventos_generados = []
            for evento in comision.obtener_eventos():
                self._repositorio_eventos.guardar_evento(evento)
                eventos_generados.append(type(evento).__name__)
            
            # 8. Notificar si hay servicio de notificaciones
            if self._servicio_notificaciones and monto_calculado:
                self._servicio_notificaciones.notificar_comision_calculada(comision)
            
            # 9. Auditar acción
            if self._servicio_auditoria:
                self._servicio_auditoria.registrar_accion(
                    usuario_id=comando.usuario_id,
                    accion="crear_comision",
                    detalles={
                        "comision_id": comision.id,
                        "conversion_id": comando.conversion_id,
                        "monto_base": str(comando.monto_base)
                    }
                )
            
            self._logger.info(f"Comisión creada exitosamente: {comision.id}")
            
            return ResultadoCreacionComision(
                comision_id=comision.id,
                estado=comision.estado,
                monto_calculado=monto_calculado,
                eventos_generados=eventos_generados,
                exitoso=True,
                mensaje="Comisión creada exitosamente"
            )
            
        except ExcepcionDominio as ex:
            self._logger.error(f"Error de dominio al crear comisión: {ex}")
            raise ValidacionFallidaError(str(ex)) from ex
        except Exception as ex:
            self._logger.error(f"Error inesperado al crear comisión: {ex}")
            raise ExcepcionAplicacion(f"Error al crear comisión: {ex}") from ex
    
    def calcular_comision(self, comando: CalcularComision) -> ResultadoCalculoComision:
        """
        Caso de uso: Calcular monto de comisión
        Principio de Responsabilidad Única - solo cálculo
        """
        try:
            self._logger.info(f"Iniciando cálculo de comisión {comando.comision_id}")
            
            # 1. Obtener comisión
            comision = self._repositorio_comisiones.obtener_por_id(comando.comision_id)
            if not comision:
                raise ComisionNoEncontradaError(f"Comisión no encontrada: {comando.comision_id}")
            
            # 2. Validar que se pueda calcular
            if not comando.forzar_recalculo and comision.estado != EstadoComision.PENDIENTE:
                raise OperacionNoPermitidaError(f"No se puede calcular comisión en estado {comision.estado.value}")
            
            # 3. Preparar configuración de cálculo
            configuracion = comando.configuracion_personalizada or ConfiguracionComision.por_defecto()
            
            # 4. Calcular monto
            monto_calculado = self._calculador_comision.calcular(comision, configuracion)
            
            # 5. Actualizar comisión
            comision.establecer_monto_calculado(monto_calculado)
            comision.actualizar()
            
            # 6. Guardar cambios
            self._repositorio_comisiones.guardar(comision)
            
            # 7. Guardar eventos
            for evento in comision.obtener_eventos():
                self._repositorio_eventos.guardar_evento(evento)
            
            # 8. Notificar
            if self._servicio_notificaciones:
                self._servicio_notificaciones.notificar_comision_calculada(comision)
            
            # 9. Auditar
            if self._servicio_auditoria:
                self._servicio_auditoria.registrar_accion(
                    usuario_id=comando.usuario_id,
                    accion="calcular_comision",
                    detalles={
                        "comision_id": comision.id,
                        "monto_calculado": str(monto_calculado.valor),
                        "forzar_recalculo": comando.forzar_recalculo
                    }
                )
            
            self._logger.info(f"Comisión calculada exitosamente: {comision.id} = {monto_calculado.valor}")
            
            return ResultadoCalculoComision(
                comision_id=comision.id,
                monto_calculado=monto_calculado,
                metodo_calculo=configuracion.metodo_calculo.value if configuracion else "desconocido",
                fecha_calculo=datetime.now(),
                detalles_calculo=self._calculador_comision.obtener_detalles_ultimo_calculo(),
                exitoso=True
            )
            
        except ExcepcionDominio as ex:
            self._logger.error(f"Error de dominio al calcular comisión: {ex}")
            raise ValidacionFallidaError(str(ex)) from ex
        except Exception as ex:
            self._logger.error(f"Error inesperado al calcular comisión: {ex}")
            raise ExcepcionAplicacion(f"Error al calcular comisión: {ex}") from ex
    
    def aprobar_comision(self, comando: AprobarComision) -> ResultadoAprobacionComision:
        """
        Caso de uso: Aprobar comisión calculada
        Principio de Responsabilidad Única - solo aprobación
        """
        try:
            self._logger.info(f"Iniciando aprobación de comisión {comando.comision_id}")
            
            # 1. Obtener comisión
            comision = self._repositorio_comisiones.obtener_por_id(comando.comision_id)
            if not comision:
                raise ComisionNoEncontradaError(f"Comisión no encontrada: {comando.comision_id}")
            
            # 2. Validar estado
            estado_anterior = comision.estado
            if estado_anterior != EstadoComision.CALCULADA:
                raise OperacionNoPermitidaError(f"No se puede aprobar comisión en estado {estado_anterior.value}")
            
            # 3. Validar reglas de negocio
            self._validador_comision.validar_aprobacion(comision, comando.aprobador_id)
            
            # 4. Aprobar comisión
            comision.aprobar(
                aprobador_id=comando.aprobador_id,
                comentarios=comando.comentarios,
                metadatos_aprobacion=comando.metadatos_aprobacion
            )
            
            # 5. Guardar cambios
            self._repositorio_comisiones.guardar(comision)
            
            # 6. Guardar eventos
            for evento in comision.obtener_eventos():
                self._repositorio_eventos.guardar_evento(evento)
            
            # 7. Notificar
            if self._servicio_notificaciones:
                self._servicio_notificaciones.notificar_comision_aprobada(comision)
            
            # 8. Auditar
            if self._servicio_auditoria:
                self._servicio_auditoria.registrar_accion(
                    usuario_id=comando.usuario_id,
                    accion="aprobar_comision",
                    detalles={
                        "comision_id": comision.id,
                        "aprobador_id": comando.aprobador_id,
                        "comentarios": comando.comentarios
                    }
                )
            
            self._logger.info(f"Comisión aprobada exitosamente: {comision.id}")
            
            return ResultadoAprobacionComision(
                comision_id=comision.id,
                estado_anterior=estado_anterior,
                estado_nuevo=comision.estado,
                aprobador_id=comando.aprobador_id,
                fecha_aprobacion=comision.fecha_aprobacion or datetime.now(),
                exitoso=True,
                mensaje="Comisión aprobada exitosamente"
            )
            
        except ExcepcionDominio as ex:
            self._logger.error(f"Error de dominio al aprobar comisión: {ex}")
            raise ValidacionFallidaError(str(ex)) from ex
        except Exception as ex:
            self._logger.error(f"Error inesperado al aprobar comisión: {ex}")
            raise ExcepcionAplicacion(f"Error al aprobar comisión: {ex}") from ex
    
    def rechazar_comision(self, comando: RechazarComision) -> ResultadoAprobacionComision:
        """
        Caso de uso: Rechazar comisión
        Principio de Responsabilidad Única - solo rechazo
        """
        try:
            self._logger.info(f"Iniciando rechazo de comisión {comando.comision_id}")
            
            # 1. Obtener comisión
            comision = self._repositorio_comisiones.obtener_por_id(comando.comision_id)
            if not comision:
                raise ComisionNoEncontradaError(f"Comisión no encontrada: {comando.comision_id}")
            
            # 2. Validar estado
            estado_anterior = comision.estado
            if estado_anterior not in [EstadoComision.CALCULADA, EstadoComision.PENDIENTE]:
                raise OperacionNoPermitidaError(f"No se puede rechazar comisión en estado {estado_anterior.value}")
            
            # 3. Rechazar comisión
            comision.rechazar(
                rechazador_id=comando.rechazador_id,
                motivo=comando.motivo_rechazo,
                comentarios=comando.comentarios,
                metadatos_rechazo=comando.metadatos_rechazo
            )
            
            # 4. Guardar cambios
            self._repositorio_comisiones.guardar(comision)
            
            # 5. Guardar eventos
            for evento in comision.obtener_eventos():
                self._repositorio_eventos.guardar_evento(evento)
            
            # 6. Notificar
            if self._servicio_notificaciones:
                self._servicio_notificaciones.notificar_comision_rechazada(comision, comando.motivo_rechazo)
            
            # 7. Auditar
            if self._servicio_auditoria:
                self._servicio_auditoria.registrar_accion(
                    usuario_id=comando.usuario_id,
                    accion="rechazar_comision",
                    detalles={
                        "comision_id": comision.id,
                        "rechazador_id": comando.rechazador_id,
                        "motivo": comando.motivo_rechazo
                    }
                )
            
            self._logger.info(f"Comisión rechazada: {comision.id}")
            
            return ResultadoAprobacionComision(
                comision_id=comision.id,
                estado_anterior=estado_anterior,
                estado_nuevo=comision.estado,
                aprobador_id=comando.rechazador_id,
                fecha_aprobacion=datetime.now(),
                exitoso=True,
                mensaje=f"Comisión rechazada: {comando.motivo_rechazo}"
            )
            
        except ExcepcionDominio as ex:
            self._logger.error(f"Error de dominio al rechazar comisión: {ex}")
            raise ValidacionFallidaError(str(ex)) from ex
        except Exception as ex:
            self._logger.error(f"Error inesperado al rechazar comisión: {ex}")
            raise ExcepcionAplicacion(f"Error al rechazar comisión: {ex}") from ex

# =============================================================================
# SERVICIO DE CONSULTAS - COORDINADOR DE LECTURA
# =============================================================================

class ServicioConsultasComisiones:
    """
    Servicio de consultas de comisiones
    Principio de Responsabilidad Única - solo consultas
    """
    
    def __init__(
        self,
        repositorio_comisiones: RepositorioComisiones,
        cache_consultas: Optional[CacheConsultas] = None,
        logger: Optional[logging.Logger] = None
    ):
        self._repositorio_comisiones = repositorio_comisiones
        self._cache = cache_consultas
        self._logger = logger or logging.getLogger(__name__)
    
    def obtener_comision(self, consulta: ObtenerComision) -> Optional[ComisionDTO]:
        """Obtener comisión específica por ID"""
        try:
            # Verificar cache
            if self._cache and consulta.usar_cache:
                clave_cache = f"comision_{consulta.comision_id}"
                resultado_cache = self._cache.obtener(clave_cache)
                if resultado_cache:
                    return resultado_cache
            
            # Consultar repositorio
            comision = self._repositorio_comisiones.obtener_por_id(consulta.comision_id)
            if not comision:
                return None
            
            # Convertir a DTO
            dto = ComisionDTO.desde_entidad(comision)
            
            # Guardar en cache
            if self._cache and consulta.usar_cache:
                self._cache.guardar(clave_cache, dto, consulta.timeout_cache_segundos)
            
            return dto
            
        except Exception as ex:
            self._logger.error(f"Error al obtener comisión {consulta.comision_id}: {ex}")
            raise ExcepcionAplicacion(f"Error al obtener comisión: {ex}") from ex
    
    def listar_comisiones_por_afiliado(self, consulta: ObtenerComisionesPorAfiliado) -> ResultadoPaginado[ComisionDTO]:
        """Listar comisiones de un afiliado"""
        try:
            # Obtener comisiones del repositorio
            comisiones = self._repositorio_comisiones.listar_por_afiliado(
                afiliado_id=consulta.afiliado_id,
                estados=consulta.estados_filtro
            )
            
            # Aplicar filtros adicionales
            if consulta.fecha_desde or consulta.fecha_hasta:
                comisiones = self._filtrar_por_fechas(comisiones, consulta.fecha_desde, consulta.fecha_hasta)
            
            # Convertir a DTOs
            dtos = [ComisionDTO.desde_entidad(c) for c in comisiones]
            
            # Aplicar paginación
            total_elementos = len(dtos)
            inicio = consulta.paginacion.offset
            fin = inicio + consulta.paginacion.tamaño
            elementos_pagina = dtos[inicio:fin]
            
            return ResultadoPaginado.crear(
                elementos=elementos_pagina,
                total_elementos=total_elementos,
                criterio=consulta.paginacion
            )
            
        except Exception as ex:
            self._logger.error(f"Error al listar comisiones por afiliado {consulta.afiliado_id}: {ex}")
            raise ExcepcionAplicacion(f"Error al listar comisiones: {ex}") from ex
    
    def _filtrar_por_fechas(self, comisiones: List[Comision], fecha_desde: Optional[date], fecha_hasta: Optional[date]) -> List[Comision]:
        """Filtrar comisiones por rango de fechas"""
        if not fecha_desde and not fecha_hasta:
            return comisiones
        
        resultado = []
        for comision in comisiones:
            fecha_comision = comision.fecha_creacion.date()
            
            incluir = True
            if fecha_desde and fecha_comision < fecha_desde:
                incluir = False
            if fecha_hasta and fecha_comision > fecha_hasta:
                incluir = False
            
            if incluir:
                resultado.append(comision)
        
        return resultado

# =============================================================================
# COORDINADOR DE CASOS DE USO - FACADE PATTERN
# =============================================================================

class CoordinadorComisiones:
    """
    Coordinador principal de casos de uso de comisiones
    Facade Pattern - punto de entrada unificado
    """
    
    def __init__(
        self,
        servicio_comisiones: ServicioComisiones,
        servicio_consultas: ServicioConsultasComisiones,
        bus_comandos: BusComandos,
        bus_consultas: BusConsultas
    ):
        self._servicio_comisiones = servicio_comisiones
        self._servicio_consultas = servicio_consultas
        self._bus_comandos = bus_comandos
        self._bus_consultas = bus_consultas
    
    # Métodos de comandos
    def crear_comision(self, comando: CrearComision) -> ResultadoCreacionComision:
        """Crear nueva comisión"""
        return self._servicio_comisiones.crear_comision(comando)
    
    def calcular_comision(self, comando: CalcularComision) -> ResultadoCalculoComision:
        """Calcular monto de comisión"""
        return self._servicio_comisiones.calcular_comision(comando)
    
    def aprobar_comision(self, comando: AprobarComision) -> ResultadoAprobacionComision:
        """Aprobar comisión"""
        return self._servicio_comisiones.aprobar_comision(comando)
    
    def rechazar_comision(self, comando: RechazarComision) -> ResultadoAprobacionComision:
        """Rechazar comisión"""
        return self._servicio_comisiones.rechazar_comision(comando)
    
    # Métodos de consultas
    def obtener_comision(self, consulta: ObtenerComision) -> Optional[ComisionDTO]:
        """Obtener comisión por ID"""
        return self._servicio_consultas.obtener_comision(consulta)
    
    def listar_comisiones_afiliado(self, consulta: ObtenerComisionesPorAfiliado) -> ResultadoPaginado[ComisionDTO]:
        """Listar comisiones por afiliado"""
        return self._servicio_consultas.listar_comisiones_por_afiliado(consulta)
    
    # Métodos de bus
    def ejecutar_comando(self, comando: ComandoBase) -> Any:
        """Ejecutar comando a través del bus"""
        return self._bus_comandos.ejecutar(comando)
    
    def ejecutar_consulta(self, consulta: ConsultaBase) -> Any:
        """Ejecutar consulta a través del bus"""
        return self._bus_consultas.ejecutar(consulta)

# =============================================================================
# FACTORY PARA SERVICIOS - DEPENDENCY INJECTION
# =============================================================================

class FabricaServiciosComisiones:
    """
    Factory para servicios de comisiones
    Principio de Responsabilidad Única - solo creación de servicios
    """
    
    @staticmethod
    def crear_coordinador(
        repositorio_comisiones: RepositorioComisiones,
        repositorio_eventos: RepositorioEventos,
        calculador_comision: CalculadorComision,
        validador_comision: ValidadorComision,
        servicio_notificaciones: Optional[ServicioNotificaciones] = None,
        servicio_auditoria: Optional[ServicioAuditoria] = None,
        cache_consultas: Optional[CacheConsultas] = None
    ) -> CoordinadorComisiones:
        """Crear coordinador con todas las dependencias"""
        
        # Crear servicios
        servicio_comisiones = ServicioComisiones(
            repositorio_comisiones=repositorio_comisiones,
            repositorio_eventos=repositorio_eventos,
            calculador_comision=calculador_comision,
            validador_comision=validador_comision,
            servicio_notificaciones=servicio_notificaciones,
            servicio_auditoria=servicio_auditoria
        )
        
        servicio_consultas = ServicioConsultasComisiones(
            repositorio_comisiones=repositorio_comisiones,
            cache_consultas=cache_consultas
        )
        
        # Crear buses
        bus_comandos = BusComandosImplementacion()
        bus_consultas = BusConsultasImplementacion(cache_consultas)
        
        # Crear coordinador
        return CoordinadorComisiones(
            servicio_comisiones=servicio_comisiones,
            servicio_consultas=servicio_consultas,
            bus_comandos=bus_comandos,
            bus_consultas=bus_consultas
        )