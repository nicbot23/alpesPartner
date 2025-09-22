# AlpesPartner Docker Compose

Este archivo contiene la configuración **completamente autónoma** de Docker Compose para los microservicios de AlpesPartner, incluyendo toda la infraestructura necesaria.

## Prerequisitos

**NINGUNO** - Este docker-compose es completamente autónomo e incluye:
- ✅ **Apache Pulsar completo** (Zookeeper, Bookie, Broker, Pulsar-init)
- ✅ **MySQL 8** para persistencia
- ✅ **Redes independientes**
- ✅ **Volúmenes persistentes**

## Infraestructura incluida

### 🚀 Apache Pulsar Stack
- **Zookeeper**: Coordinación distribuida (puerto interno)
- **Bookie**: Almacenamiento de logs (puerto interno)  
- **Broker**: Broker de mensajes (puertos 6650, 8080)
- **Pulsar-init**: Inicialización del clúster (automático)

### 🗄️ Base de Datos
- **MySQL 8**: Puerto 3307 (para evitar conflictos con MySQL local)
- **Usuario**: `alpespartner` / `alpespartner123`
- **Base de datos**: `alpespartner`
- **Inicialización**: Automática con esquemas y datos de ejemplo

## Uso

### Levantar TODO el sistema (infraestructura + microservicios)
```bash
docker-compose -f docker-compose-alpespartner.yml --profile alpespartner up --build
```

### Levantar solo infraestructura
```bash
docker-compose -f docker-compose-alpespartner.yml --profile infrastructure up -d
```

### Levantar servicios específicos
```bash
# Solo BFF y campanias (requiere infraestructura)
docker-compose -f docker-compose-alpespartner.yml --profile infrastructure --profile bff --profile campanias up --build

# Solo Pulsar
docker-compose -f docker-compose-alpespartner.yml --profile pulsar up -d

# Solo Base de datos
docker-compose -f docker-compose-alpespartner.yml --profile database up -d
```

### Reconstruir servicios
```bash
docker-compose -f docker-compose-alpespartner.yml build --no-cache
```

## Puertos y Servicios

### 🌐 Infraestructura
- **Pulsar Broker**: http://localhost:8080 (Admin UI), pulsar://localhost:6650 (Cliente)
- **MySQL**: localhost:3307 (usuario: `alpespartner`, password: `alpespartner123`)

### 🏗️ Microservicios AlpesPartner
- **BFF**: http://localhost:8001 - API Gateway y orquestador
- **campanias**: http://localhost:8002 - Gestión de campanias de marketing
- **Afiliados**: http://localhost:8003 - Gestión de afiliados
- **Comisiones**: http://localhost:8004 - Cálculo de comisiones
- **Conversiones**: http://localhost:8005 - Tracking de conversiones
- **Notificaciones**: http://localhost:8006 - Sistema de notificaciones
- **Sagas**: http://localhost:8007 - Coordinador de sagas distribuidas

### 📚 Documentación API
Cada servicio expone su documentación en `/docs`:
- http://localhost:8001/docs (BFF)
- http://localhost:8002/docs (campanias)
- etc.

## Base de Datos

### 🔗 Conexión
```
Host: localhost:3307
Usuario: alpespartner
Password: alpespartner123
Base de datos: alpespartner
```

### 📊 Esquema
- **campanias**: Gestión de campanias
- **afiliados**: Información de afiliados
- **comisiones**: Registro de comisiones
- **conversiones**: Tracking de conversiones
- **notificaciones**: Cola de notificaciones
- **sagas**: Estado de sagas distribuidas

### 🧪 Datos de ejemplo
El sistema incluye datos de ejemplo para pruebas inmediatas.

## Logs

```bash
# Ver logs de todos los servicios
docker-compose -f docker-compose-alpespartner.yml logs -f

# Ver logs de un servicio específico
docker-compose -f docker-compose-alpespartner.yml logs -f bff
docker-compose -f docker-compose-alpespartner.yml logs -f campanias
```

## Arquitectura

