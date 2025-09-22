"""
🎭 API REST para monitoreo de Sagas (alineada con SagaLoggerV2)
- GET /sagas/{saga_id}           → snapshot (estado/fechas/finalizada)
- GET /sagas/{saga_id}/progreso  → detalle (saga + pasos)
- GET /sagas/{saga_id}/estado    → estado ultra-rápido (para polling)
- GET /sagas/{saga_id}/pasos     → lista de pasos (con duración por paso)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import os

from campanias.sagas.saga_logger_v2 import SagaLoggerV2

router = APIRouter(prefix="/sagas", tags=["Sagas - Monitoreo"])

# Instancia del logger (usa DATABASE_URL / SAGAS_DATABASE_URL configuradas)
storage_type = os.getenv("SAGAS_STORAGE_TYPE", "sqlite")
saga_logger = SagaLoggerV2(storage_type=storage_type)

# ---------------------------
# Helpers
# ---------------------------
def _calc_duracion_s(seg_ini: Optional[str], seg_fin: Optional[str]) -> Optional[float]:
    if not seg_ini or not seg_fin:
        return None
    try:
        ini = datetime.fromisoformat(seg_ini.replace("Z", ""))
        fin = datetime.fromisoformat(seg_fin.replace("Z", ""))
        return (fin - ini).total_seconds()
    except Exception:
        return None

def _calc_progreso(pasos: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not pasos:
        return {"pasos_totales": 0, "pasos_completados": 0, "porcentaje": 0.0}
    total = len(pasos)
    completos = sum(1 for p in pasos if str(p.get("estado", "")).upper() in {"OK", "COMPENSADO"})
    return {
        "pasos_totales": total,
        "pasos_completados": completos,
        "porcentaje": round((completos / total) * 100, 1) if total else 0.0
    }

# ---------------------------
# Endpoints
# ---------------------------

@router.get("/{saga_id}")
def obtener_saga(saga_id: str) -> Dict[str, Any]:
    """
    Snapshot de la saga: estado, fechas y si está finalizada.
    """
    try:
        data = saga_logger.obtener_estado_saga(saga_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"Saga {saga_id} no encontrada")

        # Enriquecemos con progreso porcentual
        prog = saga_logger.obtener_progreso_detallado(saga_id) or {}
        pasos = prog.get("pasos", [])
        progreso = _calc_progreso(pasos)

        return {
            **data,                # {"saga_id","nombre","estado","fecha_inicio","fecha_fin","finalizada"}
            "progreso": progreso,  # {"pasos_totales","pasos_completados","porcentaje"}
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error obteniendo saga {saga_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{saga_id}/progreso")
def obtener_progreso_saga(saga_id: str) -> Dict[str, Any]:
    """
    Detalle completo: estado + lista de pasos con timestamps y detalle.
    """
    try:
        data = saga_logger.obtener_progreso_detallado(saga_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"Saga {saga_id} no encontrada")

        # añadir duración por paso
        pasos = data.get("pasos", [])
        for p in pasos:
            p["duracion_segundos"] = _calc_duracion_s(p.get("fecha_inicio"), p.get("fecha_fin"))

        # añadir progreso porcentual
        data["progreso"] = _calc_progreso(pasos)
        return data
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error obteniendo progreso de saga {saga_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{saga_id}/estado")
def obtener_estado_saga(saga_id: str) -> Dict[str, str]:
    """
    Endpoint ultra-rápido para polling desde el BFF (solo estado).
    """
    try:
        data = saga_logger.obtener_estado_saga(saga_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"Saga {saga_id} no encontrada")
        return {"estado": data.get("estado")}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error obteniendo estado de saga {saga_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{saga_id}/pasos")
def obtener_pasos_saga(saga_id: str) -> List[Dict[str, Any]]:
    """
    Lista de pasos con duración por paso (cuando aplique).
    """
    try:
        data = saga_logger.obtener_progreso_detallado(saga_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"Saga {saga_id} no encontrada")
        pasos = data.get("pasos", [])
        for p in pasos:
            p["duracion_segundos"] = _calc_duracion_s(p.get("fecha_inicio"), p.get("fecha_fin"))
        return pasos
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error obteniendo pasos de saga {saga_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))







### ------ CODIGO NO SOPORTADO

# from fastapi import APIRouter, HTTPException, Query
# from typing import List, Dict, Any, Optional
# from datetime import datetime, timedelta
# import logging
# import os
# from campanias.sagas.saga_logger_v2 import SagaLoggerV2
# #from campanias.sagas import SagaLogger

# # ==========================================
# # CONFIGURACIÓN DEL ROUTER
# # ==========================================

# router = APIRouter(
#     prefix="/sagas",
#     tags=["Sagas - Monitoreo"]
# )

# # Instancia del logger para consultas (híbrido MySQL/SQLite)
# storage_type = os.getenv("SAGAS_STORAGE_TYPE", "sqlite")
# saga_logger = SagaLoggerV2(storage_type=storage_type)

# # ==========================================
# # ENDPOINTS DE CONSULTA INDIVIDUAL
# # ==========================================

# @router.get("/{saga_id}")
# async def obtener_saga(saga_id: str) -> Dict[str, Any]:
#     """
#     📋 Obtiene información completa de una saga específica.
    
