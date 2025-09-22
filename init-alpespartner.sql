-- Crear base de datos AlpesPartner
CREATE DATABASE IF NOT EXISTS alpespartner;
USE alpespartner;

-- Crear usuario específico para AlpesPartner
CREATE USER IF NOT EXISTS 'alpespartner'@'%' IDENTIFIED BY 'alpespartner123';
GRANT ALL PRIVILEGES ON alpespartner.* TO 'alpespartner'@'%';
FLUSH PRIVILEGES;

-- ==========================================
-- Tablas de campanias
-- ==========================================

-- Tabla de campanias
CREATE TABLE IF NOT EXISTS campanias (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATETIME,
    fecha_fin DATETIME,
    estado ENUM('CREADA', 'ACTIVA', 'PAUSADA', 'FINALIZADA') DEFAULT 'CREADA',
    tipo_campania ENUM('CONVERSION', 'BRANDING', 'PROMOCIONAL') DEFAULT 'CONVERSION',
    presupuesto DECIMAL(10,2),
    meta_conversiones INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de afiliados en campanias
CREATE TABLE IF NOT EXISTS campanias_afiliados (
    id VARCHAR(36) PRIMARY KEY,
    campania_id VARCHAR(36) NOT NULL,
    afiliado_id VARCHAR(36) NOT NULL,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comision_pct DECIMAL(5,2),
    INDEX idx_campania (campania_id),
    INDEX idx_afiliado (afiliado_id)
);

-- ==========================================
-- Tablas de Afiliados
-- ==========================================

-- Tabla de afiliados
CREATE TABLE IF NOT EXISTS afiliados (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    tipo_afiliado ENUM('INDIVIDUAL', 'EMPRESA', 'INFLUENCER') DEFAULT 'INDIVIDUAL',
    estado ENUM('ACTIVO', 'INACTIVO', 'SUSPENDIDO') DEFAULT 'ACTIVO',
    comision_base DECIMAL(5,2) DEFAULT 5.00,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==========================================
-- Tablas de Comisiones
-- ==========================================

-- Tabla de comisiones
CREATE TABLE IF NOT EXISTS comisiones (
    id VARCHAR(36) PRIMARY KEY,
    afiliado_id VARCHAR(36) NOT NULL,
    campania_id VARCHAR(36) NOT NULL,
    conversion_id VARCHAR(36),
    monto_base DECIMAL(10,2) NOT NULL,
    porcentaje_comision DECIMAL(5,2) NOT NULL,
    monto_comision DECIMAL(10,2) NOT NULL,
    estado ENUM('PENDIENTE', 'CALCULADA', 'PAGADA', 'CANCELADA') DEFAULT 'PENDIENTE',
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_pago DATETIME NULL,
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_campania (campania_id),
    INDEX idx_conversion (conversion_id)
);

-- ==========================================
-- Tablas de Conversiones
-- ==========================================

-- Tabla de conversiones
CREATE TABLE IF NOT EXISTS conversiones (
    id VARCHAR(36) PRIMARY KEY,
    afiliado_id VARCHAR(36) NOT NULL,
    campania_id VARCHAR(36) NOT NULL,
    usuario_referido VARCHAR(255),
    tipo_conversion ENUM('REGISTRO', 'COMPRA', 'CLICK', 'IMPRESION') NOT NULL,
    valor_conversion DECIMAL(10,2),
    metadata JSON,
    fecha_conversion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_campania (campania_id),
    INDEX idx_fecha (fecha_conversion)
);

-- ==========================================
-- Tablas de Notificaciones
-- ==========================================

-- Tabla de notificaciones
CREATE TABLE IF NOT EXISTS notificaciones (
    id VARCHAR(36) PRIMARY KEY,
    destinatario VARCHAR(255) NOT NULL,
    tipo_notificacion ENUM('EMAIL', 'SMS', 'PUSH', 'WEBHOOK') NOT NULL,
    asunto VARCHAR(255),
    mensaje TEXT NOT NULL,
    estado ENUM('PENDIENTE', 'ENVIADA', 'FALLIDA', 'LEIDA') DEFAULT 'PENDIENTE',
    intentos INT DEFAULT 0,
    fecha_envio DATETIME NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    INDEX idx_destinatario (destinatario),
    INDEX idx_estado (estado),
    INDEX idx_fecha (fecha_creacion)
);

-- ==========================================
-- Tablas de Sagas
-- ==========================================

-- Tabla de sagas
CREATE TABLE IF NOT EXISTS sagas (
    id VARCHAR(36) PRIMARY KEY,
    tipo_saga VARCHAR(100) NOT NULL,
    estado ENUM('INICIADA', 'EN_PROGRESO', 'COMPLETADA', 'FALLIDA', 'COMPENSANDO', 'COMPENSADA') DEFAULT 'INICIADA',
    contexto JSON,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME NULL,
    error_mensaje TEXT NULL,
    INDEX idx_tipo (tipo_saga),
    INDEX idx_estado (estado)
);

-- Tabla de pasos de saga
CREATE TABLE IF NOT EXISTS saga_pasos (
    id VARCHAR(36) PRIMARY KEY,
    saga_id VARCHAR(36) NOT NULL,
    paso_numero INT NOT NULL,
    servicio VARCHAR(100) NOT NULL,
    comando VARCHAR(100) NOT NULL,
    estado ENUM('PENDIENTE', 'EJECUTANDO', 'COMPLETADO', 'FALLIDO', 'COMPENSADO') DEFAULT 'PENDIENTE',
    request_data JSON,
    response_data JSON,
    error_mensaje TEXT NULL,
    fecha_inicio DATETIME NULL,
    fecha_fin DATETIME NULL,
    INDEX idx_saga (saga_id),
    INDEX idx_estado (estado),
    FOREIGN KEY (saga_id) REFERENCES sagas(id) ON DELETE CASCADE
);

-- ==========================================
-- Datos de ejemplo
-- ==========================================

-- Insertar afiliado de ejemplo
INSERT IGNORE INTO afiliados (id, nombre, email, telefono, tipo_afiliado, comision_base) VALUES 
('af-001', 'Juan Pérez', 'juan.perez@email.com', '+57300123456', 'INDIVIDUAL', 7.50),
('af-002', 'Tech Solutions SAS', 'contact@techsolutions.com', '+57301987654', 'EMPRESA', 10.00),
('af-003', 'María Influencer', 'maria@socialnet.com', '+57302456789', 'INFLUENCER', 12.00);

-- Insertar campaña de ejemplo
INSERT IGNORE INTO campanias (id, nombre, descripcion, presupuesto, meta_conversiones, tipo_campania) VALUES 
('camp-001', 'Campaña Navideña 2024', 'Promoción especial para temporada navideña', 50000.00, 1000, 'PROMOCIONAL'),
('camp-002', 'Lanzamiento Producto', 'Campaña para nuevo producto tech', 75000.00, 500, 'CONVERSION');

-- Relacionar afiliados con campanias
INSERT IGNORE INTO campanias_afiliados (id, campania_id, afiliado_id, comision_pct) VALUES 
('ca-001', 'camp-001', 'af-001', 7.50),
('ca-002', 'camp-001', 'af-002', 10.00),
('ca-003', 'camp-002', 'af-003', 12.00);