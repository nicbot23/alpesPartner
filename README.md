docker-compose -f docker-compose-alpespartner.yml --profile alpespartner up --build
docker-compose -f docker-compose-alpespartner.yml --profile infrastructure up -d
docker-compose -f docker-compose-alpespartner.yml --profile infrastructure --profile bff --profile campanias up --build
docker-compose -f docker-compose-alpespartner.yml --profile pulsar up -d
docker-compose -f docker-compose-alpespartner.yml --profile database up -d
docker-compose -f docker-compose-alpespartner.yml build --no-cache


# ✨ Bienvenido a AlpesPartner

<p align="center">
	<img src="https://user-images.githubusercontent.com/123456789/partner-logo.png" alt="AlpesPartner Logo" width="180"/>
</p>

<p align="center">
	<b>Microservicios | Eventos | Sagas | Docker | Pulsar | MySQL</b>
</p>

---

AlpesPartner es una plataforma modular para la gestión de campañas, afiliados, comisiones y conversiones, basada en microservicios y comunicación asíncrona con Apache Pulsar. ¡Despliega, explora y prueba todo el flujo de negocio en minutos!

---


## 🚦 Pasos Rápidos para Empezar

<ol>
	<li><b>Instala Docker y Docker Compose</b></li>
	<li><b>Clona el repositorio y navega al proyecto</b></li>
	<li><b>Levanta toda la infraestructura y microservicios</b></li>
	<li><b>Accede a la documentación interactiva de APIs</b></li>
	<li><b>Prueba los endpoints con Postman o curl</b></li>
	<li><b>Verifica los eventos y la persistencia</b></li>
</ol>

---

docker-compose -f docker-compose-alpespartner.yml --profile alpespartner up --build
docker-compose -f docker-compose-alpespartner.yml ps

## 🚀 Despliegue Completo

<details>
<summary><b>Desplegar todo el sistema (infraestructura + microservicios)</b></summary>

```bash
docker-compose -f docker-compose-alpespartner.yml --profile alpespartner up --build
```
</details>

<details>
<summary><b>Verificar servicios activos</b></summary>

```bash
docker-compose -f docker-compose-alpespartner.yml ps
```
</details>

---


## 📚 Documentación Interactiva

Accede a la documentación Swagger de cada microservicio en `/docs`:

| Servicio        | URL                              |
|-----------------|----------------------------------|
| BFF             | http://localhost:8001/docs       |
| Campañas        | http://localhost:8002/docs       |
| Afiliados       | http://localhost:8003/docs       |
| Comisiones      | http://localhost:8004/docs       |
| Conversiones    | http://localhost:8005/docs       |
| Notificaciones  | http://localhost:8006/docs       |
| Sagas           | http://localhost:8007/docs       |

---


## 🧪 Pruebas End-to-End: BFF y Sagas de Campañas

### 1. Probar el BFF

<details>
<summary><b>Crear una campaña desde el BFF (curl)</b></summary>

```bash
curl -X POST http://localhost:8001/campanias \
	-H "Content-Type: application/json" \
	-d '{
		"nombre": "Campaña Demo",
		"descripcion": "Prueba end-to-end",
		"fecha_inicio": "2025-09-22",
		"fecha_fin": "2025-09-30",
		"presupuesto": 10000,
		"comision_porcentaje": 0.10
	}'
```

<b>Respuesta esperada:</b>
```json
{
	"correlation_id": "bff-uuid-generado",
	"status": "procesando"
}
```
</details>

### 2. Probar Sagas de Campañas

<details>
<summary><b>Lanzar una saga de campaña (curl)</b></summary>

```bash
curl -X POST http://localhost:8007/sagas/campanias \
	-H "Content-Type: application/json" \
	-d '{
		"nombre": "Campaña Saga",
		"descripcion": "Saga de prueba",
		"fecha_inicio": "2025-09-22",
		"fecha_fin": "2025-09-30",
		"presupuesto": 20000,
		"comision_porcentaje": 0.15
	}'
```

