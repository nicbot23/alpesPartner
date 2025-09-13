#!/usr/bin/env bash
# Quick E2E smoke test for Campanas + Outbox
set -euo pipefail
API_URL="http://localhost:5000/api/v1/campanas"

echo "[1] Creando campaña..."
CREATE_PAYLOAD='{
  "nombre": "Promo Q4",
  "descripcion": "Campaña de fin de año",
  "marca": "ALPES",
  "categoria": "GENERICA",
  "tags": ["q4","premium"],
  "fecha_inicio": "'$(date -u -v+5M +%Y-%m-%dT%H:%M:%SZ)'",
  "fecha_fin": "'$(date -u -v+10M +%Y-%m-%dT%H:%M:%SZ)'",
  "porcentaje_base": 10.0,
  "porcentaje_premium": 15.0,
  "umbral_premium": 1000.0,
  "moneda": "USD",
  "paises_permitidos": ["CO","US"],
  "regiones_excluidas": ["AK"]
}'
CAMPANA_ID=$(curl -s -X POST -H 'Content-Type: application/json' -d "$CREATE_PAYLOAD" "$API_URL" | jq -r '.campana_id')

echo "Campaña creada: $CAMPANA_ID"

sleep 1

echo "[2] Activando campaña..."
curl -s -X POST "$API_URL/$CAMPANA_ID/activar" -H 'Content-Type: application/json' | jq '.'

sleep 1

echo "[3] Consultando campaña..."
curl -s "$API_URL/$CAMPANA_ID" | jq '.'

# Outbox dump (direct SQL) si mysql cliente disponible
if command -v mysql >/dev/null 2>&1; then
  echo "[4] Events en outbox (ultimos 5 Campana*)"
  mysql -h mysql -ualpes -palpes -D alpes -e "SELECT event_type, aggregate_id, JSON_EXTRACT(payload,'$.eventType') as evt, occurred_at FROM outbox_event WHERE aggregate_type='Campana' ORDER BY occurred_at DESC LIMIT 5;" || true
else
  echo "[WARN] mysql client no disponible; salteando verificación directa de outbox"
fi

echo "OK"
