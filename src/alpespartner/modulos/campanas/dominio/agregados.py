"""
Agregado Campaña del Bounded Context Campañas
Siguiendo principios DDD estrictos - Core del dominio de campañas
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from alpespartner.seedwork.dominio.entidades import RaizAgregado
from .objetos_valor import PeriodoVigencia, TerminosComision, RestriccionGeografica, MetadatosCampana
from .eventos import CampanaCreada, CampanaActivada, CampanaDesactivada, TerminosModificados


class EstadoCampana(Enum):
    BORRADOR = "BORRADOR"
    ACTIVA = "ACTIVA"
    PAUSADA = "PAUSADA"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"


def _uuid():
    return str(uuid.uuid4())


@dataclass
class Campana(RaizAgregado):
    """
    Agregado Raíz Campaña - Gestiona el ciclo de vida completo de una campaña
    
    Responsabilidades:
    - Mantener coherencia de estado de la campaña
    - Validar reglas de negocio (períodos, términos)
    - Emitir eventos de dominio
    - Gestionar transiciones de estado válidas
    """
    
    metadatos: MetadatosCampana
    periodo_vigencia: PeriodoVigencia
    terminos_comision: TerminosComision
    restriccion_geografica: RestriccionGeografica
    estado: EstadoCampana = EstadoCampana.BORRADOR
    creada_en: datetime = field(default_factory=datetime.utcnow)
    activada_en: Optional[datetime] = None
    finalizada_en: Optional[datetime] = None
    
    @staticmethod
    def crear(metadatos: MetadatosCampana, 
              periodo: PeriodoVigencia, 
              terminos: TerminosComision,
              restricciones: RestriccionGeografica) -> 'Campana':
        """
        Factory method para crear una nueva campaña
        Aplica reglas de negocio y emite eventos
        """
        
        # Validaciones de dominio
        if periodo.inicio <= datetime.utcnow():
            raise ValueError("La fecha de inicio debe ser futura")
            
        if periodo.inicio >= periodo.fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha fin")
        
        campana = Campana(
            id=_uuid(),
            metadatos=metadatos,
            periodo_vigencia=periodo,
            terminos_comision=terminos,
            restriccion_geografica=restricciones,
            estado=EstadoCampana.BORRADOR
        )
        
        # Emitir evento de dominio
        campana.agregar_evento(CampanaCreada(
            campana_id=campana.id,
            nombre=metadatos.nombre,
            marca=metadatos.marca,
            occurred_at=campana.creada_en
        ))
        
        return campana
    
    def activar(self) -> None:
        """
        Activa la campaña si cumple las condiciones de negocio
        """
        # Reglas de negocio para activación
        if self.estado != EstadoCampana.BORRADOR:
            raise ValueError(f"No se puede activar campaña en estado {self.estado.value}")
            
        if self.periodo_vigencia.inicio > datetime.utcnow():
            # Programar activación futura (simplificado para POC)
            pass
            
        # Transición de estado
        self.estado = EstadoCampana.ACTIVA
        self.activada_en = datetime.utcnow()
        
        # Emitir evento de dominio
        self.agregar_evento(CampanaActivada(
            campana_id=self.id,
            nombre=self.metadatos.nombre,
            fecha_inicio=self.periodo_vigencia.inicio,
            fecha_fin=self.periodo_vigencia.fin,
            occurred_at=self.activada_en
        ))
    
    def pausar(self, motivo: str = "Pausada manualmente") -> None:
        """
        Pausa una campaña activa
        """
        if self.estado != EstadoCampana.ACTIVA:
            raise ValueError(f"Solo se pueden pausar campañas activas. Estado actual: {self.estado.value}")
            
        self.estado = EstadoCampana.PAUSADA
        
        self.agregar_evento(CampanaDesactivada(
            campana_id=self.id,
            nombre=self.metadatos.nombre,
            motivo=motivo,
            occurred_at=datetime.utcnow()
        ))
    
    def modificar_terminos(self, nuevos_terminos: TerminosComision) -> None:
        """
        Modifica los términos de comisión de la campaña
        Solo permitido en estado BORRADOR o PAUSADA
        """
        if self.estado not in [EstadoCampana.BORRADOR, EstadoCampana.PAUSADA]:
            raise ValueError(f"No se pueden modificar términos en estado {self.estado.value}")
            
        terminos_anteriores = self.terminos_comision
        self.terminos_comision = nuevos_terminos
        
        self.agregar_evento(TerminosModificados(
            campana_id=self.id,
            nombre=self.metadatos.nombre,
            porcentaje_anterior=str(terminos_anteriores.porcentaje_base),
            porcentaje_nuevo=str(nuevos_terminos.porcentaje_base),
            occurred_at=datetime.utcnow()
        ))
    
    def esta_vigente(self, fecha: datetime = None) -> bool:
        """
        Verifica si la campaña está vigente y activa
        """
        if self.estado != EstadoCampana.ACTIVA:
            return False
            
        return self.periodo_vigencia.esta_vigente(fecha)
    
    def puede_generar_comisiones(self, pais: str, region: str = None) -> bool:
        """
        Verifica si la campaña puede generar comisiones para una ubicación
        """
        if not self.esta_vigente():
            return False
            
        return self.restriccion_geografica.es_ubicacion_valida(pais, region)
    
    def finalizar_automaticamente(self) -> None:
        """
        Finaliza automáticamente la campaña cuando expire el período
        """
        if self.estado == EstadoCampana.ACTIVA and not self.periodo_vigencia.esta_vigente():
            self.estado = EstadoCampana.FINALIZADA
            self.finalizada_en = datetime.utcnow()
            
            self.agregar_evento(CampanaDesactivada(
                campana_id=self.id,
                nombre=self.metadatos.nombre,
                motivo="Campaña expirada automáticamente",
                occurred_at=self.finalizada_en
            ))
