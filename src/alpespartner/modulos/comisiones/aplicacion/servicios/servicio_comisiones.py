from alpespartner.seedwork.aplicacion.servicios.base import ServicioAplicacion
from alpespartner.seedwork.infraestructura.uow import uow
from alpespartner.modulos.comisiones.infraestructura.repositorios_sqlalchemy import RepoComisionesSQLAlchemy

class ServicioComisiones(ServicioAplicacion):
    
    def calcular(self, dto):
        """
        Servicio actualizado para usar AgregacionRaiz y manejar eventos
        """
        with uow() as s:
            repo = RepoComisionesSQLAlchemy(s)
            
            # Crear comisión que ahora hereda de AgregacionRaiz
            commission_id = repo.crear_desde_datos(
                dto.conversionId, 
                dto.affiliateId, 
                dto.campaignId, 
                dto.grossAmount, 
                dto.currency
            )
            
            # El agregado ahora registra eventos automáticamente
            # Los eventos se capturarán en el UoW commit con repositorio_eventos_func
            
            return {'commissionId': commission_id}
    
    def aprobar(self, commission_id: str):
        """
        Servicio de aprobación actualizado para manejar eventos
        """
        with uow() as s:
            repo = RepoComisionesSQLAlchemy(s)
            
            # Aprobar comisión - esto generará evento ComisionAprobada
            repo.aprobar(commission_id)
            
            # Los eventos se registrarán automáticamente en el agregado
            
            return {'ok': True}
