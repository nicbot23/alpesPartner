"""
Entidades específicas del dominio Marketing
Implementa principios SOLID y Domain-Driven Design
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, TypeVar
from enum import Enum
import uuid

from .eventos import EventoDominio, EventoMarketingBase, GeneradorEventos

# Principio de Responsabilidad Única - Estados específicos
class EstadoCampana(Enum):
    """Estados posibles de una campaña"""
    BORRADOR = "borrador"
    ACTIVA = "activa"
    PAUSADA = "pausada"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"

class TipoCampana(Enum):
    """Tipos de campañas de marketing"""
    PROMOCIONAL = "promocional"
    FIDELIZACION = "fidelizacion"
    ADQUISICION = "adquisicion"
    RETENCION = "retencion"
    CROSS_SELLING = "cross_selling"
    UP_SELLING = "up_selling"

class TipoSegmento(Enum):
    """Tipos de segmentación"""
    DEMOGRAFICO = "demografico"
    GEOGRAFICO = "geografico"
    COMPORTAMIENTO = "comportamiento"
    PSICOGRAFICO = "psicografico"
    TRANSACCIONAL = "transaccional"

# Base para todas las entidades
@dataclass
class Entidad(ABC):
    """
    Base para todas las entidades del dominio
    Principio de Responsabilidad Única - identidad y comportamiento básico
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    version: int = 1

    def __post_init__(self):
        """Operaciones post-inicialización"""
        self.validar()
    
    @abstractmethod
    def validar(self):
        """Validar invariantes de la entidad"""
        pass

    def actualizar(self):
        """Actualizar timestamp de modificación"""
        self.fecha_actualizacion = datetime.now()
        self.version += 1

@dataclass
class RaizAgregado(Entidad):
    """
    Raíz de agregado DDD - coordina transacciones y eventos
    Principio de Consistencia y Cohesión
    """
    _eventos: List[object] = field(default_factory=list, init=False)
    
    def agregar_evento(self, evento: object):
        """Agregar evento de dominio"""
        self._eventos.append(evento)
    
    def obtener_eventos(self) -> List[object]:
        """Obtener eventos pendientes"""
        return self._eventos.copy()
    
    def limpiar_eventos(self):
        """Limpiar eventos después de procesamiento"""
        self._eventos.clear()

@dataclass  
class EntidadBase(Entidad):
    """
    Alias para compatibilidad hacia atrás
    """
    pass
    _eventos: List[EventoDominio] = field(default_factory=list, init=False, repr=False)
    
    def eventos(self) -> List[EventoDominio]:
        """Retorna eventos generados por la entidad"""
        return self._eventos.copy()
    
    def limpiar_eventos(self) -> None:
        """Limpia eventos después de ser procesados"""
        self._eventos.clear()
    
    def _agregar_evento(self, evento: EventoDominio) -> None:
        """Agrega evento a la lista interna"""
        self._eventos.append(evento)
    
    def _actualizar_version(self) -> None:
        """Actualiza versión y fecha de modificación"""
        self.version += 1
        self.fecha_actualizacion = datetime.now()

# Objetos de valor específicos de Marketing
@dataclass(frozen=True)
class ConfiguracionCampana:
    """
    Objeto de valor para configuración de campaña
    Principio de Responsabilidad Única - configuración específica
    """
    presupuesto_maximo: float
    fecha_inicio: datetime
    fecha_fin: datetime
    objetivo_conversiones: int
    canales: List[str]
    metadatos: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.fecha_inicio >= self.fecha_fin:
            raise ValueError("Fecha de inicio debe ser anterior a fecha fin")
        if self.presupuesto_maximo <= 0:
            raise ValueError("Presupuesto debe ser mayor a cero")
        if self.objetivo_conversiones <= 0:
            raise ValueError("Objetivo de conversiones debe ser mayor a cero")

