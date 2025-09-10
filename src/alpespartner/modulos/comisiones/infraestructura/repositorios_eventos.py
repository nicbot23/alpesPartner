"""Implementación SQL del repositorio de eventos de comisiones

En este archivo usted encontrará la implementación SQL del repositorio
de eventos usando el patrón Outbox

"""

import uuid
import json
from sqlalchemy.orm import Session
from pulsar.schema import JsonSchema
from alpespartner.modulos.comisiones.dominio.repositorios.repositorios_eventos import RepositorioEventosComision
from alpespartner.modulos.comisiones.dominio.eventos import EventoComision
from alpespartner.modulos.comisiones.dominio.fabricas.fabricas import FabricaComisiones
from .mapeadores.mapeadores import MapeadorEventosComision
from .modelos import OutboxEvent

class RepositorioEventosComisionSQLAlchemy(RepositorioEventosComision):
    
    def __init__(self, session: Session):
        self.session = session
        self._fabrica_comisiones = FabricaComisiones()
        self._mapeador = MapeadorEventosComision()

    @property
    def fabrica_comisiones(self):
        return self._fabrica_comisiones

    def agregar(self, evento: EventoComision):
        # Transformar evento dominio → evento integración usando mapeador
        comision_evento = self._fabrica_comisiones.crear_objeto(evento, self._mapeador)
        
        # Serializar a JSON usando JsonSchema de Pulsar
        parser_payload = JsonSchema(comision_evento.data.__class__)
        json_str = parser_payload.encode(comision_evento.data)

        # Crear DTO para tabla outbox
        evento_dto = OutboxEvent(
            id=str(uuid.uuid4()),
            aggregate_type='Commission',
            aggregate_id=str(evento.commission_id),
            event_type=evento.__class__.__name__,
            payload=json.loads(json_str) if isinstance(json_str, str) else json_str,
            occurred_at=evento.occurred_at,
            published=False
        )
        
        self.session.add(evento_dto)
