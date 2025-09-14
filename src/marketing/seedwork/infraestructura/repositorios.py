"""
Repositorios de infraestructura para Marketing
Implementa interfaces de dominio con SQLAlchemy y otros adaptadores
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type, TypeVar
from dataclasses import asdict
import json
from datetime import datetime

from ..dominio.entidades import (
    Campana, Segmento, RepositorioCampanas, RepositorioSegmentos,
    EstadoCampana, TipoCampana, TipoSegmento
)
from ..dominio.eventos import EventoDominio, RepositorioEventos

# Principio de Inversión de Dependencias - Abstracciones para ORM
T = TypeVar('T')

class ConexionBaseDatos(ABC):
    """
    Abstracción para conexión a base de datos
    Principio de Inversión de Dependencias
    """
    
    @abstractmethod
    async def ejecutar_consulta(self, consulta: str, parametros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Ejecuta consulta SQL"""
        pass
    
    @abstractmethod
    async def ejecutar_comando(self, comando: str, parametros: Dict[str, Any] = None) -> int:
        """Ejecuta comando SQL"""
        pass
    
    @abstractmethod
    async def iniciar_transaccion(self) -> 'TransaccionBaseDatos':
        """Inicia transacción"""
        pass

class TransaccionBaseDatos(ABC):
    """
    Abstracción para transacciones
    Principio de Responsabilidad Única - gestión de transacciones
    """
    
    @abstractmethod
    async def confirmar(self) -> None:
        """Confirma transacción"""
        pass
    
    @abstractmethod
    async def cancelar(self) -> None:
        """Cancela transacción"""
        pass
    
    @abstractmethod
    async def __aenter__(self):
        """Context manager entry"""
        return self
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass

# Mapeadores para convertir entre dominio y persistencia
class MapeadorCampana:
    """
    Mapeador para entidad Campaña
    Principio de Responsabilidad Única - mapeo específico
    """
    
    @staticmethod
    def entidad_a_dict(campana: Campana) -> Dict[str, Any]:
        """Convierte entidad a diccionario para persistencia"""
        data = {
            'id': campana.id,
            'nombre': campana.nombre,
            'descripcion': campana.descripcion,
            'tipo': campana.tipo.value,
            'estado': campana.estado.value,
            'presupuesto_utilizado': campana.presupuesto_utilizado,
            'conversiones_obtenidas': campana.conversiones_obtenidas,
            'creador_id': campana.creador_id,
            'fecha_creacion': campana.fecha_creacion.isoformat(),
            'fecha_actualizacion': campana.fecha_actualizacion.isoformat(),
            'version': campana.version,
            'segmentos_objetivo': json.dumps(campana.segmentos_objetivo),
            'configuracion': json.dumps(asdict(campana.configuracion)) if campana.configuracion else None
        }
        return data
    
    @staticmethod
    def dict_a_entidad(data: Dict[str, Any]) -> Campana:
        """Convierte diccionario de base de datos a entidad"""
        from ..dominio.entidades import ConfiguracionCampana
        
        campana = Campana()
        campana.id = data['id']
        campana.nombre = data['nombre']
        campana.descripcion = data['descripcion']
        campana.tipo = TipoCampana(data['tipo'])
        campana.estado = EstadoCampana(data['estado'])
        campana.presupuesto_utilizado = data['presupuesto_utilizado']
        campana.conversiones_obtenidas = data['conversiones_obtenidas']
        campana.creador_id = data['creador_id']
        campana.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        campana.fecha_actualizacion = datetime.fromisoformat(data['fecha_actualizacion'])
        campana.version = data['version']
        campana.segmentos_objetivo = json.loads(data['segmentos_objetivo']) if data['segmentos_objetivo'] else []
        
        if data['configuracion']:
            config_data = json.loads(data['configuracion'])
            config_data['fecha_inicio'] = datetime.fromisoformat(config_data['fecha_inicio'])
            config_data['fecha_fin'] = datetime.fromisoformat(config_data['fecha_fin'])
            campana.configuracion = ConfiguracionCampana(**config_data)
        
        return campana

