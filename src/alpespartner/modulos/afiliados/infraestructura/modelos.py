"""
Modelos de infraestructura para Afiliados - Base de datos separada
"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Text, Numeric, Integer, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any
import json


class AfiliadosBase(DeclarativeBase):
    """Base separada para el microservicio Afiliados"""
    pass


class AfiliadoDTO(AfiliadosBase):
    """DTO para persistencia del agregado Afiliado"""
    
    __tablename__ = 'afiliados'
    
    # Identidad
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Datos personales
    nombres: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(100))
    fecha_nacimiento: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Documento de identidad
    tipo_documento: Mapped[str] = mapped_column(String(20))
    numero_documento: Mapped[str] = mapped_column(String(50), unique=True)
    fecha_expedicion_documento: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Datos de contacto
    email: Mapped[str] = mapped_column(String(255), unique=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ciudad: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pais: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Tipo y estado
    tipo_afiliado: Mapped[str] = mapped_column(String(20))
    estado: Mapped[str] = mapped_column(String(20), default='PENDIENTE')
    
    # Configuración de comisiones
    porcentaje_comision_base: Mapped[Decimal] = mapped_column(Numeric(5, 4))
    porcentaje_comision_premium: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    monto_minimo_comision: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Datos bancarios (opcionales)
    banco: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tipo_cuenta: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    numero_cuenta: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    titular_cuenta: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Sistema de referencias
    codigo_referencia: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    afiliado_referente_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Metadatos adicionales (JSON como Text)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Auditoría
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    fecha_actualizacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    
    # Versionado optimista
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Campos de correlación para eventos
    correlation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    causation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Relación con referencias
    referencias: Mapped[list["ReferenciaDTO"]] = relationship(
        "ReferenciaDTO", 
        foreign_keys="ReferenciaDTO.afiliado_referente_id",
        back_populates="afiliado_referente"
    )
    
    # Índices
    __table_args__ = (
        Index('idx_afiliados_documento', 'tipo_documento', 'numero_documento'),
        Index('idx_afiliados_email', 'email'),
        Index('idx_afiliados_estado', 'estado'),
        Index('idx_afiliados_tipo', 'tipo_afiliado'),
        Index('idx_afiliados_referente', 'afiliado_referente_id'),
        Index('idx_afiliados_codigo_ref', 'codigo_referencia'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el DTO a diccionario."""
        metadata_dict = {}
        if self.metadata:
            try:
                metadata_dict = json.loads(self.metadata)
            except (json.JSONDecodeError, TypeError):
                metadata_dict = {}
        
        return {
            'id': self.id,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'tipo_documento': self.tipo_documento,
            'numero_documento': self.numero_documento,
            'fecha_expedicion_documento': self.fecha_expedicion_documento.isoformat() if self.fecha_expedicion_documento else None,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'pais': self.pais,
            'tipo_afiliado': self.tipo_afiliado,
            'estado': self.estado,
            'porcentaje_comision_base': float(self.porcentaje_comision_base) if self.porcentaje_comision_base else None,
            'porcentaje_comision_premium': float(self.porcentaje_comision_premium) if self.porcentaje_comision_premium else None,
            'monto_minimo_comision': float(self.monto_minimo_comision) if self.monto_minimo_comision else None,
            'banco': self.banco,
            'tipo_cuenta': self.tipo_cuenta,
            'numero_cuenta': self.numero_cuenta,
            'titular_cuenta': self.titular_cuenta,
            'codigo_referencia': self.codigo_referencia,
            'afiliado_referente_id': self.afiliado_referente_id,
            'metadata': metadata_dict,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'version': self.version,
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id
        }


class ReferenciaDTO(AfiliadosBase):
    """DTO para persistencia de Referencias entre afiliados"""
    
    __tablename__ = 'referencias_afiliados'
    
    # Identidad
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Relaciones
    afiliado_referente_id: Mapped[str] = mapped_column(String(36), ForeignKey('afiliados.id'))
    afiliado_referido_id: Mapped[str] = mapped_column(String(36))
    
    # Estado de la referencia
    estado: Mapped[str] = mapped_column(String(20), default='ACTIVA')
    
    # Auditoría
    fecha_referencia: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    fecha_actualizacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
    
    # Relación hacia el afiliado referente
    afiliado_referente: Mapped["AfiliadoDTO"] = relationship(
        "AfiliadoDTO", 
        foreign_keys=[afiliado_referente_id],
        back_populates="referencias"
    )
    
    # Índices
    __table_args__ = (
        Index('idx_referencias_referente', 'afiliado_referente_id'),
        Index('idx_referencias_referido', 'afiliado_referido_id'),
        Index('idx_referencias_estado', 'estado'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el DTO a diccionario."""
        return {
            'id': self.id,
            'afiliado_referente_id': self.afiliado_referente_id,
            'afiliado_referido_id': self.afiliado_referido_id,
            'estado': self.estado,
            'fecha_referencia': self.fecha_referencia.isoformat() if self.fecha_referencia else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class OutboxAfiliadosDTO(AfiliadosBase):
    """DTO para el patrón Outbox de eventos de Afiliados"""
    
    __tablename__ = 'outbox_afiliados'
    
    # Identidad del evento
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Metadatos del evento
    tipo_evento: Mapped[str] = mapped_column(String(100))
    agregado_id: Mapped[str] = mapped_column(String(36))
    agregado_tipo: Mapped[str] = mapped_column(String(50), default='Afiliado')
    
    # Datos del evento (JSON como Text)
    datos_evento: Mapped[str] = mapped_column(Text)
    
    # Estado del evento
    procesado: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Correlación y causación
    correlation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    causation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Auditoría
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    fecha_procesamiento: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Índices para consultas eficientes
    __table_args__ = (
        Index('idx_outbox_afiliados_procesado', 'procesado'),
        Index('idx_outbox_afiliados_tipo', 'tipo_evento'),
        Index('idx_outbox_afiliados_agregado', 'agregado_id'),
        Index('idx_outbox_afiliados_fecha', 'fecha_creacion'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el DTO a diccionario."""
        datos_dict = {}
        if self.datos_evento:
            try:
                datos_dict = json.loads(self.datos_evento)
            except (json.JSONDecodeError, TypeError):
                datos_dict = {}
        
        return {
            'id': self.id,
            'tipo_evento': self.tipo_evento,
            'agregado_id': self.agregado_id,
            'agregado_tipo': self.agregado_tipo,
            'datos_evento': datos_dict,
            'procesado': self.procesado,
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_procesamiento': self.fecha_procesamiento.isoformat() if self.fecha_procesamiento else None
        }