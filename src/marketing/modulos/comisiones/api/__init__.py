"""
API del módulo de comisiones - Marketing Microservice
Arquitectura: FastAPI + OpenAPI + Dependency Injection + Error Handling
"""

from .router import router

__all__ = ['router']