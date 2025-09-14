"""
Manejadores de comandos para el microservicio Conversiones
"""
from ....seedwork.aplicacion.comandos import ManejadorComando
from ....seedwork.dominio.eventos import EventoDominio
from ..dominio.eventos import ConversionDetectada, ConversionValidada, ConversionRechazada, ConversionActualizada
from .comandos import DetectarConversion, ValidarConversion, RechazarConversion, ActualizarConversion
from ..infraestructura.despachadores import DespachadorEventos
import uuid
from datetime import datetime


class ManejadorDetectarConversion(ManejadorComando):
    
    def __init__(self, despachador: DespachadorEventos):
        self._despachador = despachador
    
    def manejar(self, comando: DetectarConversion):
        # Generar ID único para la conversión
        conversion_id = str(uuid.uuid4())
        
        # Crear evento de conversión detectada
        evento = ConversionDetectada(
            conversion_id=conversion_id,
            user_id=comando.user_id,
            tipo_conversion=comando.tipo_conversion,
            valor=comando.valor,
            moneda=comando.moneda,
            metadata=comando.metadata,
            fecha_conversion=datetime.utcnow()
        )
        
        # Publicar evento
        self._despachador.publicar_evento(evento)


class ManejadorValidarConversion(ManejadorComando):
    
    def __init__(self, despachador: DespachadorEventos):
        self._despachador = despachador
    
    def manejar(self, comando: ValidarConversion):
        # Crear evento de conversión validada
        evento = ConversionValidada(
            conversion_id=comando.conversion_id,
            user_id=comando.user_id,
            estado_validacion="validada",
            valor_validado="",  # Se podría obtener de la BD
            observaciones=comando.observaciones,
            fecha_validacion=datetime.utcnow()
        )
        
        # Publicar evento
        self._despachador.publicar_evento(evento)


class ManejadorRechazarConversion(ManejadorComando):
    
    def __init__(self, despachador: DespachadorEventos):
        self._despachador = despachador
    
    def manejar(self, comando: RechazarConversion):
        # Crear evento de conversión rechazada
        evento = ConversionRechazada(
            conversion_id=comando.conversion_id,
            user_id=comando.user_id,
            razon_rechazo=comando.razon_rechazo,
            observaciones=comando.observaciones,
            fecha_rechazo=datetime.utcnow()
        )
        
        # Publicar evento
        self._despachador.publicar_evento(evento)


class ManejadorActualizarConversion(ManejadorComando):
    
    def __init__(self, despachador: DespachadorEventos):
        self._despachador = despachador
    
    def manejar(self, comando: ActualizarConversion):
        # Crear evento de conversión actualizada
        evento = ConversionActualizada(
            conversion_id=comando.conversion_id,
            user_id=comando.user_id,
            valor_anterior="",  # Se podría obtener de la BD
            valor_nuevo=comando.nuevo_valor,
            tipo_actualizacion=comando.tipo_actualizacion,
            fecha_actualizacion=datetime.utcnow()
        )
        
        # Publicar evento
        self._despachador.publicar_evento(evento)