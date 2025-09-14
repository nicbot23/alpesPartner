from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import asyncio
import logging
from datetime import datetime

from ...comandos import ComandoCrearCampana
from ...despachadores import despachador
from ...utils import generar_uuid, time_millis

router = APIRouter()
logger = logging.getLogger(__name__)


class CampanaRequest(BaseModel):
    """Modelo para request de creación de campaña"""
    nombre: str
    descripcion: str
    tipo_campana: str = "DESCUENTO"
    fecha_inicio: str
    fecha_fin: str
    meta_conversiones: int = 100
    presupuesto: float
    afiliados: Optional[list[str]] = []  # Lista de IDs de afiliados
    comision_porcentaje: Optional[float] = 0.05  # 5% por defecto


class CampanaResponse(BaseModel):
    """Respuesta de creación de campaña"""
    success: bool
    campaign_id: str
    message: str
    data: dict


@router.get("/")
async def listar_campanas():
    """Listar todas las campañas"""
    try:
        # Simulación de datos - en producción vendría de la base de datos
        campanas = [
            {
                "id": "camp-001",
                "nombre": "Campaña Enero 2024", 
                "estado": "activa",
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-01-31",
                "presupuesto": 10000.0,
                "meta_conversiones": 500
            },
            {
                "id": "camp-002",
                "nombre": "Black Friday 2024",
                "estado": "programada", 
                "fecha_inicio": "2024-11-29",
                "fecha_fin": "2024-12-02",
                "presupuesto": 50000.0,
                "meta_conversiones": 2000
            }
        ]
        
        return {
            "message": "Lista de campañas de marketing",
            "total": len(campanas),
            "data": campanas
        }
    except Exception as e:
        logger.error(f"Error listando campañas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/", response_model=CampanaResponse)
async def crear_campana(request: CampanaRequest):
    """
    Crear nueva campaña de marketing
    
    Este endpoint desencadena todo el flujo de eventos:
    1. Crea la campaña
    2. Asigna afiliados automáticamente
    3. Configura comisiones
    4. Activa notificaciones
    """
    try:
        logger.info(f"Creando campaña: {request.nombre}")
        
        # Generar ID único para la campaña
        campaign_id = generar_uuid()
        
        # Crear comando para crear campaña
        comando = ComandoCrearCampana(
            id=generar_uuid(),
            nombre=request.nombre,
            descripcion=request.descripcion,
            tipo_campana=request.tipo_campana,
            fecha_inicio=request.fecha_inicio,
            fecha_fin=request.fecha_fin,
            meta_conversiones=request.meta_conversiones,
            presupuesto=request.presupuesto,
            created_by="api-user",
            timestamp=time_millis()
        )
        
        # Publicar comando (esto desencadenará eventos automáticamente)
        await despachador.publicar_comando_crear_campana(comando)
        
        logger.info(f"✅ Campaña creada: {campaign_id}")
        
        # Si se especificaron afiliados, enviar comandos de asignación
        if request.afiliados:
            logger.info(f"Asignando {len(request.afiliados)} afiliados a la campaña")
            
            for afiliado_id in request.afiliados:
                # En un escenario real, esto enviaría eventos de asignación
                logger.info(f"Afiliado {afiliado_id} asignado a campaña {campaign_id}")
        
        # Respuesta exitosa
        return CampanaResponse(
            success=True,
            campaign_id=campaign_id,
            message=f"Campaña '{request.nombre}' creada exitosamente",
            data={
                "campaign_id": campaign_id,
                "nombre": request.nombre,
                "presupuesto": request.presupuesto,
                "meta_conversiones": request.meta_conversiones,
                "afiliados_asignados": len(request.afiliados or []),
                "comision_porcentaje": request.comision_porcentaje,
                "fecha_creacion": datetime.now().isoformat(),
                "eventos_generados": [
                    "CampanaCreada",
                    "AfiliacionesConfiguradas" if request.afiliados else None,
                    "ComisionesConfiguradas"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"Error creando campaña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando campaña: {str(e)}"
        )


@router.post("/{campaign_id}/activate")
async def activar_campana(campaign_id: str):
    """Activar una campaña específica"""
    try:
        logger.info(f"Activando campaña: {campaign_id}")
        
        # Aquí se enviaría el comando de activación
        # que desencadenaría eventos de activación automáticamente
        
        return {
            "success": True,
            "message": f"Campaña {campaign_id} activada exitosamente",
            "events_triggered": [
                "CampanaActivada",
                "NotificacionesAfiliados",
                "ConfiguracionSegmentacion"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error activando campaña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activando campaña: {str(e)}"
        )


@router.get("/{campaign_id}/stats")
async def estadisticas_campana(campaign_id: str):
    """Obtener estadísticas de una campaña"""
    try:
        # Simulación de estadísticas
        stats = {
            "campaign_id": campaign_id,
            "conversiones_totales": 45,
            "comisiones_pagadas": 2250.0,
            "afiliados_activos": 8,
            "porcentaje_meta": 45.0,
            "eventos_procesados": [
                {"tipo": "ConversionDetected", "cantidad": 45},
                {"tipo": "ComisionCalculada", "cantidad": 45}, 
                {"tipo": "NotificacionEnviada", "cantidad": 53}
            ]
        }
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )