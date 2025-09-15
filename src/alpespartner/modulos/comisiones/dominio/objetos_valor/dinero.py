from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Dinero: 
    monto:Decimal; 
    moneda:str
