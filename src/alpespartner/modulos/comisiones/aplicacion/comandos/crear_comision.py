from dataclasses import dataclass
from alpespartner.seedwork.aplicacion.comandos import Comando
from alpespartner.seedwork.aplicacion.mediador import manejador_comando
from alpespartner.modulos.comisiones.aplicacion.servicios.servicio_comisiones import ServicioComisiones
from alpespartner.modulos.comisiones.aplicacion.dto import CrearComisionDTO

@dataclass(frozen=True)
class CrearComision(Comando):
    conversionId:str; 
    affiliateId:str; 
    campaignId:str; 
    grossAmount:float; 
    currency:str


@manejador_comando(CrearComision)
def ejecutar(cmd: CrearComision):
    """
    Manejador de comando simplificado - el UoW y eventos se manejan en el servicio
    """
    svc = ServicioComisiones()
    return svc.calcular(CrearComisionDTO(**cmd.__dict__))
