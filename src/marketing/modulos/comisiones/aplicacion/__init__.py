"""
Capa de Aplicación del módulo de comisiones - Marketing Microservice  
Implementa casos de uso, CQRS y coordinación entre dominio e infraestructura
Arquitectura: Application Layer + CQRS + Use Cases
"""

# Re-export para facilitar importaciones
from .comandos import *
from .consultas import *
from .handlers import *
from .servicios import *