-- Base de datos para microservicio de Notificaciones
CREATE DATABASE IF NOT EXISTS notificaciones;
USE notificaciones;

-- Crear usuario específico
CREATE USER IF NOT EXISTS 'notificaciones'@'%' IDENTIFIED BY 'notificaciones123';
GRANT ALL PRIVILEGES ON notificaciones.* TO 'notificaciones'@'%';
FLUSH PRIVILEGES;

-- ==========================================
-- Esquema de Notificaciones
-- ==========================================

-- Tabla principal de notificaciones
CREATE TABLE IF NOT EXISTS notificaciones (
    id VARCHAR(36) PRIMARY KEY,
    destinatario VARCHAR(255) NOT NULL,
    tipo_destinatario ENUM('AFILIADO', 'ADMIN', 'SISTEMA', 'CLIENTE') DEFAULT 'AFILIADO',
    tipo_notificacion ENUM('EMAIL', 'SMS', 'PUSH', 'WEBHOOK', 'SLACK', 'DISCORD') NOT NULL,
    canal ENUM('TRANSACCIONAL', 'MARKETING', 'SISTEMA', 'URGENTE') DEFAULT 'TRANSACCIONAL',
    prioridad ENUM('BAJA', 'MEDIA', 'ALTA', 'CRITICA') DEFAULT 'MEDIA',
    asunto VARCHAR(255),
    mensaje TEXT NOT NULL,
    mensaje_html TEXT NULL,
    template_id VARCHAR(100) NULL,
    variables JSON NULL, -- Variables para el template
    estado ENUM('PENDIENTE', 'ENVIANDO', 'ENVIADA', 'FALLIDA', 'CANCELADA', 'LEIDA') DEFAULT 'PENDIENTE',
    intentos INT DEFAULT 0,
    max_intentos INT DEFAULT 3,
    fecha_programada DATETIME NULL, -- Para notificaciones programadas
    fecha_envio DATETIME NULL,
    fecha_leida DATETIME NULL,
    fecha_expiracion DATETIME NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_mensaje TEXT NULL,
    referencia_externa VARCHAR(100) NULL, -- ID de campaña, comisión, etc.
    metadata JSON NULL,
    INDEX idx_destinatario (destinatario),
    INDEX idx_tipo_destinatario (tipo_destinatario),
    INDEX idx_tipo_notificacion (tipo_notificacion),
    INDEX idx_estado (estado),
    INDEX idx_prioridad (prioridad),
    INDEX idx_fecha_programada (fecha_programada),
    INDEX idx_fecha_creacion (fecha_creacion),
    INDEX idx_referencia (referencia_externa)
);

-- Tabla de templates de notificación
CREATE TABLE IF NOT EXISTS notificaciones_templates (
    id VARCHAR(36) PRIMARY KEY,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo_notificacion ENUM('EMAIL', 'SMS', 'PUSH', 'WEBHOOK') NOT NULL,
    asunto_template VARCHAR(255),
    mensaje_template TEXT NOT NULL,
    mensaje_html_template TEXT NULL,
    variables_requeridas JSON NULL, -- Lista de variables que debe recibir
    activo BOOLEAN DEFAULT TRUE,
    version INT DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo_notificacion),
    INDEX idx_activo (activo)
);

-- Tabla de configuración de canales
CREATE TABLE IF NOT EXISTS notificaciones_canales (
    id VARCHAR(36) PRIMARY KEY,
    tipo_notificacion ENUM('EMAIL', 'SMS', 'PUSH', 'WEBHOOK', 'SLACK', 'DISCORD') NOT NULL,
    proveedor VARCHAR(100) NOT NULL, -- SendGrid, Twilio, Firebase, etc.
    configuracion JSON NOT NULL, -- API keys, endpoints, etc.
    activo BOOLEAN DEFAULT TRUE,
    limite_diario INT NULL,
    limite_mensual INT NULL,
    costo_por_envio DECIMAL(6,4) DEFAULT 0.0000,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tipo (tipo_notificacion),
    INDEX idx_proveedor (proveedor),
    INDEX idx_activo (activo)
);

