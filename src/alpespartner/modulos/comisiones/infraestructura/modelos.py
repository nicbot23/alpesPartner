from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Numeric, DateTime, JSON, Boolean
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase): pass

class Commission(Base):
    __tablename__='commission'
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    conversion_id:Mapped[str]=mapped_column(String(36),unique=True)
    affiliate_id:Mapped[str]=mapped_column(String(64))
    campaign_id:Mapped[str]=mapped_column(String(64))
    gross_amount:Mapped[float]=mapped_column(Numeric(12,2))
    gross_currency:Mapped[str]=mapped_column(String(3))
    percentage:Mapped[float]=mapped_column(Numeric(5,2))
    net_amount:Mapped[float]=mapped_column(Numeric(12,2))
    net_currency:Mapped[str]=mapped_column(String(3))
    status:Mapped[str]=mapped_column(String(16))
    calculated_at:Mapped[datetime]=mapped_column(DateTime)
    approved_at:Mapped[Optional[datetime]]=mapped_column(DateTime,nullable=True)

class OutboxEvent(Base):
    __tablename__='outbox_event'
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    aggregate_type:Mapped[str]=mapped_column(String(64))
    aggregate_id:Mapped[str]=mapped_column(String(36))
    event_type:Mapped[str]=mapped_column(String(64))
    payload:Mapped[dict]=mapped_column(JSON)
    occurred_at:Mapped[datetime]=mapped_column(DateTime)
    published:Mapped[bool]=mapped_column(Boolean,default=False)
