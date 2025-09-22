from campanias.seedwork.dominio.fabricas import Fabrica
from campanias.seedwork.dominio.repositorios import Repositorio
from campanias.modulos.dominio.entidades import Campaña
from campanias.modulos.aplicacion.dto import CampañaDTO
from campanias.modulos.aplicacion.mapeadores import MapeadorCampania

class FabricaRepositorios(Fabrica):
    """Fábrica para crear repositorios siguiendo el patrón AeroAlpes"""
    
    def crear_objeto(self, obj: type, mapeador: any = None) -> Repositorio:
        if obj == 'RepositorioCampanias':
            from campanias.modulos.infraestructura.repositorios import RepositorioCampanias
            return RepositorioCampanias()
        elif obj == 'RepositorioEventosCampanias':
            from campanias.modulos.infraestructura.repositorios import RepositorioEventosCampanias  
            return RepositorioEventosCampanias()
        else:
            raise Exception(f'No existe fábrica para el objeto {obj}')

class FabricaCampanias(Fabrica):
    """Fábrica para crear entidades Campaña siguiendo el patrón AeroAlpes"""
    
    def crear_objeto(self, obj: any, mapeador: any = None) -> Campaña:
        if isinstance(obj, CampañaDTO):
            return mapeador.dto_a_entidad(obj)
        else:
            raise Exception(f'No existe fábrica para el objeto {obj}')