"""
API REST para el microservicio de Afiliados
Expone endpoints HTTP para operaciones de afiliados
"""

from flask import Blueprint, request, jsonify
from flask.views import MethodView
from datetime import datetime
from decimal import Decimal, InvalidOperation
import uuid

from alpespartner.seedwork.infraestructura.uow import UnidadTrabajo
from alpespartner.seedwork.aplicacion.comandos import ejecutar_commando
from alpespartner.seedwork.aplicacion.queries import ejecutar_query
from alpespartner.modulos.afiliados.dominio.excepciones import ExcepcionDominio

from ..aplicacion.comandos import (
    ComandoCrearAfiliado, ComandoActivarAfiliado, ComandoDesactivarAfiliado,
    ComandoSuspenderAfiliado, ComandoBloquearAfiliado, ComandoActualizarDatosBancarios,
    ComandoActualizarConfiguracionComisiones, ComandoAgregarReferencia,
    ComandoActualizarDatosPersonales, ComandoValidarAfiliado
)

from ..aplicacion.queries import (
    QueryObtenerAfiliado, QueryObtenerAfiliadoPorDocumento, QueryObtenerAfiliadoPorEmail,
    QueryBuscarAfiliados, QueryObtenerReferidosActivos, QueryObtenerEstadisticasAfiliados,
    QueryValidarDisponibilidadDocumento, QueryValidarDisponibilidadEmail,
    QueryCalcularComisiones, QueryObtenerReporteAfiliados
)

from ..aplicacion.servicios import ServicioAplicacionAfiliados
from ..dominio.excepciones import (
    ExcepcionAfiliados, AfiliadoNoExiste, DocumentoYaRegistrado,
    EmailYaRegistrado, TransicionEstadoInvalida
)
from ..infraestructura.repositorios import RepositorioAfiliadosSQLAlchemy
from ..infraestructura.db import obtener_session_afiliados


# Blueprint para afiliados
bp_afiliados = Blueprint('afiliados', __name__, url_prefix='/api/v1/afiliados')


def obtener_uow():
    """Factory para obtener UoW con repositorio de afiliados."""
    session = next(obtener_session_afiliados())
    repositorio = RepositorioAfiliadosSQLAlchemy(session)
    
    class UoWAfiliados(UnidadTrabajo):
        def __init__(self):
            super().__init__()
            self._repositorio_afiliados = repositorio
            self._session = session
        
        def commit(self):
            self._session.commit()
        
        def rollback(self):
            self._session.rollback()
    
    return UoWAfiliados()


@bp_afiliados.errorhandler(Exception)
def manejar_error(error):
    """Manejador global de errores para el módulo de afiliados"""
    if isinstance(error, ExcepcionDominio):
        return jsonify({
            "error": "Error de dominio",
            "mensaje": str(error),
            "tipo": type(error).__name__
        }), 400
    elif isinstance(error, ValueError):
        return jsonify({
            "error": "Error de validación",
            "mensaje": str(error)
        }), 400
    else:
        return jsonify({
            "error": "Error interno",
            "mensaje": "Ha ocurrido un error inesperado"
        }), 500


