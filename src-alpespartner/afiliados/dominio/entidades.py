from dataclasses import dataclass, field
from typing import Optional, List
import uuid

@dataclass
class Afiliado:
    id: str
    nombre: str
    email: str
    tipo_afiliado: str  # INDIVIDUAL, EMPRESA, INFLUENCER
    nivel_comision: str  # BASICO, PREMIUM, VIP
    fecha_registro: Optional[str] = None
    condiciones_especiales: Optional[str] = None
    estado: str = "PENDIENTE"  # ACTIVO, INACTIVO, PENDIENTE, RECHAZADO
    eventos: List = field(default_factory=list)

    def aplicar_evento(self, evento):
        self.eventos.append(evento)
        # Aquí se puede agregar lógica para modificar el estado según el evento
