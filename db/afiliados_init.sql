-- Script de inicialización para la base de datos de Afiliados
-- Microservicio descentralizado con outbox pattern

CREATE DATABASE IF NOT EXISTS alpes_afiliados;
USE alpes_afiliados;

-- Crear tabla principal de afiliados
CREATE TABLE IF NOT EXISTS afiliados (
    id VARCHAR(36) PRIMARY KEY,
    numero_documento VARCHAR(20) NOT NULL UNIQUE,
    tipo_documento ENUM('CC', 'CE', 'PP', 'TI') NOT NULL DEFAULT 'CC',
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    fecha_nacimiento DATE,
    tipo_afiliado ENUM('INDIVIDUAL', 'EMPRESA') NOT NULL DEFAULT 'INDIVIDUAL',
    estado ENUM('ACTIVO', 'INACTIVO', 'SUSPENDIDO', 'BLOQUEADO', 'PENDIENTE_VALIDACION') NOT NULL DEFAULT 'PENDIENTE_VALIDACION',
    
    -- Datos bancarios
    banco VARCHAR(100),
    tipo_cuenta ENUM('AHORROS', 'CORRIENTE') DEFAULT 'AHORROS',
    numero_cuenta VARCHAR(50),
    
    -- Configuración comisiones
    comision_base DECIMAL(5,2) DEFAULT 5.00,
    comision_adicional DECIMAL(5,2) DEFAULT 0.00,
    comision_activa BOOLEAN DEFAULT TRUE,
    
    -- Referidos
    afiliado_referente_id VARCHAR(36),
    codigo_referencia VARCHAR(20) UNIQUE,
    total_referidos INT DEFAULT 0,
    
    -- Metadatos
    fecha_afiliacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fecha_validacion DATETIME,
    validado_por VARCHAR(100),
    observaciones TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    version INT NOT NULL DEFAULT 1,
    
    -- Constraints
    CONSTRAINT fk_afiliado_referente FOREIGN KEY (afiliado_referente_id) REFERENCES afiliados(id),
    INDEX idx_documento (numero_documento),
    INDEX idx_email (email),
    INDEX idx_estado (estado),
    INDEX idx_tipo (tipo_afiliado),
    INDEX idx_referente (afiliado_referente_id),
    INDEX idx_codigo_ref (codigo_referencia),
    INDEX idx_fecha_afiliacion (fecha_afiliacion)
);

-- Crear tabla de referencias de afiliados
CREATE TABLE IF NOT EXISTS referencias_afiliados (
    id VARCHAR(36) PRIMARY KEY,
    afiliado_id VARCHAR(36) NOT NULL,
    nombre_referencia VARCHAR(100) NOT NULL,
    telefono_referencia VARCHAR(20) NOT NULL,
    email_referencia VARCHAR(150),
    relacion VARCHAR(50) NOT NULL,
    verificada BOOLEAN DEFAULT FALSE,
    fecha_verificacion DATETIME,
    observaciones TEXT,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    
    CONSTRAINT fk_referencia_afiliado FOREIGN KEY (afiliado_id) REFERENCES afiliados(id) ON DELETE CASCADE,
    INDEX idx_afiliado_ref (afiliado_id),
    INDEX idx_verificada (verificada)
);

-- Crear tabla outbox para eventos descentralizados de afiliados
CREATE TABLE IF NOT EXISTS outbox_afiliados_events (
    id VARCHAR(36) PRIMARY KEY,
    aggregate_id VARCHAR(36) NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL DEFAULT 'Afiliado',
    event_type VARCHAR(100) NOT NULL,
    event_data JSON NOT NULL,
    correlation_id VARCHAR(36),
    causation_id VARCHAR(36),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME NULL,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    retry_count INT NOT NULL DEFAULT 0,
    error_message TEXT NULL,
    version INT NOT NULL DEFAULT 1,
    
    INDEX idx_aggregate_id (aggregate_id),
    INDEX idx_event_type (event_type),
    INDEX idx_processed (processed),
    INDEX idx_created_at (created_at),
    INDEX idx_correlation_id (correlation_id),
    INDEX idx_causation_id (causation_id)
);

