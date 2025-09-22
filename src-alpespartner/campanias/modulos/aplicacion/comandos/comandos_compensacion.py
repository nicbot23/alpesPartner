from campanias.seedwork.aplicacion.comandos import Comando, ComandoHandler
from campanias.seedwork.aplicacion.comandos import ejecutar_commando as comando
from dataclasses import dataclass
from typing import Optional, List
import uuid

@dataclass
class CancelarCampana(Comando):
    """Comando de compensación para cancelar una campaña"""
    id_campana: str
    razon_cancelacion: str
    fecha_cancelacion: str = None

@dataclass
class DesregistrarAfiliadosDeCampana(Comando):
    """Comando de compensación para desregistrar todos los afiliados"""
    id_campana: str
    razon_desregistro: str
    notificar_afiliados: bool = True

@dataclass
class RevertirActivacionAfiliado(Comando):
    """Comando de compensación para revertir activación de afiliado"""
    id_campana: str
    id_afiliado: str
    razon_reversion: str

@dataclass
class CancelarComisionesPendientes(Comando):
    """Comando de compensación para cancelar comisiones pendientes"""
    id_campana: str
    ids_comisiones: Optional[List[str]] = None  # Si es None, cancela todas
    razon_cancelacion: str

@dataclass
class RevertirPagosComisiones(Comando):
    """Comando de compensación para revertir pagos de comisiones"""
    ids_comisiones: List[str]
    razon_reversion: str
    metodo_reversion: str  # CONTRACARGO, REEMBOLSO, AJUSTE

@dataclass
class InvalidarCodigosPromocionales(Comando):
    """Comando de compensación para invalidar códigos promocionales"""
    id_campana: str
    id_afiliado: Optional[str] = None  # Si es None, invalida todos los de la campaña
    razon_invalidacion: str

@dataclass
class RevertirConversionesAfiliado(Comando):
    """Comando de compensación para revertir conversiones de un afiliado"""
    id_campana: str
    id_afiliado: str
    razon_reversion: str

@dataclass
class FinalizarCampanaForzadamente(Comando):
    """Comando de compensación para terminar campaña por fallos críticos"""
    id_campana: str
    razon_finalizacion: str
    liquidar_pendientes: bool = True

class CancelarCampanaHandler(ComandoHandler):
    def handle(self, comando: CancelarCampana):
        """Cancela una campaña y todos sus procesos asociados"""
        try:
            # TODO: Cambiar estado de campaña a CANCELADA
            # TODO: Pausar todos los procesos activos
            # TODO: Notificar a todos los afiliados
            # TODO: Cancelar comisiones pendientes
            # TODO: Programar liquidación final
            # TODO: Publicar evento CampanaCancelada
            
            print(f"Cancelando campaña {comando.id_campana}: {comando.razon_cancelacion}")
            
        except Exception as e:
            raise e

class DesregistrarAfiliadosDeCampanaHandler(ComandoHandler):
    def handle(self, comando: DesregistrarAfiliadosDeCampana):
        """Desregistra todos los afiliados de una campaña"""
        try:
            # TODO: Obtener lista de afiliados activos
            # TODO: Cambiar estado a DESREGISTRADO
            # TODO: Invalidar códigos promocionales
            # TODO: Calcular comisiones pendientes
            # TODO: Notificar afiliados si corresponde
            # TODO: Publicar evento AfiliadosDesregistrados
            
            print(f"Desregistrando afiliados de campaña {comando.id_campana}")
            
        except Exception as e:
            raise e

class RevertirActivacionAfiliadoHandler(ComandoHandler):
    def handle(self, comando: RevertirActivacionAfiliado):
        """Revierte la activación de un afiliado específico"""
        try:
            # TODO: Cambiar estado afiliado a INACTIVO
            # TODO: Invalidar códigos promocionales
            # TODO: Marcar conversiones como suspendidas
            # TODO: Pausar comisiones pendientes
            # TODO: Publicar evento ActivacionAfiliadoRevertida
            
            print(f"Revirtiendo activación del afiliado {comando.id_afiliado}")
            
        except Exception as e:
            raise e

class CancelarComisionesPendientesHandler(ComandoHandler):
    def handle(self, comando: CancelarComisionesPendientes):
        """Cancela comisiones que están pendientes de pago"""
        try:
            # TODO: Identificar comisiones pendientes
            # TODO: Cambiar estado a CANCELADA
            # TODO: Registrar razón de cancelación
            # TODO: Actualizar métricas de campaña
            # TODO: Publicar evento ComisionesCanceladas
            
            print(f"Cancelando comisiones pendientes de campaña {comando.id_campana}")
            
        except Exception as e:
            raise e

