# afiliados/modulos/aplicacion/handlers.py
from __future__ import annotations
import os
import logging
from typing import Dict, Any, List

from afiliados.despachadores import DespachadorAfiliados

log = logging.getLogger(__name__)


class HandlerComandosAfiliados:
    """
    Encapsula la lógica de negocio de Afiliados para el comando
    'buscar afiliados elegibles'. El consumidor solo delega aquí.
    """

    def __init__(self, pulsar_url: str | None = None):
        self.pulsar_url = pulsar_url or f"pulsar://{os.getenv('PULSAR_HOST','broker')}:6650"
        self.desp = DespachadorAfiliados(self.pulsar_url)

    async def handle_buscar_afiliados_elegibles(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        payload esperado:
          {
            "saga_id": "...",                 # si no viene, se usa campania_id
            "campania_id": "...",
            "segmento_audiencia": "general" | "...",
            ...
          }
        """
        saga_id = str(payload.get("saga_id") or payload.get("campania_id"))
        seg = (payload.get("segmento_audiencia") or "general").lower()

        # Bandera para probar compensaciones sin tocar código
        force_fail = os.getenv("AFILIADOS_FORCE_FAIL", "false").lower() in ("1", "true", "yes")

        if force_fail or seg in {"ninguno", "vacio", "vacío"}:
            detalle = {"criterios": seg, "encontrados": 0}
            await self.desp.publicar_evento_saga_fallido(
                saga_id=saga_id,
                paso="solicitar_afiliados_elegibles",
                motivo="No hay afiliados elegibles",
                detalle=detalle,
            )
            return {"ok": False, "detalle": detalle}

        # Lógica dummy de elegibilidad (puedes reemplazar luego por consultas reales)
        base: List[str] = ["af-001", "af-002", "af-003", "af-004", "af-005"]
        detalle = {
            "criterios": seg,
            "encontrados": len(base),
            "afiliados": base,
        }
        await self.desp.publicar_evento_saga_ok(
            saga_id=saga_id,
            paso="solicitar_afiliados_elegibles",
            detalle=detalle,
        )
        return {"ok": True, "detalle": detalle}



# from afiliados.seedwork.aplicacion.handlers import Handler
# from afiliados.dominio.eventos import AfiliadoCreado, AfiliadoActualizado, AfiliadoActivado, AfiliadoDesactivado
# from afiliados.infraestructura.despachadores import Despachador

# class HandlerAfiliadosIntegracion(Handler):
#     """Handler para eventos de dominio de afiliados - los publica a otros microservicios"""

#     @staticmethod
#     def handle_afiliado_creado(evento):
#         despachador = Despachador()
#         despachador.publicar_evento(evento, 'eventos-afiliado')

#     @staticmethod
#     def handle_afiliado_actualizado(evento):
#         despachador = Despachador()
#         despachador.publicar_evento(evento, 'eventos-afiliado')

#     @staticmethod
#     def handle_afiliado_activado(evento):
#         despachador = Despachador()
#         despachador.publicar_evento(evento, 'eventos-afiliado')

#     @staticmethod
#     def handle_afiliado_desactivado(evento):
#         despachador = Despachador()
#         despachador.publicar_evento(evento, 'eventos-afiliado')
