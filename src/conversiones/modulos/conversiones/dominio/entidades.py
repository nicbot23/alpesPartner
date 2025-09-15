"""
Entidades de dominio para el microservicio Conversiones
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from ....seedwork.dominio.entidades import AgregacionRaiz
from .eventos import ConversionDetectada, ConversionValidada, ConversionRechazada, ConversionActualizada
import uuid


@dataclass
class Conversion(AgregacionRaiz):
    """Agregación raíz para el dominio de Conversiones"""
    user_id: str = ""
    tipo_conversion: str = ""
    valor: Decimal = field(default_factory=lambda: Decimal('0.00'))
    moneda: str = "USD"
    estado: str = "detectada"  # detectada, validada, rechazada
    metadata: str = ""
    fecha_conversion: datetime = field(default_factory=datetime.utcnow)
    observaciones: str = ""
    
    @classmethod
    def detectar_conversion(cls, user_id: str, tipo_conversion: str, valor: Decimal, 
                          moneda: str = "USD", metadata: str = "") -> 'Conversion':
        """Factory method para detectar una nueva conversión"""
        conversion = cls(
            id=cls.siguiente_id(),
            user_id=user_id,
            tipo_conversion=tipo_conversion,
            valor=valor,
            moneda=moneda,
            estado="detectada",
            metadata=metadata,
            fecha_conversion=datetime.utcnow()
        )
        
        # Agregar evento de dominio
        evento = ConversionDetectada(
            conversion_id=str(conversion.id),
            user_id=user_id,
            tipo_conversion=tipo_conversion,
            valor=str(valor),
            moneda=moneda,
            metadata=metadata,
            fecha_conversion=conversion.fecha_conversion
        )
        conversion.agregar_evento(evento)
        
        return conversion
    
    def validar(self, observaciones: str = "") -> None:
        """Validar la conversión"""
        if self.estado != "detectada":
            raise ValueError("Solo se pueden validar conversiones en estado 'detectada'")
        
        self.estado = "validada"
        self.observaciones = observaciones
        self.fecha_actualizacion = datetime.utcnow()
        
        # Agregar evento de dominio
        evento = ConversionValidada(
            conversion_id=str(self.id),
            user_id=self.user_id,
            estado_validacion="validada",
            valor_validado=str(self.valor),
            observaciones=observaciones,
            fecha_validacion=self.fecha_actualizacion
        )
        self.agregar_evento(evento)
    
    def rechazar(self, razon_rechazo: str, observaciones: str = "") -> None:
        """Rechazar la conversión"""
        if self.estado != "detectada":
            raise ValueError("Solo se pueden rechazar conversiones en estado 'detectada'")
        
        self.estado = "rechazada"
        self.observaciones = f"Rechazada: {razon_rechazo}. {observaciones}".strip()
        self.fecha_actualizacion = datetime.utcnow()
        
        # Agregar evento de dominio
        evento = ConversionRechazada(
            conversion_id=str(self.id),
            user_id=self.user_id,
            razon_rechazo=razon_rechazo,
            observaciones=observaciones,
            fecha_rechazo=self.fecha_actualizacion
        )
        self.agregar_evento(evento)
    
    def actualizar_valor(self, nuevo_valor: Decimal, tipo_actualizacion: str = "manual") -> None:
        """Actualizar el valor de la conversión"""
        valor_anterior = self.valor
        self.valor = nuevo_valor
        self.fecha_actualizacion = datetime.utcnow()
        
        # Agregar evento de dominio
        evento = ConversionActualizada(
            conversion_id=str(self.id),
            user_id=self.user_id,
            valor_anterior=str(valor_anterior),
            valor_nuevo=str(nuevo_valor),
            tipo_actualizacion=tipo_actualizacion,
            fecha_actualizacion=self.fecha_actualizacion
        )
        self.agregar_evento(evento)