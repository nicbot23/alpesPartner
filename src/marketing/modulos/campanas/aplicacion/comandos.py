"""Comandos de aplicación para Campañas"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

@dataclass
class CrearCampanaCommand:
    nombre: str
    descripcion: str
    tipo_campana: str = "PROMOCIONAL"
    fecha_inicio: str = "2024-01-01"
    fecha_fin: str = "2024-12-31"
    meta_conversiones: int = 100
    presupuesto: float = 0.0
    comision_porcentaje: float = 0.05
    marca: str = "ALPES"
    categoria: str = "MARKETING"
    tags: List[str] = field(default_factory=list)
    afiliados: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None

    def ensure_defaults(self):
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())

@dataclass
class ResultadoCrearCampana:
    campaign_id: str
    eventos_publicados: List[str]
    creado_en: str
    correlation_id: str
