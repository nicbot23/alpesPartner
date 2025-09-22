from campanias.seedwork.aplicacion.comandos import Comando, ComandoHandler
from campanias.seedwork.aplicacion.comandos import ejecutar_commando as comando
from dataclasses import dataclass
from typing import Optional, Dict
import uuid

@dataclass
class RegistrarConversion(Comando):
    """Comando para registrar una nueva conversión"""
    id_campana: str
    id_afiliado: str
    codigo_promocional: str
    tipo_conversion: str  # VENTA, LEAD, CLICK, IMPRESION, DESCARGA
    monto_conversion: Optional[float] = None
    moneda: str = "USD"
    id_cliente: Optional[str] = None
    datos_conversion: Optional[Dict] = None  # Metadata adicional
    fuente_conversion: str = "WEB"  # WEB, MOBILE, EMAIL, SOCIAL
    ip_usuario: Optional[str] = None
    user_agent: Optional[str] = None
    fecha_conversion: str = None

@dataclass
class ValidarConversion(Comando):
    """Comando para validar una conversión registrada"""
    id_conversion: str
    criterios_validacion: Dict
    id_validador: Optional[str] = None

@dataclass
class ConfirmarConversion(Comando):
    """Comando para confirmar una conversión validada"""
    id_conversion: str
    id_confirmador: str
    comentarios: Optional[str] = None
    fecha_confirmacion: str = None

@dataclass
class RechazarConversion(Comando):
    """Comando para rechazar una conversión (fraude, duplicada, etc.)"""
    id_conversion: str
    razon_rechazo: str
    id_rechazador: str
    fecha_rechazo: str = None

@dataclass
class MarcarConversionComoDuplicada(Comando):
    """Comando para marcar conversión como duplicada"""
    id_conversion: str
    id_conversion_original: str
    id_marcador: str

@dataclass
class RevertirConversion(Comando):
    """Comando para revertir una conversión (devolución, cancelación)"""
    id_conversion: str
    razon_reversion: str
    monto_revertir: Optional[float] = None  # Si es reversión parcial
    fecha_reversion: str = None

@dataclass
class ActualizarDatosConversion(Comando):
    """Comando para actualizar datos de una conversión"""
    id_conversion: str
    nuevos_datos: Dict
    id_actualizador: str
    razon_actualizacion: str

class RegistrarConversionHandler(ComandoHandler):
    def handle(self, comando: RegistrarConversion):
        """Registra una nueva conversión en el sistema"""
        try:
            # TODO: Validar que la campaña existe y está activa
            # TODO: Validar que el afiliado está activo en la campaña
            # TODO: Validar código promocional
            # TODO: Detectar posibles duplicados
            # TODO: Crear entidad Conversion
            # TODO: Persistir conversión
            # TODO: Publicar evento ConversionRegistrada
            # TODO: Iniciar proceso de validación automática
            
            print(f"Conversión registrada para afiliado {comando.id_afiliado} en campaña {comando.id_campana}")
            
        except Exception as e:
            # TODO: Publicar evento RegistroConversionFallido
            raise e

class ValidarConversionHandler(ComandoHandler):
    def handle(self, comando: ValidarConversion):
        """Valida una conversión según criterios establecidos"""
        try:
            # TODO: Obtener datos de la conversión
            # TODO: Ejecutar validaciones anti-fraude
            # TODO: Verificar datos del cliente
            # TODO: Validar que no es duplicada
            # TODO: Publicar evento ConversionValidada o ConversionRechazada
            
            print(f"Validando conversión {comando.id_conversion}")
            
        except Exception as e:
            # TODO: Publicar evento ValidacionConversionFallida
            raise e

class ConfirmarConversionHandler(ComandoHandler):
    def handle(self, comando: ConfirmarConversion):
        """Confirma una conversión validada"""
        try:
            # TODO: Verificar que la conversión está validada
            # TODO: Cambiar estado a CONFIRMADA
            # TODO: Publicar evento ConversionConfirmada
            # TODO: Disparar cálculo de comisión
            
            print(f"Conversión {comando.id_conversion} confirmada por {comando.id_confirmador}")
            
        except Exception as e:
            # TODO: Publicar evento ConfirmacionConversionFallida
            raise e

class RechazarConversionHandler(ComandoHandler):
    def handle(self, comando: RechazarConversion):
        """Rechaza una conversión"""
        try:
            # TODO: Cambiar estado a RECHAZADA
            # TODO: Guardar razón del rechazo
            # TODO: Publicar evento ConversionRechazada
            # TODO: Notificar al afiliado si corresponde
            
            print(f"Conversión {comando.id_conversion} rechazada: {comando.razon_rechazo}")
            
        except Exception as e:
            raise e

class MarcarConversionComoDuplicadaHandler(ComandoHandler):
    def handle(self, comando: MarcarConversionComoDuplicada):
        """Marca una conversión como duplicada"""
        try:
            # TODO: Validar que la conversión original existe
            # TODO: Marcar como duplicada
            # TODO: Referenciar a la original
            # TODO: Publicar evento ConversionMarcadaComoDuplicada
            
            print(f"Conversión {comando.id_conversion} marcada como duplicada de {comando.id_conversion_original}")
            
        except Exception as e:
            raise e

class RevertirConversionHandler(ComandoHandler):
    def handle(self, comando: RevertirConversion):
        """Revierte una conversión confirmada"""
        try:
            # TODO: Validar que la conversión puede ser revertida
            # TODO: Calcular impacto en comisiones
            # TODO: Crear registro de reversión
            # TODO: Publicar evento ConversionRevertida
            # TODO: Disparar reversión de comisión si ya fue pagada
            
            print(f"Revirtiendo conversión {comando.id_conversion}: {comando.razon_reversion}")
            
        except Exception as e:
            raise e

class ActualizarDatosConversionHandler(ComandoHandler):
    def handle(self, comando: ActualizarDatosConversion):
        """Actualiza datos de una conversión existente"""
        try:
            # TODO: Validar permisos del actualizador
            # TODO: Crear registro de auditoría
            # TODO: Actualizar datos
            # TODO: Publicar evento DatosConversionActualizados
            
            print(f"Actualizando datos de conversión {comando.id_conversion}")
            
        except Exception as e:
            raise e

# Registrar todos los handlers
@comando.register(RegistrarConversion)
def ejecutar_registrar_conversion(comando: RegistrarConversion):
    handler = RegistrarConversionHandler()
    handler.handle(comando)

@comando.register(ValidarConversion)
def ejecutar_validar_conversion(comando: ValidarConversion):
    handler = ValidarConversionHandler()
    handler.handle(comando)

@comando.register(ConfirmarConversion)
def ejecutar_confirmar_conversion(comando: ConfirmarConversion):
    handler = ConfirmarConversionHandler()
    handler.handle(comando)

@comando.register(RechazarConversion)
def ejecutar_rechazar_conversion(comando: RechazarConversion):
    handler = RechazarConversionHandler()
    handler.handle(comando)

@comando.register(MarcarConversionComoDuplicada)
def ejecutar_marcar_duplicada(comando: MarcarConversionComoDuplicada):
    handler = MarcarConversionComoDuplicadaHandler()
    handler.handle(comando)

@comando.register(RevertirConversion)
def ejecutar_revertir_conversion(comando: RevertirConversion):
    handler = RevertirConversionHandler()
    handler.handle(comando)

@comando.register(ActualizarDatosConversion)
def ejecutar_actualizar_conversion(comando: ActualizarDatosConversion):
    handler = ActualizarDatosConversionHandler()
    handler.handle(comando)