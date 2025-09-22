-- Base de datos para microservicio de Conversiones
CREATE DATABASE IF NOT EXISTS conversiones;
USE conversiones;

-- Crear usuario específico
CREATE USER IF NOT EXISTS 'conversiones'@'%' IDENTIFIED BY 'conversiones123';
GRANT ALL PRIVILEGES ON conversiones.* TO 'conversiones'@'%';
FLUSH PRIVILEGES;

-- ==========================================
-- Esquema de Conversiones
-- ==========================================

-- Tabla principal de conversiones
CREATE TABLE IF NOT EXISTS conversiones (
    id VARCHAR(36) PRIMARY KEY,
    afiliado_id VARCHAR(36) NOT NULL,
    campania_id VARCHAR(36) NOT NULL,
    usuario_referido VARCHAR(255),
    email_usuario VARCHAR(255),
    ip_usuario VARCHAR(45),
    user_agent TEXT,
    tipo_conversion ENUM('REGISTRO', 'COMPRA', 'CLICK', 'IMPRESION', 'DESCARGA', 'SUSCRIPCION') NOT NULL,
    valor_conversion DECIMAL(10,2) DEFAULT 0.00,
    moneda VARCHAR(3) DEFAULT 'USD',
    codigo_referido VARCHAR(100), -- Código único del afiliado
    url_origen TEXT,
    url_destino TEXT,
    dispositivo ENUM('MOBILE', 'DESKTOP', 'TABLET', 'UNKNOWN') DEFAULT 'UNKNOWN',
    navegador VARCHAR(100),
    pais VARCHAR(2),
    ciudad VARCHAR(100),
    metadata JSON,
    fecha_conversion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_validacion DATETIME NULL,
    validada BOOLEAN DEFAULT FALSE,
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_campania (campania_id),
    INDEX idx_tipo (tipo_conversion),
    INDEX idx_fecha (fecha_conversion),
    INDEX idx_usuario (usuario_referido),
    INDEX idx_email (email_usuario),
    INDEX idx_codigo (codigo_referido),
    INDEX idx_validada (validada)
);

-- Tabla de sesiones de usuario (tracking)
CREATE TABLE IF NOT EXISTS conversiones_sesiones (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    afiliado_id VARCHAR(36) NOT NULL,
    campania_id VARCHAR(36) NOT NULL,
    ip_usuario VARCHAR(45),
    user_agent TEXT,
    primer_click TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_click TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_clicks INT DEFAULT 1,
    conversion_realizada BOOLEAN DEFAULT FALSE,
    conversion_id VARCHAR(36) NULL,
    dispositivo ENUM('MOBILE', 'DESKTOP', 'TABLET', 'UNKNOWN') DEFAULT 'UNKNOWN',
    pais VARCHAR(2),
    ciudad VARCHAR(100),
    fecha_expiracion TIMESTAMP,
    INDEX idx_session (session_id),
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_campania (campania_id),
    INDEX idx_conversion (conversion_realizada),
    INDEX idx_expiracion (fecha_expiracion),
    FOREIGN KEY (conversion_id) REFERENCES conversiones(id)
);

-- Tabla de eventos de tracking
CREATE TABLE IF NOT EXISTS conversiones_eventos (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    conversion_id VARCHAR(36) NULL,
    tipo_evento ENUM('CLICK', 'VIEW', 'HOVER', 'SCROLL', 'FORM_START', 'FORM_SUBMIT', 'PURCHASE', 'CUSTOM') NOT NULL,
    elemento_objetivo VARCHAR(255), -- CSS selector o descripción del elemento
    valor_evento VARCHAR(500),
    pagina_url TEXT,
    tiempo_en_pagina INT, -- segundos
    timestamp_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    INDEX idx_session (session_id),
    INDEX idx_conversion (conversion_id),
    INDEX idx_tipo (tipo_evento),
    INDEX idx_timestamp (timestamp_evento),
    FOREIGN KEY (conversion_id) REFERENCES conversiones(id)
);

-- Tabla de análisis de conversiones por período
CREATE TABLE IF NOT EXISTS conversiones_analytics (
    id VARCHAR(36) PRIMARY KEY,
    campania_id VARCHAR(36) NOT NULL,
    afiliado_id VARCHAR(36) NOT NULL,
    fecha DATE NOT NULL,
    hora INT NOT NULL, -- 0-23
    clicks_total INT DEFAULT 0,
    impresiones_total INT DEFAULT 0,
    conversiones_total INT DEFAULT 0,
    valor_total_conversiones DECIMAL(12,2) DEFAULT 0.00,
    tasa_conversion DECIMAL(5,4) DEFAULT 0.0000,
    valor_promedio_conversion DECIMAL(10,2) DEFAULT 0.00,
    usuarios_unicos INT DEFAULT 0,
    sesiones_total INT DEFAULT 0,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_campania (campania_id),
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_fecha (fecha),
    INDEX idx_hora (hora),
    UNIQUE KEY unique_analytics (campania_id, afiliado_id, fecha, hora)
);

