from campanias.modulos.dominio.eventos import (
    CampaniaCreada, CampaniaActivada, AfiliadoAgregadoACampania, CampaniaEliminada
)
from campanias.seedwork.aplicacion.handlers import Handler
from campanias.modulos.infraestructura.despachadores import Despachador
from campanias.seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado, ejecutar_query
from campanias.modulos.aplicacion.dto import CampañaDTO
from campanias.modulos.infraestructura.repositorios import RepositorioCampanias
from campanias.comandos import ComandoLanzarCampaniaCompleta, ComandoCancelarSaga
from campanias.despachadores import Despachador as DespachadorSaga
from dataclasses import dataclass
from typing import List, Optional
import logging

# ==========================================
# HANDLERS DE EVENTOS DE DOMINIO (INTEGRACIÓN)
# ==========================================

class HandlerCampaniaIntegracion(Handler):
    """Handler para eventos de dominio de campanias - los publica a otros microservicios"""

    @staticmethod
    def handle_campania_creada(evento):
        """Maneja el evento CampaniaCreada y lo publica para afiliados/comisiones/conversiones"""
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-campania')

    @staticmethod
    def handle_campania_activada(evento):
        """Maneja el evento CampaniaActivada y lo publica para notificaciones/afiliados"""
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-campania')

    @staticmethod
    def handle_afiliado_agregado_a_campania(evento):
        """Maneja el evento AfiliadoAgregadoACampania y lo publica para afiliados/comisiones"""
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-campania')

    @staticmethod
    def handle_campania_eliminada(evento):
        """Maneja el evento CampaniaEliminada y lo publica para limpieza en otros servicios"""
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-campania')

# ==========================================
# CONSULTAS (QUERIES)
# ==========================================

@dataclass
class ObtenerCampaniaPorId(Query):
    """Query para obtener una campaña por su ID"""
    id_campania: str

@dataclass
class ObtenerTodasLasCampanias(Query):
    """Query para obtener todas las campanias"""
    estado: Optional[str] = None  # Filtro opcional por estado
    tipo: Optional[str] = None    # Filtro opcional por tipo

@dataclass
class ObtenerCampaniasPorAfiliado(Query):
    """Query para obtener campanias asociadas a un afiliado"""
    id_afiliado: str

@dataclass
class ObtenerCampaniasActivas(Query):
    """Query para obtener campanias en estado activo"""
    canal_publicidad: Optional[str] = None  # Filtro opcional por canal

# ==========================================
# QUERY HANDLERS
# ==========================================

class ObtenerCampaniaPorIdHandler(QueryHandler):
    """Handler para obtener una campaña específica por ID"""
    
    def __init__(self):
        self._repositorio: RepositorioCampanias = RepositorioCampanias()

    def handle(self, query: ObtenerCampaniaPorId) -> QueryResultado:
        """Ejecuta la consulta y retorna la campaña o None"""
        campania = self._repositorio.obtener_por_id(query.id_campania)
        
        if campania:
            # Convertir entidad a DTO para la respuesta
            campania_dto = CampañaDTO(
                fecha_creacion=campania.fecha_creacion.isoformat(),
                fecha_actualizacion=campania.fecha_actualizacion.isoformat(),
                id=str(campania.id),
                nombre=campania.nombre,
                descripcion=campania.descripcion,
                tipo=campania.tipo.value,
                canal_publicidad=campania.canal_publicidad.value,
                objetivo=campania.objetivo.value,
                fecha_inicio=campania.fecha_inicio.isoformat(),
                fecha_fin=campania.fecha_fin.isoformat(),
                presupuesto=campania.presupuesto,
                moneda=campania.moneda,
                codigo_campana=campania.codigo_campana,
                segmento_audiencia=campania.segmento_audiencia,
                estado=campania.estado.value
            )
            return QueryResultado(resultado=campania_dto)
        
        return QueryResultado(resultado=None)

class ObtenerTodasLasCampaniasHandler(QueryHandler):
    """Handler para obtener todas las campanias con filtros opcionales"""
    
    def __init__(self):
        self._repositorio: RepositorioCampanias = RepositorioCampanias()

    def handle(self, query: ObtenerTodasLasCampanias) -> QueryResultado:
        """Ejecuta la consulta y retorna lista de campanias"""
        campanias = self._repositorio.obtener_todos()
        
        # Aplicar filtros si están presentes
        if query.estado:
            campanias = [c for c in campanias if c.estado.value == query.estado]
        
        if query.tipo:
            campanias = [c for c in campanias if c.tipo.value == query.tipo]
        
        # Convertir entidades a DTOs
        campanias_dto = []
        for campania in campanias:
            campania_dto = CampañaDTO(
                fecha_creacion=campania.fecha_creacion.isoformat(),
                fecha_actualizacion=campania.fecha_actualizacion.isoformat(),
                id=str(campania.id),
                nombre=campania.nombre,
                descripcion=campania.descripcion,
                tipo=campania.tipo.value,
                canal_publicidad=campania.canal_publicidad.value,
                objetivo=campania.objetivo.value,
                fecha_inicio=campania.fecha_inicio.isoformat(),
                fecha_fin=campania.fecha_fin.isoformat(),
                presupuesto=campania.presupuesto,
                moneda=campania.moneda,
                codigo_campana=campania.codigo_campana,
                segmento_audiencia=campania.segmento_audiencia,
                estado=campania.estado.value
            )
            campanias_dto.append(campania_dto)
        
        return QueryResultado(resultado=campanias_dto)

