from dataclasses import dataclass
from datetime import datetime
from alpespartner.seedwork.dominio.eventos import (EventoDominio)

class EventoComision(EventoDominio):
    ... # Definición de la clase base para eventos de comisión

@dataclass(frozen=True)
class ComisionCalculada(EventoComision): 
    commission_id:str; 
    occurred_at:datetime

@dataclass(frozen=True)
class ComisionAprobada(EventoComision): 
    commission_id:str; 
    occurred_at:datetime
