# 🚀 PLAN DE DESPLIEGUE Y VALIDACIÓN - AlpesPartner Microservicios

## 📋 OBJETIVO
Desplegar y validar completamente el sistema AlpesPartner con microservicios, bases de datos individuales, tópicos Pulsar y SagaLogger híbrido MySQL/SQLite.

---

## 🎯 FASE 1: PREPARACIÓN PRE-DESPLIEGUE

### ✅ Verificaciones Iniciales
```bash
# 1. Verificar archivos necesarios
ls -la docker-compose-alpespartner.yml
ls -la src-alpespartner/

# 2. Limpiar contenedores previos (si existen)
docker-compose -f docker-compose-alpespartner.yml down -v
docker system prune -f

# 3. Verificar espacio en disco (mínimo 5GB)
df -h
```

---

## 🏗️ FASE 2: DESPLIEGUE INFRAESTRUCTURA

### 🎭 Paso 1: Levantar Infraestructura Base
```bash
# Desplegar solo infraestructura (Pulsar + MySQL)
docker-compose -f docker-compose-alpespartner.yml --profile infrastructure up -d

# Esperar 60 segundos para estabilización
sleep 60
```

### ✅ Validación Infraestructura
```bash
# 1. Verificar contenedores de infraestructura
docker ps --filter "name=alpespartner" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. Verificar Pulsar Broker
curl -s http://localhost:8080/admin/v2/clusters | jq .

# 3. Verificar bases de datos MySQL (6 instancias)
docker exec alpespartner-campanias-mysql mysql -u campanias -pcampanias123 -e "SELECT 'campanias DB OK' as status;"
docker exec alpespartner-afiliados-mysql mysql -u afiliados -pafiliados123 -e "SELECT 'Afiliados DB OK' as status;"
docker exec alpespartner-comisiones-mysql mysql -u comisiones -pcomisiones123 -e "SELECT 'Comisiones DB OK' as status;"
docker exec alpespartner-conversiones-mysql mysql -u conversiones -pconversiones123 -e "SELECT 'Conversiones DB OK' as status;"
docker exec alpespartner-notificaciones-mysql mysql -u notificaciones -pnotificaciones123 -e "SELECT 'Notificaciones DB OK' as status;"
docker exec alpespartner-sagas-mysql mysql -u sagas -psagas123 -e "SELECT 'Sagas DB OK' as status;"
```

**🎯 CRITERIO DE ÉXITO FASE 2:**
- ✅ 9 contenedores de infraestructura ejecutándose
- ✅ Pulsar Admin API responde (puerto 8080)
- ✅ 6 bases de datos MySQL conectables

---

## 🎭 FASE 3: DESPLIEGUE MICROSERVICIOS

### 🚀 Paso 2: Levantar Microservicios AlpesPartner
```bash
# Desplegar microservicios con SagaLogger MySQL
SAGAS_STORAGE_TYPE=mysql docker-compose -f docker-compose-alpespartner.yml --profile alpespartner up -d

# Esperar 90 segundos para inicialización
sleep 90
```

### ✅ Validación Microservicios
```bash
# 1. Verificar todos los contenedores
docker ps --filter "name=alpespartner" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(bff|campanias|afiliados|comisiones|conversiones|notificaciones)"

# 2. Health check de cada microservicio
echo "🏥 HEALTH CHECKS:"
curl -s http://localhost:8001/docs && echo "✅ BFF OK (8001)" || echo "❌ BFF FAIL"
curl -s http://localhost:8003/docs && echo "✅ campanias OK (8003)" || echo "❌ campanias FAIL" 
curl -s http://localhost:8004/docs && echo "✅ Afiliados OK (8004)" || echo "❌ Afiliados FAIL"
curl -s http://localhost:8005/docs && echo "✅ Comisiones OK (8005)" || echo "❌ Comisiones FAIL"
curl -s http://localhost:8006/docs && echo "✅ Conversiones OK (8006)" || echo "❌ Conversiones FAIL"
curl -s http://localhost:8008/docs && echo "✅ Notificaciones OK (8008)" || echo "❌ Notificaciones FAIL"

# 3. Verificar logs de inicialización
echo "📋 LOGS DE INICIALIZACIÓN:"
docker logs alpespartner-campanias --tail 10 | grep -E "(SagaLogger|MySQL|SAGA)"
docker logs alpespartner-bff --tail 5
```

