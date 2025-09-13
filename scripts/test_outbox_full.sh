#!/usr/bin/env bash
# E2E test: crea campaña, la activa, (opcional) simula comisión y corre publisher
set -euo pipefail
API_CAMPANAS="http://localhost:5000/api/v1/campanas"

log(){ echo "[test] $*"; }

if ! command -v jq >/dev/null 2>&1; then
  echo "jq requerido" >&2; exit 1; fi

# 1. Crear Campaña
PAYLOAD='{
  "nombre": "Promo Correlacion",
  "descripcion": "Campaña correlacion",
  "marca": "ALPES",
  "categoria": "GENERICA",
  "tags": ["corr","chain"],
  "fecha_inicio": "'$(date -u -v+1d +%Y-%m-%dT%H:%M:%SZ)'",
  "fecha_fin": "'$(date -u -v+30d +%Y-%m-%dT%H:%M:%SZ)'",
  "porcentaje_base": 8.0,
  "porcentaje_premium": 12.0,
  "umbral_premium": 500.0,
  "moneda": "USD",
  "paises_permitidos": ["CO"],
  "regiones_excluidas": []
}'
log "Creando campaña..."
CAMPANA_ID=$(curl -s -X POST -H 'Content-Type: application/json' -d "$PAYLOAD" "$API_CAMPANAS" | jq -r '.campana_id')
log "Campaña: $CAMPANA_ID"

sleep 1
log "Activando..."
curl -s -X POST "$API_CAMPANAS/$CAMPANA_ID/activar" -H 'Content-Type: application/json' | jq '.' >/dev/null

# 2. Dump outbox antes publisher
if command -v mysql >/dev/null 2>&1; then
  log "Outbox (antes publisher)"
  mysql -h mysql -ualpes -palpes -D alpes -e "SELECT id,event_type,correlation_id,causation_id,published FROM outbox_event WHERE aggregate_id='$CAMPANA_ID' ORDER BY occurred_at;" || true
fi

# 3. Publisher dry-run
log "Publisher dry-run..."
DRY_RUN=true python scripts/outbox_publisher.py --batch-size 100 || true

# 4. Publisher real
log "Publisher real..."
python scripts/outbox_publisher.py --batch-size 100 || true

# 5. Dump outbox despues
if command -v mysql >/dev/null 2>&1; then
  log "Outbox (despues publisher)"
  mysql -h mysql -ualpes -palpes -D alpes -e "SELECT id,event_type,correlation_id,causation_id,published FROM outbox_event WHERE aggregate_id='$CAMPANA_ID' ORDER BY occurred_at;" || true
fi

log "OK"