class AfiliadosAPI(MethodView):
    """API para operaciones CRUD de afiliados."""
    
    def post(self):
        """Crear un nuevo afiliado."""
        try:
            datos = request.get_json()
            
            # Validar datos requeridos
            campos_requeridos = [
                'nombres', 'apellidos', 'email', 'tipo_documento', 
                'numero_documento', 'tipo_afiliado', 'porcentaje_comision_base'
            ]
            
            for campo in campos_requeridos:
                if campo not in datos:
                    return jsonify({'error': f'Campo requerido: {campo}'}), 400
            
            # Convertir porcentaje a Decimal
            try:
                porcentaje_base = Decimal(str(datos['porcentaje_comision_base']))
                porcentaje_premium = None
                if 'porcentaje_comision_premium' in datos and datos['porcentaje_comision_premium']:
                    porcentaje_premium = Decimal(str(datos['porcentaje_comision_premium']))
                
                monto_minimo = None
                if 'monto_minimo_comision' in datos and datos['monto_minimo_comision']:
                    monto_minimo = Decimal(str(datos['monto_minimo_comision']))
                    
            except (InvalidOperation, ValueError):
                return jsonify({'error': 'Valores numéricos inválidos'}), 400
            
            # Parsear fecha de nacimiento si existe
            fecha_nacimiento = None
            if 'fecha_nacimiento' in datos and datos['fecha_nacimiento']:
                try:
                    fecha_nacimiento = datetime.fromisoformat(datos['fecha_nacimiento'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Formato de fecha_nacimiento inválido (ISO 8601)'}), 400
            
            # Crear comando
            comando = ComandoCrearAfiliado(
                nombres=datos['nombres'],
                apellidos=datos['apellidos'],
                fecha_nacimiento=fecha_nacimiento,
                tipo_documento=datos['tipo_documento'],
                numero_documento=datos['numero_documento'],
                email=datos['email'],
                telefono=datos.get('telefono'),
                direccion=datos.get('direccion'),
                ciudad=datos.get('ciudad'),
                pais=datos.get('pais'),
                tipo_afiliado=datos['tipo_afiliado'],
                porcentaje_comision_base=porcentaje_base,
                porcentaje_comision_premium=porcentaje_premium,
                monto_minimo_comision=monto_minimo,
                afiliado_referente_id=datos.get('afiliado_referente_id'),
                metadata=datos.get('metadata'),
                correlation_id=str(uuid.uuid4())
            )
            
            # Ejecutar comando
            uow = obtener_uow()
            ejecutar_commando(comando, uow)
            
            # Obtener afiliado creado
            query = QueryObtenerAfiliadoPorDocumento(
                tipo_documento=datos['tipo_documento'],
                numero_documento=datos['numero_documento']
            )
            resultado = ejecutar_query(query, uow)
            
            return jsonify({
                'mensaje': 'Afiliado creado exitosamente',
                'afiliado': resultado
            }), 201
            
        except Exception as e:
            return manejar_error(e)
    
    def get(self, afiliado_id=None):
        """Obtener afiliado(s)."""
        try:
            uow = obtener_uow()
            
            if afiliado_id:
                # Obtener afiliado específico
                query = QueryObtenerAfiliado(afiliado_id=afiliado_id)
                resultado = ejecutar_query(query, uow)
                
                if not resultado:
                    return jsonify({'error': 'Afiliado no encontrado'}), 404
                
                return jsonify({'afiliado': resultado})
            
            else:
                # Buscar afiliados con filtros
                filtros = {}
                args = request.args
                
                if 'estado' in args:
                    filtros['estado'] = args['estado']
                if 'tipo_afiliado' in args:
                    filtros['tipo_afiliado'] = args['tipo_afiliado']
                if 'email_like' in args:
                    filtros['email_like'] = args['email_like']
                if 'nombres_like' in args:
                    filtros['nombres_like'] = args['nombres_like']
                
                # Paginación
                limite = min(int(args.get('limite', 50)), 100)  # Máximo 100
                offset = int(args.get('offset', 0))
                ordenar_por = args.get('ordenar_por', 'fecha_creacion')
                orden_desc = args.get('orden_desc', 'true').lower() == 'true'
                
                query = QueryBuscarAfiliados(
                    estado=filtros.get('estado'),
                    tipo_afiliado=filtros.get('tipo_afiliado'),
                    email_like=filtros.get('email_like'),
                    nombres_like=filtros.get('nombres_like'),
                    limite=limite,
                    offset=offset,
                    ordenar_por=ordenar_por,
                    orden_desc=orden_desc
                )
                
                resultado = ejecutar_query(query, uow)
                return jsonify(resultado)
                
        except Exception as e:
            return manejar_error(e)


class AfiliadoAPI(MethodView):
    """API para operaciones específicas de un afiliado."""
    
    def put(self, afiliado_id, accion):
        """Ejecutar acciones sobre un afiliado específico."""
        try:
            datos = request.get_json() or {}
            correlation_id = str(uuid.uuid4())
            uow = obtener_uow()
            
            if accion == 'activar':
                comando = ComandoActivarAfiliado(
                    afiliado_id=afiliado_id,
                    codigo_referencia=datos.get('codigo_referencia'),
                    correlation_id=correlation_id
                )
                
            elif accion == 'desactivar':
                comando = ComandoDesactivarAfiliado(
                    afiliado_id=afiliado_id,
                    motivo=datos.get('motivo'),
                    correlation_id=correlation_id
                )
                
            elif accion == 'suspender':
                comando = ComandoSuspenderAfiliado(
                    afiliado_id=afiliado_id,
                    motivo=datos.get('motivo', 'Suspensión administrativa'),
                    correlation_id=correlation_id
                )
                
            elif accion == 'bloquear':
                comando = ComandoBloquearAfiliado(
                    afiliado_id=afiliado_id,
                    motivo=datos.get('motivo', 'Bloqueo administrativo'),
                    correlation_id=correlation_id
                )
                
            elif accion == 'actualizar-datos-bancarios':
                campos_requeridos = ['banco', 'tipo_cuenta', 'numero_cuenta', 'titular_cuenta']
                for campo in campos_requeridos:
                    if campo not in datos:
                        return jsonify({'error': f'Campo requerido: {campo}'}), 400
                
                comando = ComandoActualizarDatosBancarios(
                    afiliado_id=afiliado_id,
                    banco=datos['banco'],
                    tipo_cuenta=datos['tipo_cuenta'],
                    numero_cuenta=datos['numero_cuenta'],
                    titular_cuenta=datos['titular_cuenta'],
                    correlation_id=correlation_id
                )
                
            elif accion == 'actualizar-comisiones':
                try:
                    kwargs = {'afiliado_id': afiliado_id, 'correlation_id': correlation_id}
                    
                    if 'porcentaje_comision_base' in datos:
                        kwargs['porcentaje_comision_base'] = Decimal(str(datos['porcentaje_comision_base']))
                    if 'porcentaje_comision_premium' in datos:
                        kwargs['porcentaje_comision_premium'] = Decimal(str(datos['porcentaje_comision_premium']))
                    if 'monto_minimo_comision' in datos:
                        kwargs['monto_minimo_comision'] = Decimal(str(datos['monto_minimo_comision']))
                    
                    comando = ComandoActualizarConfiguracionComisiones(**kwargs)
                    
                except (InvalidOperation, ValueError):
                    return jsonify({'error': 'Valores numéricos inválidos'}), 400
                
            else:
                return jsonify({'error': f'Acción no válida: {accion}'}), 400
            
            # Ejecutar comando
            ejecutar_commando(comando, uow)
            
            # Retornar afiliado actualizado
            query = QueryObtenerAfiliado(afiliado_id=afiliado_id)
            resultado = ejecutar_query(query, uow)
            
            return jsonify({
                'mensaje': f'Acción {accion} ejecutada exitosamente',
                'afiliado': resultado
            })
            
        except Exception as e:
            return manejar_error(e)


class ReferenciasAPI(MethodView):
    """API para manejo de referencias entre afiliados."""
    
    def post(self, afiliado_referente_id):
        """Agregar una nueva referencia."""
        try:
            datos = request.get_json()
            
            if 'afiliado_referido_id' not in datos:
                return jsonify({'error': 'Campo requerido: afiliado_referido_id'}), 400
            
            comando = ComandoAgregarReferencia(
                afiliado_referente_id=afiliado_referente_id,
                afiliado_referido_id=datos['afiliado_referido_id'],
                correlation_id=str(uuid.uuid4())
            )
            
            uow = obtener_uow()
            ejecutar_commando(comando, uow)
            
            return jsonify({'mensaje': 'Referencia agregada exitosamente'}), 201
            
        except Exception as e:
            return manejar_error(e)
    
    def get(self, afiliado_referente_id):
        """Obtener referidos activos de un afiliado."""
        try:
            query = QueryObtenerReferidosActivos(
                afiliado_referente_id=afiliado_referente_id
            )
            
            uow = obtener_uow()
            resultado = ejecutar_query(query, uow)
            
            return jsonify({
                'afiliado_referente_id': afiliado_referente_id,
                'referidos_activos': resultado
            })
            
        except Exception as e:
            return manejar_error(e)


class UtilsAPI(MethodView):
    """API para utilidades y validaciones."""
    
    def post(self, operacion):
        """Ejecutar operaciones de utilidad."""
        try:
            datos = request.get_json()
            uow = obtener_uow()
            
            if operacion == 'validar-documento':
                query = QueryValidarDisponibilidadDocumento(
                    tipo_documento=datos['tipo_documento'],
                    numero_documento=datos['numero_documento'],
                    excluir_afiliado_id=datos.get('excluir_afiliado_id')
                )
                resultado = ejecutar_query(query, uow)
                
            elif operacion == 'validar-email':
                query = QueryValidarDisponibilidadEmail(
                    email=datos['email'],
                    excluir_afiliado_id=datos.get('excluir_afiliado_id')
                )
                resultado = ejecutar_query(query, uow)
                
            elif operacion == 'calcular-comisiones':
                if 'afiliado_id' not in datos or 'monto_transaccion' not in datos:
                    return jsonify({'error': 'Campos requeridos: afiliado_id, monto_transaccion'}), 400
                
                query = QueryCalcularComisiones(
                    afiliado_id=datos['afiliado_id'],
                    monto_transaccion=str(datos['monto_transaccion']),
                    incluir_comision_referencia=datos.get('incluir_comision_referencia', True)
                )
                resultado = ejecutar_query(query, uow)
                
            else:
                return jsonify({'error': f'Operación no válida: {operacion}'}), 400
            
            return jsonify(resultado)
            
        except Exception as e:
            return manejar_error(e)


class EstadisticasAPI(MethodView):
    """API para estadísticas de afiliados."""
    
    def get(self):
        """Obtener estadísticas de afiliados."""
        try:
            args = request.args
            
            # Parsear fechas opcionales
            fecha_desde = None
            fecha_hasta = None
            
            if 'fecha_desde' in args:
                try:
                    fecha_desde = datetime.fromisoformat(args['fecha_desde'])
                except ValueError:
                    return jsonify({'error': 'Formato de fecha_desde inválido (ISO 8601)'}), 400
            
            if 'fecha_hasta' in args:
                try:
                    fecha_hasta = datetime.fromisoformat(args['fecha_hasta'])
                except ValueError:
                    return jsonify({'error': 'Formato de fecha_hasta inválido (ISO 8601)'}), 400
            
            query = QueryObtenerEstadisticasAfiliados(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta
            )
            
            uow = obtener_uow()
            resultado = ejecutar_query(query, uow)
            
            return jsonify(resultado)
            
        except Exception as e:
            return manejar_error(e)


class ReportesAPI(MethodView):
    """API para generación de reportes."""
    
    def get(self):
        """Generar reporte de afiliados."""
        try:
            args = request.args
            
            query = QueryObtenerReporteAfiliados(
                formato=args.get('formato', 'json'),
                incluir_estadisticas=args.get('incluir_estadisticas', 'true').lower() == 'true',
                incluir_referencias=args.get('incluir_referencias', 'true').lower() == 'true'
            )
            
            uow = obtener_uow()
            resultado = ejecutar_query(query, uow)
            
            return jsonify(resultado)
            
        except Exception as e:
            return manejar_error(e)


# Registro de rutas
afiliados_view = AfiliadosAPI.as_view('afiliados_api')
afiliado_view = AfiliadoAPI.as_view('afiliado_api')
referencias_view = ReferenciasAPI.as_view('referencias_api')
utils_view = UtilsAPI.as_view('utils_api')
estadisticas_view = EstadisticasAPI.as_view('estadisticas_api')
reportes_view = ReportesAPI.as_view('reportes_api')

# Rutas principales
bp_afiliados.add_url_rule('/', view_func=afiliados_view, methods=['GET', 'POST'])
bp_afiliados.add_url_rule('/<string:afiliado_id>', view_func=afiliados_view, methods=['GET'])

# Rutas de acciones específicas
bp_afiliados.add_url_rule('/<string:afiliado_id>/<string:accion>', view_func=afiliado_view, methods=['PUT'])

# Rutas de referencias
bp_afiliados.add_url_rule('/<string:afiliado_referente_id>/referencias', view_func=referencias_view, methods=['GET', 'POST'])

# Rutas de utilidades
bp_afiliados.add_url_rule('/utils/<string:operacion>', view_func=utils_view, methods=['POST'])

# Rutas de estadísticas y reportes
bp_afiliados.add_url_rule('/estadisticas', view_func=estadisticas_view, methods=['GET'])
bp_afiliados.add_url_rule('/reportes', view_func=reportes_view, methods=['GET'])


# Health check específico para afiliados
@bp_afiliados.route('/health', methods=['GET'])
def health_check():
    """Health check del microservicio de afiliados."""
    try:
        from ..infraestructura.db import afiliados_db_manager
        
        # Verificar conexión a BD
        db_status = afiliados_db_manager.verificar_conexion()
        
        # Info de conexión (sin credenciales)
        db_info = afiliados_db_manager.obtener_info_conexion()
        
        return jsonify({
            'microservicio': 'afiliados',
            'estado': 'ok' if db_status else 'degradado',
            'timestamp': datetime.now().isoformat(),
            'base_datos': {
                'disponible': db_status,
                'host': db_info['host'],
                'puerto': db_info['port'],
                'base_datos': db_info['database']
            },
            'version': '1.0.0'
        }), 200 if db_status else 503
        
    except Exception as e:
        return jsonify({
            'microservicio': 'afiliados',
            'estado': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500