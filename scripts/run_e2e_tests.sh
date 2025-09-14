#!/bin/bash

# =============================================================================
# Script de casos de prueba End-to-End - AlpesPartner Ecosystem
# =============================================================================

set -e

echo "🧪 Ejecutando casos de prueba End-to-End para AlpesPartner Ecosystem..."

# Configuración de servicios
AFILIADOS_URL="http://localhost:8001"
CONVERSIONES_URL="http://localhost:8002"
MARKETING_URL="http://localhost:8003"
PULSAR_ADMIN_URL="http://localhost:8080"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores de pruebas
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Función para logging con color
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para verificar respuesta HTTP
check_http_response() {
    local response=$1
    local expected_status=${2:-200}
    local test_name=$3
    
    ((TOTAL_TESTS++))
    
    if echo "$response" | head -n 1 | grep -q "$expected_status"; then
        log_success "$test_name"
        return 0
    else
        log_error "$test_name - Status code: $(echo "$response" | head -n 1)"
        return 1
    fi
}

# Función para verificar JSON response
check_json_field() {
    local json=$1
    local field=$2
    local test_name=$3
    
    ((TOTAL_TESTS++))
    
    if echo "$json" | jq -e ".$field" >/dev/null 2>&1; then
        local value=$(echo "$json" | jq -r ".$field")
        log_success "$test_name - Valor: $value"
        return 0
    else
        log_error "$test_name - Campo $field no encontrado"
        return 1
    fi
}

# Función para esperar eventos en Pulsar
wait_for_pulsar_events() {
    local topic=$1
    local expected_count=${2:-1}
    local timeout=${3:-30}
    
    log_info "Esperando $expected_count eventos en tópico $topic (timeout: ${timeout}s)..."
    
    local count=0
    local attempts=0
    local max_attempts=$((timeout / 2))
    
    while [ $attempts -lt $max_attempts ]; do
        # Verificar estadísticas del tópico
        local stats=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/persistent/public/default/$topic/stats" 2>/dev/null || echo "{}")
        
        if [ "$stats" != "{}" ]; then
            local msg_count=$(echo "$stats" | jq -r '.msgInCounter // 0' 2>/dev/null || echo "0")
            if [ "$msg_count" -ge "$expected_count" ]; then
                log_success "Eventos encontrados en $topic: $msg_count"
                return 0
            fi
        fi
        
        sleep 2
        ((attempts++))
    done
    
    log_warning "Timeout esperando eventos en $topic"
    return 1
}

# Función para verificar conectividad de servicios
verify_services() {
    log_info "Verificando conectividad de servicios..."
    
    # Verificar Afiliados
    local afiliados_health=$(curl -s -w "%{http_code}" "$AFILIADOS_URL/health" -o /dev/null)
    check_http_response "$afiliados_health" "200" "Servicio Afiliados disponible"
    
    # Verificar Conversiones
    local conversiones_health=$(curl -s -w "%{http_code}" "$CONVERSIONES_URL/health" -o /dev/null)
    check_http_response "$conversiones_health" "200" "Servicio Conversiones disponible"
    
    # Verificar Marketing
    local marketing_health=$(curl -s -w "%{http_code}" "$MARKETING_URL/health" -o /dev/null)
    check_http_response "$marketing_health" "200" "Servicio Marketing disponible"
    
    # Verificar Pulsar
    local pulsar_health=$(curl -s -w "%{http_code}" "$PULSAR_ADMIN_URL/admin/v2/clusters" -o /dev/null)
    check_http_response "$pulsar_health" "200" "Apache Pulsar disponible"
}

