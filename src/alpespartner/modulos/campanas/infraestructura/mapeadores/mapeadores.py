"""Mapeadores de infraestructura para Campañas

Se encargan de traducir entre el agregado de dominio y los DTOs/Outbox.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from alpespartner.modulos.campanas.dominio.agregados import Campana, EstadoCampana
from alpespartner.modulos.campanas.dominio.eventos import (
    CampanaCreada, CampanaActivada, CampanaDesactivada, TerminosModificados
)
from alpespartner.modulos.campanas.dominio.objetos_valor import (
    MetadatosCampana, PeriodoVigencia, TerminosComision, RestriccionGeografica
)
from ..modelos import CampanaDTO

# Reutilizamos OutboxEvent existente (ubicado en módulo comisiones) hasta factorizarlo a seedwork
from alpespartner.seedwork.infraestructura.outbox.modelos import OutboxEvent


def _uuid() -> str:
    return str(uuid.uuid4())


def a_modelo(agg: Campana) -> CampanaDTO:
    """Mapea agregado Campana -> DTO persistible"""
    return CampanaDTO(
        id=agg.id,
        nombre=agg.metadatos.nombre,
        descripcion=agg.metadatos.descripcion,
        marca=agg.metadatos.marca,
        categoria=agg.metadatos.categoria,
        tags=list(agg.metadatos.tags),
        fecha_inicio=agg.periodo_vigencia.inicio,
        fecha_fin=agg.periodo_vigencia.fin,
        terminos_comision={
            'porcentaje_base': float(agg.terminos_comision.porcentaje_base),
            'porcentaje_premium': float(agg.terminos_comision.porcentaje_premium),
            'umbral_premium': float(agg.terminos_comision.umbral_premium),
            'moneda': agg.terminos_comision.moneda
        },
        restriccion_geografica={
            'paises_permitidos': agg.restriccion_geografica.paises_permitidos,
            'regiones_excluidas': agg.restriccion_geografica.regiones_excluidas
        },
        estado=agg.estado.value,
        creada_en=agg.creada_en,
        activada_en=agg.activada_en,
        finalizada_en=agg.finalizada_en,
        version=1,
        activa=True
    )


def _payload_base(evt, agg: Campana) -> dict:
    return {
        'aggregate': 'Campana',
        'campanaId': agg.id,
        'nombre': agg.metadatos.nombre,
        'marca': agg.metadatos.marca,
        'eventVersion': 1
    }


def a_outbox(evt, agg: Campana):  # -> OutboxEvent | None (compatibilidad py<3.10)
    """Mapea evento de dominio -> OutboxEvent (CDC)"""
    base = _payload_base(evt, agg)

    if isinstance(evt, CampanaCreada):
        payload = {
            **base,
            'eventType': 'CampanaCreada',
            'creadaEn': agg.creada_en.isoformat() + 'Z'
        }
        return OutboxEvent(
            id=_uuid(),
            aggregate_type='Campana',
            aggregate_id=agg.id,
            event_type='CampanaCreada',
            payload=payload,
            occurred_at=evt.occurred_at or datetime.utcnow(),
            published=False,
            correlation_id=evt.correlation_id or str(evt.id),
            causation_id=evt.causation_id
        )

    if isinstance(evt, CampanaActivada):
        payload = {
            **base,
            'eventType': 'CampanaActivada',
            'fechaInicio': agg.periodo_vigencia.inicio.isoformat() + 'Z',
            'fechaFin': agg.periodo_vigencia.fin.isoformat() + 'Z'
        }
        return OutboxEvent(
            id=_uuid(),
            aggregate_type='Campana',
            aggregate_id=agg.id,
            event_type='CampanaActivada',
            payload=payload,
            occurred_at=evt.occurred_at or datetime.utcnow(),
            published=False,
            correlation_id=evt.correlation_id or str(evt.id),
            causation_id=evt.causation_id
        )

    if isinstance(evt, CampanaDesactivada):
        payload = {
            **base,
            'eventType': 'CampanaDesactivada',
            'motivo': evt.motivo
        }
        return OutboxEvent(
            id=_uuid(),
            aggregate_type='Campana',
            aggregate_id=agg.id,
            event_type='CampanaDesactivada',
            payload=payload,
            occurred_at=evt.occurred_at or datetime.utcnow(),
            published=False,
            correlation_id=evt.correlation_id or str(evt.id),
            causation_id=evt.causation_id
        )

    if isinstance(evt, TerminosModificados):
        payload = {
            **base,
            'eventType': 'TerminosModificados',
            'porcentajeAnterior': evt.porcentaje_anterior,
            'porcentajeNuevo': evt.porcentaje_nuevo
        }
        return OutboxEvent(
            id=_uuid(),
            aggregate_type='Campana',
            aggregate_id=agg.id,
            event_type='TerminosModificados',
            payload=payload,
            occurred_at=evt.occurred_at or datetime.utcnow(),
            published=False,
            correlation_id=evt.correlation_id or str(evt.id),
            causation_id=evt.causation_id
        )

    return None


def dto_a_agregado(dto: CampanaDTO) -> Campana:
    """Reconstruye un agregado desde el DTO (sin disparar eventos)"""
    from alpespartner.modulos.campanas.dominio.fabricas import FabricaCampanas

    metadatos = MetadatosCampana(
        nombre=dto.nombre,
        descripcion=dto.descripcion,
        marca=dto.marca,
        categoria=dto.categoria,
        tags=list(dto.tags or [])
    )
    periodo = PeriodoVigencia(inicio=dto.fecha_inicio, fin=dto.fecha_fin)
    terminos = TerminosComision(
        porcentaje_base=dto.terminos_comision['porcentaje_base'],
        porcentaje_premium=dto.terminos_comision['porcentaje_premium'],
        umbral_premium=dto.terminos_comision['umbral_premium'],
        moneda=dto.terminos_comision['moneda']
    )
    restricciones = RestriccionGeografica(
        paises_permitidos=dto.restriccion_geografica['paises_permitidos'],
        regiones_excluidas=dto.restriccion_geografica['regiones_excluidas']
    )
    estado = EstadoCampana[dto.estado]

    agg = FabricaCampanas.reconstruir(
        campana_id=dto.id,
        metadatos=metadatos,
        periodo=periodo,
        terminos=terminos,
        restricciones=restricciones,
        estado=estado,
        creada_en=dto.creada_en,
        activada_en=dto.activada_en,
        finalizada_en=dto.finalizada_en
    )
    return agg
