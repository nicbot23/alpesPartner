from typing import Any, Dict, List, Optional
import asyncio
from datetime import datetime, timedelta
from ..clientes.campanias_cliente import cliente_campanias
from ..clientes.otros_clientes import (
    cliente_afiliados,
    cliente_comisiones,
    cliente_conversiones,
    cliente_notificaciones
)
from ...despachadores import despachador_bff


class CampaniasService:
    """Servicio de agregación para campanias que combina datos de múltiples microservicios"""
    
    async def obtener_campania_completa(self, campania_id: str) -> Dict[str, Any]:
        """
        Obtiene información completa de una campaña agregando datos de todos los microservicios
        """
        try:
            # Obtener información básica de la campaña
            campania = await cliente_campanias.obtener_campania(campania_id)
            
            # Obtener datos relacionados en paralelo
            tareas = [
                self._obtener_afiliados_campania(campania_id),
                self._obtener_metricas_conversiones(campania_id),
                self._obtener_resumen_comisiones(campania_id)
            ]
            
            afiliados, metricas, comisiones = await asyncio.gather(*tareas, return_exceptions=True)
            
            # Construir respuesta agregada
            respuesta = {
                "campania": campania,
                "afiliados": afiliados if not isinstance(afiliados, Exception) else [],
                "metricas": metricas if not isinstance(metricas, Exception) else {},
                "comisiones": comisiones if not isinstance(comisiones, Exception) else {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return respuesta
            
        except Exception as e:
            raise Exception(f"Error al obtener campaña completa: {str(e)}")
    
    async def listar_campanias_con_resumen(
        self,
        estado: Optional[str] = None,
        tipo: Optional[str] = None,
        incluir_metricas: bool = True
    ) -> Dict[str, Any]:
        """
        Lista campanias con resumen de métricas de cada una
        """
        try:
            # Obtener lista de campanias
            campanias_response = await cliente_campanias.listar_campanias(
                estado=estado,
                tipo=tipo
            )
            
            campanias = campanias_response.get("campanias", [])
            
            if incluir_metricas and campanias:
                # Obtener métricas para todas las campanias en paralelo
                tareas_metricas = [
                    self._obtener_metricas_conversiones(campania["id"])
                    for campania in campanias
                ]
                
                metricas_resultados = await asyncio.gather(*tareas_metricas, return_exceptions=True)
                
                # Combinar campanias con sus métricas
                for i, campania in enumerate(campanias):
                    metricas = metricas_resultados[i]
                    if not isinstance(metricas, Exception):
                        campania["metricas"] = metricas
                    else:
                        campania["metricas"] = {}
            
            return {
                "campanias": campanias,
                "total": len(campanias),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error al listar campanias con resumen: {str(e)}")
    
    async def lanzar_campania_completa(self, datos_campania: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lanza una campaña completa enviando comando via Pulsar al microservicio de campanias.
        AHORA USA EVENTOS EN LUGAR DE HTTP - Arquitectura corregida.
        """
        try:
            # 🎯 ENVIAR COMANDO VIA PULSAR (NO HTTP)
            resultado = despachador_bff.lanzar_campania_completa(datos_campania)
            
            if resultado["exito"]:
                return {
                    "exito": True,
                    "comando_id": resultado["comando_id"],
                    "mensaje": "Comando de campaña completa enviado exitosamente via Pulsar",
                    "topico": "comando-lanzar-campania-completa",
                    "timestamp": resultado["timestamp"],
                    "nota": "La saga se iniciará cuando campanias procese el comando"
                }
            else:
                return {
                    "exito": False,
                    "error": resultado.get("error", "Error desconocido"),
                    "mensaje": "Error al enviar comando via Pulsar",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "exito": False,
                "error": str(e),
                "mensaje": "Error interno al lanzar campaña completa",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def obtener_dashboard_resumen(self) -> Dict[str, Any]:
        """
        Obtiene un resumen completo para el dashboard del frontend
        """
        try:
            # Obtener datos de todos los microservicios en paralelo
            tareas = [
                cliente_campanias.listar_campanias(),
                cliente_afiliados.listar_afiliados(activo=True),
                self._obtener_estadisticas_generales()
            ]
            
            campanias_resp, afiliados_resp, estadisticas = await asyncio.gather(
                *tareas, return_exceptions=True
            )
            
            # Procesar resultados
            campanias = campanias_resp.get("campanias", []) if not isinstance(campanias_resp, Exception) else []
            afiliados = afiliados_resp.get("afiliados", []) if not isinstance(afiliados_resp, Exception) else []
            
            # Calcular métricas del dashboard
            campanias_activas = len([c for c in campanias if c.get("estado") == "ACTIVA"])
            campanias_total = len(campanias)
            afiliados_activos = len(afiliados)
            
            return {
                "resumen": {
                    "campanias_activas": campanias_activas,
                    "campanias_total": campanias_total,
                    "afiliados_activos": afiliados_activos,
                    "rendimiento_general": estadisticas if not isinstance(estadisticas, Exception) else {}
                },
                "campanias_recientes": campanias[:5],  # Últimas 5 campanias
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error al obtener dashboard: {str(e)}")
    
    # Métodos auxiliares privados
    async def _obtener_afiliados_campania(self, campania_id: str) -> List[Dict[str, Any]]:
        """Obtiene los afiliados asociados a una campaña"""
        try:
            resultado = await cliente_campanias.listar_afiliados_campania(campania_id)
            return resultado.get("afiliados", [])
        except:
            return []
    
    async def _obtener_metricas_conversiones(self, campania_id: str) -> Dict[str, Any]:
        """Obtiene métricas de conversión de una campaña"""
        try:
            return await cliente_conversiones.obtener_metricas_campania(campania_id)
        except:
            return {}
    
    async def _obtener_resumen_comisiones(self, campania_id: str) -> Dict[str, Any]:
        """Obtiene resumen de comisiones de una campaña"""
        try:
            # Nota: Este endpoint tendría que existir en el microservicio de comisiones
            # Por ahora retornamos estructura vacía
            return {
                "total_comisiones": 0,
                "comisiones_pagadas": 0,
                "comisiones_pendientes": 0
            }
        except:
            return {}
    
    async def _obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del sistema"""
        try:
            # Agregar estadísticas de rendimiento general
            return {
                "conversion_promedio": 0.0,
                "ingresos_mes_actual": 0.0,
                "crecimiento_mensual": 0.0
            }
        except:
            return {}


# Instancia singleton del servicio
campanias_service = CampaniasService()