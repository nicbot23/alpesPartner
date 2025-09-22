from datetime import datetime
from campanias.seedwork.dominio.entidades import Entidad, AgregacionRaiz
from dataclasses import dataclass, field
import uuid

from .objetos_valor import (
    NombreCampaña, DescripcionCampaña, FechaInicio, FechaFin, 
    CodigoCampana, EstadoCampana, TipoCampana, CanalPublicidad, 
    ObjetivoCampana, Presupuesto, Moneda, SegmentoAudiencia, Activo
)
from .eventos import (
    CampaniaCreada, CampaniaActivada, CampaniaPausada, CampaniaConfirmada,
    CampaniaActualizada, CampaniaEliminada, AfiliadoAgregadoACampania,
    AfiliadoRemovidoDeCampania, CampaniaProductoAsignada, CampaniaServicioAsignada
)

@dataclass
class Campaña(AgregacionRaiz):
    nombre: NombreCampaña = field(default_factory=NombreCampaña)
    descripcion: DescripcionCampaña = field(default_factory=DescripcionCampaña)
    estado: EstadoCampana = field(default=EstadoCampana.BORRADOR)
    tipo: TipoCampana = field(default_factory=lambda: None)
    canal_publicidad: CanalPublicidad = field(default_factory=lambda: None)
    objetivo: ObjetivoCampana = field(default_factory=lambda: None)
    fecha_inicio: FechaInicio = field(default_factory=FechaInicio)
    fecha_fin: FechaFin = field(default_factory=FechaFin)
    presupuesto: Presupuesto = field(default_factory=Presupuesto)
    moneda: Moneda = field(default_factory=Moneda)
    codigo_campana: CodigoCampana = field(default_factory=CodigoCampana)
    segmento_audiencia: SegmentoAudiencia = field(default_factory=SegmentoAudiencia)
    activo: Activo = field(default_factory=lambda: Activo(True))

    def crear_campania(self, datos_campania):
        """Crea una nueva campaña y dispara evento CampaniaCreada"""
        self.nombre = NombreCampaña(datos_campania.get('nombre'))
        self.descripcion = DescripcionCampaña(datos_campania.get('descripcion'))
        self.tipo = datos_campania.get('tipo')
        self.canal_publicidad = datos_campania.get('canal_publicidad')
        self.objetivo = datos_campania.get('objetivo')
        self.fecha_inicio = FechaInicio(datos_campania.get('fecha_inicio'))
        self.fecha_fin = FechaFin(datos_campania.get('fecha_fin'))
        self.presupuesto = Presupuesto(datos_campania.get('presupuesto', 0.0))
        self.moneda = Moneda(datos_campania.get('moneda', 'USD'))
        self.codigo_campana = CodigoCampana(datos_campania.get('codigo_campana'))
        self.segmento_audiencia = SegmentoAudiencia(datos_campania.get('segmento_audiencia'))
        self.estado = EstadoCampana.BORRADOR
        self.fecha_creacion = datetime.now()
        self.activo = Activo(True)

        self.agregar_evento(CampaniaCreada(
            id_campania=str(self.id),
            nombre=self.nombre.nombre,
            descripcion=self.descripcion.descripcion,
            estado=self.estado.value,
            tipo=self.tipo.value if self.tipo else None,
            canal_publicidad=self.canal_publicidad.value if self.canal_publicidad else None,
            objetivo=self.objetivo.value if self.objetivo else None,
            fecha_inicio=self.fecha_inicio.fecha_inicio,
            fecha_fin=self.fecha_fin.fecha_fin,
            fecha_creacion=self.fecha_creacion,
            presupuesto=self.presupuesto.presupuesto,
            moneda=self.moneda.moneda,
            codigo_campana=self.codigo_campana.codigo_campana,
            segmento_audiencia=self.segmento_audiencia.segmento_audiencia,
            activo=self.activo.activo
        ))

    def activar_campania(self):
        """Activa una campaña y dispara evento CampaniaActivada"""
        estado_anterior = self.estado
        self.estado = EstadoCampana.ACTIVA
        self.fecha_actualizacion = datetime.now()

        self.agregar_evento(CampaniaActivada(
            id_campania=str(self.id),
            fecha_activacion=self.fecha_actualizacion,
            estado_anterior=estado_anterior.value,
            estado_nuevo=self.estado.value
        ))

    def pausar_campania(self, razon: str = "Pausada manualmente"):
        """Pausa una campaña y dispara evento CampaniaPausada"""
        estado_anterior = self.estado
        self.estado = EstadoCampana.PAUSADA
        self.fecha_actualizacion = datetime.now()

        self.agregar_evento(CampaniaPausada(
            id_campania=str(self.id),
            fecha_pausa=self.fecha_actualizacion,
            razon_pausa=razon,
            estado_anterior=estado_anterior.value,
            estado_nuevo=self.estado.value
        ))

    def confirmar_campania(self, confirmada_por: str, detalles: str = ""):
        """Confirma una campaña y dispara evento CampaniaConfirmada"""
        self.fecha_actualizacion = datetime.now()

        self.agregar_evento(CampaniaConfirmada(
            id_campania=str(self.id),
            fecha_confirmacion=self.fecha_actualizacion,
            confirmada_por=confirmada_por,
            detalles_confirmacion=detalles
        ))

    def actualizar_campania(self, nuevos_datos: dict):
        """Actualiza una campaña y dispara evento CampaniaActualizada"""
        campos_modificados = []
        
        if 'nombre' in nuevos_datos and nuevos_datos['nombre'] != self.nombre.nombre:
            self.nombre = NombreCampaña(nuevos_datos['nombre'])
            campos_modificados.append('nombre')
            
        if 'descripcion' in nuevos_datos and nuevos_datos['descripcion'] != self.descripcion.descripcion:
            self.descripcion = DescripcionCampaña(nuevos_datos['descripcion'])
            campos_modificados.append('descripcion')
            
        if 'presupuesto' in nuevos_datos and nuevos_datos['presupuesto'] != self.presupuesto.presupuesto:
            self.presupuesto = Presupuesto(nuevos_datos['presupuesto'])
            campos_modificados.append('presupuesto')

        self.fecha_actualizacion = datetime.now()

        if campos_modificados:
            self.agregar_evento(CampaniaActualizada(
                id_campania=str(self.id),
                nombre=self.nombre.nombre,
                descripcion=self.descripcion.descripcion,
                fecha_inicio=self.fecha_inicio.fecha_inicio,
                fecha_fin=self.fecha_fin.fecha_fin,
                fecha_actualizacion=self.fecha_actualizacion,
                presupuesto=self.presupuesto.presupuesto,
                campos_modificados=campos_modificados
            ))

    def eliminar_campania(self, eliminada_por: str, razon: str = "Eliminación manual"):
        """Elimina una campaña y dispara evento CampaniaEliminada"""
        self.estado = EstadoCampana.CANCELADA
        self.activo = Activo(False)
        self.fecha_actualizacion = datetime.now()

        self.agregar_evento(CampaniaEliminada(
            id_campania=str(self.id),
            nombre=self.nombre.nombre,
            fecha_eliminacion=self.fecha_actualizacion,
            eliminada_por=eliminada_por,
            razon_eliminacion=razon,
            estado_final=self.estado.value
        ))

    def agregar_afiliado(self, id_afiliado: str, configuracion: dict, comision: float = 0.0):
        """Agrega un afiliado a la campaña y dispara evento"""
        fecha_asignacion = datetime.now()

        self.agregar_evento(AfiliadoAgregadoACampania(
            id_campania=str(self.id),
            id_afiliado=id_afiliado,
            fecha_asignacion=fecha_asignacion,
            configuracion_afiliado=configuracion,
            comision_aplicable=comision
        ))

    def remover_afiliado(self, id_afiliado: str, razon: str = "Removido manualmente"):
        """Remueve un afiliado de la campaña y dispara evento"""
        fecha_remocion = datetime.now()

        self.agregar_evento(AfiliadoRemovidoDeCampania(
            id_campania=str(self.id),
            id_afiliado=id_afiliado,
            fecha_remocion=fecha_remocion,
            razon_remocion=razon
        ))

