from alpespartner.seedwork.aplicacion.handlers import ManejadorComando
from alpespartner.modulos.conversiones.aplicacion.comandos import (
    CreateConversion, ValidateConversion, ConfirmConversion, 
    RejectConversion, CancelConversion, AttributeConversion
)
from alpespartner.modulos.conversiones.dominio.repositorios import RepositorioConversiones
from alpespartner.modulos.conversiones.dominio.fabricas import FabricaConversiones
from alpespartner.modulos.conversiones.dominio.objetos_valor import (
    TipoConversion, DatosAfiliado, DatosCampana, DatosTransaccion, MetadatosConversion
)
from alpespartner.seedwork.infraestructura.uow import UnidadTrabajoPort
from alpespartner.seedwork.dominio.excepciones import ReglaNegocioException
from datetime import datetime
from decimal import Decimal
import logging


logger = logging.getLogger(__name__)


class CreateConversionHandler(ManejadorComando):
    """Handler para crear nuevas conversiones."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, comando: CreateConversion):
        """Procesa comando de creación de conversión."""
        try:
            # Validar y convertir tipo de conversión
            tipo_conversion = TipoConversion(comando.tipo_conversion)
            
            # Crear objetos valor
            datos_afiliado = DatosAfiliado(id=comando.afiliado_id)
            datos_campana = DatosCampana(id=comando.campana_id)
            datos_transaccion = DatosTransaccion(
                monto=comando.monto_transaccion,
                fecha=datetime.fromisoformat(comando.fecha_conversion)
            )
            metadata = MetadatosConversion(datos=comando.metadata or {})
            
            # Crear conversión usando la fábrica
            fabrica = FabricaConversiones()
            conversion = fabrica.crear_conversion(
                datos_afiliado=datos_afiliado,
                datos_campana=datos_campana,
                tipo_conversion=tipo_conversion,
                datos_transaccion=datos_transaccion,
                metadata=metadata
            )
            
            # Guardar usando el repositorio (incluye manejo de outbox)
            self._repositorio.guardar(conversion)
            
            logger.info(f"Conversión creada exitosamente: {conversion.id}")
            return conversion.id
            
        except ValueError as e:
            raise ReglaNegocioException(f"Tipo de conversión inválido: {e}")
        except Exception as e:
            logger.error(f"Error creando conversión: {e}")
            raise


class ValidateConversionHandler(ManejadorComando):
    """Handler para validar conversiones."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, comando: ValidateConversion):
        """Procesa comando de validación de conversión."""
        try:
            # Obtener la conversión
            conversion = self._repositorio.obtener_por_id(comando.conversion_id)
            if not conversion:
                raise ReglaNegocioException(f"Conversión no encontrada: {comando.conversion_id}")
            
            # Validar la conversión
            conversion.validar(comando.validado_por, comando.notas_validacion)
            
            # Guardar cambios
            self._repositorio.guardar(conversion)
            
            logger.info(f"Conversión validada: {comando.conversion_id}")
            
        except Exception as e:
            logger.error(f"Error validando conversión {comando.conversion_id}: {e}")
            raise


class ConfirmConversionHandler(ManejadorComando):
    """Handler para confirmar conversiones manualmente."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, comando: ConfirmConversion):
        """Procesa comando de confirmación de conversión."""
        try:
            # Obtener la conversión
            conversion = self._repositorio.obtener_por_id(comando.conversion_id)
            if not conversion:
                raise ReglaNegocioException(f"Conversión no encontrada: {comando.conversion_id}")
            
            # Confirmar la conversión
            conversion.confirmar_manualmente(comando.confirmado_por, comando.notas_confirmacion)
            
            # Guardar cambios
            self._repositorio.guardar(conversion)
            
            logger.info(f"Conversión confirmada: {comando.conversion_id}")
            
        except Exception as e:
            logger.error(f"Error confirmando conversión {comando.conversion_id}: {e}")
            raise


class RejectConversionHandler(ManejadorComando):
    """Handler para rechazar conversiones."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, comando: RejectConversion):
        """Procesa comando de rechazo de conversión."""
        try:
            # Obtener la conversión
            conversion = self._repositorio.obtener_por_id(comando.conversion_id)
            if not conversion:
                raise ReglaNegocioException(f"Conversión no encontrada: {comando.conversion_id}")
            
            # Rechazar la conversión
            conversion.rechazar(comando.rechazado_por, comando.motivo_rechazo)
            
            # Guardar cambios
            self._repositorio.guardar(conversion)
            
            logger.info(f"Conversión rechazada: {comando.conversion_id}")
            
        except Exception as e:
            logger.error(f"Error rechazando conversión {comando.conversion_id}: {e}")
            raise


class CancelConversionHandler(ManejadorComando):
    """Handler para cancelar conversiones."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, comando: CancelConversion):
        """Procesa comando de cancelación de conversión."""
        try:
            # Obtener la conversión
            conversion = self._repositorio.obtener_por_id(comando.conversion_id)
            if not conversion:
                raise ReglaNegocioException(f"Conversión no encontrada: {comando.conversion_id}")
            
            # Cancelar la conversión
            conversion.cancelar(comando.cancelado_por, comando.motivo_cancelacion)
            
            # Guardar cambios
            self._repositorio.guardar(conversion)
            
            logger.info(f"Conversión cancelada: {comando.conversion_id}")
            
        except Exception as e:
            logger.error(f"Error cancelando conversión {comando.conversion_id}: {e}")
            raise


class AttributeConversionHandler(ManejadorComando):
    """Handler para atribuir comisiones a conversiones."""
    
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self._repositorio = repositorio_conversiones

    def handle(self, comando: AttributeConversion):
        """Procesa comando de atribución de comisión."""
        try:
            # Obtener la conversión
            conversion = self._repositorio.obtener_por_id(comando.conversion_id)
            if not conversion:
                raise ReglaNegocioException(f"Conversión no encontrada: {comando.conversion_id}")
            
            # Atribuir la comisión
            conversion.atribuir(
                comando.comision_id, 
                comando.monto_comision, 
                comando.atribuido_por
            )
            
            # Guardar cambios
            self._repositorio.guardar(conversion)
            
            logger.info(f"Comisión {comando.comision_id} atribuida a conversión {comando.conversion_id}")
            
        except Exception as e:
            logger.error(f"Error atribuyendo comisión a conversión {comando.conversion_id}: {e}")
            raise