class ObtenerCampaniasActivasHandler(QueryHandler):
    """Handler para obtener campanias activas"""
    
    def __init__(self):
        self._repositorio: RepositorioCampanias = RepositorioCampanias()

    def handle(self, query: ObtenerCampaniasActivas) -> QueryResultado:
        """Ejecuta la consulta y retorna campanias activas"""
        campanias = self._repositorio.obtener_todos()
        
        # Filtrar solo campanias activas
        campanias_activas = [c for c in campanias if c.estado.value == "activa"]
        
        # Aplicar filtro adicional por canal si está presente
        if query.canal_publicidad:
            campanias_activas = [c for c in campanias_activas 
                               if c.canal_publicidad.value == query.canal_publicidad]
        
        # Convertir a DTOs
        campanias_dto = []
        for campania in campanias_activas:
            campania_dto = CampañaDTO(
                fecha_creacion=campania.fecha_creacion.isoformat(),
                fecha_actualizacion=campania.fecha_actualizacion.isoformat(),
                id=str(campania.id),
                nombre=campania.nombre,
                descripcion=campania.descripcion,
                tipo=campania.tipo.value,
                canal_publicidad=campania.canal_publicidad.value,
                objetivo=campania.objetivo.value,
                fecha_inicio=campania.fecha_inicio.isoformat(),
                fecha_fin=campania.fecha_fin.isoformat(),
                presupuesto=campania.presupuesto,
                moneda=campania.moneda,
                codigo_campana=campania.codigo_campana,
                segmento_audiencia=campania.segmento_audiencia,
                estado=campania.estado.value
            )
            campanias_dto.append(campania_dto)
        
        return QueryResultado(resultado=campanias_dto)

# ==========================================
# REGISTRO DE QUERY HANDLERS
# ==========================================

@ejecutar_query.register(ObtenerCampaniaPorId)
def ejecutar_query_obtener_campania_por_id(query: ObtenerCampaniaPorId):
    handler = ObtenerCampaniaPorIdHandler()
    return handler.handle(query)

@ejecutar_query.register(ObtenerTodasLasCampanias)
def ejecutar_query_obtener_todas_campanias(query: ObtenerTodasLasCampanias):
    handler = ObtenerTodasLasCampaniasHandler()
    return handler.handle(query)

@ejecutar_query.register(ObtenerCampaniasActivas)
def ejecutar_query_obtener_campanias_activas(query: ObtenerCampaniasActivas):
    handler = ObtenerCampaniasActivasHandler()
    return handler.handle(query)

# ==========================================
# HANDLERS DE COMANDOS DESDE BFF (SAGAS)
# ==========================================

class HandlerComandosBFF(Handler):
    """Handler para comandos provenientes del BFF - inicia sagas"""

    @staticmethod
    async def handle_lanzar_campania_completa(comando: ComandoLanzarCampaniaCompleta):
        """
        Maneja el comando del BFF para lanzar una campaña completa.
        Inicia la saga completa de creación y configuración.
        """
        try:
            print(f"🎭 COMANDO BFF RECIBIDO: Lanzar campaña completa - {comando.data.nombre}")
            
            # Extraer datos del comando CloudEvent
            datos_campania = {
                'id': comando.id,  # Usar ID del comando como ID de campaña
                'saga_id': comando.id,  # Propagar saga_id igual al comando.id -- correlacion
                'nombre': comando.data.nombre,
                'tipo': comando.data.tipo,
                'descripcion': comando.data.descripcion,
                'canal_publicidad': comando.data.canal_publicidad,
                'objetivo': comando.data.objetivo,
                'segmento_audiencia': comando.data.segmento_audiencia,
                'fecha_inicio': comando.data.fecha_inicio,
                'fecha_fin': comando.data.fecha_fin,
                'presupuesto': comando.data.presupuesto,
                'moneda': comando.data.moneda,
                'usuario_solicitante': ""
            }
            
            # Iniciar saga usando el despachador existente
            despachador_saga = DespachadorSaga()
            saga_id = despachador_saga.orquestar_saga_campania_completa(datos_campania)
            
            print(f"✅ SAGA INICIADA: {saga_id} para comando BFF {comando.id}")
            return saga_id
            
        except Exception as e:
            error_msg = f"Error procesando comando BFF lanzar campaña: {str(e)}"
            logging.error(error_msg)
            raise e
            print(f"❌ ERROR EN COMANDO BFF: {error_msg}")

    @staticmethod
    def handle_cancelar_saga(comando: ComandoCancelarSaga):
        """
        Maneja el comando del BFF para cancelar una saga en progreso.
        """
        try:
            print(f"⚠️ COMANDO BFF RECIBIDO: Cancelar saga - {comando.data.saga_id}")
            
            # TODO: Implementar lógica de cancelación de saga
            # Esto requeriría buscar la saga y ejecutar compensación
            
            print(f"✅ CANCELACIÓN PROCESADA: Saga {comando.data.saga_id}")
            
        except Exception as e:
            error_msg = f"Error cancelando saga {comando.data.saga_id}: {str(e)}"
            logging.error(error_msg)
            print(f"❌ ERROR CANCELANDO SAGA: {error_msg}")