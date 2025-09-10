"""Implementación SQL del repositorio de eventos de comisiones

En este archivo usted encontrará la implementación SQL del repositorio
de eventos usando el patrón Outbox

"""

import uuid
import json
from sqlalchemy.orm import Session
from datetime import datetime
from pulsar.schema import JsonSchema
from alpespartner.modulos.comisiones.dominio.repositorios.repositorios_eventos import RepositorioEventosComision
from alpespartner.modulos.comisiones.dominio.eventos import EventoComision, ComisionCalculada, ComisionAprobada
from alpespartner.modulos.comisiones.dominio.fabricas.fabricas import FabricaComisiones
from .mapeadores.mapeadores import MapeadorEventosComision
from .modelos import OutboxEvent
from alpespartner.config.db import db

class RepositorioEventosComisionSQLAlchemy(RepositorioEventosComision):
    
    def __init__(self, session: Session = None):
        self.session = session or db.session
        self._fabrica_comisiones = FabricaComisiones()
        self._mapeador = MapeadorEventosComision()

    @property
    def fabrica_comisiones(self):
        return self._fabrica_comisiones

    def agregar(self, evento: EventoComision):
        """
        Agregar evento al outbox para CDC - método simplificado para pruebas
        """
        try:
            # Crear payload básico
            if isinstance(evento, ComisionCalculada):
                payload = {
                    "eventVersion": 2,
                    "commissionId": str(evento.commission_id),
                    "occurredAt": int(evento.occurred_at.timestamp() * 1000) if hasattr(evento, 'occurred_at') and evento.occurred_at else int(datetime.utcnow().timestamp() * 1000)
                }
                event_type = 'CommissionCalculated'
                
            elif isinstance(evento, ComisionAprobada):
                payload = {
                    "eventVersion": 1,
                    "commissionId": str(evento.commission_id),
                    "occurredAt": int(evento.occurred_at.timestamp() * 1000) if hasattr(evento, 'occurred_at') and evento.occurred_at else int(datetime.utcnow().timestamp() * 1000)
                }
                event_type = 'CommissionApproved'
                
            else:
                # Fallback para otros eventos
                payload = {
                    "eventVersion": 1,
                    "commissionId": str(getattr(evento, 'commission_id', '')),
                    "occurredAt": int(datetime.utcnow().timestamp() * 1000)
                }
                event_type = evento.__class__.__name__

            # Crear entrada en outbox
            evento_dto = OutboxEvent(
                id=str(uuid.uuid4()),
                aggregate_type='Commission',
                aggregate_id=str(getattr(evento, 'commission_id', '')),
                event_type=event_type,
                payload=payload,
                occurred_at=getattr(evento, 'occurred_at', datetime.utcnow()),
                published=False
            )
            
            self.session.add(evento_dto)
            
        except Exception as e:
            print(f"Error agregando evento al outbox: {str(e)}")
            # Crear entrada básica para no fallar
            evento_dto = OutboxEvent(
                id=str(uuid.uuid4()),
                aggregate_type='Commission',
                aggregate_id=str(getattr(evento, 'commission_id', 'unknown')),
                event_type=evento.__class__.__name__,
                payload={"eventVersion": 1, "error": str(e)},
                occurred_at=datetime.utcnow(),
                published=False
            )
            self.session.add(evento_dto)
