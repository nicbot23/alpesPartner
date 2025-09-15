from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CampanaBase(BaseModel):
    nombre: str = Field(..., description="Nombre de la campaña")
    descripcion: str = Field(..., description="Descripción de la campaña")
    tipo_campana: str = Field(..., description="Tipo de campaña (afiliacion, conversion, retention)")
    fecha_inicio: str = Field(..., description="Fecha de inicio en formato ISO")
    fecha_fin: str = Field(..., description="Fecha de fin en formato ISO")
    meta_conversiones: int = Field(..., description="Meta de conversiones")
    presupuesto: float = Field(..., description="Presupuesto de la campaña")


class CampanaCrear(CampanaBase):
    created_by: str = Field(..., description="ID del usuario que crea la campaña")


class CampanaActualizar(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre de la campaña")
    descripcion: Optional[str] = Field(None, description="Descripción de la campaña")
    fecha_inicio: Optional[str] = Field(None, description="Fecha de inicio")
    fecha_fin: Optional[str] = Field(None, description="Fecha de fin")
    meta_conversiones: Optional[int] = Field(None, description="Meta de conversiones")
    presupuesto: Optional[float] = Field(None, description="Presupuesto")


class CampanaResponse(CampanaBase):
    id: str = Field(..., description="ID único de la campaña")
    estado: str = Field(..., description="Estado de la campaña (creada, activa, pausada, finalizada)")
    created_by: str = Field(..., description="ID del usuario que creó la campaña")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")

    class Config:
        from_attributes = True


class CampanaListResponse(BaseModel):
    campanas: List[CampanaResponse]
    total: int
    page: int
    size: int


class ActivarCampanaRequest(BaseModel):
    criterios_segmentacion: str = Field(..., description="Criterios de segmentación en JSON")


class ComisionResponse(BaseModel):
    id: str
    campana_id: str
    afiliado_id: str
    conversion_id: str
    monto_comision: float
    porcentaje_comision: float
    fecha_calculo: str
    estado: str


class ComisionListResponse(BaseModel):
    comisiones: List[ComisionResponse]
    total: int
    total_monto: float
    page: int
    size: int


class EstadisticasCampanaResponse(BaseModel):
    campana_id: str
    total_conversiones: int
    total_comisiones: float
    valor_total_conversiones: float
    afiliados_participantes: int
    tasa_conversion: float


class MessageResponse(BaseModel):
    message: str