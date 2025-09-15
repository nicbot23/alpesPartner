#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Script: script_escenarios_pruebas.sh
# Objetivo: Ejecutar escenarios de prueba para la arquitectura event-driven
# Servicios involucrados: bff (9000), marketing (8003), Pulsar (6650/8080), MySQL (3306)
# Requisitos: docker-compose levantado, curl, jq instalado (opcional para mejor formato)
# -----------------------------------------------------------------------------

set -euo pipefail
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BFF_URL="http://localhost:9000"
MARKETING_URL="http://localhost:8003"
PULSAR_ADMIN="http://localhost:8080/admin/v2"
PULSAR_CONTAINER="alpes-pulsar"
TOPIC_EVENTOS="persistent://public/default/marketing.eventos"
TOPIC_COMISIONES="persistent://public/default/marketing.comisiones.eventos"
TOPIC_COMANDOS="persistent://public/default/marketing.campanas.comandos"
MYSQL_CONT="alpes-mysql-marketing"
JQ_BIN="jq"

# Colores
OK="\e[32m✔\e[0m"
FAIL="\e[31m✖\e[0m"
INFO="\e[34mℹ\e[0m"
WARN="\e[33m⚠\e[0m"

function check_dep() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo -e "$WARN Dependencia '$1' no encontrada. Continuando sin ella."
    return 1
  fi
  return 0
}

check_dep "$JQ_BIN" || JQ_BIN="cat"

function header() {
  echo -e "\n======================================================================"
  echo -e "  ESCENARIO: $1"
  echo -e "======================================================================"
}

function wait_seconds() { sleep "$1"; }

function consume_topic_latest() {
  local topic=$1
  local subs=$2
  docker exec -i "$PULSAR_CONTAINER" bin/pulsar-client consume \
    "$topic" -s "$subs-$(date +%s)" -p Latest -n 1 2>/dev/null || true
}

function consume_topic_earliest() {
  local topic=$1
  local subs=$2
  docker exec -i "$PULSAR_CONTAINER" bin/pulsar-client consume \
    "$topic" -s "$subs-$(date +%s)" -p Earliest -n 50 2>/dev/null || true
}

function sql_marketing() {
  local q=$1
  docker exec -i "$MYSQL_CONT" mysql -u alpes -palpes -D alpes_marketing -e "$q" 2>/dev/null || true
}

# -----------------------------------------------------------------------------
# Escenario 1: Flujo Exitoso Básico
# -----------------------------------------------------------------------------
function escenario_exitoso() {
  header "1 - Flujo Exitoso Básico"
  local payload='{
    "nombre": "Campaña Escenario OK",
    "descripcion": "Demo flujo exitoso",
    "fecha_inicio": "2024-11-01",
    "fecha_fin": "2024-11-30",
    "presupuesto": 10000.0,
    "comision_porcentaje": 0.07,
    "tags": ["demo","ok"]
  }'
  echo -e "$INFO Enviando comando CrearCampana..."
  local resp=$(curl -s -X POST "$BFF_URL/campanas" -H 'Content-Type: application/json' -d "$payload")
  echo "$resp" | $JQ_BIN
  local corr=$(echo "$resp" | grep -o '"correlation_id":"[^"]*"' | cut -d '"' -f4 || true)
  echo -e "$INFO correlation_id=$corr"
  echo -e "$INFO Esperando procesamiento..."
  wait_seconds 4
  echo -e "$INFO Última campaña persistida:"; sql_marketing "SELECT id,nombre,estado,creada_en FROM campanas ORDER BY creada_en DESC LIMIT 1;"
  echo -e "$INFO Buscar comisión asociada (puede no existir si lógica inicial = 0 monto):"; sql_marketing "SELECT id,campaign_id,percentage,status,calculated_at FROM commission ORDER BY calculated_at DESC LIMIT 2;"
}

