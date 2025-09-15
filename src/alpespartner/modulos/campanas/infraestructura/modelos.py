"""
Modelos de Infraestructura para Campañas (MySQL)
DTOs anémicos para persistencia, separados del modelo de dominio
"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Numeric, Text, JSON, Boolean
from datetime import datetime
from typing import Optional


class Base(DeclarativeBase):
    pass


class CampanaDTO(Base):
    """
    Modelo de persistencia para el agregado Campaña
    Mapea a MySQL con JSON para objetos valor complejos
    """
    __tablename__ = 'campanas'
    
    # Identificación
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Metadatos (desnormalizado para consultas rápidas)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    marca: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    
    # Período de vigencia (desnormalizado para consultas)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Términos de comisión (JSON para flexibilidad)
    terminos_comision: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Restricciones geográficas (JSON)
    restriccion_geografica: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Estado y timestamps
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default='BORRADOR', index=True)
    creada_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    activada_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finalizada_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Metadatos de auditoría
    version: Mapped[int] = mapped_column(Numeric, nullable=False, default=1)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f"<CampanaDTO(id='{self.id}', nombre='{self.nombre}', estado='{self.estado}')>"
