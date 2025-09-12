# 🚀 AlpesPartner - Comisiones con CDC Pattern

Sistema de comisiones usando **Change Data Capture (CDC)** con patrón Outbox para garantizar consistencia transaccional entre base de datos y eventos.

## 📋 Stack Tecnológico

- **API**: Flask (Python)
- **Base de datos**: MySQL 8 con binlog
- **Tabla Outbox**: Para eventos transaccionales
- **Message Broker**: Apache Pulsar 3.1.2
- **CDC**: Simulador manual (Debezium alternativo)

## 🏗️ Arqutectura

```
┌─────────┐    HTTP    ┌─────────┐    INSERT    ┌─────────┐    CDC    ┌─────────┐
│ Cliente │ ────────> │   API   │ ──────────> │  MySQL  │ ────────> │ Pulsar  │
└─────────┘           └─────────┘              └─────────┘           └─────────┘
                                                    │
                                              [outbox_event]
                                               published: 0→1
```

## ⚡ Inicio Rápido

### 1. **Clonar y ejecutar**
```bash
git clone <repo-url>
cd alpesPartner

# Levantar todos los servicios
docker-compose up --build -d
```

### 2. **Verificar servicios**
```bash
docker-compose ps
# Debe mostrar: api, mysql, pulsar funcionando
```

### 3. **Ejecutar pruebas automáticas**
```bash
./test-cdc-complete.sh
```

## 🔧 Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/health` | Estado de la API |
| `POST` | `/commissions/calculate` | Calcular comisión |
| `POST` | `/commissions/approve` | Aprobar comisión |
| `GET` | `/debug/outbox` | Ver eventos en outbox |

## 📊 Ejemplo de Uso

### Crear comisión:
```bash
curl -X POST http://localhost:5001/commissions/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "conversionId": "conv-001",
    "affiliateId": "aff-123",
    "campaignId": "camp-456",
    "grossAmount": 1000.00,
    "currency": "USD"
  }'
```

### Verificar eventos:
```bash
curl http://localhost:5001/debug/outbox
```

## 🎯 Flujo CDC Manual

1. **Crear evento** → Se inserta en `outbox_event` con `published=0`
2. **Ejecutar CDC** → `python manual_cdc.py` procesa eventos pendientes
3. **Verificar Pulsar** → Eventos aparecen en topic `outbox-events`
4. **Consumir** → `python consumer_cdc.py` lee eventos de Pulsar

## 🧪 Scripts de Prueba

- `test-cdc-complete.sh` - Prueba completa del flujo CDC
- `manual_cdc.py` - Simulador CDC manual
- `consumer_cdc.py` - Consumidor de eventos
- `advanced_cdc_test.py` - Pruebas avanzadas con múltiples eventos

## 📂 Estructura Simplificada

```
alpesPartner/
├── docker-compose.yml     # Orquestación completa
├── Dockerfile            # API Flask
├── api_simple.py         # API principal
├── requirements.txt      # Dependencias Python
├── manual_cdc.py         # Procesador CDC
├── consumer_cdc.py       # Consumidor eventos
├── test-cdc-complete.sh  # Pruebas automáticas
└── db/init.sql          # Schema inicial
```

## 🔍 Monitoreo en Tiempo Real

### Ver eventos en Pulsar:
```bash
docker exec alpespartner-pulsar-1 bin/pulsar-client consume \
  persistent://public/default/outbox-events -s live -n 0 -p Earliest
```

### Ver tabla outbox:
```bash
docker exec alpespartner-mysql-1 mysql -u alpes -palpes \
  -e "SELECT * FROM outbox_event ORDER BY occurred_at DESC LIMIT 5;" alpes
```

### Logs de la API:
```bash
docker logs -f alpespartner-api-1
```

## ✅ Verificación de Estado

1. **Servicios activos**: `docker-compose ps`
2. **API funcionando**: `curl http://localhost:5001/health`
3. **Base datos**: `docker exec alpespartner-mysql-1 mysql -u alpes -palpes -e "SHOW TABLES;" alpes`
4. **Pulsar topics**: `docker exec alpespartner-pulsar-1 bin/pulsar-admin topics list public/default`

## 🛠️ Troubleshooting

- **API no responde**: Verificar `docker logs alpespartner-api-1`
- **MySQL no conecta**: Esperar ~30s después de `docker-compose up`
- **Sin eventos CDC**: Ejecutar `python manual_cdc.py` manualmente
- **Pulsar no funciona**: Verificar puertos 6650 y 8080 libres

## 📈 Resultados Esperados

✅ Comisiones se crean correctamente  
✅ Eventos se insertan en `outbox_event`  
✅ CDC procesa eventos (`published: 0→1`)  
✅ Eventos llegan a Pulsar topic  
✅ Consumidores reciben eventos en tiempo real

---

**🎉 ¡Sistema CDC funcionando completamente!**
- **CQS**: consultas HTTP leen directamente de MySQL (no pasan por Pulsar).

---

**🎉 ¡Sistema CDC funcionando completamente!**

---

## ⚙️ Requisitos

- Docker y Docker Compose
- `uuidgen` (en macOS/Linux) y `jq` (opcional para formatear JSON)

---

## 🚀 Despliegue desde cero

> Este procedimiento **borra** datos previos.

1) **Apagar y limpiar** (si hay algo corriendo):
```bash
docker compose down -v
rm -rf data/*
```

2) **Construir e iniciar** contenedores:
```bash
docker compose build --no-cache
docker compose up -d
docker compose ps
```