class MapeadorSegmento:
    """
    Mapeador para entidad Segmento
    Principio de Responsabilidad Única - mapeo específico
    """
    
    @staticmethod
    def entidad_a_dict(segmento: Segmento) -> Dict[str, Any]:
        """Convierte entidad a diccionario para persistencia"""
        criterios_data = []
        for criterio in segmento.criterios:
            criterios_data.append({
                'tipo': criterio.tipo.value,
                'campo': criterio.campo,
                'operador': criterio.operador,
                'valor': criterio.valor,
                'descripcion': criterio.descripcion
            })
        
        data = {
            'id': segmento.id,
            'nombre': segmento.nombre,
            'descripcion': segmento.descripcion,
            'tipo': segmento.tipo.value,
            'activo': segmento.activo,
            'creador_id': segmento.creador_id,
            'fecha_creacion': segmento.fecha_creacion.isoformat(),
            'fecha_actualizacion': segmento.fecha_actualizacion.isoformat(),
            'version': segmento.version,
            'usuarios_incluidos': json.dumps(segmento.usuarios_incluidos),
            'criterios': json.dumps(criterios_data)
        }
        return data
    
    @staticmethod
    def dict_a_entidad(data: Dict[str, Any]) -> Segmento:
        """Convierte diccionario de base de datos a entidad"""
        from ..dominio.entidades import CriterioSegmentacion
        
        segmento = Segmento()
        segmento.id = data['id']
        segmento.nombre = data['nombre']
        segmento.descripcion = data['descripcion']
        segmento.tipo = TipoSegmento(data['tipo'])
        segmento.activo = data['activo']
        segmento.creador_id = data['creador_id']
        segmento.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        segmento.fecha_actualizacion = datetime.fromisoformat(data['fecha_actualizacion'])
        segmento.version = data['version']
        segmento.usuarios_incluidos = json.loads(data['usuarios_incluidos']) if data['usuarios_incluidos'] else []
        
        if data['criterios']:
            criterios_data = json.loads(data['criterios'])
            for criterio_data in criterios_data:
                criterio = CriterioSegmentacion(
                    tipo=TipoSegmento(criterio_data['tipo']),
                    campo=criterio_data['campo'],
                    operador=criterio_data['operador'],
                    valor=criterio_data['valor'],
                    descripcion=criterio_data['descripcion']
                )
                segmento.criterios.append(criterio)
        
        return segmento

# Implementaciones de repositorios
class RepositorioCampanasSQLAlchemy(RepositorioCampanas):
    """
    Implementación SQLAlchemy del repositorio de campañas
    Principio de Inversión de Dependencias - implementación específica
    """
    
    def __init__(self, conexion: ConexionBaseDatos):
        self._conexion = conexion
        self._mapeador = MapeadorCampana()
    
    async def guardar(self, campana: Campana) -> None:
        """Guarda campaña en base de datos"""
        data = self._mapeador.entidad_a_dict(campana)
        
        # Verificar si existe
        existe = await self._conexion.ejecutar_consulta(
            "SELECT id FROM marketing_campanas WHERE id = :id",
            {"id": campana.id}
        )
        
        if existe:
            # Actualizar
            comando = """
            UPDATE marketing_campanas SET 
                nombre = :nombre,
                descripcion = :descripcion,
                tipo = :tipo,
                estado = :estado,
                presupuesto_utilizado = :presupuesto_utilizado,
                conversiones_obtenidas = :conversiones_obtenidas,
                fecha_actualizacion = :fecha_actualizacion,
                version = :version,
                segmentos_objetivo = :segmentos_objetivo,
                configuracion = :configuracion
            WHERE id = :id
            """
        else:
            # Insertar
            comando = """
            INSERT INTO marketing_campanas (
                id, nombre, descripcion, tipo, estado,
                presupuesto_utilizado, conversiones_obtenidas, creador_id,
                fecha_creacion, fecha_actualizacion, version,
                segmentos_objetivo, configuracion
            ) VALUES (
                :id, :nombre, :descripcion, :tipo, :estado,
                :presupuesto_utilizado, :conversiones_obtenidas, :creador_id,
                :fecha_creacion, :fecha_actualizacion, :version,
                :segmentos_objetivo, :configuracion
            )
            """
        
        await self._conexion.ejecutar_comando(comando, data)
    
    async def obtener_por_id(self, campana_id: str) -> Optional[Campana]:
        """Obtiene campaña por ID"""
        resultados = await self._conexion.ejecutar_consulta(
            "SELECT * FROM marketing_campanas WHERE id = :id",
            {"id": campana_id}
        )
        
        if not resultados:
            return None
        
        return self._mapeador.dict_a_entidad(resultados[0])
    
    async def obtener_activas(self) -> List[Campana]:
        """Obtiene campañas activas"""
        resultados = await self._conexion.ejecutar_consulta(
            "SELECT * FROM marketing_campanas WHERE estado = :estado",
            {"estado": EstadoCampana.ACTIVA.value}
        )
        
        return [self._mapeador.dict_a_entidad(data) for data in resultados]
    
    async def obtener_por_creador(self, creador_id: str) -> List[Campana]:
        """Obtiene campañas por creador"""
        resultados = await self._conexion.ejecutar_consulta(
            "SELECT * FROM marketing_campanas WHERE creador_id = :creador_id ORDER BY fecha_creacion DESC",
            {"creador_id": creador_id}
        )
        
        return [self._mapeador.dict_a_entidad(data) for data in resultados]

