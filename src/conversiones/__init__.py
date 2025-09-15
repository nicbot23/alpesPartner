"""
Microservicio de Conversiones - AlpesPartner
===============================================

Microservicio independiente para gestión de conversiones de marketing.
Siguiendo el patrón de arquitectura con eventos:

- FastAPI con APIs versionadas (v1)
- Comunicación por eventos via Pulsar
- Base de datos independiente (puerto 3307)
- Health checks y observabilidad

Estructura:
- main_eventos.py: Aplicación FastAPI principal con eventos
- config/: Configuración de API y BD
- api/v1/: Endpoints REST versionados
- eventos.py: Definición de eventos
- comandos.py: Definición de comandos  
- consumidores.py: Consumidores asíncronos
- despachadores.py: Publishers de eventos
- utils.py: Utilidades del microservicio

Puerto: 8002
Base de datos: mysql-conversiones:3307
"""

__version__ = "1.0.0"
__author__ = "AlpesPartner Team"

from .main_eventos import app

__all__ = ["app"]