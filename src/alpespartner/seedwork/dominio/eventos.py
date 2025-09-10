from dataclasses import dataclass, field
from datetime import datetime
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion
import uuid

@dataclass(frozen=True)
class EventoDominio():
    nombre: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    fecha: datetime = field(default_factory=datetime.now)

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