#     **Uso desde BFF:**
#     ```python
#     respuesta = requests.get(f"http://campanias:8000/sagas/{saga_id}")
#     estado_saga = respuesta.json()
#     ```
    
#     **Respuesta:**
#     ```json
#     {
#         "saga_id": "uuid-de-la-saga",
#         "estado": "ejecutando", 
#         "tipo_saga": "lanzar_campania_completa",
#         "fecha_inicio": "2024-01-15T10:30:00",
#         "fecha_fin": null,
#         "descripcion": "Saga completa para campaña: Campaña Navidad",
#         "datos_entrada": { ... },
#         "mensaje_error": null,
#         "progreso": {
#             "pasos_totales": 4,
#             "pasos_completados": 2, 
#             "porcentaje": 50.0
#         }
#     }
#     ```
#     """
#     try:
#         saga = saga_logger.obtener_saga(saga_id)
        
#         if not saga:
#             raise HTTPException(
#                 status_code=404, 
#                 detail=f"Saga {saga_id} no encontrada"
#             )
        
#         # Convertir RegistroSaga a dict para respuesta API
#         return {
#             "saga_id": getattr(saga, "saga_id", None),
#             "estado": getattr(saga, "estado", None).value if getattr(saga, "estado", None) else None,
#             "tipo": getattr(saga, "tipo", None),
#             "timestamp_inicio": getattr(saga, "fecha_inicio", None).isoformat() if getattr(saga, "fecha_inicio", None) else None,
#             "timestamp_fin": getattr(saga, "fecha_fin", None).isoformat() if getattr(saga, "fecha_fin", None) else None,
#             "duracion_total_segundos": getattr(saga, "duracion_total_segundos", None),
#             "campania_id": getattr(saga, "campania_id", None),
#             "usuario_id": getattr(saga, "usuario_id", None),
#             "metadatos": getattr(saga, "metadatos", None),
#             "progreso": {
#                 "estado": getattr(saga, "estado", None).value if getattr(saga, "estado", None) else None,
#                 "duracion_segundos": getattr(saga, "duracion_total_segundos", None) or 0
#             }
#         }
        
#     except Exception as e:
#         logging.error(f"Error obteniendo saga {saga_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/{saga_id}/pasos")
# async def obtener_pasos_saga(saga_id: str) -> List[Dict[str, Any]]:
#     """
#     📝 Obtiene todos los pasos de una saga con su estado actual.
    
#     **Uso desde BFF:**
#     ```python
#     respuesta = requests.get(f"http://campanias:8000/sagas/{saga_id}/pasos")
#     pasos = respuesta.json()
#     ```
    