# -----------------------------------------------------------------------------
# Escenario 2: Fechas inválidas (inicio > fin)
# Actualmente no hay validación estricta en BFF, se probaría futura lógica.
# Se muestra cómo se aceptaría y qué deberíamos marcar como mejora.
# -----------------------------------------------------------------------------
function escenario_fechas_invalidas() {
  header "2 - Fechas Inválidas (inicio > fin)"
  local payload='{
    "nombre": "Campaña Fechas Invalidas",
    "descripcion": "Inicio posterior a fin",
    "fecha_inicio": "2024-12-31",
    "fecha_fin": "2024-01-01",
    "presupuesto": 5000.0
  }'
  local resp=$(curl -s -X POST "$BFF_URL/campanas" -H 'Content-Type: application/json' -d "$payload")
  echo "$resp" | $JQ_BIN
  echo -e "$WARN No se valida actualmente en backend -> Debería agregarse regla de negocio futura."
  wait_seconds 3
  sql_marketing "SELECT id,nombre,fecha_inicio,fecha_fin FROM campanas ORDER BY creada_en DESC LIMIT 1;"
}

# -----------------------------------------------------------------------------
# Escenario 3: Comisión con porcentaje no estándar (>100 o negativo)
# -----------------------------------------------------------------------------
function escenario_porcentaje_extremo() {
  header "3 - Comisión Porcentaje Extremo"
  local payload='{
    "nombre": "Campaña Porcentaje Extremo",
    "descripcion": "Porcentaje > 1 (100%)",
    "fecha_inicio": "2024-11-01",
    "fecha_fin": "2024-11-30",
    "presupuesto": 1000.0,
    "comision_porcentaje": 1.50
  }'
  local resp=$(curl -s -X POST "$BFF_URL/campanas" -H 'Content-Type: application/json' -d "$payload")
  echo "$resp" | $JQ_BIN
  echo -e "$WARN Comisión porcentual >100% aceptada -> Falta validación futura." 
  wait_seconds 3
  sql_marketing "SELECT id,terminos_comision FROM campanas ORDER BY creada_en DESC LIMIT 1;"
}

# -----------------------------------------------------------------------------
# Escenario 4: Duplicado (mismo nombre rápido) -> Se permite; ID distinto.
# -----------------------------------------------------------------------------
function escenario_duplicado_nombre() {
  header "4 - Campañas Duplicadas Nombre"
  local base='{
    "nombre": "Campaña Duplicada",
    "descripcion": "Primera",
    "fecha_inicio": "2024-11-01",
    "fecha_fin": "2024-11-30",
    "presupuesto": 2000.0
  }'
  curl -s -X POST "$BFF_URL/campanas" -H 'Content-Type: application/json' -d "$base" >/dev/null
  wait_seconds 2
  curl -s -X POST "$BFF_URL/campanas" -H 'Content-Type: application/json' -d "$base" >/dev/null
  wait_seconds 3
  echo -e "$INFO Mostrando últimas 2 inserciones:" 
  sql_marketing "SELECT id,nombre,creada_en FROM campanas ORDER BY creada_en DESC LIMIT 2;"
}

# -----------------------------------------------------------------------------
# Escenario 5: Consumo histórico de eventos (Earliest)
# -----------------------------------------------------------------------------
function escenario_consumo_historico() {
  header "5 - Consumo Histórico de Eventos"
  echo -e "$INFO Recuperando eventos Campaña (marketing.eventos)"
  consume_topic_earliest "$TOPIC_EVENTOS" "hist-camp"
  echo -e "$INFO Recuperando eventos Comisiones (marketing.comisiones.eventos)"
  consume_topic_earliest "$TOPIC_COMISIONES" "hist-com"
}

