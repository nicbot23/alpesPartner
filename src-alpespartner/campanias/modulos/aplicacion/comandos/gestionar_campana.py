from campanias.seedwork.aplicacion.comandos import Comando, ComandoHandler
from campanias.seedwork.aplicacion.comandos import ejecutar_commando as comando
from dataclasses import dataclass
import uuid

@dataclass
class ActivarCampana(Comando):
    """Comando para activar una campaña"""
    id_campana: str
    fecha_activacion: str = None

@dataclass
class PausarCampana(Comando):
    """Comando para pausar una campaña temporalmente"""
    id_campana: str
    razon: str
    fecha_pausa: str = None

@dataclass
class TerminarCampana(Comando):
    """Comando para terminar una campaña definitivamente"""
    id_campana: str
    razon: str
    fecha_terminacion: str = None

class ActivarCampanaHandler(ComandoHandler):
    def handle(self, comando: ActivarCampana):
        # TODO: Validar que la campaña existe y puede ser activada
        # TODO: Cambiar estado a ACTIVA
        # TODO: Publicar evento CampanaActivada
        # TODO: Iniciar procesos de notificación a afiliados
        pass

class PausarCampanaHandler(ComandoHandler):
    def handle(self, comando: PausarCampana):
        # TODO: Validar que la campaña está activa
        # TODO: Cambiar estado a PAUSADA
        # TODO: Publicar evento CampanaPausada
        # TODO: Pausar procesos relacionados
        pass

class TerminarCampanaHandler(ComandoHandler):
    def handle(self, comando: TerminarCampana):
        # TODO: Cambiar estado a TERMINADA
        # TODO: Publicar evento CampanaTerminada
        # TODO: Iniciar proceso de liquidación final
        # TODO: Calcular comisiones pendientes
        pass

# Registrar handlers
@comando.register(ActivarCampana)
def ejecutar_activar_campana(comando: ActivarCampana):
    handler = ActivarCampanaHandler()
    handler.handle(comando)

@comando.register(PausarCampana)
def ejecutar_pausar_campana(comando: PausarCampana):
    handler = PausarCampanaHandler()
    handler.handle(comando)

@comando.register(TerminarCampana)
def ejecutar_terminar_campana(comando: TerminarCampana):
    handler = TerminarCampanaHandler()
    handler.handle(comando)