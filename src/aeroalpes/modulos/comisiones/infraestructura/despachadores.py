import os, json, pulsar
PULSAR_URL=os.getenv('PULSAR_URL','pulsar://localhost:6650')
TOPIC_CMDS=os.getenv('TOPIC_CMDS','persistent://public/default/commands')
def publicar_comando_integracion(tipo:str, payload:dict):
    client=pulsar.Client(PULSAR_URL)
    try:
        producer=client.create_producer(TOPIC_CMDS)
        producer.send(json.dumps({'type': tipo, 'payload': payload}).encode('utf-8'))
    finally:
        client.close()