#     **Respuesta:**
#     ```json
#     [
#         {
#             "paso_id": 1,
#             "nombre_paso": "solicitar_afiliados_elegibles",
#             "servicio_destino": "afiliados", 
#             "estado": "completado",
#             "fecha_inicio": "2024-01-15T10:30:15",
#             "fecha_fin": "2024-01-15T10:30:18",
#             "topico_pulsar": "comando-buscar-afiliados-elegibles",
#             "datos_entrada": { ... },
#             "datos_salida": { ... },
#             "mensaje_error": null,
#             "duracion_segundos": 3.2
#         }
#     ]
#     ```
#     """
#     try:
#         # Verificar que la saga existe
#         saga = saga_logger.obtener_saga(saga_id)
#         if not saga:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Saga {saga_id} no encontrada"
#             )
        
#         pasos = saga_logger.obtener_pasos_saga(saga_id)
        
#         # Enriquecer cada paso con información calculada
#         pasos_enriquecidos = []
#         for paso in pasos:
#             paso_enriquecido = dict(paso)
            
#             # Calcular duración si está completado
#             if paso["fecha_inicio"] and paso["fecha_fin"]:
#                 inicio = datetime.fromisoformat(paso["fecha_inicio"])
#                 fin = datetime.fromisoformat(paso["fecha_fin"])
#                 paso_enriquecido["duracion_segundos"] = (fin - inicio).total_seconds()
#             else:
#                 paso_enriquecido["duracion_segundos"] = None
                
#             pasos_enriquecidos.append(paso_enriquecido)
        
