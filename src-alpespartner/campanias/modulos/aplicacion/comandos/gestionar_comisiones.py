from campanias.seedwork.aplicacion.comandos import Comando, ComandoHandler
from campanias.seedwork.aplicacion.comandos import ejecutar_commando as comando
from dataclasses import dataclass
from typing import Optional, List
import uuid

@dataclass
class CalcularComision(Comando):
    """Comando para calcular comisión basada en conversión"""
    id_campana: str
    id_afiliado: str
    id_conversion: str
    monto_conversion: float
    tipo_conversion: str  # VENTA, LEAD, CLICK, IMPRESION
    fecha_conversion: str
    datos_adicionales: Optional[dict] = None

@dataclass
class AprobarComision(Comando):
    """Comando para aprobar una comisión calculada"""
    id_comision: str
    id_aprobador: str
    comentarios: Optional[str] = None
    fecha_aprobacion: str = None

@dataclass
class RechazarComision(Comando):
    """Comando para rechazar una comisión"""
    id_comision: str
    id_rechazador: str
    razon_rechazo: str
    fecha_rechazo: str = None

@dataclass
class PagarComision(Comando):
    """Comando para procesar el pago de comisión"""
    id_comision: str
    metodo_pago: str  # TRANSFERENCIA, PAYPAL, CRYPTO
    cuenta_destino: str
    fecha_pago_programada: str = None
    referencia_pago: Optional[str] = None

@dataclass
class AgruparComisionesParaPago(Comando):
    """Comando para agrupar múltiples comisiones en un solo pago"""
    id_afiliado: str
    ids_comisiones: List[str]
    fecha_agrupacion: str = None
    periodo_agrupacion: str  # SEMANAL, QUINCENAL, MENSUAL

@dataclass
class RevertirComision(Comando):
    """Comando para revertir una comisión (por devolución, fraude, etc.)"""
    id_comision: str
    razon_reversion: str
    monto_revertir: Optional[float] = None  # Si es parcial
    fecha_reversion: str = None

class CalcularComisionHandler(ComandoHandler):
    def handle(self, comando: CalcularComision):
        """Calcula la comisión según las reglas de la campaña"""
        try:
            # TODO: Obtener reglas de comisión de la campaña
            # TODO: Obtener nivel de afiliado
            # TODO: Calcular monto de comisión
            # TODO: Aplicar descuentos/bonificaciones
            # TODO: Crear entidad Comision
            # TODO: Persistir comisión
            # TODO: Publicar evento ComisionCalculada
            
            print(f"Comisión calculada para afiliado {comando.id_afiliado} en campaña {comando.id_campana}")
            
        except Exception as e:
            # TODO: Publicar evento CalculoComisionFallido
            raise e

class AprobarComisionHandler(ComandoHandler):
    def handle(self, comando: AprobarComision):
        """Aprueba una comisión para pago"""
        try:
            # TODO: Validar que existe la comisión
            # TODO: Verificar permisos del aprobador
            # TODO: Cambiar estado a APROBADA
            # TODO: Actualizar fecha de aprobación
            # TODO: Publicar evento ComisionAprobada
            # TODO: Programar para próximo ciclo de pago
            
            print(f"Comisión {comando.id_comision} aprobada por {comando.id_aprobador}")
            
        except Exception as e:
            # TODO: Publicar evento AprobacionComisionFallida
            raise e

class RechazarComisionHandler(ComandoHandler):
    def handle(self, comando: RechazarComision):
        """Rechaza una comisión"""
        try:
            # TODO: Cambiar estado a RECHAZADA
            # TODO: Guardar razón del rechazo
            # TODO: Publicar evento ComisionRechazada
            # TODO: Notificar al afiliado
            
            print(f"Comisión {comando.id_comision} rechazada: {comando.razon_rechazo}")
            
        except Exception as e:
            raise e

class PagarComisionHandler(ComandoHandler):
    def handle(self, comando: PagarComision):
        """Procesa el pago de la comisión"""
        try:
            # TODO: Validar cuenta destino
            # TODO: Verificar saldo disponible
            # TODO: Procesar pago según método
            # TODO: Cambiar estado a PAGADA
            # TODO: Generar comprobante
            # TODO: Publicar evento ComisionPagada
            
            print(f"Procesando pago de comisión {comando.id_comision}")
            
        except Exception as e:
            # TODO: Publicar evento PagoComisionFallido
            raise e

class AgruparComisionesParaPagoHandler(ComandoHandler):
    def handle(self, comando: AgruparComisionesParaPago):
        """Agrupa comisiones para pago masivo"""
        try:
            # TODO: Validar que todas las comisiones están aprobadas
            # TODO: Crear agrupación de pago
            # TODO: Calcular total
            # TODO: Publicar evento ComisionesAgrupadasParaPago
            
            print(f"Agrupando {len(comando.ids_comisiones)} comisiones para afiliado {comando.id_afiliado}")
            
        except Exception as e:
            raise e

class RevertirComisionHandler(ComandoHandler):
    def handle(self, comando: RevertirComision):
        """Revierte una comisión pagada"""
        try:
            # TODO: Validar que la comisión puede ser revertida
            # TODO: Calcular monto a revertir
            # TODO: Crear comisión negativa
            # TODO: Actualizar balance del afiliado
            # TODO: Publicar evento ComisionRevertida
            
            print(f"Revirtiendo comisión {comando.id_comision}: {comando.razon_reversion}")
            
        except Exception as e:
            raise e

# Registrar todos los handlers
@comando.register(CalcularComision)
def ejecutar_calcular_comision(comando: CalcularComision):
    handler = CalcularComisionHandler()
    handler.handle(comando)

@comando.register(AprobarComision)
def ejecutar_aprobar_comision(comando: AprobarComision):
    handler = AprobarComisionHandler()
    handler.handle(comando)

@comando.register(RechazarComision)
def ejecutar_rechazar_comision(comando: RechazarComision):
    handler = RechazarComisionHandler()
    handler.handle(comando)

@comando.register(PagarComision)
def ejecutar_pagar_comision(comando: PagarComision):
    handler = PagarComisionHandler()
    handler.handle(comando)

@comando.register(AgruparComisionesParaPago)
def ejecutar_agrupar_comisiones(comando: AgruparComisionesParaPago):
    handler = AgruparComisionesParaPagoHandler()
    handler.handle(comando)

@comando.register(RevertirComision)
def ejecutar_revertir_comision(comando: RevertirComision):
    handler = RevertirComisionHandler()
    handler.handle(comando)