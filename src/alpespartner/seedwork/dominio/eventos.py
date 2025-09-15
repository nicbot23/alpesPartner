from dataclasses import dataclass, field
from datetime import datetime
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion
import uuid
from typing import Optional, TypeVar, Type

E = TypeVar('E', bound='EventoDominio')

@dataclass(frozen=True)
class EventoDominio():
    nombre: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    fecha: datetime = field(default_factory=datetime.now)
    # Identificador que permite correlacionar una cadena de eventos (trazabilidad end-to-end)
    correlation_id: Optional[str] = None
    # Identificador del evento que causó (directamente) este evento
    causation_id: Optional[str] = None

    @classmethod
    def siguiente_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: uuid.UUID) -> None:
        if not IdEntidadEsInmutable(self).es_valido():
            raise IdDebeSerInmutableExcepcion()
        self._id = self.siguiente_id()

    # Helper para encadenar eventos preservando correlación/causación
    def encadenar(self: E, nuevo_evento_cls: Type[E], **kwargs) -> E:
        """Crea un nuevo evento que desciende de este preservando correlation/causation.

        - correlation_id: se mantiene (si no existe se usa el id de este evento)
        - causation_id: id de este evento
        """
        base_corr = self.correlation_id or str(self.id)
        return nuevo_evento_cls(
            correlation_id=base_corr,
            causation_id=str(self.id),
            **kwargs
        )
