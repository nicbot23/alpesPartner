"""
Servicios de dominio para Afiliados
Contienen lógica de negocio compleja que involucra múltiples agregados
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from .agregados import Afiliado
from .repositorios import RepositorioAfiliados
from .excepciones import (
    DocumentoYaRegistrado, EmailYaRegistrado, CodigoReferenciaYaExiste,
    ReferenciaCircular, AfiliadoYaReferido, ComisionInvalida
)
from .objetos_valor import TipoAfiliado, EstadoAfiliado


class ServicioDominioAfiliados:
    """
    Servicio de dominio que encapsula lógica de negocio compleja
    que involucra múltiples afiliados o reglas de dominio sofisticadas.
    """
    
    def __init__(self, repositorio: RepositorioAfiliados):
        self._repositorio = repositorio
    
    def verificar_unicidad_documento(
        self, 
        tipo_documento: str, 
        numero_documento: str,
        excluir_afiliado_id: Optional[str] = None
    ) -> None:
        """
        Verifica que el documento no esté ya registrado.
        
        Args:
            tipo_documento: Tipo del documento
            numero_documento: Número del documento  
            excluir_afiliado_id: ID a excluir de la verificación (para actualizaciones)
            
        Raises:
            DocumentoYaRegistrado: Si el documento ya está registrado
        """
        afiliado_existente = self._repositorio.obtener_por_documento(
            tipo_documento, numero_documento
        )
        
        if afiliado_existente and afiliado_existente.id != excluir_afiliado_id:
            raise DocumentoYaRegistrado(tipo_documento, numero_documento)
    
    def verificar_unicidad_email(
        self, 
        email: str,
        excluir_afiliado_id: Optional[str] = None
    ) -> None:
        """
        Verifica que el email no esté ya registrado.
        
        Args:
            email: Email a verificar
            excluir_afiliado_id: ID a excluir de la verificación
            
        Raises:
            EmailYaRegistrado: Si el email ya está registrado
        """
        afiliado_existente = self._repositorio.obtener_por_email(email)
        
        if afiliado_existente and afiliado_existente.id != excluir_afiliado_id:
            raise EmailYaRegistrado(email)
    
    def generar_codigo_referencia_unico(self, base: str) -> str:
        """
        Genera un código de referencia único basado en una cadena base.
        
        Args:
            base: Cadena base para el código
            
        Returns:
            Código de referencia único
        """
        codigo_base = base.upper().replace(" ", "")[:10]
        contador = 1
        
        while True:
            codigo = f"{codigo_base}{contador:03d}"
            if not self._repositorio.obtener_por_codigo_referencia(codigo):
                return codigo
            contador += 1
    
    def verificar_referencia_circular(
        self, 
        afiliado_id: str, 
        afiliado_referente_id: str
    ) -> None:
        """
        Verifica que no se cree una referencia circular.
        
        Args:
            afiliado_id: ID del afiliado que será referido
            afiliado_referente_id: ID del afiliado referente
            
        Raises:
            ReferenciaCircular: Si se detecta una referencia circular
        """
        # Verificar referencia directa
        if afiliado_id == afiliado_referente_id:
            raise ReferenciaCircular(afiliado_id, afiliado_referente_id)
        
        # Verificar referencia indirecta (el referente es referido por el afiliado)
        afiliado_referente = self._repositorio.obtener_por_id(afiliado_referente_id)
        if afiliado_referente and afiliado_referente.afiliado_referente_id == afiliado_id:
            raise ReferenciaCircular(afiliado_id, afiliado_referente_id)
    
    def puede_referenciar_afiliado(self, afiliado_referido_id: str) -> bool:
        """
        Verifica si un afiliado puede ser referido.
        
        Args:
            afiliado_referido_id: ID del afiliado a referenciar
            
        Returns:
            True si puede ser referido, False en caso contrario
        """
        afiliado = self._repositorio.obtener_por_id(afiliado_referido_id)
        
        if not afiliado:
            return False
        
        # Solo afiliados activos pueden ser referidos
        if afiliado.estado != EstadoAfiliado.ACTIVO:
            return False
        
        # No puede tener ya un referente
        if afiliado.afiliado_referente_id:
            return False
        
        return True
    
    def calcular_comisiones_escalonadas(
        self, 
        afiliado: Afiliado, 
        monto_transaccion: Decimal
    ) -> Decimal:
        """
        Calcula comisiones con escalones basados en el tipo de afiliado.
        
        Args:
            afiliado: El afiliado
            monto_transaccion: Monto de la transacción
            
        Returns:
            Monto de la comisión calculada
        """
        config = afiliado.configuracion_comisiones
        
        # Aplicar monto mínimo
        if config.monto_minimo and monto_transaccion < config.monto_minimo:
            return Decimal('0')
        
        # Calcular comisión base
        comision = monto_transaccion * (config.porcentaje_base / 100)
        
        # Aplicar escalones según tipo de afiliado
        if afiliado.tipo_afiliado == TipoAfiliado.PREMIUM:
            if config.porcentaje_premium:
                comision = monto_transaccion * (config.porcentaje_premium / 100)
            else:
                # Incremento automático del 20% para premium
                comision = comision * Decimal('1.2')
        
        elif afiliado.tipo_afiliado == TipoAfiliado.EMPRESA:
            # Descuento para empresas en transacciones grandes
            if monto_transaccion > Decimal('1000000'):  # 1M
                comision = comision * Decimal('0.9')  # 10% descuento
        
        elif afiliado.tipo_afiliado == TipoAfiliado.INFLUENCER:
            # Bonificación para influencers
            comision = comision * Decimal('1.15')  # 15% bonificación
        
        return comision.quantize(Decimal('0.01'))
    
    def obtener_afiliados_referidos_activos(self, afiliado_id: str) -> List[Afiliado]:
        """
        Obtiene todos los afiliados referidos activos de un afiliado.
        
        Args:
            afiliado_id: ID del afiliado referente
            
        Returns:
            Lista de afiliados referidos activos
        """
        return self._repositorio.obtener_referidos_activos(afiliado_id)
    
    def calcular_comision_por_referidos(
        self, 
        afiliado_referente: Afiliado, 
        comision_referido: Decimal
    ) -> Decimal:
        """
        Calcula la comisión que recibe un afiliado por sus referidos.
        
        Args:
            afiliado_referente: El afiliado que hizo la referencia
            comision_referido: Comisión ganada por el referido
            
        Returns:
            Comisión por referencia
        """
        # Porcentaje base de comisión por referencia
        porcentaje_referencia = Decimal('0.05')  # 5%
        
        # Incremento según tipo de afiliado
        if afiliado_referente.tipo_afiliado == TipoAfiliado.PREMIUM:
            porcentaje_referencia = Decimal('0.08')  # 8%
        elif afiliado_referente.tipo_afiliado == TipoAfiliado.INFLUENCER:
            porcentaje_referencia = Decimal('0.10')  # 10%
        
        comision = comision_referido * porcentaje_referencia
        return comision.quantize(Decimal('0.01'))
    
    def validar_configuracion_comisiones(
        self, 
        porcentaje_base: Decimal,
        porcentaje_premium: Optional[Decimal] = None,
        monto_minimo: Optional[Decimal] = None
    ) -> None:
        """
        Valida que la configuración de comisiones sea coherente.
        
        Args:
            porcentaje_base: Porcentaje base de comisión
            porcentaje_premium: Porcentaje premium opcional
            monto_minimo: Monto mínimo opcional
            
        Raises:
            ComisionInvalida: Si la configuración es inválida
        """
        if porcentaje_base < Decimal('0') or porcentaje_base > Decimal('50'):
            raise ComisionInvalida(
                "El porcentaje base debe estar entre 0% y 50%"
            )
        
        if porcentaje_premium:
            if porcentaje_premium < porcentaje_base:
                raise ComisionInvalida(
                    "El porcentaje premium debe ser mayor al porcentaje base"
                )
            
            if porcentaje_premium > Decimal('50'):
                raise ComisionInvalida(
                    "El porcentaje premium no puede exceder 50%"
                )
        
        if monto_minimo and monto_minimo < Decimal('0'):
            raise ComisionInvalida(
                "El monto mínimo no puede ser negativo"
            )