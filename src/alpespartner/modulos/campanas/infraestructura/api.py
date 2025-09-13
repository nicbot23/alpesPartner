"""
API REST para el Bounded Context Campañas
Implementa endpoints siguiendo principios REST y DDD
"""

from flask import Blueprint, request, jsonify
from flask.views import MethodView
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

# Importaciones de aplicación y dominio
from ..aplicacion.comandos import (
    CrearCampana, ActivarCampana, PausarCampana,
    ModificarTerminosCampana, ConsultarCampana, ListarCampanasActivas
)
from ..aplicacion.manejadores import (
    ManejadorCrearCampana, ManejadorActivarCampana, ManejadorPausarCampana,
    ManejadorModificarTerminos, ManejadorConsultarCampana, ManejadorListarCampanasActivas
)
from ..infraestructura.repositorios import RepositorioCampanasMySQL
from ..dominio.agregados import Campana

# Configuración del blueprint
bp_campanas = Blueprint('campanas', __name__, url_prefix='/api/v1/campanas')


class CampanaAPI(MethodView):
    """
    API RESTful para gestión de campañas
    """
    
    def __init__(self):
        # TODO: Inyección de dependencias más elegante con DI container
        from alpespartner.config.db import get_db_session
        self.session = get_db_session()
        self.repositorio = RepositorioCampanasMySQL(self.session)
    
    def post(self):
        """
        POST /api/v1/campanas
        Crear nueva campaña
        """
        try:
            data = request.get_json()
            
            # Validar datos requeridos
            campos_requeridos = [
                'nombre', 'descripcion', 'marca', 'categoria',
                'fecha_inicio', 'fecha_fin', 'porcentaje_base',
                'porcentaje_premium', 'umbral_premium', 'moneda',
                'paises_permitidos'
            ]
            
            for campo in campos_requeridos:
                if campo not in data:
                    return jsonify({'error': f'Campo requerido: {campo}'}), 400
            
            # Convertir strings a datetime
            fecha_inicio = datetime.fromisoformat(data['fecha_inicio'].replace('Z', '+00:00'))
            fecha_fin = datetime.fromisoformat(data['fecha_fin'].replace('Z', '+00:00'))
            
            # Crear comando
            comando = CrearCampana(
                nombre=data['nombre'],
                descripcion=data['descripcion'],
                marca=data['marca'],
                categoria=data['categoria'],
                tags=data.get('tags', []),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                porcentaje_base=Decimal(str(data['porcentaje_base'])),
                porcentaje_premium=Decimal(str(data['porcentaje_premium'])),
                umbral_premium=Decimal(str(data['umbral_premium'])),
                moneda=data['moneda'],
                paises_permitidos=data['paises_permitidos'],
                regiones_excluidas=data.get('regiones_excluidas', [])
            )
            
            # Ejecutar comando
            from alpespartner.config.uow import UnidadTrabajoSQLAlchemy
            with UnidadTrabajoSQLAlchemy() as uow:
                manejador = ManejadorCrearCampana(self.repositorio, uow)
                campana_id = manejador.manejar(comando)
            
            return jsonify({
                'campana_id': campana_id,
                'mensaje': 'Campaña creada exitosamente'
            }), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get(self, campana_id=None):
        """
        GET /api/v1/campanas/{id} - Obtener campaña específica
        GET /api/v1/campanas - Listar campañas activas
        """
        try:
            if campana_id:
                # Consultar campaña específica
                comando = ConsultarCampana(campana_id=campana_id)
                manejador = ManejadorConsultarCampana(self.repositorio)
                campana = manejador.manejar(comando)
                
                if not campana:
                    return jsonify({'error': 'Campaña no encontrada'}), 404
                
                return jsonify(self._campana_a_dict(campana)), 200
            
            else:
                # Listar campañas activas
                limite = int(request.args.get('limite', 10))
                offset = int(request.args.get('offset', 0))
                
                comando = ListarCampanasActivas(limite=limite, offset=offset)
                manejador = ManejadorListarCampanasActivas(self.repositorio)
                campanas = manejador.manejar(comando)
                
                return jsonify({
                    'campanas': [self._campana_a_dict(c) for c in campanas],
                    'total': len(campanas),
                    'limite': limite,
                    'offset': offset
                }), 200
                
        except Exception as e:
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def _campana_a_dict(self, campana: Campana) -> Dict[str, Any]:
        """
        Convierte un agregado Campaña a diccionario para JSON
        """
        return {
            'id': campana.id,
            'metadatos': {
                'nombre': campana.metadatos.nombre,
                'descripcion': campana.metadatos.descripcion,
                'marca': campana.metadatos.marca,
                'categoria': campana.metadatos.categoria,
                'tags': campana.metadatos.tags
            },
            'periodo': {
                'fecha_inicio': campana.periodo_vigencia.inicio.isoformat(),
                'fecha_fin': campana.periodo_vigencia.fin.isoformat(),
                'esta_vigente': campana.periodo_vigencia.esta_vigente(),
                'dias_restantes': campana.periodo_vigencia.dias_restantes()
            },
            'terminos_comision': {
                'porcentaje_base': float(campana.terminos_comision.porcentaje_base),
                'porcentaje_premium': float(campana.terminos_comision.porcentaje_premium),
                'umbral_premium': float(campana.terminos_comision.umbral_premium),
                'moneda': campana.terminos_comision.moneda
            },
            'restricciones': {
                'paises_permitidos': campana.restriccion_geografica.paises_permitidos,
                'regiones_excluidas': campana.restriccion_geografica.regiones_excluidas
            },
            'estado': campana.estado.value,
            'timestamps': {
                'creada_en': campana.creada_en.isoformat(),
                'activada_en': campana.activada_en.isoformat() if campana.activada_en else None,
                'finalizada_en': campana.finalizada_en.isoformat() if campana.finalizada_en else None
            }
        }