### 📡 Comunicación
- **Comandos**: Vía eventos en Pulsar (async, resiliente)
- **Consultas**: Vía HTTP REST (rápido, directo)

### 🔗 Redes
- **pulsar**: Red interna para infraestructura Pulsar (Zookeeper, Bookie, Broker)
- **alpespartner**: Red para comunicación HTTP entre microservicios

### 🎯 Temas de Pulsar
- `comando-lanzar-campania-completa`: BFF → campanias
- `comando-cancelar-saga`: BFF → campanias  
- `eventos-campania`: campanias → Otros servicios
- `eventos-afiliado`: Afiliados → Otros servicios
- `eventos-comision`: Comisiones → Otros servicios
- `eventos-conversion`: Conversiones → Otros servicios
- `eventos-notificacion`: Notificaciones → Otros servicios

### 💾 Persistencia
- **MySQL 8**: Base de datos relacional para todos los microservicios
- **Volúmenes persistentes**: Datos se conservan entre reinicios

## Desarrollo

### 🔄 Hot Reload
Los volúmenes están configurados para desarrollo con recarga automática:
- Cambios en el código se reflejan inmediatamente
- No necesitas reconstruir la imagen para cambios de código
- Solo reconstruye si cambias dependencias (requirements.txt)

### 🐛 Debug
```bash
# Ver logs de todos los servicios
docker-compose -f docker-compose-alpespartner.yml logs -f

# Ver logs de un servicio específico
docker-compose -f docker-compose-alpespartner.yml logs -f bff
docker-compose -f docker-compose-alpespartner.yml logs -f campanias

# Ver logs de infraestructura
docker-compose -f docker-compose-alpespartner.yml logs -f broker
docker-compose -f docker-compose-alpespartner.yml logs -f alpespartner-db
```

## Desarrollo

Los volúmenes están configurados para desarrollo con recarga automática:
- Cambios en el código se reflejan inmediatamente
- No necesitas reconstruir la imagen para cambios de código
- Solo reconstruye si cambias dependencias (requirements.txt)

## Troubleshooting

### ❌ Error: MySQL no conecta
```bash
# Verificar que MySQL está corriendo
docker-compose -f docker-compose-alpespartner.yml ps alpespartner-db

# Ver logs de MySQL
docker-compose -f docker-compose-alpespartner.yml logs alpespartner-db

# Conectar manualmente para probar
mysql -h localhost -P 3307 -u alpespartner -p
```

### ❌ Error: Pulsar no disponible
```bash
# Verificar que broker está corriendo
docker-compose -f docker-compose-alpespartner.yml ps broker

# Ver logs del broker
docker-compose -f docker-compose-alpespartner.yml logs broker

# Verificar estado del clúster
curl http://localhost:8080/admin/v2/clusters
```

### ❌ Puerto ya en uso
```bash
# Verificar qué usa el puerto
lsof -i :8001
lsof -i :3307
lsof -i :6650

# Matar proceso si es necesario
kill -9 <PID>
```

### ❌ Volúmenes corruptos
```bash
# Eliminar volúmenes y recrear (CUIDADO: borra datos)
docker-compose -f docker-compose-alpespartner.yml down -v
docker volume prune
```

### ❌ Servicios no se conectan entre sí
```bash
# Verificar redes
docker network ls | grep alpespartner

# Inspeccionar red
docker network inspect tutorial-8-sagas_alpespartner

# Verificar que servicios están en la red correcta
docker-compose -f docker-compose-alpespartner.yml ps
```

## Comandos útiles

```bash
# Parar todo
docker-compose -f docker-compose-alpespartner.yml down

# Parar y eliminar volúmenes
docker-compose -f docker-compose-alpespartner.yml down -v

# Reconstruir solo un servicio
docker-compose -f docker-compose-alpespartner.yml build bff

# Escalar un servicio (ej: 3 instancias de BFF)
docker-compose -f docker-compose-alpespartner.yml up --scale bff=3

# Entrar a un contenedor
docker exec -it alpespartner-bff bash
docker exec -it alpespartner-mysql mysql -u alpespartner -p
```