"""
Modelos de infraestructura para Conversiones - Base de datos separada
"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Numeric, Text, Boolean, JSON, Index
from datetime import datetime
from decimal import Decimal
from typing import Optional


class ConversionesBase(DeclarativeBase):
    """Base separada para el microservicio Conversiones"""
    pass


class ConversionDTO(ConversionesBase):
    """DTO para persistencia del agregado Conversion"""
    __tablename__ = 'conversions'
    
    # Identidad
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Datos básicos
    conversion_type: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default='PENDIENTE')
    
    # Datos afiliado
    affiliate_id: Mapped[str] = mapped_column(String(36), nullable=False)
    affiliate_type: Mapped[str] = mapped_column(String(20), nullable=False)
    tier_level: Mapped[str] = mapped_column(String(20), nullable=False, default='STANDARD')
    
    # Datos campaña
    campaign_id: Mapped[str] = mapped_column(String(36), nullable=False)
    campaign_name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Datos transacción
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Metadatos (JSON para flexibilidad)
    metadatos: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Validación y atribución
    validation_score: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=0.0)
    attribution_model: Mapped[str] = mapped_column(String(20), nullable=False, default='LAST_CLICK')
    
    # Auditoría
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    
    # Índices para performance
    __table_args__ = (
        Index('idx_conversions_affiliate', 'affiliate_id'),
        Index('idx_conversions_campaign', 'campaign_id'),
        Index('idx_conversions_estado', 'estado'),
        Index('idx_conversions_created', 'created_at'),
        Index('idx_conversions_confirmed', 'confirmed_at'),
        Index('idx_conversions_tipo', 'conversion_type'),
        Index('idx_conversions_brand', 'brand'),
        Index('idx_conversions_transaction', 'transaction_id'),
    )


# Outbox separado para Conversiones (alternativa: usar outbox compartido)
class ConversionOutboxEvent(ConversionesBase):
    """Outbox events específico para Conversiones (descentralización completa)"""
    __tablename__ = 'conversion_outbox_events'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    aggregate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    causation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Campos de retry para descentralización completa
    attempts: Mapped[int] = mapped_column(nullable=False, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    dead_letter: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    __table_args__ = (
        Index('idx_conv_outbox_agg_type', 'aggregate_type'),
        Index('idx_conv_outbox_agg_id', 'aggregate_id'),
        Index('idx_conv_outbox_event_type', 'event_type'),
        Index('idx_conv_outbox_published', 'published'),
        Index('idx_conv_outbox_correlation', 'correlation_id'),
        Index('idx_conv_outbox_retry', 'next_retry_at'),
        Index('idx_conv_outbox_occurred', 'occurred_at'),
    )