Deberías ver **mysql**, **pulsar**, **api** activos (y opcionalmente **notificaciones** y **commands** si están en `docker-compose.yml`).

3) **Verificar MySQL para CDC** (binlog, formato, etc.):
```bash
docker exec -it $(docker ps -qf name=mysql) mysql -uroot -pdebezium -e "\
SHOW VARIABLES LIKE 'log_bin'; \
SHOW VARIABLES LIKE 'binlog_format'; \
SHOW VARIABLES LIKE 'binlog_row_image'; \
SHOW VARIABLES LIKE 'server_id';"
```

Debe mostrar: `log_bin=ON`, `binlog_format=ROW`, `binlog_row_image=FULL`, `server_id` fijo.

4) **Crear/actualizar la Source de Debezium en Pulsar**:
> El `NAR` y el `JSON` **ya** están montados en `/pulsar/connectors` dentro del contenedor Pulsar.

```bash
docker exec -it $(docker ps -qf name=pulsar) bash -lc '\
ls -lh /pulsar/connectors && \
bin/pulsar-admin sources delete --tenant public --namespace default --name mysql-outbox-commissions || true && \
bin/pulsar-admin sources create \
  --tenant public --namespace default --name mysql-outbox-commissions \
  --archive /pulsar/connectors/pulsar-io-debezium-mysql-3.1.2.nar \
  --destination-topic-name persistent://public/default/outbox-events \
  --source-config-file /pulsar/connectors/debezium-mysql-outbox.json && \
sleep 2 && \
bin/pulsar-admin sources status --tenant public --namespace default --name mysql-outbox-commissions'
```

Si todo sale bien verá `running: true` y contadores `numReceivedFromSource/numWritten` aumentando cuando haya inserts.

**Contenido de `connectors/pulsar/debezium-mysql-outbox.json` (referencia):**
```json
{
  "archive": "/pulsar/connectors/pulsar-io-debezium-mysql-3.1.2.nar",
  "tenant": "public",
  "namespace": "default",
  "name": "mysql-outbox-commissions",
  "topicName": "persistent://public/default/outbox-events",
  "parallelism": 1,
  "configs": {
    "database.hostname": "mysql",
    "database.port": "3306",
    "database.user": "alpes",
    "database.password": "alpes",
    "database.server.id": "223344",
    "database.server.name": "alpes-mysql",

    "database.history": "org.apache.pulsar.io.debezium.PulsarDatabaseHistory",
    "database.history.pulsar.topic": "persistent://public/default/schema-changes.alpes",
    "database.history.pulsar.service.url": "pulsar://localhost:6650",

    "database.include.list": "alpes",
    "table.include.list": "alpes.outbox_event",

    "include.schema.changes": "false",
    "tombstones.on.delete": "false",
    "decimal.handling.mode": "double",

    "database.allowPublicKeyRetrieval": "true",
    "database.ssl.mode": "disabled",

    "transforms": "route",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "(.*)",
    "transforms.route.replacement": "outbox-events"
  }
}
```

---

## 🔌 Endpoints HTTP (API)

- **Calcular comisión** (genera outbox en BD):
```bash
CID=$(uuidgen)
curl -s -X POST http://localhost:5001/commissions/calculate \
  -H 'Content-Type: application/json' \
  -d "{
    \"conversionId\":\"$CID\",
    \"affiliateId\":\"aff-1\",
    \"campaignId\":\"cmp-1\",
    \"grossAmount\":120.5,
    \"currency\":\"USD\"
  }" | tee /tmp/calc.json

COMM_ID=$(jq -r .commissionId /tmp/calc.json)
echo "CommissionId -> $COMM_ID"
```

- **Aprobar comisión** (genera outbox en BD):
```bash
curl -s -X POST http://localhost:5001/commissions/approve \
  -H 'Content-Type: application/json' \
  -d "{\"commissionId\":\"$COMM_ID\"}"
```

- **Consulta por conversión** (CQS directo a BD):
```bash
curl -s http://localhost:5001/commissions/by-conversion/$CID | jq .
```

---

## 🔭 Cómo observar **en vivo**

**Terminal A – Logs del Source Debezium en Pulsar**
```bash
docker exec -it $(docker ps -qf name=pulsar) bash -lc "\
tail -f logs/functions/public/default/mysql-outbox-commissions/mysql-outbox-commissions-0.log"
```

**Terminal B – Consumir eventos desde Pulsar**  
_Te recomiendo ver **ambos** tópicos durante la demo:_
```bash
# 1) Tópico "enrutado" (target) por la RegexRouter
docker exec -it $(docker ps -qf name=pulsar) \
  bin/pulsar-client consume persistent://public/default/outbox-events \
  -s "live-outbox" -n 0 -p Earliest

# 2) Tópico "crudo" (nombre Debezium por server.db.table) -- en este topico se puede identificar los eventos totales, es necesario identificarlo como principal
docker exec -it $(docker ps -qf name=pulsar) \
  bin/pulsar-client consume persistent://public/default/alpes-mysql.alpes.outbox_event \
  -s "live-raw" -n 0 -p Earliest
```

**Terminal C – Logs del servicio de Notificaciones**
```bash
docker logs -f $(docker ps -qf name=notificaciones)
# También puedes ver el archivo generado por el suscriptor:
tail -n 50 data/events.jsonl
```

**Terminal D – (Opcional) consumidor de comandos**
```bash
docker logs -f $(docker ps -qf name=commands)
```

---

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
