"""
Seedwork completo para el microservicio Marketing
Arquitectura enterprise con principios SOLID, CQRS, DDD y Event-Driven
"""

# Aplicación - CQRS/CQS
from .aplicacion.comandos import (
    Comando, ManejadorComando, BusComandos,
    ValidadorComando, InterceptorComando, BusComandosImplemetacion
)

from .aplicacion.consultas import (
    Consulta, ManejadorConsulta, BusConsultas,
    ResultadoPaginado, CacheConsultas, BusConsultasImplementacion
)

from .aplicacion.outbox import (
    EventoOutboxMarketing, RepositorioOutboxMarketing, ServicioOutboxMarketing
)

from .aplicacion.eventos_integracion import (
    NuevoAfiliadoDisponible, AfiliadoActualizado, AfiliadoDesactivado,
    ConversionRegistrada, ConversionAnulada, CampanaLanzada,
    CampanaPausadaOFinalizada, NuevoSegmentoCreado, MetricasCampanaActualizadas,
    ComisionCalculada, RendimientoAfiliadoAnalizado, AlertaCampanaPresupuesto,
    ReporteCampanaFinalizada, SchemaEventosIntegracion
)

# Dominio - Entidades y Eventos
from .dominio.eventos import (
    EventoDominio, EventoIntegracion, EventoMarketingBase,
    GeneradorEventos, DespachadorEventos, RepositorioEventos,
    ManejadorEvento, BusEventos, BusEventosImplementacion,
    FabricaBusEventos, ObservadorEventos, PublicadorEventos
)

from .dominio.entidades import (
    EstadoCampana, TipoCampana, TipoSegmento, EntidadBase,
    ConfiguracionCampana, CriterioSegmentacion, Campana, Segmento,
    CampanaCreada, CampanaActivada, CampanaPausada, SegmentoCreado,
    RepositorioCampanas, RepositorioSegmentos, FabricaMarketing
)

# Infraestructura - Repositorios y Despachadores
from .infraestructura.repositorios import (
    ConexionBaseDatos, TransaccionBaseDatos, MapeadorCampana, MapeadorSegmento,
    RepositorioCampanasSQLAlchemy, RepositorioSegmentosSQLAlchemy,
    RepositorioEventosSQLAlchemy, FabricaRepositoriosMarketing,
    UnidadDeTrabajoMarketing
)

from .infraestructura.despachadores import (
    ConfiguracionPulsarMarketing, EstadoCircuitBreaker, CircuitBreakerPulsar,
    ManejadorReintentos, DespachadorPulsarMarketing, ConsumidorEventosMarketing,
    FabricaDespachadorMarketing
)

__all__ = [
    # Aplicación
    'Comando', 'ComandoConRespuesta', 'ManejadorComando', 'BusComandos',
    'ValidadorComando', 'InterceptorComando', 'BusComandosImplementacion',
    'Consulta', 'ConsultaConPaginacion', 'ManejadorConsulta', 'BusConsultas',
    'ResultadoPaginado', 'CacheConsultas', 'BusConsultasImplementacion',
    'EventoOutboxMarketing', 'PrioridadEvento', 'EstadoEvento',
    'RepositorioOutboxMarketing', 'ServicioOutboxMarketing',
    
    # Eventos de Integración
    'NuevoAfiliadoDisponible', 'AfiliadoActualizado', 'AfiliadoDesactivado',
    'ConversionRegistrada', 'ConversionAnulada', 'CampanaLanzada',
    'CampanaPausadaOFinalizada', 'NuevoSegmentoCreado', 'MetricasCampanaActualizadas',
    'ComisionCalculada', 'RendimientoAfiliadoAnalizado', 'AlertaCampanaPresupuesto',
    'ReporteCampanaFinalizada', 'SchemaEventosIntegracion',
    
    # Dominio
    'EventoDominio', 'EventoIntegracion', 'EventoMarketingBase',
    'GeneradorEventos', 'DespachadorEventos', 'RepositorioEventos',
    'ManejadorEvento', 'BusEventos', 'BusEventosImplementacion',
    'FabricaBusEventos', 'ObservadorEventos', 'PublicadorEventos',
    'EstadoCampana', 'TipoCampana', 'TipoSegmento', 'EntidadBase',
    'ConfiguracionCampana', 'CriterioSegmentacion', 'Campana', 'Segmento',
    'CampanaCreada', 'CampanaActivada', 'CampanaPausada', 'SegmentoCreado',
    'RepositorioCampanas', 'RepositorioSegmentos', 'FabricaMarketing',
    
    # Infraestructura
    'ConexionBaseDatos', 'TransaccionBaseDatos', 'MapeadorCampana', 'MapeadorSegmento',
    'RepositorioCampanasSQLAlchemy', 'RepositorioSegmentosSQLAlchemy',
    'RepositorioEventosSQLAlchemy', 'FabricaRepositoriosMarketing',
    'UnidadDeTrabajoMarketing', 'ConfiguracionPulsarMarketing',
    'EstadoCircuitBreaker', 'CircuitBreakerPulsar', 'ManejadorReintentos',
    'DespachadorPulsarMarketing', 'ConsumidorEventosMarketing',
    'FabricaDespachadorMarketing'
]

# Información del seedwork
__version__ = "1.0.0"
__description__ = "Seedwork enterprise para microservicio Marketing con SOLID, CQRS, DDD y Event-Driven Architecture"