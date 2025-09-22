from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

# Comandos y Consultas
from campanias.modulos.aplicacion.comandos.crear_campana import (
    CrearCampana, ActivarCampana, AgregarAfiliadoACampana
)
from campanias.modulos.aplicacion.handlers import (
    ObtenerCampaniaPorId, ObtenerTodasLasCampanias, ObtenerCampaniasActivas
)

# Ejecutores
from campanias.seedwork.aplicacion.comandos import ejecutar_commando
from campanias.seedwork.aplicacion.queries import ejecutar_query

# DTOs y excepciones
from campanias.modulos.aplicacion.dto import CampañaDTO
from campanias.seedwork.dominio.excepciones import ExcepcionDominio

# ==========================================
# MODELOS PYDANTIC PARA API
# ==========================================

class CrearCampaniaRequest(BaseModel):
    """Modelo de request para crear una campaña"""
    nombre: str
    descripcion: str
    tipo_campana: str  # promocional, descuento, cashback
    canal_publicidad: str  # web, social_media, email, mobile_app, tv, radio
    objetivo_campana: str  # incrementar_ventas, fidelizar_clientes, captar_nuevos_clientes
    fecha_inicio: str  # ISO format
    fecha_fin: str     # ISO format
    presupuesto: float = 0.0
    moneda: str = "USD"
    codigo_campana: Optional[str] = None
    segmento_audiencia: Optional[str] = None

class ActivarCampaniaRequest(BaseModel):
    """Modelo de request para activar una campaña"""
    fecha_activacion: str  # ISO format

class AgregarAfiliadoRequest(BaseModel):
    """Modelo de request para agregar afiliado a campaña"""
    id_afiliado: str
    configuracion_afiliado: dict
    comision_aplicable: float = 0.0
    fecha_asignacion: str  # ISO format

class CampaniaResponse(BaseModel):
    """Modelo de respuesta para campanias"""
    id: str
    nombre: str
    descripcion: str
    tipo: str
    canal_publicidad: str
    objetivo: str
    fecha_inicio: str
    fecha_fin: str
    fecha_creacion: str
    fecha_actualizacion: str
    presupuesto: float
    moneda: str
    codigo_campana: Optional[str] = None
    segmento_audiencia: Optional[str] = None
    estado: str

# ==========================================
# ROUTER FASTAPI
# ==========================================

router = APIRouter(prefix="/campanias", tags=["campanias"])

# ==========================================
# ENDPOINTS DE COMANDOS (WRITE OPERATIONS)
# ==========================================

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
def crear_campania(request: CrearCampaniaRequest):
    """
    Crea una nueva campaña de marketing.
    
    Este endpoint dispara eventos para:
    - afiliados: notificación de nueva campaña disponible
    - comisiones: configuración de comisiones para la campaña
    - conversiones: setup de tracking para la campaña
    """
    try:
        # Generar ID único y timestamps
        id_campania = str(uuid.uuid4())
        timestamp_actual = datetime.now().isoformat()
        
        # Generar código si no se proporciona
        codigo_campana = request.codigo_campana or f"CAMP-{str(uuid.uuid4())[:8].upper()}"
        
        # Crear comando
        comando = CrearCampana(
            id=id_campania,
            fecha_creacion=timestamp_actual,
            fecha_actualizacion=timestamp_actual,
            nombre=request.nombre,
            descripcion=request.descripcion,
            tipo_campana=request.tipo_campana,
            canal_publicidad=request.canal_publicidad,
            objetivo_campana=request.objetivo_campana,
            fecha_inicio=request.fecha_inicio,
            fecha_fin=request.fecha_fin,
            presupuesto=request.presupuesto,
            moneda=request.moneda,
            codigo_campana=codigo_campana,
            segmento_audiencia=request.segmento_audiencia or "general"
        )
        
        # Ejecutar comando - DISPARA CampaniaCreada
        ejecutar_commando(comando)
        
        return {
            "mensaje": "Campaña creada exitosamente",
            "id": id_campania,
            "codigo_campana": codigo_campana,
            "eventos_enviados": ["eventos-campania::CampaniaCreada"]
        }
        
    except ExcepcionDominio as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.put("/{id_campania}/activar", response_model=dict)
def activar_campania(id_campania: str, request: ActivarCampaniaRequest):
    """
    Activa una campaña existente.
    
    Este endpoint dispara eventos para:
    - notificaciones: envío de notificaciones a afiliados
    - afiliados: activación de la campaña en sus sistemas
    """
    try:
        comando = ActivarCampana(
            id_campania=id_campania,
            fecha_activacion=request.fecha_activacion
        )
        
        # Ejecutar comando - DISPARA CampaniaActivada
        ejecutar_commando(comando)
        
        return {
            "mensaje": "Campaña activada exitosamente",
            "id": id_campania,
            "eventos_enviados": ["eventos-campania::CampaniaActivada"]
        }
        
    except ExcepcionDominio as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.put("/{id_campania}/afiliados", response_model=dict)
