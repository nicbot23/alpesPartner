CREATE TABLE IF NOT EXISTS commission (id CHAR(36) PRIMARY KEY, conversion_id CHAR(36) UNIQUE NOT NULL, affiliate_id VARCHAR(64) NOT NULL, campaign_id VARCHAR(64) NOT NULL, gross_amount DECIMAL(12,2) NOT NULL, gross_currency CHAR(3) NOT NULL, percentage DECIMAL(5,2) NOT NULL, net_amount DECIMAL(12,2) NOT NULL, net_currency CHAR(3) NOT NULL, status VARCHAR(16) NOT NULL, calculated_at TIMESTAMP NOT NULL, approved_at TIMESTAMP NULL);
CREATE TABLE IF NOT EXISTS commission_policy (id CHAR(36) PRIMARY KEY, name VARCHAR(128) NOT NULL, version INT NOT NULL, active_from TIMESTAMP NOT NULL, active_to TIMESTAMP NULL);
CREATE TABLE IF NOT EXISTS commission_rule (id CHAR(36) PRIMARY KEY, policy_id CHAR(36) NOT NULL, scope VARCHAR(16) NOT NULL, formula VARCHAR(16) NOT NULL, payload JSON NOT NULL);
-- Outbox unificado (se añaden columnas de correlación/causación para trazabilidad cross-aggregate)
CREATE TABLE IF NOT EXISTS outbox_event (
	id CHAR(36) PRIMARY KEY,
	aggregate_type VARCHAR(64) NOT NULL,
	aggregate_id CHAR(36) NOT NULL,
	event_type VARCHAR(64) NOT NULL,
	payload JSON NOT NULL,
	occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	published BOOLEAN NOT NULL DEFAULT FALSE,
	correlation_id CHAR(36) NULL,
	causation_id CHAR(36) NULL,
	INDEX idx_outbox_agg_type (aggregate_type),
	INDEX idx_outbox_agg_id (aggregate_id),
	INDEX idx_outbox_event_type (event_type),
	INDEX idx_outbox_published (published),
	INDEX idx_outbox_correlation (correlation_id)
);
INSERT INTO commission_policy (id,name,version,active_from,active_to) VALUES ('00000000-0000-0000-0000-000000000001','default',1,NOW(),NULL) ON DUPLICATE KEY UPDATE name=name;
INSERT INTO commission_rule (id,policy_id,scope,formula,payload) VALUES ('00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001','GLOBAL','PCT', JSON_OBJECT('percentage',12.5)) ON DUPLICATE KEY UPDATE scope=VALUES(scope);

-- Tabla campanas (agregado Campana)
CREATE TABLE IF NOT EXISTS campanas (
	id CHAR(36) PRIMARY KEY,
	nombre VARCHAR(200) NOT NULL,
	descripcion TEXT NOT NULL,
	marca VARCHAR(100) NOT NULL,
	categoria VARCHAR(100) NOT NULL,
	tags JSON NOT NULL,
	fecha_inicio TIMESTAMP NOT NULL,
	fecha_fin TIMESTAMP NOT NULL,
	terminos_comision JSON NOT NULL,
	restriccion_geografica JSON NOT NULL,
	estado VARCHAR(20) NOT NULL DEFAULT 'BORRADOR',
	creada_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	activada_en TIMESTAMP NULL,
	finalizada_en TIMESTAMP NULL,
	version INT NOT NULL DEFAULT 1,
	activa BOOLEAN NOT NULL DEFAULT TRUE,
	INDEX idx_campanas_nombre (nombre),
	INDEX idx_campanas_marca (marca),
	INDEX idx_campanas_estado (estado),
	INDEX idx_campanas_fechas (fecha_inicio, fecha_fin)
);