# Caso de prueba 1: Flujo completo de afiliado premium
test_case_1_premium_affiliate() {
    echo ""
    log_info "🎯 CASO DE PRUEBA 1: Flujo completo afiliado premium"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 1.1 Crear afiliado premium
    log_info "1.1 Creando afiliado premium..."
    local afiliado_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$AFILIADOS_URL/api/v1/afiliados" \
        -H "Content-Type: application/json" \
        -d '{
            "nombre": "Elena Martínez Premium",
            "email": "elena.martinez@premium.com",
            "telefono": "+57 320 555 1234",
            "documento": {
                "tipo": "cedula",
                "numero": "1122334455"
            },
            "tipo_afiliado": "premium",
            "datos_bancarios": {
                "banco": "Banco Premium",
                "tipo_cuenta": "ahorros",
                "numero_cuenta": "1122334455"
            },
            "configuracion_comisiones": {
                "comision_base": 18.0,
                "comision_premium": 25.0,
                "minimo_pago": 100000.0
            }
        }')
    
    local afiliado_body=$(echo "$afiliado_response" | sed -E 's/HTTPSTATUS:[0-9]{3}$//')
    local afiliado_status=$(echo "$afiliado_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    
    check_http_response "HTTP/1.1 $afiliado_status" "201" "Afiliado premium creado"
    
    local afiliado_id=$(echo "$afiliado_body" | jq -r '.afiliado_id')
    check_json_field "$afiliado_body" "afiliado_id" "ID de afiliado generado"
    
    # 1.2 Crear campaña premium
    log_info "1.2 Creando campaña premium..."
    local campana_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$MARKETING_URL/api/v1/campanas" \
        -H "Content-Type: application/json" \
        -d '{
            "nombre": "Campaña Premium Test E2E",
            "descripcion": "Campaña de prueba para afiliados premium",
            "fecha_inicio": "2023-12-01T00:00:00Z",
            "fecha_fin": "2023-12-31T23:59:59Z",
            "presupuesto": 1000000.0,
            "moneda": "COP",
            "tipo_campana": "premium",
            "canales": ["web", "mobile", "email"],
            "configuracion_comisiones": {
                "comision_conversion": 25.0,
                "comision_venta": 15.0,
                "bonus_objetivos": 40.0
            }
        }')
    
    local campana_body=$(echo "$campana_response" | sed -E 's/HTTPSTATUS:[0-9]{3}$//')
    local campana_status=$(echo "$campana_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    
    check_http_response "HTTP/1.1 $campana_status" "201" "Campaña premium creada"
    
    local campana_id=$(echo "$campana_body" | jq -r '.campana_id')
    check_json_field "$campana_body" "campana_id" "ID de campaña generado"
    
    # 1.3 Registrar conversión de alto valor
    log_info "1.3 Registrando conversión de alto valor..."
    local conversion_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$CONVERSIONES_URL/api/v1/conversiones" \
        -H "Content-Type: application/json" \
        -d "{
            \"afiliado_id\": \"$afiliado_id\",
            \"campana_id\": \"$campana_id\",
            \"tipo_conversion\": \"venta\",
            \"valor_conversion\": 500000.0,
            \"moneda\": \"COP\",
            \"canal_origen\": \"web\",
            \"datos_cliente\": {
                \"email\": \"cliente.premium@test.com\",
                \"ubicacion\": \"Bogotá\",
                \"dispositivo\": \"desktop\"
            },
            \"productos\": [
                {
                    \"id\": \"PREMIUM001\",
                    \"nombre\": \"Producto Premium\",
                    \"categoria\": \"Premium\",
                    \"precio\": 500000.0,
                    \"cantidad\": 1
                }
            ]
        }")
    
    local conversion_body=$(echo "$conversion_response" | sed -E 's/HTTPSTATUS:[0-9]{3}$//')
    local conversion_status=$(echo "$conversion_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    
    check_http_response "HTTP/1.1 $conversion_status" "201" "Conversión de alto valor registrada"
    
    local conversion_id=$(echo "$conversion_body" | jq -r '.conversion_id')
    check_json_field "$conversion_body" "conversion_id" "ID de conversión generado"
    
    # 1.4 Esperar eventos de conversión
    wait_for_pulsar_events "conversiones.eventos" 1 30
    
    # 1.5 Crear comisión
    log_info "1.5 Creando comisión para conversión premium..."
    local comision_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$MARKETING_URL/api/v1/comisiones" \
        -H "Content-Type: application/json" \
        -d "{
            \"afiliado_id\": \"$afiliado_id\",
            \"campana_id\": \"$campana_id\",
            \"conversion_id\": \"$conversion_id\",
            \"monto_base\": {
                \"valor\": 500000.0,
                \"moneda\": \"COP\"
            },
            \"tipo_comision\": \"porcentual\",
            \"porcentaje\": 25.0,
            \"configuracion\": {
                \"aplicar_descuentos\": false,
                \"incluir_iva\": true
            }
        }")
    
    local comision_body=$(echo "$comision_response" | sed -E 's/HTTPSTATUS:[0-9]{3}$//')
    local comision_status=$(echo "$comision_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    
    check_http_response "HTTP/1.1 $comision_status" "201" "Comisión premium creada"
    
    local comision_id=$(echo "$comision_body" | jq -r '.comision_id')
    check_json_field "$comision_body" "comision_id" "ID de comisión generado"
    
    # 1.6 Calcular comisión
    log_info "1.6 Calculando comisión..."
    local calculo_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$MARKETING_URL/api/v1/comisiones/$comision_id/calcular" \
        -H "Content-Type: application/json" \
        -d '{"forzar_recalculo": false}')
    
    local calculo_status=$(echo "$calculo_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    check_http_response "HTTP/1.1 $calculo_status" "200" "Comisión calculada correctamente"
    
    # 1.7 Esperar eventos de comisión
    wait_for_pulsar_events "comisiones.eventos" 1 30
    
    # 1.8 Aprobar comisión
    log_info "1.8 Aprobando comisión..."
    local aprobacion_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$MARKETING_URL/api/v1/comisiones/$comision_id/aprobar" \
        -H "Content-Type: application/json" \
        -d '{
            "comentarios": "Comisión premium aprobada - E2E test",
            "metadatos_aprobacion": {
                "nivel_aprobacion": "automatico",
                "test_e2e": true
            }
        }')
    
    local aprobacion_status=$(echo "$aprobacion_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    check_http_response "HTTP/1.1 $aprobacion_status" "200" "Comisión aprobada exitosamente"
    
    # 1.9 Verificar estado final
    log_info "1.9 Verificando estado final de la comisión..."
    local estado_response=$(curl -s "$MARKETING_URL/api/v1/comisiones/$comision_id")
    
    check_json_field "$estado_response" "estado" "Estado de comisión disponible"
    local estado_actual=$(echo "$estado_response" | jq -r '.estado')
    
    if [ "$estado_actual" = "aprobada" ]; then
        log_success "Comisión en estado aprobada correctamente"
    else
        log_error "Comisión en estado incorrecto: $estado_actual"
    fi
    
    # 1.10 Verificar monto calculado
    local monto_calculado=$(echo "$estado_response" | jq -r '.monto_calculado // 0')
    if (( $(echo "$monto_calculado > 100000" | bc -l) )); then
        log_success "Monto calculado correcto: $monto_calculado COP"
    else
        log_error "Monto calculado incorrecto: $monto_calculado COP"
    fi
    
    echo ""
    log_info "📊 Caso de prueba 1 completado"
    echo "   • Afiliado ID: $afiliado_id"
    echo "   • Campaña ID: $campana_id"
    echo "   • Conversión ID: $conversion_id"
    echo "   • Comisión ID: $comision_id"
    echo "   • Monto final: $monto_calculado COP"
}

# Caso de prueba 2: Flujo con múltiples conversiones
test_case_2_multiple_conversions() {
    echo ""
    log_info "🎯 CASO DE PRUEBA 2: Múltiples conversiones para mismo afiliado"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Usar datos existentes del archivo test_data_ids.json si existe
    if [ -f "test_data_ids.json" ]; then
        local existing_afiliado=$(jq -r '.afiliados[0].id' test_data_ids.json 2>/dev/null || echo "")
        local existing_campana=$(jq -r '.campanas[0].id' test_data_ids.json 2>/dev/null || echo "")
        
        if [ -n "$existing_afiliado" ] && [ "$existing_afiliado" != "null" ] && [ -n "$existing_campana" ] && [ "$existing_campana" != "null" ]; then
            log_info "2.1 Usando afiliado y campaña existentes..."
            
            # 2.1 Crear múltiples conversiones
            for i in {1..3}; do
                log_info "2.$((i+1)) Creando conversión $i..."
                local valor=$((150000 + i * 50000))
                
                local conversion_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$CONVERSIONES_URL/api/v1/conversiones" \
                    -H "Content-Type: application/json" \
                    -d "{
                        \"afiliado_id\": \"$existing_afiliado\",
                        \"campana_id\": \"$existing_campana\",
                        \"tipo_conversion\": \"venta\",
                        \"valor_conversion\": $valor.0,
                        \"moneda\": \"COP\",
                        \"canal_origen\": \"mobile\",
                        \"datos_cliente\": {
                            \"email\": \"cliente$i@test.com\",
                            \"ubicacion\": \"Medellín\",
                            \"dispositivo\": \"mobile\"
                        },
                        \"productos\": [
                            {
                                \"id\": \"MULTI00$i\",
                                \"nombre\": \"Producto Multi $i\",
                                \"categoria\": \"Tecnología\",
                                \"precio\": $valor.0,
                                \"cantidad\": 1
                            }
                        ]
                    }")
                
                local conversion_status=$(echo "$conversion_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
                check_http_response "HTTP/1.1 $conversion_status" "201" "Conversión $i creada"
                
                # Crear comisión correspondiente
                local conversion_body=$(echo "$conversion_response" | sed -E 's/HTTPSTATUS:[0-9]{3}$//')
                local conversion_id=$(echo "$conversion_body" | jq -r '.conversion_id')
                
                local comision_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$MARKETING_URL/api/v1/comisiones" \
                    -H "Content-Type: application/json" \
                    -d "{
                        \"afiliado_id\": \"$existing_afiliado\",
                        \"campana_id\": \"$existing_campana\",
                        \"conversion_id\": \"$conversion_id\",
                        \"monto_base\": {
                            \"valor\": $valor.0,
                            \"moneda\": \"COP\"
                        },
                        \"tipo_comision\": \"porcentual\",
                        \"porcentaje\": 15.0
                    }")
                
                local comision_status=$(echo "$comision_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
                check_http_response "HTTP/1.1 $comision_status" "201" "Comisión $i creada"
                
                sleep 1  # Pequeña pausa entre conversiones
            done
            
            # 2.5 Esperar procesamiento de eventos
            wait_for_pulsar_events "conversiones.eventos" 3 45
            wait_for_pulsar_events "comisiones.eventos" 3 45
            
            log_success "Múltiples conversiones procesadas correctamente"
        else
            log_warning "No se encontraron datos existentes, saltando caso de prueba 2"
        fi
    else
        log_warning "Archivo test_data_ids.json no encontrado, saltando caso de prueba 2"
    fi
}