@dataclass(frozen=True)
class CriterioSegmentacion:
    """
    Objeto de valor para criterios de segmentación
    Principio de Responsabilidad Única - criterios específicos
    """
    tipo: TipoSegmento
    campo: str
    operador: str
    valor: Any
    descripcion: Optional[str] = None
    
    def evaluar(self, datos_usuario: Dict[str, Any]) -> bool:
        """Evalúa si un usuario cumple el criterio"""
        if self.campo not in datos_usuario:
            return False
        
        valor_usuario = datos_usuario[self.campo]
        
        if self.operador == "igual":
            return valor_usuario == self.valor
        elif self.operador == "mayor":
            return valor_usuario > self.valor
        elif self.operador == "menor":
            return valor_usuario < self.valor
        elif self.operador == "contiene":
            return self.valor in str(valor_usuario)
        elif self.operador == "en":
            return valor_usuario in self.valor
        else:
            return False

# Eventos específicos de Marketing
@dataclass
class CampanaCreada(EventoMarketingBase):
    """Evento: Campaña creada"""
    nombre_campana: str = ""
    tipo_campana: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "CampanaCreada"

@dataclass
class CampanaActivada(EventoMarketingBase):
    """Evento: Campaña activada"""
    presupuesto: float = 0.0
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "CampanaActivada"

@dataclass
class CampanaPausada(EventoMarketingBase):
    """Evento: Campaña pausada"""
    razon: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "CampanaPausada"

@dataclass
class SegmentoCreado(EventoMarketingBase):
    """Evento: Segmento creado"""
    nombre_segmento: str = ""
    tipo_segmento: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.nombre = "SegmentoCreado"

# Entidad Agregado - Campaña
@dataclass
class Campana(EntidadBase, GeneradorEventos):
    """
    Agregado raíz para campañas de marketing
    Principio de Responsabilidad Única - gestionar campaña completa
    """
    nombre: str = ""
    descripcion: str = ""
    tipo: TipoCampana = TipoCampana.PROMOCIONAL
    estado: EstadoCampana = EstadoCampana.BORRADOR
    configuracion: Optional[ConfiguracionCampana] = None
    segmentos_objetivo: List[str] = field(default_factory=list)  # IDs de segmentos
    presupuesto_utilizado: float = 0.0
    conversiones_obtenidas: int = 0
    creador_id: str = ""
    
    def crear(self, nombre: str, descripcion: str, tipo: TipoCampana, creador_id: str) -> None:
        """
        Crea una nueva campaña
        Principio de Responsabilidad Única - creación controlada
        """
        if not nombre.strip():
            raise ValueError("Nombre de campaña es obligatorio")
        if not creador_id.strip():
            raise ValueError("Creador es obligatorio")
        
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()
        self.tipo = tipo
        self.creador_id = creador_id
        self.estado = EstadoCampana.BORRADOR
        
        # Generar evento
        evento = CampanaCreada(
            nombre_campana=self.nombre,
            tipo_campana=self.tipo.value
        )
        evento.campana_id = self.id
        evento.usuario_id = self.creador_id
        self._agregar_evento(evento)
        self._actualizar_version()
    
    def configurar(self, configuracion: ConfiguracionCampana) -> None:
        """
        Configura parámetros de la campaña
        Principio de Responsabilidad Única - configuración separada
        """
        if self.estado != EstadoCampana.BORRADOR:
            raise ValueError("Solo se puede configurar una campaña en borrador")
        
        self.configuracion = configuracion
        self._actualizar_version()
    
    def activar(self) -> None:
        """
        Activa la campaña
        Principio de Responsabilidad Única - cambio de estado controlado
        """
        if self.estado != EstadoCampana.BORRADOR:
            raise ValueError("Solo se puede activar una campaña en borrador")
        if not self.configuracion:
            raise ValueError("Campaña debe estar configurada antes de activar")
        if not self.segmentos_objetivo:
            raise ValueError("Campaña debe tener al menos un segmento objetivo")
        
        self.estado = EstadoCampana.ACTIVA
        
        # Generar evento
        evento = CampanaActivada(
            presupuesto=self.configuracion.presupuesto_maximo
        )
        evento.campana_id = self.id
        self._agregar_evento(evento)
        self._actualizar_version()
    
    def pausar(self, razon: str = "") -> None:
        """
        Pausa la campaña
        Principio de Responsabilidad Única - pausa controlada
        """
        if self.estado != EstadoCampana.ACTIVA:
            raise ValueError("Solo se puede pausar una campaña activa")
        
        self.estado = EstadoCampana.PAUSADA
        
        # Generar evento
        evento = CampanaPausada(
            razon=razon
        )
        evento.campana_id = self.id
        self._agregar_evento(evento)
        self._actualizar_version()
    
    def agregar_segmento(self, segmento_id: str) -> None:
        """Agrega segmento objetivo a la campaña"""
        if not segmento_id.strip():
            raise ValueError("ID de segmento es obligatorio")
        
        if segmento_id not in self.segmentos_objetivo:
            self.segmentos_objetivo.append(segmento_id)
            self._actualizar_version()
    
    def registrar_conversion(self, valor: float = 0.0) -> None:
        """
        Registra una conversión en la campaña
        Principio de Responsabilidad Única - tracking específico
        """
        if self.estado != EstadoCampana.ACTIVA:
            return  # Solo registrar en campañas activas
        
        self.conversiones_obtenidas += 1
        if valor > 0:
            self.presupuesto_utilizado += valor
        
        self._actualizar_version()
    
    def puede_continuar(self) -> bool:
        """Determina si la campaña puede continuar ejecutándose"""
        if self.estado != EstadoCampana.ACTIVA:
            return False
        
        if not self.configuracion:
            return False
        
        # Verificar límites
        if self.presupuesto_utilizado >= self.configuracion.presupuesto_maximo:
            return False
        
        if datetime.now() > self.configuracion.fecha_fin:
            return False
        
        return True
    
    def validar(self):
        """Validar invariantes de la entidad Campana"""
        # Básico: nombre no vacío
        if hasattr(self, 'nombre') and self.nombre and not self.nombre.strip():
            raise ValueError("Nombre de campaña no puede estar vacío")
        # Otras validaciones pueden agregarse aquí según evolucionen las reglas de negocio

