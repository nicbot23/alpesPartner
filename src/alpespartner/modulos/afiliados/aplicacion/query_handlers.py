"""
Query handlers para el módulo de Afiliados
Manejan las consultas de información sin cambio de estado
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal

from alpespartner.seedwork.aplicacion.handlers import QueryHandler
from alpespartner.seedwork.aplicacion.queries import ejecutar_query as query
from alpespartner.seedwork.infraestructura.uow import UnidadTrabajo

from ..dominio.repositorios import RepositorioAfiliados
from ..dominio.servicios import ServicioDominioAfiliados
from ..dominio.excepciones import AfiliadoNoExiste

from .queries import (
    QueryObtenerAfiliado, QueryObtenerAfiliadoPorDocumento, QueryObtenerAfiliadoPorEmail,
    QueryObtenerAfiliadoPorCodigoReferencia, QueryBuscarAfiliados, QueryObtenerReferidosActivos,
    QueryObtenerEstadisticasAfiliados, QueryValidarDisponibilidadDocumento,
    QueryValidarDisponibilidadEmail, QueryCalcularComisiones, QueryObtenerHistorialEstados,
    QueryObtenerReporteAfiliados
)


@QueryHandler(QueryObtenerAfiliado)
def obtener_afiliado_handler(query: QueryObtenerAfiliado, uow: UnidadTrabajo) -> Dict[str, Any]:
    """
    Handler para obtener un afiliado por ID.
    
    Args:
        query: Query con ID del afiliado
        uow: Unidad de trabajo
        
    Returns:
        Dict con datos del afiliado o None si no existe
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    
    afiliado = repositorio.obtener_por_id(query.afiliado_id)
    
    if not afiliado:
        return None
    
    return {
        'id': afiliado.id,
        'nombres': afiliado.datos_personales.nombres,
        'apellidos': afiliado.datos_personales.apellidos,
        'email': afiliado.datos_contacto.email,
        'documento': {
            'tipo': afiliado.documento_identidad.tipo.value,
            'numero': afiliado.documento_identidad.numero
        },
        'tipo_afiliado': afiliado.tipo_afiliado.value,
        'estado': afiliado.estado.value,
        'codigo_referencia': afiliado.codigo_referencia,
        'fecha_creacion': afiliado.fecha_creacion.isoformat() if afiliado.fecha_creacion else None,
        'comisiones': {
            'porcentaje_base': float(afiliado.configuracion_comisiones.porcentaje_base),
            'porcentaje_premium': float(afiliado.configuracion_comisiones.porcentaje_premium) if afiliado.configuracion_comisiones.porcentaje_premium else None,
            'monto_minimo': float(afiliado.configuracion_comisiones.monto_minimo) if afiliado.configuracion_comisiones.monto_minimo else None
        },
        'referencias_count': len(afiliado.referencias)
    }


@QueryHandler(QueryObtenerAfiliadoPorDocumento)
def obtener_afiliado_por_documento_handler(query: QueryObtenerAfiliadoPorDocumento, uow: UnidadTrabajo) -> Optional[Dict[str, Any]]:
    """
    Handler para obtener un afiliado por documento.
    
    Args:
        query: Query con datos del documento
        uow: Unidad de trabajo
        
    Returns:
        Dict con datos del afiliado o None si no existe
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    
    afiliado = repositorio.obtener_por_documento(query.tipo_documento, query.numero_documento)
    
    if not afiliado:
        return None
    
    # Reutilizar la lógica del handler anterior
    query_afiliado = QueryObtenerAfiliado(afiliado_id=afiliado.id)
    return obtener_afiliado_handler(query_afiliado, uow)


@QueryHandler(QueryObtenerAfiliadoPorEmail)
def obtener_afiliado_por_email_handler(query: QueryObtenerAfiliadoPorEmail, uow: UnidadTrabajo) -> Optional[Dict[str, Any]]:
    """
    Handler para obtener un afiliado por email.
    
    Args:
        query: Query con email
        uow: Unidad de trabajo
        
    Returns:
        Dict con datos del afiliado o None si no existe
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    
    afiliado = repositorio.obtener_por_email(query.email)
    
    if not afiliado:
        return None
    
    query_afiliado = QueryObtenerAfiliado(afiliado_id=afiliado.id)
    return obtener_afiliado_handler(query_afiliado, uow)


