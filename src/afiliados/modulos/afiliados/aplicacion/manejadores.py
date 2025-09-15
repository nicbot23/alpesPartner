"""
Manejadores de comandos del módulo de afiliados
"""
import logging
from seedwork.aplicacion.comandos import ManejadorComando
from .comandos import RegistrarAfiliado, AprobarAfiliado, RechazarAfiliado, ActualizarAfiliado, DesactivarAfiliado
from ..dominio.entidades import Afiliado
from ..infraestructura.despachadores import DespachadorEventosPulsar
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DespachadorEventos:
    """Interface para despachador de eventos"""
    async def publicar_evento(self, evento):
        pass

class ManejadorRegistrarAfiliado(ManejadorComando):
    """Manejador para el comando de registrar afiliado"""
    
    def __init__(self, despachador_eventos: DespachadorEventos = None):
        self.despachador_eventos = despachador_eventos or DespachadorEventosPulsar()
    
    def manejar(self, comando: RegistrarAfiliado) -> Dict[str, Any]:
        """Maneja el registro de un nuevo afiliado"""
        logger.info(f"Registrando afiliado: {comando.nombre}")
        
        # Crear agregado de afiliado
        afiliado = Afiliado.registrar(
            nombre=comando.nombre,
            tipo_afiliacion=comando.tipo_afiliacion,
            email=comando.email,
            telefono=comando.telefono,
            direccion=comando.direccion
        )
        
        # Publicar eventos de dominio
        for evento in afiliado.eventos:
            # Aquí se publicaría el evento a través del despachador
            logger.info(f"Evento generado: {evento.nombre}")
        
        afiliado.limpiar_eventos()
        
        return {
            "afiliado_id": str(afiliado.id),
            "estado": afiliado.estado,
            "message": f"Afiliado {comando.nombre} registrado exitosamente"
        }

class ManejadorAprobarAfiliado(ManejadorComando):
    """Manejador para el comando de aprobar afiliado"""
    
    def __init__(self, despachador_eventos: DespachadorEventos = None):
        self.despachador_eventos = despachador_eventos or DespachadorEventosPulsar()
    
    def manejar(self, comando: AprobarAfiliado) -> Dict[str, Any]:
        """Maneja la aprobación de un afiliado"""
        logger.info(f"Aprobando afiliado: {comando.afiliado_id}")
        
        # Aquí se buscaría el afiliado en el repositorio
        # Por ahora simulamos que existe
        afiliado = Afiliado(
            id=comando.afiliado_id,
            estado="pendiente"
        )
        
        afiliado.aprobar(
            aprobado_por=comando.aprobado_por,
            observaciones=comando.observaciones
        )
        
        # Publicar eventos de dominio
        for evento in afiliado.eventos:
            logger.info(f"Evento generado: {evento.nombre}")
        
        afiliado.limpiar_eventos()
        
        return {
            "afiliado_id": comando.afiliado_id,
            "estado": afiliado.estado,
            "message": "Afiliado aprobado exitosamente"
        }

class ManejadorRechazarAfiliado(ManejadorComando):
    """Manejador para el comando de rechazar afiliado"""
    
    def __init__(self, despachador_eventos: DespachadorEventos = None):
        self.despachador_eventos = despachador_eventos or DespachadorEventosPulsar()
    
    def manejar(self, comando: RechazarAfiliado) -> Dict[str, Any]:
        """Maneja el rechazo de un afiliado"""
        logger.info(f"Rechazando afiliado: {comando.afiliado_id}")
        
        # Aquí se buscaría el afiliado en el repositorio
        afiliado = Afiliado(
            id=comando.afiliado_id,
            estado="pendiente"
        )
        
        afiliado.rechazar(
            rechazado_por=comando.rechazado_por,
            razon_rechazo=comando.razon_rechazo
        )
        
        # Publicar eventos de dominio
        for evento in afiliado.eventos:
            logger.info(f"Evento generado: {evento.nombre}")
        
        afiliado.limpiar_eventos()
        
        return {
            "afiliado_id": comando.afiliado_id,
            "estado": afiliado.estado,
            "message": "Afiliado rechazado"
        }

class ManejadorActualizarAfiliado(ManejadorComando):
    """Manejador para el comando de actualizar afiliado"""
    
    def __init__(self, despachador_eventos: DespachadorEventos = None):
        self.despachador_eventos = despachador_eventos or DespachadorEventosPulsar()
    
    def manejar(self, comando: ActualizarAfiliado) -> Dict[str, Any]:
        """Maneja la actualización de un afiliado"""
        logger.info(f"Actualizando afiliado: {comando.afiliado_id}")
        
        # Aquí se buscaría el afiliado en el repositorio
        afiliado = Afiliado(id=comando.afiliado_id)
        
        # Preparar datos para actualizar
        datos_actualizacion = {}
        if comando.nombre is not None:
            datos_actualizacion['nombre'] = comando.nombre
        if comando.telefono is not None:
            datos_actualizacion['telefono'] = comando.telefono
        if comando.direccion is not None:
            datos_actualizacion['direccion'] = comando.direccion
        if comando.observaciones is not None:
            datos_actualizacion['observaciones'] = comando.observaciones
        
        afiliado.actualizar_datos(
            actualizado_por=comando.actualizado_por,
            **datos_actualizacion
        )
        
        # Publicar eventos de dominio
        for evento in afiliado.eventos:
            logger.info(f"Evento generado: {evento.nombre}")
        
        afiliado.limpiar_eventos()
        
        return {
            "afiliado_id": comando.afiliado_id,
            "message": "Afiliado actualizado exitosamente"
        }

class ManejadorDesactivarAfiliado(ManejadorComando):
    """Manejador para el comando de desactivar afiliado"""
    
    def __init__(self, despachador_eventos: DespachadorEventos = None):
        self.despachador_eventos = despachador_eventos or DespachadorEventosPulsar()
    
    def manejar(self, comando: DesactivarAfiliado) -> Dict[str, Any]:
        """Maneja la desactivación de un afiliado"""
        logger.info(f"Desactivando afiliado: {comando.afiliado_id}")
        
        # Aquí se buscaría el afiliado en el repositorio
        afiliado = Afiliado(id=comando.afiliado_id)
        
        afiliado.desactivar(
            desactivado_por=comando.desactivado_por,
            razon_desactivacion=comando.razon_desactivacion
        )
        
        # Publicar eventos de dominio
        for evento in afiliado.eventos:
            logger.info(f"Evento generado: {evento.nombre}")
        
        afiliado.limpiar_eventos()
        
        return {
            "afiliado_id": comando.afiliado_id,
            "estado": afiliado.estado,
            "message": "Afiliado desactivado"
        }