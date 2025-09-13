"""Fábricas del dominio Campañas

Proporcionan métodos para crear y reconstruir agregados manteniendo
la lógica encapsulada y facilitando futuros cambios (p.ej. versiones
de eventos, reconstrucción desde snapshots, etc.)
"""

from __future__ import annotations
from typing import Optional
from .agregados import Campana, EstadoCampana
from .objetos_valor import (
    MetadatosCampana, PeriodoVigencia, TerminosComision, RestriccionGeografica
)
from datetime import datetime


class FabricaCampanas:
    """Factory estática para el agregado Campana"""

    @staticmethod
    def crear(metadatos: MetadatosCampana,
              periodo: PeriodoVigencia,
              terminos: TerminosComision,
              restricciones: RestriccionGeografica) -> Campana:
        return Campana.crear(metadatos, periodo, terminos, restricciones)

    @staticmethod
    def reconstruir(campana_id: str,
                    metadatos: MetadatosCampana,
                    periodo: PeriodoVigencia,
                    terminos: TerminosComision,
                    restricciones: RestriccionGeografica,
                    estado: EstadoCampana,
                    creada_en: datetime,
                    activada_en: Optional[datetime] = None,
                    finalizada_en: Optional[datetime] = None) -> Campana:
        """Reconstruye un agregado a partir de datos persistidos"""
        agg = Campana(
            id="temp",  # será reemplazado
            metadatos=metadatos,
            periodo_vigencia=periodo,
            terminos_comision=terminos,
            restriccion_geografica=restricciones,
            estado=estado,
            creada_en=creada_en,
            activada_en=activada_en,
            finalizada_en=finalizada_en
        )
        # Forzar el id original (el setter genera uno nuevo por diseño)
        object.__setattr__(agg, '_id', campana_id)
        return agg