-- ==========================================
-- Datos de ejemplo
-- ==========================================

-- Insertar conversiones de ejemplo
INSERT IGNORE INTO conversiones (id, afiliado_id, campania_id, usuario_referido, email_usuario, tipo_conversion, valor_conversion, codigo_referido, dispositivo, validada, fecha_validacion) VALUES 
('conv-001', 'af-001', 'camp-001', 'user123', 'user123@email.com', 'COMPRA', 100.00, 'REF001', 'DESKTOP', TRUE, '2024-12-01 10:15:00'),
('conv-002', 'af-001', 'camp-001', 'user456', 'user456@email.com', 'COMPRA', 150.00, 'REF001', 'MOBILE', TRUE, '2024-12-01 11:45:00'),
('conv-003', 'af-002', 'camp-002', 'user789', 'user789@email.com', 'COMPRA', 500.00, 'REF002', 'DESKTOP', TRUE, '2024-12-01 16:00:00'),
('conv-004', 'af-003', 'camp-001', 'user101', 'user101@email.com', 'REGISTRO', 0.00, 'REF003', 'MOBILE', TRUE, '2024-12-01 09:30:00'),
('conv-005', 'af-001', 'camp-001', 'user202', 'user202@email.com', 'CLICK', 0.00, 'REF001', 'TABLET', TRUE, '2024-11-30 14:20:00');

-- Insertar sesiones de ejemplo
INSERT IGNORE INTO conversiones_sesiones (id, session_id, afiliado_id, campania_id, primer_click, total_clicks, conversion_realizada, conversion_id, dispositivo) VALUES 
('ses-001', 'sess_abc123', 'af-001', 'camp-001', '2024-12-01 10:00:00', 3, TRUE, 'conv-001', 'DESKTOP'),
('ses-002', 'sess_def456', 'af-001', 'camp-001', '2024-12-01 11:30:00', 2, TRUE, 'conv-002', 'MOBILE'),
('ses-003', 'sess_ghi789', 'af-002', 'camp-002', '2024-12-01 15:45:00', 5, TRUE, 'conv-003', 'DESKTOP'),
('ses-004', 'sess_jkl012', 'af-003', 'camp-001', '2024-12-01 09:15:00', 1, TRUE, 'conv-004', 'MOBILE'),
('ses-005', 'sess_mno345', 'af-001', 'camp-001', '2024-12-02 08:00:00', 1, FALSE, NULL, 'DESKTOP');

-- Insertar eventos de ejemplo
INSERT IGNORE INTO conversiones_eventos (id, session_id, conversion_id, tipo_evento, elemento_objetivo, pagina_url, timestamp_evento) VALUES 
('evt-001', 'sess_abc123', NULL, 'CLICK', 'banner-promo', 'https://store.com/promo', '2024-12-01 10:00:00'),
('evt-002', 'sess_abc123', NULL, 'VIEW', 'product-page', 'https://store.com/product/123', '2024-12-01 10:05:00'),
('evt-003', 'sess_abc123', 'conv-001', 'PURCHASE', 'buy-button', 'https://store.com/checkout', '2024-12-01 10:15:00'),
('evt-004', 'sess_def456', NULL, 'CLICK', 'mobile-banner', 'https://store.com/mobile-promo', '2024-12-01 11:30:00'),
('evt-005', 'sess_def456', 'conv-002', 'PURCHASE', 'mobile-buy', 'https://store.com/mobile-checkout', '2024-12-01 11:45:00');

-- Insertar analytics de ejemplo
INSERT IGNORE INTO conversiones_analytics (id, campania_id, afiliado_id, fecha, hora, clicks_total, conversiones_total, valor_total_conversiones, tasa_conversion, usuarios_unicos) VALUES 
('ana-001', 'camp-001', 'af-001', '2024-12-01', 10, 25, 2, 250.00, 0.0800, 15),
('ana-002', 'camp-001', 'af-001', '2024-12-01', 11, 18, 1, 150.00, 0.0556, 12),
('ana-003', 'camp-002', 'af-002', '2024-12-01', 16, 30, 1, 500.00, 0.0333, 20),
('ana-004', 'camp-001', 'af-003', '2024-12-01', 9, 10, 1, 0.00, 0.1000, 8);