# Caso de prueba 3: Validación de eventos Pulsar
test_case_3_pulsar_events() {
    echo ""
    log_info "🎯 CASO DE PRUEBA 3: Validación de eventos Pulsar"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 3.1 Verificar tópicos configurados
    log_info "3.1 Verificando tópicos Pulsar configurados..."
    
    local topics=("afiliados.eventos" "conversiones.eventos" "marketing.eventos" "comisiones.eventos" "auditoria.eventos" "sistema.eventos")
    
    for topic in "${topics[@]}"; do
        local topic_stats=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/persistent/public/default/$topic/stats" 2>/dev/null || echo "{}")
        
        if [ "$topic_stats" != "{}" ]; then
            log_success "Tópico $topic existe y es accesible"
            
            # Verificar subscripciones
            local subscriptions=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/persistent/public/default/$topic/subscriptions" 2>/dev/null || echo "[]")
            local sub_count=$(echo "$subscriptions" | jq '. | length' 2>/dev/null || echo "0")
            
            if [ "$sub_count" -gt 0 ]; then
                log_success "Tópico $topic tiene $sub_count subscripciones"
            else
                log_warning "Tópico $topic no tiene subscripciones"
            fi
        else
            log_error "Tópico $topic no accesible"
        fi
    done
    
    # 3.2 Verificar producción de eventos
    log_info "3.2 Verificando producción de eventos..."
    
    # Crear un evento de prueba simple
    local test_conversion=$(curl -s -w "HTTPSTATUS:%{http_code}" "$CONVERSIONES_URL/api/v1/conversiones" \
        -H "Content-Type: application/json" \
        -d '{
            "afiliado_id": "test-afiliado-events",
            "campana_id": "test-campana-events",
            "tipo_conversion": "lead",
            "valor_conversion": 50000.0,
            "moneda": "COP",
            "canal_origen": "test",
            "datos_cliente": {
                "email": "test@events.com",
                "ubicacion": "Test City",
                "dispositivo": "test"
            }
        }')
    
    local test_status=$(echo "$test_conversion" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    check_http_response "HTTP/1.1 $test_status" "201" "Evento de prueba creado"
    
    # Esperar y verificar el evento
    sleep 5
    wait_for_pulsar_events "conversiones.eventos" 1 30
}

# Caso de prueba 4: APIs de consulta
test_case_4_query_apis() {
    echo ""
    log_info "🎯 CASO DE PRUEBA 4: APIs de consulta y reportes"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 4.1 Consultar afiliados
    log_info "4.1 Consultando lista de afiliados..."
    local afiliados_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$AFILIADOS_URL/api/v1/afiliados")
    local afiliados_status=$(echo "$afiliados_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    
    check_http_response "HTTP/1.1 $afiliados_status" "200" "Lista de afiliados obtenida"
    
    # 4.2 Consultar campañas
    log_info "4.2 Consultando campañas activas..."
    local campanas_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$MARKETING_URL/api/v1/campanas")
    local campanas_status=$(echo "$campanas_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    
    check_http_response "HTTP/1.1 $campanas_status" "200" "Lista de campañas obtenida"
    
    # 4.3 Consultar conversiones
    log_info "4.3 Consultando conversiones registradas..."
    local conversiones_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$CONVERSIONES_URL/api/v1/conversiones")
    local conversiones_status=$(echo "$conversiones_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    
    check_http_response "HTTP/1.1 $conversiones_status" "200" "Lista de conversiones obtenida"
    
    # 4.4 Consultar comisiones
    log_info "4.4 Consultando comisiones calculadas..."
    local comisiones_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$MARKETING_URL/api/v1/comisiones")
    local comisiones_status=$(echo "$comisiones_response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
    
    check_http_response "HTTP/1.1 $comisiones_status" "200" "Lista de comisiones obtenida"
    
    # 4.5 Verificar datos en respuestas
    local afiliados_body=$(echo "$afiliados_response" | sed -E 's/HTTPSTATUS:[0-9]{3}$//')
    local afiliados_count=$(echo "$afiliados_body" | jq '. | length' 2>/dev/null || echo "0")
    
    if [ "$afiliados_count" -gt 0 ]; then
        log_success "Datos de afiliados disponibles ($afiliados_count registros)"
    else
        log_warning "No hay datos de afiliados disponibles"
    fi
}

# Función principal de reporte
generate_test_report() {
    echo ""
    echo "📊 REPORTE FINAL DE PRUEBAS E2E"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📈 Estadísticas:"
    echo "   • Total de pruebas ejecutadas: $TOTAL_TESTS"
    echo "   • Pruebas exitosas: $TESTS_PASSED"
    echo "   • Pruebas fallidas: $TESTS_FAILED"
    
    local success_rate=$((TESTS_PASSED * 100 / TOTAL_TESTS))
    echo "   • Tasa de éxito: ${success_rate}%"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!${NC}"
        echo ""
        echo "✅ El ecosistema AlpesPartner funciona correctamente:"
        echo "   • Comunicación entre microservicios ✓"
        echo "   • Eventos Pulsar funcionando ✓"
        echo "   • APIs REST respondiendo ✓"
        echo "   • Flujos de comisiones completos ✓"
    else
        echo -e "${RED}⚠️  ALGUNAS PRUEBAS FALLARON${NC}"
        echo ""
        echo "❌ Problemas detectados:"
        echo "   • Revisar logs de servicios"
        echo "   • Verificar configuración de Pulsar"
        echo "   • Validar conectividad entre servicios"
    fi
    
    echo ""
    echo "🔗 URLs útiles para debugging:"
    echo "   • Afiliados API: $AFILIADOS_URL/docs"
    echo "   • Conversiones API: $CONVERSIONES_URL/docs"
    echo "   • Marketing API: $MARKETING_URL/docs"
    echo "   • Pulsar Manager: http://localhost:9527"
    echo "   • phpMyAdmin: http://localhost:8082"
    echo "   • Redis Commander: http://localhost:8081"
    
    # Guardar reporte
    cat > e2e_test_report.json << EOF
{
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "total_tests": $TOTAL_TESTS,
    "tests_passed": $TESTS_PASSED,
    "tests_failed": $TESTS_FAILED,
    "success_rate": $success_rate,
    "services": {
        "afiliados": "$AFILIADOS_URL",
        "conversiones": "$CONVERSIONES_URL",
        "marketing": "$MARKETING_URL",
        "pulsar": "$PULSAR_ADMIN_URL"
    },
    "test_status": "$([ $TESTS_FAILED -eq 0 ] && echo "PASSED" || echo "FAILED")"
}
EOF
    
    echo ""
    echo "💾 Reporte guardado en: e2e_test_report.json"
}

# Función principal
main() {
    echo "🚀 Iniciando pruebas End-to-End de AlpesPartner Ecosystem"
    echo "$(date)"
    echo ""
    
    # Verificar servicios
    verify_services
    
    if [ $TESTS_FAILED -gt 0 ]; then
        log_error "Servicios no disponibles. Abortando pruebas E2E."
        exit 1
    fi
    
    # Ejecutar casos de prueba
    test_case_1_premium_affiliate
    test_case_2_multiple_conversions
    test_case_3_pulsar_events
    test_case_4_query_apis
    
    # Generar reporte final
    generate_test_report
    
    # Código de salida basado en resultados
    if [ $TESTS_FAILED -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Verificar dependencias
if ! command -v curl &> /dev/null; then
    echo "❌ curl no está instalado. Por favor instálalo primero."
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "❌ jq no está instalado. Por favor instálalo primero."
    exit 1
fi

if ! command -v bc &> /dev/null; then
    echo "❌ bc no está instalado. Por favor instálalo primero."
    exit 1
fi

# Ejecutar función principal
main