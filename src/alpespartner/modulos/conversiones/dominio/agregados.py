"""
Agregado Conversion - Raíz del contexto Conversiones
Gestiona el ciclo de vida de conversiones y su comunicación por eventos
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from alpespartner.seedwork.dominio.entidades import AgregacionRaiz
from .objetos_valor import (
    TipoConversion, EstadoConversion, DatosAfiliado, 
    DatosCampana, DatosTransaccion, MetadatosConversion
)
from .eventos import (
    ConversionCreated, ConversionConfirmed, ConversionRejected,
    ConversionCancelled, ConversionValidated, ConversionAttributed
)


class Conversion(AgregacionRaiz):
    """
    Agregado que representa una interacción de afiliado que puede generar comisión.
    Comunica cambios de estado vía eventos de integración.
    """
    
    def __init__(
        self,
        conversion_id: str,
        tipo: TipoConversion,
        datos_afiliado: DatosAfiliado,
        datos_campana: DatosCampana,
        datos_transaccion: DatosTransaccion,
        metadatos: Optional[MetadatosConversion] = None
    ):
        super().__init__(conversion_id)
        self._tipo = tipo
        self._datos_afiliado = datos_afiliado
        self._datos_campana = datos_campana
        self._datos_transaccion = datos_transaccion
        self._metadatos = metadatos or MetadatosConversion()
        self._estado = EstadoConversion.PENDIENTE
        self._created_at = datetime.utcnow()
        self._confirmed_at = None
        self._rejected_at = None
        self._cancelled_at = None
        self._validation_score = 0.0
        self._attribution_model = "LAST_CLICK"
        
        # Emitir evento de creación
        self.agregar_evento(ConversionCreated(
            conversion_id=self.id,
            affiliate_id=self._datos_afiliado.affiliate_id,
            campaign_id=self._datos_campana.campaign_id,
            conversion_type=self._tipo.value,
            gross_amount=str(self._datos_transaccion.gross_amount),
            currency=self._datos_transaccion.currency,
            transaction_id=self._datos_transaccion.transaction_id,
            correlation_id=str(uuid.uuid4())  # Inicio de cadena de correlación
        ))
    
    @property
    def tipo(self) -> TipoConversion:
        return self._tipo
    
    @property
    def estado(self) -> EstadoConversion:
        return self._estado
    
    @property
    def datos_afiliado(self) -> DatosAfiliado:
        return self._datos_afiliado
    
    @property
    def datos_campana(self) -> DatosCampana:
        return self._datos_campana
    
    @property
    def datos_transaccion(self) -> DatosTransaccion:
        return self._datos_transaccion
    
    @property
    def metadatos(self) -> MetadatosConversion:
        return self._metadatos
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def confirmed_at(self) -> Optional[datetime]:
        return self._confirmed_at
    
    @property
    def validation_score(self) -> float:
        return self._validation_score
    
    def validar(self, score: float = 1.0) -> None:
        """Marca conversión como validada técnicamente"""
        if self._estado != EstadoConversion.PENDIENTE:
            raise ValueError(f"No se puede validar conversión en estado {self._estado}")
        
        self._validation_score = score
        
        # Evento interno de validación
        validation_event = ConversionValidated(
            conversion_id=self.id,
            validation_score=score
        )
        self.agregar_evento(validation_event)
        
        # Auto-confirmar si score es alto
        if score >= 0.8:
            self._auto_confirmar(validation_event)
    
    def _auto_confirmar(self, trigger_event) -> None:
        """Confirmación automática basada en validación"""
        self._estado = EstadoConversion.CONFIRMADA
        self._confirmed_at = datetime.utcnow()
        
        # Evento de integración para otros microservicios
        confirmed_event = ConversionConfirmed(
            conversion_id=self.id,
            affiliate_id=self._datos_afiliado.affiliate_id,
            campaign_id=self._datos_campana.campaign_id,
            gross_amount=str(self._datos_transaccion.gross_amount),
            currency=self._datos_transaccion.currency,
            correlation_id=trigger_event.correlation_id,
            causation_id=str(trigger_event.id)
        )
        self.agregar_evento(confirmed_event)
    
    def confirmar_manualmente(self, motivo: str = "Confirmación manual") -> None:
        """Confirmación manual por operador"""
        if self._estado != EstadoConversion.PENDIENTE:
            raise ValueError(f"No se puede confirmar conversión en estado {self._estado}")
        
        self._estado = EstadoConversion.CONFIRMADA
        self._confirmed_at = datetime.utcnow()
        
        # Evento de integración
        self.agregar_evento(ConversionConfirmed(
            conversion_id=self.id,
            affiliate_id=self._datos_afiliado.affiliate_id,
            campaign_id=self._datos_campana.campaign_id,
            gross_amount=str(self._datos_transaccion.gross_amount),
            currency=self._datos_transaccion.currency,
            correlation_id=str(uuid.uuid4())  # Nueva cadena si es manual
        ))
    
    def rechazar(self, motivo: str) -> None:
        """Rechaza conversión por incumplimiento de reglas"""
        if self._estado not in [EstadoConversion.PENDIENTE]:
            raise ValueError(f"No se puede rechazar conversión en estado {self._estado}")
        
        self._estado = EstadoConversion.RECHAZADA
        self._rejected_at = datetime.utcnow()
        
        # Evento de integración
        self.agregar_evento(ConversionRejected(
            conversion_id=self.id,
            affiliate_id=self._datos_afiliado.affiliate_id,
            campaign_id=self._datos_campana.campaign_id,
            rejection_reason=motivo,
            correlation_id=str(uuid.uuid4())
        ))
    
    def cancelar(self, motivo: str) -> None:
        """Cancela conversión (ej. refund, fraude detectado)"""
        if self._estado not in [EstadoConversion.CONFIRMADA]:
            raise ValueError(f"Solo se puede cancelar conversión confirmada, actual: {self._estado}")
        
        self._estado = EstadoConversion.CANCELADA
        self._cancelled_at = datetime.utcnow()
        
        # Evento de integración
        self.agregar_evento(ConversionCancelled(
            conversion_id=self.id,
            affiliate_id=self._datos_afiliado.affiliate_id,
            campaign_id=self._datos_campana.campaign_id,
            cancellation_reason=motivo,
            correlation_id=str(uuid.uuid4())
        ))
    
    def atribuir(self, modelo: str = "LAST_CLICK") -> None:
        """Establece modelo de atribución para el afiliado"""
        self._attribution_model = modelo
        
        self.agregar_evento(ConversionAttributed(
            conversion_id=self.id,
            affiliate_id=self._datos_afiliado.affiliate_id,
            attribution_model=modelo
        ))
    
    def puede_generar_comision(self) -> bool:
        """Determina si la conversión está lista para generar comisión"""
        return (
            self._estado == EstadoConversion.CONFIRMADA and
            self._validation_score >= 0.7 and
            self._datos_transaccion.gross_amount > 0
        )