def agregar_afiliado_a_campania(id_campania: str, request: AgregarAfiliadoRequest):
    """
    Agrega un afiliado a una campaña específica.
    
    Este endpoint dispara eventos para:
    - afiliados: notificación de asignación a campaña
    - comisiones: configuración de comisiones específicas del afiliado
    """
    try:
        comando = AgregarAfiliadoACampana(
            id_campania=id_campania,
            id_afiliado=request.id_afiliado,
            configuracion_afiliado=request.configuracion_afiliado,
            comision_aplicable=request.comision_aplicable,
            fecha_asignacion=request.fecha_asignacion
        )
        
        # Ejecutar comando - DISPARA AfiliadoAgregadoACampania
        ejecutar_commando(comando)
        
        return {
            "mensaje": "Afiliado agregado a campaña exitosamente",
            "id_campania": id_campania,
            "id_afiliado": request.id_afiliado,
            "eventos_enviados": ["eventos-campania::AfiliadoAgregadoACampania"]
        }
        
    except ExcepcionDominio as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# ==========================================
# ENDPOINTS DE CONSULTAS (READ OPERATIONS)
# ==========================================

@router.get("/{id_campania}", response_model=CampaniaResponse)
def obtener_campania(id_campania: str):
    """Obtiene una campaña específica por su ID"""
    try:
        query = ObtenerCampaniaPorId(id_campania=id_campania)
        resultado = ejecutar_query(query)
        
        if not resultado.resultado:
            raise HTTPException(status_code=404, detail="Campaña no encontrada")
        
        campania_dto: CampañaDTO = resultado.resultado
        return CampaniaResponse(
            id=campania_dto.id,
            nombre=campania_dto.nombre,
            descripcion=campania_dto.descripcion,
            tipo=campania_dto.tipo,
            canal_publicidad=campania_dto.canal_publicidad,
            objetivo=campania_dto.objetivo,
            fecha_inicio=campania_dto.fecha_inicio,
            fecha_fin=campania_dto.fecha_fin,
            fecha_creacion=campania_dto.fecha_creacion,
            fecha_actualizacion=campania_dto.fecha_actualizacion,
            presupuesto=campania_dto.presupuesto,
            moneda=campania_dto.moneda,
            codigo_campana=campania_dto.codigo_campana,
            segmento_audiencia=campania_dto.segmento_audiencia,
            estado=campania_dto.estado
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/", response_model=List[CampaniaResponse])
def listar_campanias(
    estado: Optional[str] = None,
    tipo: Optional[str] = None
):
    """
    Lista todas las campanias con filtros opcionales.
    
    Parámetros:
    - estado: activa, pausada, finalizada, borrador
    - tipo: promocional, descuento, cashback
    """
    try:
        query = ObtenerTodasLasCampanias(estado=estado, tipo=tipo)
        resultado = ejecutar_query(query)
        
        campanias_dto: List[CampañaDTO] = resultado.resultado or []
        
        return [
            CampaniaResponse(
                id=campania.id,
                nombre=campania.nombre,
                descripcion=campania.descripcion,
                tipo=campania.tipo,
                canal_publicidad=campania.canal_publicidad,
                objetivo=campania.objetivo,
                fecha_inicio=campania.fecha_inicio,
                fecha_fin=campania.fecha_fin,
                fecha_creacion=campania.fecha_creacion,
                fecha_actualizacion=campania.fecha_actualizacion,
                presupuesto=campania.presupuesto,
                moneda=campania.moneda,
                codigo_campana=campania.codigo_campana,
                segmento_audiencia=campania.segmento_audiencia,
                estado=campania.estado
            )
            for campania in campanias_dto
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/activas/", response_model=List[CampaniaResponse])
def listar_campanias_activas(canal_publicidad: Optional[str] = None):
    """
    Lista todas las campanias activas con filtro opcional por canal.
    
    Parámetros:
    - canal_publicidad: web, social_media, email, mobile_app, tv, radio
    """
    try:
        query = ObtenerCampaniasActivas(canal_publicidad=canal_publicidad)
        resultado = ejecutar_query(query)
        
        campanias_dto: List[CampañaDTO] = resultado.resultado or []
        
        return [
            CampaniaResponse(
                id=campania.id,
                nombre=campania.nombre,
                descripcion=campania.descripcion,
                tipo=campania.tipo,
                canal_publicidad=campania.canal_publicidad,
                objetivo=campania.objetivo,
                fecha_inicio=campania.fecha_inicio,
                fecha_fin=campania.fecha_fin,
                fecha_creacion=campania.fecha_creacion,
                fecha_actualizacion=campania.fecha_actualizacion,
                presupuesto=campania.presupuesto,
                moneda=campania.moneda,
                codigo_campana=campania.codigo_campana,
                segmento_audiencia=campania.segmento_audiencia,
                estado=campania.estado
            )
            for campania in campanias_dto
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# ==========================================
# ENDPOINT DE HEALTH CHECK
# ==========================================

@router.get("/health", response_model=dict)
def health_check():
    """Health check para el servicio de campanias"""
    return {
        "servicio": "campanias",
        "estado": "activo",
        "version": "1.0.0",
        "eventos_soportados": [
            "CampaniaCreada",
            "CampaniaActivada", 
            "AfiliadoAgregadoACampania",
            "CampaniaEliminada"
        ]
    }