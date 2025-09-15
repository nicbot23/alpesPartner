"""
Infraestructura del módulo de comisiones - Marketing Microservice
Implementa persistencia, comunicación y servicios técnicos enterprise
Arquitectura: Repository + Unit of Work + Event Sourcing + Messaging
"""

# Re-export para facilitar importaciones
from .repositorios import *
from .despachadores import *
from .configuracion import *