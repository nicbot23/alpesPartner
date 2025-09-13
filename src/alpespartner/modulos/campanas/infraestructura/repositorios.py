"""Repositorio SQLAlchemy para Campañas

Implementa el puerto `RepositorioCampanas` usando los DTOs y mapeadores definidos.
Genera eventos Outbox reusando el modelo existente mientras se factoriza al seedwork.
"""

from __future__ import annotations
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from alpespartner.modulos.campanas.dominio.repositorios import RepositorioCampanas
from alpespartner.modulos.campanas.dominio.agregados import Campana, EstadoCampana
from .modelos import CampanaDTO
from .mapeadores.mapeadores import a_modelo, a_outbox, dto_a_agregado

# Reutilizamos OutboxEvent (ubicado en comisiones)
from alpespartner.seedwork.infraestructura.outbox.modelos import OutboxEvent

from alpespartner.config.db import db  # Flask SQLAlchemy wrapper


class RepositorioCampanasMySQL(RepositorioCampanas):
	"""Implementación concreta con SQLAlchemy"""

	def __init__(self, session: Session | None = None):
		# Permite inyectar sesión (p.ej. para pruebas) o usar la global de Flask
		self.session: Session = session or db.session

	# --------------------------- Métodos del contrato --------------------------- #
	def guardar(self, campana: Campana) -> str:
		existente = self.session.get(CampanaDTO, campana.id)
		if existente:
			# Actualización (mantener versión simple por ahora)
			existente.nombre = campana.metadatos.nombre
			existente.descripcion = campana.metadatos.descripcion
			existente.marca = campana.metadatos.marca
			existente.categoria = campana.metadatos.categoria
			existente.tags = list(campana.metadatos.tags)
			existente.fecha_inicio = campana.periodo_vigencia.inicio
			existente.fecha_fin = campana.periodo_vigencia.fin
			existente.terminos_comision = {
				'porcentaje_base': float(campana.terminos_comision.porcentaje_base),
				'porcentaje_premium': float(campana.terminos_comision.porcentaje_premium),
				'umbral_premium': float(campana.terminos_comision.umbral_premium),
				'moneda': campana.terminos_comision.moneda
			}
			existente.restriccion_geografica = {
				'paises_permitidos': campana.restriccion_geografica.paises_permitidos,
				'regiones_excluidas': campana.restriccion_geografica.regiones_excluidas
			}
			existente.estado = campana.estado.value
			existente.activada_en = campana.activada_en
			existente.finalizada_en = campana.finalizada_en
		else:
			self.session.add(a_modelo(campana))

		# Procesar eventos de dominio -> Outbox
		for evt in getattr(campana, '_eventos', []):
			out = a_outbox(evt, campana)
			if out:
				self.session.add(out)
		# Limpiar eventos ya mapeados
		if hasattr(campana, 'pull_eventos'):
			campana.pull_eventos()
		return campana.id

	def obtener_por_id(self, campana_id: str) -> Optional[Campana]:
		dto = self.session.get(CampanaDTO, campana_id)
		if not dto:
			return None
		return dto_a_agregado(dto)

	def listar_activas(self, limite: int, offset: int) -> List[Campana]:
		stmt = (
			select(CampanaDTO)
			.where(CampanaDTO.estado == EstadoCampana.ACTIVA.value)
			.order_by(CampanaDTO.creada_en.desc())
			.limit(limite).offset(offset)
		)
		dtos = self.session.execute(stmt).scalars().all()
		return [dto_a_agregado(d) for d in dtos]

	def existe_campana_activa_para_marca(self, marca: str) -> bool:
		stmt = select(func.count()).select_from(CampanaDTO).where(
			CampanaDTO.marca == marca,
			CampanaDTO.estado == EstadoCampana.ACTIVA.value
		)
		total = self.session.execute(stmt).scalar_one()
		return total > 0

	# --------------------------- Métodos auxiliares --------------------------- #
	def obtener_outbox_pendiente(self, limite: int = 50) -> list[OutboxEvent]:
		"""Devuelve eventos outbox no publicados relacionados a campañas"""
		stmt = select(OutboxEvent).where(
			OutboxEvent.aggregate_type == 'Campana',
			OutboxEvent.published == False  # noqa: E712
		).limit(limite)
		return self.session.execute(stmt).scalars().all()