<b>Respuesta esperada:</b>
```json
{
	"saga_id": "saga-uuid-generado",
	"estado": "iniciada",
	"mensaje": "Saga lanzada correctamente"
}
```
</details>

### 3. Usar Colecciones Postman

Importa los archivos de la carpeta <b>collections/</b> en Postman para probar todos los endpoints de BFF y Campañas, incluyendo flujos de saga y verificación de eventos.

---

### 4. Verificar eventos y persistencia

<details>
<summary><b>Ver eventos en Pulsar</b></summary>

```bash
# Eventos de campañas
docker exec -it <pulsar-container-name> bin/pulsar-client consume \
	"persistent://public/default/eventos-campania" -s "test-sub" -p Earliest -n 10

# Eventos de comisiones
docker exec -it <pulsar-container-name> bin/pulsar-client consume \
	"persistent://public/default/eventos-comision" -s "test-sub" -p Earliest -n 10
```
</details>

<details>
<summary><b>Verificar persistencia en MySQL</b></summary>

```bash
docker exec -it <mysql-container-name> mysql -u alpespartner -palpespartner123 -D alpespartner \
	-e "SELECT * FROM campanias ORDER BY creada_en DESC LIMIT 5;"
```
</details>

---


## 🌈 Experiencia de Usuario

<p align="center">
	<img src="https://user-images.githubusercontent.com/123456789/flow-diagram.png" alt="Flujo de Campañas" width="600"/>
</p>

Sigue los pasos de la guía y explora la documentación interactiva para entender el flujo completo:

1. Despliega el sistema
2. Prueba la creación de campañas y sagas
3. Verifica los eventos y la persistencia
4. Explora los endpoints y la arquitectura

---

docker-compose -f docker-compose-alpespartner.yml logs -f
docker-compose -f docker-compose-alpespartner.yml logs -f bff
docker-compose -f docker-compose-alpespartner.yml logs -f campanias

## 📝 Logs y Debug

```bash
# Ver logs de todos los servicios
docker-compose -f docker-compose-alpespartner.yml logs -f

# Ver logs de un servicio específico
docker-compose -f docker-compose-alpespartner.yml logs -f bff
docker-compose -f docker-compose-alpespartner.yml logs -f campanias
```

---


## 🛠️ Troubleshooting Rápido

- **MySQL no conecta**: Verifica con `docker-compose ps` y revisa los logs.
- **Pulsar no disponible**: Revisa el estado del broker y los logs.
- **Puerto ocupado**: Usa `lsof -i :<puerto>` y libera el puerto si es necesario.
- **Volúmenes corruptos**: `docker-compose down -v` y `docker volume prune` (borra datos).
- **Servicios no se comunican**: Verifica redes con `docker network ls` y `docker network inspect`.

---

docker-compose -f docker-compose-alpespartner.yml down
docker-compose -f docker-compose-alpespartner.yml build --no-cache
docker exec -it <container-name> bash

## ⚡ Comandos Útiles

```bash
# Parar todo
docker-compose -f docker-compose-alpespartner.yml down

# Reconstruir servicios
docker-compose -f docker-compose-alpespartner.yml build --no-cache

# Entrar a un contenedor
docker exec -it <container-name> bash
```

---


## 🗂️ Estructura de Carpetas Clave

- `src-alpespartner/` - Código fuente de todos los microservicios
- `collections/` - Colecciones Postman para pruebas automáticas
- `README-alpespartner.md` - Esta guía
- `docker-compose-alpespartner.yml` - Infraestructura y servicios

---


## 📖 Recursos y Documentación

- Documentación técnica y de arquitectura: revisa los archivos `docs/`, `README.md`, y los endpoints `/docs` de cada servicio.

---

<p align="center">
	<b>¡Listo! Despliega, prueba y explora AlpesPartner con esta guía. Si tienes dudas, revisa la documentación o los endpoints interactivos.</b>
</p>

**¡Listo! Con estos pasos puedes desplegar, probar y entender el flujo completo de AlpesPartner, desde la creación de campañas hasta la orquestación de sagas y la verificación de eventos y persistencia.**

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