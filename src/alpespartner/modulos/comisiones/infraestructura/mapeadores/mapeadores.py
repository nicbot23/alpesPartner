import uuid
from alpespartner.modulos.comisiones.dominio.agregados import Comision
from alpespartner.modulos.comisiones.dominio.eventos import ComisionCalculada, ComisionAprobada
from alpespartner.seedwork.infraestructura.utils import unix_time_millis
from ..modelos import Commission, OutboxEvent
from alpespartner.seedwork.dominio.eventos import (EventoDominio)
from alpespartner.modulos.comisiones.dominio.eventos import EventoComision, ComisionCalculada, ComisionAprobada
from alpespartner.seedwork.dominio.repositorios.base import Mapeador


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


class MapeadorEventosComision(Mapeador):
    
    # Versiones aceptadas
    versions = ('v1', 'v2')

    LATEST_VERSION = versions[1]  # v2 como última versión

    def __init__(self, version=None):
        self.router = {
            ComisionCalculada: self._entidad_a_comision_calculada,
            ComisionAprobada: self._entidad_a_comision_aprobada
        }

    def obtener_tipo(self) -> type:
        return EventoComision.__class__

    def es_version_valida(self, version):
        return version in self.versions

    def _entidad_a_comision_calculada(self, entidad: ComisionCalculada, version=LATEST_VERSION):
        def v1(evento):
            from alpespartner.modulos.comisiones.infraestructura.schema.v1.eventos import ComisionCalculadaPayload, EventoComisionCalculada
            
            payload = ComisionCalculadaPayload(
                commission_id=str(evento.commission_id),
                occurred_at=int(unix_time_millis(evento.occurred_at))
            )
            evento_integracion = EventoComisionCalculada(id=str(evento.commission_id))
            evento_integracion.id = str(evento.commission_id)
            evento_integracion.time = int(unix_time_millis(evento.occurred_at))
            evento_integracion.specversion = str(version)
            evento_integracion.type = 'ComisionCalculada'
            evento_integracion.datacontenttype = 'AVRO'
            evento_integracion.service_name = 'alpespartner'
            evento_integracion.data = payload

            return evento_integracion

        def v2(evento):
            from alpespartner.modulos.comisiones.infraestructura.schema.v2.eventos import ComisionCalculadaPayload, EventoComisionCalculada

            # Obtener el agregado asociado para datos completos
            agregado = self._obtener_agregado(evento.commission_id)
            
            payload = ComisionCalculadaPayload(
                commission_id=str(evento.commission_id),
                conversion_id=str(agregado.conversion_id) if agregado else "",
                affiliate_id=str(agregado.affiliate_id) if agregado else "",
                campaign_id=str(agregado.campaign_id) if agregado else "",
                gross_amount=f'{{"amount": {float(agregado.bruto.monto)}, "currency": "{agregado.bruto.moneda}"}}' if agregado else "{}",
                percentage=float(agregado.porcentaje) if agregado else 0.0,
                net_amount=f'{{"amount": {float(agregado.neto.monto)}, "currency": "{agregado.neto.moneda}"}}' if agregado else "{}",
                occurred_at=int(unix_time_millis(evento.occurred_at))
            )
            evento_integracion = EventoComisionCalculada(id=str(evento.commission_id))
            evento_integracion.id = str(evento.commission_id)
            evento_integracion.time = int(unix_time_millis(evento.occurred_at))
            evento_integracion.specversion = str(version)
            evento_integracion.type = 'ComisionCalculada'
            evento_integracion.datacontenttype = 'AVRO'
            evento_integracion.service_name = 'alpespartner'
            evento_integracion.data = payload

            return evento_integracion
                    
        if not self.es_version_valida(version):
            raise Exception(f'No se sabe procesar la version {version}')

        if version == 'v1':
            return v1(entidad)
        elif version == 'v2':
            return v2(entidad)
        
    def _entidad_a_comision_aprobada(self, entidad: ComisionAprobada, version=LATEST_VERSION):
        def v1(evento):
            from alpespartner.modulos.comisiones.infraestructura.schema.v1.eventos import ComisionAprobadaPayload, EventoComisionAprobada
            
            payload = ComisionAprobadaPayload(
                commission_id=str(evento.commission_id),
                approved_at=int(unix_time_millis(evento.occurred_at))
            )
            evento_integracion = EventoComisionAprobada(id=str(evento.commission_id))
            evento_integracion.id = str(evento.commission_id)
            evento_integracion.time = int(unix_time_millis(evento.occurred_at))
            evento_integracion.specversion = str(version)
            evento_integracion.type = 'ComisionAprobada'
            evento_integracion.datacontenttype = 'AVRO'
            evento_integracion.service_name = 'alpespartner'
            evento_integracion.data = payload

            return evento_integracion

        def v2(evento):
            from alpespartner.modulos.comisiones.infraestructura.schema.v2.eventos import ComisionAprobadaPayload, EventoComisionAprobada

            # Obtener el agregado asociado para datos completos
            agregado = self._obtener_agregado(evento.commission_id)
            
            payload = ComisionAprobadaPayload(
                commission_id=str(evento.commission_id),
                conversion_id=str(agregado.conversion_id) if agregado else "",
                affiliate_id=str(agregado.affiliate_id) if agregado else "",
                campaign_id=str(agregado.campaign_id) if agregado else "",
                approved_at=int(unix_time_millis(evento.occurred_at))
            )
            evento_integracion = EventoComisionAprobada(id=str(evento.commission_id))
            evento_integracion.id = str(evento.commission_id)
            evento_integracion.time = int(unix_time_millis(evento.occurred_at))
            evento_integracion.specversion = str(version)
            evento_integracion.type = 'ComisionAprobada'
            evento_integracion.datacontenttype = 'AVRO'
            evento_integracion.service_name = 'alpespartner'
            evento_integracion.data = payload

            return evento_integracion
                    
        if not self.es_version_valida(version):
            raise Exception(f'No se sabe procesar la version {version}')

        if version == 'v1':
            return v1(entidad)
        elif version == 'v2':
            return v2(entidad)

    def _obtener_agregado(self, commission_id):
        # Método auxiliar para obtener el agregado completo cuando sea necesario
        # Implementar según tu arquitectura de repositorios
        from alpespartner.modulos.comisiones.infraestructura.repositorios_sqlalchemy import RepoComisionesSQLAlchemy
        from alpespartner.seedwork.infraestructura.db import SessionLocal
        
        with SessionLocal() as session:
            repositorio = RepoComisionesSQLAlchemy(session)
            # Por ahora retornamos None, se debe implementar método en repositorio
            return None

    def entidad_a_dto(self, entidad: EventoComision, version=LATEST_VERSION) -> any:
        if not entidad:
            raise Exception('Entidad no puede ser None')
        func = self.router.get(entidad.__class__, None)

        if not func:
            raise Exception(f'No existe mapeador para el tipo {entidad.__class__}')

        return func(entidad, version=version)

    def dto_a_entidad(self, dto: any, version=LATEST_VERSION) -> EventoComision:
        raise NotImplementedError('dto_a_entidad no implementado')
    
