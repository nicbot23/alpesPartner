import pulsar
from pulsar.schema import *

from alpespartner.modulos.comisiones.infraestructura.schema.v1.eventos import EventoComissionCalculated

from alpespartner.seedwork.infraestructura import utils

class Dispatcher:
    def __init__(self):
        pass
    def publish_event(self, event, topic):
        # Logic to publish the event to the specified topic
        event = self.mapper.

        
    def public_message(self, message, topic):
        # Logic to publish the message to the specified topic
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        publisher = cliente.create_producer(topic, schema=AvroSchema(EventoComissionCalculated))
        publisher.send(message)
        cliente.close()


    def public_command(self, command, topic):
        # Logic to publish the command to the specified topic
        pass