-- Insertar datos de prueba para afiliados
INSERT INTO afiliados (
    id, numero_documento, tipo_documento, nombres, apellidos, email, telefono,
    fecha_nacimiento, tipo_afiliado, estado, banco, tipo_cuenta, numero_cuenta,
    comision_base, comision_adicional, codigo_referencia, fecha_afiliacion
) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440001',
    '12345678',
    'CC',
    'Juan Carlos',
    'Pérez Gómez',
    'juan.perez@example.com',
    '+57 300 123 4567',
    '1985-03-15',
    'INDIVIDUAL',
    'ACTIVO',
    'Banco de Bogotá',
    'AHORROS',
    '1234567890',
    5.50,
    1.00,
    'REF001',
    '2024-01-15 10:30:00'
),
(
    '550e8400-e29b-41d4-a716-446655440002',
    '87654321',
    'CC',
    'María Elena',
    'González López',
    'maria.gonzalez@example.com',
    '+57 301 234 5678',
    '1990-07-22',
    'INDIVIDUAL',
    'ACTIVO',
    'Bancolombia',
    'CORRIENTE',
    '0987654321',
    6.00,
    0.50,
    'REF002',
    '2024-01-20 14:45:00'
),
(
    '550e8400-e29b-41d4-a716-446655440003',
    '11223344',
    'CC',
    'Pedro Antonio',
    'Ramírez Silva',
    'pedro.ramirez@example.com',
    '+57 302 345 6789',
    '1982-11-08',
    'INDIVIDUAL',
    'PENDIENTE_VALIDACION',
    'Banco Popular',
    'AHORROS',
    '1122334455',
    5.00,
    0.00,
    'REF003',
    '2024-02-01 09:15:00'
),
(
    '550e8400-e29b-41d4-a716-446655440004',
    '99887766',
    'CC',
    'Ana Sofía',
    'Torres Medina',
    'ana.torres@example.com',
    '+57 303 456 7890',
    '1988-05-12',
    'INDIVIDUAL',
    'SUSPENDIDO',
    'Banco Davivienda',
    'AHORROS',
    '9988776655',
    5.25,
    0.75,
    'REF004',
    '2024-01-10 16:20:00'
),
(
    '550e8400-e29b-41d4-a716-446655440005',
    '55443322',
    'CC',
    'Luis Fernando',
    'Vargas Castro',
    'luis.vargas@example.com',
    '+57 304 567 8901',
    '1975-12-03',
    'INDIVIDUAL',
    'ACTIVO',
    'Banco Agrario',
    'CORRIENTE',
    '5544332211',
    7.00,
    2.00,
    'REF005',
    '2024-01-25 11:00:00'
);

-- Establecer relación de referidos
UPDATE afiliados SET afiliado_referente_id = '550e8400-e29b-41d4-a716-446655440001', total_referidos = 1 
WHERE id = '550e8400-e29b-41d4-a716-446655440002';

UPDATE afiliados SET total_referidos = 2 
WHERE id = '550e8400-e29b-41d4-a716-446655440001';

-- Insertar referencias de prueba
INSERT INTO referencias_afiliados (
    id, afiliado_id, nombre_referencia, telefono_referencia, email_referencia, 
    relacion, verificada, fecha_verificacion
) VALUES 
(
    '660e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440001',
    'Carlos Mendoza',
    '+57 310 111 2222',
    'carlos.mendoza@example.com',
    'Amigo',
    TRUE,
    '2024-01-16 12:00:00'
),
(
    '660e8400-e29b-41d4-a716-446655440002',
    '550e8400-e29b-41d4-a716-446655440001',
    'Sofia Herrera',
    '+57 311 222 3333',
    'sofia.herrera@example.com',
    'Familiar',
    TRUE,
    '2024-01-17 15:30:00'
),
(
    '660e8400-e29b-41d4-a716-446655440003',
    '550e8400-e29b-41d4-a716-446655440002',
    'Roberto Jiménez',
    '+57 312 333 4444',
    'roberto.jimenez@example.com',
    'Compañero trabajo',
    FALSE,
    NULL
);

-- Insertar algunos eventos de ejemplo en outbox
INSERT INTO outbox_afiliados_events (
    id, aggregate_id, event_type, event_data, correlation_id, causation_id
) VALUES 
(
    '770e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440001',
    'AffiliateCreated',
    JSON_OBJECT(
        'affiliate_id', '550e8400-e29b-41d4-a716-446655440001',
        'document_number', '12345678',
        'document_type', 'CC',
        'email', 'juan.perez@example.com',
        'affiliate_type', 'INDIVIDUAL',
        'registration_date', '2024-01-15T10:30:00Z'
    ),
    '880e8400-e29b-41d4-a716-446655440001',
    NULL
),
(
    '770e8400-e29b-41d4-a716-446655440002',
    '550e8400-e29b-41d4-a716-446655440001',
    'AffiliateActivated',
    JSON_OBJECT(
        'affiliate_id', '550e8400-e29b-41d4-a716-446655440001',
        'activation_date', '2024-01-15T11:00:00Z',
        'activated_by', 'system'
    ),
    '880e8400-e29b-41d4-a716-446655440002',
    '880e8400-e29b-41d4-a716-446655440001'
);

-- Opcional: Crear usuario específico para el microservicio de afiliados
-- CREATE USER IF NOT EXISTS 'afiliados_user'@'%' IDENTIFIED BY 'afiliados_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON alpes_afiliados.* TO 'afiliados_user'@'%';
-- FLUSH PRIVILEGES;

-- Mostrar resumen de datos insertados
SELECT 
    'Afiliados creados' as Tabla,
    COUNT(*) as Total,
    COUNT(CASE WHEN estado = 'ACTIVO' THEN 1 END) as Activos,
    COUNT(CASE WHEN estado = 'PENDIENTE_VALIDACION' THEN 1 END) as Pendientes,
    COUNT(CASE WHEN estado = 'SUSPENDIDO' THEN 1 END) as Suspendidos
FROM afiliados

UNION ALL

SELECT 
    'Referencias creadas' as Tabla,
    COUNT(*) as Total,
    COUNT(CASE WHEN verificada = TRUE THEN 1 END) as Verificadas,
    COUNT(CASE WHEN verificada = FALSE THEN 1 END) as Pendientes,
    0 as Suspendidos
FROM referencias_afiliados

UNION ALL

SELECT 
    'Eventos outbox' as Tabla,
    COUNT(*) as Total,
    COUNT(CASE WHEN processed = TRUE THEN 1 END) as Procesados,
    COUNT(CASE WHEN processed = FALSE THEN 1 END) as Pendientes,
    0 as Suspendidos
FROM outbox_afiliados_events;