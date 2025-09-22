import pulsar
from ..dominio.eventos import AfiliadoCreado, AfiliadoActualizado, AfiliadoActivado, AfiliadoDesactivado
from ..infraestructura.repositorio import RepositorioEventSourcingAfiliados
from ..infraestructura.productor import ProductorEventosAfiliados

# Este consumidor escucha eventos de campanias y dispara comandos/eventos de afiliados
class ConsumidorEventoscampaniasAfiliados:
    def __init__(self, pulsar_host: str, repositorio: RepositorioEventSourcingAfiliados):
        self.pulsar_host = pulsar_host
        self.repositorio = repositorio
        self.client = pulsar.Client(f'pulsar://{self.pulsar_host}')
        self.consumer = self.client.subscribe('eventos-campania', subscription_name='afiliados-campanias')
        self.productor = ProductorEventosAfiliados(self.pulsar_host)

    def escuchar(self):
        while True:
            msg = self.consumer.receive()
            try:
                evento = self._deserializar_evento(msg.data())
                self._procesar_evento(evento)
                self.consumer.acknowledge(msg)
            except Exception as error:
                self._publicar_evento_fallo(msg.data(), str(error))
                self.consumer.acknowledge(msg)

    def _publicar_evento_fallo(self, raw_data, error_msg):
        import json
        # Publica un evento de fallo en el tópico de coordinación
        productor_fallo = self.client.create_producer('evento-afiliado-fallo')
        evento_fallo = {
            'tipo': 'AfiliadoCreacionFallida',
            'error': error_msg,
            'data_original': raw_data.decode('utf-8') if hasattr(raw_data, 'decode') else str(raw_data)
        }
        productor_fallo.send(json.dumps(evento_fallo).encode('utf-8'))
        productor_fallo.close()

    def _deserializar_evento(self, data):
        import json
        try:
            evento = json.loads(data.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Error al deserializar evento de campaña: {e}")

        # Validación básica de campos requeridos
        tipo = evento.get('tipo')
        if tipo != 'CampaniaCreada':
            raise ValueError(f"Tipo de evento no soportado: {tipo}")

        campos_requeridos = ['id_afiliado', 'nombre', 'email', 'tipo_afiliado', 'nivel_comision', 'fecha_registro']
        for campo in campos_requeridos:
            if campo not in evento:
                raise ValueError(f"Falta campo requerido en evento: {campo}")

        return evento

    def _procesar_evento(self, evento):
        if evento['tipo'] == 'CampaniaCreada':
            afiliado_evento = AfiliadoCreado(
                id_afiliado=evento['id_afiliado'],
                nombre=evento['nombre'],
                email=evento['email'],
                tipo_afiliado=evento['tipo_afiliado'],
                nivel_comision=evento['nivel_comision'],
                fecha_registro=evento['fecha_registro']
            )
            self.repositorio.agregar_evento(afiliado_evento)
            self.productor.publicar_evento(afiliado_evento)
        # Agregar lógica para otros tipos de eventos de campaña

    def cerrar(self):
        self.productor.cerrar()
        self.client.close()