**🎯 CRITERIO DE ÉXITO FASE 3:**
- ✅ 6 microservicios ejecutándose correctamente
- ✅ Todas las APIs responden en sus puertos
- ✅ SagaLogger MySQL inicializado en campanias

---

## 🎭 FASE 4: VALIDACIÓN TÓPICOS PULSAR

### 📡 Paso 3: Verificar Tópicos Activos
```bash
# 1. Listar todos los tópicos creados
echo "📡 TÓPICOS PULSAR DISPONIBLES:"
docker exec alpespartner-broker bin/pulsar-admin topics list public/default

# 2. Verificar tópicos críticos para Sagas
echo "🎭 TÓPICOS CRÍTICOS PARA SAGAS:"
docker exec alpespartner-broker bin/pulsar-admin topics stats public/default/comando-lanzar-campania-completa
docker exec alpespartner-broker bin/pulsar-admin topics stats public/default/comando-buscar-afiliados-elegibles
docker exec alpespartner-broker bin/pulsar-admin topics stats public/default/comando-configurar-comisiones
docker exec alpespartner-broker bin/pulsar-admin topics stats public/default/comando-inicializar-tracking
docker exec alpespartner-broker bin/pulsar-admin topics stats public/default/comando-preparar-notificaciones

# 3. Verificar suscripciones activas
echo "👂 SUSCRIPCIONES ACTIVAS:"
docker exec alpespartner-broker bin/pulsar-admin topics subscriptions public/default/comando-lanzar-campania-completa
```

### ✅ Validación Manual de Tópicos
```bash
# Prueba básica: Enviar mensaje de prueba
echo "🧪 PRUEBA DE CONECTIVIDAD PULSAR:"
docker exec alpespartner-broker bin/pulsar-client produce public/default/test-topic --messages "Hello AlpesPartner $(date)"
docker exec alpespartner-broker bin/pulsar-client consume public/default/test-topic -s test-subscription -n 1
```

**🎯 CRITERIO DE ÉXITO FASE 4:**
- ✅ Tópicos principales creados y disponibles
- ✅ Microservicios suscritos a sus tópicos
- ✅ Conectividad Pulsar funcional

---

## 🎭 FASE 5: VALIDACIÓN SAGALOGGER HÍBRIDO

### 🗄️ Paso 4: Verificar SagaLogger V2
```bash
# 1. Verificar tablas MySQL creadas automáticamente
echo "🗄️ TABLAS SAGA EN MySQL:"
docker exec alpespartner-sagas-mysql mysql -u sagas -psagas123 sagas -e "SHOW TABLES;"
docker exec alpespartner-sagas-mysql mysql -u sagas -psagas123 sagas -e "DESCRIBE sagas;"
docker exec alpespartner-sagas-mysql mysql -u sagas -psagas123 sagas -e "DESCRIBE pasos_saga;"

# 2. Verificar endpoint de monitoreo de Sagas
echo "📊 APIS DE MONITOREO SAGA:"
curl -s http://localhost:8003/api/v1/sagas/activas | jq .
curl -s http://localhost:8003/api/v1/campanias | jq .
```

### 🧪 Prueba de SagaLogger
```bash
# Crear una saga de prueba simple para validar persistencia
echo "🧪 CREANDO SAGA DE PRUEBA:"
curl -X POST http://localhost:8003/api/v1/campanias \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Campaña Prueba SagaLogger",
    "descripcion": "Validación del sistema de sagas",
    "tipo": "promocional",
    "canal_publicidad": "social_media",
    "objetivo": "incrementar_ventas",
    "fecha_inicio": "2024-12-01",
    "fecha_fin": "2024-12-31"
  }'

# Verificar que se registró en BD
sleep 5
docker exec alpespartner-sagas-mysql mysql -u sagas -psagas123 sagas -e "SELECT saga_id, tipo, estado, timestamp_inicio FROM sagas ORDER BY timestamp_inicio DESC LIMIT 3;"
```

**🎯 CRITERIO DE ÉXITO FASE 5:**
- ✅ Tablas `sagas` y `pasos_saga` creadas en MySQL
- ✅ API de monitoreo `/sagas/activas` funcional
- ✅ Persistencia de sagas en base de datos

---

