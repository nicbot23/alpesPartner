from dataclasses import dataclass
from aeroalpes.seedwork.aplicacion.comandos import Comando
from aeroalpes.seedwork.aplicacion.mediador import manejador_comando
from aeroalpes.modulos.comisiones.aplicacion.servicios.servicio_comisiones import ServicioComisiones

@dataclass(frozen=True)
class AprobarComision(Comando): 
    commissionId:str

@manejador_comando(AprobarComision)
def ejecutar(cmd: AprobarComision):
    svc=ServicioComisiones(); 
    return svc.aprobar(cmd.commissionId)