class RevertirPagosComisionesHandler(ComandoHandler):
    def handle(self, comando: RevertirPagosComisiones):
        """Revierte pagos de comisiones ya procesados"""
        try:
            # TODO: Validar que los pagos pueden ser revertidos
            # TODO: Procesar reversión según método
            # TODO: Actualizar balance de afiliados
            # TODO: Generar comprobantes de reversión
            # TODO: Publicar evento PagosComisionesRevertidos
            
            print(f"Revirtiendo {len(comando.ids_comisiones)} pagos de comisiones")
            
        except Exception as e:
            raise e

class InvalidarCodigosPromocionalesHandler(ComandoHandler):
    def handle(self, comando: InvalidarCodigosPromocionales):
        """Invalida códigos promocionales"""
        try:
            # TODO: Identificar códigos a invalidar
            # TODO: Marcar como INVALIDADOS
            # TODO: Registrar razón y fecha
            # TODO: Notificar a afiliados afectados
            # TODO: Publicar evento CodigosPromocionalesInvalidados
            
            print(f"Invalidando códigos promocionales de campaña {comando.id_campana}")
            
        except Exception as e:
            raise e

class RevertirConversionesAfiliadoHandler(ComandoHandler):
    def handle(self, comando: RevertirConversionesAfiliado):
        """Revierte todas las conversiones de un afiliado"""
        try:
            # TODO: Obtener conversiones del afiliado
            # TODO: Marcar como REVERTIDAS
            # TODO: Calcular impacto en comisiones
            # TODO: Actualizar métricas de campaña
            # TODO: Publicar evento ConversionesAfiliadoRevertidas
            
            print(f"Revirtiendo conversiones del afiliado {comando.id_afiliado}")
            
        except Exception as e:
            raise e

class FinalizarCampanaForzadamenteHandler(ComandoHandler):
    def handle(self, comando: FinalizarCampanaForzadamente):
        """Finaliza una campaña de manera forzada por fallos críticos"""
        try:
            # TODO: Cambiar estado a FINALIZADA_FORZADAMENTE
            # TODO: Detener todos los procesos
            # TODO: Calcular liquidación final si corresponde
            # TODO: Generar reporte de cierre
            # TODO: Notificar a stakeholders
            # TODO: Publicar evento CampanaFinalizadaForzadamente
            
            print(f"Finalizando campaña {comando.id_campana} forzadamente")
            
        except Exception as e:
            raise e

# Registrar todos los handlers de compensación
@comando.register(CancelarCampana)
def ejecutar_cancelar_campana(comando: CancelarCampana):
    handler = CancelarCampanaHandler()
    handler.handle(comando)

@comando.register(DesregistrarAfiliadosDeCampana)
def ejecutar_desregistrar_afiliados(comando: DesregistrarAfiliadosDeCampana):
    handler = DesregistrarAfiliadosDeCampanaHandler()
    handler.handle(comando)

@comando.register(RevertirActivacionAfiliado)
def ejecutar_revertir_activacion(comando: RevertirActivacionAfiliado):
    handler = RevertirActivacionAfiliadoHandler()
    handler.handle(comando)

@comando.register(CancelarComisionesPendientes)
def ejecutar_cancelar_comisiones(comando: CancelarComisionesPendientes):
    handler = CancelarComisionesPendientesHandler()
    handler.handle(comando)

@comando.register(RevertirPagosComisiones)
def ejecutar_revertir_pagos(comando: RevertirPagosComisiones):
    handler = RevertirPagosComisionesHandler()
    handler.handle(comando)

@comando.register(InvalidarCodigosPromocionales)
def ejecutar_invalidar_codigos(comando: InvalidarCodigosPromocionales):
    handler = InvalidarCodigosPromocionalesHandler()
    handler.handle(comando)

@comando.register(RevertirConversionesAfiliado)
def ejecutar_revertir_conversiones(comando: RevertirConversionesAfiliado):
    handler = RevertirConversionesAfiliadoHandler()
    handler.handle(comando)

@comando.register(FinalizarCampanaForzadamente)
def ejecutar_finalizar_forzadamente(comando: FinalizarCampanaForzadamente):
    handler = FinalizarCampanaForzadamenteHandler()
    handler.handle(comando)