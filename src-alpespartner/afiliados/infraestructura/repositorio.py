from typing import List
from ..dominio.entidades import Afiliado
from ..dominio.eventos import AfiliadoCreado, AfiliadoActualizado, AfiliadoActivado, AfiliadoDesactivado

class RepositorioEventSourcingAfiliados:
    def __init__(self):
        # En una implementación real, esto sería una base de datos de eventos
        self._event_store: List = []

    def agregar_evento(self, evento):
        self._event_store.append(evento)

    def obtener_eventos(self, afiliado_id: str) -> List:
        return [e for e in self._event_store if getattr(e, 'id_afiliado', None) == afiliado_id]

    def reconstruir_afiliado(self, afiliado_id: str) -> Afiliado:
        eventos = self.obtener_eventos(afiliado_id)
        afiliado = None
        for evento in eventos:
            if isinstance(evento, AfiliadoCreado):
                afiliado = Afiliado(
                    id=evento.id_afiliado,
                    nombre=evento.nombre,
                    email=evento.email,
                    tipo_afiliado=evento.tipo_afiliado,
                    nivel_comision=evento.nivel_comision,
                    fecha_registro=evento.fecha_registro,
                    eventos=[evento]
                )
            elif afiliado:
                afiliado.aplicar_evento(evento)
        return afiliado

    def obtener_todos(self) -> List[Afiliado]:
        afiliado_ids = set(getattr(e, 'id_afiliado', None) for e in self._event_store)
        return [self.reconstruir_afiliado(aid) for aid in afiliado_ids if aid]
