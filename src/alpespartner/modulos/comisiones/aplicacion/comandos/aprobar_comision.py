from dataclasses import dataclass
from alpespartner.seedwork.aplicacion.comandos import Comando
from alpespartner.seedwork.aplicacion.mediador import manejador_comando
from alpespartner.modulos.comisiones.aplicacion.servicios.servicio_comisiones import ServicioComisiones

@dataclass(frozen=True)
class AprobarComision(Comando): 
    commissionId:str

@manejador_comando(AprobarComision)
def ejecutar(cmd: AprobarComision):
    svc=ServicioComisiones(); 
    return svc.aprobar(cmd.commissionId)
