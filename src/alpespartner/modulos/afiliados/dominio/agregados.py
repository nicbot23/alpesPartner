"""
Agregado Afiliado - Entidad raíz del dominio de Afiliados
Maneja la lógica de negocio y emite eventos de dominio
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

from alpespartner.seedwork.dominio.entidades import AgregacionRaiz
from .objetos_valor import (
    TipoAfiliado, EstadoAfiliado, DatosPersonales, DocumentoIdentidad,
    DatosContacto, DatosBancarios, ConfiguracionComisiones, MetadatosAfiliado,
    Referencia
)
from .eventos import (
    AffiliateCreated, AffiliateActivated, AffiliateDeactivated,
    AffiliateSuspended, AffiliateBlocked, AffiliateCommissionConfigUpdated,
    AffiliateReferralCreated, AffiliateValidated, AffiliateBankingDataUpdated,
    AffiliateContactDataUpdated, AffiliateMetadataUpdated
)


class Afiliado(AgregacionRaiz):
    """
    Agregado Afiliado - Entidad raíz del dominio de Afiliados.
    
    Responsabilidades:
    - Gestionar el ciclo de vida del afiliado
    - Validar transiciones de estado
    - Manejar referencias y comisiones
    - Emitir eventos de dominio
    """
    
    def __init__(
        self,
        datos_personales: DatosPersonales,
        documento_identidad: DocumentoIdentidad,
        datos_contacto: DatosContacto,
        tipo_afiliado: TipoAfiliado,
        configuracion_comisiones: ConfiguracionComisiones,
        afiliado_id: Optional[str] = None,
        estado: EstadoAfiliado = EstadoAfiliado.PENDIENTE_VERIFICACION,
        datos_bancarios: Optional[DatosBancarios] = None,
        metadata: Optional[MetadatosAfiliado] = None,
        codigo_referencia: Optional[str] = None,
        afiliado_referente_id: Optional[str] = None,
        referencias: Optional[List[Referencia]] = None,
        fecha_creacion: Optional[datetime] = None,
        fecha_actualizacion: Optional[datetime] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None
    ):
        super().__init__(afiliado_id or str(uuid.uuid4()), correlation_id, causation_id)
        
        # Datos obligatorios
        self._datos_personales = datos_personales
        self._documento_identidad = documento_identidad
        self._datos_contacto = datos_contacto
        self._tipo_afiliado = tipo_afiliado
        self._configuracion_comisiones = configuracion_comisiones
        self._estado = estado
        
        # Datos opcionales
        self._datos_bancarios = datos_bancarios
        self._metadata = metadata or MetadatosAfiliado({})
        self._codigo_referencia = codigo_referencia or self._generar_codigo_referencia()
        self._afiliado_referente_id = afiliado_referente_id
        self._referencias = referencias or []
        
        # Timestamps
        self._fecha_creacion = fecha_creacion or datetime.utcnow()
        self._fecha_actualizacion = fecha_actualizacion
        
        # Si es un nuevo afiliado, emitir evento de creación
        if not fecha_creacion:
            self._emitir_evento_creacion()

    # Propiedades de solo lectura
    
    @property
    def datos_personales(self) -> DatosPersonales:
        return self._datos_personales
    
    @property
    def documento_identidad(self) -> DocumentoIdentidad:
        return self._documento_identidad
    
    @property
    def datos_contacto(self) -> DatosContacto:
        return self._datos_contacto
    
    @property
    def tipo_afiliado(self) -> TipoAfiliado:
        return self._tipo_afiliado
    
    @property
    def estado(self) -> EstadoAfiliado:
        return self._estado
    
    @property
    def configuracion_comisiones(self) -> ConfiguracionComisiones:
        return self._configuracion_comisiones
    
    @property
    def datos_bancarios(self) -> Optional[DatosBancarios]:
        return self._datos_bancarios
    
    @property
    def metadata(self) -> MetadatosAfiliado:
        return self._metadata
    
    @property
    def codigo_referencia(self) -> str:
        return self._codigo_referencia
    
    @property
    def afiliado_referente_id(self) -> Optional[str]:
        return self._afiliado_referente_id
    
    @property
    def referencias(self) -> List[Referencia]:
        return self._referencias.copy()
    
    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion
    
    @property
    def fecha_actualizacion(self) -> Optional[datetime]:
        return self._fecha_actualizacion
    
    # Métodos de negocio
    
    def activar(self, activado_por: str) -> None:
        """Activa el afiliado."""
        if self._estado == EstadoAfiliado.ACTIVO:
            raise ValueError("El afiliado ya está activo")
        
        if self._estado == EstadoAfiliado.BLOQUEADO:
            raise ValueError("No se puede activar un afiliado bloqueado")
        
        estado_anterior = self._estado
        self._estado = EstadoAfiliado.ACTIVO
        self._fecha_actualizacion = datetime.utcnow()
        
        # Emitir evento de integración
        evento = AffiliateActivated(
            afiliado_id=self.id,
            activated_by=activado_por,
            activated_at=self._fecha_actualizacion,
            previous_state=estado_anterior.value,
            correlation_id=self.correlation_id,
            causation_id=self.id
        )
        self.agregar_evento(evento)
    
    def desactivar(self, desactivado_por: str, motivo: str) -> None:
        """Desactiva el afiliado."""
        if self._estado == EstadoAfiliado.INACTIVO:
            raise ValueError("El afiliado ya está inactivo")
        
        estado_anterior = self._estado
        self._estado = EstadoAfiliado.INACTIVO
        self._fecha_actualizacion = datetime.utcnow()
        
        # Emitir evento de integración
        evento = AffiliateDeactivated(
            afiliado_id=self.id,
            deactivated_by=desactivado_por,
            deactivated_at=self._fecha_actualizacion,
            reason=motivo,
            previous_state=estado_anterior.value,
            correlation_id=self.correlation_id,
            causation_id=self.id
        )
        self.agregar_evento(evento)
    
    def suspender(self, suspendido_por: str, motivo: str, hasta: Optional[datetime] = None) -> None:
        """Suspende el afiliado temporalmente."""
        if self._estado == EstadoAfiliado.SUSPENDIDO:
            raise ValueError("El afiliado ya está suspendido")
        
        if self._estado == EstadoAfiliado.BLOQUEADO:
            raise ValueError("No se puede suspender un afiliado bloqueado")
        
        self._estado = EstadoAfiliado.SUSPENDIDO
        self._fecha_actualizacion = datetime.utcnow()
        
        # Emitir evento de integración
        evento = AffiliateSuspended(
            afiliado_id=self.id,
            suspended_by=suspendido_por,
            suspended_at=self._fecha_actualizacion,
            reason=motivo,
            suspension_until=hasta,
            correlation_id=self.correlation_id,
            causation_id=self.id
        )
        self.agregar_evento(evento)
    
    def bloquear(self, bloqueado_por: str, motivo: str) -> None:
        """Bloquea permanentemente el afiliado."""
        if self._estado == EstadoAfiliado.BLOQUEADO:
            raise ValueError("El afiliado ya está bloqueado")
        
        self._estado = EstadoAfiliado.BLOQUEADO
        self._fecha_actualizacion = datetime.utcnow()
        
        # Emitir evento de integración
        evento = AffiliateBlocked(
            afiliado_id=self.id,
            blocked_by=bloqueado_por,
            blocked_at=self._fecha_actualizacion,
            reason=motivo,
            correlation_id=self.correlation_id,
            causation_id=self.id
        )
        self.agregar_evento(evento)
    
    def actualizar_configuracion_comisiones(
        self, 
        nueva_configuracion: ConfiguracionComisiones,
        actualizado_por: str
    ) -> None:
        """Actualiza la configuración de comisiones."""
        configuracion_anterior = {
            'porcentaje_base': float(self._configuracion_comisiones.porcentaje_base),
            'porcentaje_premium': float(self._configuracion_comisiones.porcentaje_premium) if self._configuracion_comisiones.porcentaje_premium else None,
            'monto_minimo': float(self._configuracion_comisiones.monto_minimo) if self._configuracion_comisiones.monto_minimo else None
        }
        
        nueva_config_dict = {
            'porcentaje_base': float(nueva_configuracion.porcentaje_base),
            'porcentaje_premium': float(nueva_configuracion.porcentaje_premium) if nueva_configuracion.porcentaje_premium else None,
            'monto_minimo': float(nueva_configuracion.monto_minimo) if nueva_configuracion.monto_minimo else None
        }
        
        self._configuracion_comisiones = nueva_configuracion
        self._fecha_actualizacion = datetime.utcnow()
        
        # Emitir evento de integración
        evento = AffiliateCommissionConfigUpdated(
            afiliado_id=self.id,
            updated_by=actualizado_por,
            updated_at=self._fecha_actualizacion,
            previous_config=configuracion_anterior,
            new_config=nueva_config_dict,
            correlation_id=self.correlation_id,
            causation_id=self.id
        )
        self.agregar_evento(evento)
    
    def agregar_referencia(self, afiliado_referido_id: str, codigo_referencia: Optional[str] = None) -> None:
        """Agrega una referencia a otro afiliado."""
        if self._estado != EstadoAfiliado.ACTIVO:
            raise ValueError("Solo afiliados activos pueden hacer referencias")
        
        # Verificar que no se refiera a sí mismo
        if afiliado_referido_id == self.id:
            raise ValueError("Un afiliado no puede referirse a sí mismo")
        
        # Verificar que no exista ya esta referencia
        if any(ref.afiliado_referido_id == afiliado_referido_id for ref in self._referencias):
            raise ValueError("Ya existe una referencia a este afiliado")
        
        fecha_referencia = datetime.utcnow()
        nueva_referencia = Referencia(
            afiliado_referido_id=afiliado_referido_id,
            fecha_referencia=fecha_referencia,
            estado="ACTIVO"
        )
        
        self._referencias.append(nueva_referencia)
        self._fecha_actualizacion = fecha_referencia
        
        # Emitir evento de integración
        evento = AffiliateReferralCreated(
            afiliado_referente_id=self.id,
            afiliado_referido_id=afiliado_referido_id,
            referral_date=fecha_referencia,
            referral_code=codigo_referencia,
            correlation_id=self.correlation_id,
            causation_id=self.id
        )
        self.agregar_evento(evento)
    
    def actualizar_datos_bancarios(self, nuevos_datos: DatosBancarios, actualizado_por: str) -> None:
        """Actualiza los datos bancarios del afiliado."""
        self._datos_bancarios = nuevos_datos
        self._fecha_actualizacion = datetime.utcnow()
        
        # Emitir evento interno
        evento = AffiliateBankingDataUpdated(
            afiliado_id=self.id,
            updated_by=actualizado_por,
            updated_at=self._fecha_actualizacion,
            bank_info={
                'banco': nuevos_datos.banco,
                'tipo_cuenta': nuevos_datos.tipo_cuenta,
                'numero_cuenta': nuevos_datos.numero_cuenta,
                'titular': nuevos_datos.titular
            },
            correlation_id=self.correlation_id,
            causation_id=self.id
        )
        self.agregar_evento(evento)
    
    def actualizar_datos_contacto(self, nuevos_datos: DatosContacto, actualizado_por: str) -> None:
        """Actualiza los datos de contacto del afiliado."""
        cambios = {}
        if self._datos_contacto.email != nuevos_datos.email:
            cambios['email'] = {'anterior': self._datos_contacto.email, 'nuevo': nuevos_datos.email}
        if self._datos_contacto.telefono != nuevos_datos.telefono:
            cambios['telefono'] = {'anterior': self._datos_contacto.telefono, 'nuevo': nuevos_datos.telefono}
        if self._datos_contacto.direccion != nuevos_datos.direccion:
            cambios['direccion'] = {'anterior': self._datos_contacto.direccion, 'nuevo': nuevos_datos.direccion}
        
        self._datos_contacto = nuevos_datos
        self._fecha_actualizacion = datetime.utcnow()
        
        if cambios:
            # Emitir evento interno
            evento = AffiliateContactDataUpdated(
                afiliado_id=self.id,
                updated_by=actualizado_por,
                updated_at=self._fecha_actualizacion,
                contact_changes=cambios,
                correlation_id=self.correlation_id,
                causation_id=self.id
            )
            self.agregar_evento(evento)
    
    def validar(self, validado_por: str, notas: Optional[str] = None) -> None:
        """Valida el afiliado internamente."""
        if self._estado != EstadoAfiliado.PENDIENTE_VERIFICACION:
            raise ValueError("Solo se pueden validar afiliados pendientes de verificación")
        
        self._fecha_actualizacion = datetime.utcnow()
        
        # Emitir evento interno
        evento = AffiliateValidated(
            afiliado_id=self.id,
            validated_by=validado_por,
            validated_at=self._fecha_actualizacion,
            validation_notes=notas,
            correlation_id=self.correlation_id,
            causation_id=self.id
        )
        self.agregar_evento(evento)
    
    # Métodos privados
    
    def _generar_codigo_referencia(self) -> str:
        """Genera un código de referencia único."""
        return f"REF_{self.id[:8].upper()}"
    
    def _emitir_evento_creacion(self) -> None:
        """Emite el evento de creación del afiliado."""
        evento = AffiliateCreated(
            afiliado_id=self.id,
            tipo_afiliado=self._tipo_afiliado.value,
            email=self._datos_contacto.email,
            nombres=self._datos_personales.nombres,
            apellidos=self._datos_personales.apellidos,
            created_at=self._fecha_creacion,
            correlation_id=self.correlation_id,
            causation_id=self.id
        )
        self.agregar_evento(evento)