@QueryHandler(QueryObtenerAfiliadoPorCodigoReferencia)
def obtener_afiliado_por_codigo_referencia_handler(query: QueryObtenerAfiliadoPorCodigoReferencia, uow: UnidadTrabajo) -> Optional[Dict[str, Any]]:
    """
    Handler para obtener un afiliado por código de referencia.
    
    Args:
        query: Query con código de referencia
        uow: Unidad de trabajo
        
    Returns:
        Dict con datos del afiliado o None si no existe
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    
    afiliado = repositorio.obtener_por_codigo_referencia(query.codigo_referencia)
    
    if not afiliado:
        return None
    
    query_afiliado = QueryObtenerAfiliado(afiliado_id=afiliado.id)
    return obtener_afiliado_handler(query_afiliado, uow)


@QueryHandler(QueryBuscarAfiliados)
def buscar_afiliados_handler(query: QueryBuscarAfiliados, uow: UnidadTrabajo) -> Dict[str, Any]:
    """
    Handler para buscar afiliados con filtros.
    
    Args:
        query: Query con filtros de búsqueda
        uow: Unidad de trabajo
        
    Returns:
        Dict con resultados de la búsqueda
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    
    # Construir filtros
    filtros = {}
    if query.estado:
        filtros['estado'] = query.estado
    if query.tipo_afiliado:
        filtros['tipo_afiliado'] = query.tipo_afiliado
    if query.email_like:
        filtros['email_like'] = query.email_like
    if query.nombres_like:
        filtros['nombres_like'] = query.nombres_like
    if query.fecha_desde:
        filtros['fecha_desde'] = query.fecha_desde
    if query.fecha_hasta:
        filtros['fecha_hasta'] = query.fecha_hasta
    if query.afiliado_referente_id:
        filtros['afiliado_referente_id'] = query.afiliado_referente_id
    
    # Buscar afiliados
    afiliados = repositorio.buscar_con_filtros(
        filtros=filtros,
        ordenar_por=query.ordenar_por,
        orden_desc=query.orden_desc,
        limite=query.limite,
        offset=query.offset
    )
    
    # Convertir a diccionarios
    resultados = []
    for afiliado in afiliados:
        resultado = {
            'id': afiliado.id,
            'nombres': afiliado.datos_personales.nombres,
            'apellidos': afiliado.datos_personales.apellidos,
            'email': afiliado.datos_contacto.email,
            'tipo_afiliado': afiliado.tipo_afiliado.value,
            'estado': afiliado.estado.value,
            'codigo_referencia': afiliado.codigo_referencia,
            'fecha_creacion': afiliado.fecha_creacion.isoformat() if afiliado.fecha_creacion else None
        }
        resultados.append(resultado)
    
    return {
        'afiliados': resultados,
        'total': len(resultados),
        'offset': query.offset,
        'limite': query.limite
    }


@QueryHandler(QueryObtenerReferidosActivos)
def obtener_referidos_activos_handler(query: QueryObtenerReferidosActivos, uow: UnidadTrabajo) -> List[Dict[str, Any]]:
    """
    Handler para obtener afiliados referidos activos.
    
    Args:
        query: Query con ID del afiliado referente
        uow: Unidad de trabajo
        
    Returns:
        Lista de afiliados referidos activos
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    servicio_dominio = ServicioDominioAfiliados(repositorio)
    
    referidos_activos = servicio_dominio.obtener_afiliados_referidos_activos(query.afiliado_referente_id)
    
    resultados = []
    for afiliado in referidos_activos:
        resultado = {
            'id': afiliado.id,
            'nombres': afiliado.datos_personales.nombres,
            'apellidos': afiliado.datos_personales.apellidos,
            'email': afiliado.datos_contacto.email,
            'tipo_afiliado': afiliado.tipo_afiliado.value,
            'estado': afiliado.estado.value,
            'fecha_creacion': afiliado.fecha_creacion.isoformat() if afiliado.fecha_creacion else None
        }
        resultados.append(resultado)
    
    return resultados


@QueryHandler(QueryObtenerEstadisticasAfiliados)
def obtener_estadisticas_afiliados_handler(query: QueryObtenerEstadisticasAfiliados, uow: UnidadTrabajo) -> Dict[str, Any]:
    """
    Handler para obtener estadísticas de afiliados.
    
    Args:
        query: Query con parámetros de estadísticas
        uow: Unidad de trabajo
        
    Returns:
        Dict con estadísticas calculadas
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    
    estadisticas = repositorio.obtener_estadisticas(
        fecha_desde=query.fecha_desde,
        fecha_hasta=query.fecha_hasta
    )
    
    return estadisticas


