from campanias.seedwork.aplicacion.dto import Mapeador as AppMap
from campanias.seedwork.dominio.repositorios import Mapeador as RepMap
from campanias.modulos.dominio.entidades import Campaña, CampañaProducto, campaniaservicio, campaniasegmento
from .dto import CampañaDTO, CampañaProductoDTO, campaniaservicioDTO, campaniasegmentoDTO
from datetime import datetime

class MapeadorCampañaDTOApp(AppMap):
    def entidad_a_dto(self, entidad: Campaña) -> CampañaDTO:
        return CampañaDTO(
            id=entidad.id,
            nombre=entidad.nombre.nombre,
            descripcion=entidad.descripcion.descripcion,
            estado=entidad.estado.value,
            tipo=entidad.tipo.value,
            canal_publicidad=entidad.canal_publicidad.value,
            objetivo=entidad.objetivo.value,
            fecha_inicio=entidad.fecha_inicio.fecha_inicio,
            fecha_fin=entidad.fecha_fin.fecha_fin,
            fecha_creacion=entidad.fecha_creacion.fecha_creacion
        )

    def dto_a_entidad(self, dto: CampañaDTO) -> Campaña:
        raise NotImplementedError('No es necesario implementar este método para el mapeador de aplicación')

class MapeadorCampaniaDTOJson():
    """Mapeador para convertir entre JSON de API y DTOs - Usado en endpoints para eventos"""
    
    def externo_a_dto(self, externo: dict) -> CampañaDTO:
        """Convierte JSON de API request a DTO"""
        return CampañaDTO(
            id=externo.get('id'),
            nombre=externo.get('nombre'),
            descripcion=externo.get('descripcion'),
            estado=externo.get('estado', 'BORRADOR'),
            tipo=externo.get('tipo'),
            canal_publicidad=externo.get('canal_publicidad'),
            objetivo=externo.get('objetivo'),
            fecha_inicio=self._str_to_datetime(externo.get('fecha_inicio')) if externo.get('fecha_inicio') else datetime.now(),
            fecha_fin=self._str_to_datetime(externo.get('fecha_fin')) if externo.get('fecha_fin') else None,
            fecha_creacion=self._str_to_datetime(externo.get('fecha_creacion')) if externo.get('fecha_creacion') else datetime.now(),
            presupuesto=externo.get('presupuesto', 0.0),
            moneda=externo.get('moneda', 'USD'),
            codigo_campana=externo.get('codigo_campana'),
            segmento_audiencia=externo.get('segmento_audiencia'),
            activo=externo.get('activo', True)
        )
    
    def dto_a_externo(self, dto: CampañaDTO) -> dict:
        """Convierte DTO a JSON de API response"""
        return {
            'id': dto.id,
            'nombre': dto.nombre,
            'descripcion': dto.descripcion,
            'estado': dto.estado,
            'tipo': dto.tipo,
            'canal_publicidad': dto.canal_publicidad,
            'objetivo': dto.objetivo,
            'fecha_inicio': self._datetime_to_str(dto.fecha_inicio),
            'fecha_fin': self._datetime_to_str(dto.fecha_fin) if dto.fecha_fin else None,
            'fecha_creacion': self._datetime_to_str(dto.fecha_creacion),
            'presupuesto': dto.presupuesto,
            'moneda': dto.moneda,
            'codigo_campana': dto.codigo_campana,
            'segmento_audiencia': dto.segmento_audiencia,
            'activo': dto.activo
        }
    
    def _str_to_datetime(self, fecha_str: str) -> datetime:
        """Convierte string ISO a datetime"""
        if not fecha_str:
            return None
        try:
            return datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        except:
            return datetime.now()
    
    def _datetime_to_str(self, fecha: datetime) -> str:
        """Convierte datetime a string ISO"""
        if not fecha:
            return None
        return fecha.isoformat()

class MapeadorCampañaProductoDTOJson():
    """Mapeador para productos de campaña"""
    
    def externo_a_dto(self, externo: dict) -> CampañaProductoDTO:
        return CampañaProductoDTO(
            id=externo.get('id'),
            campania_id=externo.get('campania_id'),
            producto_id=externo.get('producto_id'),
            descuento=externo.get('descuento', 0.0),
            comision=externo.get('comision', 0.0)
        )
    
    def dto_a_externo(self, dto: CampañaProductoDTO) -> dict:
        return {
            'id': dto.id,
            'campania_id': dto.campania_id,
            'producto_id': dto.producto_id,
            'descuento': dto.descuento,
            'comision': dto.comision
        }

class MapeadorcampaniaservicioDTOJson():
    """Mapeador para servicios de campaña"""
    
    def externo_a_dto(self, externo: dict) -> campaniaservicioDTO:
        return campaniaservicioDTO(
            id=externo.get('id'),
            campania_id=externo.get('campania_id'),
            servicio_id=externo.get('servicio_id'),
            descuento=externo.get('descuento', 0.0),
            comision=externo.get('comision', 0.0)
        )
    
    def dto_a_externo(self, dto: campaniaservicioDTO) -> dict:
        return {
            'id': dto.id,
            'campania_id': dto.campania_id,
            'servicio_id': dto.servicio_id,
            'descuento': dto.descuento,
            'comision': dto.comision
        }

# Alias para compatibilidad
MapeadorCampania = MapeadorCampañaDTOApp