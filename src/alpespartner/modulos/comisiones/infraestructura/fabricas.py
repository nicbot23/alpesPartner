"""Fábricas para la creación de repositorios en la capa de infraestructura de comisiones

En este archivo usted encontrará las diferentes fábricas para crear
repositorios en la capa de infraestructura del dominio de comisiones

"""

from dataclasses import dataclass
from sqlalchemy.orm import Session
from alpespartner.seedwork.dominio.fabricas import Fabrica
from alpespartner.seedwork.dominio.repositorios.base import Repositorio
from alpespartner.modulos.comisiones.dominio.repositorios.repositorios import RepositorioComisiones
from alpespartner.modulos.comisiones.dominio.repositorios.repositorios_eventos import RepositorioEventosComision
from .repositorios_sqlalchemy import RepoComisionesSQLAlchemy
from .repositorios_eventos import RepositorioEventosComisionSQLAlchemy
from .excepciones import ExcepcionFabrica

@dataclass
class FabricaRepositorio(Fabrica):
    def crear_objeto(self, obj: type, session: Session = None) -> Repositorio:
        if obj == RepositorioComisiones:
            return RepoComisionesSQLAlchemy(session)
        elif obj == RepositorioEventosComision:
            return RepositorioEventosComisionSQLAlchemy(session)
        else:
            raise ExcepcionFabrica(f'No existe fábrica para el objeto {obj}')

@dataclass  
class FabricaComisiones(Fabrica):
    def crear_objeto(self, obj: any, mapeador: any = None) -> any:
        if mapeador:
            return mapeador.entidad_a_dto(obj)
        return obj
