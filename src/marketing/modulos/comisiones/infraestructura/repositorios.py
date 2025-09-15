"""
Repositorios del módulo de comisiones - Marketing Microservice
Implementación de persistencia con SQLAlchemy y patrones enterprise
Arquitectura: Repository Pattern + Unit of Work + ORM Mapping
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any, Type, Union
from abc import ABC, abstractmethod
import uuid

from sqlalchemy import (
    Column, String, DateTime, Numeric, Text, Boolean, 
    ForeignKey, Index, CheckConstraint, UniqueConstraint,
    create_engine, MetaData, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship, backref
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from ..dominio.entidades import (
    Comision, EstadoComision, TipoComision, MontoMonetario,
    PorcentajeComision, ConfiguracionComision, ExcepcionDominio
)
from ..aplicacion.servicios import RepositorioComisiones, RepositorioEventos

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================

Base = declarative_base()
metadata = MetaData()

# =============================================================================
# MODELOS ORM - MAPEO OBJETO-RELACIONAL
# =============================================================================

class ComisionORM(Base):
    """
    Modelo ORM para la tabla de comisiones
    Principio de Responsabilidad Única - solo mapeo de datos
    """
    __tablename__ = 'comisiones'
    
    # Clave primaria
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relaciones con otros bounded contexts
    afiliado_id = Column(String(36), nullable=False, index=True)
    campana_id = Column(String(36), nullable=False, index=True)
    conversion_id = Column(String(36), nullable=False, unique=True)
    
    # Estado y tipo
    estado = Column(String(20), nullable=False, default=EstadoComision.PENDIENTE.value)
    tipo_comision = Column(String(20), nullable=False)
    
    # Montos y cálculos
    monto_base_valor = Column(Numeric(precision=12, scale=2), nullable=False)
    monto_base_moneda = Column(String(3), nullable=False, default='COP')
    porcentaje_valor = Column(Numeric(precision=5, scale=2), nullable=True)
    monto_calculado_valor = Column(Numeric(precision=12, scale=2), nullable=True)
    monto_calculado_moneda = Column(String(3), nullable=True)
    
    # Fechas de ciclo de vida
    fecha_creacion = Column(DateTime, nullable=False, default=func.now())
    fecha_actualizacion = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    fecha_calculo = Column(DateTime, nullable=True)
    fecha_aprobacion = Column(DateTime, nullable=True)
    fecha_pago = Column(DateTime, nullable=True)
    fecha_anulacion = Column(DateTime, nullable=True)
    
    # Workflow y auditoría
    aprobador_id = Column(String(36), nullable=True)
    rechazador_id = Column(String(36), nullable=True)
    motivo_rechazo = Column(Text, nullable=True)
    comentarios = Column(Text, nullable=True)
    
    # Pagos
    metodo_pago = Column(String(50), nullable=True)
    referencia_pago = Column(String(100), nullable=True)
    monto_pagado_valor = Column(Numeric(precision=12, scale=2), nullable=True)
    monto_pagado_moneda = Column(String(3), nullable=True)
    
    # Configuración y metadatos (JSON para flexibilidad)
    configuracion = Column(JSONB, nullable=True)
    metadatos = Column(JSONB, nullable=True)
    metadatos_aprobacion = Column(JSONB, nullable=True)
    metadatos_rechazo = Column(JSONB, nullable=True)
    metadatos_pago = Column(JSONB, nullable=True)
    
    # Auditoría
    version = Column(String(10), nullable=False, default='1.0')
    usuario_creacion = Column(String(36), nullable=True)
    usuario_actualizacion = Column(String(36), nullable=True)
    
    # Índices para optimización de consultas
    __table_args__ = (
        Index('ix_comisiones_afiliado_estado', 'afiliado_id', 'estado'),
        Index('ix_comisiones_campana_estado', 'campana_id', 'estado'),
        Index('ix_comisiones_fechas', 'fecha_creacion', 'fecha_calculo'),
        Index('ix_comisiones_montos', 'monto_calculado_valor', 'estado'),
        CheckConstraint('monto_base_valor > 0', name='ck_monto_base_positivo'),
        CheckConstraint('porcentaje_valor >= 0 AND porcentaje_valor <= 100', name='ck_porcentaje_valido'),
        UniqueConstraint('conversion_id', name='uq_comision_conversion'),
    )

class EventoComisionORM(Base):
    """
    Modelo ORM para eventos de dominio de comisiones
    Event Sourcing simplificado para auditoría
    """
    __tablename__ = 'eventos_comisiones'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    comision_id = Column(String(36), ForeignKey('comisiones.id'), nullable=False, index=True)
    tipo_evento = Column(String(50), nullable=False)
    datos_evento = Column(JSONB, nullable=False)
    fecha_evento = Column(DateTime, nullable=False, default=func.now())
    usuario_id = Column(String(36), nullable=True)
    correlacion_id = Column(String(36), nullable=True)
    version_agregado = Column(String(10), nullable=False)
    
    # Relación con comisión
    comision = relationship("ComisionORM", backref=backref("eventos", lazy="dynamic"))
    
    __table_args__ = (
        Index('ix_eventos_comision_fecha', 'comision_id', 'fecha_evento'),
        Index('ix_eventos_tipo_fecha', 'tipo_evento', 'fecha_evento'),
    )

# =============================================================================
# MAPEADORES - CONVERSIÓN DOMINIO <-> ORM
# =============================================================================

class MapeadorComision:
    """
    Mapeador entre entidad de dominio y modelo ORM
    Principio de Responsabilidad Única - solo conversión de datos
    """
    
    @staticmethod
    def a_orm(comision: Comision) -> ComisionORM:
        """Convertir entidad de dominio a modelo ORM"""
        orm = ComisionORM()
        
        # Campos básicos
        orm.id = comision.id
        orm.afiliado_id = comision.afiliado_id
        orm.campana_id = comision.campana_id
        orm.conversion_id = comision.conversion_id
        orm.estado = comision.estado.value
        orm.tipo_comision = comision.tipo_comision.value
        
        # Montos
        orm.monto_base_valor = comision.monto_base.valor
        orm.monto_base_moneda = comision.monto_base.moneda
        
        if comision.porcentaje:
            orm.porcentaje_valor = comision.porcentaje.valor
        
        if comision.monto_calculado:
            orm.monto_calculado_valor = comision.monto_calculado.valor
            orm.monto_calculado_moneda = comision.monto_calculado.moneda
        
        # Fechas
        orm.fecha_creacion = comision.fecha_creacion
        orm.fecha_actualizacion = comision.fecha_actualizacion
        orm.fecha_calculo = comision.fecha_calculo
        orm.fecha_aprobacion = comision.fecha_aprobacion
        orm.fecha_pago = comision.fecha_pago
        
        # Workflow
        orm.aprobador_id = comision.aprobador_id
        orm.comentarios = comision.comentarios
        
        # Configuración y metadatos
        if comision.configuracion:
            orm.configuracion = comision.configuracion.a_dict()
        orm.metadatos = comision.metadatos
        
        # Versión
        orm.version = str(comision.version)
        
        return orm
    
    @staticmethod
    def a_dominio(orm: ComisionORM) -> Comision:
        """Convertir modelo ORM a entidad de dominio"""
        # Crear objetos de valor
        monto_base = MontoMonetario(
            valor=orm.monto_base_valor,
            moneda=orm.monto_base_moneda
        )
        
        porcentaje = None
        if orm.porcentaje_valor is not None:
            porcentaje = PorcentajeComision(valor=orm.porcentaje_valor)
        
        monto_calculado = None
        if orm.monto_calculado_valor is not None:
            monto_calculado = MontoMonetario(
                valor=orm.monto_calculado_valor,
                moneda=orm.monto_calculado_moneda or orm.monto_base_moneda
            )
        
        configuracion = None
        if orm.configuracion:
            configuracion = ConfiguracionComision.desde_dict(orm.configuracion)
        
        # Crear entidad
        comision = Comision(
            id=orm.id,
            afiliado_id=orm.afiliado_id,
            campana_id=orm.campana_id,
            conversion_id=orm.conversion_id,
            estado=EstadoComision(orm.estado),
            tipo_comision=TipoComision(orm.tipo_comision),
            monto_base=monto_base,
            porcentaje=porcentaje,
            monto_calculado=monto_calculado,
            configuracion=configuracion,
            fecha_creacion=orm.fecha_creacion,
            fecha_actualizacion=orm.fecha_actualizacion,
            fecha_calculo=orm.fecha_calculo,
            fecha_aprobacion=orm.fecha_aprobacion,
            fecha_pago=orm.fecha_pago,
            aprobador_id=orm.aprobador_id,
            comentarios=orm.comentarios,
            metadatos=orm.metadatos or {},
            version=int(float(orm.version))
        )
        
        return comision

# =============================================================================
# IMPLEMENTACIONES DE REPOSITORIO
# =============================================================================

class RepositorioComisionesSQLAlchemy(RepositorioComisiones):
    """
    Implementación SQLAlchemy del repositorio de comisiones
    Repository Pattern + Dependency Inversion Principle
    """
    
    def __init__(self, session: Session):
        self._session = session
        self._mapeador = MapeadorComision()
    
    def obtener_por_id(self, comision_id: str) -> Optional[Comision]:
        """Obtener comisión por ID"""
        try:
            orm = self._session.query(ComisionORM).filter(ComisionORM.id == comision_id).first()
            if orm:
                return self._mapeador.a_dominio(orm)
            return None
        except Exception as ex:
            raise ExcepcionDominio(f"Error al obtener comisión {comision_id}: {ex}") from ex
    
    def guardar(self, comision: Comision) -> None:
        """Guardar comisión (crear o actualizar)"""
        try:
            # Verificar si existe
            orm_existente = self._session.query(ComisionORM).filter(ComisionORM.id == comision.id).first()
            
            if orm_existente:
                # Actualizar existente
                orm_actualizado = self._mapeador.a_orm(comision)
                for attr, value in vars(orm_actualizado).items():
                    if not attr.startswith('_') and attr != 'id':
                        setattr(orm_existente, attr, value)
            else:
                # Crear nuevo
                orm_nuevo = self._mapeador.a_orm(comision)
                self._session.add(orm_nuevo)
            
            # No hacer commit aquí - se maneja en la unidad de trabajo
            
        except Exception as ex:
            raise ExcepcionDominio(f"Error al guardar comisión {comision.id}: {ex}") from ex
    
    def listar_por_afiliado(self, afiliado_id: str, estados: Optional[List[EstadoComision]] = None) -> List[Comision]:
        """Listar comisiones por afiliado"""
        try:
            query = self._session.query(ComisionORM).filter(ComisionORM.afiliado_id == afiliado_id)
            
            if estados:
                estados_valores = [estado.value for estado in estados]
                query = query.filter(ComisionORM.estado.in_(estados_valores))
            
            query = query.order_by(ComisionORM.fecha_creacion.desc())
            ormes = query.all()
            
            return [self._mapeador.a_dominio(orm) for orm in ormes]
            
        except Exception as ex:
            raise ExcepcionDominio(f"Error al listar comisiones por afiliado {afiliado_id}: {ex}") from ex
    
    def listar_por_campana(self, campana_id: str, estados: Optional[List[EstadoComision]] = None) -> List[Comision]:
        """Listar comisiones por campaña"""
        try:
            query = self._session.query(ComisionORM).filter(ComisionORM.campana_id == campana_id)
            
            if estados:
                estados_valores = [estado.value for estado in estados]
                query = query.filter(ComisionORM.estado.in_(estados_valores))
            
            query = query.order_by(ComisionORM.fecha_creacion.desc())
            ormes = query.all()
            
            return [self._mapeador.a_dominio(orm) for orm in ormes]
            
        except Exception as ex:
            raise ExcepcionDominio(f"Error al listar comisiones por campaña {campana_id}: {ex}") from ex
    
    def existe_por_conversion(self, conversion_id: str) -> bool:
        """Verificar si existe comisión para conversión"""
        try:
            return self._session.query(ComisionORM).filter(ComisionORM.conversion_id == conversion_id).first() is not None
        except Exception as ex:
            raise ExcepcionDominio(f"Error al verificar conversión {conversion_id}: {ex}") from ex
    
    def listar_por_filtros(
        self,
        estados: Optional[List[EstadoComision]] = None,
        tipos: Optional[List[TipoComision]] = None,
        afiliados_ids: Optional[List[str]] = None,
        campanas_ids: Optional[List[str]] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limite: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Comision]:
        """Listar comisiones con filtros avanzados"""
        try:
            query = self._session.query(ComisionORM)
            
            # Aplicar filtros
            if estados:
                estados_valores = [estado.value for estado in estados]
                query = query.filter(ComisionORM.estado.in_(estados_valores))
            
            if tipos:
                tipos_valores = [tipo.value for tipo in tipos]
                query = query.filter(ComisionORM.tipo_comision.in_(tipos_valores))
            
            if afiliados_ids:
                query = query.filter(ComisionORM.afiliado_id.in_(afiliados_ids))
            
            if campanas_ids:
                query = query.filter(ComisionORM.campana_id.in_(campanas_ids))
            
            if fecha_desde:
                query = query.filter(ComisionORM.fecha_creacion >= fecha_desde)
            
            if fecha_hasta:
                query = query.filter(ComisionORM.fecha_creacion <= fecha_hasta)
            
            # Ordenamiento y paginación
            query = query.order_by(ComisionORM.fecha_creacion.desc())
            
            if offset:
                query = query.offset(offset)
            
            if limite:
                query = query.limit(limite)
            
            ormes = query.all()
            return [self._mapeador.a_dominio(orm) for orm in ormes]
            
        except Exception as ex:
            raise ExcepcionDominio(f"Error al listar comisiones con filtros: {ex}") from ex
    
    def contar_por_filtros(
        self,
        estados: Optional[List[EstadoComision]] = None,
        tipos: Optional[List[TipoComision]] = None,
        afiliados_ids: Optional[List[str]] = None,
        campanas_ids: Optional[List[str]] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> int:
        """Contar comisiones que coinciden con filtros"""
        try:
            query = self._session.query(ComisionORM)
            
            # Aplicar los mismos filtros que en listar_por_filtros
            if estados:
                estados_valores = [estado.value for estado in estados]
                query = query.filter(ComisionORM.estado.in_(estados_valores))
            
            if tipos:
                tipos_valores = [tipo.value for tipo in tipos]
                query = query.filter(ComisionORM.tipo_comision.in_(tipos_valores))
            
            if afiliados_ids:
                query = query.filter(ComisionORM.afiliado_id.in_(afiliados_ids))
            
            if campanas_ids:
                query = query.filter(ComisionORM.campana_id.in_(campanas_ids))
            
            if fecha_desde:
                query = query.filter(ComisionORM.fecha_creacion >= fecha_desde)
            
            if fecha_hasta:
                query = query.filter(ComisionORM.fecha_creacion <= fecha_hasta)
            
            return query.count()
            
        except Exception as ex:
            raise ExcepcionDominio(f"Error al contar comisiones: {ex}") from ex

# =============================================================================
# REPOSITORIO DE EVENTOS
# =============================================================================

class RepositorioEventosSQLAlchemy(RepositorioEventos):
    """
    Implementación SQLAlchemy del repositorio de eventos
    Event Store Pattern para auditoría y trazabilidad
    """
    
    def __init__(self, session: Session):
        self._session = session
    
    def guardar_evento(self, evento: Any) -> None:
        """Guardar evento de dominio"""
        try:
            evento_orm = EventoComisionORM(
                id=str(uuid.uuid4()),
                comision_id=getattr(evento, 'comision_id', ''),
                tipo_evento=type(evento).__name__,
                datos_evento={
                    'id': getattr(evento, 'id', ''),
                    'fecha': getattr(evento, 'fecha', datetime.now()).isoformat(),
                    'datos': getattr(evento, '__dict__', {})
                },
                fecha_evento=getattr(evento, 'fecha', datetime.now()),
                usuario_id=getattr(evento, 'usuario_id', ''),
                correlacion_id=getattr(evento, 'correlacion_id', ''),
                version_agregado='1.0'
            )
            
            self._session.add(evento_orm)
            
        except Exception as ex:
            raise ExcepcionDominio(f"Error al guardar evento: {ex}") from ex
    
    def obtener_eventos_por_agregado(self, agregado_id: str) -> List[Any]:
        """Obtener eventos por agregado (comisión)"""
        try:
            eventos_orm = (
                self._session.query(EventoComisionORM)
                .filter(EventoComisionORM.comision_id == agregado_id)
                .order_by(EventoComisionORM.fecha_evento)
                .all()
            )
            
            # Simplificado - en producción habría deserialización completa
            return [evento.datos_evento for evento in eventos_orm]
            
        except Exception as ex:
            raise ExcepcionDominio(f"Error al obtener eventos para {agregado_id}: {ex}") from ex

# =============================================================================
# UNIDAD DE TRABAJO - UNIT OF WORK PATTERN
# =============================================================================

class UnidadDeTrabajoComisiones:
    """
    Unidad de trabajo para operaciones transaccionales
    Unit of Work Pattern - garantiza consistencia transaccional
    """
    
    def __init__(self, session: Session):
        self._session = session
        self._repositorio_comisiones: Optional[RepositorioComisionesSQLAlchemy] = None
        self._repositorio_eventos: Optional[RepositorioEventosSQLAlchemy] = None
        self._committed = False
    
    @property
    def comisiones(self) -> RepositorioComisionesSQLAlchemy:
        """Obtener repositorio de comisiones"""
        if self._repositorio_comisiones is None:
            self._repositorio_comisiones = RepositorioComisionesSQLAlchemy(self._session)
        return self._repositorio_comisiones
    
    @property
    def eventos(self) -> RepositorioEventosSQLAlchemy:
        """Obtener repositorio de eventos"""
        if self._repositorio_eventos is None:
            self._repositorio_eventos = RepositorioEventosSQLAlchemy(self._session)
        return self._repositorio_eventos
    
    def commit(self) -> None:
        """Confirmar transacción"""
        if not self._committed:
            try:
                self._session.commit()
                self._committed = True
            except Exception as ex:
                self._session.rollback()
                raise ExcepcionDominio(f"Error al confirmar transacción: {ex}") from ex
    
    def rollback(self) -> None:
        """Revertir transacción"""
        if not self._committed:
            self._session.rollback()
    
    def __enter__(self):
        """Entrada del context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Salida del context manager"""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

# =============================================================================
# FACTORY DE INFRAESTRUCTURA
# =============================================================================

class FabricaInfraestructuraComisiones:
    """
    Factory para componentes de infraestructura
    Principio de Responsabilidad Única - solo creación de componentes
    """
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def crear_tablas(self) -> None:
        """Crear todas las tablas"""
        Base.metadata.create_all(bind=self.engine)
    
    def crear_session(self) -> Session:
        """Crear nueva sesión de base de datos"""
        return self.SessionLocal()
    
    def crear_unidad_trabajo(self) -> UnidadDeTrabajoComisiones:
        """Crear nueva unidad de trabajo"""
        session = self.crear_session()
        return UnidadDeTrabajoComisiones(session)
    
    def crear_repositorio_comisiones(self, session: Optional[Session] = None) -> RepositorioComisionesSQLAlchemy:
        """Crear repositorio de comisiones"""
        if session is None:
            session = self.crear_session()
        return RepositorioComisionesSQLAlchemy(session)
    
    def crear_repositorio_eventos(self, session: Optional[Session] = None) -> RepositorioEventosSQLAlchemy:
        """Crear repositorio de eventos"""
        if session is None:
            session = self.crear_session()
        return RepositorioEventosSQLAlchemy(session)