#         return pasos_enriquecidos
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logging.error(f"Error obteniendo pasos de saga {saga_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# # ==========================================
# # ENDPOINTS DE CONSULTA MASIVA 
# # ==========================================

# @router.get("/")
# async def listar_sagas(
#     estado: Optional[str] = Query(None, description="Filtrar por estado: iniciada, ejecutando, completada, fallida, etc."),
#     tipo_saga: Optional[str] = Query(None, description="Filtrar por tipo: lanzar_campania_completa, etc."), 
#     limite: int = Query(50, description="Máximo número de sagas a retornar"),
#     desde: Optional[datetime] = Query(None, description="Fecha inicio filtro (ISO format)")
# ) -> List[Dict[str, Any]]:
#     """
#     📊 Lista sagas con filtros opcionales para el dashboard del BFF.
    
#     **Uso desde BFF:**
#     ```python
#     # Todas las sagas ejecutándose
#     respuesta = requests.get("http://campanias:8000/sagas?estado=ejecutando")
    
#     # Sagas de hoy
#     respuesta = requests.get("http://campanias:8000/sagas?desde=2024-01-15T00:00:00")
    
#     # Solo lanzamientos de campanias
#     respuesta = requests.get("http://campanias:8000/sagas?tipo_saga=lanzar_campania_completa")
#     ```
#     """
#     try:
#         sagas = saga_logger.listar_sagas(
#             estado=estado,
#             tipo_saga=tipo_saga, 
#             limite=limite,
#             desde=desde
#         )
        
#         # Enriquecer cada saga con progreso
#         sagas_enriquecidas = []
#         for saga in sagas:
#             pasos = saga_logger.obtener_pasos_saga(saga["saga_id"])
#             progreso = _calcular_progreso_saga(pasos)
            
#             saga_enriquecida = dict(saga)
#             saga_enriquecida["progreso"] = progreso
#             sagas_enriquecidas.append(saga_enriquecida)
            
#         return sagas_enriquecidas
        
#     except Exception as e:
#         logging.error(f"Error listando sagas: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/estadisticas")
# async def obtener_estadisticas_sagas() -> Dict[str, Any]:
#     """
#     📈 Estadísticas generales de sagas para dashboard del BFF.
    
#     **Uso desde BFF:**
#     ```python
#     respuesta = requests.get("http://campanias:8000/sagas/estadisticas")
#     stats = respuesta.json()
#     ```
    
#     **Respuesta:**
#     ```json
#     {
#         "total_sagas": 150,
#         "por_estado": {
#             "ejecutando": 5,
#             "completada": 120, 
#             "fallida": 10,
#             "compensada": 15
#         },
#         "promedio_duracion_minutos": 8.5,
#         "tasa_exito": 85.7,
#         "sagas_ultimo_dia": 25
#     }
#     ```
#     """
#     try:
#         estadisticas = saga_logger.obtener_estadisticas()
#         return estadisticas
        
#     except Exception as e:
#         logging.error(f"Error obteniendo estadísticas: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# # ==========================================
# # ENDPOINTS DE MONITOREO EN TIEMPO REAL
# # ==========================================

# @router.get("/{saga_id}/estado")
# async def obtener_estado_saga(saga_id: str) -> Dict[str, str]:
#     """
#     ⚡ Endpoint ULTRA-RÁPIDO para polling del estado de saga.
#     Solo retorna el estado actual sin datos adicionales.
    
#     **Uso desde BFF (polling cada 2 segundos):**
#     ```python
#     respuesta = requests.get(f"http://campanias:8000/sagas/{saga_id}/estado")
#     estado = respuesta.json()["estado"]
#     ```
#     """
#     try:
#         saga = saga_logger.obtener_saga(saga_id)
#         if not saga:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Saga {saga_id} no encontrada"
#             )
#         return {"estado": saga.estado.value if hasattr(saga, "estado") and saga.estado else None}
#     except HTTPException:
#         raise
#     except Exception as e:
#         logging.error(f"Error obteniendo estado de saga {saga_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/activas")
# async def obtener_sagas_activas() -> List[Dict[str, Any]]:
#     """
#     🔄 Obtiene todas las sagas que están actualmente ejecutándose.
#     Útil para monitoreo en tiempo real desde el BFF.
    
#     **Uso desde BFF:**
#     ```python
#     respuesta = requests.get("http://campanias:8000/sagas/activas")
#     sagas_activas = respuesta.json()
#     ```
#     """
#     try:
#         sagas_activas = saga_logger.obtener_sagas_activas()
        
#         # Convertir RegistroSaga a dict para respuesta API
#         return [
#             {
#                 "saga_id": saga.saga_id,
#                 "estado": saga.estado.value,
#                 "tipo": saga.tipo,
#                 "timestamp_inicio": saga.timestamp_inicio.isoformat() if saga.timestamp_inicio else None,
#                 "timestamp_fin": saga.timestamp_fin.isoformat() if saga.timestamp_fin else None,
#                 "duracion_total_segundos": saga.duracion_total_segundos,
#                 "campania_id": saga.campania_id,
#                 "usuario_id": saga.usuario_id,
#                 "metadatos": saga.metadatos
#             } for saga in sagas_activas
#         ]
        
#     except Exception as e:
#         logging.error(f"Error obteniendo sagas activas: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# # ==========================================
# # FUNCIONES AUXILIARES
# # ==========================================

# def _calcular_progreso_saga(pasos: List[Dict[str, Any]]) -> Dict[str, Any]:
#     """
#     Calcula el progreso de una saga basado en sus pasos.
#     """
#     if not pasos:
#         return {
#             "pasos_totales": 0,
#             "pasos_completados": 0,
#             "porcentaje": 0.0
#         }
    
#     pasos_completados = len([p for p in pasos if p["estado"] == "completado"])
#     pasos_totales = len(pasos)
#     porcentaje = (pasos_completados / pasos_totales) * 100 if pasos_totales > 0 else 0
    
#     return {
#         "pasos_totales": pasos_totales,
#         "pasos_completados": pasos_completados, 
#         "porcentaje": round(porcentaje, 1)
#     }