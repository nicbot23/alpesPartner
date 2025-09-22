import pulsar
from ..dominio.eventos import AfiliadoCreado, AfiliadoActualizado, AfiliadoActivado, AfiliadoDesactivado

class ProductorEventosAfiliados:
    def __init__(self, pulsar_host: str):
        self.pulsar_host = pulsar_host
        self.client = pulsar.Client(f'pulsar://{self.pulsar_host}')
        self.producer = self.client.create_producer('evento-afiliado')

    def publicar_evento(self, evento):
        # Serialización simple, se recomienda usar json o avro en producción
        self.producer.send(str(evento).encode('utf-8'))

    def cerrar(self):
        self.client.close()