class RepositorioSegmentosSQLAlchemy(RepositorioSegmentos):
    """
    Implementación SQLAlchemy del repositorio de segmentos
    Principio de Inversión de Dependencias - implementación específica
    """
    
    def __init__(self, conexion: ConexionBaseDatos):
        self._conexion = conexion
        self._mapeador = MapeadorSegmento()
    
    async def guardar(self, segmento: Segmento) -> None:
        """Guarda segmento en base de datos"""
        data = self._mapeador.entidad_a_dict(segmento)
        
        # Verificar si existe
        existe = await self._conexion.ejecutar_consulta(
            "SELECT id FROM marketing_segmentos WHERE id = :id",
            {"id": segmento.id}
        )
        
        if existe:
            # Actualizar
            comando = """
            UPDATE marketing_segmentos SET 
                nombre = :nombre,
                descripcion = :descripcion,
                tipo = :tipo,
                activo = :activo,
                fecha_actualizacion = :fecha_actualizacion,
                version = :version,
                usuarios_incluidos = :usuarios_incluidos,
                criterios = :criterios
            WHERE id = :id
            """
        else:
            # Insertar
            comando = """
            INSERT INTO marketing_segmentos (
                id, nombre, descripcion, tipo, activo, creador_id,
                fecha_creacion, fecha_actualizacion, version,
                usuarios_incluidos, criterios
            ) VALUES (
                :id, :nombre, :descripcion, :tipo, :activo, :creador_id,
                :fecha_creacion, :fecha_actualizacion, :version,
                :usuarios_incluidos, :criterios
            )
            """
        
        await self._conexion.ejecutar_comando(comando, data)
    
    async def obtener_por_id(self, segmento_id: str) -> Optional[Segmento]:
        """Obtiene segmento por ID"""
        resultados = await self._conexion.ejecutar_consulta(
            "SELECT * FROM marketing_segmentos WHERE id = :id",
            {"id": segmento_id}
        )
        
        if not resultados:
            return None
        
        return self._mapeador.dict_a_entidad(resultados[0])
    
    async def obtener_activos(self) -> List[Segmento]:
        """Obtiene segmentos activos"""
        resultados = await self._conexion.ejecutar_consulta(
            "SELECT * FROM marketing_segmentos WHERE activo = :activo",
            {"activo": True}
        )
        
        return [self._mapeador.dict_a_entidad(data) for data in resultados]
    
    async def obtener_por_tipo(self, tipo: TipoSegmento) -> List[Segmento]:
        """Obtiene segmentos por tipo"""
        resultados = await self._conexion.ejecutar_consulta(
            "SELECT * FROM marketing_segmentos WHERE tipo = :tipo AND activo = :activo",
            {"tipo": tipo.value, "activo": True}
        )
        
        return [self._mapeador.dict_a_entidad(data) for data in resultados]

