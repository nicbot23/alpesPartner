# 🚀 AlpesPartner - Sistema de Gestión de Comisiones# 🚀 AlpesPartner - Sistema de Gestión de Comisiones



Sistema distribuido de gestión de afiliados, conversiones y comisiones con arquitectura de microservicios y comunicación asíncrona mediante eventos Apache Pulsar.Sistema distribuido de gestión de afiliados, conversiones y comisiones con arquitectura de microservicios y comunicación asíncrona mediante eventos Apache Pulsar.



## 📋 Tabla de Contenidos## 📋 Tabla de Contenidos



1. [Arquitectura General](#-arquitectura-general)1. [Arquitectura General](#-arquitectura-general)

2. [Estructura del Proyecto](#-estructura-del-proyecto)2. [Estructura del Proyecto](#-estructura-del-proyecto)

3. [Escenarios de Calidad](#-escenarios-de-calidad)3. [Escenarios de Calidad](#-escenarios-de-calidad)

4. [Instrucciones de Despliegue](#-instrucciones-de-despliegue)4. [Instrucciones de Despliegue](#-instrucciones-de-despliegue)

5. [APIs y Endpoints](#-apis-y-endpoints)5. [APIs y Endpoints](#-apis-y-endpoints)

6. [Monitoreo y Observabilidad](#-monitoreo-y-observabilidad)6. [Monitoreo y Observabilidad](#-monitoreo-y-observabilidad)

7. [Pruebas y Validación](#-pruebas-y-validación)7. [Pruebas y Validación](#-pruebas-y-validación)

8. [Troubleshooting](#-troubleshooting)8. [Troubleshooting](#-troubleshooting)



------



## 🏗️ Arquitectura General## 🏗️ Arquitectura General



### Diseño de Alto Nivel### Diseño de Alto Nivel



``````

┌─────────────────────────────────────────────────────────────────────────────┐┌─────────────────────────────────────────────────────────────────────────────┐

│                        AlpesPartner Ecosystem                               ││                        AlpesPartner Ecosystem                               │

├─────────────────────────────────────────────────────────────────────────────┤├─────────────────────────────────────────────────────────────────────────────┤

│                                                                             ││                                                                             │

│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────────────────┐ ││  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────────────────┐ │

│  │  Afiliados  │  │Conversiones │  │           Marketing                  │ ││  │  Afiliados  │  │Conversiones │  │           Marketing                  │ │

│  │   :8001     │  │   :8002     │  │            :8003                     │ ││  │   :8001     │  │   :8002     │  │            :8003                     │ │

│  │             │  │             │  │  ┌─────────────────────────────────┐ │ ││  │             │  │             │  │  ┌─────────────────────────────────┐ │ │

│  │ - Registro  │  │ - Tracking  │  │  │        Comisiones               │ │ ││  │ - Registro  │  │ - Tracking  │  │  │        Comisiones               │ │ │

│  │ - Gestión   │  │ - Métricas  │  │  │    - Cálculo automático         │ │ ││  │ - Gestión   │  │ - Métricas  │  │  │    - Cálculo automático         │ │ │

│  │ - Perfiles  │  │ - Analytics │  │  │    - Workflow aprobación        │ │ ││  │ - Perfiles  │  │ - Analytics │  │  │    - Workflow aprobación        │ │ │

│  │ - Config    │  │ - Reporting │  │  │    - Procesamiento pagos        │ │ ││  │ - Config    │  │ - Reporting │  │  │    - Procesamiento pagos        │ │ │

│  └─────────────┘  └─────────────┘  │  └─────────────────────────────────┘ │ ││  └─────────────┘  └─────────────┘  │  └─────────────────────────────────┘ │ │

│         │                 │        │                                     │ ││         │                 │        │                                     │ │

│         └─────────────────┼────────┼─────────────────────────────────────┘ ││         └─────────────────┼────────┼─────────────────────────────────────┘ │

│                           │        │                                       ││                           │        │                                       │

│  ┌───────────────────────────────────────────────────────────────────────┐   ││  ┌───────────────────────────────────────────────────────────────────────┐   │

│  │                    Apache Pulsar - Event Bus                         │   ││  │                    Apache Pulsar - Event Bus                         │   │

│  │               Messaging & Event Streaming Platform                   │   ││  │               Messaging & Event Streaming Platform                   │   │

│  │                                                                       │   ││  │                                                                       │   │

│  │  📢 marketing.eventos     📢 comisiones.eventos                      │   ││  │  📢 marketing.eventos     📢 comisiones.eventos                      │   │

│  │  📢 afiliados.eventos     📢 sistema.eventos                         │   ││  │  📢 afiliados.eventos     📢 sistema.eventos                         │   │

│  │  📢 conversiones.eventos  📢 notificaciones.eventos                  │   ││  │  📢 conversiones.eventos  📢 notificaciones.eventos                  │   │

│  └───────────────────────────────────────────────────────────────────────┘   ││  └───────────────────────────────────────────────────────────────────────┘   │

│                                                                             ││                                                                             │

│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────────────────┐ ││  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────────────────┐ │

│  │MySQL        │ │MySQL        │ │MySQL                                    │ ││  │MySQL        │ │MySQL        │ │MySQL                                    │ │

│  │Afiliados    │ │Conversiones │ │Marketing/Comisiones                     │ ││  │Afiliados    │ │Conversiones │ │Marketing/Comisiones                     │ │

│  │:3306        │ │:3307        │ │:3308                                    │ ││  │:3306        │ │:3307        │ │:3308                                    │ │

│  └─────────────┘ └─────────────┘ └─────────────────────────────────────────┘ ││  └─────────────┘ └─────────────┘ └─────────────────────────────────────────┘ │

│                                                                             ││                                                                             │

│  ┌─────────────────────────────────────────────────────────────────────────┐ ││  ┌─────────────────────────────────────────────────────────────────────────┐ │

│  │                    Herramientas de Administración                      │ ││  │                    Herramientas de Administración                      │ │

│  │  • Pulsar Manager (9527)    • phpMyAdmin (8082)                       │ ││  │  • Pulsar Manager (9527)    • phpMyAdmin (8082)                       │ │

│  │  • Redis Commander (8081)   • Monitoreo Tiempo Real                   │ ││  │  • Redis Commander (8081)   • Monitoreo Tiempo Real                   │ │

│  └─────────────────────────────────────────────────────────────────────────┘ ││  └─────────────────────────────────────────────────────────────────────────┘ │

└─────────────────────────────────────────────────────────────────────────────┘└─────────────────────────────────────────────────────────────────────────────┘

``````



### Principios Arquitectónicos### Principios Arquitectónicos



- **🔄 Event-Driven Architecture**: Comunicación asíncrona mediante eventos- **🔄 Event-Driven Architecture**: Comunicación asíncrona mediante eventos

- **🎯 Domain-Driven Design**: Separación clara de contextos de negocio- **🎯 Domain-Driven Design**: Separación clara de contextos de negocio

- **📦 Microservicios**: Servicios independientes y escalables- **📦 Microservicios**: Servicios independientes y escalables

- **💾 Database per Service**: Base de datos dedicada por microservicio- **💾 Database per Service**: Base de datos dedicada por microservicio

- **🚀 CQRS**: Separación de comandos y consultas- **🚀 CQRS**: Separación de comandos y consultas

- **📊 Event Sourcing**: Manejo de estado mediante eventos- **📊 Event Sourcing**: Manejo de estado mediante eventos

- **🔒 Outbox Pattern**: Consistencia transaccional en eventos- **🔒 Outbox Pattern**: Consistencia transaccional en eventos



------



## 📁 Estructura del Proyecto## 📁 Estructura del Proyecto



### Organización de Directorios### Organización de Directorios



``````

alpesPartner/alpesPartner/

├── 📊 Configuración y Orquestación├── 📊 Configuración y Orquestación

│   ├── docker-compose.yml              # Orquestación completa del ecosistema│   ├── docker-compose.yml              # Orquestación completa del ecosistema

│   ├── *.Dockerfile                    # Contenedores por microservicio│   ├── *.Dockerfile                    # Contenedores por microservicio

│   ├── *-requirements.txt             # Dependencias por servicio│   ├── *-requirements.txt             # Dependencias por servicio

│   └── .env.*                         # Configuraciones de entorno│   └── .env.*                         # Configuraciones de entorno

││

├── 🏗️ Código Fuente Principal├── 🏗️ Código Fuente Principal

│   └── src/│   └── src/

│       ├── afiliados/                 # Microservicio Afiliados│       ├── afiliados/                 # Microservicio Afiliados

│       │   ├── main.py               # Entry point FastAPI│       │   ├── main.py               # Entry point FastAPI

│       │   ├── eventos.py            # Domain events│       │   ├── eventos.py            # Domain events

│       │   ├── despachadores.py      # Event dispatchers│       │   ├── despachadores.py      # Event dispatchers

│       │   └── api/v1/router.py      # REST endpoints│       │   └── api/v1/router.py      # REST endpoints

│       ││       │

│       ├── conversiones/             # Microservicio Conversiones│       ├── conversiones/             # Microservicio Conversiones

│       │   ├── main.py               # Entry point FastAPI│       │   ├── main.py               # Entry point FastAPI

│       │   ├── eventos.py            # Domain events│       │   ├── eventos.py            # Domain events

│       │   ├── comandos.py           # Command handlers│       │   ├── comandos.py           # Command handlers

│       │   └── consumidores.py       # Event consumers│       │   └── consumidores.py       # Event consumers

│       ││       │

│       ├── marketing/                # Microservicio Marketing│       ├── marketing/                # Microservicio Marketing

│       │   ├── main.py               # Entry point FastAPI│       │   ├── main.py               # Entry point FastAPI

│       │   ├── eventos.py            # Domain events│       │   ├── eventos.py            # Domain events

│       │   ├── despachadores.py      # Event dispatchers│       │   ├── despachadores.py      # Event dispatchers

│       │   └── campanas.py           # Campaign management│       │   └── campanas.py           # Campaign management

│       ││       │

│       └── alpespartner/             # Framework Compartido│       └── alpespartner/             # Framework Compartido

│           ├── api/                  # API Gateway principal│           ├── api/                  # API Gateway principal

│           ├── config/               # Configuraciones compartidas│           ├── config/               # Configuraciones compartidas

│           ├── seedwork/            # Building blocks DDD│           ├── seedwork/            # Building blocks DDD

│           └── modulos/             # Módulos de dominio│           └── modulos/             # Módulos de dominio

│               ├── afiliados/       # Dominio Afiliados│               ├── afiliados/       # Dominio Afiliados

│               ├── conversiones/    # Dominio Conversiones│               ├── conversiones/    # Dominio Conversiones

│               ├── campanas/        # Dominio Campañas│               ├── campanas/        # Dominio Campañas

│               └── comisiones/      # Dominio Comisiones│               └── comisiones/      # Dominio Comisiones

││

├── 🗄️ Base de Datos├── 🗄️ Base de Datos

│   └── db/│   └── db/

│       ├── init.sql                  # Schema principal│       ├── init.sql                  # Schema principal

│       ├── afiliados_init.sql       # Schema afiliados│       ├── afiliados_init.sql       # Schema afiliados

│       ├── conversiones_init.sql    # Schema conversiones│       ├── conversiones_init.sql    # Schema conversiones

│       └── migration_*.sql          # Migraciones específicas│       └── migration_*.sql          # Migraciones específicas

││

├── 🔧 Scripts de Automatización├── 🔧 Scripts de Automatización

│   └── scripts/│   └── scripts/

│       ├── run_full_ecosystem.sh    # Despliegue completo automatizado│       ├── run_full_ecosystem.sh    # Despliegue completo automatizado

│       ├── setup_pulsar_topics.sh   # Configuración tópicos Pulsar│       ├── setup_pulsar_topics.sh   # Configuración tópicos Pulsar

│       ├── init_test_data.sh        # Datos de prueba│       ├── init_test_data.sh        # Datos de prueba

│       ├── run_e2e_tests.sh         # Pruebas end-to-end│       ├── run_e2e_tests.sh         # Pruebas end-to-end

│       ├── monitor_pulsar.sh        # Monitoreo en tiempo real│       ├── monitor_pulsar.sh        # Monitoreo en tiempo real

│       └── outbox_publisher.py      # Publicador de eventos outbox│       └── outbox_publisher.py      # Publicador de eventos outbox

││

├── 🧪 Herramientas de Monitoreo├── 🧪 Herramientas de Monitoreo

│   ├── monitor_escenarios_completo.py  # Monitor completo de escenarios│   ├── monitor_escenarios_completo.py  # Monitor completo de escenarios

│   └── consumer_integration_demo.py    # Demo integración consumers│   ├── consumer_integration_demo.py    # Demo integración consumers

││   └── connectors/pulsar/              # Conectores Pulsar especializados

└── 📚 Documentación│

    ├── README.md                    # Este archivo└── � Documentación

    ├── CONTEXT_MAP.md              # Mapa de contextos DDD    ├── README.md                    # Este archivo

    ├── ECOSYSTEM_DOCS.md           # Documentación técnica detallada    ├── CONTEXT_MAP.md              # Mapa de contextos DDD

    └── REPORTE_ARQUITECTURA.md     # Análisis arquitectónico    ├── ECOSYSTEM_DOCS.md           # Documentación técnica detallada

```    └── REPORTE_ARQUITECTURA.md     # Análisis arquitectónico

```

### Patrones de Código

### Patrones de Código

**Estructura por Microservicio:**

```**Estructura por Microservicio:**

src/{microservicio}/```

├── main.py                 # FastAPI applicationsrc/{microservicio}/

├── eventos.py             # Domain events definition  ├── main.py                 # FastAPI application

├── comandos.py            # Command objects├── eventos.py             # Domain events definition  

├── despachadores.py       # Event dispatchers├── comandos.py            # Command objects

├── consumidores.py        # Event consumers├── despachadores.py       # Event dispatchers

└── api/v1/router.py      # REST API routes├── consumidores.py        # Event consumers

```└── api/v1/router.py      # REST API routes

```

**Estructura DDD (alpespartner/):**

```**Estructura DDD (alpespartner/):**

modulos/{contexto}/```

├── dominio/               # Domain layermodulos/{contexto}/

│   ├── agregados.py      # Aggregate roots├── dominio/               # Domain layer

│   ├── eventos.py        # Domain events│   ├── agregados.py      # Aggregate roots

│   ├── objetos_valor.py  # Value objects│   ├── eventos.py        # Domain events

│   └── repositorios.py   # Repository contracts│   ├── objetos_valor.py  # Value objects

├── aplicacion/           # Application layer│   └── repositorios.py   # Repository contracts

│   ├── comandos.py       # Command objects├── aplicacion/           # Application layer

│   ├── handlers.py       # Command handlers│   ├── comandos.py       # Command objects

│   └── servicios.py      # Application services│   ├── handlers.py       # Command handlers

└── infraestructura/      # Infrastructure layer│   └── servicios.py      # Application services

    ├── modelos.py        # Database models└── infraestructura/      # Infrastructure layer

    ├── repositorios.py   # Repository implementations    ├── modelos.py        # Database models

    └── despachadores.py  # Event dispatchers    ├── repositorios.py   # Repository implementations

```    └── despachadores.py  # Event dispatchers

```

---

---

## 🎯 Escenarios de Calidad

## 🎯 Escenarios de Calidad

### Atributos de Calidad Implementados

### Atributos de Calidad Implementados

#### 1. **Disponibilidad (Availability)**

- **Objetivo**: > 99.5% uptime#### 1. **Disponibilidad (Availability)**

- **Implementación**:- **Objetivo**: > 99.5% uptime

  - Health checks en cada microservicio (`/health`)- **Implementación**:

  - Circuit breaker patterns en comunicaciones  - Health checks en cada microservicio (`/health`)

  - Retry policies con backoff exponencial  - Circuit breaker patterns en comunicaciones

  - Graceful degradation en fallas de dependencias  - Retry policies con backoff exponencial

  - Graceful degradation en fallas de dependencias

**Pruebas de Disponibilidad:**

```bash**Pruebas de Disponibilidad:**

# Verificar health de todos los servicios```bash

curl http://localhost:8001/health  # Afiliados# Verificar health de todos los servicios

curl http://localhost:8002/health  # Conversiones curl http://localhost:8001/health  # Afiliados

curl http://localhost:8003/health  # Marketingcurl http://localhost:8002/health  # Conversiones 

curl http://localhost:8003/health  # Marketing

# Simular falla de servicio y verificar degradación

docker stop alpes-afiliados# Simular falla de servicio y verificar degradación

# El sistema debe continuar funcionando con funcionalidad reducidadocker stop alpes-afiliados

```# El sistema debe continuar funcionando con funcionalidad reducida

```

#### 2. **Escalabilidad (Scalability)**

- **Objetivo**: Soportar 10x carga actual sin modificaciones#### 2. **Escalabilidad (Scalability)**

- **Implementación**:- **Objetivo**: Soportar 10x carga actual sin modificaciones

  - Arquitectura stateless en todos los microservicios- **Implementación**:

  - Event-driven communication para desacoplamiento  - Arquitectura stateless en todos los microservicios

  - Particionado de tópicos Pulsar para paralelización  - Event-driven communication para desacoplamiento

  - Base de datos separada por bounded context  - Particionado de tópicos Pulsar para paralelización

  - Base de datos separada por bounded context

**Pruebas de Escalabilidad:**

```bash**Pruebas de Escalabilidad:**

# Escalar horizontalmente un microservicio```bash

docker-compose up --scale alpes-marketing=3 -d# Escalar horizontalmente un microservicio

docker-compose up --scale alpes-marketing=3 -d

# Generar carga de trabajo para probar escalabilidad

python monitor_escenarios_completo.py# Generar carga de trabajo para probar escalabilidad

```python monitor_escenarios_completo.py

```

#### 3. **Rendimiento (Performance)**

- **Objetivo**: < 200ms response time p95, > 1000 TPS#### 3. **Rendimiento (Performance)**

- **Implementación**:- **Objetivo**: < 200ms response time p95, > 1000 TPS

  - Comunicación asíncrona mediante eventos- **Implementación**:

  - Caching en Redis para consultas frecuentes  - Comunicación asíncrona mediante eventos

  - Connection pooling en bases de datos  - Caching en Redis para consultas frecuentes

  - Índices optimizados en queries principales  - Connection pooling en bases de datos

  - Índices optimizados en queries principales

**Pruebas de Rendimiento:**

```bash**Pruebas de Rendimiento:**

# Ejecutar pruebas de carga```bash

./scripts/run_e2e_tests.sh# Ejecutar pruebas de carga

./scripts/run_e2e_tests.sh

# Monitorear métricas en tiempo real

python monitor_estadisticas_real_time.py# Monitorear métricas en tiempo real

```python monitor_estadisticas_real_time.py

```

#### 4. **Confiabilidad (Reliability)**

- **Objetivo**: MTBF > 720 horas, MTTR < 15 minutos#### 4. **Confiabilidad (Reliability)**

- **Implementación**:- **Objetivo**: MTBF > 720 horas, MTTR < 15 minutos

  - Outbox pattern para consistencia eventual- **Implementación**:

  - Event sourcing para trazabilidad completa  - Outbox pattern para consistencia eventual

  - Transacciones ACID en operaciones críticas  - Event sourcing para trazabilidad completa

  - Dead letter queues para eventos fallidos  - Transacciones ACID en operaciones críticas

  - Dead letter queues para eventos fallidos

**Pruebas de Confiabilidad:**

```bash**Pruebas de Confiabilidad:**

# Verificar consistencia de eventos```bash

docker exec -it alpes-pulsar bin/pulsar-client consume sistema.eventos -s test -n 0# Verificar consistencia de eventos

docker exec -it alpes-pulsar bin/pulsar-client consume sistema.eventos -s test -n 0

# Validar outbox pattern

curl http://localhost:8003/debug/outbox# Validar outbox pattern

```curl http://localhost:8003/debug/outbox

```

#### 5. **Seguridad (Security)**

- **Objetivo**: Cumplir estándares OWASP#### 5. **Seguridad (Security)**

- **Implementación**:- **Objetivo**: Cumplir estándares OWASP

  - Validación de entrada en todos los endpoints- **Implementación**:

  - Rate limiting en APIs públicas  - Validación de entrada en todos los endpoints

  - Logs de auditoría para operaciones críticas  - Rate limiting en APIs públicas

  - Encriptación en tránsito (HTTPS)  - Logs de auditoría para operaciones críticas

  - Encriptación en tránsito (HTTPS)

#### 6. **Mantenibilidad (Maintainability)**

- **Objetivo**: Nuevas features en < 2 sprints#### 6. **Mantenibilidad (Maintainability)**

- **Implementación**:- **Objetivo**: Nuevas features en < 2 sprints

  - Arquitectura hexagonal (ports & adapters)- **Implementación**:

  - Separación clara de responsabilidades  - Arquitectura hexagonal (ports & adapters)

  - APIs versionadas y documentadas  - Separación clara de responsabilidades

  - Tests automatizados E2E  - APIs versionadas y documentadas

  - Tests automatizados E2E

---

---

## 🚀 Instrucciones de Despliegue

## 🚀 Instrucciones de Despliegue

### Prerrequisitos

### Prerrequisitos

- **Docker**: >= 20.10.0

- **Docker Compose**: >= 2.0.0- **Docker**: >= 20.10.0

- **Python**: >= 3.9 (para scripts de monitoreo)- **Docker Compose**: >= 2.0.0

- **Git**: Para clonar el repositorio- **Python**: >= 3.9 (para scripts de monitoreo)

- **curl/jq**: Para pruebas de API- **Git**: Para clonar el repositorio

- **curl/jq**: Para pruebas de API

### Despliegue Automatizado (Recomendado)

### Despliegue Automatizado (Recomendado)

```bash

# 1. Clonar el repositorio```bash

git clone <repository-url># 1. Clonar el repositorio

cd alpesPartnergit clone <repository-url>

cd alpesPartner

# 2. Ejecutar despliegue completo automatizado

./scripts/run_full_ecosystem.sh# 2. Ejecutar despliegue completo automatizado

```./scripts/run_full_ecosystem.sh

```

Este script ejecuta automáticamente:

- ✅ Build y deployment de todos los microserviciosEste script ejecuta automáticamente:

- ✅ Configuración de tópicos Apache Pulsar- ✅ Build y deployment de todos los microservicios

- ✅ Inicialización de bases de datos- ✅ Configuración de tópicos Apache Pulsar

- ✅ Poblado de datos de prueba- ✅ Inicialización de bases de datos

- ✅ Ejecución de casos de prueba E2E- ✅ Poblado de datos de prueba

- ✅ Validación de health checks- ✅ Ejecución de casos de prueba E2E

- ✅ Verificación de comunicación entre servicios- ✅ Validación de health checks

- ✅ Verificación de comunicación entre servicios

### Despliegue Manual Paso a Paso

### Despliegue Manual Paso a Paso

#### Paso 1: Levantar Infraestructura

```bash#### Paso 1: Levantar Infraestructura

# Levantar todos los servicios

docker-compose up --build -d```bash

# Clonar repositorio

# Verificar que todos los contenedores estén corriendogit clone <repository-url>

docker-compose pscd alpesPartner



# Verificar logs si hay problemas# Ejecutar ecosistema completo

docker-compose logs -f./scripts/run_full_ecosystem.sh

``````



#### Paso 2: Configurar Apache PulsarEste script realiza automáticamente:

```bash- ✅ Construcción y deployment de servicios

# Configurar tópicos necesarios- ✅ Configuración de tópicos Apache Pulsar

./scripts/setup_pulsar_topics.sh- ✅ Poblado de datos de prueba

- ✅ Ejecución de casos de prueba E2E

# Verificar tópicos creados- ✅ Validación de eventos y métricas

docker exec -it alpes-pulsar bin/pulsar-admin topics list public/default- ✅ Generación de reportes

```

### 2. Ejecución Manual

#### Paso 3: Inicializar Datos

```bash```bash

# Poblar datos de prueba# 1. Levantar servicios

./scripts/init_test_data.shdocker-compose up --build -d



# Verificar datos en base de datos# 2. Configurar Pulsar

docker exec -it alpes-mysql-marketing mysql -u alpes -palpes -e "SELECT COUNT(*) FROM alpes.afiliados;"./scripts/setup_pulsar_topics.sh

```

# 3. Poblar datos de prueba

#### Paso 4: Validar Despliegue./scripts/init_test_data.sh

```bash

# Ejecutar pruebas E2E# 4. Ejecutar pruebas E2E

./scripts/run_e2e_tests.sh./scripts/run_e2e_tests.sh

```

# Verificar health de servicios

for port in 8001 8002 8003; do## � URLs de Acceso

  echo "Checking service on port $port"

  curl -f http://localhost:$port/health || echo "Service on port $port is not healthy"### APIs REST (Documentación OpenAPI)

done- **Afiliados**: http://localhost:8001/docs

```- **Conversiones**: http://localhost:8002/docs  

- **Marketing**: http://localhost:8003/docs

### Configuración de Entorno

### Herramientas de Administración

#### Variables de Entorno Críticas- **Pulsar Manager**: http://localhost:9527

```bash- **phpMyAdmin**: http://localhost:8082

# MySQL Configuration- **Redis Commander**: http://localhost:8081

MYSQL_ROOT_PASSWORD=alpes

MYSQL_DATABASE=alpes### Health Checks

MYSQL_USER=alpes- **Afiliados**: http://localhost:8001/health

MYSQL_PASSWORD=alpes- **Conversiones**: http://localhost:8002/health

- **Marketing**: http://localhost:8003/health

# Pulsar Configuration

PULSAR_MEM="-Xms512m -Xmx512m -XX:MaxDirectMemorySize=256m"## 📊 Monitoreo en Tiempo Real



# Service Ports```bash

AFILIADOS_PORT=8001# Dashboard interactivo de Pulsar

CONVERSIONES_PORT=8002./scripts/monitor_pulsar.sh dashboard

MARKETING_PORT=8003

```# Logging continuo de eventos

./scripts/monitor_pulsar.sh log

#### Puertos y Servicios

| Servicio | Puerto | URL | Descripción |# Ver logs de servicios

|----------|--------|-----|-------------|docker-compose logs -f

| Afiliados API | 8001 | http://localhost:8001 | Gestión de afiliados |```

| Conversiones API | 8002 | http://localhost:8002 | Tracking conversiones |

| Marketing API | 8003 | http://localhost:8003 | Campañas y comisiones |## 🧪 Casos de Uso E2E

| Pulsar Manager | 9527 | http://localhost:9527 | Administración Pulsar |

| phpMyAdmin | 8082 | http://localhost:8082 | Administración MySQL |### Flujo Completo de Comisión

| Redis Commander | 8081 | http://localhost:8081 | Administración Redis |

```bash

---# 1. Crear afiliado

curl -X POST http://localhost:8001/api/v1/afiliados \

## 🔌 APIs y Endpoints  -H "Content-Type: application/json" \

  -d '{

### Documentación OpenAPI    "nombre": "Juan Pérez",

    "email": "juan@email.com",

Cada microservicio expone documentación interactiva Swagger:    "tipo_afiliado": "premium",

    "configuracion_comisiones": {

- **Afiliados**: http://localhost:8001/docs      "comision_base": 15.0,

- **Conversiones**: http://localhost:8002/docs        "comision_premium": 20.0

- **Marketing**: http://localhost:8003/docs    }

  }'

### Endpoints Principales

# 2. Registrar conversión  

#### 👥 Afiliados API (Puerto 8001)curl -X POST http://localhost:8002/api/v1/conversiones \

  -H "Content-Type: application/json" \

```bash  -d '{

# Registrar nuevo afiliado    "afiliado_id": "af_123",

curl -X POST http://localhost:8001/afiliados \    "valor_conversion": 100000.0,

  -H "Content-Type: application/json" \    "tipo_conversion": "venta"

  -d '{  }'

    "nombre": "Juan Pérez",

    "email": "juan@example.com",# 3. Crear y aprobar comisión (automático vía eventos)

    "telefono": "+57300123456",curl -X POST http://localhost:8003/api/v1/comisiones \

    "tipo_afiliacion": "premium",  -H "Content-Type: application/json" \

    "comision_base": 15.0  -d '{

  }'    "afiliado_id": "af_123",

    "conversion_id": "conv_456",

# Listar todos los afiliados    "tipo_comision": "porcentual",

curl http://localhost:8001/afiliados    "porcentaje": 15.0

  }'

# Obtener afiliado específico```

curl http://localhost:8001/afiliados/{afiliado_id}

## 📚 Documentación Completa

# Actualizar configuración de afiliado

curl -X PUT http://localhost:8001/afiliados/{afiliado_id} \- **[Documentación del Ecosistema](ECOSYSTEM_DOCS.md)**: Guía completa con APIs, eventos, deployment y troubleshooting

  -H "Content-Type: application/json" \- **[Context Map](CONTEXT_MAP.md)**: Mapeo de bounded contexts y relaciones

  -d '{"comision_base": 20.0}'- **Scripts**: Ver carpeta `/scripts/` para herramientas de automatización

```

## 🛠️ Scripts Disponibles

#### 📊 Conversiones API (Puerto 8002)

| Script | Descripción |

```bash|--------|-------------|

# Registrar nueva conversión| `run_full_ecosystem.sh` | 🚀 Ejecución completa del ecosistema |

curl -X POST http://localhost:8002/conversiones \| `setup_pulsar_topics.sh` | 📡 Configuración de tópicos Pulsar |

  -H "Content-Type: application/json" \| `init_test_data.sh` | 🗄️ Poblado de datos de prueba |

  -d '{| `run_e2e_tests.sh` | 🧪 Casos de prueba E2E |

    "afiliado_id": "af_123",| `monitor_pulsar.sh` | 📊 Monitoreo en tiempo real |

    "campana_id": "camp_456", 

    "valor_conversion": 250.00,## 📈 Métricas y Reportes

    "moneda": "USD",

    "metadata": {Después de la ejecución, revisa:

      "source": "website",- `test_data_ids.json`: IDs de entidades creadas

      "user_id": "user_789"- `e2e_test_report.json`: Reporte de pruebas E2E

    }- `performance_report.json`: Métricas de rendimiento

  }'

## 🛑 Detener el Ecosistema

# Obtener conversiones por afiliado

curl http://localhost:8002/conversiones/afiliado/{afiliado_id}```bash

# Parar servicios

# Métricas de conversionesdocker-compose down

curl http://localhost:8002/conversiones/metricas?fecha_inicio=2024-01-01&fecha_fin=2024-12-31

# Parar y limpiar volúmenes

# Analytics detalladodocker-compose down -v

curl http://localhost:8002/analytics/dashboard```

```

## 🔧 Requisitos del Sistema

#### 🎯 Marketing API (Puerto 8003)

- **Docker**: >= 20.10

```bash- **Docker Compose**: >= 2.0

# Crear nueva campaña- **RAM**: 8GB recomendado

curl -X POST http://localhost:8003/campanas \- **CPU**: 4 cores recomendado

  -H "Content-Type: application/json" \- **Disco**: 10GB disponibles

  -d '{

    "nombre": "Campaña Q4 2024",## 🤝 Contribución

    "descripcion": "Campaña promocional fin de año",

    "fecha_inicio": "2024-10-01",1. Fork el repositorio

    "fecha_fin": "2024-12-31",2. Crea tu rama de feature (`git checkout -b feature/AmazingFeature`)

    "presupuesto": 50000.00,3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)

    "meta_conversiones": 1000,4. Push a la rama (`git push origin feature/AmazingFeature`)

    "tipo_campana": "digital",5. Abre un Pull Request

    "estado": "activa",

    "afiliados": [## 📄 Licencia

      {"id": "af_123", "nombre": "Afiliado Premium"},

      {"id": "af_456", "nombre": "Afiliado Standard"}Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

    ],

    "porcentaje_comision": 15.0---

  }'

*🚀 AlpesPartner Ecosystem - Microservicios con Event-Driven Architecture*

# Listar campañas- **CDC**: Simulador manual (Debezium alternativo)

curl http://localhost:8003/campanas

## 🏗️ Arqutectura

# Gestión de comisiones

curl http://localhost:8003/comisiones/pendientes```

curl -X POST http://localhost:8003/comisiones/{comision_id}/aprobar┌─────────┐    HTTP    ┌─────────┐    INSERT    ┌─────────┐    CDC    ┌─────────┐

curl -X POST http://localhost:8003/comisiones/{comision_id}/procesar_pago│ Cliente │ ────────> │   API   │ ──────────> │  MySQL  │ ────────> │ Pulsar  │

```└─────────┘           └─────────┘              └─────────┘           └─────────┘

                                                    │

### Health Checks y Monitoring                                              [outbox_event]

                                               published: 0→1

```bash```

# Health checks

curl http://localhost:8001/health## ⚡ Inicio Rápido

curl http://localhost:8002/health  

curl http://localhost:8003/health### 1. **Clonar y ejecutar**

```bash

# Métricas internasgit clone <repo-url>

curl http://localhost:8003/metricscd alpesPartner

curl http://localhost:8003/debug/outbox

# Levantar todos los servicios

# Status de eventosdocker-compose up --build -d

curl http://localhost:8003/eventos/status```

```

### 2. **Verificar servicios**

---```bash

docker-compose ps

## 📊 Monitoreo y Observabilidad# Debe mostrar: api, mysql, pulsar funcionando

```

### Herramientas de Monitoreo Incluidas

### 3. **Ejecutar pruebas automáticas**

#### 1. **Monitor de Escenarios Completo**```bash

```bash./test-cdc-complete.sh

# Ejecutar monitoreo integral```

python monitor_escenarios_completo.py

## 🔧 Endpoints API

# Funcionalidades:

# - Generación automática de campañas de prueba| Método | Endpoint | Descripción |

# - Simulación de conversiones realistas|--------|----------|-------------|

# - Cálculo automático de comisiones| `GET` | `/health` | Estado de la API |

# - Verificación de flujo completo| `POST` | `/commissions/calculate` | Calcular comisión |

# - Reporte de métricas en tiempo real| `POST` | `/commissions/approve` | Aprobar comisión |

```| `GET` | `/debug/outbox` | Ver eventos en outbox |



#### 2. **Monitoreo de Tópicos Pulsar**## 📊 Ejemplo de Uso

```bash

# Monitorear todos los tópicos en tiempo real### Crear comisión:

python monitor_topicos.py```bash

curl -X POST http://localhost:5001/commissions/calculate \

# Ver estadísticas específicas de un tópico  -H "Content-Type: application/json" \

docker exec -it alpes-pulsar bin/pulsar-admin topics stats persistent://public/default/marketing.eventos  -d '{

```    "conversionId": "conv-001",

    "affiliateId": "aff-123",

#### 3. **Dashboard de Administración**    "campaignId": "camp-456",

    "grossAmount": 1000.00,

**Pulsar Manager** (http://localhost:9527):    "currency": "USD"

- Gestión de tópicos y subscriptions  }'

- Métricas de throughput y latencia```

- Monitoreo de consumers y producers

- Configuración de políticas de retención### Verificar eventos:

```bash

**phpMyAdmin** (http://localhost:8082):curl http://localhost:5001/debug/outbox

- Consultas SQL directas```

- Monitoreo de transacciones

- Análisis de performance de queries## 🎯 Flujo CDC Manual

- Gestión de índices

1. **Crear evento** → Se inserta en `outbox_event` con `published=0`

### Comandos de Monitoreo Útiles2. **Ejecutar CDC** → `python manual_cdc.py` procesa eventos pendientes

3. **Verificar Pulsar** → Eventos aparecen en topic `outbox-events`

#### Ver Eventos en Tiempo Real4. **Consumir** → `python consumer_cdc.py` lee eventos de Pulsar

```bash

# Consumir eventos de marketing## 🧪 Scripts de Prueba

docker exec -it alpes-pulsar bin/pulsar-client consume marketing.eventos -s monitor -n 0

- `test-cdc-complete.sh` - Prueba completa del flujo CDC

# Consumir eventos de comisiones  - `manual_cdc.py` - Simulador CDC manual

docker exec -it alpes-pulsar bin/pulsar-client consume comisiones.eventos -s monitor -n 0- `consumer_cdc.py` - Consumidor de eventos

- `advanced_cdc_test.py` - Pruebas avanzadas con múltiples eventos

# Consumir eventos del sistema

docker exec -it alpes-pulsar bin/pulsar-client consume sistema.eventos -s monitor -n 0## 📂 Estructura Simplificada

```

```

#### Métricas de PerformancealpesPartner/

```bash├── docker-compose.yml     # Orquestación completa

# Estadísticas de tópicos├── Dockerfile            # API Flask

docker exec -it alpes-pulsar bin/pulsar-admin topics list public/default├── api_simple.py         # API principal

├── requirements.txt      # Dependencias Python

# Información detallada de subscriptions├── manual_cdc.py         # Procesador CDC

docker exec -it alpes-pulsar bin/pulsar-admin topics subscriptions persistent://public/default/marketing.eventos├── consumer_cdc.py       # Consumidor eventos

├── test-cdc-complete.sh  # Pruebas automáticas

# Backlog de mensajes pendientes└── db/init.sql          # Schema inicial

docker exec -it alpes-pulsar bin/pulsar-admin topics stats-internal persistent://public/default/marketing.eventos```

```

## 🔍 Monitoreo en Tiempo Real

#### Logs de Aplicación

```bash### Ver eventos en Pulsar:

# Logs de todos los servicios```bash

docker-compose logs -fdocker exec alpespartner-pulsar-1 bin/pulsar-client consume \

  persistent://public/default/outbox-events -s live -n 0 -p Earliest

# Logs específicos por servicio```

docker-compose logs -f alpes-marketing

docker-compose logs -f alpes-afiliados  ### Ver tabla outbox:

docker-compose logs -f alpes-conversiones```bash

docker exec alpespartner-mysql-1 mysql -u alpes -palpes \

# Logs de Pulsar  -e "SELECT * FROM outbox_event ORDER BY occurred_at DESC LIMIT 5;" alpes

docker-compose logs -f alpes-pulsar```

```

### Logs de la API:

---```bash

docker logs -f alpespartner-api-1

## 🧪 Pruebas y Validación```



### Suite de Pruebas Automatizadas## ✅ Verificación de Estado



#### 1. **Pruebas End-to-End Completas**1. **Servicios activos**: `docker-compose ps`

```bash2. **API funcionando**: `curl http://localhost:5001/health`

# Ejecutar suite completa de pruebas3. **Base datos**: `docker exec alpespartner-mysql-1 mysql -u alpes -palpes -e "SHOW TABLES;" alpes`

./scripts/run_e2e_tests.sh4. **Pulsar topics**: `docker exec alpespartner-pulsar-1 bin/pulsar-admin topics list public/default`



# Incluye:## 🛠️ Troubleshooting

# ✅ Validación de health checks

# ✅ Creación de campañas end-to-end- **API no responde**: Verificar `docker logs alpespartner-api-1`

# ✅ Registro y gestión de afiliados- **MySQL no conecta**: Esperar ~30s después de `docker-compose up`

# ✅ Procesamiento de conversiones- **Sin eventos CDC**: Ejecutar `python manual_cdc.py` manualmente

# ✅ Cálculo automático de comisiones- **Pulsar no funciona**: Verificar puertos 6650 y 8080 libres

# ✅ Verificación de eventos Pulsar

# ✅ Pruebas de consistencia eventual## 📈 Resultados Esperados

```

✅ Comisiones se crean correctamente  

#### 2. **Pruebas de Integración de Microservicios**✅ Eventos se insertan en `outbox_event`  

```bash✅ CDC procesa eventos (`published: 0→1`)  

# Demo de integración completa✅ Eventos llegan a Pulsar topic  

python demo_integracion_microservicios.py✅ Consumidores reciben eventos en tiempo real



# Valida:---

# - Comunicación entre servicios

# - Procesamiento de eventos**🎉 ¡Sistema CDC funcionando completamente!**

# - Consistencia de datos- **CQS**: consultas HTTP leen directamente de MySQL (no pasan por Pulsar).

# - Manejo de errores

```---



#### 3. **Pruebas de Escenarios de Calidad****🎉 ¡Sistema CDC funcionando completamente!**

```bash

# Ejecutar escenarios de calidad específicos---

python test_escenarios_calidad.py

## ⚙️ Requisitos

# Escenarios incluidos:

# - Alta disponibilidad con fallas simuladas- Docker y Docker Compose

# - Escalabilidad bajo carga- `uuidgen` (en macOS/Linux) y `jq` (opcional para formatear JSON)

# - Consistencia eventual

# - Recovery automático---

```

## 🚀 Despliegue desde cero

### Validación Manual de Funcionalidades

> Este procedimiento **borra** datos previos.

#### Flujo Completo de Negocio

```bash1) **Apagar y limpiar** (si hay algo corriendo):

# 1. Crear campaña```bash

CAMP_ID=$(curl -s -X POST http://localhost:8003/campanas \docker compose down -v

  -H "Content-Type: application/json" \rm -rf data/*

  -d '{```

    "nombre": "Test Campaign",

    "descripcion": "Campaña de prueba",2) **Construir e iniciar** contenedores:

    "fecha_inicio": "2024-01-01",```bash

    "fecha_fin": "2024-12-31", docker compose build --no-cache

    "presupuesto": 10000,docker compose up -d

    "meta_conversiones": 100,docker compose ps

    "tipo_campana": "digital",```

    "estado": "activa",

    "afiliados": [{"id": "af1", "nombre": "Test Affiliate"}],Deberías ver **mysql**, **pulsar**, **api** activos (y opcionalmente **notificaciones** y **commands** si están en `docker-compose.yml`).

    "porcentaje_comision": 15.0

  }' | jq -r '.id')3) **Verificar MySQL para CDC** (binlog, formato, etc.):

```bash

echo "Campaña creada: $CAMP_ID"docker exec -it $(docker ps -qf name=mysql) mysql -uroot -pdebezium -e "\

SHOW VARIABLES LIKE 'log_bin'; \

# 2. Simular conversiónSHOW VARIABLES LIKE 'binlog_format'; \

curl -X POST http://localhost:8002/conversiones \SHOW VARIABLES LIKE 'binlog_row_image'; \

  -H "Content-Type: application/json" \SHOW VARIABLES LIKE 'server_id';"

  -d "{```

    \"afiliado_id\": \"af1\",

    \"campana_id\": \"$CAMP_ID\",Debe mostrar: `log_bin=ON`, `binlog_format=ROW`, `binlog_row_image=FULL`, `server_id` fijo.

    \"valor_conversion\": 500.00,

    \"moneda\": \"USD\"4) **Crear/actualizar la Source de Debezium en Pulsar**:

  }"> El `NAR` y el `JSON` **ya** están montados en `/pulsar/connectors` dentro del contenedor Pulsar.



# 3. Verificar comisión calculada```bash

sleep 2docker exec -it $(docker ps -qf name=pulsar) bash -lc '\

curl http://localhost:8003/comisiones/pendientes | jq '.'ls -lh /pulsar/connectors && \

bin/pulsar-admin sources delete --tenant public --namespace default --name mysql-outbox-commissions || true && \

# 4. Verificar eventos generadosbin/pulsar-admin sources create \

docker exec -it alpes-pulsar bin/pulsar-client consume sistema.eventos -s test -n 10  --tenant public --namespace default --name mysql-outbox-commissions \

```  --archive /pulsar/connectors/pulsar-io-debezium-mysql-3.1.2.nar \

  --destination-topic-name persistent://public/default/outbox-events \

#### Verificación de Consistencia  --source-config-file /pulsar/connectors/debezium-mysql-outbox.json && \

```bashsleep 2 && \

# Verificar que los eventos se propaguen correctamentebin/pulsar-admin sources status --tenant public --namespace default --name mysql-outbox-commissions'

python consumer_integration_demo.py```



# Monitorear estadísticas en tiempo realSi todo sale bien verá `running: true` y contadores `numReceivedFromSource/numWritten` aumentando cuando haya inserts.

python monitor_estadisticas_real_time.py

```**Contenido de `connectors/pulsar/debezium-mysql-outbox.json` (referencia):**

```json

---{

  "archive": "/pulsar/connectors/pulsar-io-debezium-mysql-3.1.2.nar",

## 🔧 Troubleshooting  "tenant": "public",

  "namespace": "default",

### Problemas Comunes y Soluciones  "name": "mysql-outbox-commissions",

  "topicName": "persistent://public/default/outbox-events",

#### 1. **Servicios no inician correctamente**  "parallelism": 1,

```bash  "configs": {

# Verificar logs de error    "database.hostname": "mysql",

docker-compose logs    "database.port": "3306",

    "database.user": "alpes",

# Verificar puertos ocupados    "database.password": "alpes",

netstat -tulpn | grep :800    "database.server.id": "223344",

    "database.server.name": "alpes-mysql",

# Limpiar y reiniciar

docker-compose down -v    "database.history": "org.apache.pulsar.io.debezium.PulsarDatabaseHistory",

docker-compose up --build -d    "database.history.pulsar.topic": "persistent://public/default/schema-changes.alpes",

```    "database.history.pulsar.service.url": "pulsar://localhost:6650",



#### 2. **Pulsar no conecta**    "database.include.list": "alpes",

```bash    "table.include.list": "alpes.outbox_event",

# Verificar estado de Pulsar

docker exec -it alpes-pulsar bin/pulsar-admin brokers list public    "include.schema.changes": "false",

    "tombstones.on.delete": "false",

# Recrear tópicos    "decimal.handling.mode": "double",

./scripts/setup_pulsar_topics.sh

    "database.allowPublicKeyRetrieval": "true",

# Verificar conectividad    "database.ssl.mode": "disabled",

docker exec -it alpes-pulsar bin/pulsar-client produce test-topic --messages "test"

```    "transforms": "route",

    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",

#### 3. **Base de datos no inicializa**    "transforms.route.regex": "(.*)",

```bash    "transforms.route.replacement": "outbox-events"

# Verificar logs de MySQL  }

docker-compose logs alpes-mysql-marketing}

```

# Recrear volúmenes

docker-compose down -v---

docker volume prune -f

docker-compose up --build -d## 🔌 Endpoints HTTP (API)

```

- **Calcular comisión** (genera outbox en BD):

#### 4. **Eventos no se procesan**```bash

```bashCID=$(uuidgen)

# Verificar consumers activoscurl -s -X POST http://localhost:5001/commissions/calculate \

docker exec -it alpes-pulsar bin/pulsar-admin topics subscriptions persistent://public/default/marketing.eventos  -H 'Content-Type: application/json' \

  -d "{

# Verificar backlog    \"conversionId\":\"$CID\",

docker exec -it alpes-pulsar bin/pulsar-admin topics stats persistent://public/default/marketing.eventos    \"affiliateId\":\"aff-1\",

    \"campaignId\":\"cmp-1\",

# Resetear subscription si es necesario    \"grossAmount\":120.5,

docker exec -it alpes-pulsar bin/pulsar-admin topics reset-cursor persistent://public/default/marketing.eventos -s monitor --reset-to-earliest    \"currency\":\"USD\"

```  }" | tee /tmp/calc.json



### Scripts de DiagnósticoCOMM_ID=$(jq -r .commissionId /tmp/calc.json)

echo "CommissionId -> $COMM_ID"

#### Verificación Completa del Sistema```

```bash

#!/bin/bash- **Aprobar comisión** (genera outbox en BD):

echo "🔍 Diagnóstico del Sistema AlpesPartner"```bash

echo "======================================"curl -s -X POST http://localhost:5001/commissions/approve \

  -H 'Content-Type: application/json' \

# Health checks  -d "{\"commissionId\":\"$COMM_ID\"}"

echo "1. Verificando health de servicios..."```

for port in 8001 8002 8003; do

  status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health)- **Consulta por conversión** (CQS directo a BD):

  echo "   Puerto $port: $status"```bash

donecurl -s http://localhost:5001/commissions/by-conversion/$CID | jq .

```

# Docker containers

echo "2. Estado de contenedores..."---

docker-compose ps

## 🔭 Cómo observar **en vivo**

# Pulsar topics

echo "3. Tópicos Pulsar..."**Terminal A – Logs del Source Debezium en Pulsar**

docker exec -it alpes-pulsar bin/pulsar-admin topics list public/default```bash

docker exec -it $(docker ps -qf name=pulsar) bash -lc "\

# Database connectionstail -f logs/functions/public/default/mysql-outbox-commissions/mysql-outbox-commissions-0.log"

echo "4. Conexiones de base de datos..."```

docker exec -it alpes-mysql-marketing mysqladmin -u alpes -palpes ping

**Terminal B – Consumir eventos desde Pulsar**  

echo "✅ Diagnóstico completado"_Te recomiendo ver **ambos** tópicos durante la demo:_

``````bash

# 1) Tópico "enrutado" (target) por la RegexRouter

### Contacto y Soportedocker exec -it $(docker ps -qf name=pulsar) \

  bin/pulsar-client consume persistent://public/default/outbox-events \

Para problemas específicos:  -s "live-outbox" -n 0 -p Earliest



1. **Logs**: Siempre incluir logs relevantes usando `docker-compose logs`# 2) Tópico "crudo" (nombre Debezium por server.db.table) -- en este topico se puede identificar los eventos totales, es necesario identificarlo como principal

2. **Configuración**: Verificar variables de entorno y configuracionesdocker exec -it $(docker ps -qf name=pulsar) \

3. **Documentación**: Consultar documentación técnica en `ECOSYSTEM_DOCS.md`  bin/pulsar-client consume persistent://public/default/alpes-mysql.alpes.outbox_event \

4. **Issues**: Reportar problemas con pasos para reproducir  -s "live-raw" -n 0 -p Earliest

```

---

**Terminal C – Logs del servicio de Notificaciones**

## 📚 Referencias Adicionales```bash

docker logs -f $(docker ps -qf name=notificaciones)

- **CONTEXT_MAP.md**: Mapa de contextos y bounded contexts# También puedes ver el archivo generado por el suscriptor:

- **ECOSYSTEM_DOCS.md**: Documentación técnica detallada  tail -n 50 data/events.jsonl

- **REPORTE_ARQUITECTURA.md**: Análisis y decisiones arquitectónicas```



---**Terminal D – (Opcional) consumidor de comandos**

```bash

*🚀 AlpesPartner Ecosystem - Microservicios Enterprise con Event-Driven Architecture*docker logs -f $(docker ps -qf name=commands)

```

**Versión**: 2.0.0  

**Última actualización**: Septiembre 2024  ---

**Mantenido por**: Equipo AlpesPartner
## 🔁 Flujo interno por endpoint (qué archivos toca)

1) **POST /commissions/calculate**
   - `src/alpespartner/api/app.py` recibe el request y crea un `CrearComision`.
   - `seedwork/aplicacion/mediador.py` despacha el comando al handler.
   - `modulos/comisiones/aplicacion/comandos/crear_comision.py` llama a
     `modulos/comisiones/aplicacion/servicios/servicio_comisiones.py#calcular`.
   - El servicio abre un **Unit of Work** (`seedwork/infraestructura/uow.py`), guarda la entidad **Commission**
     y **apendea** un registro en `alpes.outbox_event` (dentro de la misma transacción).
   - Se hace `commit()` → **Debezium** detecta el insert en `outbox_event` y publica en Pulsar.
   - La **respuesta** HTTP devuelve `commissionId`.

2) **POST /commissions/approve**
   - Flujo análogo:
     `app.py` → `mediador.py` → `aprobar_comision.py` → `servicio_comisiones.py#aprobar`
     → `UPDATE` de la comisión + **insert outbox** → Debezium → Pulsar.

3) **GET /commissions/by-conversion/{id}**
   - Capa de consulta (**CQS**) que lee **directo** de MySQL y regresa los campos normalizados.

> En código verás **decoradores** y objetos de dominio/DTOs que encapsulan validaciones y orquestación.
> El **Outbox** asegura consistencia eventual (escribe en la misma transacción de la operación de negocio).

---

## ✅ Escenarios de calidad a probar

- **Consistencia eventual**: el mensaje llega a Pulsar después del commit.
- **Idempotencia en dominio**: `conversion_id` único evita duplicados (ver error 1062).
- **Resiliencia**: reiniciar la `source` conserva `offsets` (replay desde `mysql-outbox-commissions-debezium-offset-topic`).
- **Backpressure**: observar métricas de producer/consumer en logs.
- **Tolerancia a fallos externos**: si Pulsar cae, los cambios quedan en BD y se publican al volver la `source`.
- **Auditoría**: `data/events.jsonl` (suscriptor) como rastro de lo publicado.

---

## 🧪 Pruebas de punta a punta (script sugerido)

1) **Reset BD/tablas** (opcional en ambientes de demo):
```bash
docker exec -it $(docker ps -qf name=mysql) mysql -uroot -pdebezium -e "\
SET FOREIGN_KEY_CHECKS=0; \
TRUNCATE TABLE alpes.outbox_event; \
TRUNCATE TABLE alpes.commission; \
SET FOREIGN_KEY_CHECKS=1; \
SELECT COUNT(*) AS outbox, (SELECT COUNT(*) FROM alpes.commission) AS commissions FROM alpes.outbox_event;"
```

2) **Calcular → Aprobar → Consultar** (ver sección Endpoints).
3) **Verificar en Pulsar** (Terminal B) que llegaron **2** eventos (calculate/approve).
4) **Verificar en Notificaciones**: `tail -n 50 data/events.jsonl`.

---

## 🧰 Troubleshooting

- **No aparecen mensajes en Pulsar**
  - Revisa estado:  
    `docker exec -it $(docker ps -qf name=pulsar) bin/pulsar-admin sources status --tenant public --namespace default --name mysql-outbox-commissions`
  - Reinicia instancia:  
    `docker exec -it $(docker ps -qf name=pulsar) bash -lc "bin/pulsar-admin sources restart --tenant public --namespace default --name mysql-outbox-commissions --instance-id 0"`
  - Consume desde **Earliest** y usa una **nueva** suscripción (`-s ...` distinto).
  - Verifica binlog en MySQL (sección despliegue).

- **Error 1062 Duplicate entry ... `commission.conversion_id`**
  - Es **intencional**: garantiza idempotencia por conversión. Usa un `CID` nuevo o vacía tablas (script arriba).

- **`ClassNotFound: PulsarDatabaseHistory`**
  - Asegúrate de usar `database.history = org.apache.pulsar.io.debezium.PulsarDatabaseHistory`
    (¡sin `.mysql.` en el paquete!).

- **API no levanta en 5001**
  - `docker compose logs -f api`
  - Confirma puerto mapeado `5001:5000` en `docker-compose.yml`.

---

## 🧹 Apagar / limpiar

```bash
docker compose down -v
rm -rf data/*
```

Esto elimina contenedores, volúmenes (incluye offsets y topics locales del standalone) y archivos de demo.

---

## 📌 Referencias rápidas

- **Listar tópicos**:
  ```bash
  docker exec -it $(docker ps -qf name=pulsar) bin/pulsar-admin topics list public/default
  ```

- **Ver Source + logs**:
  ```bash
  docker exec -it $(docker ps -qf name=pulsar) \
    bash -lc "bin/pulsar-admin sources status --tenant public --namespace default --name mysql-outbox-commissions && \
              tail -n 200 logs/functions/public/default/mysql-outbox-commissions/mysql-outbox-commissions-0.log"
  ```

- **Consumir un tópico**:
  ```bash
  docker exec -it $(docker ps -qf name=pulsar) \
    bin/pulsar-client consume persistent://public/default/outbox-events -s debug -n 0 -p Earliest
  ```

---

## 🗒️ Notas finales

- Este PoC está optimizado para **ambiente local** (Pulsar standalone, MySQL sin TLS).
