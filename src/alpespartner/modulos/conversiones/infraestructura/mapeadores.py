"""
Mapeadores para Conversiones
Transforman entre agregado, DTO y eventos outbox
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from ..dominio.agregados import Conversion
from ..dominio.objetos_valor import (
    TipoConversion, EstadoConversion, DatosAfiliado,
    DatosCampana, DatosTransaccion, MetadatosConversion
)
from ..dominio.eventos import (
    ConversionCreated, ConversionConfirmed, ConversionRejected,
    ConversionCancelled, ConversionValidated, ConversionAttributed
)
from .modelos import ConversionDTO, ConversionOutboxEvent


def _uuid() -> str:
    return str(uuid.uuid4())


def conversion_a_dto(conversion: Conversion) -> ConversionDTO:
    """Mapea agregado Conversion -> ConversionDTO"""
    return ConversionDTO(
        id=conversion.id,
        conversion_type=conversion.tipo.value,
        estado=conversion.estado.value,
        affiliate_id=conversion.datos_afiliado.affiliate_id,
        affiliate_type=conversion.datos_afiliado.affiliate_type,
        tier_level=conversion.datos_afiliado.tier_level,
        campaign_id=conversion.datos_campana.campaign_id,
        campaign_name=conversion.datos_campana.campaign_name,
        brand=conversion.datos_campana.brand,
        gross_amount=conversion.datos_transaccion.gross_amount,
        currency=conversion.datos_transaccion.currency,
        transaction_id=conversion.datos_transaccion.transaction_id,
        payment_method=conversion.datos_transaccion.payment_method,
        metadatos={
            'user_agent': conversion.metadatos.user_agent,
            'ip_address': conversion.metadatos.ip_address,
            'referrer': conversion.metadatos.referrer,
            'utm_source': conversion.metadatos.utm_source,
            'utm_medium': conversion.metadatos.utm_medium,
            'utm_campaign': conversion.metadatos.utm_campaign,
            'device_type': conversion.metadatos.device_type,
            'geo_country': conversion.metadatos.geo_country,
            'geo_region': conversion.metadatos.geo_region
        } if conversion.metadatos else None,
        created_at=conversion.created_at,
        confirmed_at=conversion.confirmed_at,
        validation_score=conversion.validation_score,
        version=1
    )


def dto_a_conversion(dto: ConversionDTO) -> Conversion:
    """Reconstruye Conversion desde ConversionDTO"""
    from ..dominio.fabricas import FabricaConversiones
    
    return FabricaConversiones.reconstruir_conversion(
        conversion_id=dto.id,
        tipo=dto.conversion_type,
        affiliate_id=dto.affiliate_id,
        affiliate_type=dto.affiliate_type,
        tier_level=dto.tier_level,
        campaign_id=dto.campaign_id,
        campaign_name=dto.campaign_name,
        brand=dto.brand,
        gross_amount=dto.gross_amount,
        currency=dto.currency,
        transaction_id=dto.transaction_id,
        estado=dto.estado,
        created_at=dto.created_at,
        confirmed_at=dto.confirmed_at,
        validation_score=float(dto.validation_score),
        metadatos=dto.metadatos
    )


def evento_a_outbox(evento, conversion: Conversion) -> Optional[ConversionOutboxEvent]:
    """Mapea evento de dominio -> ConversionOutboxEvent"""
    
    def _payload_base(evt, conv: Conversion) -> dict:
        return {
            'aggregate': 'Conversion',
            'conversionId': conv.id,
            'affiliateId': conv.datos_afiliado.affiliate_id,
            'campaignId': conv.datos_campana.campaign_id,
            'brand': conv.datos_campana.brand,
            'eventVersion': 1,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    base = _payload_base(evento, conversion)
    
    if isinstance(evento, ConversionCreated):
        payload = {
            **base,
            'eventType': 'ConversionCreated',
            'conversionType': conversion.tipo.value,
            'grossAmount': {
                'amount': float(conversion.datos_transaccion.gross_amount),
                'currency': conversion.datos_transaccion.currency
            },
            'transactionId': conversion.datos_transaccion.transaction_id,
            'affiliateType': conversion.datos_afiliado.affiliate_type,
            'tierLevel': conversion.datos_afiliado.tier_level
        }
        return ConversionOutboxEvent(
            id=_uuid(),
            aggregate_type='Conversion',
            aggregate_id=conversion.id,
            event_type='ConversionCreated',
            payload=payload,
            occurred_at=evento.occurred_at or datetime.utcnow(),
            correlation_id=evento.correlation_id or str(evento.id),
            causation_id=evento.causation_id
        )
    
    elif isinstance(evento, ConversionConfirmed):
        payload = {
            **base,
            'eventType': 'ConversionConfirmed',
            'grossAmount': {
                'amount': float(conversion.datos_transaccion.gross_amount),
                'currency': conversion.datos_transaccion.currency
            },
            'confirmedAt': evento.confirmed_at.isoformat() + 'Z',
            'validationScore': conversion.validation_score
        }
        return ConversionOutboxEvent(
            id=_uuid(),
            aggregate_type='Conversion',
            aggregate_id=conversion.id,
            event_type='ConversionConfirmed',
            payload=payload,
            occurred_at=evento.confirmed_at or datetime.utcnow(),
            correlation_id=evento.correlation_id or str(evento.id),
            causation_id=evento.causation_id
        )
    
    elif isinstance(evento, ConversionRejected):
        payload = {
            **base,
            'eventType': 'ConversionRejected',
            'rejectionReason': evento.rejection_reason,
            'rejectedAt': evento.rejected_at.isoformat() + 'Z'
        }
        return ConversionOutboxEvent(
            id=_uuid(),
            aggregate_type='Conversion',
            aggregate_id=conversion.id,
            event_type='ConversionRejected',
            payload=payload,
            occurred_at=evento.rejected_at or datetime.utcnow(),
            correlation_id=evento.correlation_id or str(evento.id),
            causation_id=evento.causation_id
        )
    
    elif isinstance(evento, ConversionCancelled):
        payload = {
            **base,
            'eventType': 'ConversionCancelled',
            'cancellationReason': evento.cancellation_reason,
            'cancelledAt': evento.cancelled_at.isoformat() + 'Z'
        }
        return ConversionOutboxEvent(
            id=_uuid(),
            aggregate_type='Conversion',
            aggregate_id=conversion.id,
            event_type='ConversionCancelled',
            payload=payload,
            occurred_at=evento.cancelled_at or datetime.utcnow(),
            correlation_id=evento.correlation_id or str(evento.id),
            causation_id=evento.causation_id
        )
    
    elif isinstance(evento, ConversionValidated):
        # Evento interno - no se publica fuera del contexto
        return None
    
    elif isinstance(evento, ConversionAttributed):
        # Evento interno - no se publica fuera del contexto  
        return None
    
    return None


class MapeadorConversiones:
    """Mapeador para conversiones con métodos estáticos."""
    
    @staticmethod
    def entidad_a_dict(conversion: Conversion) -> dict:
        """Convierte una entidad Conversion a diccionario para respuestas API."""
        return {
            'id': conversion.id,
            'afiliado_id': conversion.datos_afiliado.id,
            'campana_id': conversion.datos_campana.id,
            'tipo_conversion': conversion.tipo_conversion.value,
            'estado': conversion.estado.value,
            'monto_transaccion': float(conversion.datos_transaccion.monto),
            'fecha_conversion': conversion.datos_transaccion.fecha.isoformat(),
            'metadata': conversion.metadata.datos,
            'comision_id': conversion.comision_id,
            'monto_comision': float(conversion.monto_comision) if conversion.monto_comision else None,
            'fecha_creacion': conversion.fecha_creacion.isoformat(),
            'fecha_actualizacion': conversion.fecha_actualizacion.isoformat() if conversion.fecha_actualizacion else None,
            'correlation_id': conversion.correlation_id,
            'causation_id': conversion.causation_id,
            'version': conversion.version
        }