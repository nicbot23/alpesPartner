from dataclasses import dataclass
from sqlalchemy import select
from alpespartner.seedwork.aplicacion.queries import Query
from alpespartner.seedwork.aplicacion.mediador import manejador_query
from alpespartner.seedwork.infraestructura.uow import uow
from alpespartner.modulos.comisiones.infraestructura.modelos import Commission

@dataclass(frozen=True)
class ComisionPorConversion(Query): 
    conversionId:str

@manejador_query(ComisionPorConversion)
def ejecutar(q: ComisionPorConversion):
    with uow() as s:
        row=s.execute(select(Commission).where(Commission.conversion_id==q.conversionId)).scalar_one_or_none()
        return None if not row else {'commissionId':row.id,'status':row.status,'netAmount':float(row.net_amount),'currency':row.net_currency}