# Repositorio de eventos
class RepositorioEventosSQLAlchemy(RepositorioEventos):
    """
    Implementación SQLAlchemy del repositorio de eventos
    Principio de Inversión de Dependencias - Event Store
    """
    
    def __init__(self, conexion: ConexionBaseDatos):
        self._conexion = conexion
    
    async def guardar_evento(self, evento: EventoDominio) -> None:
        """Guarda evento en el store"""
        data = {
            'id': evento.id,
            'nombre': evento.nombre,
            'fecha': evento.fecha.isoformat(),
            'version': evento.version,
            'correlation_id': evento.correlation_id,
            'causation_id': evento.causation_id,
            'datos': json.dumps(asdict(evento)),
            'tipo_evento': evento.__class__.__name__
        }
        
        comando = """
        INSERT INTO marketing_eventos (
            id, nombre, fecha, version, correlation_id, causation_id, datos, tipo_evento
        ) VALUES (
            :id, :nombre, :fecha, :version, :correlation_id, :causation_id, :datos, :tipo_evento
        )
        """
        
        await self._conexion.ejecutar_comando(comando, data)
    
    async def obtener_eventos_por_agregado(self, agregado_id: str) -> List[EventoDominio]:
        """Obtiene eventos de un agregado específico"""
        # Implementación específica dependería de cómo se estructura el agregado_id
        resultados = await self._conexion.ejecutar_consulta(
            "SELECT * FROM marketing_eventos WHERE datos LIKE :pattern ORDER BY fecha",
            {"pattern": f'%"campana_id": "{agregado_id}"%'}
        )
        
        eventos = []
        for data in resultados:
            # Deserializar evento (simplificado)
            evento_data = json.loads(data['datos'])
            # Aquí iría lógica para reconstruir el evento específico
            eventos.append(evento_data)
        
        return eventos
    
    async def obtener_eventos_por_tipo(self, tipo_evento: str) -> List[EventoDominio]:
        """Obtiene eventos de un tipo específico"""
        resultados = await self._conexion.ejecutar_consulta(
            "SELECT * FROM marketing_eventos WHERE tipo_evento = :tipo ORDER BY fecha",
            {"tipo": tipo_evento}
        )
        
        eventos = []
        for data in resultados:
            evento_data = json.loads(data['datos'])
            eventos.append(evento_data)
        
        return eventos
    
    async def obtener_eventos_desde(self, fecha: datetime) -> List[EventoDominio]:
        """Obtiene eventos desde una fecha específica"""
        resultados = await self._conexion.ejecutar_consulta(
            "SELECT * FROM marketing_eventos WHERE fecha >= :fecha ORDER BY fecha",
            {"fecha": fecha.isoformat()}
        )
        
        eventos = []
        for data in resultados:
            evento_data = json.loads(data['datos'])
            eventos.append(evento_data)
        
        return eventos

# Factory para crear repositorios
class FabricaRepositoriosMarketing:
    """
    Factory para crear repositorios de marketing
    Principio de Responsabilidad Única - creación centralizada
    """
    
    def __init__(self, conexion: ConexionBaseDatos):
        self._conexion = conexion
    
    def crear_repositorio_campanas(self) -> RepositorioCampanas:
        """Crea repositorio de campañas"""
        return RepositorioCampanasSQLAlchemy(self._conexion)
    
    def crear_repositorio_segmentos(self) -> RepositorioSegmentos:
        """Crea repositorio de segmentos"""
        return RepositorioSegmentosSQLAlchemy(self._conexion)
    
    def crear_repositorio_eventos(self) -> RepositorioEventos:
        """Crea repositorio de eventos"""
        return RepositorioEventosSQLAlchemy(self._conexion)

# Unidad de trabajo para transacciones
class UnidadDeTrabajoMarketing:
    """
    Patrón Unit of Work para gestionar transacciones
    Principio de Responsabilidad Única - coordinación transaccional
    """
    
    def __init__(self, conexion: ConexionBaseDatos):
        self._conexion = conexion
        self._transaccion: Optional[TransaccionBaseDatos] = None
        self._fabrica = FabricaRepositoriosMarketing(conexion)
    
    async def __aenter__(self):
        """Inicia unidad de trabajo"""
        self._transaccion = await self._conexion.iniciar_transaccion()
        await self._transaccion.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Finaliza unidad de trabajo"""
        if self._transaccion:
            await self._transaccion.__aexit__(exc_type, exc_val, exc_tb)
    
    @property
    def campanas(self) -> RepositorioCampanas:
        """Repositorio de campañas"""
        return self._fabrica.crear_repositorio_campanas()
    
    @property
    def segmentos(self) -> RepositorioSegmentos:
        """Repositorio de segmentos"""
        return self._fabrica.crear_repositorio_segmentos()
    
    @property
    def eventos(self) -> RepositorioEventos:
        """Repositorio de eventos"""
        return self._fabrica.crear_repositorio_eventos()
    
    async def confirmar(self) -> None:
        """Confirma cambios"""
        if self._transaccion:
            await self._transaccion.confirmar()
    
    async def cancelar(self) -> None:
        """Cancela cambios"""
        if self._transaccion:
            await self._transaccion.cancelar()