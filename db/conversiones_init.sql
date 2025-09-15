-- DDL para microservicio Conversiones (Base de datos separada)
-- Esquema descentralizado para almacenamiento independiente

-- Tabla principal de conversiones
CREATE TABLE IF NOT EXISTS conversions (
    id CHAR(36) PRIMARY KEY,
    conversion_type VARCHAR(20) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    
    -- Datos afiliado
    affiliate_id VARCHAR(36) NOT NULL,
    affiliate_type VARCHAR(20) NOT NULL,
    tier_level VARCHAR(20) NOT NULL DEFAULT 'STANDARD',
    
    -- Datos campaña (desnormalizado para descentralización)
    campaign_id VARCHAR(36) NOT NULL,
    campaign_name VARCHAR(200) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    
    -- Datos transacción
    gross_amount DECIMAL(12,2) NOT NULL,
    currency CHAR(3) NOT NULL,
    transaction_id VARCHAR(100) NULL UNIQUE,
    payment_method VARCHAR(50) NULL,
    
    -- Metadatos (JSON para flexibilidad)
    metadatos JSON NULL,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP NULL,
    rejected_at TIMESTAMP NULL,
    cancelled_at TIMESTAMP NULL,
    
    -- Validación y atribución
    validation_score DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    attribution_model VARCHAR(20) NOT NULL DEFAULT 'LAST_CLICK',
    
    -- Auditoría
    version INT NOT NULL DEFAULT 1,
    
    -- Índices para performance
    INDEX idx_conversions_affiliate (affiliate_id),
    INDEX idx_conversions_campaign (campaign_id),
    INDEX idx_conversions_estado (estado),
    INDEX idx_conversions_created (created_at),
    INDEX idx_conversions_confirmed (confirmed_at),
    INDEX idx_conversions_tipo (conversion_type),
    INDEX idx_conversions_brand (brand),
    INDEX idx_conversions_transaction (transaction_id)
);

-- Outbox events descentralizado para Conversiones
CREATE TABLE IF NOT EXISTS conversion_outbox_events (
    id CHAR(36) PRIMARY KEY,
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id CHAR(36) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSON NOT NULL,
    occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    published BOOLEAN NOT NULL DEFAULT FALSE,
    correlation_id CHAR(36) NULL,
    causation_id CHAR(36) NULL,
    
    -- Campos de retry para descentralización
    attempts INT NOT NULL DEFAULT 0,
    last_error TEXT NULL,
    next_retry_at TIMESTAMP NULL,
    dead_letter BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Índices optimizados para outbox pattern
    INDEX idx_conv_outbox_agg_type (aggregate_type),
    INDEX idx_conv_outbox_agg_id (aggregate_id),
    INDEX idx_conv_outbox_event_type (event_type),
    INDEX idx_conv_outbox_published (published),
    INDEX idx_conv_outbox_correlation (correlation_id),
    INDEX idx_conv_outbox_retry (next_retry_at),
    INDEX idx_conv_outbox_occurred (occurred_at)
);

-- Datos de ejemplo para desarrollo (opcional)
INSERT INTO conversions (
    id, conversion_type, affiliate_id, affiliate_type, tier_level,
    campaign_id, campaign_name, brand, gross_amount, currency,
    estado, validation_score
) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440001',
    'PURCHASE',
    'aff-001',
    'INFLUENCER',
    'PREMIUM',
    'camp-001',
    'Black Friday 2025',
    'ALPES',
    299.99,
    'USD',
    'CONFIRMADA',
    0.95
),
(
    '550e8400-e29b-41d4-a716-446655440002', 
    'CLICK',
    'aff-002',
    'BRAND',
    'STANDARD',
    'camp-002',
    'Summer Campaign',
    'ALPES',
    0.00,
    'USD',
    'PENDIENTE',
    0.60
) ON DUPLICATE KEY UPDATE id=id;