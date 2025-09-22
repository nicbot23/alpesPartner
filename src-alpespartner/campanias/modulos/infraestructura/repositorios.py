from abc import ABC
from campanias.seedwork.dominio.repositorios import Repositorio
from campanias.modulos.dominio.entidades import Campaña
from campanias.modulos.dominio.eventos import EventoDominioCampania
from typing import List, Optional

class RepositorioCampanias(Repositorio, ABC):
    """Repositorio para gestionar campanias"""
    
    def obtener_por_id(self, id: str) -> Optional[Campaña]:
        """Obtiene una campaña por su ID"""
        raise NotImplementedError()
    
    def obtener_todos(self) -> List[Campaña]:
        """Obtiene todas las campanias"""
        raise NotImplementedError()
    
    def agregar(self, campania: Campaña):
        """Agrega una nueva campaña"""
        raise NotImplementedError()
    
    def actualizar(self, campania: Campaña):
        """Actualiza una campaña existente"""
        raise NotImplementedError()
    
    def eliminar(self, id: str):
        """Elimina una campaña por su ID"""
        raise NotImplementedError()

class RepositorioEventosCampanias(Repositorio, ABC):
    """Repositorio para gestionar eventos de dominio de campanias"""
    
    def obtener_por_id(self, id: str) -> Optional[EventoDominioCampania]:
        """Obtiene un evento por su ID"""
        raise NotImplementedError()
    
    def obtener_todos(self) -> List[EventoDominioCampania]:
        """Obtiene todos los eventos"""
        raise NotImplementedError()
    
    def agregar(self, evento: EventoDominioCampania):
        """Agrega un nuevo evento de dominio"""
        raise NotImplementedError()
    
    def actualizar(self, evento: EventoDominioCampania):
        """Actualiza un evento existente"""
        raise NotImplementedError()
    
    def eliminar(self, id: str):
        """Elimina un evento por su ID"""
        raise NotImplementedError()

# Alias para compatibilidad con el código anterior
Repositoriocampanias = RepositorioCampanias