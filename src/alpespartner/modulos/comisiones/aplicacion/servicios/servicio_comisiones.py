from alpespartner.seedwork.aplicacion.servicios.base import ServicioAplicacion
from alpespartner.config.uow import UnidadTrabajoSQLAlchemy
from alpespartner.modulos.comisiones.infraestructura.repositorios_sqlalchemy import RepoComisionesSQLAlchemy

class ServicioComisiones(ServicioAplicacion):
    
    def calcular(self, dto):
        """
        Servicio actualizado para usar UoW con eventos CDC
        """
        from alpespartner.modulos.comisiones.infraestructura.repositorios_eventos import RepositorioEventosComisionSQLAlchemy
        
        def repositorio_eventos_func():
            return RepositorioEventosComisionSQLAlchemy()
        
        with UnidadTrabajoSQLAlchemy() as uow:
            repo = RepoComisionesSQLAlchemy(uow)
            
            # Crear comisión que ahora hereda de AgregacionRaiz y registra eventos
            commission_id = repo.crear_desde_datos(
                dto.conversionId, 
                dto.affiliateId, 
                dto.campaignId, 
                dto.grossAmount, 
                dto.currency
            )
            
            # Confirmar transacción con manejo de eventos CDC
            uow.commit(repositorio_eventos_func=repositorio_eventos_func)
            
            return {'commissionId': commission_id}
    
    def aprobar(self, commission_id: str):
        """
        Servicio de aprobación actualizado para manejar eventos CDC
        """
        from alpespartner.modulos.comisiones.infraestructura.repositorios_eventos import RepositorioEventosComisionSQLAlchemy
        
        def repositorio_eventos_func():
            return RepositorioEventosComisionSQLAlchemy()
            
        with UnidadTrabajoSQLAlchemy() as uow:
            repo = RepoComisionesSQLAlchemy(uow)
            
            # Aprobar comisión - esto generará evento ComisionAprobada
            repo.aprobar(commission_id)
            
            # Confirmar transacción con manejo de eventos CDC
            uow.commit(repositorio_eventos_func=repositorio_eventos_func)
            
            return {'ok': True}
