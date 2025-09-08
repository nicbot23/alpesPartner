from aeroalpes.seedwork.aplicacion.mediador import manejador_evento
import os, json

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
