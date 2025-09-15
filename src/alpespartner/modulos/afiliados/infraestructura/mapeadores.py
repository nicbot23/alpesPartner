"""
Mapeadores entre dominio e infraestructura para Afiliados
Transforman agregados de dominio a DTOs de persistencia y viceversa
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import json
import uuid

from ..dominio.agregados import Afiliado
from ..dominio.objetos_valor import (
    TipoAfiliado, EstadoAfiliado, DatosPersonales, DocumentoIdentidad,
    DatosContacto, DatosBancarios, ConfiguracionComisiones, MetadatosAfiliado,
    TipoDocumento, Referencia
)
from ..dominio.fabricas import FabricaAfiliados
from .modelos import AfiliadoDTO, ReferenciaDTO, OutboxAfiliadosDTO


class MapeadorAfiliado:
    """Mapeador entre agregado Afiliado y AfiliadoDTO."""
    
    @staticmethod
    def entidad_a_dto(afiliado: Afiliado) -> AfiliadoDTO:
        """
        Convierte un agregado Afiliado a AfiliadoDTO para persistencia.
        
        Args:
            afiliado: Agregado de dominio
            
        Returns:
            AfiliadoDTO: DTO para persistencia
        """
        # Serializar metadatos
        metadata_json = None
        if afiliado.metadata and afiliado.metadata.datos:
            metadata_json = json.dumps(afiliado.metadata.datos, ensure_ascii=False)
        
        return AfiliadoDTO(
            id=afiliado.id,
            nombres=afiliado.datos_personales.nombres,
            apellidos=afiliado.datos_personales.apellidos,
            fecha_nacimiento=afiliado.datos_personales.fecha_nacimiento,
            tipo_documento=afiliado.documento_identidad.tipo.value,
            numero_documento=afiliado.documento_identidad.numero,
            fecha_expedicion_documento=afiliado.documento_identidad.fecha_expedicion,
            email=afiliado.datos_contacto.email,
            telefono=afiliado.datos_contacto.telefono,
            direccion=afiliado.datos_contacto.direccion,
            ciudad=afiliado.datos_contacto.ciudad,
            pais=afiliado.datos_contacto.pais,
            tipo_afiliado=afiliado.tipo_afiliado.value,
            estado=afiliado.estado.value,
            porcentaje_comision_base=afiliado.configuracion_comisiones.porcentaje_base,
            porcentaje_comision_premium=afiliado.configuracion_comisiones.porcentaje_premium,
            monto_minimo_comision=afiliado.configuracion_comisiones.monto_minimo,
            banco=afiliado.datos_bancarios.banco if afiliado.datos_bancarios else None,
            tipo_cuenta=afiliado.datos_bancarios.tipo_cuenta if afiliado.datos_bancarios else None,
            numero_cuenta=afiliado.datos_bancarios.numero_cuenta if afiliado.datos_bancarios else None,
            titular_cuenta=afiliado.datos_bancarios.titular if afiliado.datos_bancarios else None,
            codigo_referencia=afiliado.codigo_referencia,
            afiliado_referente_id=afiliado.afiliado_referente_id,
            metadata=metadata_json,
            fecha_creacion=afiliado.fecha_creacion,
            fecha_actualizacion=afiliado.fecha_actualizacion,
            version=afiliado._version,
            correlation_id=afiliado._correlation_id,
            causation_id=afiliado._causation_id
        )
    
    @staticmethod
    def dto_a_entidad(dto: AfiliadoDTO, referencias: Optional[List[ReferenciaDTO]] = None) -> Afiliado:
        """
        Convierte un AfiliadoDTO a agregado Afiliado de dominio.
        
        Args:
            dto: DTO de persistencia
            referencias: Lista opcional de referencias del afiliado
            
        Returns:
            Afiliado: Agregado de dominio reconstruido
        """
        # Deserializar referencias
        referencias_dominio = []
        if referencias:
            for ref_dto in referencias:
                referencia = Referencia(
                    afiliado_referido_id=ref_dto.afiliado_referido_id,
                    fecha_referencia=ref_dto.fecha_referencia,
                    estado=ref_dto.estado
                )
                referencias_dominio.append(referencia)
        
        # Deserializar metadatos
        metadata_dict = {}
        if dto.metadata:
            try:
                metadata_dict = json.loads(dto.metadata)
            except (json.JSONDecodeError, TypeError):
                metadata_dict = {}
        
        # Reconstruir usando la fábrica
        afiliado = FabricaAfiliados.reconstruir_afiliado(
            afiliado_id=dto.id,
            nombres=dto.nombres,
            apellidos=dto.apellidos,
            email=dto.email,
            tipo_documento=dto.tipo_documento,
            numero_documento=dto.numero_documento,
            tipo_afiliado=dto.tipo_afiliado,
            estado=dto.estado,
            porcentaje_comision_base=dto.porcentaje_comision_base,
            fecha_creacion=dto.fecha_creacion,
            telefono=dto.telefono,
            direccion=dto.direccion,
            ciudad=dto.ciudad,
            pais=dto.pais,
            fecha_nacimiento=dto.fecha_nacimiento,
            fecha_expedicion_documento=dto.fecha_expedicion_documento,
            porcentaje_comision_premium=dto.porcentaje_comision_premium,
            monto_minimo_comision=dto.monto_minimo_comision,
            banco=dto.banco,
            tipo_cuenta=dto.tipo_cuenta,
            numero_cuenta=dto.numero_cuenta,
            titular_cuenta=dto.titular_cuenta,
            codigo_referencia=dto.codigo_referencia,
            afiliado_referente_id=dto.afiliado_referente_id,
            referencias=referencias_dominio if referencias_dominio else None,
            metadata=metadata_dict,
            fecha_actualizacion=dto.fecha_actualizacion,
            correlation_id=dto.correlation_id,
            causation_id=dto.causation_id,
            version=dto.version
        )
        
        return afiliado


class MapeadorReferencia:
    """Mapeador entre Referencia de dominio y ReferenciaDTO."""
    
    @staticmethod
    def entidad_a_dto(
        referencia: Referencia, 
        afiliado_referente_id: str,
        referencia_id: Optional[str] = None
    ) -> ReferenciaDTO:
        """
        Convierte una Referencia de dominio a ReferenciaDTO.
        
        Args:
            referencia: Referencia de dominio
            afiliado_referente_id: ID del afiliado que hace la referencia
            referencia_id: ID opcional para la referencia
            
        Returns:
            ReferenciaDTO: DTO para persistencia
        """
        return ReferenciaDTO(
            id=referencia_id or str(uuid.uuid4()),
            afiliado_referente_id=afiliado_referente_id,
            afiliado_referido_id=referencia.afiliado_referido_id,
            estado=referencia.estado,
            fecha_referencia=referencia.fecha_referencia,
            fecha_actualizacion=datetime.now()
        )
    
    @staticmethod
    def dto_a_entidad(dto: ReferenciaDTO) -> Referencia:
        """
        Convierte un ReferenciaDTO a Referencia de dominio.
        
        Args:
            dto: DTO de persistencia
            
        Returns:
            Referencia: Objeto de valor de dominio
        """
        return Referencia(
            afiliado_referido_id=dto.afiliado_referido_id,
            fecha_referencia=dto.fecha_referencia,
            estado=dto.estado
        )


class MapeadorOutboxAfiliados:
    """Mapeador para eventos de outbox de Afiliados."""
    
    @staticmethod
    def evento_a_dto(
        evento_id: str,
        tipo_evento: str,
        agregado_id: str,
        datos_evento: Dict[str, Any],
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None
    ) -> OutboxAfiliadosDTO:
        """
        Convierte datos de evento a OutboxAfiliadosDTO.
        
        Args:
            evento_id: ID del evento
            tipo_evento: Tipo del evento
            agregado_id: ID del agregado que generó el evento
            datos_evento: Datos del evento
            correlation_id: ID de correlación
            causation_id: ID de causación
            
        Returns:
            OutboxAfiliadosDTO: DTO para persistencia del evento
        """
        return OutboxAfiliadosDTO(
            id=evento_id,
            tipo_evento=tipo_evento,
            agregado_id=agregado_id,
            agregado_tipo='Afiliado',
            datos_evento=json.dumps(datos_evento, ensure_ascii=False, default=str),
            procesado=False,
            correlation_id=correlation_id,
            causation_id=causation_id,
            fecha_creacion=datetime.now()
        )
    
    @staticmethod
    def dto_a_evento(dto: OutboxAfiliadosDTO) -> Dict[str, Any]:
        """
        Convierte un OutboxAfiliadosDTO a datos de evento.
        
        Args:
            dto: DTO de persistencia
            
        Returns:
            Dict: Datos del evento deserializados
        """
        datos_evento = {}
        if dto.datos_evento:
            try:
                datos_evento = json.loads(dto.datos_evento)
            except (json.JSONDecodeError, TypeError):
                datos_evento = {}
        
        return {
            'evento_id': dto.id,
            'tipo_evento': dto.tipo_evento,
            'agregado_id': dto.agregado_id,
            'agregado_tipo': dto.agregado_tipo,
            'datos': datos_evento,
            'procesado': dto.procesado,
            'correlation_id': dto.correlation_id,
            'causation_id': dto.causation_id,
            'fecha_creacion': dto.fecha_creacion,
            'fecha_procesamiento': dto.fecha_procesamiento
        }