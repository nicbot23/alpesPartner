import os, json, pulsar
from alpespartner.seedwork.aplicacion.mediador import publicar_evento
from alpespartner.modulos.comisiones.aplicacion import handlers as _handlers  # ensure decorators loaded

PULSAR_URL=os.getenv('PULSAR_URL','pulsar://localhost:6650')
TOPIC=os.getenv('TOPIC_OUTBOX','persistent://public/default/outbox-events')
STORE=os.getenv('EVENT_STORE','/app/data/events.jsonl')

def main():
    os.makedirs(os.path.dirname(STORE), exist_ok=True) if '/' in STORE else None
    client=pulsar.Client(PULSAR_URL)
    consumer=client.subscribe(TOPIC,'notificaciones',initial_position=pulsar.InitialPosition.Latest)
    print('[cdc-consumer] escuchando',TOPIC)
    try:
        while True:
            msg=consumer.receive()
            try:
                data=json.loads(msg.data())
                payload=data.get('payload') or data
                after=payload.get('after') if isinstance(payload,dict) else None
                if after and 'event_type' in after and 'payload' in after:
                    tipo=after['event_type']
                    evt_payload=json.loads(after['payload']) if isinstance(after['payload'],str) else after['payload']
                    publicar_evento(tipo, evt_payload)
                    with open(STORE,'a') as f: f.write(json.dumps({'type':tipo,'evt':evt_payload})+'\n')
                consumer.acknowledge(msg)
            except Exception as e:
                print('error procesando cdc:', e); consumer.negative_acknowledge(msg)
    finally:
        client.close()
if __name__=='__main__': main()
