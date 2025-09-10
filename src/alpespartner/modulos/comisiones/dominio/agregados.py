from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from alpespartner.seedwork.dominio.entidades import RaizAgregado
from .objetos_valor.dinero import Dinero
from .eventos import ComisionCalculada, ComisionAprobada

def _uuid(): 
    return str(uuid.uuid4())

@dataclass
class Comision(RaizAgregado):
    conversion_id:str; 
    affiliate_id:str; 
    campaign_id:str
    bruto:Dinero; 
    porcentaje:Decimal; 
    neto:Dinero
    status:str='CALCULATED'; 
    calculated_at:datetime=datetime.utcnow(); 
    approved_at:Optional[datetime]=None
    
    @staticmethod
    def calcular(conversion_id, affiliate_id, campaign_id, bruto:Dinero, pct:Decimal):
        net=(bruto.monto*pct/Decimal(100)).quantize(Decimal('0.01'))
        c=Comision(
            id=_uuid(), 
            conversion_id=conversion_id, 
            affiliate_id=affiliate_id, 
            campaign_id=campaign_id,
            bruto=bruto, 
            porcentaje=pct, 
            neto=Dinero(net, bruto.moneda)
        )

        c.agregar_evento(ComisionCalculada(commission_id=c.id, occurred_at=c.calculated_at))
        
        return c

    def aprobar(self):
        from datetime import datetime as dt
        self.status='APPROVED'; 
        self.approved_at=dt.utcnow()
        self.agregar_evento(ComisionAprobada(commission_id=self.id, 
                                             occurred_at=self.approved_at)
                            )
