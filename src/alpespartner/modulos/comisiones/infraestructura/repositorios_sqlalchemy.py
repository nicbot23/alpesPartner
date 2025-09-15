from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from alpespartner.modulos.comisiones.dominio.repositorios.repositorios import RepositorioComisiones
from alpespartner.modulos.comisiones.dominio.agregados import Comision
from alpespartner.modulos.comisiones.infraestructura.mapeadores.mapeadores import a_modelo, a_outbox
from .modelos import Commission
from alpespartner.seedwork.infraestructura.outbox.modelos import OutboxEvent
from alpespartner.config.db import db

class RepoComisionesSQLAlchemy(RepositorioComisiones):
    def __init__(self, uow=None): 
        # Usar la sesión de la UoW o la sesión de Flask-SQLAlchemy
        self.session = db.session if not uow else db.session
    
    def _pct(self)->Decimal:
        pct=self.session.execute(text("SELECT JSON_EXTRACT(payload,'$.percentage') FROM commission_rule LIMIT 1")).scalar_one()
        return Decimal(pct)
    
    def agregar(self, comision:Comision)->str:
        """
        Agregar actualizado para usar AgregacionRaiz con eventos
        """
        # Convertir agregado a modelo SQLAlchemy
        modelo = a_modelo(comision)
        self.session.add(modelo)
        
        # Los eventos se procesarán en el UoW commit, no aquí
        # Esto permite que el patrón CDC funcione correctamente
        
        return comision.id
    
    def crear_desde_datos(self, conversion_id, affiliate_id, campaign_id, bruto, currency)->str:
        """
        Crear comisión usando factory pattern y AgregacionRaiz
        """
        pct=self._pct()
        from alpespartner.modulos.comisiones.dominio.fabricas.fabricas import FabricaComisiones
        
        # Crear agregado con eventos automáticos
        agg=FabricaComisiones.crear_calculada(
            conversion_id, affiliate_id, campaign_id, 
            float(bruto), currency, float(pct)
        )
        
        # Agregar a la sesión - los eventos se procesarán en commit
        return self.agregar(agg)
    
    def aprobar(self, commission_id:str)->None:
        """
        Aprobar comisión generando eventos de dominio
        """
        # Obtener modelo de la BD
        cm=self.session.get(Commission, commission_id)
        if not cm: raise ValueError('Commission not found')
        
        # Actualizar estado
        cm.status='APPROVED'
        from datetime import datetime as dt
        cm.approved_at=dt.utcnow()
        
        # Crear evento de dominio (se procesará en UoW commit)
        from alpespartner.modulos.comisiones.dominio.eventos import ComisionAprobada
        from alpespartner.modulos.comisiones.dominio.agregados import Comision
        
        # TODO: Recuperar agregado completo para generar evento correctamente
        # Por ahora creamos evento simple
        evento = ComisionAprobada(commission_id=commission_id, occurred_at=cm.approved_at)
        
        # Crear outbox entry directamente por compatibilidad
        out=OutboxEvent(
            aggregate_type='Commission', 
            aggregate_id=commission_id, 
            event_type='CommissionApproved', 
            id=str(__import__('uuid').uuid4()), 
            payload={
                'eventVersion':1,
                'commissionId':commission_id,
                'approvedAt':cm.approved_at.isoformat()+'Z'
            }, 
            occurred_at=cm.approved_at, 
            published=False
        )
        self.session.add(out)

    def obtener_por_conversion(self, conversion_id:str)->dict|None:
        """Obtiene datos básicos de una comisión por conversion_id"""
        cm=self.session.query(Commission).filter(Commission.conversion_id==conversion_id).one_or_none()
        if not cm:
            return None
        return {
            'commissionId':cm.id,
            'status':cm.status,
            'netAmount':float(cm.net_amount),
            'currency':cm.net_currency
        }
