"""
🎭 Comandos del BFF para comunicación con microservicios
Siguiendo el patrón de eventos de la arquitectura AlpesPartner
"""

from pulsar.schema import *
from typing import Dict, Any, Optional
import uuid
from datetime import datetime


# ==========================================
# COMANDOS HACIA campanias (CloudEvents)
# ==========================================

class LanzarCampaniaCompletaPayload(Record):
    """Payload del comando para lanzar campaña completa"""
    nombre = String()
    descripcion = String()
    tipo = String()
    canal_publicidad = String()
    objetivo = String()
    fecha_inicio = Long()  # timestamp en milisegundos
    fecha_fin = Long()     # timestamp en milisegundos  
    presupuesto = Double()
    moneda = String()
    segmento_audiencia = String()


class ComandoLanzarCampaniaCompleta(Record):
    """
    Comando CloudEvent para lanzar una campaña completa desde el BFF hacia campanias.
    Inicia la saga completa de creación y activación de campaña.
    """
    id = String()
    time = Long()
    ingestion = Long()
    specversion = String()
    type = String() 
    datacontenttype = String()
    service_name = String()
    data = LanzarCampaniaCompletaPayload()


class CancelarSagaPayload(Record):
    """Payload del comando para cancelar saga"""
    saga_id = String()
    razon = String()


class ComandoCancelarSaga(Record):
    """
    Comando CloudEvent para cancelar una saga en progreso desde el BFF hacia campanias.
    """
    id = String()
    time = Long()
    ingestion = Long()
    specversion = String()
    type = String()
    datacontenttype = String() 
    service_name = String()
    data = CancelarSagaPayload()


# ==========================================
# EVENTOS QUE CONSUME EL BFF (RESPUESTAS)
# ==========================================

class EventoSagaIniciada(Record):
    """
    Evento que recibe el BFF cuando una saga se inicia exitosamente en campanias.
    """
    evento_id = String()
    timestamp = String()
    
    saga_id = String()
    comando_id = String()  # Referencia al comando original
    campania_id = String()
    estado_inicial = String()
    pasos_programados = Array(String())  # Lista de pasos de la saga
    tiempo_estimado_minutos = Integer()


class EventoSagaActualizada(Record):
    """
    Evento que recibe el BFF cuando hay actualizaciones en el estado de saga.
    """
    evento_id = String()
    timestamp = String()
    
    saga_id = String()
    estado_anterior = String()
    estado_actual = String()
    paso_actual = String()
    progreso_porcentaje = Double()
    mensaje = String()
    datos_adicionales = Map(String())


class EventoSagaCompletada(Record):
    """
    Evento que recibe el BFF cuando una saga se completa exitosamente.
    """
    evento_id = String()
    timestamp = String()
    
    saga_id = String()
    campania_id = String()
    estado_final = String()
    duracion_total_segundos = Double()
    pasos_ejecutados = Array(String())
    resultados = Map(String())  # Resultados de cada paso


class EventoSagaFallida(Record):
    """
    Evento que recibe el BFF cuando una saga falla.
    """
    evento_id = String()
    timestamp = String()
    
    saga_id = String()
    campania_id = String()
    paso_fallido = String()
    error_mensaje = String()
    error_codigo = String()
    compensacion_iniciada = Boolean()
    recuperable = Boolean()