## 🔗 FASE 6: PRUEBA DE CONECTIVIDAD DE EVENTOS

### 📡 Paso 5: Validación de Suscripciones y Flujo de Eventos
```bash
echo "🔗 INICIANDO PRUEBA DE CONECTIVIDAD DE EVENTOS BFF ↔ campanias"

# 1. Verificar que las suscripciones estén activas ANTES de enviar eventos
echo "👂 VERIFICANDO SUSCRIPCIONES ACTIVAS:"
docker exec alpespartner-broker bin/pulsar-admin topics subscriptions public/default/comando-crear-campania
docker exec alpespartner-broker bin/pulsar-admin topics subscriptions public/default/evento-campania-creada

# 2. Enviar comando simple de CREACIÓN desde BFF (no saga completa)
echo "📤 ENVIANDO COMANDO SIMPLE DE CREACIÓN DESDE BFF:"
curl -X POST http://localhost:8001/api/v1/comandos/crear-campania \
  -H "Content-Type: application/json" \
  -d '{
    "campania": {
      "nombre": "Prueba Conectividad Eventos",
      "descripcion": "Validación de suscripciones BFF → campanias",
      "tipo": "test_conectividad",
      "canal_publicidad": "email",
      "objetivo": "validar_eventos",
      "fecha_inicio": "2024-12-01",
      "fecha_fin": "2024-12-07"
    }
  }' | jq .

echo "⏱️ Esperando procesamiento del evento (15 segundos)..."
sleep 15

# 3. Verificar LOGS de procesamiento en ambos servicios
echo "📋 LOGS BFF (comando enviado):"
docker logs alpespartner-bff --tail 10 | grep -E "(comando|enviado|Pulsar|crear)"

echo "📋 LOGS campanias (comando recibido):"
docker logs alpespartner-campanias --tail 15 | grep -E "(comando|recibido|creando|campaña|CrearCampania)"

# 4. Verificar si se generó EVENTO de respuesta (CampaniaCreada)
echo "📋 LOGS DE EVENTO GENERADO (CampaniaCreada):"
docker logs alpespartner-campanias --tail 10 | grep -E "(evento|CampaniaCreada|publicado)"

# 5. Consultar base de datos para ver si se creó la campaña
echo "🗄️ VERIFICANDO CREACIÓN EN BD campanias:"
docker exec alpespartner-campanias-mysql mysql -u campanias -pcampanias123 campanias -e "
  SELECT id, nombre, tipo, estado, fecha_creacion 
  FROM campanias 
  WHERE nombre LIKE '%Conectividad%' 
  ORDER BY fecha_creacion DESC LIMIT 3;
"

# 6. Verificar trazas en SagaLogger (si aplica)
echo "🎭 TRAZAS EN SAGALOGGER:"
curl -s http://localhost:8003/api/v1/sagas/activas | jq '.[] | select(.tipo | contains("crear")) | {saga_id, estado, tipo}'

# 7. Verificar estadísticas de tópicos después del evento
echo "📊 ESTADÍSTICAS DE TÓPICOS POST-EVENTO:"
docker exec alpespartner-broker bin/pulsar-admin topics stats public/default/comando-crear-campania | jq '.publishers, .subscriptions'
```

### 🧪 Prueba de Flujo Completo de Creación
```bash
echo "🔄 FLUJO COMPLETO: BFF → Comando → campanias → Evento → Verificación"

# Monitorear logs en tiempo real (background)
echo "🔍 INICIANDO MONITOREO DE LOGS..."
(docker logs -f alpespartner-campanias 2>&1 | grep -E "(comando|evento|saga)" &) &
LOGS_PID=$!

# Enviar comando y medir tiempo de respuesta
START_TIME=$(date +%s)
echo "⏰ Tiempo inicio: $(date)"

curl -X POST http://localhost:8001/api/v1/comandos/crear-campania \
  -H "Content-Type: application/json" \
  -d '{
    "campania": {
      "nombre": "Test Flujo Completo $(date +%H%M%S)",
      "descripcion": "Validación end-to-end de eventos",
      "tipo": "flujo_completo",
      "canal_publicidad": "multi_canal",
      "objetivo": "test_e2e",
      "fecha_inicio": "2024-12-01",
      "fecha_fin": "2024-12-15"
    }
  }'

sleep 10
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "⏰ Tiempo final: $(date)"
echo "⌛ Duración total: ${DURATION} segundos"

# Detener monitoreo
kill $LOGS_PID 2>/dev/null

# Verificar resultado final
echo "✅ RESULTADO FINAL:"
docker exec alpespartner-campanias-mysql mysql -u campanias -pcampanias123 campanias -e "
  SELECT COUNT(*) as total_campanias, 
         COUNT(CASE WHEN tipo LIKE '%test%' THEN 1 END) as campanias_test
  FROM campanias;
"
```

