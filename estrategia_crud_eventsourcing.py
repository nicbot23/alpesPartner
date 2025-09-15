"""
Estrategia Híbrida CRUD + Event Sourcing
Implementación completa siguiendo recomendaciones entrega4

Este módulo define:
- CRUD para operaciones síncronas inmediatas
- Event Sourcing para comunicación inter-servicios
- Patrones de proyección para vistas optimizadas
- Manejo de comandos y eventos separados
"""

import json
import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class TipoOperacion(Enum):
    """Tipos de operaciones en el sistema híbrido"""
    CRUD_DIRECTO = "crud_directo"        # Operaciones síncronas directas a BD
    EVENT_SOURCING = "event_sourcing"    # Comunicación asíncrona entre servicios
    CQRS_QUERY = "cqrs_query"           # Consultas optimizadas
    CQRS_COMMAND = "cqrs_command"       # Comandos con eventos

class EstadoConsistencia(Enum):
    """Estados de consistencia de datos"""
    CONSISTENTE = "consistente"
    EVENTUAL = "eventual" 
    INCONSISTENTE = "inconsistente"

class StrategyPattern(ABC):
    """Patrón Strategy para seleccionar entre CRUD y Event Sourcing"""
    
    @abstractmethod
    async def ejecutar_operacion(self, operacion: Dict) -> Dict:
        pass
    
    @abstractmethod
    def es_aplicable(self, contexto: Dict) -> bool:
        pass