@QueryHandler(QueryValidarDisponibilidadDocumento)
def validar_disponibilidad_documento_handler(query: QueryValidarDisponibilidadDocumento, uow: UnidadTrabajo) -> Dict[str, Any]:
    """
    Handler para validar disponibilidad de documento.
    
    Args:
        query: Query con datos del documento
        uow: Unidad de trabajo
        
    Returns:
        Dict con resultado de la validación
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    servicio_dominio = ServicioDominioAfiliados(repositorio)
    
    try:
        servicio_dominio.verificar_unicidad_documento(
            query.tipo_documento,
            query.numero_documento,
            query.excluir_afiliado_id
        )
        disponible = True
        mensaje = "Documento disponible"
    except Exception as e:
        disponible = False
        mensaje = str(e)
    
    return {
        'disponible': disponible,
        'mensaje': mensaje,
        'tipo_documento': query.tipo_documento,
        'numero_documento': query.numero_documento
    }


@QueryHandler(QueryValidarDisponibilidadEmail)
def validar_disponibilidad_email_handler(query: QueryValidarDisponibilidadEmail, uow: UnidadTrabajo) -> Dict[str, Any]:
    """
    Handler para validar disponibilidad de email.
    
    Args:
        query: Query con email
        uow: Unidad de trabajo
        
    Returns:
        Dict con resultado de la validación
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    servicio_dominio = ServicioDominioAfiliados(repositorio)
    
    try:
        servicio_dominio.verificar_unicidad_email(
            query.email,
            query.excluir_afiliado_id
        )
        disponible = True
        mensaje = "Email disponible"
    except Exception as e:
        disponible = False
        mensaje = str(e)
    
    return {
        'disponible': disponible,
        'mensaje': mensaje,
        'email': query.email
    }


@QueryHandler(QueryCalcularComisiones)
def calcular_comisiones_handler(query: QueryCalcularComisiones, uow: UnidadTrabajo) -> Dict[str, Any]:
    """
    Handler para calcular comisiones de un afiliado.
    
    Args:
        query: Query con datos para cálculo
        uow: Unidad de trabajo
        
    Returns:
        Dict con cálculos de comisiones
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    servicio_dominio = ServicioDominioAfiliados(repositorio)
    
    afiliado = repositorio.obtener_por_id(query.afiliado_id)
    if not afiliado:
        raise AfiliadoNoExiste(query.afiliado_id)
    
    monto_transaccion = Decimal(query.monto_transaccion)
    
    # Calcular comisión principal
    comision_principal = servicio_dominio.calcular_comisiones_escalonadas(
        afiliado, monto_transaccion
    )
    
    resultado = {
        'afiliado_id': query.afiliado_id,
        'monto_transaccion': float(monto_transaccion),
        'comision_principal': float(comision_principal),
        'porcentaje_aplicado': float(afiliado.configuracion_comisiones.porcentaje_base)
    }
    
    # Calcular comisión por referencia si es solicitado
    if query.incluir_comision_referencia and afiliado.afiliado_referente_id:
        afiliado_referente = repositorio.obtener_por_id(afiliado.afiliado_referente_id)
        if afiliado_referente:
            comision_referencia = servicio_dominio.calcular_comision_por_referidos(
                afiliado_referente, comision_principal
            )
            resultado['comision_referencia'] = {
                'afiliado_referente_id': afiliado.afiliado_referente_id,
                'monto': float(comision_referencia)
            }
    
    return resultado


@QueryHandler(QueryObtenerReporteAfiliados)
def obtener_reporte_afiliados_handler(query: QueryObtenerReporteAfiliados, uow: UnidadTrabajo) -> Dict[str, Any]:
    """
    Handler para generar reporte de afiliados.
    
    Args:
        query: Query con parámetros del reporte
        uow: Unidad de trabajo
        
    Returns:
        Dict con datos del reporte
    """
    repositorio: RepositorioAfiliados = uow._repositorio_afiliados
    
    # Aplicar filtros si existen
    filtros = query.filtros or {}
    afiliados = repositorio.buscar_con_filtros(filtros=filtros, limite=1000)
    
    # Construir reporte básico
    reporte = {
        'fecha_generacion': query.fecha_generacion.isoformat() if hasattr(query, 'fecha_generacion') else None,
        'formato': query.formato,
        'total_afiliados': len(afiliados),
        'afiliados': []
    }
    
    # Agregar datos de afiliados
    for afiliado in afiliados:
        datos_afiliado = {
            'id': afiliado.id,
            'nombres': afiliado.datos_personales.nombres,
            'apellidos': afiliado.datos_personales.apellidos,
            'email': afiliado.datos_contacto.email,
            'documento': f"{afiliado.documento_identidad.tipo.value}-{afiliado.documento_identidad.numero}",
            'tipo_afiliado': afiliado.tipo_afiliado.value,
            'estado': afiliado.estado.value,
            'fecha_creacion': afiliado.fecha_creacion.isoformat() if afiliado.fecha_creacion else None
        }
        
        if query.incluir_referencias:
            datos_afiliado['referencias_count'] = len(afiliado.referencias)
            datos_afiliado['tiene_referente'] = afiliado.afiliado_referente_id is not None
        
        reporte['afiliados'].append(datos_afiliado)
    
    # Agregar estadísticas si se solicita
    if query.incluir_estadisticas:
        estadisticas = repositorio.obtener_estadisticas()
        reporte['estadisticas'] = estadisticas
    
    return reporte