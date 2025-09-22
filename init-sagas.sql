-- Base de datos para microservicio de Sagas
CREATE DATABASE IF NOT EXISTS sagas;
USE sagas;

-- Crear usuario específico
CREATE USER IF NOT EXISTS 'sagas'@'%' IDENTIFIED BY 'sagas123';
GRANT ALL PRIVILEGES ON sagas.* TO 'sagas'@'%';
FLUSH PRIVILEGES;

-- ==========================================
-- Esquema de Sagas
-- ==========================================

-- Tabla principal de sagas
CREATE TABLE IF NOT EXISTS sagas (
    id VARCHAR(36) PRIMARY KEY,
    tipo_saga VARCHAR(100) NOT NULL,
    nombre_saga VARCHAR(255) NOT NULL,
    descripcion TEXT,
    estado ENUM('INICIADA', 'EN_PROGRESO', 'COMPLETADA', 'FALLIDA', 'COMPENSANDO', 'COMPENSADA', 'CANCELADA') DEFAULT 'INICIADA',
    contexto JSON, -- Estado global de la saga
    resultado JSON NULL, -- Resultado final de la saga
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME NULL,
    tiempo_expiracion DATETIME NULL,
    error_mensaje TEXT NULL,
    iniciado_por VARCHAR(36), -- ID del usuario o sistema que inició
    prioridad ENUM('BAJA', 'MEDIA', 'ALTA', 'CRITICA') DEFAULT 'MEDIA',
    reintentos_maximos INT DEFAULT 3,
    reintentos_actuales INT DEFAULT 0,
    version INT DEFAULT 1, -- Para optimistic locking
    metadata JSON NULL,
    INDEX idx_tipo (tipo_saga),
    INDEX idx_estado (estado),
    INDEX idx_fecha_inicio (fecha_inicio),
    INDEX idx_prioridad (prioridad),
    INDEX idx_iniciado_por (iniciado_por)
);

-- Tabla de pasos de saga
CREATE TABLE IF NOT EXISTS saga_pasos (
    id VARCHAR(36) PRIMARY KEY,
    saga_id VARCHAR(36) NOT NULL,
    paso_numero INT NOT NULL,
    nombre_paso VARCHAR(255) NOT NULL,
    servicio VARCHAR(100) NOT NULL,
    comando VARCHAR(100) NOT NULL,
    tipo_operacion ENUM('ACCION', 'COMPENSACION') DEFAULT 'ACCION',
    estado ENUM('PENDIENTE', 'EJECUTANDO', 'COMPLETADO', 'FALLIDO', 'COMPENSADO', 'OMITIDO') DEFAULT 'PENDIENTE',
    es_opcional BOOLEAN DEFAULT FALSE,
    timeout_segundos INT DEFAULT 30,
    request_data JSON,
    response_data JSON NULL,
    error_mensaje TEXT NULL,
    fecha_inicio DATETIME NULL,
    fecha_fin DATETIME NULL,
    intentos INT DEFAULT 0,
    max_intentos INT DEFAULT 3,
    compensacion_completada BOOLEAN DEFAULT FALSE,
    dependencias JSON NULL, -- IDs de pasos que deben completarse antes
    metadata JSON NULL,
    INDEX idx_saga (saga_id),
    INDEX idx_estado (estado),
    INDEX idx_paso_numero (paso_numero),
    INDEX idx_servicio (servicio),
    INDEX idx_tipo_operacion (tipo_operacion),
    FOREIGN KEY (saga_id) REFERENCES sagas(id) ON DELETE CASCADE
);

-- Tabla de definiciones de saga (templates)
CREATE TABLE IF NOT EXISTS saga_definiciones (
    id VARCHAR(36) PRIMARY KEY,
    tipo_saga VARCHAR(100) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    definicion_pasos JSON NOT NULL, -- Definición de los pasos de la saga
    configuracion JSON NULL, -- Configuración por defecto
    activo BOOLEAN DEFAULT TRUE,
    timeout_global_segundos INT DEFAULT 300,
    max_reintentos INT DEFAULT 3,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tipo (tipo_saga),
    INDEX idx_activo (activo),
    INDEX idx_version (version)
);

