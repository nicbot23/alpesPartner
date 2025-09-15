from .mensajes import Mensaje
from typing import Any

class EventoIntegracion(Mensaje):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
