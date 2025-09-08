from abc import ABC, abstractmethod
from aeroalpes.modulos.comisiones.dominio.agregados import Comision

class RepositorioComisiones(ABC):
    
    @abstractmethod
    def agregar(self, comision:Comision)->str: 
        ...
    
    @abstractmethod
    def aprobar(self, commission_id:str)->None: 
        ...
    
    @abstractmethod
    def obtener_por_conversion(self, conversion_id:str)->dict|None: 
        ...
