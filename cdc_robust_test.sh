#!/bin/bash

# Script de Pruebas CDC Simplificado y Robusto
# Genera eventos, procesa CDC y verifica hasta que todos estén publicados

echo "🚀 PRUEBAS CDC ROBUSTAS - AlpesPartner"
echo "======================================"

# Configuración
API_URL="http://localhost:5001"
MAX_ITERATIONS=15
WAIT_TIME=3

# Función para verificar si la API está disponible
check_api() {
    echo "🔍 Verificando API..."
    if curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo "✅ API disponible"
        return 0
    else
        echo "❌ API no disponible"
        return 1
    fi
}

# Función para crear comisión
create_commission() {
    local conv_id=$1
    local affiliate_id=$2
    local campaign_id=$3
    local amount=$4
    local currency=$5
    
    echo "📝 Creando comisión: $conv_id ($amount $currency)"
    
    response=$(curl -s -X POST "$API_URL/commissions/calculate" \
        -H "Content-Type: application/json" \
        -d "{
            \"conversionId\": \"$conv_id\",
            \"affiliateId\": \"$affiliate_id\",
            \"campaignId\": \"$campaign_id\",
            \"grossAmount\": $amount,
            \"currency\": \"$currency\"
        }" 2>/dev/null)
    
    if echo "$response" | grep -q "commissionId"; then
        commission_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('commissionId', 'N/A'))" 2>/dev/null)
        echo "   ✅ Comisión creada: $commission_id"
        return 0
    else
        echo "   ❌ Error creando comisión: $response"
        return 1
    fi
}

# Función para obtener estadísticas del outbox
get_outbox_stats() {
    response=$(curl -s "$API_URL/debug/outbox" 2>/dev/null)
    if [ $? -eq 0 ]; then
        total=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_events', 0))" 2>/dev/null)
        unpublished=$(echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
events = data.get('events', [])
unpublished = sum(1 for e in events if e.get('published') == 0)
print(unpublished)
" 2>/dev/null)
        
        echo "$total:$unpublished"
    else
        echo "0:0"
    fi
}

# Función para ejecutar CDC processor
run_cdc() {
    echo "🔄 Ejecutando procesador CDC..."
    cd "/Users/nicolasibarra/uniandes/miso-uniandes/semestre4/ciclo 1/Diseño y cosntrucción de soluciones no monoliticas/semana5/alpesPartner"
    
    output=$("/Users/nicolasibarra/uniandes/miso-uniandes/semestre4/ciclo 1/Diseño y cosntrucción de soluciones no monoliticas/semana5/alpesPartner/.venv/bin/python" manual_cdc.py 2>/dev/null)
    
    if echo "$output" | grep -q "eventos no publicados"; then
        processed=$(echo "$output" | grep -o "[0-9]* eventos no publicados" | grep -o "[0-9]*" | head -1)
        echo "   ✅ Procesados: $processed eventos"
        return 0
    else
        echo "   ✅ CDC ejecutado"
        return 0
    fi
}

# Verificar prerrequisitos
if ! check_api; then
    exit 1
fi

echo ""
echo "📊 Estado inicial del outbox:"
initial_stats=$(get_outbox_stats)
initial_total=$(echo "$initial_stats" | cut -d: -f1)
initial_unpublished=$(echo "$initial_stats" | cut -d: -f2)
echo "   Total eventos: $initial_total"
echo "   No publicados: $initial_unpublished"

echo ""
echo "🧪 GENERANDO ESCENARIOS DE PRUEBA"
echo "================================="

# Escenario 1: 3 comisiones normales
echo ""
echo "🎯 Escenario 1: Comisiones variadas"
timestamp=$(date +%s)

create_commission "test-conv-${timestamp}-1" "aff-001" "camp-retail" 1500.50 "USD"
sleep 1
create_commission "test-conv-${timestamp}-2" "aff-002" "camp-luxury" 3200.75 "EUR"
sleep 1
create_commission "test-conv-${timestamp}-3" "aff-003" "camp-tech" 950.25 "GBP"

# Escenario 2: Comisión con moneda diferente
echo ""
echo "🎯 Escenario 2: Comisión en CAD"
sleep 1
create_commission "test-conv-${timestamp}-4" "aff-004" "camp-canada" 2500.00 "CAD"

echo ""
echo "📊 Estado después de crear eventos:"
post_create_stats=$(get_outbox_stats)
post_create_total=$(echo "$post_create_stats" | cut -d: -f1)
post_create_unpublished=$(echo "$post_create_stats" | cut -d: -f2)
echo "   Total eventos: $post_create_total"
echo "   No publicados: $post_create_unpublished"

# Monitoreo y procesamiento CDC
echo ""
echo "🔄 INICIANDO MONITOREO CDC"
echo "=========================="

iteration=0
while [ $iteration -lt $MAX_ITERATIONS ]; do
    iteration=$((iteration + 1))
    
    echo ""
    echo "--- Iteración $iteration/$MAX_ITERATIONS ---"
    
    # Obtener estadísticas actuales
    current_stats=$(get_outbox_stats)
    current_total=$(echo "$current_stats" | cut -d: -f1)
    current_unpublished=$(echo "$current_stats" | cut -d: -f2)
    
    echo "📊 Estado actual - Total: $current_total | No publicados: $current_unpublished"
    
    if [ "$current_unpublished" -gt 0 ]; then
        echo "🔄 Hay $current_unpublished eventos pendientes, procesando..."
        
        # Ejecutar CDC
        run_cdc
        
        # Verificar nuevamente después del procesamiento
        echo "⏳ Esperando $WAIT_TIME segundos para verificar..."
        sleep $WAIT_TIME
        
        post_cdc_stats=$(get_outbox_stats)
        post_cdc_unpublished=$(echo "$post_cdc_stats" | cut -d: -f2)
        
        if [ "$post_cdc_unpublished" -lt "$current_unpublished" ]; then
            echo "✅ Progreso: $((current_unpublished - post_cdc_unpublished)) eventos procesados"
        fi
        
    else
        echo "🎉 ¡Todos los eventos están publicados!"
        break
    fi
    
    # Pausa antes de la siguiente iteración
    if [ $iteration -lt $MAX_ITERATIONS ]; then
        echo "⏳ Esperando $WAIT_TIME segundos antes de la siguiente verificación..."
        sleep $WAIT_TIME
    fi
done

# Resumen final
echo ""
echo "📊 RESUMEN FINAL"
echo "================"

final_stats=$(get_outbox_stats)
final_total=$(echo "$final_stats" | cut -d: -f1)
final_unpublished=$(echo "$final_stats" | cut -d: -f2)
final_published=$((final_total - final_unpublished))

echo "📈 Total eventos generados: $final_total"
echo "✅ Eventos publicados: $final_published"
echo "⏳ Eventos pendientes: $final_unpublished"

events_created=$((final_total - initial_total))
echo "🆕 Nuevos eventos en esta prueba: $events_created"

if [ "$final_unpublished" -eq 0 ]; then
    echo ""
    echo "🎉 ¡ÉXITO! Todos los eventos han sido publicados correctamente"
    echo "✅ El sistema CDC está funcionando perfectamente"
else
    echo ""
    echo "⚠️  Hay $final_unpublished eventos pendientes de publicar"
    echo "🔍 Puede necesitar más tiempo o verificar la conectividad de Pulsar"
fi

echo ""
echo "✅ Pruebas CDC completadas"
echo "=========================="
