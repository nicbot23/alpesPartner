from dataclasses import dataclass
from aeroalpes.seedwork.aplicacion.comandos import Comando
from aeroalpes.seedwork.aplicacion.mediador import manejador_comando
from aeroalpes.modulos.comisiones.aplicacion.servicios.servicio_comisiones import ServicioComisiones
from aeroalpes.modulos.comisiones.aplicacion.dto import CrearComisionDTO

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
