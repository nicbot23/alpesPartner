from alpespartner.seedwork.aplicacion.mediador import manejador_evento
import os, json
from alpespartner.seedwork.aplicacion.handlers import Handler
from alpespartner.modulos.vuelos.infraestructura.despachadores import Despachador

STORE=os.getenv('EVENT_STORE','/app/data/events.jsonl')
os.makedirs(os.path.dirname(STORE), exist_ok=True) if '/' in STORE else None


@manejador_evento('CommissionCalculated')
def on_calculated(evt:dict):
    with open(STORE,'a') as f: 
        f.write(json.dumps({'type':'CommissionCalculated','evt':evt})+'\n')

@manejador_evento('CommissionApproved')
def on_approved(evt:dict):
    with open(STORE,'a') as f: 
        f.write(json.dumps({'type':'CommissionApproved','evt':evt})+'\n')



class HandlerReservaIntegracion(Handler):

    @staticmethod
    def handle_comission_creada(evento):
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-comission')

    @staticmethod
    def handle_comission_cancelada(evento):
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-comission')

    @staticmethod
    def handle_comission_aprobada(evento):
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-comission')