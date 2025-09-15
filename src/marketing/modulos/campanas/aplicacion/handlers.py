"""Handlers/Servicios de aplicación para Campañas"""
from datetime import datetime
from .comandos import CrearCampanaCommand, ResultadoCrearCampana
from ..dominio.modelos import Campana, TipoCampana, ConfiguracionCampana
from ...comisiones.aplicacion.calculo_inicial_command import CalcularComisionInicialCommand, CalcularComisionInicialCommand as CICCommand
from ...comisiones.aplicacion.calculo_inicial_handler import CalcularComisionInicialHandler
from typing import Protocol, List
import json
import uuid

class PublicadorEventos(Protocol):
    async def publicar_campana_creada(self, payload: dict): ...
    async def publicar_comision_configurada(self, payload: dict): ...
    async def publicar_notificacion(self, payload: dict): ...

class RepositorioCampanas(Protocol):
    async def guardar(self, campana_data: dict) -> None: ...

class CrearCampanaHandler:
    def __init__(self, publicador: PublicadorEventos, repositorio: RepositorioCampanas, handler_comision: CalcularComisionInicialHandler | None = None):
        self.publicador = publicador
        self.repositorio = repositorio
        self.handler_comision = handler_comision

    async def handle(self, comando: CrearCampanaCommand) -> ResultadoCrearCampana:
        comando.ensure_defaults()
        eventos_publicados: List[str] = []
        campaign_id = f"camp-{comando.nombre.replace(' ', '-').lower()}"
        timestamp = int(datetime.now().timestamp() * 1000)

        # 1. Crear entidad (para trazabilidad / futura extensión)
        campana_entidad = Campana()
        campana_entidad.crear(
            nombre=comando.nombre,
            descripcion=comando.descripcion,
            tipo=TipoCampana[comando.tipo_campana] if comando.tipo_campana in TipoCampana.__members__ else TipoCampana.PROMOCIONAL,
            creador_id="api-user"
        )

        # 2. Publicar CampanaCreada
        evento_campana = {
            "tipo": "CampanaCreada",
            "id": campaign_id,
            "campana_id": campaign_id,
            "nombre": comando.nombre,
            "descripcion": comando.descripcion,
            "tipo_campana": comando.tipo_campana,
            "fecha_inicio": comando.fecha_inicio,
            "fecha_fin": comando.fecha_fin,
            "estado": "creada",
            "meta_conversiones": comando.meta_conversiones,
            "presupuesto": float(comando.presupuesto),
            "created_by": "api-user",
            "timestamp": timestamp,
            "correlation_id": comando.correlation_id
        }
        await self.publicador.publicar_campana_creada(evento_campana)
        eventos_publicados.append("CampanaCreada")

        # 3. Calcular comisión inicial vía handler de comisiones (si disponible)
        if self.handler_comision:
            cmd_com = CalcularComisionInicialCommand(
                campana_id=campaign_id,
                monto_base=0.0,
                porcentaje=float(comando.comision_porcentaje * 100),
                correlation_id=comando.correlation_id
            )
            try:
                res_com = await self.handler_comision.handle(cmd_com)
                eventos_publicados.append("ComisionesConfiguradas")
            except Exception as e:
                # Log pero no abortar flujo de campaña
                eventos_publicados.append("ComisionesConfiguradasError")
        else:
            eventos_publicados.append("ComisionesConfiguradasPending")

        # 4. Publicar NotificacionSolicitada
        evento_notificacion = {
            "tipo": "NotificacionSolicitada",
            "id": f"notif-{campaign_id}",
            "destinatario": "marketing-team@alpes.com",
            "tipo_notificacion": "email",
            "plantilla": "nueva-campana",
            "datos": {
                "campana": comando.nombre,
                "presupuesto": comando.presupuesto
            },
            "prioridad": "alta",
            "timestamp": timestamp,
            "correlation_id": comando.correlation_id
        }
        await self.publicador.publicar_notificacion(evento_notificacion)
        eventos_publicados.append("NotificacionSolicitada")

        # 5. Simular afiliaciones
        if comando.afiliados:
            eventos_publicados.append("AfiliacionesConfiguradas")

        # 6. Persistir
        campana_bd = {
            "id": campaign_id,
            "nombre": comando.nombre,
            "descripcion": comando.descripcion,
            "marca": comando.marca,
            "categoria": comando.categoria,
            "tags": json.dumps(comando.tags),
            "fecha_inicio": datetime.strptime(comando.fecha_inicio, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S'),
            "fecha_fin": datetime.strptime(comando.fecha_fin, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S'),
            "terminos_comision": json.dumps({"porcentaje": comando.comision_porcentaje}),
            "restriccion_geografica": json.dumps({"paises": ["CO"]}),
            "estado": "BORRADOR",
            "creada_en": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "version": 1,
            "activa": True
        }
        await self.repositorio.guardar(campana_bd)
        eventos_publicados.append("CampanaPersistida")

        return ResultadoCrearCampana(
            campaign_id=campaign_id,
            eventos_publicados=eventos_publicados,
            creado_en=datetime.now().isoformat(),
            correlation_id=comando.correlation_id or ""
        )
