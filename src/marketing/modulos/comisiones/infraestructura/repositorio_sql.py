"""Repositorio SQL para persistir comisiones calculadas"""
import os
import logging
from typing import Dict
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

class RepositorioComisionesSQL:
    def __init__(self) -> None:
        self._url = os.getenv('DATABASE_URL', 'mysql+pymysql://alpes:alpes@mysql-marketing:3306/alpes_marketing')
        self._engine = None

    async def inicializar(self):
        if not self._engine:
            try:
                self._engine = create_engine(self._url)
                with self._engine.connect() as conn:
                    conn.execute(text('SELECT 1'))
                logger.info('[Comisiones] Conexión BD lista')
            except Exception as e:
                logger.error(f"Error init BD Comisiones: {e}")

    async def guardar_comision_calculada(self, datos: Dict):
        if not self._engine:
            await self.inicializar()
        sql = text("""
            INSERT INTO commission (
                id, conversion_id, affiliate_id, campaign_id,
                gross_amount, gross_currency, percentage,
                net_amount, net_currency, status, calculated_at, approved_at
            ) VALUES (
                :id, :conversion_id, :affiliate_id, :campaign_id,
                :gross_amount, :gross_currency, :percentage,
                :net_amount, :net_currency, :status, :calculated_at, NULL
            ) ON DUPLICATE KEY UPDATE
                gross_amount=VALUES(gross_amount),
                net_amount=VALUES(net_amount),
                percentage=VALUES(percentage),
                status=VALUES(status),
                calculated_at=VALUES(calculated_at)
        """)
        try:
            with self._engine.connect() as conn:
                conn.execute(sql, datos)
                conn.commit()
            logger.info(f"💾 Comisión persistida {datos['id']}")
        except Exception as e:
            logger.error(f"❌ Error persistiendo comisión: {e}")
            raise
