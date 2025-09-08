import os, json, pulsar
from aeroalpes.seedwork.aplicacion.mediador import ejecutar_comando
from aeroalpes.modulos.comisiones.aplicacion.comandos.crear_comision_integracion import CrearComisionIntegracion
from aeroalpes.modulos.comisiones.aplicacion.comandos.crear_comision_integracion import ejecutar as _reg1  # noqa

PULSAR_URL=os.getenv('PULSAR_URL','pulsar://localhost:6650')
TOPIC_CMDS=os.getenv('TOPIC_CMDS','persistent://public/default/commands')

def main():
    client=pulsar.Client(PULSAR_URL)
    consumer=client.subscribe(TOPIC_CMDS,'commands.comisiones',initial_position=pulsar.InitialPosition.Latest)
    print('[commands-consumer] escuchando',TOPIC_CMDS)
    try:
        while True:
            msg=consumer.receive()
            try:
                data=json.loads(msg.data())
                tipo=data.get('type'); payload=data.get('payload') or {}
                if tipo=='CrearComisionIntegracion':
                    ejecutar_comando(CrearComisionIntegracion(**payload))
                consumer.acknowledge(msg)
            except Exception as e:
                print('error procesando comando:', e); consumer.negative_acknowledge(msg)
    finally:
        client.close()
if __name__=='__main__': main()
