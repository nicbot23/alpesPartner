from typing import Any, Dict, List, Optional
import asyncio
from datetime import datetime, timedelta
from ..clientes.campanias_cliente import cliente_campanias
from ...config import config


class SagasService:
    """Servicio para seguimiento y gestión de sagas"""
    
    def __init__(self):
        self._cache_estados = {}  # Cache simple para estados de saga
        self._cache_ttl = timedelta(seconds=config.intervalo_polling_saga)
    
    async def obtener_estado_saga(self, saga_id: str, usar_cache: bool = True) -> Dict[str, Any]:
        """
        Obtiene el estado actual de una saga
        """
        try:
            # Verificar cache si está habilitado
            if usar_cache and saga_id in self._cache_estados:
                entrada_cache = self._cache_estados[saga_id]
                if datetime.utcnow() - entrada_cache["timestamp"] < self._cache_ttl:
                    return entrada_cache["estado"]
            
            # Obtener estado del microservicio de campanias
            estado = await cliente_campanias.consultar_estado_saga(saga_id)
            
            # Actualizar cache
            if usar_cache:
                self._cache_estados[saga_id] = {
                    "estado": estado,
                    "timestamp": datetime.utcnow()
                }
            
            return estado
            
        except Exception as e:
            raise Exception(f"Error al obtener estado de saga {saga_id}: {str(e)}")
    
    async def obtener_progreso_detallado(self, saga_id: str) -> Dict[str, Any]:
        """
        Obtiene el progreso detallado de una saga con información de cada paso
        """
        try:
            progreso = await cliente_campanias.obtener_progreso_saga(saga_id)
            
            # Enriquecer con información adicional para el frontend
            pasos_procesados = []
            for paso in progreso.get("pasos", []):
                paso_enriquecido = {
                    **paso,
                    "tiempo_transcurrido": self._calcular_tiempo_transcurrido(paso),
                    "progreso_porcentaje": self._calcular_porcentaje_paso(paso)
                }
                pasos_procesados.append(paso_enriquecido)
            
            resultado = {
                **progreso,
                "pasos": pasos_procesados,
                "progreso_total": self._calcular_progreso_total(pasos_procesados),
                "tiempo_estimado_restante": self._estimar_tiempo_restante(pasos_procesados),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return resultado
            
        except Exception as e:
            raise Exception(f"Error al obtener progreso de saga {saga_id}: {str(e)}")
    
    async def monitorear_saga(
        self,
        saga_id: str,
        callback_progreso: Optional[callable] = None,
        timeout_segundos: int = None
    ) -> Dict[str, Any]:
        """
        Monitorea una saga hasta su completación o timeout
        Útil para casos donde el frontend necesita esperar el resultado
        """
        timeout = timeout_segundos or config.timeout_saga_segundos
        inicio = datetime.utcnow()
        
        while (datetime.utcnow() - inicio).total_seconds() < timeout:
            try:
                estado = await self.obtener_estado_saga(saga_id, usar_cache=False)
                
                # Llamar callback si se proporciona
                if callback_progreso:
                    await callback_progreso(estado)
                
                # Verificar si la saga terminó
                estado_saga = estado.get("estado")
                if estado_saga in ["COMPLETADA", "FALLIDA", "CANCELADA"]:
                    return {
                        "saga_id": saga_id,
                        "estado_final": estado_saga,
                        "tiempo_total": (datetime.utcnow() - inicio).total_seconds(),
                        "exito": estado_saga == "COMPLETADA",
                        "detalles": estado
                    }
                
                # Esperar antes del siguiente polling
                await asyncio.sleep(config.intervalo_polling_saga)
                
            except Exception as e:
                # En caso de error, intentar una vez más antes de fallar
                await asyncio.sleep(1)
                continue
        
        # Timeout alcanzado
        return {
            "saga_id": saga_id,
            "estado_final": "TIMEOUT",
            "tiempo_total": timeout,
            "exito": False,
            "mensaje": f"Saga no completada en {timeout} segundos"
        }
    
    async def cancelar_saga(self, saga_id: str, razon: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancela una saga en progreso
        """
        try:
            resultado = await cliente_campanias.cancelar_saga(saga_id)
            
            # Limpiar cache
            if saga_id in self._cache_estados:
                del self._cache_estados[saga_id]
            
            return {
                "exito": True,
                "saga_id": saga_id,
                "mensaje": "Saga cancelada exitosamente",
                "razon": razon,
                "timestamp": datetime.utcnow().isoformat(),
                "detalles": resultado
            }
            
        except Exception as e:
            return {
                "exito": False,
                "saga_id": saga_id,
                "error": str(e),
                "mensaje": "Error al cancelar saga",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def listar_sagas_activas(self) -> Dict[str, Any]:
        """
        Lista todas las sagas activas en el sistema
        """
        try:
            # Nota: Este endpoint tendría que existir en el microservicio de campanias
            # Por ahora simulamos la estructura
            sagas_activas = []
            
            return {
                "sagas": sagas_activas,
                "total": len(sagas_activas),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error al listar sagas activas: {str(e)}")
    
    def limpiar_cache(self):
        """Limpia el cache de estados de saga"""
        self._cache_estados.clear()
    
    # Métodos auxiliares privados
    def _calcular_tiempo_transcurrido(self, paso: Dict[str, Any]) -> Optional[float]:
        """Calcula el tiempo transcurrido para un paso"""
        try:
            if paso.get("fecha_inicio") and paso.get("fecha_fin"):
                inicio = datetime.fromisoformat(paso["fecha_inicio"].replace("Z", "+00:00"))
                fin = datetime.fromisoformat(paso["fecha_fin"].replace("Z", "+00:00"))
                return (fin - inicio).total_seconds()
            elif paso.get("fecha_inicio"):
                inicio = datetime.fromisoformat(paso["fecha_inicio"].replace("Z", "+00:00"))
                return (datetime.utcnow() - inicio).total_seconds()
            return None
        except:
            return None
    
    def _calcular_porcentaje_paso(self, paso: Dict[str, Any]) -> int:
        """Calcula el porcentaje de completitud de un paso"""
        estado = paso.get("estado", "").upper()
        if estado == "COMPLETADO":
            return 100
        elif estado == "EN_PROGRESO":
            return 50
        elif estado == "FALLIDO":
            return 0
        elif estado == "PENDIENTE":
            return 0
        else:
            return 0
    
    def _calcular_progreso_total(self, pasos: List[Dict[str, Any]]) -> int:
        """Calcula el progreso total de la saga"""
        if not pasos:
            return 0
        
        total_porcentaje = sum(paso.get("progreso_porcentaje", 0) for paso in pasos)
        return min(100, total_porcentaje // len(pasos))
    
    def _estimar_tiempo_restante(self, pasos: List[Dict[str, Any]]) -> Optional[float]:
        """Estima el tiempo restante para completar la saga"""
        try:
            pasos_completados = [p for p in pasos if p.get("progreso_porcentaje") == 100]
            pasos_pendientes = len(pasos) - len(pasos_completados)
            
            if pasos_pendientes == 0:
                return 0
            
            if pasos_completados:
                tiempo_promedio = sum(
                    p.get("tiempo_transcurrido", 0) for p in pasos_completados
                ) / len(pasos_completados)
                return tiempo_promedio * pasos_pendientes
            
            return None
        except:
            return None


# Instancia singleton del servicio
sagas_service = SagasService()