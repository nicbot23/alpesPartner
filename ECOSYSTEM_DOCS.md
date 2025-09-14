# 🚀 AlpesPartner Ecosystem - Documentación Completa

## 📋 Índice

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Microservicios](#microservicios)
3. [APIs REST](#apis-rest)
4. [Eventos Pulsar](#eventos-pulsar)
5. [Deployment](#deployment)
6. [Casos de Uso](#casos-de-uso)
7. [Monitoreo](#monitoreo)
8. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    AlpesPartner Ecosystem                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │  Afiliados  │    │ Conversiones│    │     Marketing       │  │
│  │ :8001       │    │ :8002       │    │     :8003           │  │
│  │             │    │             │    │ ┌─────────────────┐ │  │
│  │ - Registro  │    │ - Tracking  │    │ │   Comisiones    │ │  │
│  │ - Gestión   │    │ - Métricas  │    │ │   - Cálculo     │ │  │
│  │ - Config    │    │ - Reporting │    │ │   - Aprobación  │ │  │
│  └─────────────┘    └─────────────┘    │ │   - Pago        │ │  │
│          │                   │         │ └─────────────────┘ │  │
│          │                   │         └─────────────────────┘  │
│          │                   │                   │              │
│          └───────────────────┼───────────────────┘              │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  Apache Pulsar                              │  │
│  │                Event Streaming                              │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐    │  │
│  │  │ afiliados   │ │conversiones │ │     comisiones      │    │  │
│  │  │ .eventos    │ │ .eventos    │ │     .eventos        │    │  │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │MySQL        │    │MySQL        │    │MySQL                │  │
│  │Afiliados    │    │Conversiones │    │Marketing            │  │
│  │:3306        │    │:3307        │    │:3308                │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                                                 │
│  ┌─────────────┐    ┌─────────────────────────────────────────┐  │
│  │Redis Cache  │    │         Herramientas Admin              │  │
│  │:6379        │    │ • phpMyAdmin :8082                      │  │
│  └─────────────┘    │ • Pulsar Manager :9527                  │  │
│                     │ • Redis Commander :8081                 │  │
│                     └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Tecnologías Utilizadas

- **Framework**: FastAPI (Python 3.11)
- **Base de Datos**: MySQL 8.0 (una por microservicio)
- **Cache**: Redis 7.0
- **Messaging**: Apache Pulsar
- **Containerización**: Docker & Docker Compose
- **Arquitectura**: Microservicios + Event-Driven Architecture

---

## 🎯 Microservicios

### 1. Servicio Afiliados (Puerto 8001)

**Responsabilidades:**
- Gestión de afiliados (registro, actualización, eliminación)
- Configuración de comisiones por afiliado
- Datos bancarios y documentación
- Emisión de eventos de ciclo de vida de afiliados

**Base de Datos:** `alpes_afiliados` (Puerto 3306)

**Eventos Publicados:**
- `afiliado_creado`
- `afiliado_actualizado`
- `afiliado_eliminado`

### 2. Servicio Conversiones (Puerto 8002)

**Responsabilidades:**
- Tracking de conversiones y ventas
- Métricas de rendimiento por canal
- Atribución de conversiones a campañas
- Validación de datos de conversión

**Base de Datos:** `alpes_conversiones` (Puerto 3307)

**Eventos Publicados:**
- `conversion_registrada`
- `conversion_validada`
- `conversion_procesada`

### 3. Servicio Marketing (Puerto 8003)

**Responsabilidades:**
- Gestión de campañas de marketing
- **Módulo Comisiones** (coordinador central)
- Segmentación y targeting
- Coordinación entre servicios

**Base de Datos:** `alpes_marketing` (Puerto 3308)

**Eventos Publicados:**
- `campana_creada`
- `campana_activada`
- `comision_creada`
- `comision_calculada`
- `comision_aprobada`

---

## 🔗 APIs REST

### Servicio Afiliados

#### Crear Afiliado
```http
POST http://localhost:8001/api/v1/afiliados
Content-Type: application/json

{
    "nombre": "María González",
    "email": "maria.gonzalez@email.com",
    "telefono": "+57 300 123 4567",
    "documento": {
        "tipo": "cedula",
        "numero": "1234567890"
    },
    "tipo_afiliado": "premium",
    "datos_bancarios": {
        "banco": "Banco Nacional",
        "tipo_cuenta": "ahorros",
        "numero_cuenta": "1234567890"
    },
    "configuracion_comisiones": {
        "comision_base": 15.0,
        "comision_premium": 20.0,
        "minimo_pago": 50000.0
    }
}
```

**Respuesta:**
```json
{
    "afiliado_id": "af_12345",
    "nombre": "María González",
    "email": "maria.gonzalez@email.com",
    "estado": "activo",
    "fecha_registro": "2023-12-01T10:00:00Z"
}
```

#### Listar Afiliados
```http
GET http://localhost:8001/api/v1/afiliados
```

#### Obtener Afiliado
```http
GET http://localhost:8001/api/v1/afiliados/{afiliado_id}
```

#### Actualizar Afiliado
```http
PUT http://localhost:8001/api/v1/afiliados/{afiliado_id}
Content-Type: application/json

{
    "telefono": "+57 300 999 8888",
    "configuracion_comisiones": {
        "comision_base": 18.0,
        "comision_premium": 25.0,
        "minimo_pago": 75000.0
    }
}
```

### Servicio Conversiones

#### Registrar Conversión
```http
POST http://localhost:8002/api/v1/conversiones
Content-Type: application/json

{
    "afiliado_id": "af_12345",
    "campana_id": "camp_67890",
    "tipo_conversion": "venta",
    "valor_conversion": 250000.0,
    "moneda": "COP",
    "canal_origen": "web",
    "datos_cliente": {
        "email": "cliente@email.com",
        "ubicacion": "Bogotá",
        "dispositivo": "desktop"
    },
    "productos": [
        {
            "id": "PROD001",
            "nombre": "Laptop Gaming",
            "categoria": "Tecnología",
            "precio": 250000.0,
            "cantidad": 1
        }
    ],
    "metadatos": {
        "utm_source": "google",
        "utm_campaign": "black_friday",
        "utm_medium": "cpc"
    }
}
```

**Respuesta:**
```json
{
    "conversion_id": "conv_98765",
    "afiliado_id": "af_12345",
    "campana_id": "camp_67890",
    "estado": "registrada",
    "valor_conversion": 250000.0,
    "fecha_conversion": "2023-12-01T10:30:00Z"
}
```

#### Listar Conversiones
```http
GET http://localhost:8002/api/v1/conversiones?afiliado_id=af_12345&campana_id=camp_67890
```

#### Métricas de Conversión
```http
GET http://localhost:8002/api/v1/conversiones/metricas?periodo=30d&canal=web
```

### Servicio Marketing

#### Crear Campaña
```http
POST http://localhost:8003/api/v1/campanas
Content-Type: application/json

{
    "nombre": "Campaña Black Friday 2023",
    "descripcion": "Promoción especial de Black Friday",
    "fecha_inicio": "2023-11-24T00:00:00Z",
    "fecha_fin": "2023-11-27T23:59:59Z",
    "presupuesto": 500000.0,
    "moneda": "COP",
    "tipo_campana": "promocional",
    "canales": ["web", "email", "social"],
    "segmentacion": {
        "edad_minima": 18,
        "edad_maxima": 65,
        "ubicaciones": ["Bogotá", "Medellín", "Cali"]
    },
    "configuracion_comisiones": {
        "comision_conversion": 15.0,
        "comision_venta": 8.0,
        "bonus_objetivos": 25.0
    }
}
```

#### Crear Comisión
```http
POST http://localhost:8003/api/v1/comisiones
Content-Type: application/json

{
    "afiliado_id": "af_12345",
    "campana_id": "camp_67890",
    "conversion_id": "conv_98765",
    "monto_base": {
        "valor": 250000.0,
        "moneda": "COP"
    },
    "tipo_comision": "porcentual",
    "porcentaje": 15.0,
    "configuracion": {
        "aplicar_descuentos": true,
        "incluir_iva": false
    }
}
```

#### Calcular Comisión
```http
POST http://localhost:8003/api/v1/comisiones/{comision_id}/calcular
Content-Type: application/json

{
    "forzar_recalculo": false
}
```

#### Aprobar Comisión
```http
POST http://localhost:8003/api/v1/comisiones/{comision_id}/aprobar
Content-Type: application/json

{
    "comentarios": "Comisión aprobada automáticamente",
    "metadatos_aprobacion": {
        "nivel_aprobacion": "automatico",
        "politica_aplicada": "estandar"
    }
}
```

#### Listar Comisiones
```http
GET http://localhost:8003/api/v1/comisiones?afiliado_id=af_12345&estado=aprobada
```

#### Reportes de Comisiones
```http
GET http://localhost:8003/api/v1/comisiones/reportes?periodo=30d&formato=json
```

---

## 📡 Eventos Pulsar

### Configuración de Tópicos

| Tópico | Particiones | Retención | Descripción |
|--------|-------------|-----------|-------------|
| `afiliados.eventos` | 4 | 30d | Eventos del ciclo de vida de afiliados |
| `conversiones.eventos` | 6 | 90d | Eventos de tracking y conversiones |
| `marketing.eventos` | 4 | 60d | Eventos de campañas y marketing |
| `comisiones.eventos` | 8 | 365d | Eventos del módulo de comisiones |
| `auditoria.eventos` | 4 | 1y | Eventos de auditoría y compliance |
| `sistema.eventos` | 2 | 7d | Eventos de sistema y monitoreo |

### Esquemas de Eventos

#### Evento de Afiliado
```json
{
    "evento_id": "evt_123456",
    "tipo_evento": "afiliado_creado",
    "fecha_evento": "2023-12-01T10:00:00Z",
    "afiliado_id": "af_12345",
    "datos_afiliado": {
        "nombre": "María González",
        "email": "maria.gonzalez@email.com",
        "tipo_afiliado": "premium",
        "configuracion_comisiones": {
            "comision_base": 15.0,
            "comision_premium": 20.0
        }
    },
    "metadatos": {
        "version": "1.0",
        "origen": "afiliados-service"
    }
}
```

#### Evento de Conversión
```json
{
    "evento_id": "evt_789012",
    "tipo_evento": "conversion_registrada",
    "fecha_evento": "2023-12-01T10:30:00Z",
    "conversion_id": "conv_98765",
    "afiliado_id": "af_12345",
    "campana_id": "camp_67890",
    "datos_conversion": {
        "tipo_conversion": "venta",
        "valor_conversion": 250000.0,
        "moneda": "COP",
        "canal_origen": "web"
    },
    "metadatos": {
        "version": "1.0",
        "origen": "conversiones-service"
    }
}
```

#### Evento de Comisión
```json
{
    "evento_id": "evt_345678",
    "tipo_evento": "comision_aprobada",
    "fecha_evento": "2023-12-01T11:00:00Z",
    "comision_id": "com_11111",
    "afiliado_id": "af_12345",
    "campana_id": "camp_67890",
    "conversion_id": "conv_98765",
    "datos_comision": {
        "monto_calculado": 37500.0,
        "moneda": "COP",
        "estado": "aprobada",
        "tipo_comision": "porcentual"
    },
    "metadatos": {
        "version": "1.0",
        "origen": "marketing-service",
        "modulo": "comisiones"
    }
}
```

### Subscripciones por Servicio

| Servicio | Subscripciones |
|----------|---------------|
| **Afiliados** | `marketing-consumer`, `audit-consumer` |
| **Conversiones** | `marketing-consumer`, `analytics-consumer` |
| **Marketing** | `afiliados-consumer`, `conversiones-consumer` |
| **Comisiones** | `afiliados-consumer`, `payment-consumer`, `reporting-consumer` |

---

## 🚀 Deployment

### Requisitos del Sistema

- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0
- **RAM**: Mínimo 8GB recomendado
- **CPU**: 4 cores recomendado
- **Disco**: 10GB disponibles

### Instalación

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd alpesPartner
```

2. **Construir y levantar servicios:**
```bash
docker-compose up --build -d
```

3. **Configurar tópicos Pulsar:**
```bash
./scripts/setup_pulsar_topics.sh
```

4. **Poblar datos de prueba:**
```bash
./scripts/init_test_data.sh
```

5. **Ejecutar pruebas E2E:**
```bash
./scripts/run_e2e_tests.sh
```

### Verificación de Deployment

#### Health Checks
```bash
# Verificar servicios
curl http://localhost:8001/health  # Afiliados
curl http://localhost:8002/health  # Conversiones
curl http://localhost:8003/health  # Marketing

# Verificar Pulsar
curl http://localhost:8080/admin/v2/clusters
```

#### URLs de Administración
- **Afiliados API**: http://localhost:8001/docs
- **Conversiones API**: http://localhost:8002/docs
- **Marketing API**: http://localhost:8003/docs
- **Pulsar Manager**: http://localhost:9527
- **phpMyAdmin**: http://localhost:8082
- **Redis Commander**: http://localhost:8081

### Variables de Entorno

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `PYTHONPATH` | `/app/src` | Path para imports Python |
| `DATABASE_URL` | `mysql://...` | Conexión a MySQL |
| `REDIS_URL` | `redis://redis:6379` | Conexión a Redis |
| `PULSAR_URL` | `pulsar://pulsar:6650` | Conexión a Pulsar |

---

## 💼 Casos de Uso

### Caso 1: Registro de Nuevo Afiliado

**Flujo:**
1. Usuario registra afiliado vía API POST `/afiliados`
2. Servicio Afiliados valida y almacena datos
3. Se emite evento `afiliado_creado` en Pulsar
4. Marketing consume evento y actualiza configuraciones

**Código de ejemplo:**
```bash
curl -X POST http://localhost:8001/api/v1/afiliados \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Juan Pérez", "email": "juan@email.com", ...}'
```

### Caso 2: Procesamiento de Conversión con Comisión

**Flujo:**
1. Se registra conversión vía API POST `/conversiones`
2. Servicio Conversiones valida y almacena
3. Se emite evento `conversion_registrada`
4. Marketing consume evento y crea comisión automáticamente
5. Se calcula y aprueba comisión
6. Se emite evento `comision_aprobada`

**Código de ejemplo:**
```bash
# 1. Registrar conversión
CONVERSION_RESPONSE=$(curl -X POST http://localhost:8002/api/v1/conversiones \
  -H "Content-Type: application/json" \
  -d '{"afiliado_id": "af_123", "valor_conversion": 100000, ...}')

CONVERSION_ID=$(echo $CONVERSION_RESPONSE | jq -r '.conversion_id')

# 2. Crear comisión
curl -X POST http://localhost:8003/api/v1/comisiones \
  -H "Content-Type: application/json" \
  -d "{\"conversion_id\": \"$CONVERSION_ID\", ...}"
```

### Caso 3: Reporte de Comisiones

**Flujo:**
1. Consultar comisiones por período vía API GET `/comisiones`
2. Filtrar por estado, afiliado, campaña
3. Exportar datos en formato JSON/CSV

**Código de ejemplo:**
```bash
# Obtener comisiones aprobadas del último mes
curl "http://localhost:8003/api/v1/comisiones?estado=aprobada&periodo=30d"

# Reporte de afiliado específico
curl "http://localhost:8003/api/v1/comisiones?afiliado_id=af_123&formato=csv"
```

---

## 📊 Monitoreo

### Dashboard en Tiempo Real

**Monitoreo de Pulsar:**
```bash
./scripts/monitor_pulsar.sh dashboard
```

**Logging continuo:**
```bash
./scripts/monitor_pulsar.sh log 10
```

### Métricas Clave

| Métrica | Descripción | Umbral |
|---------|-------------|--------|
| **Throughput** | Mensajes/segundo en Pulsar | > 100 msg/s |
| **Latencia** | Tiempo respuesta APIs | < 200ms |
| **Backlog** | Mensajes pendientes | < 100 |
| **Storage** | Uso almacenamiento Pulsar | < 1GB |

### Alertas Automáticas

El script de monitoreo genera alertas cuando:
- Backlog > 100 mensajes en cualquier tópico
- Uso de almacenamiento > 100MB por tópico
- Servicios no responden a health checks

### Logs de Aplicación

```bash
# Ver logs de servicios
docker-compose logs -f afiliados
docker-compose logs -f conversiones
docker-compose logs -f marketing

# Ver logs de Pulsar
docker-compose logs -f pulsar
```

---

## 🛠️ Troubleshooting

### Problemas Comunes

#### 1. Servicios no inician
**Síntomas:** Error al acceder a APIs
**Solución:**
```bash
# Verificar estado de contenedores
docker-compose ps

# Revisar logs
docker-compose logs

# Reiniciar servicios
docker-compose restart
```

#### 2. Error de conexión a base de datos
**Síntomas:** 500 error en APIs, logs muestran connection refused
**Solución:**
```bash
# Verificar MySQL
docker-compose exec mysql-afiliados mysql -u root -p -e "SHOW DATABASES;"

# Recrear contenedores de BD
docker-compose down
docker volume rm alpespartner_mysql_afiliados_data
docker-compose up -d
```

#### 3. Eventos no se procesan en Pulsar
**Síntomas:** Backlog alto, eventos no llegan a consumidores
**Solución:**
```bash
# Verificar tópicos
./scripts/monitor_pulsar.sh topics

# Recrear tópicos
./scripts/setup_pulsar_topics.sh

# Verificar subscripciones
curl http://localhost:8080/admin/v2/persistent/public/default/comisiones.eventos/subscriptions
```

#### 4. Performance degradado
**Síntomas:** APIs lentas, timeouts
**Solución:**
```bash
# Verificar recursos
docker stats

# Escalar servicios
docker-compose up -d --scale marketing=2

# Verificar cache Redis
docker-compose exec redis redis-cli INFO memory
```

### Comandos de Diagnóstico

```bash
# Estado general del ecosistema
docker-compose ps
docker-compose top

# Uso de recursos
docker system df
docker system prune

# Conectividad de red
docker network ls
docker network inspect alpespartner_alpes_network

# Verificar datos
docker-compose exec mysql-marketing mysql -u marketing -p -e "SELECT COUNT(*) FROM comisiones;"
```

### Recovery Procedures

#### Reinicio Completo
```bash
# Parar todos los servicios
docker-compose down

# Limpiar volúmenes (¡cuidado! esto elimina datos)
docker-compose down -v

# Reconstruir e iniciar
docker-compose up --build -d

# Reconfigurar
./scripts/setup_pulsar_topics.sh
./scripts/init_test_data.sh
```

#### Backup y Restore
```bash
# Backup de bases de datos
docker-compose exec mysql-afiliados mysqldump -u root -p alpes_afiliados > backup_afiliados.sql

# Restore
docker-compose exec -i mysql-afiliados mysql -u root -p alpes_afiliados < backup_afiliados.sql
```

---

## 📚 Recursos Adicionales

### Documentación de APIs
- **OpenAPI Specs**: Disponibles en `/docs` de cada servicio
- **Postman Collection**: [Descargar aquí]()
- **Insomnia Workspace**: [Importar archivo]()

### Arquitectura
- **Diagramas C4**: Ver carpeta `/docs/architecture/`
- **Context Map**: Ver `CONTEXT_MAP.md`
- **ADRs**: Architectural Decision Records en `/docs/adr/`

### Desarrollo
- **Contributing Guide**: `CONTRIBUTING.md`
- **Code Style**: PEP 8 + Black + isort
- **Testing**: pytest + coverage

### Soporte
- **Issues**: GitHub Issues
- **Discord**: [Canal del proyecto]()
- **Email**: soporte@alpespartner.com

---

*Documentación generada automáticamente - AlpesPartner Ecosystem v1.0*