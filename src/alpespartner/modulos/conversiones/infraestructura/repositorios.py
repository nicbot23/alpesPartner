"""
Repositorio de infraestructura para Conversiones
Implementa persistencia descentralizada con outbox propio
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
import logging
from ..dominio.repositorios import RepositorioConversiones
from ..dominio.agregados import Conversion
from .modelos import ConversionDTO, ConversionOutboxEvent
from .mapeadores import conversion_a_dto, dto_a_conversion, evento_a_outbox
from .db import ConversionesSessionLocal


logger = logging.getLogger(__name__)


class RepositorioConversionesMySQL(RepositorioConversiones):
    """Implementación MySQL del repositorio Conversiones con outbox descentralizado"""
    
    def __init__(self, session: Optional[Session] = None):
        self._session = session or ConversionesSessionLocal()
        self._session_owned = session is None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session_owned:
            if exc_type:
                self._session.rollback()
            else:
                self._session.commit()
            self._session.close()
    
    def guardar(self, conversion: Conversion) -> None:
        """Persiste conversión y eventos en outbox descentralizado"""
        try:
            # 1. Persistir el agregado
            dto = conversion_a_dto(conversion)
            
            # Verificar si existe (update vs insert)
            existing = self._session.get(ConversionDTO, conversion.id)
            if existing:
                # Actualizar campos
                existing.estado = dto.estado
                existing.confirmed_at = dto.confirmed_at
                existing.validation_score = dto.validation_score
                existing.version += 1
            else:
                # Insertar nuevo
                self._session.add(dto)
            
            # 2. Persistir eventos en outbox propio
            for evento in conversion.eventos:
                outbox_event = evento_a_outbox(evento, conversion)
                if outbox_event:  # Solo eventos de integración
                    self._session.add(outbox_event)
            
            # 3. Confirmar transacción
            if self._session_owned:
                self._session.commit()
            
            # 4. Limpiar eventos del agregado
            conversion.limpiar_eventos()
            
        except Exception as e:
            if self._session_owned:
                self._session.rollback()
            raise e
    
    def obtener_por_id(self, conversion_id: str) -> Optional[Conversion]:
        """Obtiene conversión por ID"""
        dto = self._session.get(ConversionDTO, conversion_id)
        return dto_a_conversion(dto) if dto else None
    
    def obtener_por_transaction_id(self, transaction_id: str) -> Optional[Conversion]:
        """Obtiene conversión por transaction_id único"""
        dto = self._session.query(ConversionDTO).filter(
            ConversionDTO.transaction_id == transaction_id
        ).first()
        return dto_a_conversion(dto) if dto else None
    
    def listar_por_afiliado(self, affiliate_id: str, limite: int = 100) -> List[Conversion]:
        """Lista conversiones de un afiliado"""
        dtos = self._session.query(ConversionDTO).filter(
            ConversionDTO.affiliate_id == affiliate_id
        ).order_by(desc(ConversionDTO.created_at)).limit(limite).all()
        
        return [dto_a_conversion(dto) for dto in dtos]
    
    def listar_por_campana(self, campaign_id: str, limite: int = 100) -> List[Conversion]:
        """Lista conversiones de una campaña"""
        dtos = self._session.query(ConversionDTO).filter(
            ConversionDTO.campaign_id == campaign_id
        ).order_by(desc(ConversionDTO.created_at)).limit(limite).all()
        
        return [dto_a_conversion(dto) for dto in dtos]
    
    def listar_pendientes(self, limite: int = 100) -> List[Conversion]:
        """Lista conversiones pendientes de validación"""
        dtos = self._session.query(ConversionDTO).filter(
            ConversionDTO.estado == 'PENDIENTE'
        ).order_by(asc(ConversionDTO.created_at)).limit(limite).all()
        
        return [dto_a_conversion(dto) for dto in dtos]
    
    def contar_por_estado(self, estado: str) -> int:
        """Cuenta conversiones por estado"""
        return self._session.query(func.count(ConversionDTO.id)).filter(
            ConversionDTO.estado == estado
        ).scalar() or 0
    
    def listar_eventos_pendientes(self, limite: int = 50) -> List[ConversionOutboxEvent]:
        """Lista eventos pendientes de publicación en outbox propio"""
        return self._session.query(ConversionOutboxEvent).filter(
            ConversionOutboxEvent.published == False,
            ConversionOutboxEvent.dead_letter == False
        ).order_by(asc(ConversionOutboxEvent.occurred_at)).limit(limite).all()
    
    def marcar_eventos_publicados(self, event_ids: List[str]) -> int:
        """Marca eventos como publicados"""
        if not event_ids:
            return 0
        
        updated = self._session.query(ConversionOutboxEvent).filter(
            ConversionOutboxEvent.id.in_(event_ids)
        ).update({ConversionOutboxEvent.published: True})
        
        if self._session_owned:
            self._session.commit()
        
        return updated

    def buscar_con_filtros(self, filtros: dict, page: int = 1, size: int = 20) -> List[Conversion]:
        """Busca conversiones aplicando filtros con paginación."""
        try:
            query = self._session.query(ConversionDTO)
            
            # Aplicar filtros
            if 'afiliado_id' in filtros:
                query = query.filter(ConversionDTO.afiliado_id == filtros['afiliado_id'])
            if 'campana_id' in filtros:
                query = query.filter(ConversionDTO.campana_id == filtros['campana_id'])
            if 'tipo_conversion' in filtros:
                query = query.filter(ConversionDTO.tipo_conversion == filtros['tipo_conversion'])
            if 'estado' in filtros:
                query = query.filter(ConversionDTO.estado == filtros['estado'])
            if 'fecha_desde' in filtros:
                query = query.filter(ConversionDTO.fecha_conversion >= filtros['fecha_desde'])
            if 'fecha_hasta' in filtros:
                query = query.filter(ConversionDTO.fecha_conversion <= filtros['fecha_hasta'])
            
            # Paginación
            offset = (page - 1) * size
            conversion_dtos = query.offset(offset).limit(size).all()
            
            return [dto_a_conversion(dto) for dto in conversion_dtos]
            
        except Exception as e:
            logger.error(f"Error buscando conversiones con filtros: {e}")
            raise

    def contar_con_filtros(self, filtros: dict) -> int:
        """Cuenta conversiones que coinciden con los filtros."""
        try:
            query = self._session.query(ConversionDTO)
            
            # Aplicar los mismos filtros que buscar_con_filtros
            if 'afiliado_id' in filtros:
                query = query.filter(ConversionDTO.afiliado_id == filtros['afiliado_id'])
            if 'campana_id' in filtros:
                query = query.filter(ConversionDTO.campana_id == filtros['campana_id'])
            if 'tipo_conversion' in filtros:
                query = query.filter(ConversionDTO.tipo_conversion == filtros['tipo_conversion'])
            if 'estado' in filtros:
                query = query.filter(ConversionDTO.estado == filtros['estado'])
            if 'fecha_desde' in filtros:
                query = query.filter(ConversionDTO.fecha_conversion >= filtros['fecha_desde'])
            if 'fecha_hasta' in filtros:
                query = query.filter(ConversionDTO.fecha_conversion <= filtros['fecha_hasta'])
            
            return query.count()
            
        except Exception as e:
            logger.error(f"Error contando conversiones con filtros: {e}")
            raise

    def obtener_por_afiliado(self, afiliado_id: str, incluir_canceladas: bool = False) -> List[Conversion]:
        """Obtiene conversiones de un afiliado específico."""
        try:
            query = self._session.query(ConversionDTO).filter(
                ConversionDTO.afiliado_id == afiliado_id
            )
            
            if not incluir_canceladas:
                query = query.filter(ConversionDTO.estado != 'CANCELADA')
            
            conversion_dtos = query.order_by(ConversionDTO.fecha_conversion.desc()).all()
            return [dto_a_conversion(dto) for dto in conversion_dtos]
            
        except Exception as e:
            logger.error(f"Error obteniendo conversiones del afiliado {afiliado_id}: {e}")
            raise

    def obtener_por_campana(self, campana_id: str, estado: str = None) -> List[Conversion]:
        """Obtiene conversiones de una campaña específica."""
        try:
            query = self._session.query(ConversionDTO).filter(
                ConversionDTO.campana_id == campana_id
            )
            
            if estado:
                query = query.filter(ConversionDTO.estado == estado)
            
            conversion_dtos = query.order_by(ConversionDTO.fecha_conversion.desc()).all()
            return [dto_a_conversion(dto) for dto in conversion_dtos]
            
        except Exception as e:
            logger.error(f"Error obteniendo conversiones de la campaña {campana_id}: {e}")
            raise

    def obtener_estadisticas(self, fecha_desde=None, fecha_hasta=None, agrupado_por='estado') -> dict:
        """Obtiene estadísticas de conversiones."""
        try:
            from sqlalchemy import func
            
            query = self._session.query(ConversionDTO)
            
            # Aplicar filtros de fecha
            if fecha_desde:
                query = query.filter(ConversionDTO.fecha_conversion >= fecha_desde)
            if fecha_hasta:
                query = query.filter(ConversionDTO.fecha_conversion <= fecha_hasta)
            
            if agrupado_por == 'estado':
                resultado = query.with_entities(
                    ConversionDTO.estado,
                    func.count(ConversionDTO.id).label('cantidad'),
                    func.sum(ConversionDTO.monto_transaccion).label('monto_total')
                ).group_by(ConversionDTO.estado).all()
                
                return {
                    'agrupado_por': 'estado',
                    'datos': [
                        {
                            'estado': row.estado,
                            'cantidad': row.cantidad,
                            'monto_total': float(row.monto_total or 0)
                        }
                        for row in resultado
                    ]
                }
            
            elif agrupado_por == 'tipo':
                resultado = query.with_entities(
                    ConversionDTO.tipo_conversion,
                    func.count(ConversionDTO.id).label('cantidad'),
                    func.sum(ConversionDTO.monto_transaccion).label('monto_total')
                ).group_by(ConversionDTO.tipo_conversion).all()
                
                return {
                    'agrupado_por': 'tipo',
                    'datos': [
                        {
                            'tipo': row.tipo_conversion,
                            'cantidad': row.cantidad,
                            'monto_total': float(row.monto_total or 0)
                        }
                        for row in resultado
                    ]
                }
            
            else:
                # Estadísticas generales
                total = query.count()
                monto_total = query.with_entities(
                    func.sum(ConversionDTO.monto_transaccion)
                ).scalar() or 0
                
                return {
                    'agrupado_por': 'general',
                    'datos': {
                        'total_conversiones': total,
                        'monto_total': float(monto_total)
                    }
                }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            raise