# -----------------------------------------------------------------------------
# Escenario 6: Correlación (crear varias campañas y filtrar por correlation_id)
# -----------------------------------------------------------------------------
function escenario_correlacion() {
  header "6 - Correlación de Eventos"
  for i in 1 2 3; do
    local corr="corr-demo-$i-$(date +%s)"
    local payload=$(cat <<PAY
{
  "nombre": "Campaña Corr $i",
  "descripcion": "Test correlación $i",
  "fecha_inicio": "2024-11-01",
  "fecha_fin": "2024-11-30",
  "presupuesto": 1000.0,
  "correlation_id": "$corr"
}
PAY
)
    curl -s -X POST "$BFF_URL/campanas" -H 'Content-Type: application/json' -d "$payload" >/dev/null
    wait_seconds 1
  done
  echo -e "$INFO Buscar en logs marketing (requiere docker logs manualmente):"
  echo -e "docker logs alpes-marketing | grep corr-demo"
}

# -----------------------------------------------------------------------------
# Escenario 7: Resiliencia - restart marketing mid-stream
# -----------------------------------------------------------------------------
function escenario_resiliencia_restart() {
  header "7 - Resiliencia (Restart Marketing)"
  local payload='{"nombre":"Campaña Restart","descripcion":"Antes restart","fecha_inicio":"2024-11-01","fecha_fin":"2024-11-30","presupuesto":3000.0}'
  curl -s -X POST "$BFF_URL/campanas" -H 'Content-Type: application/json' -d "$payload" >/dev/null
  wait_seconds 2
  echo -e "$INFO Reiniciando servicio marketing..."
  docker-compose restart marketing >/dev/null
  wait_seconds 8
  local payload2='{"nombre":"Campaña Post Restart","descripcion":"Después restart","fecha_inicio":"2024-11-01","fecha_fin":"2024-11-30","presupuesto":3500.0}'
  curl -s -X POST "$BFF_URL/campanas" -H 'Content-Type: application/json' -d "$payload2" >/dev/null
  wait_seconds 4
  sql_marketing "SELECT id,nombre,creada_en FROM campanas ORDER BY creada_en DESC LIMIT 2;"
}

# -----------------------------------------------------------------------------
# Escenario 8: Comisión - simular error (modificación manual sugerida)
# Sin hook directo; se instruye cómo provocar fallo temporal en repo o publisher.
# -----------------------------------------------------------------------------
function escenario_fallo_comision_doc() {
  header "8 - Documento: Simular fallo comisión"
  cat <<EOF
No existe un flag runtime para simular fallo. Opciones manuales:
1. Editar temporalmente 'calculo_inicial_handler.py' e introducir: raise Exception("Simulación error comisión") antes de persistir.
2. O detener momentáneamente Pulsar: docker stop alpes-pulsar (NO recomendado en entorno compartido).
3. Validar comportamiento: campaña persiste, evento ComisionCalculada no aparece o se loguea error.
EOF
}

# -----------------------------------------------------------------------------
# Runner principal
# -----------------------------------------------------------------------------
function help() {
  cat <<EOF
Uso: $0 [escenario]
Escenarios disponibles:
  all                      Ejecuta escenarios 1-7 (8 es documental)
  1|exitoso                Flujo básico exitoso
  2|fechas                 Fechas inválidas
  3|porcentaje             Porcentaje comisión extremo
  4|duplicado              Campañas con mismo nombre
  5|historico              Consumo histórico eventos
  6|correlacion            Correlación múltiples campañas
  7|resiliencia            Restart servicio marketing
  8|fallo-comision         Instrucciones simulación fallo comisión
EOF
}

case "${1:-all}" in
  1|exitoso) escenario_exitoso ;;
  2|fechas) escenario_fechas_invalidas ;;
  3|porcentaje) escenario_porcentaje_extremo ;;
  4|duplicado) escenario_duplicado_nombre ;;
  5|historico) escenario_consumo_historico ;;
  6|correlacion) escenario_correlacion ;;
  7|resiliencia) escenario_resiliencia_restart ;;
  8|fallo-comision) escenario_fallo_comision_doc ;;
  all)
    escenario_exitoso
    escenario_fechas_invalidas
    escenario_porcentaje_extremo
    escenario_duplicado_nombre
    escenario_consumo_historico
    escenario_correlacion
    escenario_resiliencia_restart
    escenario_fallo_comision_doc
    ;;
  *) help ;;
 esac
