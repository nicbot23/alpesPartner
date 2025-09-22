from campanias.seedwork.aplicacion.comandos import Comando, ComandoHandler
from campanias.modulos.aplicacion.dto import CampañaDTO
from .base import CrearCampaniaBaseHandler
from dataclasses import dataclass, field
from campanias.seedwork.aplicacion.comandos import ejecutar_commando as comando

from campanias.modulos.dominio.entidades import Campaña
from campanias.seedwork.infraestructura.uow import UnidadTrabajoPuerto, UnidadTrabajo
from campanias.modulos.aplicacion.mapeadores import MapeadorCampania
from campanias.modulos.infraestructura.repositorios import RepositorioCampanias, RepositorioEventosCampanias
from campanias.modulos.aplicacion.mapeadores import MapeadorCampania
from campanias.modulos.infraestructura.repositorios import RepositorioCampanias, RepositorioEventosCampanias
from datetime import datetime

@dataclass
class CrearCampana(Comando):
    fecha_creacion: str
    fecha_actualizacion: str
    id: str
    nombre: str
    descripcion: str
    tipo_campana: str
    canal_publicidad: str
    objetivo_campana: str
    fecha_inicio: str
    fecha_fin: str
    presupuesto: float = 0.0
    moneda: str = "USD"
    codigo_campana: str = None
    segmento_audiencia: str = None

@dataclass
class ActivarCampana(Comando):
    id_campania: str
    fecha_activacion: str

@dataclass
class AgregarAfiliadoACampana(Comando):
    id_campania: str
    id_afiliado: str
    fecha_asignacion: str
    configuracion_afiliado: dict = None
    comision_aplicable: float = 0.0

class CrearCampaniaHandler(CrearCampaniaBaseHandler):
    
    def handle(self, comando: CrearCampana):
        campania_dto = CampañaDTO(
            fecha_actualizacion=comando.fecha_actualizacion,
            fecha_creacion=comando.fecha_creacion,
            id=comando.id,
            nombre=comando.nombre,
            descripcion=comando.descripcion,
            tipo=comando.tipo_campana,
            canal_publicidad=comando.canal_publicidad,
            objetivo=comando.objetivo_campana,
            fecha_inicio=comando.fecha_inicio,
            fecha_fin=comando.fecha_fin,
            presupuesto=comando.presupuesto,
            moneda=comando.moneda,
            codigo_campana=comando.codigo_campana,
            segmento_audiencia=comando.segmento_audiencia
        )

        campania: Campaña = self.fabrica_campanias.crear_objeto(campania_dto, MapeadorCampania())
        campania.crear_campania(campania)

        repositorio = self.fabrica_repositorio.crear_objeto('RepositorioCampanias')
        repositorio_eventos = self.fabrica_repositorio.crear_objeto('RepositorioEventosCampanias')

        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, campania, repositorio_eventos_func=repositorio_eventos.agregar)
        UnidadTrabajoPuerto.commit()

class ActivarCampaniaHandler(CrearCampaniaBaseHandler):
    
    def handle(self, comando: ActivarCampana):
        repositorio = self.fabrica_repositorio.crear_objeto('RepositorioCampanias')
        repositorio_eventos = self.fabrica_repositorio.crear_objeto('RepositorioEventosCampanias')
        
        campania = repositorio.obtener_por_id(comando.id_campania)
        if not campania:
            raise Exception(f"Campaña {comando.id_campania} no encontrada")
        
        campania.activar_campania()

        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, campania, repositorio_eventos_func=repositorio_eventos.agregar)
        UnidadTrabajoPuerto.commit()

class AgregarAfiliadoACampaniaHandler(CrearCampaniaBaseHandler):
    
    def handle(self, comando: AgregarAfiliadoACampana):
        repositorio = self.fabrica_repositorio.crear_objeto('RepositorioCampanias')
        repositorio_eventos = self.fabrica_repositorio.crear_objeto('RepositorioEventosCampanias')
        
        campania = repositorio.obtener_por_id(comando.id_campania)
        if not campania:
            raise Exception(f"Campaña {comando.id_campania} no encontrada")
        
        campania.agregar_afiliado(
            comando.id_afiliado,
            comando.configuracion_afiliado,
            comando.comision_aplicable
        )

        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, campania, repositorio_eventos_func=repositorio_eventos.agregar)
        UnidadTrabajoPuerto.commit()

@comando.register(CrearCampana)
def ejecutar_comando_crear_campania(comando: CrearCampana):
    handler = CrearCampaniaHandler()
    handler.handle(comando)

@comando.register(ActivarCampana) 
def ejecutar_comando_activar_campania(comando: ActivarCampana):
    handler = ActivarCampaniaHandler()
    handler.handle(comando)

@comando.register(AgregarAfiliadoACampana)
def ejecutar_comando_agregar_afiliado(comando: AgregarAfiliadoACampana):
    handler = AgregarAfiliadoACampaniaHandler()
    handler.handle(comando)

@dataclass  
class ActivarCampana(Comando):
    """Comando para activar una campaña existente"""
    id_campania: str

class ActivarCampanaHandler(ComandoHandler):
    """Handler para activar campanias"""
    
    def __init__(self):
        self._repositorio_campanias: RepositorioCampanias = RepositorioCampanias()
        self._uow: UnidadTrabajo = UnidadTrabajo()

    def handle(self, comando: ActivarCampana):
        """Activa la campaña especificada"""
        with self._uow:
            repositorio = self._uow.repositorio_campanias
            campania = repositorio.obtener_por_id(comando.id_campania)
            
            if not campania:
                raise Exception(f"Campaña {comando.id_campania} no encontrada")
            
            # Ejecutar lógica de dominio - DISPARA CampaniaActivada
            campania.activar_campania()
            
            repositorio.agregar(campania)
            self._uow.savepoint()

@dataclass
class AgregarAfiliadoACampana(Comando):
    """Comando para agregar un afiliado a una campaña"""
    id_campania: str
    id_afiliado: str
    configuracion_afiliado: dict
    comision_aplicable: float = 0.0

class AgregarAfiliadoACampanaHandler(ComandoHandler):
    """Handler para agregar afiliados a campanias"""
    
    def __init__(self):
        self._repositorio_campanias: RepositorioCampanias = RepositorioCampanias()
        self._uow: UnidadTrabajo = UnidadTrabajo()

    def handle(self, comando: AgregarAfiliadoACampana):
        """Agrega afiliado a la campaña"""
        with self._uow:
            repositorio = self._uow.repositorio_campanias
            campania = repositorio.obtener_por_id(comando.id_campania)
            
            if not campania:
                raise Exception(f"Campaña {comando.id_campania} no encontrada")
            
            # Ejecutar lógica de dominio - DISPARA AfiliadoAgregadoACampania
            campania.agregar_afiliado(
                comando.id_afiliado,
                comando.configuracion_afiliado,
                comando.comision_aplicable
            )
            
            repositorio.agregar(campania)
            self._uow.savepoint()

# Registrar handlers con el despachador de comandos
@comando.register(CrearCampana)
def ejecutar_comando_crear_campania(comando: CrearCampana):
    handler = CrearCampaniaHandler()
    handler.handle(comando)

@comando.register(ActivarCampana) 
def ejecutar_comando_activar_campania(comando: ActivarCampana):
    handler = ActivarCampanaHandler()
    handler.handle(comando)

@comando.register(AgregarAfiliadoACampana)
def ejecutar_comando_agregar_afiliado(comando: AgregarAfiliadoACampana):
    handler = AgregarAfiliadoACampanaHandler()
    handler.handle(comando)