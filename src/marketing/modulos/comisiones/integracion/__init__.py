"""
Módulo de integración para eventos entre bounded contexts
Arquitectura: Event-Driven + Domain Events + Apache Pulsar + Async Processing
"""

from .eventos import (
    EventoIntegracionComision,
    ComisionCreada,
    ComisionCalculada,
    ComisionAprobada,
    ComisionRechazada,
    ComisionPagada,
    ComisionAnulada,
    SolicitudValidacionAfiliado,
    SolicitudVerificacionConversion,
    NotificacionEstadoComision,
    FabricaEventosIntegracion,
    RegistroEventosIntegracion
)

from .manejadores import (
    ManejadorEventoIntegracion,
    RepositorioEventosIntegracion,
    ManejadorComisionCreada,
    ManejadorComisionCalculada,
    ManejadorComisionAprobada,
    CoordinadorEventosIntegracion,
    ServicioIntegracionComisiones
)

__all__ = [
    # Eventos
    'EventoIntegracionComision',
    'ComisionCreada',
    'ComisionCalculada', 
    'ComisionAprobada',
    'ComisionRechazada',
    'ComisionPagada',
    'ComisionAnulada',
    'SolicitudValidacionAfiliado',
    'SolicitudVerificacionConversion',
    'NotificacionEstadoComision',
    'FabricaEventosIntegracion',
    'RegistroEventosIntegracion',
    
    # Manejadores
    'ManejadorEventoIntegracion',
    'RepositorioEventosIntegracion',
    'ManejadorComisionCreada',
    'ManejadorComisionCalculada',
    'ManejadorComisionAprobada',
    'CoordinadorEventosIntegracion',
    'ServicioIntegracionComisiones'
]