**🎯 CRITERIO DE ÉXITO FASE 6:**
- ✅ BFF envía comando via Pulsar correctamente
- ✅ campanias recibe y procesa comando
- ✅ Se crea campaña en base de datos
- ✅ Se genera evento CampaniaCreada de respuesta
- ✅ Logs muestran flujo completo
- ✅ SagaLogger registra actividad (si aplica)
- ✅ Tópicos muestran estadísticas de mensajes

---

## 🎭 FASE 7: PRUEBA END-TO-END COMPLETA

### 🔄 Paso 6: Flujo Completo BFF → campanias → Sagas
```bash
echo "🎯 INICIANDO FLUJO COMPLETO DE SAGA:"

# 1. Enviar comando desde BFF para lanzar campaña completa
curl -X POST http://localhost:8001/api/v1/comandos/lanzar-campania-completa \
  -H "Content-Type: application/json" \
  -d '{
    "campania": {
      "id": "camp-test-001",
      "nombre": "Campaña End-to-End Test",
      "descripcion": "Prueba completa del flujo de sagas",
      "tipo": "promocional", 
      "canal_publicidad": "social_media",
      "objetivo": "incrementar_ventas",
      "fecha_inicio": "2024-12-01",
      "fecha_fin": "2024-12-31",
      "segmento_audiencia": "premium"
    }
  }'

echo "⏱️ Esperando procesamiento de saga (30 segundos)..."
sleep 30

# 2. Verificar logs de procesamiento
echo "📋 LOGS DE SAGA PROCESSING:"
docker logs alpespartner-campanias --tail 20 | grep -E "(SAGA|🎭|📝|✅)"

# 3. Consultar estado de sagas activas
echo "📊 ESTADO ACTUAL DE SAGAS:"
curl -s http://localhost:8003/api/v1/sagas/activas | jq '.[] | {saga_id, estado, tipo, campania_id}'

# 4. Verificar datos en MySQL
echo "🗄️ SAGAS EN BASE DE DATOS:"
docker exec alpespartner-sagas-mysql mysql -u sagas -psagas123 sagas -e "
  SELECT saga_id, tipo, estado, campania_id, timestamp_inicio 
  FROM sagas 
  WHERE tipo = 'lanzar_campania_completa' 
  ORDER BY timestamp_inicio DESC LIMIT 5;
"

# 5. Verificar pasos de saga
echo "📝 PASOS DE SAGA:"
docker exec alpespartner-sagas-mysql mysql -u sagas -psagas123 sagas -e "
  SELECT s.saga_id, p.nombre, p.microservicio, p.estado 
  FROM sagas s 
  JOIN pasos_saga p ON s.saga_id = p.saga_id 
  WHERE s.tipo = 'lanzar_campania_completa' 
  ORDER BY s.timestamp_inicio DESC, p.timestamp_inicio ASC;
"
```

**🎯 CRITERIO DE ÉXITO FASE 6:**
- ✅ BFF recibe comando y lo envía a campanias via Pulsar
- ✅ campanias orquesta saga con pasos secuenciales
- ✅ SagaLogger registra cada paso en MySQL
- ✅ Todos los microservicios reciben sus comandos correspondientes

---

## 📊 FASE 7: REPORTE DE VALIDACIÓN

