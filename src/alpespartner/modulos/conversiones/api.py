"""
API REST para el módulo de Conversiones.
Microservicio descentralizado con endpoints especializados.
"""

from flask import Blueprint, request, jsonify
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Optional, Dict, Any
import logging

from alpespartner.modulos.conversiones.aplicacion.servicios import ServicioConversiones
from alpespartner.modulos.conversiones.infraestructura.repositorios import RepositorioConversionesMySQL
from alpespartner.modulos.conversiones.infraestructura.db import ConversionesSessionLocal
from alpespartner.seedwork.aplicacion.mediador import Mediador
from alpespartner.seedwork.dominio.excepciones import ReglaNegocioException


logger = logging.getLogger(__name__)

# Blueprint para el módulo de conversiones
bp_conversiones = Blueprint('conversiones', __name__, url_prefix='/api/v1/conversiones')


# Funciones de validación

def validate_create_conversion_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida datos para crear conversión."""
    errors = {}
    
    if not data.get('afiliado_id'):
        errors['afiliado_id'] = 'Campo requerido'
    if not data.get('campana_id'):
        errors['campana_id'] = 'Campo requerido'
    if not data.get('tipo_conversion'):
        errors['tipo_conversion'] = 'Campo requerido'
    elif data['tipo_conversion'] not in ['VENTA', 'LEAD', 'CLICK', 'IMPRESION']:
        errors['tipo_conversion'] = 'Tipo inválido'
    
    if not data.get('monto_transaccion'):
        errors['monto_transaccion'] = 'Campo requerido'
    else:
        try:
            data['monto_transaccion'] = Decimal(str(data['monto_transaccion']))
        except (InvalidOperation, ValueError):
            errors['monto_transaccion'] = 'Monto inválido'
    
    if not data.get('fecha_conversion'):
        errors['fecha_conversion'] = 'Campo requerido'
    else:
        try:
            data['fecha_conversion'] = datetime.fromisoformat(data['fecha_conversion'])
        except ValueError:
            errors['fecha_conversion'] = 'Formato de fecha inválido (ISO 8601)'
    
    data['metadata'] = data.get('metadata', {})
    
    if errors:
        raise ValueError(f"Errores de validación: {errors}")
    
    return data


def validate_required_field(data: Dict[str, Any], field: str) -> str:
    """Valida que un campo requerido esté presente."""
    value = data.get(field)
    if not value:
        raise ValueError(f"Campo '{field}' es requerido")
    return value


# Función auxiliar para crear servicio
def get_servicio_conversiones() -> ServicioConversiones:
    """Factory para crear el servicio de conversiones."""
    repositorio = RepositorioConversionesMySQL()
    mediador = Mediador()
    return ServicioConversiones(repositorio, mediador)


# Endpoints

@bp_conversiones.route('', methods=['POST'])
def crear_conversion():
    """Crear una nueva conversión."""
    try:
        data = validate_create_conversion_data(request.json or {})
        
        servicio = get_servicio_conversiones()
        conversion_id = servicio.crear_conversion(
            afiliado_id=data['afiliado_id'],
            campana_id=data['campana_id'],
            tipo_conversion=data['tipo_conversion'],
            monto_transaccion=data['monto_transaccion'],
            fecha_conversion=data['fecha_conversion'],
            metadata=data['metadata']
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Conversión creada exitosamente',
            'data': {'conversion_id': conversion_id}
        }), 201
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except ReglaNegocioException as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creando conversión: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('/<conversion_id>', methods=['GET'])
def obtener_conversion(conversion_id: str):
    """Obtener una conversión específica."""
    try:
        servicio = get_servicio_conversiones()
        conversion = servicio.obtener_conversion(conversion_id)
        
        return jsonify({
            'status': 'success',
            'data': conversion
        })
        
    except ReglaNegocioException as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error obteniendo conversión {conversion_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('', methods=['GET'])
def listar_conversiones():
    """Listar conversiones con filtros opcionales."""
    try:
        # Obtener parámetros de consulta
        afiliado_id = request.args.get('afiliado_id')
        campana_id = request.args.get('campana_id')
        tipo_conversion = request.args.get('tipo_conversion')
        estado = request.args.get('estado')
        fecha_desde_str = request.args.get('fecha_desde')
        fecha_hasta_str = request.args.get('fecha_hasta')
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        
        # Convertir fechas si están presentes
        fecha_desde = None
        fecha_hasta = None
        if fecha_desde_str:
            fecha_desde = datetime.fromisoformat(fecha_desde_str)
        if fecha_hasta_str:
            fecha_hasta = datetime.fromisoformat(fecha_hasta_str)
        
        servicio = get_servicio_conversiones()
        resultado = servicio.listar_conversiones(
            afiliado_id=afiliado_id,
            campana_id=campana_id,
            tipo_conversion=tipo_conversion,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            page=page,
            size=size
        )
        
        return jsonify({
            'status': 'success',
            'data': resultado
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Formato de fecha inválido: {e}'
        }), 400
    except Exception as e:
        logger.error(f"Error listando conversiones: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('/<conversion_id>/validate', methods=['POST'])
def validar_conversion(conversion_id: str):
    """Validar una conversión."""
    try:
        data = request.json or {}
        validado_por = validate_required_field(data, 'validado_por')
        notas_validacion = data.get('notas_validacion')
        
        servicio = get_servicio_conversiones()
        servicio.validar_conversion(
            conversion_id=conversion_id,
            validado_por=validado_por,
            notas_validacion=notas_validacion
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Conversión validada exitosamente'
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except ReglaNegocioException as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error validando conversión {conversion_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('/<conversion_id>/confirm', methods=['POST'])
def confirmar_conversion(conversion_id: str):
    """Confirmar una conversión manualmente."""
    try:
        data = request.json or {}
        confirmado_por = validate_required_field(data, 'confirmado_por')
        notas_confirmacion = data.get('notas_confirmacion')
        
        servicio = get_servicio_conversiones()
        servicio.confirmar_conversion(
            conversion_id=conversion_id,
            confirmado_por=confirmado_por,
            notas_confirmacion=notas_confirmacion
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Conversión confirmada exitosamente'
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except ReglaNegocioException as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error confirmando conversión {conversion_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('/<conversion_id>/reject', methods=['POST'])
def rechazar_conversion(conversion_id: str):
    """Rechazar una conversión."""
    try:
        data = request.json or {}
        rechazado_por = validate_required_field(data, 'rechazado_por')
        motivo_rechazo = validate_required_field(data, 'motivo_rechazo')
        
        servicio = get_servicio_conversiones()
        servicio.rechazar_conversion(
            conversion_id=conversion_id,
            rechazado_por=rechazado_por,
            motivo_rechazo=motivo_rechazo
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Conversión rechazada exitosamente'
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except ReglaNegocioException as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error rechazando conversión {conversion_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('/<conversion_id>/cancel', methods=['POST'])
def cancelar_conversion(conversion_id: str):
    """Cancelar una conversión."""
    try:
        data = request.json or {}
        cancelado_por = validate_required_field(data, 'cancelado_por')
        motivo_cancelacion = validate_required_field(data, 'motivo_cancelacion')
        
        servicio = get_servicio_conversiones()
        servicio.cancelar_conversion(
            conversion_id=conversion_id,
            cancelado_por=cancelado_por,
            motivo_cancelacion=motivo_cancelacion
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Conversión cancelada exitosamente'
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except ReglaNegocioException as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error cancelando conversión {conversion_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('/<conversion_id>/attribute', methods=['POST'])
def atribuir_comision(conversion_id: str):
    """Atribuir una comisión a una conversión."""
    try:
        data = request.json or {}
        comision_id = validate_required_field(data, 'comision_id')
        atribuido_por = validate_required_field(data, 'atribuido_por')
        
        try:
            monto_comision = Decimal(str(data.get('monto_comision', 0)))
        except (InvalidOperation, ValueError):
            raise ValueError("Monto de comisión inválido")
        
        servicio = get_servicio_conversiones()
        servicio.atribuir_comision(
            conversion_id=conversion_id,
            comision_id=comision_id,
            monto_comision=monto_comision,
            atribuido_por=atribuido_por
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Comisión atribuida exitosamente'
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except ReglaNegocioException as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error atribuyendo comisión a conversión {conversion_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('/afiliado/<afiliado_id>', methods=['GET'])
def obtener_conversiones_afiliado(afiliado_id: str):
    """Obtener conversiones de un afiliado específico."""
    try:
        incluir_canceladas = request.args.get('incluir_canceladas', 'false').lower() == 'true'
        
        servicio = get_servicio_conversiones()
        conversiones = servicio.obtener_conversiones_afiliado(
            afiliado_id=afiliado_id,
            incluir_canceladas=incluir_canceladas
        )
        
        return jsonify({
            'status': 'success',
            'data': conversiones
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo conversiones del afiliado {afiliado_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('/campana/<campana_id>', methods=['GET'])
def obtener_conversiones_campana(campana_id: str):
    """Obtener conversiones de una campaña específica."""
    try:
        estado = request.args.get('estado')
        
        servicio = get_servicio_conversiones()
        conversiones = servicio.obtener_conversiones_campana(
            campana_id=campana_id,
            estado=estado
        )
        
        return jsonify({
            'status': 'success',
            'data': conversiones
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo conversiones de la campaña {campana_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('/stats', methods=['GET'])
def obtener_estadisticas():
    """Obtener estadísticas de conversiones."""
    try:
        fecha_desde_str = request.args.get('fecha_desde')
        fecha_hasta_str = request.args.get('fecha_hasta')
        agrupado_por = request.args.get('agrupado_por', 'estado')
        
        # Convertir fechas si están presentes
        fecha_desde = None
        fecha_hasta = None
        if fecha_desde_str:
            fecha_desde = datetime.fromisoformat(fecha_desde_str)
        if fecha_hasta_str:
            fecha_hasta = datetime.fromisoformat(fecha_hasta_str)
        
        servicio = get_servicio_conversiones()
        stats = servicio.obtener_estadisticas(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            agrupado_por=agrupado_por
        )
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Formato de fecha inválido: {e}'
        }), 400
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500


@bp_conversiones.route('/health', methods=['GET'])
def health_check():
    """Health check para el microservicio de conversiones."""
    try:
        # Verificar conexión a base de datos
        session = ConversionesSessionLocal()
        session.execute('SELECT 1')
        session.close()
        
        return jsonify({
            'status': 'healthy',
            'service': 'conversiones',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'conversiones',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 503