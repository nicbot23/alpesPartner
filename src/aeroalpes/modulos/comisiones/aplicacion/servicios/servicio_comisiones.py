from aeroalpes.seedwork.aplicacion.servicios.base import ServicioAplicacion
from aeroalpes.seedwork.infraestructura.uow import uow
from aeroalpes.modulos.comisiones.infraestructura.repositorios_sqlalchemy import RepoComisionesSQLAlchemy

class ServicioComisiones(ServicioAplicacion):
    
    def calcular(self, dto):
        with uow() as s:
            repo=RepoComisionesSQLAlchemy(s)
            return {'commissionId': repo.crear_desde_datos(
                dto.conversionId, 
                dto.affiliateId, 
                dto.campaignId, 
                dto.grossAmount, 
                dto.currency)   
            }
    
    def aprobar(self, commission_id:str):
        with uow() as s:
            repo=RepoComisionesSQLAlchemy(s); 
            repo.aprobar(commission_id); 
            return {'ok': True}
