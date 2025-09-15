"""
Entidades del dominio de afiliados
"""
from dataclasses import dataclass, field
from afiliados.seedwork.dominio.entidades import AgregacionRaiz
from .eventos import AfiliadoRegistrado, AfiliadoAprobado, AfiliadoRechazado, AfiliadoActualizado, AfiliadoDesactivado
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class Afiliado(AgregacionRaiz):
    """Agregación raíz para el dominio de afiliados"""
    nombre: str = ""
    tipo_afiliacion: str = ""  # individual, empresa, etc.
    email: str = ""
    telefono: str = ""
    direccion: str = ""
    estado: str = "pendiente"  # pendiente, aprobado, rechazado, desactivado
    fecha_registro: datetime = field(default_factory=datetime.now)
    fecha_aprobacion: Optional[datetime] = None
    observaciones: str = ""
    
    @classmethod
    def registrar(cls, nombre: str, tipo_afiliacion: str, email: str, telefono: str = "", direccion: str = "") -> 'Afiliado':
        """Factory method para registrar un nuevo afiliado"""
        afiliado = cls(
            id=cls.siguiente_id(),
            nombre=nombre,
            tipo_afiliacion=tipo_afiliacion,
            email=email,
            telefono=telefono,
            direccion=direccion,
            estado="pendiente",
            fecha_registro=datetime.now()
        )
        
        # Agregar evento de dominio
        evento = AfiliadoRegistrado(
            nombre=nombre,
            tipo_afiliacion=tipo_afiliacion,
            email=email,
            telefono=telefono,
            direccion=direccion
        )
        afiliado.agregar_evento(evento)
        
        return afiliado
    
    def aprobar(self, aprobado_por: str, observaciones: str = ""):
        """Aprobar un afiliado"""
        if self.estado != "pendiente":
            raise ValueError(f"No se puede aprobar un afiliado en estado {self.estado}")
        
        self.estado = "aprobado"
        self.fecha_aprobacion = datetime.now()
        self.observaciones = observaciones
        self.fecha_actualizacion = datetime.now()
        
        # Agregar evento de dominio
        evento = AfiliadoAprobado(
            afiliado_id=str(self.id),
            aprobado_por=aprobado_por,
            observaciones=observaciones
        )
        self.agregar_evento(evento)
    
    def rechazar(self, rechazado_por: str, razon_rechazo: str):
        """Rechazar un afiliado"""
        if self.estado != "pendiente":
            raise ValueError(f"No se puede rechazar un afiliado en estado {self.estado}")
        
        self.estado = "rechazado"
        self.observaciones = razon_rechazo
        self.fecha_actualizacion = datetime.now()
        
        # Agregar evento de dominio
        evento = AfiliadoRechazado(
            afiliado_id=str(self.id),
            rechazado_por=rechazado_por,
            razon_rechazo=razon_rechazo
        )
        self.agregar_evento(evento)
    
    def actualizar_datos(self, actualizado_por: str, **kwargs):
        """Actualizar datos del afiliado"""
        campos_actualizados = {}
        
        for campo, valor in kwargs.items():
            if hasattr(self, campo) and getattr(self, campo) != valor:
                campos_actualizados[campo] = {"anterior": getattr(self, campo), "nuevo": valor}
                setattr(self, campo, valor)
        
        if campos_actualizados:
            self.fecha_actualizacion = datetime.now()
            
            # Agregar evento de dominio
            import json
            evento = AfiliadoActualizado(
                afiliado_id=str(self.id),
                campos_actualizados=json.dumps(campos_actualizados),
                actualizado_por=actualizado_por
            )
            self.agregar_evento(evento)
    
    def desactivar(self, desactivado_por: str, razon_desactivacion: str):
        """Desactivar un afiliado"""
        if self.estado == "desactivado":
            raise ValueError("El afiliado ya está desactivado")
        
        self.estado = "desactivado"
        self.observaciones = razon_desactivacion
        self.fecha_actualizacion = datetime.now()
        
        # Agregar evento de dominio
        evento = AfiliadoDesactivado(
            afiliado_id=str(self.id),
            desactivado_por=desactivado_por,
            razon_desactivacion=razon_desactivacion
        )
        self.agregar_evento(evento)