"""
Manejadores de Comandos para el Bounded Context Campañas
Implementa la lógica de aplicación usando casos de uso
"""

from typing import Optional
from alpespartner.seedwork.aplicacion.handlers import ManejadorComando
from alpespartner.seedwork.infraestructura.uow import UnidadTrabajo
from ..dominio.agregados import Campana, EstadoCampana
from ..dominio.repositorios import RepositorioCampanas
from ..dominio.objetos_valor import (
    MetadatosCampana, PeriodoVigencia, 
    TerminosComision, RestriccionGeografica
)
from .comandos import (
    CrearCampana, ActivarCampana, PausarCampana, 
    ModificarTerminosCampana, ConsultarCampana, ListarCampanasActivas
)


class ManejadorCrearCampana(ManejadorComando):
    """
    Maneja la creación de nuevas campañas
    """
    
    def __init__(self, repositorio: RepositorioCampanas, uow: UnidadTrabajo):
        self.repositorio = repositorio
        self.uow = uow
    
    def manejar(self, comando: CrearCampana) -> str:
        """
        Ejecuta la creación de una campaña aplicando reglas de negocio
        """
        
        # Construir objetos valor desde el comando
        metadatos = MetadatosCampana(
            nombre=comando.nombre,
            descripcion=comando.descripcion,
            marca=comando.marca,
            categoria=comando.categoria,
            tags=comando.tags
        )
        
        periodo = PeriodoVigencia(
            inicio=comando.fecha_inicio,
            fin=comando.fecha_fin
        )
        
        terminos = TerminosComision(
            porcentaje_base=comando.porcentaje_base,
            porcentaje_premium=comando.porcentaje_premium,
            umbral_premium=comando.umbral_premium,
            moneda=comando.moneda
        )
        
        restricciones = RestriccionGeografica(
            paises_permitidos=comando.paises_permitidos,
            regiones_excluidas=comando.regiones_excluidas
        )
        
        # Reglas de negocio de aplicación
        if self.repositorio.existe_campana_activa_para_marca(comando.marca):
            raise ValueError(f"Ya existe una campaña activa para la marca {comando.marca}")
        
        # Crear el agregado usando factory method de dominio
        campana = Campana.crear(
            metadatos=metadatos,
            periodo=periodo,
            terminos=terminos,
            restricciones=restricciones
        )
        
        # Persistir usando UoW para manejar eventos CDC
        with self.uow:
            self.repositorio.guardar(campana)
            self.uow.commit()
        
        return campana.id


class ManejadorActivarCampana(ManejadorComando):
    """
    Maneja la activación de campañas
    """
    
    def __init__(self, repositorio: RepositorioCampanas, uow: UnidadTrabajo):
        self.repositorio = repositorio
        self.uow = uow
    
    def manejar(self, comando: ActivarCampana) -> None:
        """
        Activa una campaña aplicando reglas de dominio
        """
        campana = self.repositorio.obtener_por_id(comando.campana_id)
        
        if not campana:
            raise ValueError(f"Campaña {comando.campana_id} no encontrada")
        
        # La lógica de activación está en el agregado (DDD)
        campana.activar()
        
        # Persistir cambios
        with self.uow:
            self.repositorio.guardar(campana)
            self.uow.commit()


class ManejadorPausarCampana(ManejadorComando):
    """
    Maneja la pausa de campañas activas
    """
    
    def __init__(self, repositorio: RepositorioCampanas, uow: UnidadTrabajo):
        self.repositorio = repositorio
        self.uow = uow
    
    def manejar(self, comando: PausarCampana) -> None:
        """
        Pausa una campaña activa
        """
        campana = self.repositorio.obtener_por_id(comando.campana_id)
        
        if not campana:
            raise ValueError(f"Campaña {comando.campana_id} no encontrada")
        
        # La lógica de pausa está en el agregado
        campana.pausar(comando.motivo)
        
        # Persistir cambios
        with self.uow:
            self.repositorio.guardar(campana)
            self.uow.commit()


class ManejadorModificarTerminos(ManejadorComando):
    """
    Maneja la modificación de términos de comisión
    """
    
    def __init__(self, repositorio: RepositorioCampanas, uow: UnidadTrabajo):
        self.repositorio = repositorio
        self.uow = uow
    
    def manejar(self, comando: ModificarTerminosCampana) -> None:
        """
        Modifica términos de comisión de una campaña
        """
        campana = self.repositorio.obtener_por_id(comando.campana_id)
        
        if not campana:
            raise ValueError(f"Campaña {comando.campana_id} no encontrada")
        
        # Crear nuevos términos
        nuevos_terminos = TerminosComision(
            porcentaje_base=comando.porcentaje_base,
            porcentaje_premium=comando.porcentaje_premium,
            umbral_premium=comando.umbral_premium,
            moneda=campana.terminos_comision.moneda  # Mantener moneda original
        )
        
        # La lógica de modificación está en el agregado
        campana.modificar_terminos(nuevos_terminos)
        
        # Persistir cambios
        with self.uow:
            self.repositorio.guardar(campana)
            self.uow.commit()


class ManejadorConsultarCampana(ManejadorComando):
    """
    Maneja consultas de campaña individual
    """
    
    def __init__(self, repositorio: RepositorioCampanas):
        self.repositorio = repositorio
    
    def manejar(self, comando: ConsultarCampana) -> Optional[Campana]:
        """
        Consulta una campaña por ID
        """
        return self.repositorio.obtener_por_id(comando.campana_id)


class ManejadorListarCampanasActivas(ManejadorComando):
    """
    Maneja listado de campañas activas
    """
    
    def __init__(self, repositorio: RepositorioCampanas):
        self.repositorio = repositorio
    
    def manejar(self, comando: ListarCampanasActivas) -> list[Campana]:
        """
        Lista campañas activas con paginación
        """
        return self.repositorio.listar_activas(comando.limite, comando.offset)