@dataclass
class CampañaProducto(AgregacionRaiz):
    campania_id: str = None
    producto_id: str = None
    descuento_aplicable: float = 0.0
    fecha_asignacion: datetime = field(default_factory=datetime.now)
    fecha_remocion: datetime = None
    activo: bool = True

    def asignar_producto(self, campania_id: str, producto_id: str, descuento: float = 0.0):
        """Asigna un producto a la campaña"""
        self.campania_id = campania_id
        self.producto_id = producto_id
        self.descuento_aplicable = descuento
        self.fecha_asignacion = datetime.now()
        self.fecha_creacion = datetime.now()

        self.agregar_evento(CampaniaProductoAsignada(
            id_campania=campania_id,
            id_producto=producto_id,
            fecha_asignacion=self.fecha_asignacion,
            descuento_aplicable=descuento,
            fecha_creacion=self.fecha_creacion,
            activo=True
        ))

@dataclass
class campaniaservicio(AgregacionRaiz):
    campania_id: str = None
    servicio_id: str = None
    descuento_aplicable: float = 0.0
    fecha_asignacion: datetime = field(default_factory=datetime.now)
    fecha_remocion: datetime = None
    activo: bool = True

    def asignar_servicio(self, campania_id: str, servicio_id: str, descuento: float = 0.0):
        """Asigna un servicio a la campaña"""
        self.campania_id = campania_id
        self.servicio_id = servicio_id
        self.descuento_aplicable = descuento
        self.fecha_asignacion = datetime.now()
        self.fecha_creacion = datetime.now()

        self.agregar_evento(CampaniaServicioAsignada(
            id_campania=campania_id,
            id_servicio=servicio_id,
            fecha_asignacion=self.fecha_asignacion,
            descuento_aplicable=descuento,
            fecha_creacion=self.fecha_creacion,
            activo=True
        ))

@dataclass
class campaniasegmento(Campaña, AgregacionRaiz):
    segmento_id: str = None
    fecha_asignacion: datetime = field(default_factory=datetime.now)
    fecha_remocion: datetime = None
    activo: bool = True
    prioridad: int = 0
    porcentaje_cobertura: float = 0.0
    porcentaje_cumplimiento: float = 0.0
    porcentaje_exclusion: float = 0.0
    porcentaje_cumplimiento_exclusion: float = 0.0
    porcentaje_cumplimiento_inclusion: float = 0.0
    porcentaje_cumplimiento_general: float = 0.0
    porcentaje_cumplimiento_general_exclusion: float = 0.0
    porcentaje_cumplimiento_general_inclusion: float = 0.0