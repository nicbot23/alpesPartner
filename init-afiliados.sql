-- Base de datos para microservicio de Afiliados
CREATE DATABASE IF NOT EXISTS afiliados;
USE afiliados;

-- Crear usuario específico
CREATE USER IF NOT EXISTS 'afiliados'@'%' IDENTIFIED BY 'afiliados123';
GRANT ALL PRIVILEGES ON afiliados.* TO 'afiliados'@'%';
FLUSH PRIVILEGES;

-- ==========================================
-- Esquema de Afiliados
-- ==========================================

-- Tabla principal de afiliados
CREATE TABLE IF NOT EXISTS afiliados (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    tipo_afiliado ENUM('INDIVIDUAL', 'EMPRESA', 'INFLUENCER') DEFAULT 'INDIVIDUAL',
    estado ENUM('ACTIVO', 'INACTIVO', 'SUSPENDIDO', 'PENDIENTE_APROBACION') DEFAULT 'PENDIENTE_APROBACION',
    comision_base DECIMAL(5,2) DEFAULT 5.00,
    nivel_afiliado ENUM('BRONCE', 'PLATA', 'ORO', 'PLATINO') DEFAULT 'BRONCE',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_aprobacion DATETIME NULL,
    fecha_ultima_actividad DATETIME NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_estado (estado),
    INDEX idx_tipo (tipo_afiliado),
    INDEX idx_nivel (nivel_afiliado)
);

-- Tabla de información bancaria de afiliados
CREATE TABLE IF NOT EXISTS afiliados_pago (
    id VARCHAR(36) PRIMARY KEY,
    afiliado_id VARCHAR(36) NOT NULL,
    tipo_cuenta ENUM('AHORRO', 'CORRIENTE', 'PAYPAL', 'TRANSFERWISE') NOT NULL,
    banco VARCHAR(100),
    numero_cuenta VARCHAR(50),
    titular_cuenta VARCHAR(255),
    email_pago VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_afiliado (afiliado_id),
    FOREIGN KEY (afiliado_id) REFERENCES afiliados(id) ON DELETE CASCADE
);

-- Tabla de documentos de afiliados
CREATE TABLE IF NOT EXISTS afiliados_documentos (
    id VARCHAR(36) PRIMARY KEY,
    afiliado_id VARCHAR(36) NOT NULL,
    tipo_documento ENUM('CEDULA', 'PASAPORTE', 'RUT', 'TAX_ID') NOT NULL,
    numero_documento VARCHAR(50) NOT NULL,
    pais_expedicion VARCHAR(2),
    fecha_expedicion DATE,
    fecha_vencimiento DATE,
    verificado BOOLEAN DEFAULT FALSE,
    fecha_verificacion DATETIME NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_numero (numero_documento),
    FOREIGN KEY (afiliado_id) REFERENCES afiliados(id) ON DELETE CASCADE
);

-- Tabla de estadísticas de afiliados
CREATE TABLE IF NOT EXISTS afiliados_estadisticas (
    id VARCHAR(36) PRIMARY KEY,
    afiliado_id VARCHAR(36) NOT NULL,
    mes CHAR(7) NOT NULL, -- YYYY-MM format
    conversiones_total INT DEFAULT 0,
    comisiones_ganadas DECIMAL(10,2) DEFAULT 0.00,
    clicks_generados INT DEFAULT 0,
    ventas_generadas DECIMAL(12,2) DEFAULT 0.00,
    ranking_mensual INT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_mes (mes),
    FOREIGN KEY (afiliado_id) REFERENCES afiliados(id) ON DELETE CASCADE,
    UNIQUE KEY unique_afiliado_mes (afiliado_id, mes)
);

-- ==========================================
-- Datos de ejemplo
-- ==========================================

-- Insertar afiliados de ejemplo
INSERT IGNORE INTO afiliados (id, nombre, email, telefono, tipo_afiliado, estado, comision_base, nivel_afiliado, fecha_aprobacion) VALUES 
('af-001', 'Juan Pérez Martínez', 'juan.perez@email.com', '+57300123456', 'INDIVIDUAL', 'ACTIVO', 7.50, 'PLATA', '2024-11-01 10:00:00'),
('af-002', 'Tech Solutions SAS', 'contact@techsolutions.com', '+57301987654', 'EMPRESA', 'ACTIVO', 10.00, 'ORO', '2024-10-15 14:30:00'),
('af-003', 'María Influencer', 'maria@socialnet.com', '+57302456789', 'INFLUENCER', 'ACTIVO', 12.00, 'PLATINO', '2024-09-20 09:15:00'),
('af-004', 'Carlos Rodríguez', 'carlos.r@gmail.com', '+57303555666', 'INDIVIDUAL', 'PENDIENTE_APROBACION', 5.00, 'BRONCE', NULL);

-- Insertar información de pago
INSERT IGNORE INTO afiliados_pago (id, afiliado_id, tipo_cuenta, banco, numero_cuenta, titular_cuenta) VALUES 
('pago-001', 'af-001', 'AHORRO', 'Bancolombia', '*****6789', 'Juan Pérez Martínez'),
('pago-002', 'af-002', 'CORRIENTE', 'Banco de Bogotá', '*****4321', 'Tech Solutions SAS'),
('pago-003', 'af-003', 'PAYPAL', NULL, NULL, 'maria@socialnet.com');

-- Insertar documentos
INSERT IGNORE INTO afiliados_documentos (id, afiliado_id, tipo_documento, numero_documento, pais_expedicion, verificado, fecha_verificacion) VALUES 
('doc-001', 'af-001', 'CEDULA', '12345678', 'CO', TRUE, '2024-11-02 11:00:00'),
('doc-002', 'af-002', 'RUT', '900123456-7', 'CO', TRUE, '2024-10-16 15:00:00'),
('doc-003', 'af-003', 'CEDULA', '87654321', 'CO', TRUE, '2024-09-21 10:00:00');

-- Insertar estadísticas de ejemplo
INSERT IGNORE INTO afiliados_estadisticas (id, afiliado_id, mes, conversiones_total, comisiones_ganadas, clicks_generados) VALUES 
('est-001', 'af-001', '2024-11', 25, 1875.00, 150),
('est-002', 'af-002', '2024-11', 40, 4000.00, 200),
('est-003', 'af-003', '2024-11', 60, 7200.00, 300),
('est-004', 'af-001', '2024-10', 30, 2250.00, 180);