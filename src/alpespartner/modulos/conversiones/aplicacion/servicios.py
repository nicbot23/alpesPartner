"""
Servicios de aplicación para el módulo de Conversiones.

Orquesta los casos de uso del dominio y coordina entre handlers y repositorios.
"""

from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime

from alpespartner.modulos.conversiones.aplicacion.comandos import (
    CreateConversion, ValidateConversion, ConfirmConversion,
    RejectConversion, CancelConversion, AttributeConversion
)
from alpespartner.modulos.conversiones.aplicacion.queries import (
    GetConversion, ListConversions, GetConversionsByAfiliado,
    GetConversionsByCampana, GetConversionsStats
)
from alpespartner.modulos.conversiones.aplicacion.handlers import (
    CreateConversionHandler, ValidateConversionHandler, ConfirmConversionHandler,
    RejectConversionHandler, CancelConversionHandler, AttributeConversionHandler
)
from alpespartner.modulos.conversiones.aplicacion.query_handlers import (
    GetConversionHandler, ListConversionsHandler, GetConversionsByAfiliadoHandler,
    GetConversionsByCampanaHandler, GetConversionsStatsHandler
)
from alpespartner.modulos.conversiones.dominio.repositorios import RepositorioConversiones
from alpespartner.seedwork.aplicacion.mediador import Mediador


class ServicioConversiones:
    """Servicio de aplicación para operaciones de conversiones."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones, mediador: Mediador):
        self._repositorio = repositorio_conversiones
        self._mediador = mediador
        
        # Registrar handlers de comandos
        self._mediador.register(CreateConversion, CreateConversionHandler(repositorio_conversiones))
        self._mediador.register(ValidateConversion, ValidateConversionHandler(repositorio_conversiones))
        self._mediador.register(ConfirmConversion, ConfirmConversionHandler(repositorio_conversiones))
        self._mediador.register(RejectConversion, RejectConversionHandler(repositorio_conversiones))
        self._mediador.register(CancelConversion, CancelConversionHandler(repositorio_conversiones))
        self._mediador.register(AttributeConversion, AttributeConversionHandler(repositorio_conversiones))
        
        # Registrar handlers de queries
        self._mediador.register(GetConversion, GetConversionHandler(repositorio_conversiones))
        self._mediador.register(ListConversions, ListConversionsHandler(repositorio_conversiones))
        self._mediador.register(GetConversionsByAfiliado, GetConversionsByAfiliadoHandler(repositorio_conversiones))
        self._mediador.register(GetConversionsByCampana, GetConversionsByCampanaHandler(repositorio_conversiones))
        self._mediador.register(GetConversionsStats, GetConversionsStatsHandler(repositorio_conversiones))

    # Métodos de comando (escritura)
    
    def crear_conversion(
        self,
        afiliado_id: str,
        campana_id: str,
        tipo_conversion: str,
        monto_transaccion: Decimal,
        fecha_conversion: datetime,
        metadata: Optional[Dict] = None
    ) -> str:
        """Crea una nueva conversión."""
        comando = CreateConversion(
            afiliado_id=afiliado_id,
            campana_id=campana_id,
            tipo_conversion=tipo_conversion,
            monto_transaccion=monto_transaccion,
            fecha_conversion=fecha_conversion.isoformat(),
            metadata=metadata
        )
        return self._mediador.publish(comando)

    def validar_conversion(
        self,
        conversion_id: str,
        validado_por: str,
        notas_validacion: Optional[str] = None
    ) -> None:
        """Valida una conversión existente."""
        comando = ValidateConversion(
            conversion_id=conversion_id,
            validado_por=validado_por,
            notas_validacion=notas_validacion
        )
        self._mediador.publish(comando)

    def confirmar_conversion(
        self,
        conversion_id: str,
        confirmado_por: str,
        notas_confirmacion: Optional[str] = None
    ) -> None:
        """Confirma manualmente una conversión."""
        comando = ConfirmConversion(
            conversion_id=conversion_id,
            confirmado_por=confirmado_por,
            notas_confirmacion=notas_confirmacion
        )
        self._mediador.publish(comando)

    def rechazar_conversion(
        self,
        conversion_id: str,
        rechazado_por: str,
        motivo_rechazo: str
    ) -> None:
        """Rechaza una conversión."""
        comando = RejectConversion(
            conversion_id=conversion_id,
            rechazado_por=rechazado_por,
            motivo_rechazo=motivo_rechazo
        )
        self._mediador.publish(comando)

    def cancelar_conversion(
        self,
        conversion_id: str,
        cancelado_por: str,
        motivo_cancelacion: str
    ) -> None:
        """Cancela una conversión."""
        comando = CancelConversion(
            conversion_id=conversion_id,
            cancelado_por=cancelado_por,
            motivo_cancelacion=motivo_cancelacion
        )
        self._mediador.publish(comando)

    def atribuir_comision(
        self,
        conversion_id: str,
        comision_id: str,
        monto_comision: Decimal,
        atribuido_por: str
    ) -> None:
        """Atribuye una comisión a una conversión."""
        comando = AttributeConversion(
            conversion_id=conversion_id,
            comision_id=comision_id,
            monto_comision=monto_comision,
            atribuido_por=atribuido_por
        )
        self._mediador.publish(comando)

    # Métodos de consulta (lectura)

    def obtener_conversion(self, conversion_id: str) -> Dict[str, Any]:
        """Obtiene una conversión por ID."""
        query = GetConversion(conversion_id=conversion_id)
        return self._mediador.publish(query)

    def listar_conversiones(
        self,
        afiliado_id: Optional[str] = None,
        campana_id: Optional[str] = None,
        tipo_conversion: Optional[str] = None,
        estado: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """Lista conversiones con filtros opcionales."""
        query = ListConversions(
            afiliado_id=afiliado_id,
            campana_id=campana_id,
            tipo_conversion=tipo_conversion,
            estado=estado,
            fecha_desde=fecha_desde.isoformat() if fecha_desde else None,
            fecha_hasta=fecha_hasta.isoformat() if fecha_hasta else None,
            page=page,
            size=size
        )
        return self._mediador.publish(query)

    def obtener_conversiones_afiliado(
        self,
        afiliado_id: str,
        incluir_canceladas: bool = False
    ) -> List[Dict[str, Any]]:
        """Obtiene conversiones de un afiliado específico."""
        query = GetConversionsByAfiliado(
            afiliado_id=afiliado_id,
            incluir_canceladas=incluir_canceladas
        )
        return self._mediador.publish(query)

    def obtener_conversiones_campana(
        self,
        campana_id: str,
        estado: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene conversiones de una campaña específica."""
        query = GetConversionsByCampana(
            campana_id=campana_id,
            estado=estado
        )
        return self._mediador.publish(query)

    def obtener_estadisticas(
        self,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        agrupado_por: str = "estado"
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de conversiones."""
        query = GetConversionsStats(
            fecha_desde=fecha_desde.isoformat() if fecha_desde else None,
            fecha_hasta=fecha_hasta.isoformat() if fecha_hasta else None,
            agrupado_por=agrupado_por
        )
        return self._mediador.publish(query)