-- Tabla de estadísticas de envío
CREATE TABLE IF NOT EXISTS notificaciones_estadisticas (
    id VARCHAR(36) PRIMARY KEY,
    fecha DATE NOT NULL,
    hora INT NOT NULL, -- 0-23
    tipo_notificacion ENUM('EMAIL', 'SMS', 'PUSH', 'WEBHOOK', 'SLACK', 'DISCORD') NOT NULL,
    canal ENUM('TRANSACCIONAL', 'MARKETING', 'SISTEMA', 'URGENTE') NOT NULL,
    total_enviadas INT DEFAULT 0,
    total_fallidas INT DEFAULT 0,
    total_leidas INT DEFAULT 0,
    tasa_entrega DECIMAL(5,4) DEFAULT 0.0000,
    tasa_lectura DECIMAL(5,4) DEFAULT 0.0000,
    costo_total DECIMAL(10,4) DEFAULT 0.0000,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_fecha (fecha),
    INDEX idx_tipo (tipo_notificacion),
    INDEX idx_canal (canal),
    UNIQUE KEY unique_stats (fecha, hora, tipo_notificacion, canal)
);

-- Tabla de suscripciones/preferencias de usuario
CREATE TABLE IF NOT EXISTS notificaciones_preferencias (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(36) NOT NULL,
    tipo_usuario ENUM('AFILIADO', 'ADMIN', 'CLIENTE') NOT NULL,
    tipo_notificacion ENUM('EMAIL', 'SMS', 'PUSH') NOT NULL,
    canal ENUM('TRANSACCIONAL', 'MARKETING', 'SISTEMA') NOT NULL,
    suscrito BOOLEAN DEFAULT TRUE,
    frecuencia ENUM('INMEDIATA', 'DIARIA', 'SEMANAL', 'MENSUAL') DEFAULT 'INMEDIATA',
    horario_preferido TIME DEFAULT '09:00:00',
    timezone VARCHAR(50) DEFAULT 'America/Bogota',
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_usuario (usuario_id),
    INDEX idx_tipo_usuario (tipo_usuario),
    INDEX idx_suscrito (suscrito),
    UNIQUE KEY unique_user_notification (usuario_id, tipo_notificacion, canal)
);

-- ==========================================
-- Datos de ejemplo
-- ==========================================

-- Insertar templates de ejemplo
INSERT IGNORE INTO notificaciones_templates (id, codigo, nombre, tipo_notificacion, asunto_template, mensaje_template, variables_requeridas) VALUES 
('tpl-001', 'COMISION_CALCULADA', 'Comisión Calculada', 'EMAIL', 'Nueva comisión generada - ${monto}', 'Hola ${nombre_afiliado}, se ha generado una nueva comisión de ${monto} por tu campaña ${campania_nombre}.', '["nombre_afiliado", "monto", "campania_nombre"]'),
('tpl-002', 'PAGO_PROCESADO', 'Pago Procesado', 'EMAIL', 'Pago procesado por ${total}', 'Tu pago por ${total} ha sido procesado exitosamente. Referencia: ${referencia_pago}', '["total", "referencia_pago"]'),
('tpl-003', 'NUEVA_CAMPANIA', 'Nueva Campaña Disponible', 'EMAIL', 'Nueva campaña: ${campania_nombre}', 'Se ha creado una nueva campaña "${campania_nombre}" con comisión del ${comision}%.', '["campania_nombre", "comision"]'),
('tpl-004', 'BIENVENIDA_AFILIADO', 'Bienvenido a AlpesPartner', 'EMAIL', 'Bienvenido ${nombre}', 'Hola ${nombre}, bienvenido al programa de afiliados AlpesPartner. Tu código de referido es: ${codigo_referido}', '["nombre", "codigo_referido"]');

