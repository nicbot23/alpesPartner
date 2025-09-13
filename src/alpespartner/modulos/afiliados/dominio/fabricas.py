"""
Fábrica para crear y reconstruir afiliados
Encapsula la lógica de construcción de objetos complejos
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal

from .agregados import Afiliado
from .objetos_valor import (
    TipoAfiliado, EstadoAfiliado, DatosPersonales, DocumentoIdentidad,
    DatosContacto, DatosBancarios, ConfiguracionComisiones, MetadatosAfiliado,
    TipoDocumento, Referencia
)


class FabricaAfiliados:
    """Fábrica para crear instancias de Afiliado."""
    
    @classmethod
    def crear_afiliado(
        cls,
        nombres: str,
        apellidos: str,
        email: str,
        tipo_documento: str,
        numero_documento: str,
        tipo_afiliado: str,
        porcentaje_comision_base: Decimal,
        telefono: Optional[str] = None,
        direccion: Optional[str] = None,
        ciudad: Optional[str] = None,
        pais: Optional[str] = None,
        fecha_nacimiento: Optional[datetime] = None,
        fecha_expedicion_documento: Optional[datetime] = None,
        porcentaje_comision_premium: Optional[Decimal] = None,
        monto_minimo_comision: Optional[Decimal] = None,
        afiliado_referente_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None
    ) -> Afiliado:
        """
        Crea un nuevo afiliado con los datos proporcionados.
        
        Args:
            nombres: Nombres del afiliado
            apellidos: Apellidos del afiliado
            email: Email de contacto
            tipo_documento: Tipo de documento (CEDULA, PASAPORTE, NIT, RUT)
            numero_documento: Número del documento
            tipo_afiliado: Tipo de afiliado (INFLUENCER, EMPRESA, INDIVIDUAL, PREMIUM)
            porcentaje_comision_base: Porcentaje base de comisión
            ... otros parámetros opcionales
            
        Returns:
            Instancia de Afiliado creada
        """
        
        # Crear objetos valor
        datos_personales = DatosPersonales(
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento
        )
        
        documento_identidad = DocumentoIdentidad(
            tipo=TipoDocumento(tipo_documento),
            numero=numero_documento,
            fecha_expedicion=fecha_expedicion_documento
        )
        
        datos_contacto = DatosContacto(
            email=email,
            telefono=telefono,
            direccion=direccion,
            ciudad=ciudad,
            pais=pais
        )
        
        configuracion_comisiones = ConfiguracionComisiones(
            porcentaje_base=porcentaje_comision_base,
            porcentaje_premium=porcentaje_comision_premium,
            monto_minimo=monto_minimo_comision
        )
        
        metadata_obj = MetadatosAfiliado(metadata or {})
        
        # Crear el afiliado
        afiliado = Afiliado(
            datos_personales=datos_personales,
            documento_identidad=documento_identidad,
            datos_contacto=datos_contacto,
            tipo_afiliado=TipoAfiliado(tipo_afiliado),
            configuracion_comisiones=configuracion_comisiones,
            metadata=metadata_obj,
            afiliado_referente_id=afiliado_referente_id,
            correlation_id=correlation_id,
            causation_id=causation_id
        )
        
        return afiliado
    
    @classmethod
    def reconstruir_afiliado(
        cls,
        afiliado_id: str,
        nombres: str,
        apellidos: str,
        email: str,
        tipo_documento: str,
        numero_documento: str,
        tipo_afiliado: str,
        estado: str,
        porcentaje_comision_base: Decimal,
        fecha_creacion: datetime,
        telefono: Optional[str] = None,
        direccion: Optional[str] = None,
        ciudad: Optional[str] = None,
        pais: Optional[str] = None,
        fecha_nacimiento: Optional[datetime] = None,
        fecha_expedicion_documento: Optional[datetime] = None,
        porcentaje_comision_premium: Optional[Decimal] = None,
        monto_minimo_comision: Optional[Decimal] = None,
        banco: Optional[str] = None,
        tipo_cuenta: Optional[str] = None,
        numero_cuenta: Optional[str] = None,
        titular_cuenta: Optional[str] = None,
        codigo_referencia: Optional[str] = None,
        afiliado_referente_id: Optional[str] = None,
        referencias: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        fecha_actualizacion: Optional[datetime] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        version: int = 1
    ) -> Afiliado:
        """
        Reconstruye un afiliado desde datos de persistencia.
        
        Args:
            afiliado_id: ID del afiliado
            ... todos los datos persistidos
            
        Returns:
            Instancia de Afiliado reconstruida
        """
        
        # Crear objetos valor
        datos_personales = DatosPersonales(
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento
        )
        
        documento_identidad = DocumentoIdentidad(
            tipo=TipoDocumento(tipo_documento),
            numero=numero_documento,
            fecha_expedicion=fecha_expedicion_documento
        )
        
        datos_contacto = DatosContacto(
            email=email,
            telefono=telefono,
            direccion=direccion,
            ciudad=ciudad,
            pais=pais
        )
        
        configuracion_comisiones = ConfiguracionComisiones(
            porcentaje_base=porcentaje_comision_base,
            porcentaje_premium=porcentaje_comision_premium,
            monto_minimo=monto_minimo_comision
        )
        
        # Datos bancarios opcionales
        datos_bancarios = None
        if banco and tipo_cuenta and numero_cuenta and titular_cuenta:
            datos_bancarios = DatosBancarios(
                banco=banco,
                tipo_cuenta=tipo_cuenta,
                numero_cuenta=numero_cuenta,
                titular=titular_cuenta
            )
        
        # Reconstruir referencias
        referencias_obj = []
        if referencias:
            for ref_data in referencias:
                referencia = Referencia(
                    afiliado_referido_id=ref_data['afiliado_referido_id'],
                    fecha_referencia=ref_data['fecha_referencia'],
                    estado=ref_data['estado']
                )
                referencias_obj.append(referencia)
        
        metadata_obj = MetadatosAfiliado(metadata or {})
        
        # Reconstruir el afiliado
        afiliado = Afiliado(
            datos_personales=datos_personales,
            documento_identidad=documento_identidad,
            datos_contacto=datos_contacto,
            tipo_afiliado=TipoAfiliado(tipo_afiliado),
            configuracion_comisiones=configuracion_comisiones,
            afiliado_id=afiliado_id,
            estado=EstadoAfiliado(estado),
            datos_bancarios=datos_bancarios,
            metadata=metadata_obj,
            codigo_referencia=codigo_referencia,
            afiliado_referente_id=afiliado_referente_id,
            referencias=referencias_obj,
            fecha_creacion=fecha_creacion,
            fecha_actualizacion=fecha_actualizacion,
            correlation_id=correlation_id,
            causation_id=causation_id
        )
        
        # Asignar versión
        afiliado._version = version
        
        # Limpiar eventos (no reproducir eventos históricos)
        afiliado._eventos.clear()
        
        return afiliado