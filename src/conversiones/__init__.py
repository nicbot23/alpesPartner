"""
Microservicio de Conversiones - AlpesPartner
===============================================

Microservicio independiente para gestión de conversiones de marketing.
Siguiendo el patrón de arquitectura de tutorial-8-sagas:

- FastAPI con APIs versionadas (v1)
- Consumidores asíncronos con asyncio
- Comunicación por eventos via Pulsar
- Base de datos independiente (puerto 3307)
- Health checks y observabilidad

Estructura:
- main.py: Aplicación FastAPI principal
- config/: Configuración de API y BD
- api/v1/: Endpoints REST versionados
- eventos.py: Definición de eventos
- comandos.py: Definición de comandos  
- consumidores.py: Consumidores asíncronos
- despachadores.py: Publishers de eventos
- utils.py: Utilidades del microservicio

Puerto: 8001
Base de datos: mysql-conversiones:3307
"""

__version__ = "1.0.0"
__author__ = "AlpesPartner Team"

from .main_simple import app

__all__ = ["app"]