-- Insertar configuración de canales
INSERT IGNORE INTO notificaciones_canales (id, tipo_notificacion, proveedor, configuracion, limite_diario, costo_por_envio) VALUES 
('canal-001', 'EMAIL', 'SendGrid', '{"api_key": "SG.xxx", "from_email": "noreply@alpespartner.com", "from_name": "AlpesPartner"}', 10000, 0.0010),
('canal-002', 'SMS', 'Twilio', '{"account_sid": "ACxxx", "auth_token": "xxx", "from_number": "+1234567890"}', 1000, 0.0750),
('canal-003', 'PUSH', 'Firebase', '{"server_key": "AAAAxxx", "project_id": "alpespartner-app"}', 50000, 0.0001);

-- Insertar notificaciones de ejemplo
INSERT IGNORE INTO notificaciones (id, destinatario, tipo_destinatario, tipo_notificacion, asunto, mensaje, template_id, variables, estado, fecha_envio, referencia_externa) VALUES 
('not-001', 'juan.perez@email.com', 'AFILIADO', 'EMAIL', 'Nueva comisión generada - $7.50', 'Hola Juan Pérez, se ha generado una nueva comisión de $7.50 por tu campaña Campaña Navideña 2024.', 'tpl-001', '{"nombre_afiliado": "Juan Pérez", "monto": "$7.50", "campania_nombre": "Campaña Navideña 2024"}', 'ENVIADA', '2024-12-01 10:30:00', 'com-001'),
('not-002', 'contact@techsolutions.com', 'AFILIADO', 'EMAIL', 'Nueva comisión generada - $50.00', 'Hola Tech Solutions, se ha generado una nueva comisión de $50.00 por tu campaña Lanzamiento Producto Tech.', 'tpl-001', '{"nombre_afiliado": "Tech Solutions", "monto": "$50.00", "campania_nombre": "Lanzamiento Producto Tech"}', 'ENVIADA', '2024-12-01 16:15:00', 'com-003'),
('not-003', 'admin@alpespartner.com', 'ADMIN', 'EMAIL', 'Resumen diario de conversiones', 'Reporte de conversiones del día: 5 conversiones, $800 en ventas totales.', NULL, NULL, 'ENVIADA', '2024-12-01 18:00:00', NULL),
('not-004', 'maria@socialnet.com', 'AFILIADO', 'EMAIL', 'Bienvenido María Influencer', 'Hola María, bienvenido al programa de afiliados AlpesPartner. Tu código de referido es: REF003', 'tpl-004', '{"nombre": "María", "codigo_referido": "REF003"}', 'ENVIADA', '2024-09-21 10:00:00', 'af-003');

-- Insertar preferencias de ejemplo
INSERT IGNORE INTO notificaciones_preferencias (id, usuario_id, tipo_usuario, tipo_notificacion, canal, suscrito, frecuencia) VALUES 
('pref-001', 'af-001', 'AFILIADO', 'EMAIL', 'TRANSACCIONAL', TRUE, 'INMEDIATA'),
('pref-002', 'af-001', 'AFILIADO', 'EMAIL', 'MARKETING', TRUE, 'SEMANAL'),
('pref-003', 'af-002', 'AFILIADO', 'EMAIL', 'TRANSACCIONAL', TRUE, 'INMEDIATA'),
('pref-004', 'af-003', 'AFILIADO', 'EMAIL', 'TRANSACCIONAL', TRUE, 'INMEDIATA'),
('pref-005', 'af-003', 'AFILIADO', 'SMS', 'TRANSACCIONAL', FALSE, 'INMEDIATA');

-- Insertar estadísticas de ejemplo
INSERT IGNORE INTO notificaciones_estadisticas (id, fecha, hora, tipo_notificacion, canal, total_enviadas, total_fallidas, total_leidas, tasa_entrega, tasa_lectura) VALUES 
('stat-001', '2024-12-01', 10, 'EMAIL', 'TRANSACCIONAL', 25, 1, 18, 0.9600, 0.7500),
('stat-002', '2024-12-01', 16, 'EMAIL', 'TRANSACCIONAL', 15, 0, 12, 1.0000, 0.8000),
('stat-003', '2024-12-01', 18, 'EMAIL', 'SISTEMA', 5, 0, 4, 1.0000, 0.8000);