-- Tabla de eventos de saga
CREATE TABLE IF NOT EXISTS saga_eventos (
    id VARCHAR(36) PRIMARY KEY,
    saga_id VARCHAR(36) NOT NULL,
    paso_id VARCHAR(36) NULL,
    tipo_evento ENUM('SAGA_INICIADA', 'PASO_INICIADO', 'PASO_COMPLETADO', 'PASO_FALLIDO', 'COMPENSACION_INICIADA', 'COMPENSACION_COMPLETADA', 'SAGA_COMPLETADA', 'SAGA_FALLIDA', 'SAGA_CANCELADA') NOT NULL,
    detalle TEXT,
    datos_evento JSON NULL,
    timestamp_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    procesado BOOLEAN DEFAULT FALSE,
    INDEX idx_saga (saga_id),
    INDEX idx_paso (paso_id),
    INDEX idx_tipo_evento (tipo_evento),
    INDEX idx_timestamp (timestamp_evento),
    INDEX idx_procesado (procesado),
    FOREIGN KEY (saga_id) REFERENCES sagas(id) ON DELETE CASCADE,
    FOREIGN KEY (paso_id) REFERENCES saga_pasos(id) ON DELETE SET NULL
);

-- Tabla de métricas de saga
CREATE TABLE IF NOT EXISTS saga_metricas (
    id VARCHAR(36) PRIMARY KEY,
    tipo_saga VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    total_iniciadas INT DEFAULT 0,
    total_completadas INT DEFAULT 0,
    total_fallidas INT DEFAULT 0,
    total_compensadas INT DEFAULT 0,
    tiempo_promedio_ejecucion DECIMAL(10,3) DEFAULT 0.000, -- en segundos
    tasa_exito DECIMAL(5,4) DEFAULT 0.0000,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tipo (tipo_saga),
    INDEX idx_fecha (fecha),
    UNIQUE KEY unique_tipo_fecha (tipo_saga, fecha)
);

-- ==========================================
-- Datos de ejemplo
-- ==========================================

-- Insertar definiciones de saga
INSERT IGNORE INTO saga_definiciones (id, tipo_saga, nombre, descripcion, definicion_pasos, timeout_global_segundos) VALUES 
('def-001', 'LANZAR_CAMPANIA_COMPLETA', 'Lanzar Campaña Completa', 'Saga que orquesta el lanzamiento completo de una campaña incluyendo todos los microservicios', 
'[
  {"paso": 1, "servicio": "campanias", "comando": "activar_campania", "opcional": false},
  {"paso": 2, "servicio": "afiliados", "comando": "asignar_afiliados", "opcional": false},
  {"paso": 3, "servicio": "comisiones", "comando": "configurar_comisiones", "opcional": false},
  {"paso": 4, "servicio": "notificaciones", "comando": "notificar_afiliados", "opcional": true},
  {"paso": 5, "servicio": "conversiones", "comando": "inicializar_tracking", "opcional": false}
]', 600),
('def-002', 'PROCESAR_PAGO_COMISIONES', 'Procesar Pago de Comisiones', 'Saga para procesar el pago mensual de comisiones a afiliados',
'[
  {"paso": 1, "servicio": "comisiones", "comando": "calcular_comisiones_periodo", "opcional": false},
  {"paso": 2, "servicio": "comisiones", "comando": "generar_lote_pago", "opcional": false},
  {"paso": 3, "servicio": "pagos", "comando": "procesar_transferencias", "opcional": false},
  {"paso": 4, "servicio": "notificaciones", "comando": "notificar_pagos_procesados", "opcional": true},
  {"paso": 5, "servicio": "afiliados", "comando": "actualizar_estadisticas", "opcional": true}
]', 1800);

-- Insertar sagas de ejemplo
INSERT IGNORE INTO sagas (id, tipo_saga, nombre_saga, estado, contexto, fecha_inicio, iniciado_por) VALUES 
('saga-001', 'LANZAR_CAMPANIA_COMPLETA', 'Lanzamiento Campaña Navideña 2024', 'COMPLETADA', 
'{"campania_id": "camp-001", "afiliados": ["af-001", "af-002", "af-003"], "presupuesto": 50000, "fecha_inicio": "2024-12-01"}', 
'2024-11-30 23:00:00', 'admin-001'),
('saga-002', 'LANZAR_CAMPANIA_COMPLETA', 'Lanzamiento Producto Tech', 'EN_PROGRESO', 
'{"campania_id": "camp-002", "afiliados": ["af-002", "af-003"], "presupuesto": 75000, "fecha_inicio": "2024-12-15"}', 
'2024-12-01 10:00:00', 'admin-001'),
('saga-003', 'PROCESAR_PAGO_COMISIONES', 'Pago Comisiones Noviembre 2024', 'COMPLETADA',
'{"periodo": "2024-11", "total_afiliados": 25, "total_comisiones": 15000}',
'2024-12-01 01:00:00', 'sistema');

