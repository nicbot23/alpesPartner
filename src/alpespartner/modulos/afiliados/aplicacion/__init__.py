"""
Inicialización del módulo de aplicación de Afiliados
"""

from .comandos import (
    ComandoCrearAfiliado, ComandoActivarAfiliado, ComandoDesactivarAfiliado,
    ComandoSuspenderAfiliado, ComandoBloquearAfiliado, ComandoActualizarDatosBancarios,
    ComandoActualizarConfiguracionComisiones, ComandoAgregarReferencia,
    ComandoActualizarDatosPersonales, ComandoActualizarMetadatos, ComandoValidarAfiliado
)

from .queries import (
    QueryObtenerAfiliado, QueryObtenerAfiliadoPorDocumento, QueryObtenerAfiliadoPorEmail,
    QueryObtenerAfiliadoPorCodigoReferencia, QueryBuscarAfiliados, QueryObtenerReferidosActivos,
    QueryObtenerEstadisticasAfiliados, QueryValidarDisponibilidadDocumento,
    QueryValidarDisponibilidadEmail, QueryCalcularComisiones, QueryObtenerHistorialEstados,
    QueryObtenerReporteAfiliados
)

from .handlers import (
    crear_afiliado_handler, activar_afiliado_handler, desactivar_afiliado_handler,
    suspender_afiliado_handler, bloquear_afiliado_handler, actualizar_datos_bancarios_handler,
    actualizar_configuracion_comisiones_handler, agregar_referencia_handler,
    actualizar_datos_personales_handler, actualizar_metadatos_handler, validar_afiliado_handler
)

from .query_handlers import (
    obtener_afiliado_handler, obtener_afiliado_por_documento_handler,
    obtener_afiliado_por_email_handler, obtener_afiliado_por_codigo_referencia_handler,
    buscar_afiliados_handler, obtener_referidos_activos_handler,
    obtener_estadisticas_afiliados_handler, validar_disponibilidad_documento_handler,
    validar_disponibilidad_email_handler, calcular_comisiones_handler,
    obtener_reporte_afiliados_handler
)

from .servicios import ServicioAplicacionAfiliados

__all__ = [
    # Comandos
    'ComandoCrearAfiliado',
    'ComandoActivarAfiliado',
    'ComandoDesactivarAfiliado',
    'ComandoSuspenderAfiliado',
    'ComandoBloquearAfiliado',
    'ComandoActualizarDatosBancarios',
    'ComandoActualizarConfiguracionComisiones',
    'ComandoAgregarReferencia',
    'ComandoActualizarDatosPersonales',
    'ComandoActualizarMetadatos',
    'ComandoValidarAfiliado',
    
    # Queries
    'QueryObtenerAfiliado',
    'QueryObtenerAfiliadoPorDocumento',
    'QueryObtenerAfiliadoPorEmail',
    'QueryObtenerAfiliadoPorCodigoReferencia',
    'QueryBuscarAfiliados',
    'QueryObtenerReferidosActivos',
    'QueryObtenerEstadisticasAfiliados',
    'QueryValidarDisponibilidadDocumento',
    'QueryValidarDisponibilidadEmail',
    'QueryCalcularComisiones',
    'QueryObtenerHistorialEstados',
    'QueryObtenerReporteAfiliados',
    
    # Command Handlers
    'crear_afiliado_handler',
    'activar_afiliado_handler',
    'desactivar_afiliado_handler',
    'suspender_afiliado_handler',
    'bloquear_afiliado_handler',
    'actualizar_datos_bancarios_handler',
    'actualizar_configuracion_comisiones_handler',
    'agregar_referencia_handler',
    'actualizar_datos_personales_handler',
    'actualizar_metadatos_handler',
    'validar_afiliado_handler',
    
    # Query Handlers
    'obtener_afiliado_handler',
    'obtener_afiliado_por_documento_handler',
    'obtener_afiliado_por_email_handler',
    'obtener_afiliado_por_codigo_referencia_handler',
    'buscar_afiliados_handler',
    'obtener_referidos_activos_handler',
    'obtener_estadisticas_afiliados_handler',
    'validar_disponibilidad_documento_handler',
    'validar_disponibilidad_email_handler',
    'calcular_comisiones_handler',
    'obtener_reporte_afiliados_handler',
    
    # Servicios
    'ServicioAplicacionAfiliados'
]