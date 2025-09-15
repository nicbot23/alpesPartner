"""
Aplicación Flask para el microservicio Conversiones.
Microservicio descentralizado con base de datos propia.
"""

import os
import logging
from flask import Flask
from dotenv import load_dotenv

from alpespartner.modulos.conversiones.api import bp_conversiones
from alpespartner.modulos.conversiones.infraestructura.db import init_db


# Cargar variables de entorno específicas de Conversiones
load_dotenv('.env.conversiones')

# Configurar logging
logging.basicConfig(
    level=os.getenv('CONVERSIONES_LOG_LEVEL', 'INFO'),
    format=os.getenv('CONVERSIONES_LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Factory para crear la aplicación Flask del microservicio Conversiones."""
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SERVICE_NAME'] = os.getenv('CONVERSIONES_SERVICE_NAME', 'conversiones')
    app.config['SERVICE_VERSION'] = os.getenv('CONVERSIONES_SERVICE_VERSION', '1.0.0')
    
    # Headers CORS básicos
    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Correlation-ID, X-Causation-ID'
        return response
    
    # Registrar blueprints
    app.register_blueprint(bp_conversiones)
    
    # Inicializar base de datos
    init_db()
    
    # Health check básico
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'service': app.config['SERVICE_NAME'],
            'version': app.config['SERVICE_VERSION']
        }
    
    # Endpoint de información del servicio
    @app.route('/info')
    def info():
        return {
            'service': app.config['SERVICE_NAME'],
            'version': app.config['SERVICE_VERSION'],
            'description': 'Microservicio descentralizado para gestión de conversiones',
            'database': 'MySQL separada (puerto 3307)',
            'outbox': 'Descentralizado con eventos propios',
            'endpoints': {
                'health': '/health',
                'conversiones': '/api/v1/conversiones'
            }
        }
    
    logger.info(f"Microservicio {app.config['SERVICE_NAME']} v{app.config['SERVICE_VERSION']} iniciado")
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('CONVERSIONES_PORT', 5001))
    debug = os.getenv('CONVERSIONES_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)