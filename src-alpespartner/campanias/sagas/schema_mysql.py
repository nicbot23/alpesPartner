# campanias/sagas/schema_mysql.py
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

def ensure_schema(engine):
    """
    Si la tabla 'sagas' no existe en la BD actual, crea un esquema mínimo compatible (PK 'id').
    Si existe, no hace cambios.
    """
    with engine.begin() as conn:
        exists = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name='sagas'
        """)).scalar_one()
        if exists == 0:
            logger.warning("No existe tabla 'sagas'. Creando esquema mínimo con PK 'id'.")
            conn.execute(text("""
                CREATE TABLE `sagas` (
                  `id` VARCHAR(36) NOT NULL,
                  `nombre_saga`   VARCHAR(255) NULL,
                  `estado`        VARCHAR(50)  NULL,
                  `contexto`      JSON NULL,
                  `error_mensaje` TEXT NULL,
                  `fecha_inicio`  TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                  `fecha_fin`     DATETIME NULL,
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """))

        exists = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name='saga_pasos'
        """)).scalar_one()
        if exists == 0:
            logger.info("Creando tabla 'saga_pasos' mínima.")
            conn.execute(text("""
                CREATE TABLE `saga_pasos` (
                  `id` VARCHAR(36) NOT NULL,
                  `saga_id` VARCHAR(36) NOT NULL,
                  `paso_numero` INT NOT NULL,
                  `nombre_paso` VARCHAR(255) NOT NULL,
                  `servicio` VARCHAR(100) NOT NULL,
                  `comando`  VARCHAR(100) NOT NULL,
                  `tipo_operacion` VARCHAR(20) DEFAULT 'ACCION',
                  `estado` VARCHAR(20) DEFAULT 'PENDIENTE',
                  `request_data` JSON NULL,
                  `response_data` JSON NULL,
                  `error_mensaje` TEXT NULL,
                  `fecha_inicio` DATETIME NULL,
                  `fecha_fin` DATETIME NULL,
                  PRIMARY KEY (`id`),
                  KEY `idx_saga` (`saga_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """))