-- Insertar pasos de saga
INSERT IGNORE INTO saga_pasos (id, saga_id, paso_numero, nombre_paso, servicio, comando, estado, request_data, response_data, fecha_inicio, fecha_fin) VALUES 
('paso-001', 'saga-001', 1, 'Activar Campaña', 'campanias', 'activar_campania', 'COMPLETADO', '{"campania_id": "camp-001"}', '{"status": "ACTIVA", "fecha_activacion": "2024-12-01T00:00:00Z"}', '2024-11-30 23:01:00', '2024-11-30 23:01:30'),
('paso-002', 'saga-001', 2, 'Asignar Afiliados', 'afiliados', 'asignar_afiliados', 'COMPLETADO', '{"campania_id": "camp-001", "afiliados": ["af-001", "af-002", "af-003"]}', '{"asignados": 3, "fallidos": 0}', '2024-11-30 23:02:00', '2024-11-30 23:02:15'),
('paso-003', 'saga-001', 3, 'Configurar Comisiones', 'comisiones', 'configurar_comisiones', 'COMPLETADO', '{"campania_id": "camp-001", "comision_base": 7.5}', '{"configuraciones_creadas": 3}', '2024-11-30 23:02:30', '2024-11-30 23:02:45'),
('paso-004', 'saga-001', 4, 'Notificar Afiliados', 'notificaciones', 'notificar_afiliados', 'COMPLETADO', '{"campania_id": "camp-001", "template": "NUEVA_CAMPANIA"}', '{"notificaciones_enviadas": 3}', '2024-11-30 23:03:00', '2024-11-30 23:03:20'),
('paso-005', 'saga-001', 5, 'Inicializar Tracking', 'conversiones', 'inicializar_tracking', 'COMPLETADO', '{"campania_id": "camp-001"}', '{"tracking_configurado": true}', '2024-11-30 23:03:30', '2024-11-30 23:03:40'),

('paso-006', 'saga-002', 1, 'Activar Campaña', 'campanias', 'activar_campania', 'COMPLETADO', '{"campania_id": "camp-002"}', '{"status": "ACTIVA", "fecha_activacion": "2024-12-01T10:01:00Z"}', '2024-12-01 10:01:00', '2024-12-01 10:01:20'),
('paso-007', 'saga-002', 2, 'Asignar Afiliados', 'afiliados', 'asignar_afiliados', 'EJECUTANDO', '{"campania_id": "camp-002", "afiliados": ["af-002", "af-003"]}', NULL, '2024-12-01 10:02:00', NULL);

-- Insertar eventos de saga
INSERT IGNORE INTO saga_eventos (id, saga_id, paso_id, tipo_evento, detalle, timestamp_evento) VALUES 
('evt-001', 'saga-001', NULL, 'SAGA_INICIADA', 'Saga iniciada para lanzamiento de Campaña Navideña 2024', '2024-11-30 23:00:00'),
('evt-002', 'saga-001', 'paso-001', 'PASO_COMPLETADO', 'Campaña activada exitosamente', '2024-11-30 23:01:30'),
('evt-003', 'saga-001', 'paso-002', 'PASO_COMPLETADO', 'Afiliados asignados a la campaña', '2024-11-30 23:02:15'),
('evt-004', 'saga-001', 'paso-005', 'PASO_COMPLETADO', 'Tracking inicializado para la campaña', '2024-11-30 23:03:40'),
('evt-005', 'saga-001', NULL, 'SAGA_COMPLETADA', 'Saga completada exitosamente', '2024-11-30 23:04:00'),
('evt-006', 'saga-002', NULL, 'SAGA_INICIADA', 'Saga iniciada para lanzamiento de Producto Tech', '2024-12-01 10:00:00');

-- Insertar métricas de ejemplo
INSERT IGNORE INTO saga_metricas (id, tipo_saga, fecha, total_iniciadas, total_completadas, total_fallidas, tiempo_promedio_ejecucion, tasa_exito) VALUES 
('met-001', 'LANZAR_CAMPANIA_COMPLETA', '2024-11-30', 1, 1, 0, 240.000, 1.0000),
('met-002', 'LANZAR_CAMPANIA_COMPLETA', '2024-12-01', 1, 0, 0, 0.000, 0.0000),
('met-003', 'PROCESAR_PAGO_COMISIONES', '2024-12-01', 1, 1, 0, 1200.000, 1.0000);