class CampanaAccionesAPI(MethodView):
    """
    API para acciones específicas de campañas
    """
    
    def __init__(self):
        from alpespartner.config.db import get_db_session
        self.session = get_db_session()
        self.repositorio = RepositorioCampanasMySQL(self.session)
    
    def post(self, campana_id, accion):
        """
        POST /api/v1/campanas/{id}/activar
        POST /api/v1/campanas/{id}/pausar
        POST /api/v1/campanas/{id}/modificar-terminos
        """
        try:
            from alpespartner.config.uow import UnidadTrabajoSQLAlchemy
            
            if accion == 'activar':
                comando = ActivarCampana(campana_id=campana_id)
                with UnidadTrabajoSQLAlchemy() as uow:
                    manejador = ManejadorActivarCampana(self.repositorio, uow)
                    manejador.manejar(comando)
                
                return jsonify({'mensaje': 'Campaña activada exitosamente'}), 200
            
            elif accion == 'pausar':
                data = request.get_json()
                motivo = data.get('motivo', 'Pausada manualmente')
                
                comando = PausarCampana(campana_id=campana_id, motivo=motivo)
                with UnidadTrabajoSQLAlchemy() as uow:
                    manejador = ManejadorPausarCampana(self.repositorio, uow)
                    manejador.manejar(comando)
                
                return jsonify({'mensaje': 'Campaña pausada exitosamente'}), 200
            
            elif accion == 'modificar-terminos':
                data = request.get_json()
                
                campos_requeridos = ['porcentaje_base', 'porcentaje_premium', 'umbral_premium']
                for campo in campos_requeridos:
                    if campo not in data:
                        return jsonify({'error': f'Campo requerido: {campo}'}), 400
                
                comando = ModificarTerminosCampana(
                    campana_id=campana_id,
                    porcentaje_base=Decimal(str(data['porcentaje_base'])),
                    porcentaje_premium=Decimal(str(data['porcentaje_premium'])),
                    umbral_premium=Decimal(str(data['umbral_premium'])),
                    motivo=data.get('motivo', 'Modificación de términos')
                )
                
                with UnidadTrabajoSQLAlchemy() as uow:
                    manejador = ManejadorModificarTerminos(self.repositorio, uow)
                    manejador.manejar(comando)
                
                return jsonify({'mensaje': 'Términos modificados exitosamente'}), 200
            
            else:
                return jsonify({'error': f'Acción no válida: {accion}'}), 400
                
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def _campana_a_dict(self, campana: Campana) -> Dict[str, Any]:
        """
        Convierte un agregado Campaña a diccionario para JSON
        """
        return {
            'id': campana.id,
            'metadatos': {
                'nombre': campana.metadatos.nombre,
                'descripcion': campana.metadatos.descripcion,
                'marca': campana.metadatos.marca,
                'categoria': campana.metadatos.categoria,
                'tags': campana.metadatos.tags
            },
            'periodo': {
                'fecha_inicio': campana.periodo_vigencia.inicio.isoformat(),
                'fecha_fin': campana.periodo_vigencia.fin.isoformat(),
                'esta_vigente': campana.periodo_vigencia.esta_vigente(),
                'dias_restantes': campana.periodo_vigencia.dias_restantes()
            },
            'terminos_comision': {
                'porcentaje_base': float(campana.terminos_comision.porcentaje_base),
                'porcentaje_premium': float(campana.terminos_comision.porcentaje_premium),
                'umbral_premium': float(campana.terminos_comision.umbral_premium),
                'moneda': campana.terminos_comision.moneda
            },
            'restricciones': {
                'paises_permitidos': campana.restriccion_geografica.paises_permitidos,
                'regiones_excluidas': campana.restriccion_geografica.regiones_excluidas
            },
            'estado': campana.estado.value,
            'timestamps': {
                'creada_en': campana.creada_en.isoformat(),
                'activada_en': campana.activada_en.isoformat() if campana.activada_en else None,
                'finalizada_en': campana.finalizada_en.isoformat() if campana.finalizada_en else None
            }
        }


# Registrar las vistas
campana_view = CampanaAPI.as_view('campana_api')
acciones_view = CampanaAccionesAPI.as_view('campana_acciones_api')

# Rutas
bp_campanas.add_url_rule('/', defaults={'campana_id': None}, view_func=campana_view, methods=['GET', 'POST'])
bp_campanas.add_url_rule('/<string:campana_id>', view_func=campana_view, methods=['GET'])
bp_campanas.add_url_rule('/<string:campana_id>/<string:accion>', view_func=acciones_view, methods=['POST'])


@bp_campanas.route('/health')
def health():
    """Endpoint de salud del módulo campañas"""
    return jsonify({
        'status': 'ok',
        'bounded_context': 'campanas',
        'version': '1.0.0'
    })
