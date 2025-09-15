"""
Repositorio del dominio Conversiones
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .agregados import Conversion


class RepositorioConversiones(ABC):
    """Contrato del repositorio para el agregado Conversion"""
    
    @abstractmethod
    def guardar(self, conversion: Conversion) -> None:
        """Persiste una conversión y sus eventos"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, conversion_id: str) -> Optional[Conversion]:
        """Obtiene conversión por ID"""
        pass
    
    @abstractmethod
    def obtener_por_transaction_id(self, transaction_id: str) -> Optional[Conversion]:
        """Obtiene conversión por transaction_id (único)"""
        pass
    
    @abstractmethod
    def listar_por_afiliado(self, affiliate_id: str, limite: int = 100) -> List[Conversion]:
        """Lista conversiones de un afiliado"""
        pass
    
    @abstractmethod
    def listar_por_campana(self, campaign_id: str, limite: int = 100) -> List[Conversion]:
        """Lista conversiones de una campaña"""
        pass
    
    @abstractmethod
    def listar_pendientes(self, limite: int = 100) -> List[Conversion]:
        """Lista conversiones pendientes de validación"""
        pass
    
    @abstractmethod
    def contar_por_estado(self, estado: str) -> int:
        """Cuenta conversiones por estado"""
        pass