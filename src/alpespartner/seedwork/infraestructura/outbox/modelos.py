"""Modelo genérico de Outbox para todos los bounded contexts.

A futuro se puede complementar con soporte multi-tenancy, particionamiento
u optimizaciones específicas. Incluye campos de correlación para trazabilidad.
"""
from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, JSON, Boolean
from typing import Optional
from datetime import datetime

class OutboxBase(DeclarativeBase):
    pass

class OutboxEvent(OutboxBase):
    __tablename__='outbox_event'
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    aggregate_type:Mapped[str]=mapped_column(String(64), index=True)
    aggregate_id:Mapped[str]=mapped_column(String(36), index=True)
    event_type:Mapped[str]=mapped_column(String(64), index=True)
    payload:Mapped[dict]=mapped_column(JSON)
    occurred_at:Mapped[datetime]=mapped_column(DateTime, index=True)
    published:Mapped[bool]=mapped_column(Boolean,default=False, index=True)
    correlation_id:Mapped[Optional[str]]=mapped_column(String(36), nullable=True, index=True)
    causation_id:Mapped[Optional[str]]=mapped_column(String(36), nullable=True)

    def marcar_publicado(self):
        self.published = True
