"""Contratos de repositorio para Campañas"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from .agregados import Campana


class RepositorioCampanas(ABC):
    """Puerto de salida principal para persistencia del agregado Campana"""

    @abstractmethod
    def guardar(self, campana: Campana) -> str: ...

    @abstractmethod
    def obtener_por_id(self, campana_id: str) -> Optional[Campana]: ...

    @abstractmethod
    def listar_activas(self, limite: int, offset: int) -> List[Campana]: ...

    @abstractmethod
    def existe_campana_activa_para_marca(self, marca: str) -> bool: ...
"""
Repositorio de Dominio para Campañas
Interface que define el contrato para persistencia de agregados Campaña
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..dominio.agregados import Campana


class RepositorioCampanas(ABC):
    """
    Repositorio abstracto para el agregado Campaña
    Define las operaciones de persistencia necesarias para el dominio
    """
    
    @abstractmethod
    def obtener_por_id(self, campana_id: str) -> Optional[Campana]:
        """
        Obtiene una campaña por su identificador único
        """
        ...
    
    @abstractmethod
    def guardar(self, campana: Campana) -> None:
        """
        Persiste una campaña (crear o actualizar)
        """
        ...
    
    @abstractmethod
    def eliminar(self, campana_id: str) -> None:
        """
        Elimina una campaña del repositorio
        """
        ...
    
    @abstractmethod
    def listar_activas(self, limite: int = 10, offset: int = 0) -> List[Campana]:
        """
        Lista todas las campañas en estado ACTIVA
        """
        ...
    
    @abstractmethod
    def buscar_por_marca(self, marca: str) -> List[Campana]:
        """
        Busca campañas por marca específica
        """
        ...
    
    @abstractmethod
    def existe_campana_activa_para_marca(self, marca: str) -> bool:
        """
        Verifica si existe al menos una campaña activa para una marca
        Útil para validaciones de dominio
        """
        ...
