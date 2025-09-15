"""Repositorio SQL para Campañas"""
import logging
import os
from typing import Dict
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

class RepositorioCampanasSQL:
    def __init__(self):
        self.engine = None
        self._db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://alpes:alpes@mysql-marketing:3306/alpes_marketing')

    async def inicializar(self):
        if not self.engine:
            try:
                self.engine = create_engine(self._db_url)
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("[Campañas] Conexión BD lista")
            except Exception as e:
                logger.error(f"Error inicializando BD Campañas: {e}")

    async def guardar(self, campana_data: Dict):
        if not self.engine:
            await self.inicializar()
        insert_sql = text("""
            INSERT INTO campanas (
                id, nombre, descripcion, marca, categoria, tags,
                fecha_inicio, fecha_fin, terminos_comision, restriccion_geografica,
                estado, creada_en, version, activa
            ) VALUES (
                :id, :nombre, :descripcion, :marca, :categoria, :tags,
                :fecha_inicio, :fecha_fin, :terminos_comision, :restriccion_geografica,
                :estado, :creada_en, :version, :activa
            )
        """)
        try:
            with self.engine.connect() as conn:
                conn.execute(insert_sql, campana_data)
                conn.commit()
            logger.info(f"💾 Campaña persistida {campana_data['id']}")
        except Exception as e:
            logger.error(f"❌ Error guardando campaña: {e}")
            raise
