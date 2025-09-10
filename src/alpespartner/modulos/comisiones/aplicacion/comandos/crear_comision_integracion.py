from dataclasses import dataclass
from alpespartner.seedwork.aplicacion.comandos import Comando
from alpespartner.seedwork.aplicacion.mediador import manejador_comando
from alpespartner.modulos.comisiones.aplicacion.servicios.servicio_comisiones import ServicioComisiones
from alpespartner.modulos.comisiones.aplicacion.dto import CrearComisionDTO

@dataclass(frozen=True)
class CrearComisionIntegracion(Comando):
    conversionId:str; 
    affiliateId:str; 
    campaignId:str; 
    grossAmount:float; 
    currency:str

@manejador_comando(CrearComisionIntegracion)
def ejecutar(cmd: CrearComisionIntegracion):
    svc=ServicioComisiones(); return svc.calcular(CrearComisionDTO(**cmd.__dict__))