### 📋 Paso 7: Generar Reporte Completo
```bash
echo "📊 GENERANDO REPORTE DE VALIDACIÓN COMPLETO..."

# Crear archivo de reporte
cat > validation_report_$(date +%Y%m%d_%H%M%S).md << 'EOF'
# 🎭 REPORTE DE VALIDACIÓN - AlpesPartner

## ✅ INFRAESTRUCTURA
EOF

# Agregar estado de contenedores
echo "### 🐳 Contenedores Ejecutándose" >> validation_report_*.md
docker ps --filter "name=alpespartner" --format "- {{.Names}}: {{.Status}}" >> validation_report_*.md

# Agregar estado de microservicios
echo -e "\n### 🚀 APIs Disponibles" >> validation_report_*.md
echo "- BFF: http://localhost:8001/docs" >> validation_report_*.md
echo "- campanias: http://localhost:8003/docs" >> validation_report_*.md  
echo "- Afiliados: http://localhost:8004/docs" >> validation_report_*.md
echo "- Comisiones: http://localhost:8005/docs" >> validation_report_*.md
echo "- Conversiones: http://localhost:8006/docs" >> validation_report_*.md
echo "- Notificaciones: http://localhost:8008/docs" >> validation_report_*.md

# Agregar estado de tópicos
echo -e "\n### 📡 Tópicos Pulsar" >> validation_report_*.md
docker exec alpespartner-broker bin/pulsar-admin topics list public/default | sed 's/^/- /' >> validation_report_*.md

# Agregar estado de sagas
echo -e "\n### 🎭 Estado de Sagas" >> validation_report_*.md
curl -s http://localhost:8003/api/v1/sagas/activas | jq -r '.[] | "- Saga: \(.saga_id) | Estado: \(.estado) | Tipo: \(.tipo)"' >> validation_report_*.md

echo "✅ Reporte generado: validation_report_$(date +%Y%m%d_%H%M%S).md"
```

**🎯 CRITERIO DE ÉXITO FASE 7:**
- ✅ BFF recibe comando y lo envía a campanias via Pulsar
- ✅ campanias orquesta saga con pasos secuenciales
- ✅ SagaLogger registra cada paso en MySQL
- ✅ Todos los microservicios reciben sus comandos correspondientes

---

## 📊 FASE 8: REPORTE DE VALIDACIÓN
```

---

## 🎯 CHECKLIST FINAL DE VALIDACIÓN

### ✅ Infraestructura Base
- [ ] Pulsar (Zookeeper, BookKeeper, Broker) ejecutándose
- [ ] 6 bases de datos MySQL funcionando (puertos 3307-3312)
- [ ] Admin UI Pulsar accesible (http://localhost:8080)

### ✅ Microservicios
- [ ] BFF ejecutándose (puerto 8001)
- [ ] campanias ejecutándose (puerto 8003) 
- [ ] Afiliados ejecutándose (puerto 8004)
- [ ] Comisiones ejecutándose (puerto 8005)
- [ ] Conversiones ejecutándose (puerto 8006)
- [ ] Notificaciones ejecutándose (puerto 8008)

### ✅ Comunicación Pulsar
- [ ] Tópicos principales creados
- [ ] Microservicios suscritos correctamente
- [ ] Mensajes fluyen entre servicios

### ✅ SagaLogger Híbrido
- [ ] Tablas MySQL creadas automáticamente
- [ ] API `/sagas/activas` funcional
- [ ] Persistencia de sagas y pasos en BD
- [ ] Logs de saga visibles en campanias

### ✅ Flujo End-to-End
- [ ] BFF → campanias via Pulsar funcional
- [ ] Orquestación de saga secuencial
- [ ] Todos los microservicios procesan comandos
- [ ] Dashboard de monitoreo operativo

---

## 🚨 TROUBLESHOOTING

### Problemas Comunes:

**🔧 Si un microservicio no inicia:**
```bash
# Ver logs detallados
docker logs alpespartner-[SERVICE_NAME] --tail 50

# Verificar conectividad a BD
docker exec alpespartner-[SERVICE_NAME] ping [DB_HOST]
```

**🔧 Si Pulsar no responde:**
```bash
# Reiniciar infraestructura Pulsar
docker-compose -f docker-compose-alpespartner.yml restart zookeeper bookkeeper broker

# Verificar logs
docker logs alpespartner-broker --tail 30
```

**🔧 Si SagaLogger falla:**
```bash
# Verificar configuración MySQL
docker logs alpespartner-campanias | grep -i saga

# Verificar tablas
docker exec alpespartner-sagas-mysql mysql -u sagas -psagas123 sagas -e "SHOW TABLES;"
```

---

**🎯 Con este plan tienes una validación completa y sistemática del despliegue. ¿Procedemos con la ejecución paso a paso?**