"""
Módulo completo de comisiones - Marketing Microservice
Bounded Context: Comisiones como coordinador central del ecosistema
Arquitectura: DDD + CQRS + Event-Driven + Enterprise Patterns
"""

# APIs - Router principal
from .api.router import router

# Facade del módulo para integración simplificada
class FacadeModuloComisiones:
    """
    Facade principal del módulo de comisiones
    Proporciona una interfaz simplificada para el bounded context completo
    """
    
    def __init__(self):
        self.router = router
    
    def obtener_router_api(self):
        """Obtener router de APIs REST"""
        return self.router

# Instancia singleton del facade para uso en la aplicación
facade_comisiones = FacadeModuloComisiones()

__all__ = [
    'FacadeModuloComisiones',
    'facade_comisiones', 
    'router'
]