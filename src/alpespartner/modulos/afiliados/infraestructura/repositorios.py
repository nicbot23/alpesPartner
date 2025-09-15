"""
Implementación del repositorio de Afiliados usando SQLAlchemy
Maneja la persistencia del agregado Afiliado en base de datos separada
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..dominio.agregados import Afiliado
from ..dominio.repositorios import RepositorioAfiliados
from ..dominio.objetos_valor import EstadoAfiliado, TipoAfiliado
from ..dominio.excepciones import (
    AfiliadoNoExiste, DocumentoYaRegistrado, EmailYaRegistrado
)
from .modelos import AfiliadoDTO, ReferenciaDTO, OutboxAfiliadosDTO
from .mapeadores import MapeadorAfiliado, MapeadorReferencia, MapeadorOutboxAfiliados
from .db import obtener_session_afiliados


class RepositorioAfiliadosSQLAlchemy(RepositorioAfiliados):
    """Implementación del repositorio de Afiliados usando SQLAlchemy."""
    
    def __init__(self, session: Optional[Session] = None):
        self._session = session
    
    @property
    def session(self) -> Session:
        """Obtiene la sesión de base de datos."""
        if self._session:
            return self._session
        # Si no hay sesión inyectada, crear una nueva
        return next(obtener_session_afiliados())
    
    def obtener_por_id(self, afiliado_id: str) -> Optional[Afiliado]:
        """
        Obtiene un afiliado por su ID.
        
        Args:
            afiliado_id: ID del afiliado
            
        Returns:
            Optional[Afiliado]: El afiliado o None si no existe
        """
        try:
            dto = self.session.query(AfiliadoDTO).filter(
                AfiliadoDTO.id == afiliado_id
            ).first()
            
            if not dto:
                return None
            
            # Obtener referencias del afiliado
            referencias = self.session.query(ReferenciaDTO).filter(
                ReferenciaDTO.afiliado_referente_id == afiliado_id
            ).all()
            
            return MapeadorAfiliado.dto_a_entidad(dto, referencias)
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def obtener_por_documento(
        self, 
        tipo_documento: str, 
        numero_documento: str
    ) -> Optional[Afiliado]:
        """
        Obtiene un afiliado por su documento de identidad.
        
        Args:
            tipo_documento: Tipo del documento
            numero_documento: Número del documento
            
        Returns:
            Optional[Afiliado]: El afiliado o None si no existe
        """
        try:
            dto = self.session.query(AfiliadoDTO).filter(
                and_(
                    AfiliadoDTO.tipo_documento == tipo_documento,
                    AfiliadoDTO.numero_documento == numero_documento
                )
            ).first()
            
            if not dto:
                return None
            
            referencias = self.session.query(ReferenciaDTO).filter(
                ReferenciaDTO.afiliado_referente_id == dto.id
            ).all()
            
            return MapeadorAfiliado.dto_a_entidad(dto, referencias)
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def obtener_por_email(self, email: str) -> Optional[Afiliado]:
        """
        Obtiene un afiliado por su email.
        
        Args:
            email: Email del afiliado
            
        Returns:
            Optional[Afiliado]: El afiliado o None si no existe
        """
        try:
            dto = self.session.query(AfiliadoDTO).filter(
                AfiliadoDTO.email == email
            ).first()
            
            if not dto:
                return None
            
            referencias = self.session.query(ReferenciaDTO).filter(
                ReferenciaDTO.afiliado_referente_id == dto.id
            ).all()
            
            return MapeadorAfiliado.dto_a_entidad(dto, referencias)
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def obtener_por_codigo_referencia(self, codigo_referencia: str) -> Optional[Afiliado]:
        """
        Obtiene un afiliado por su código de referencia.
        
        Args:
            codigo_referencia: Código de referencia
            
        Returns:
            Optional[Afiliado]: El afiliado o None si no existe
        """
        try:
            dto = self.session.query(AfiliadoDTO).filter(
                AfiliadoDTO.codigo_referencia == codigo_referencia
            ).first()
            
            if not dto:
                return None
            
            referencias = self.session.query(ReferenciaDTO).filter(
                ReferenciaDTO.afiliado_referente_id == dto.id
            ).all()
            
            return MapeadorAfiliado.dto_a_entidad(dto, referencias)
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def buscar_con_filtros(
        self,
        filtros: Optional[Dict[str, Any]] = None,
        ordenar_por: str = 'fecha_creacion',
        orden_desc: bool = True,
        limite: int = 100,
        offset: int = 0
    ) -> List[Afiliado]:
        """
        Busca afiliados aplicando filtros.
        
        Args:
            filtros: Diccionario con filtros a aplicar
            ordenar_por: Campo por el cual ordenar
            orden_desc: Si ordenar descendente
            limite: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            List[Afiliado]: Lista de afiliados encontrados
        """
        try:
            query = self.session.query(AfiliadoDTO)
            
            # Aplicar filtros
            if filtros:
                if 'estado' in filtros:
                    query = query.filter(AfiliadoDTO.estado == filtros['estado'])
                
                if 'tipo_afiliado' in filtros:
                    query = query.filter(AfiliadoDTO.tipo_afiliado == filtros['tipo_afiliado'])
                
                if 'email_like' in filtros:
                    query = query.filter(AfiliadoDTO.email.like(f"%{filtros['email_like']}%"))
                
                if 'nombres_like' in filtros:
                    query = query.filter(
                        or_(
                            AfiliadoDTO.nombres.like(f"%{filtros['nombres_like']}%"),
                            AfiliadoDTO.apellidos.like(f"%{filtros['nombres_like']}%")
                        )
                    )
                
                if 'fecha_desde' in filtros:
                    query = query.filter(AfiliadoDTO.fecha_creacion >= filtros['fecha_desde'])
                
                if 'fecha_hasta' in filtros:
                    query = query.filter(AfiliadoDTO.fecha_creacion <= filtros['fecha_hasta'])
                
                if 'afiliado_referente_id' in filtros:
                    query = query.filter(
                        AfiliadoDTO.afiliado_referente_id == filtros['afiliado_referente_id']
                    )
            
            # Aplicar ordenamiento
            campo_orden = getattr(AfiliadoDTO, ordenar_por, AfiliadoDTO.fecha_creacion)
            if orden_desc:
                query = query.order_by(desc(campo_orden))
            else:
                query = query.order_by(asc(campo_orden))
            
            # Aplicar paginación
            dtos = query.offset(offset).limit(limite).all()
            
            # Convertir a entidades de dominio
            afiliados = []
            for dto in dtos:
                referencias = self.session.query(ReferenciaDTO).filter(
                    ReferenciaDTO.afiliado_referente_id == dto.id
                ).all()
                
                afiliado = MapeadorAfiliado.dto_a_entidad(dto, referencias)
                afiliados.append(afiliado)
            
            return afiliados
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def obtener_referidos_activos(self, afiliado_referente_id: str) -> List[Afiliado]:
        """
        Obtiene los afiliados referidos activos de un afiliado.
        
        Args:
            afiliado_referente_id: ID del afiliado referente
            
        Returns:
            List[Afiliado]: Lista de afiliados referidos activos
        """
        try:
            # Obtener IDs de afiliados referidos activos
            referencias_activas = self.session.query(ReferenciaDTO).filter(
                and_(
                    ReferenciaDTO.afiliado_referente_id == afiliado_referente_id,
                    ReferenciaDTO.estado == 'ACTIVA'
                )
            ).all()
            
            afiliados_referidos = []
            for referencia in referencias_activas:
                afiliado = self.obtener_por_id(referencia.afiliado_referido_id)
                if afiliado and afiliado.estado == EstadoAfiliado.ACTIVO:
                    afiliados_referidos.append(afiliado)
            
            return afiliados_referidos
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def obtener_estadisticas(
        self, 
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de afiliados.
        
        Args:
            fecha_desde: Fecha de inicio para el rango
            fecha_hasta: Fecha de fin para el rango
            
        Returns:
            Dict[str, Any]: Estadísticas calculadas
        """
        try:
            query = self.session.query(AfiliadoDTO)
            
            # Aplicar rango de fechas si se especifica
            if fecha_desde:
                query = query.filter(AfiliadoDTO.fecha_creacion >= fecha_desde)
            if fecha_hasta:
                query = query.filter(AfiliadoDTO.fecha_creacion <= fecha_hasta)
            
            # Total de afiliados
            total_afiliados = query.count()
            
            # Afiliados por estado
            por_estado = {}
            for estado in EstadoAfiliado:
                count = query.filter(AfiliadoDTO.estado == estado.value).count()
                por_estado[estado.value] = count
            
            # Afiliados por tipo
            por_tipo = {}
            for tipo in TipoAfiliado:
                count = query.filter(AfiliadoDTO.tipo_afiliado == tipo.value).count()
                por_tipo[tipo.value] = count
            
            # Afiliados con datos bancarios
            con_datos_bancarios = query.filter(
                AfiliadoDTO.banco.isnot(None)
            ).count()
            
            # Afiliados con referente
            con_referente = query.filter(
                AfiliadoDTO.afiliado_referente_id.isnot(None)
            ).count()
            
            return {
                'total_afiliados': total_afiliados,
                'por_estado': por_estado,
                'por_tipo': por_tipo,
                'con_datos_bancarios': con_datos_bancarios,
                'con_referente': con_referente,
                'fecha_consulta': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def guardar(self, afiliado: Afiliado) -> None:
        """
        Guarda un afiliado en la base de datos.
        
        Args:
            afiliado: Agregado Afiliado a guardar
        """
        try:
            # Verificar si ya existe
            dto_existente = self.session.query(AfiliadoDTO).filter(
                AfiliadoDTO.id == afiliado.id
            ).first()
            
            if dto_existente:
                # Actualizar entidad existente
                self._actualizar_dto_desde_entidad(dto_existente, afiliado)
            else:
                # Crear nueva entidad
                dto = MapeadorAfiliado.entidad_a_dto(afiliado)
                self.session.add(dto)
            
            # Guardar referencias
            self._guardar_referencias(afiliado)
            
            # Guardar eventos en outbox
            self._guardar_eventos_outbox(afiliado)
            
            self.session.commit()
            
        except IntegrityError as e:
            self.session.rollback()
            if "numero_documento" in str(e):
                raise DocumentoYaRegistrado(
                    afiliado.documento_identidad.tipo.value,
                    afiliado.documento_identidad.numero
                )
            elif "email" in str(e):
                raise EmailYaRegistrado(afiliado.datos_contacto.email)
            else:
                raise e
        except Exception as e:
            self.session.rollback()
            raise e
    
    def eliminar(self, afiliado_id: str) -> None:
        """
        Elimina un afiliado (soft delete cambiando estado).
        
        Args:
            afiliado_id: ID del afiliado a eliminar
        """
        try:
            dto = self.session.query(AfiliadoDTO).filter(
                AfiliadoDTO.id == afiliado_id
            ).first()
            
            if not dto:
                raise AfiliadoNoExiste(afiliado_id)
            
            # Soft delete - cambiar estado
            dto.estado = EstadoAfiliado.INACTIVO.value
            dto.fecha_actualizacion = datetime.now()
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def _actualizar_dto_desde_entidad(self, dto: AfiliadoDTO, afiliado: Afiliado) -> None:
        """Actualiza un DTO existente con datos de la entidad."""
        import json
        
        dto.nombres = afiliado.datos_personales.nombres
        dto.apellidos = afiliado.datos_personales.apellidos
        dto.fecha_nacimiento = afiliado.datos_personales.fecha_nacimiento
        dto.tipo_documento = afiliado.documento_identidad.tipo.value
        dto.numero_documento = afiliado.documento_identidad.numero
        dto.fecha_expedicion_documento = afiliado.documento_identidad.fecha_expedicion
        dto.email = afiliado.datos_contacto.email
        dto.telefono = afiliado.datos_contacto.telefono
        dto.direccion = afiliado.datos_contacto.direccion
        dto.ciudad = afiliado.datos_contacto.ciudad
        dto.pais = afiliado.datos_contacto.pais
        dto.tipo_afiliado = afiliado.tipo_afiliado.value
        dto.estado = afiliado.estado.value
        dto.porcentaje_comision_base = afiliado.configuracion_comisiones.porcentaje_base
        dto.porcentaje_comision_premium = afiliado.configuracion_comisiones.porcentaje_premium
        dto.monto_minimo_comision = afiliado.configuracion_comisiones.monto_minimo
        dto.banco = afiliado.datos_bancarios.banco if afiliado.datos_bancarios else None
        dto.tipo_cuenta = afiliado.datos_bancarios.tipo_cuenta if afiliado.datos_bancarios else None
        dto.numero_cuenta = afiliado.datos_bancarios.numero_cuenta if afiliado.datos_bancarios else None
        dto.titular_cuenta = afiliado.datos_bancarios.titular if afiliado.datos_bancarios else None
        dto.codigo_referencia = afiliado.codigo_referencia
        dto.afiliado_referente_id = afiliado.afiliado_referente_id
        dto.metadata = json.dumps(afiliado.metadata.datos, ensure_ascii=False) if afiliado.metadata and afiliado.metadata.datos else None
        dto.fecha_actualizacion = datetime.now()
        dto.version = afiliado._version
        dto.correlation_id = afiliado._correlation_id
        dto.causation_id = afiliado._causation_id
    
    def _guardar_referencias(self, afiliado: Afiliado) -> None:
        """Guarda las referencias del afiliado."""
        # Eliminar referencias existentes
        self.session.query(ReferenciaDTO).filter(
            ReferenciaDTO.afiliado_referente_id == afiliado.id
        ).delete()
        
        # Agregar referencias actuales
        for referencia in afiliado.referencias:
            ref_dto = MapeadorReferencia.entidad_a_dto(
                referencia, 
                afiliado.id,
                str(uuid.uuid4())
            )
            self.session.add(ref_dto)
    
    def _guardar_eventos_outbox(self, afiliado: Afiliado) -> None:
        """Guarda los eventos del afiliado en el outbox."""
        for evento in afiliado.eventos:
            evento_dto = MapeadorOutboxAfiliados.evento_a_dto(
                evento_id=str(uuid.uuid4()),
                tipo_evento=evento.__class__.__name__,
                agregado_id=afiliado.id,
                datos_evento=evento.__dict__,
                correlation_id=getattr(evento, 'correlation_id', None),
                causation_id=getattr(evento, 'causation_id', None)
            )
            self.session.add(evento_dto)
        
        # Limpiar eventos después de guardarlos
        afiliado._eventos.clear()