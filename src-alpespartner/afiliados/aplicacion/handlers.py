from afiliados.seedwork.aplicacion.handlers import Handler
from afiliados.dominio.eventos import AfiliadoCreado, AfiliadoActualizado, AfiliadoActivado, AfiliadoDesactivado
from afiliados.infraestructura.despachadores import Despachador

class HandlerAfiliadosIntegracion(Handler):
    """Handler para eventos de dominio de afiliados - los publica a otros microservicios"""

    @staticmethod
    def handle_afiliado_creado(evento):
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-afiliado')

    @staticmethod
    def handle_afiliado_actualizado(evento):
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-afiliado')

    @staticmethod
    def handle_afiliado_activado(evento):
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-afiliado')

    @staticmethod
    def handle_afiliado_desactivado(evento):
        despachador = Despachador()
        despachador.publicar_evento(evento, 'eventos-afiliado')