# Entidad Agregado - Segmento
@dataclass
class Segmento(EntidadBase, GeneradorEventos):
    """
    Agregado raíz para segmentos de marketing
    Principio de Responsabilidad Única - gestionar segmentación
    """
    nombre: str = ""
    descripcion: str = ""
    tipo: TipoSegmento = TipoSegmento.DEMOGRAFICO
    criterios: List[CriterioSegmentacion] = field(default_factory=list)
    usuarios_incluidos: List[str] = field(default_factory=list)  # IDs de usuarios
    activo: bool = True
    creador_id: str = ""
    
    def crear(self, nombre: str, descripcion: str, tipo: TipoSegmento, creador_id: str) -> None:
        """
        Crea un nuevo segmento
        Principio de Responsabilidad Única - creación controlada
        """
        if not nombre.strip():
            raise ValueError("Nombre de segmento es obligatorio")
        if not creador_id.strip():
            raise ValueError("Creador es obligatorio")
        
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()
        self.tipo = tipo
        self.creador_id = creador_id
        self.activo = True
        
        # Generar evento
        evento = SegmentoCreado(
            nombre_segmento=self.nombre,
            tipo_segmento=self.tipo.value
        )
        evento.segmento_id = self.id
        evento.usuario_id = self.creador_id
        self._agregar_evento(evento)
        self._actualizar_version()
    
    def agregar_criterio(self, criterio: CriterioSegmentacion) -> None:
        """
        Agrega criterio de segmentación
        Principio de Responsabilidad Única - gestión de criterios
        """
        self.criterios.append(criterio)
        self._actualizar_version()
    
    def evaluar_usuario(self, datos_usuario: Dict[str, Any]) -> bool:
        """
        Evalúa si un usuario pertenece al segmento
        Principio de Responsabilidad Única - evaluación específica
        """
        if not self.activo:
            return False
        
        if not self.criterios:
            return False
        
        # Todos los criterios deben cumplirse (AND lógico)
        for criterio in self.criterios:
            if not criterio.evaluar(datos_usuario):
                return False
        
        return True
    
    def incluir_usuario(self, usuario_id: str) -> None:
        """Incluye usuario en el segmento manualmente"""
        if not usuario_id.strip():
            raise ValueError("ID de usuario es obligatorio")
        
        if usuario_id not in self.usuarios_incluidos:
            self.usuarios_incluidos.append(usuario_id)
            self._actualizar_version()
    
    def excluir_usuario(self, usuario_id: str) -> None:
        """Excluye usuario del segmento"""
        if usuario_id in self.usuarios_incluidos:
            self.usuarios_incluidos.remove(usuario_id)
            self._actualizar_version()
    
    def activar(self) -> None:
        """Activa el segmento"""
        self.activo = True
        self._actualizar_version()
    
    def desactivar(self) -> None:
        """Desactiva el segmento"""
        self.activo = False
        self._actualizar_version()
    
    def validar(self):
        """Validar invariantes de la entidad Segmento"""
        # Básico: nombre no vacío
        if hasattr(self, 'nombre') and self.nombre and not self.nombre.strip():
            raise ValueError("Nombre de segmento no puede estar vacío")
        # Otras validaciones pueden agregarse aquí según evolucionen las reglas de negocio

