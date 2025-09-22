from dataclasses import dataclass
from datetime import datetime
from typing import Any
from campanias.seedwork.dominio.eventos import EventoDominio
from .objetos_valor import EstadoCampana, TipoCampana, CanalPublicidad, ObjetivoCampana

# Clase base para eventos de dominio de campaña
class EventoDominioCampania(EventoDominio):
    """Clase base para todos los eventos de dominio relacionados con campanias"""
    pass

@dataclass
class CampaniaCreada(EventoDominioCampania):
    id_campania: str = ""
    nombre: str = ""
    descripcion: str = ""
    estado: str = ""  # EstadoCampana.BORRADOR
    tipo: str = ""  # TipoCampana value
    canal_publicidad: str = ""  # CanalPublicidad value
    objetivo: str = ""  # ObjetivoCampana value
    fecha_inicio: datetime = None
    fecha_fin: datetime = None
    fecha_creacion: datetime = None
    presupuesto: float = 0.0
    moneda: str = ""
    codigo_campana: str = ""
    segmento_audiencia: str = ""
    activo: bool = True

@dataclass
class CampaniaActivada(EventoDominioCampania):
    id_campania: str = ""
    fecha_activacion: datetime = None
    estado_anterior: str = ""
    estado_nuevo: str = ""  # EstadoCampana.ACTIVA

@dataclass
class CampaniaPausada(EventoDominio):
    id_campania: str = ""
    fecha_pausa: datetime = None
    razon_pausa: str = ""
    estado_anterior: str = ""
    estado_nuevo: str = ""  # EstadoCampana.PAUSADA

@dataclass
class CampaniaConfirmada(EventoDominio):
    id_campania: str = ""
    fecha_confirmacion: datetime = None
    confirmada_por: str = ""
    detalles_confirmacion: str = ""

@dataclass
class CampaniaActualizada(EventoDominio):
    id_campania: str = ""
    nombre: str = ""
    descripcion: str = ""
    fecha_inicio: datetime = None
    fecha_fin: datetime = None
    fecha_actualizacion: datetime = None
    presupuesto: float = 0.0
    campos_modificados: list[str] = None  # Lista de campos que cambiaron

@dataclass
class CampaniaEliminada(EventoDominio):
    id_campania: str = ""
    nombre: str = ""
    fecha_eliminacion: datetime = None
    eliminada_por: str = ""
    razon_eliminacion: str = ""
    estado_final: str = ""  # EstadoCampana.CANCELADA

@dataclass
class AfiliadoAgregadoACampania(EventoDominio):
    id_campania: str = ""
    id_afiliado: str = ""
    fecha_asignacion: datetime = None
    configuracion_afiliado: dict = None
    comision_aplicable: float = 0.0

@dataclass
class AfiliadoRemovidoDeCampania(EventoDominio):
    id_campania: str = ""
    id_afiliado: str = ""
    fecha_remocion: datetime = None
    razon_remocion: str = ""

@dataclass
class CampaniaProductoAsignada(EventoDominio):
    id_campania: str = ""
    id_producto: str = ""
    fecha_asignacion: datetime = None
    descuento_aplicable: float = 0.0
    fecha_creacion: datetime = None
    activo: bool = True

@dataclass
class CampaniaServicioAsignada(EventoDominio):
    id_campania: str = ""
    id_servicio: str = ""
    fecha_asignacion: datetime = None
    descuento_aplicable: float = 0.0
    fecha_creacion: datetime = None
    activo: bool = True

@dataclass
class CampaniaFinalizadaAutomaticamente(EventoDominio):
    id_campania: str = ""
    fecha_finalizacion: datetime = None
    razon_finalizacion: str = ""  # "fecha_limite_alcanzada", "presupuesto_agotado"
    estadisticas_finales: dict = None
    fecha_eliminacion: int = None

