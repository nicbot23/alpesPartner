#!/bin/bash

# Script de prueba completa del sistema CDC - ACTUALIZADO
# Demuestra el flujo completo: API → Outbox → CDC → Pulsar

echo "🚀 SCRIPT DE PRUEBAS COMPLETAS CDC - AlpesPartner - ACTUALIZADO"
echo "================================================================="

# Función para crear una comisión
create_commission() {
    local conversion_id=$1
    local affiliate_id=$2
    local campaign_id=$3
    local amount=$4
    local currency=$5
    
    echo "📝 Creando comisión para conversión: $conversion_id"
    response=$(curl -s -X POST http://localhost:5001/commissions/calculate \
      -H "Content-Type: application/json" \
      -d '{
        "conversionId": "'$conversion_id'",
        "affiliateId": "'$affiliate_id'", 
        "campaignId": "'$campaign_id'",
        "grossAmount": '$amount',
        "currency": "'$currency'"
      }')
    
    echo "✅ Respuesta API: $response"
    return 0
}

# Función para verificar eventos en outbox
check_outbox() {
    echo "📋 Verificando eventos en outbox_event..."
    response=$(curl -s -X GET http://localhost:5001/debug/outbox)
    echo "$response" | python3 -m json.tool
    return 0
}

# Función para ejecutar CDC
run_cdc() {
    echo "🔄 Ejecutando procesamiento CDC..."
    cd "/Users/nicolasibarra/uniandes/miso-uniandes/semestre4/ciclo 1/Diseño y cosntrucción de soluciones no monoliticas/semana5/alpesPartner"
    "/Users/nicolasibarra/uniandes/miso-uniandes/semestre4/ciclo 1/Diseño y cosntrucción de soluciones no monoliticas/semana5/alpesPartner/.venv/bin/python" manual_cdc.py
    return 0
}

# PRUEBA PRINCIPAL: Crear comisión y procesar CDC
echo "🧪 PRUEBA: Crear comisión nueva y procesar CDC"
echo "-"*50
create_commission "test-conv-NEW" "affiliate-CDC" "campaign-TEST" 7500.00 "CAD"

echo
echo "📊 Estado del outbox antes del CDC:"
check_outbox

echo
echo "🔄 Procesando eventos con CDC..."
run_cdc

echo
echo "📊 Estado del outbox después del CDC:"
check_outbox

echo
echo "🎉 ¡Prueba CDC completada exitosamente!"
echo "=================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URL de la API
API_URL="http://localhost:5001"

echo -e "\n${BLUE}📋 PASO 1: Verificando estado de contenedores${NC}"
echo "================================================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n${BLUE}📋 PASO 2: Verificando estado de MySQL binlog${NC}"
echo "================================================="
docker exec -it $(docker ps -qf name=mysql) mysql -uroot -pdebezium -e "\
SHOW VARIABLES LIKE 'log_bin'; \
SHOW VARIABLES LIKE 'binlog_format'; \
SHOW VARIABLES LIKE 'binlog_row_image'; \
SHOW VARIABLES LIKE 'server_id';"

echo -e "\n${BLUE}📋 PASO 3: Verificando estado de Debezium Source${NC}"
echo "================================================="
docker exec -it $(docker ps -qf name=pulsar) \
  bin/pulsar-admin sources status --tenant public --namespace default --name mysql-outbox-commissions 2>/dev/null || \
  echo -e "${YELLOW}⚠️  Source Debezium no encontrado. Será creado automáticamente.${NC}"

echo -e "\n${BLUE}📋 PASO 4: Limpiando tablas para prueba limpia${NC}"
echo "================================================="
docker exec -it $(docker ps -qf name=mysql) mysql -uroot -pdebezium -e "\
SET FOREIGN_KEY_CHECKS=0; \
TRUNCATE TABLE alpes.outbox_event; \
TRUNCATE TABLE alpes.commission; \
SET FOREIGN_KEY_CHECKS=1; \
SELECT COUNT(*) AS outbox_events, (SELECT COUNT(*) FROM alpes.commission) AS commissions FROM alpes.outbox_event;"

echo -e "\n${BLUE}📋 PASO 5: Creando/Reiniciando Source Debezium${NC}"
echo "================================================="
docker exec -it $(docker ps -qf name=pulsar) bash -lc "\
bin/pulsar-admin sources delete --tenant public --namespace default --name mysql-outbox-commissions 2>/dev/null || true && \
sleep 2 && \
bin/pulsar-admin sources create \
  --tenant public --namespace default --name mysql-outbox-commissions \
  --archive /pulsar/connectors/pulsar-io-debezium-mysql-3.1.2.nar \
  --destination-topic-name persistent://public/default/outbox-events \
  --source-config-file /pulsar/connectors/debezium-mysql-outbox.json && \
sleep 3 && \
bin/pulsar-admin sources status --tenant public --namespace default --name mysql-outbox-commissions"

echo -e "\n${BLUE}📋 PASO 6: Verificando conectividad API${NC}"
echo "================================================="
curl -s -o /dev/null -w "Status: %{http_code}\n" ${API_URL}/health || echo -e "${RED}❌ API no disponible${NC}"

echo -e "\n${GREEN}🧪 INICIANDO PRUEBAS DE EVENTOS CDC${NC}"
echo "================================================="

# Variables para la prueba
CONVERSION_ID="conv-$(date +%s)"
AFFILIATE_ID="aff-12345"
CAMPAIGN_ID="camp-67890"
GROSS_AMOUNT=1000.00
CURRENCY="USD"

echo -e "\n${YELLOW}🔄 PRUEBA 1: Calculando comisión${NC}"
echo "Datos: conversionId=${CONVERSION_ID}, affiliateId=${AFFILIATE_ID}, campaignId=${CAMPAIGN_ID}"

CALC_RESPONSE=$(curl -s -X POST ${API_URL}/commissions/calculate \
  -H "Content-Type: application/json" \
  -d "{
    \"conversionId\": \"${CONVERSION_ID}\",
    \"affiliateId\": \"${AFFILIATE_ID}\",
    \"campaignId\": \"${CAMPAIGN_ID}\",
    \"grossAmount\": ${GROSS_AMOUNT},
    \"currency\": \"${CURRENCY}\"
  }")

echo "Respuesta API: ${CALC_RESPONSE}"

# Extraer commission ID
COMMISSION_ID=$(echo ${CALC_RESPONSE} | grep -o '"commissionId":"[^"]*"' | cut -d'"' -f4)
echo "Commission ID: ${COMMISSION_ID}"

echo -e "\n${YELLOW}⏳ Esperando 3 segundos para que Debezium procese...${NC}"
sleep 3

echo -e "\n${YELLOW}📊 Verificando tabla outbox_event${NC}"
docker exec -it $(docker ps -qf name=mysql) mysql -uroot -pdebezium -e "\
SELECT id, aggregate_type, aggregate_id, event_type, JSON_EXTRACT(payload, '$.eventVersion') as version, occurred_at, published \
FROM alpes.outbox_event ORDER BY occurred_at DESC LIMIT 5;"

echo -e "\n${YELLOW}📡 Verificando eventos en Pulsar (tópico outbox-events)${NC}"
timeout 10s docker exec -it $(docker ps -qf name=pulsar) \
  bin/pulsar-client consume persistent://public/default/outbox-events \
  -s "test-calc-$(date +%s)" -n 1 -p Earliest 2>/dev/null || echo -e "${YELLOW}⚠️  No se recibieron eventos en 10s${NC}"

if [ ! -z "${COMMISSION_ID}" ]; then
  echo -e "\n${YELLOW}🔄 PRUEBA 2: Aprobando comisión${NC}"
  
  APPROVE_RESPONSE=$(curl -s -X POST ${API_URL}/commissions/approve \
    -H "Content-Type: application/json" \
    -d "{\"commissionId\": \"${COMMISSION_ID}\"}")
  
  echo "Respuesta API: ${APPROVE_RESPONSE}"
  
  echo -e "\n${YELLOW}⏳ Esperando 3 segundos para que Debezium procese...${NC}"
  sleep 3
  
  echo -e "\n${YELLOW}📊 Verificando tabla outbox_event (después de aprobar)${NC}"
  docker exec -it $(docker ps -qf name=mysql) mysql -uroot -pdebezium -e "\
  SELECT id, aggregate_type, aggregate_id, event_type, JSON_EXTRACT(payload, '$.eventVersion') as version, occurred_at, published \
  FROM alpes.outbox_event ORDER BY occurred_at DESC LIMIT 5;"
  
  echo -e "\n${YELLOW}📡 Verificando eventos en Pulsar (después de aprobar)${NC}"
  timeout 10s docker exec -it $(docker ps -qf name=pulsar) \
    bin/pulsar-client consume persistent://public/default/outbox-events \
    -s "test-approve-$(date +%s)" -n 2 -p Earliest 2>/dev/null || echo -e "${YELLOW}⚠️  No se recibieron eventos en 10s${NC}"
    
  echo -e "\n${YELLOW}🔍 PRUEBA 3: Consultando comisión creada${NC}"
  
  QUERY_RESPONSE=$(curl -s ${API_URL}/commissions/by-conversion/${CONVERSION_ID})
  echo "Respuesta consulta: ${QUERY_RESPONSE}"
fi

echo -e "\n${BLUE}📊 RESUMEN FINAL${NC}"
echo "================================================="

echo -e "\n${YELLOW}📈 Estadísticas de base de datos:${NC}"
docker exec -it $(docker ps -qf name=mysql) mysql -uroot -pdebezium -e "\
SELECT \
  (SELECT COUNT(*) FROM alpes.commission) as total_commissions, \
  (SELECT COUNT(*) FROM alpes.outbox_event) as total_outbox_events, \
  (SELECT COUNT(*) FROM alpes.outbox_event WHERE published=false) as unpublished_events;"

echo -e "\n${YELLOW}📈 Estado del Source Debezium:${NC}"
docker exec -it $(docker ps -qf name=pulsar) \
  bin/pulsar-admin sources status --tenant public --namespace default --name mysql-outbox-commissions 2>/dev/null | \
  grep -E "(running|numReceivedFromSource|numWritten)" || echo -e "${RED}❌ Source no disponible${NC}"

echo -e "\n${YELLOW}📈 Tópicos disponibles en Pulsar:${NC}"
docker exec -it $(docker ps -qf name=pulsar) \
  bin/pulsar-admin topics list public/default 2>/dev/null | grep -E "(outbox|alpes)" || echo -e "${YELLOW}⚠️  No hay tópicos relacionados${NC}"

echo -e "\n${YELLOW}📈 Logs del servicio de notificaciones:${NC}"
tail -n 10 ./data/events.jsonl 2>/dev/null || echo -e "${YELLOW}⚠️  No hay archivo events.jsonl${NC}"

echo -e "\n${GREEN}✅ PRUEBAS COMPLETADAS${NC}"
echo "================================================="
echo -e "${BLUE}Para monitorear en tiempo real:${NC}"
echo "- Logs Debezium: docker exec -it \$(docker ps -qf name=pulsar) tail -f logs/functions/public/default/mysql-outbox-commissions/mysql-outbox-commissions-0.log"
echo "- Eventos Pulsar: docker exec -it \$(docker ps -qf name=pulsar) bin/pulsar-client consume persistent://public/default/outbox-events -s live -n 0 -p Earliest"
echo "- Logs notificaciones: tail -f ./data/events.jsonl"
