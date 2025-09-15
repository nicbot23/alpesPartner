"""
Contratos de repositorio para el dominio de Afiliados
Define las operaciones de persistencia sin detalles de implementación
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .agregados import Afiliado


class RepositorioAfiliados(ABC):
    """Contrato del repositorio de afiliados."""
    
    @abstractmethod
    def guardar(self, afiliado: Afiliado) -> None:
        """Guarda un afiliado en el repositorio."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, afiliado_id: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su email."""
        pass
    
    @abstractmethod
    def obtener_por_documento(self, tipo_documento: str, numero_documento: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su documento de identidad."""
        pass
    
    @abstractmethod
    def obtener_por_codigo_referencia(self, codigo: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su código de referencia."""
        pass
    
    @abstractmethod
    def listar_por_estado(self, estado: str, limite: int = 100) -> List[Afiliado]:
        """Lista afiliados por estado."""
        pass
    
    @abstractmethod
    def listar_por_tipo(self, tipo_afiliado: str, limite: int = 100) -> List[Afiliado]:
        """Lista afiliados por tipo."""
        pass
    
    @abstractmethod
    def listar_referencias_de_afiliado(self, afiliado_id: str) -> List[Afiliado]:
        """Lista los afiliados referidos por un afiliado específico."""
        pass
    
    @abstractmethod
    def buscar_con_filtros(self, filtros: Dict[str, Any], page: int = 1, size: int = 20) -> List[Afiliado]:
        """Busca afiliados aplicando filtros con paginación."""
        pass
    
    @abstractmethod
    def contar_con_filtros(self, filtros: Dict[str, Any]) -> int:
        """Cuenta afiliados que coinciden con los filtros."""
        pass
    
    @abstractmethod
    def obtener_estadisticas(self, fecha_desde=None, fecha_hasta=None, agrupado_por='estado') -> Dict[str, Any]:
        """Obtiene estadísticas de afiliados."""
        pass
    
    @abstractmethod
    def obtener_eventos_pendientes(self, limite: int = 100) -> List[Any]:
        """Obtiene eventos del outbox pendientes de publicar."""
        pass
    
    @abstractmethod
    def marcar_eventos_como_publicados(self, event_ids: List[str]) -> int:
        """Marca eventos como publicados en el outbox."""
        pass