class CRUDStrategy(StrategyPattern):
    """
    Estrategia CRUD para operaciones síncronas inmediatas
    
    Casos de uso:
    - Consultas de lectura rápida
    - Operaciones dentro del mismo bounded context
    - Validaciones inmediatas
    - APIs REST tradicionales
    """
    
    def __init__(self, repository):
        self.repository = repository
    
    async def ejecutar_operacion(self, operacion: Dict) -> Dict:
        """Ejecuta operación CRUD directa"""
        try:
            metodo = operacion.get("metodo", "").upper()
            entidad = operacion.get("entidad")
            datos = operacion.get("datos", {})
            filtros = operacion.get("filtros", {})
            
            if metodo == "CREATE":
                resultado = await self.repository.crear(entidad, datos)
            elif metodo == "READ":
                resultado = await self.repository.leer(entidad, filtros)
            elif metodo == "UPDATE":
                resultado = await self.repository.actualizar(entidad, filtros, datos)
            elif metodo == "DELETE":
                resultado = await self.repository.eliminar(entidad, filtros)
            else:
                raise ValueError(f"Método CRUD no soportado: {metodo}")
            
            return {
                "success": True,
                "tipo_operacion": TipoOperacion.CRUD_DIRECTO.value,
                "consistencia": EstadoConsistencia.CONSISTENTE.value,
                "resultado": resultado,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en operación CRUD: {e}")
            return {
                "success": False,
                "tipo_operacion": TipoOperacion.CRUD_DIRECTO.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def es_aplicable(self, contexto: Dict) -> bool:
        """Determina si CRUD es la estrategia apropiada"""
        return (
            contexto.get("sincronismo_requerido", False) or
            contexto.get("mismo_bounded_context", False) or
            contexto.get("validacion_inmediata", False) or
            contexto.get("operacion_simple", False)
        )

class EventSourcingStrategy(StrategyPattern):
    """
    Estrategia Event Sourcing para comunicación asíncrona
    
    Casos de uso:
    - Comunicación entre microservicios
    - Flujos de trabajo complejos
    - Auditoría completa
    - Procesamiento eventual
    """
    
    def __init__(self, event_store, command_dispatcher, event_publisher):
        self.event_store = event_store
        self.command_dispatcher = command_dispatcher
        self.event_publisher = event_publisher
    
    async def ejecutar_operacion(self, operacion: Dict) -> Dict:
        """Ejecuta operación usando Event Sourcing"""
        try:
            tipo = operacion.get("tipo", "comando")
            
            if tipo == "comando":
                resultado = await self._procesar_comando(operacion)
            elif tipo == "evento":
                resultado = await self._procesar_evento(operacion)
            elif tipo == "consulta_eventos":
                resultado = await self._consultar_eventos(operacion)
            else:
                raise ValueError(f"Tipo Event Sourcing no soportado: {tipo}")
            
            return {
                "success": True,
                "tipo_operacion": TipoOperacion.EVENT_SOURCING.value,
                "consistencia": EstadoConsistencia.EVENTUAL.value,
                "resultado": resultado,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en Event Sourcing: {e}")
            return {
                "success": False,
                "tipo_operacion": TipoOperacion.EVENT_SOURCING.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _procesar_comando(self, operacion: Dict) -> Dict:
        """Procesa comando y genera eventos"""
        comando = operacion.get("comando")
        
        # 1. Validar comando
        if not self._validar_comando(comando):
            raise ValueError("Comando inválido")
        
        # 2. Despachar comando
        eventos_generados = await self.command_dispatcher.dispatch(comando)
        
        # 3. Persistir eventos en Event Store
        for evento in eventos_generados:
            await self.event_store.append(evento)
        
        # 4. Publicar eventos para otros servicios
        for evento in eventos_generados:
            await self.event_publisher.publish(evento)
        
        return {
            "comando_id": comando.get("id"),
            "eventos_generados": len(eventos_generados),
            "eventos": [e.get("tipo") for e in eventos_generados]
        }
    
    async def _procesar_evento(self, operacion: Dict) -> Dict:
        """Procesa evento recibido"""
        evento = operacion.get("evento")
        
        # 1. Persistir evento en Event Store
        await self.event_store.append(evento)
        
        # 2. Actualizar proyecciones
        await self._actualizar_proyecciones(evento)
        
        return {
            "evento_id": evento.get("id"),
            "tipo_evento": evento.get("tipo"),
            "procesado": True
        }
    
    async def _consultar_eventos(self, operacion: Dict) -> List[Dict]:
        """Consulta eventos del Event Store"""
        filtros = operacion.get("filtros", {})
        return await self.event_store.query(filtros)
    
    async def _actualizar_proyecciones(self, evento: Dict):
        """Actualiza vistas proyectadas desde eventos"""
        # Implementar actualización de proyecciones específicas
        pass
    
    def _validar_comando(self, comando: Dict) -> bool:
        """Valida estructura y reglas de negocio del comando"""
        return comando and "id" in comando and "tipo" in comando
    
    def es_aplicable(self, contexto: Dict) -> bool:
        """Determina si Event Sourcing es la estrategia apropiada"""
        return (
            contexto.get("comunicacion_inter_servicios", False) or
            contexto.get("auditoria_completa", False) or
            contexto.get("procesamiento_asincrono", False) or
            contexto.get("flujo_complejo", False)
        )

class HybridDataManager:
    """
    Gestor híbrido que decide entre CRUD y Event Sourcing
    Implementa el patrón Strategy y Chain of Responsibility
    """
    
    def __init__(self):
        self.strategies: List[StrategyPattern] = []
        self.metricas = {
            "operaciones_crud": 0,
            "operaciones_event_sourcing": 0,
            "errores": 0,
            "tiempo_promedio": 0.0
        }
    
    def registrar_strategy(self, strategy: StrategyPattern):
        """Registra una estrategia disponible"""
        self.strategies.append(strategy)
    
    async def ejecutar(self, operacion: Dict, contexto: Dict) -> Dict:
        """
        Ejecuta operación usando la estrategia apropiada
        
        Args:
            operacion: Detalles de la operación a ejecutar
            contexto: Contexto para decidir estrategia
        """
        inicio = datetime.now()
        
        try:
            # Seleccionar estrategia apropiada
            strategy = self._seleccionar_strategy(contexto)
            
            if not strategy:
                raise ValueError("No se encontró estrategia apropiada")
            
            # Ejecutar operación
            resultado = await strategy.ejecutar_operacion(operacion)
            
            # Actualizar métricas
            self._actualizar_metricas(resultado, inicio)
            
            return resultado
            
        except Exception as e:
            self.metricas["errores"] += 1
            logger.error(f"Error ejecutando operación híbrida: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _seleccionar_strategy(self, contexto: Dict) -> Optional[StrategyPattern]:
        """Selecciona la estrategia más apropiada según el contexto"""
        for strategy in self.strategies:
            if strategy.es_aplicable(contexto):
                return strategy
        return None
    
    def _actualizar_metricas(self, resultado: Dict, inicio: datetime):
        """Actualiza métricas de rendimiento"""
        duracion = (datetime.now() - inicio).total_seconds()
        
        if resultado.get("tipo_operacion") == TipoOperacion.CRUD_DIRECTO.value:
            self.metricas["operaciones_crud"] += 1
        elif resultado.get("tipo_operacion") == TipoOperacion.EVENT_SOURCING.value:
            self.metricas["operaciones_event_sourcing"] += 1
        
        # Calcular tiempo promedio (media móvil simple)
        total_ops = self.metricas["operaciones_crud"] + self.metricas["operaciones_event_sourcing"]
        if total_ops > 0:
            self.metricas["tiempo_promedio"] = (
                (self.metricas["tiempo_promedio"] * (total_ops - 1) + duracion) / total_ops
            )
    
    def obtener_metricas(self) -> Dict:
        """Retorna métricas de uso"""
        return self.metricas.copy()

# Configuraciones específicas para cada bounded context
CONFIGURACIONES_BOUNDED_CONTEXT = {
    "marketing": {
        "operaciones_crud": [
            "listar_campanas",
            "obtener_campana_por_id", 
            "buscar_campanas_activas",
            "validar_presupuesto_campana"
        ],
        "operaciones_event_sourcing": [
            "crear_campana",
            "activar_campana",
            "calcular_comision",
            "asignar_conversion_campana"
        ],
        "proyecciones": [
            "vista_campanas_activas",
            "resumen_comisiones_afiliado",
            "estadisticas_conversiones"
        ]
    },
    
    "conversiones": {
        "operaciones_crud": [
            "listar_conversiones",
            "obtener_conversion_por_id",
            "buscar_conversiones_pendientes"
        ],
        "operaciones_event_sourcing": [
            "detectar_conversion",
            "validar_conversion", 
            "confirmar_conversion",
            "rechazar_conversion"
        ],
        "proyecciones": [
            "vista_conversiones_por_campana",
            "metricas_conversion_tiempo_real"
        ]
    },
    
    "afiliados": {
        "operaciones_crud": [
            "listar_afiliados",
            "obtener_afiliado_por_id",
            "buscar_afiliados_activos",
            "validar_datos_afiliado"
        ],
        "operaciones_event_sourcing": [
            "registrar_afiliado",
            "actualizar_afiliado",
            "desactivar_afiliado",
            "procesar_pago_comision"
        ],
        "proyecciones": [
            "vista_afiliados_activos",
            "resumen_ganancias_afiliado"
        ]
    }
}

class ContextualDecisionEngine:
    """
    Motor de decisión contextual para estrategia híbrida
    Analiza el contexto y determina qué enfoque usar
    """
    
    @staticmethod
    def analizar_contexto(operacion: str, bounded_context: str, parametros: Dict) -> Dict:
        """
        Analiza contexto y genera recomendación de estrategia
        
        Returns:
            Dict con contexto analizado y recomendación
        """
        config = CONFIGURACIONES_BOUNDED_CONTEXT.get(bounded_context, {})
        
        contexto = {
            "operacion": operacion,
            "bounded_context": bounded_context,
            "sincronismo_requerido": False,
            "mismo_bounded_context": True,
            "validacion_inmediata": False,
            "operacion_simple": False,
            "comunicacion_inter_servicios": False,
            "auditoria_completa": False,
            "procesamiento_asincrono": False,
            "flujo_complejo": False
        }
        
        # Análisis de la operación
        if operacion in config.get("operaciones_crud", []):
            contexto.update({
                "sincronismo_requerido": True,
                "operacion_simple": True,
                "recomendacion": "CRUD"
            })
        elif operacion in config.get("operaciones_event_sourcing", []):
            contexto.update({
                "comunicacion_inter_servicios": True,
                "auditoria_completa": True,
                "procesamiento_asincrono": True,
                "flujo_complejo": True,
                "recomendacion": "EVENT_SOURCING"
            })
        
        # Análisis de parámetros adicionales
        if parametros.get("requiere_respuesta_inmediata"):
            contexto["sincronismo_requerido"] = True
            contexto["recomendacion"] = "CRUD"
        
        if parametros.get("afecta_multiples_servicios"):
            contexto["comunicacion_inter_servicios"] = True
            contexto["recomendacion"] = "EVENT_SOURCING"
        
        return contexto

# Ejemplos de uso de la estrategia híbrida
EJEMPLOS_USO = {
    "crear_campana": {
        "descripcion": "Creación de campaña con Event Sourcing",
        "contexto": {
            "operacion": "crear_campana",
            "bounded_context": "marketing",
            "afecta_multiples_servicios": True
        },
        "operacion": {
            "tipo": "comando",
            "comando": {
                "id": "cmd-001",
                "tipo": "CrearCampana",
                "datos": {"nombre": "Black Friday", "presupuesto": 10000}
            }
        }
    },
    
    "listar_campanas": {
        "descripcion": "Listado de campañas con CRUD",
        "contexto": {
            "operacion": "listar_campanas",
            "bounded_context": "marketing",
            "requiere_respuesta_inmediata": True
        },
        "operacion": {
            "metodo": "READ",
            "entidad": "campanas",
            "filtros": {"estado": "activa"}
        }
    }
}

if __name__ == "__main__":
    print("=== Estrategia Híbrida CRUD + Event Sourcing ===")
    print(json.dumps(CONFIGURACIONES_BOUNDED_CONTEXT, indent=2))
    
    print("\n=== Ejemplos de Uso ===")
    for nombre, ejemplo in EJEMPLOS_USO.items():
        print(f"\n{nombre.upper()}:")
        print(f"  Descripción: {ejemplo['descripcion']}")
        contexto = ContextualDecisionEngine.analizar_contexto(
            ejemplo["contexto"]["operacion"],
            ejemplo["contexto"]["bounded_context"], 
            ejemplo["contexto"]
        )
        print(f"  Estrategia recomendada: {contexto.get('recomendacion', 'INDETERMINADA')}")
        print(f"  Justificación: {contexto}")