# Interfaces de repositorio específicas
class RepositorioCampanas(ABC):
    """
    Interface para persistir campañas
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def guardar(self, campana: Campana) -> None:
        """Guarda campaña"""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, campana_id: str) -> Optional[Campana]:
        """Obtiene campaña por ID"""
        pass
    
    @abstractmethod
    async def obtener_activas(self) -> List[Campana]:
        """Obtiene campañas activas"""
        pass
    
    @abstractmethod
    async def obtener_por_creador(self, creador_id: str) -> List[Campana]:
        """Obtiene campañas por creador"""
        pass

class RepositorioSegmentos(ABC):
    """
    Interface para persistir segmentos
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def guardar(self, segmento: Segmento) -> None:
        """Guarda segmento"""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, segmento_id: str) -> Optional[Segmento]:
        """Obtiene segmento por ID"""
        pass
    
    @abstractmethod
    async def obtener_activos(self) -> List[Segmento]:
        """Obtiene segmentos activos"""
        pass
    
    @abstractmethod
    async def obtener_por_tipo(self, tipo: TipoSegmento) -> List[Segmento]:
        """Obtiene segmentos por tipo"""
        pass

# Factory para crear entidades
class FabricaMarketing:
    """
    Factory para crear entidades de marketing
    Principio de Responsabilidad Única - creación centralizada
    """
    
    @staticmethod
    def crear_campana_promocional(
        nombre: str,
        descripcion: str,
        creador_id: str,
        presupuesto: float,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        objetivo_conversiones: int,
        canales: List[str]
    ) -> Campana:
        """Crea una campaña promocional configurada"""
        campana = Campana()
        campana.crear(nombre, descripcion, TipoCampana.PROMOCIONAL, creador_id)
        
        configuracion = ConfiguracionCampana(
            presupuesto_maximo=presupuesto,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            objetivo_conversiones=objetivo_conversiones,
            canales=canales
        )
        campana.configurar(configuracion)
        
        return campana
    
    @staticmethod
    def crear_segmento_demografico(
        nombre: str,
        descripcion: str,
        creador_id: str,
        criterios_demograficos: List[Dict[str, Any]]
    ) -> Segmento:
        """Crea un segmento demográfico"""
        segmento = Segmento()
        segmento.crear(nombre, descripcion, TipoSegmento.DEMOGRAFICO, creador_id)
        
        for criterio_data in criterios_demograficos:
            criterio = CriterioSegmentacion(
                tipo=TipoSegmento.DEMOGRAFICO,
                campo=criterio_data["campo"],
                operador=criterio_data["operador"],
                valor=criterio_data["valor"],
                descripcion=criterio_data.get("descripcion")
            )
            segmento.agregar_criterio(criterio)
        
        return segmento