from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from alpespartner.modulos.comisiones.dominio.repositorios.repositorios import RepositorioComisiones
from alpespartner.modulos.comisiones.dominio.agregados import Comision
from alpespartner.modulos.comisiones.infraestructura.mapeadores.mapeadores import a_modelo, a_outbox
from .modelos import Commission, OutboxEvent
class RepoComisionesSQLAlchemy(RepositorioComisiones):
    def __init__(self, s: Session): 
        self.s=s
    
    def _pct(self)->Decimal:
        pct=self.s.execute(text("SELECT JSON_EXTRACT(payload,'$.percentage') FROM commission_rule LIMIT 1")).scalar_one()
        return Decimal(pct)
    
    def agregar(self, comision:Comision)->str:
        self.s.add(a_modelo(comision))
        for evt in comision.pull_eventos():
            out=a_outbox(evt, comision) # agrega a outbox 
            if out: self.s.add(out)
        return comision.id
    
    def crear_desde_datos(self, conversion_id, affiliate_id, campaign_id, bruto, currency)->str:
        pct=self._pct()
        from alpespartner.modulos.comisiones.dominio.fabricas.fabricas import FabricaComisiones
        agg=FabricaComisiones.crear_calculada(conversion_id, affiliate_id, campaign_id, float(bruto), currency, float(pct))
        return self.agregar(agg)
    
    def aprobar(self, commission_id:str)->None:
        cm=self.s.get(Commission, commission_id)
        if not cm: raise ValueError('Commission not found')
        cm.status='APPROVED'
        from datetime import datetime as dt
        cm.approved_at=dt.utcnow()
        out=OutboxEvent(aggregate_type='Commission', aggregate_id=commission_id, event_type='CommissionApproved', id=str(__import__('uuid').uuid4()), payload={'eventVersion':1,'commissionId':commission_id,'approvedAt':cm.approved_at.isoformat()+'Z'}, occurred_at=cm.approved_at, published=False)
        self.s.add(out)

    def obtener_por_conversion(self, conversion_id:str)->dict|None:
        cm=self.s.query(Commission).filter(Commission.conversion_id==conversion_id).one_or_none()
        if not cm: return None
        return {'commissionId':cm.id,'status':cm.status,'netAmount':float(cm.net_amount),'currency':cm.net_currency}
