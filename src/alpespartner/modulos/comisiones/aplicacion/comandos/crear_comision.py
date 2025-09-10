from dataclasses import dataclass
from alpespartner.seedwork.aplicacion.comandos import Comando
from alpespartner.seedwork.aplicacion.mediador import manejador_comando
from alpespartner.modulos.comisiones.aplicacion.servicios.servicio_comisiones import ServicioComisiones
from alpespartner.modulos.comisiones.aplicacion.dto import CrearComisionDTO
from alpespartner.config.uow import UnidadTrabajoPuerto

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
    Manejador de comando actualizado para usar el patrón CDC con eventos
    """
    # Importar repositorio de eventos para CDC
    from alpespartner.modulos.comisiones.infraestructura.repositorios_eventos import RepositorioEventosComisionSQLAlchemy
    
    # Crear servicio con soporte para eventos
    svc = ServicioComisiones()
    
    # Función para obtener repositorio de eventos
    def repositorio_eventos_func():
        return RepositorioEventosComisionSQLAlchemy()
    
    # Usar UoW con soporte para eventos
    uow: UnidadTrabajoPuerto = UnidadTrabajoPuerto()
    
    with uow:
        # Calcular comisión
        resultado = svc.calcular(CrearComisionDTO(**cmd.__dict__))
        
        # Confirmar transacción con eventos usando el nuevo patrón
        uow.commit(repositorio_eventos_func=repositorio_eventos_func)
        
        return resultado
