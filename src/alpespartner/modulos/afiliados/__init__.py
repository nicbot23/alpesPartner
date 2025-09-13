"""
Módulo de Afiliados - Microservicio Descentralizado
===================================================

Módulo responsable de la gestión completa de afiliados en el sistema AlpesPartner.
Implementa una arquitectura de microservicio descentralizado con:

- Base de datos independiente (Puerto 3308)
- Comunicación exclusiva por eventos
- Patrón Outbox descentralizado
- Arquitectura hexagonal con DDD

Estructura del módulo:
- dominio/: Lógica de negocio y reglas de afiliados
- aplicacion/: Casos de uso y coordinación (CQRS)
- infraestructura/: Persistencia y conectores externos
- api/: Interfaz REST HTTP

Eventos de integración:
- AffiliateCreated: Nuevo afiliado registrado
- AffiliateActivated: Afiliado activado
- AffiliateDeactivated: Afiliado desactivado
- AffiliateSuspended: Afiliado suspendido
- AffiliateBlocked: Afiliado bloqueado
- AffiliateBankDetailsUpdated: Datos bancarios actualizados
- AffiliateCommissionConfigUpdated: Configuración de comisiones actualizada
- AffiliateReferenceAdded: Nueva referencia agregada
- AffiliatePersonalDataUpdated: Datos personales actualizados
- AffiliateValidated: Afiliado validado

Este módulo sigue el patrón de microservicio descentralizado,
manteniendo independencia total de otros módulos del sistema.
"""

__version__ = "1.0.0"
__author__ = "AlpesPartner Team"

# Importaciones principales del módulo
from .dominio.agregados import Afiliado
from .dominio.objetos_valor import (
    TipoAfiliado, EstadoAfiliado, DatosBancarios, 
    ConfiguracionComisiones, DatosPersonales, Referencia
)
from .dominio.eventos import (
    AffiliateCreated, AffiliateActivated, AffiliateDeactivated,
    AffiliateSuspended, AffiliateBlocked, AffiliateBankDetailsUpdated,
    AffiliateCommissionConfigUpdated, AffiliateReferenceAdded,
    AffiliatePersonalDataUpdated, AffiliateValidated
)
from .dominio.excepciones import (
    ExcepcionAfiliados, AfiliadoNoExiste, DocumentoYaRegistrado,
    EmailYaRegistrado, TransicionEstadoInvalida
)
from .dominio.repositorios import RepositorioAfiliados
from .dominio.fabricas import FabricaAfiliados
from .dominio.servicios import ServicioDominioAfiliados

from .aplicacion.comandos import (
    ComandoCrearAfiliado, ComandoActivarAfiliado, ComandoDesactivarAfiliado,
    ComandoSuspenderAfiliado, ComandoBloquearAfiliado, ComandoActualizarDatosBancarios,
    ComandoActualizarConfiguracionComisiones, ComandoAgregarReferencia,
    ComandoActualizarDatosPersonales, ComandoValidarAfiliado
)
from .aplicacion.queries import (
    QueryObtenerAfiliado, QueryObtenerAfiliadoPorDocumento, QueryObtenerAfiliadoPorEmail,
    QueryBuscarAfiliados, QueryObtenerReferidosActivos, QueryObtenerEstadisticasAfiliados,
    QueryValidarDisponibilidadDocumento, QueryValidarDisponibilidadEmail,
    QueryCalcularComisiones, QueryObtenerReporteAfiliados
)
from .aplicacion.servicios import ServicioAplicacionAfiliados

from .infraestructura.db import engine_afiliados, SessionAfiliados, obtener_session_afiliados
from .infraestructura.repositorios import RepositorioAfiliadosSQLAlchemy

from .api.app import bp_afiliados

# Exportaciones públicas del módulo
__all__ = [
    # Dominio
    "Afiliado",
    "TipoAfiliado", "EstadoAfiliado", "DatosBancarios", 
    "ConfiguracionComisiones", "DatosPersonales", "Referencia",
    "AffiliateCreated", "AffiliateActivated", "AffiliateDeactivated",
    "AffiliateSuspended", "AffiliateBlocked", "AffiliateBankDetailsUpdated",
    "AffiliateCommissionConfigUpdated", "AffiliateReferenceAdded",
    "AffiliatePersonalDataUpdated", "AffiliateValidated",
    "ExcepcionAfiliados", "AfiliadoNoExiste", "DocumentoYaRegistrado",
    "EmailYaRegistrado", "TransicionEstadoInvalida",
    "RepositorioAfiliados", "FabricaAfiliados", "ServicioDominioAfiliados",
    
    # Aplicación
    "ComandoCrearAfiliado", "ComandoActivarAfiliado", "ComandoDesactivarAfiliado",
    "ComandoSuspenderAfiliado", "ComandoBloquearAfiliado", "ComandoActualizarDatosBancarios",
    "ComandoActualizarConfiguracionComisiones", "ComandoAgregarReferencia",
    "ComandoActualizarDatosPersonales", "ComandoValidarAfiliado",
    "QueryObtenerAfiliado", "QueryObtenerAfiliadoPorDocumento", "QueryObtenerAfiliadoPorEmail",
    "QueryBuscarAfiliados", "QueryObtenerReferidosActivos", "QueryObtenerEstadisticasAfiliados",
    "QueryValidarDisponibilidadDocumento", "QueryValidarDisponibilidadEmail",
    "QueryCalcularComisiones", "QueryObtenerReporteAfiliados",
    "ServicioAplicacionAfiliados",
    
    # Infraestructura
    "engine_afiliados", "SessionAfiliados", "obtener_session_afiliados",
    "RepositorioAfiliadosSQLAlchemy",
    
    # API
    "bp_afiliados"
]

# Metadatos del módulo
MODULO_INFO = {
    "nombre": "afiliados",
    "version": __version__,
    "descripcion": "Microservicio descentralizado de gestión de afiliados",
    "tipo": "microservicio",
    "puerto_bd": 3308,
    "base_datos": "afiliados_db",
    "comunicacion": "eventos",
    "patron_arquitectura": "hexagonal_ddd",
    "patron_persistencia": "outbox_descentralizado"
}


def obtener_info_modulo():
    """Retorna información del módulo de afiliados."""
    return MODULO_INFO


def registrar_blueprint(app):
    """
    Registra el blueprint de afiliados en la aplicación Flask.
    
    Args:
        app: Instancia de aplicación Flask
    """
    app.register_blueprint(bp_afiliados)
    return app


def inicializar_modulo():
    """
    Inicializa el módulo de afiliados.
    Puede usarse para configuraciones adicionales.
    """
    print(f"Inicializando módulo {MODULO_INFO['nombre']} v{MODULO_INFO['version']}")
    print(f"Base de datos: {MODULO_INFO['base_datos']} en puerto {MODULO_INFO['puerto_bd']}")
    print(f"Comunicación: {MODULO_INFO['comunicacion']}")
    return True
