"""
Fábrica del dominio Conversiones
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from .agregados import Conversion
from .objetos_valor import (
    TipoConversion, EstadoConversion, DatosAfiliado,
    DatosCampana, DatosTransaccion, MetadatosConversion
)


class FabricaConversiones:
    """Fábrica para crear agregados Conversion"""
    
    @staticmethod
    def crear_conversion(
        affiliate_id: str,
        campaign_id: str,
        campaign_name: str,
        brand: str,
        conversion_type: str,
        gross_amount: Decimal,
        currency: str,
        affiliate_type: str = "INFLUENCER",
        tier_level: str = "STANDARD",
        transaction_id: Optional[str] = None,
        metadatos: Optional[dict] = None
    ) -> Conversion:
        """Crea nueva conversión con validaciones de negocio"""
        
        # Validaciones
        if gross_amount <= 0:
            raise ValueError("El monto bruto debe ser mayor a cero")
        
        if conversion_type not in [t.value for t in TipoConversion]:
            raise ValueError(f"Tipo de conversión inválido: {conversion_type}")
        
        # Generar ID único
        conversion_id = str(uuid.uuid4())
        
        # Construir objetos valor
        datos_afiliado = DatosAfiliado(
            affiliate_id=affiliate_id,
            affiliate_type=affiliate_type,
            tier_level=tier_level
        )
        
        datos_campana = DatosCampana(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            brand=brand
        )
        
        datos_transaccion = DatosTransaccion(
            gross_amount=gross_amount,
            currency=currency,
            transaction_id=transaction_id
        )
        
        metadatos_obj = None
        if metadatos:
            metadatos_obj = MetadatosConversion(**metadatos)
        
        # Crear agregado
        return Conversion(
            conversion_id=conversion_id,
            tipo=TipoConversion(conversion_type),
            datos_afiliado=datos_afiliado,
            datos_campana=datos_campana,
            datos_transaccion=datos_transaccion,
            metadatos=metadatos_obj
        )
    
    @staticmethod
    def reconstruir_conversion(
        conversion_id: str,
        tipo: str,
        affiliate_id: str,
        affiliate_type: str,
        tier_level: str,
        campaign_id: str,
        campaign_name: str,
        brand: str,
        gross_amount: Decimal,
        currency: str,
        transaction_id: Optional[str],
        estado: str,
        created_at: datetime,
        confirmed_at: Optional[datetime] = None,
        rejected_at: Optional[datetime] = None,
        cancelled_at: Optional[datetime] = None,
        validation_score: float = 0.0,
        metadatos: Optional[dict] = None
    ) -> Conversion:
        """Reconstruye conversión desde persistencia sin emitir eventos"""
        
        # Construir objetos valor
        datos_afiliado = DatosAfiliado(
            affiliate_id=affiliate_id,
            affiliate_type=affiliate_type,
            tier_level=tier_level
        )
        
        datos_campana = DatosCampana(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            brand=brand
        )
        
        datos_transaccion = DatosTransaccion(
            gross_amount=gross_amount,
            currency=currency,
            transaction_id=transaction_id
        )
        
        metadatos_obj = None
        if metadatos:
            metadatos_obj = MetadatosConversion(**metadatos)
        
        # Crear agregado
        conversion = Conversion(
            conversion_id=conversion_id,
            tipo=TipoConversion(tipo),
            datos_afiliado=datos_afiliado,
            datos_campana=datos_campana,
            datos_transaccion=datos_transaccion,
            metadatos=metadatos_obj
        )
        
        # Restaurar estado sin eventos (reconstrucción)
        conversion._estado = EstadoConversion(estado)
        conversion._created_at = created_at
        conversion._confirmed_at = confirmed_at
        conversion._rejected_at = rejected_at
        conversion._cancelled_at = cancelled_at
        conversion._validation_score = validation_score
        
        # Limpiar eventos de construcción
        conversion._eventos.clear()
        
        return conversion