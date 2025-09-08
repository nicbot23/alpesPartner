import uuid
from aeroalpes.modulos.comisiones.dominio.agregados import Comision
from aeroalpes.modulos.comisiones.dominio.eventos import ComisionCalculada, ComisionAprobada
from ..modelos import Commission, OutboxEvent


def _uuid(): 
    return str(uuid.uuid4())

def a_modelo(agregado:Comision)->Commission:
    return Commission(
        id=agregado.id, 
        conversion_id=agregado.conversion_id, 
        affiliate_id=agregado.affiliate_id,
        campaign_id=agregado.campaign_id, 
        gross_amount=float(agregado.bruto.monto), 
        gross_currency=agregado.bruto.moneda,
        percentage=float(agregado.porcentaje), 
        net_amount=float(agregado.neto.monto), 
        net_currency=agregado.neto.moneda,
        status=agregado.status, 
        calculated_at=agregado.calculated_at, 
        approved_at=agregado.approved_at
    )

def a_outbox(evt, agregado:Comision)-> OutboxEvent| None:
    
    if isinstance(evt, ComisionCalculada):
        payload={
            "eventVersion":2,
            "commissionId":evt.commission_id,
            "conversionId":agregado.conversion_id,
            "affiliateId":agregado.affiliate_id,
            "campaignId":agregado.campaign_id,
            "grossAmount":{
                "amount":float(agregado.bruto.monto),
                "currency":agregado.bruto.moneda
            },
            "percentage":float(agregado.porcentaje),
            "netAmount":{
                "amount":float(agregado.neto.monto),
                "currency":agregado.neto.moneda
            }
        }
        return OutboxEvent(
            id=_uuid(),
            aggregate_type='Commission',
            aggregate_id=evt.commission_id,
            event_type='CommissionCalculated',
            payload=payload,
            occurred_at=agregado.calculated_at,
            published=False
        )
    
    if isinstance(evt, ComisionAprobada):
        payload={
            "eventVersion":1,
            "commissionId":evt.commission_id,
            "approvedAt":agregado.approved_at.isoformat()+'Z'
        }
        return OutboxEvent(
            id=_uuid(),
            aggregate_type='Commission',
            aggregate_id=evt.commission_id,
            event_type='CommissionApproved',
            payload=payload,
            occurred_at=agregado.approved_at,
            published=False
        )
    return None
