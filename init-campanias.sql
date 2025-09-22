-- Base de datos para microservicio de campanias
CREATE DATABASE IF NOT EXISTS campanias;
USE campanias;

-- Crear usuario específico
CREATE USER IF NOT EXISTS 'campanias'@'%' IDENTIFIED BY 'campanias123';
GRANT ALL PRIVILEGES ON campanias.* TO 'campanias'@'%';
FLUSH PRIVILEGES;

-- ==========================================
-- Esquema de campanias
-- ==========================================

-- Tabla principal de campanias
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
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_estado (estado),
    INDEX idx_tipo (tipo_campania),
    INDEX idx_fechas (fecha_inicio, fecha_fin)
);

-- Tabla de afiliados asignados a campanias
CREATE TABLE IF NOT EXISTS campanias_afiliados (
    id VARCHAR(36) PRIMARY KEY,
    campania_id VARCHAR(36) NOT NULL,
    afiliado_id VARCHAR(36) NOT NULL,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comision_pct DECIMAL(5,2),
    estado ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO',
    INDEX idx_campania (campania_id),
    INDEX idx_afiliado (afiliado_id),
    INDEX idx_estado (estado),
    FOREIGN KEY (campania_id) REFERENCES campanias(id) ON DELETE CASCADE
);

-- Tabla de métricas de campaña
CREATE TABLE IF NOT EXISTS campanias_metricas (
    id VARCHAR(36) PRIMARY KEY,
    campania_id VARCHAR(36) NOT NULL,
    fecha DATE NOT NULL,
    conversiones_total INT DEFAULT 0,
    comisiones_generadas DECIMAL(10,2) DEFAULT 0.00,
    ingresos_generados DECIMAL(10,2) DEFAULT 0.00,
    clicks_total INT DEFAULT 0,
    impresiones_total INT DEFAULT 0,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_campania (campania_id),
    INDEX idx_fecha (fecha),
    FOREIGN KEY (campania_id) REFERENCES campanias(id) ON DELETE CASCADE,
    UNIQUE KEY unique_campania_fecha (campania_id, fecha)
);

-- ==========================================
-- Datos de ejemplo
-- ==========================================

-- Insertar campanias de ejemplo
INSERT IGNORE INTO campanias (id, nombre, descripcion, presupuesto, meta_conversiones, tipo_campania, estado) VALUES 
('camp-001', 'Campaña Navideña 2024', 'Promoción especial para temporada navideña con descuentos hasta 50%', 50000.00, 1000, 'PROMOCIONAL', 'ACTIVA'),
('camp-002', 'Lanzamiento Producto Tech', 'Campaña para nuevo smartphone con tecnología AI', 75000.00, 500, 'CONVERSION', 'CREADA'),
('camp-003', 'Black Friday 2024', 'Mega ofertas de Black Friday para todos los productos', 100000.00, 2000, 'PROMOCIONAL', 'CREADA');

-- Insertar métricas de ejemplo
INSERT IGNORE INTO campanias_metricas (id, campania_id, fecha, conversiones_total, comisiones_generadas) VALUES 
('met-001', 'camp-001', '2024-12-01', 25, 1250.00),
('met-002', 'camp-001', '2024-12-02', 30, 1500.00),
('met-003', 'camp-002', '2024-12-01', 10, 750.00);