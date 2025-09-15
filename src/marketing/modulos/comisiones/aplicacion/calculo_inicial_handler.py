"""Handler para cálculo inicial de comisión (invocado desde creación de campaña)"""
from datetime import datetime
from .calculo_inicial_command import CalcularComisionInicialCommand, ResultadoCalculoInicial
from ..infraestructura.publisher_pulsar import PulsarPublisherComisiones
from ..infraestructura.repositorio_sql import RepositorioComisionesSQL
import uuid
import logging

logger = logging.getLogger(__name__)

class CalcularComisionInicialHandler:
    def __init__(self, publisher: PulsarPublisherComisiones, repo: RepositorioComisionesSQL):
        self.publisher = publisher
        self.repo = repo

    async def handle(self, comando: CalcularComisionInicialCommand) -> ResultadoCalculoInicial:
        comando.ensure()
        comision_id = f"comision-{comando.campana_id}"
        fecha_iso = datetime.now().isoformat()

        # Payload evento integración (manteniendo compatibilidad + enriquecido)
        evento = {
            "tipo": "ComisionCalculada",
            "id": comision_id,
            "comision_id": comision_id,
            "campana_id": comando.campana_id,
            "afiliado_id": comando.afiliado_id,
            "conversion_id": comando.conversion_id,
            "monto_comision": comando.monto_base,
            "porcentaje_comision": comando.porcentaje,
            "fecha_calculo": fecha_iso,
            "moneda": comando.moneda,
            "status": "calculada",
            "correlation_id": comando.correlation_id,
            "contexto_origen": "marketing.comisiones",
            "schema_version": "1.0"
        }

        # Persistencia en tabla commission
        datos_persistencia = {
            "id": comision_id,
            "conversion_id": comando.conversion_id,
            "affiliate_id": comando.afiliado_id,
            "campaign_id": comando.campana_id,
            "gross_amount": comando.monto_base,
            "gross_currency": comando.moneda,
            "percentage": comando.porcentaje,
            "net_amount": comando.monto_base,  # igual al bruto en inicial
            "net_currency": comando.moneda,
            "status": "calculada",
            "calculated_at": fecha_iso
        }

        logger.info(
            "[Comisiones][Handler] Persistiendo comisión inicial id=%s campana_id=%s monto_base=%s porcentaje=%s correlation_id=%s",
            comision_id, comando.campana_id, comando.monto_base, comando.porcentaje, comando.correlation_id
        )
        await self.repo.guardar_comision_calculada(datos_persistencia)
        logger.info(
            "[Comisiones][Handler] Publicando evento ComisionCalculada topic=%s correlation_id=%s",
            getattr(self.publisher, '_topic_comisiones', 'desconocido'), comando.correlation_id
        )
        await self.publisher.publicar_comision_calculada(evento)
        logger.info(
            "[Comisiones][Handler] Evento ComisionCalculada publicado id=%s correlation_id=%s",
            comision_id, comando.correlation_id
        )

        return ResultadoCalculoInicial(
            comision_id=comision_id,
            publicado=True,
            persisted=True,
            correlation_id=comando.correlation_id or "",
            fecha_calculo=fecha_iso
        )
