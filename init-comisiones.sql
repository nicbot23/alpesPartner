-- Base de datos para microservicio de Comisiones
CREATE DATABASE IF NOT EXISTS comisiones;
USE comisiones;

-- Crear usuario específico
CREATE USER IF NOT EXISTS 'comisiones'@'%' IDENTIFIED BY 'comisiones123';
GRANT ALL PRIVILEGES ON comisiones.* TO 'comisiones'@'%';
FLUSH PRIVILEGES;

-- ==========================================
-- Esquema de Comisiones
-- ==========================================

-- Tabla principal de comisiones
CREATE TABLE IF NOT EXISTS comisiones (
    id VARCHAR(36) PRIMARY KEY,
    afiliado_id VARCHAR(36) NOT NULL,
    campania_id VARCHAR(36) NOT NULL,
    conversion_id VARCHAR(36),
    referencia_externa VARCHAR(100), -- ID de la venta/transacción original
    monto_base DECIMAL(10,2) NOT NULL,
    porcentaje_comision DECIMAL(5,2) NOT NULL,
    monto_comision DECIMAL(10,2) NOT NULL,
    tipo_comision ENUM('CONVERSION', 'CLICK', 'IMPRESION', 'REGISTRO', 'BONUS') DEFAULT 'CONVERSION',
    estado ENUM('PENDIENTE', 'CALCULADA', 'APROBADA', 'PAGADA', 'CANCELADA', 'RECHAZADA') DEFAULT 'PENDIENTE',
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_calculo DATETIME NULL,
    fecha_aprobacion DATETIME NULL,
    fecha_pago DATETIME NULL,
    observaciones TEXT NULL,
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_campania (campania_id),
    INDEX idx_conversion (conversion_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha_generacion (fecha_generacion),
    INDEX idx_referencia (referencia_externa)
);

-- Tabla de configuración de comisiones por campaña
CREATE TABLE IF NOT EXISTS comisiones_config (
    id VARCHAR(36) PRIMARY KEY,
    campania_id VARCHAR(36) NOT NULL,
    afiliado_id VARCHAR(36) NULL, -- NULL significa configuración por defecto para la campaña
    tipo_comision ENUM('CONVERSION', 'CLICK', 'IMPRESION', 'REGISTRO') NOT NULL,
    porcentaje_base DECIMAL(5,2) NOT NULL,
    monto_minimo DECIMAL(10,2) DEFAULT 0.00,
    monto_maximo DECIMAL(10,2) NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_inicio DATE,
    fecha_fin DATE NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_campania (campania_id),
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_tipo (tipo_comision),
    INDEX idx_activo (activo)
);

-- Tabla de pagos de comisiones
CREATE TABLE IF NOT EXISTS comisiones_pagos (
    id VARCHAR(36) PRIMARY KEY,
    afiliado_id VARCHAR(36) NOT NULL,
    periodo_inicio DATE NOT NULL,
    periodo_fin DATE NOT NULL,
    total_comisiones DECIMAL(10,2) NOT NULL,
    total_deducciones DECIMAL(10,2) DEFAULT 0.00,
    total_neto DECIMAL(10,2) NOT NULL,
    estado ENUM('PREPARANDO', 'LISTO_PAGO', 'PAGADO', 'FALLIDO') DEFAULT 'PREPARANDO',
    metodo_pago ENUM('TRANSFERENCIA', 'PAYPAL', 'CHEQUE', 'CRIPTO') NOT NULL,
    referencia_pago VARCHAR(100) NULL,
    fecha_procesamiento DATETIME NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT NULL,
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_estado (estado),
    INDEX idx_periodo (periodo_inicio, periodo_fin),
    INDEX idx_fecha_procesamiento (fecha_procesamiento)
);

-- Tabla de comisiones incluidas en cada pago
CREATE TABLE IF NOT EXISTS comisiones_pago_detalle (
    id VARCHAR(36) PRIMARY KEY,
    pago_id VARCHAR(36) NOT NULL,
    comision_id VARCHAR(36) NOT NULL,
    monto_incluido DECIMAL(10,2) NOT NULL,
    fecha_inclusion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pago (pago_id),
    INDEX idx_comision (comision_id),
    FOREIGN KEY (pago_id) REFERENCES comisiones_pagos(id) ON DELETE CASCADE,
    FOREIGN KEY (comision_id) REFERENCES comisiones(id),
    UNIQUE KEY unique_pago_comision (pago_id, comision_id)
);

-- ==========================================
-- Datos de ejemplo
-- ==========================================

-- Insertar configuraciones de comisión
INSERT IGNORE INTO comisiones_config (id, campania_id, tipo_comision, porcentaje_base, monto_minimo, fecha_inicio) VALUES 
('cfg-001', 'camp-001', 'CONVERSION', 7.50, 5.00, '2024-11-01'),
('cfg-002', 'camp-001', 'CLICK', 0.50, 0.10, '2024-11-01'),
('cfg-003', 'camp-002', 'CONVERSION', 10.00, 10.00, '2024-11-01'),
('cfg-004', 'camp-002', 'REGISTRO', 2.00, 1.00, '2024-11-01');

-- Insertar comisiones de ejemplo
INSERT IGNORE INTO comisiones (id, afiliado_id, campania_id, conversion_id, referencia_externa, monto_base, porcentaje_comision, monto_comision, tipo_comision, estado, fecha_calculo) VALUES 
('com-001', 'af-001', 'camp-001', 'conv-001', 'ORDER-123456', 100.00, 7.50, 7.50, 'CONVERSION', 'CALCULADA', '2024-12-01 10:00:00'),
('com-002', 'af-001', 'camp-001', 'conv-002', 'ORDER-123457', 150.00, 7.50, 11.25, 'CONVERSION', 'APROBADA', '2024-12-01 11:30:00'),
('com-003', 'af-002', 'camp-002', 'conv-003', 'ORDER-789012', 500.00, 10.00, 50.00, 'CONVERSION', 'CALCULADA', '2024-12-01 15:45:00'),
('com-004', 'af-003', 'camp-001', NULL, 'CLICK-001', 0.00, 0.50, 0.50, 'CLICK', 'PAGADA', '2024-11-30 09:15:00');

-- Insertar un pago de ejemplo
INSERT IGNORE INTO comisiones_pagos (id, afiliado_id, periodo_inicio, periodo_fin, total_comisiones, total_neto, estado, metodo_pago, fecha_procesamiento) VALUES 
('pago-001', 'af-001', '2024-11-01', '2024-11-30', 45.75, 45.75, 'PAGADO', 'TRANSFERENCIA', '2024-12-01 16:00:00');

-- Insertar detalle del pago
INSERT IGNORE INTO comisiones_pago_detalle (id, pago_id, comision_id, monto_incluido) VALUES 
('det-001', 'pago-001', 'com-001', 7.50),
('det-002', 'pago-001', 'com-002', 11.25);