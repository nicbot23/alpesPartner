from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ComisionCalculada: 
    commission_id:str; 
    occurred_at:datetime

@dataclass(frozen=True)
class ComisionAprobada: 
    commission_id:str; 
    occurred_at:datetime
