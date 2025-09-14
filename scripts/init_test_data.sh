#!/bin/bash

# =============================================================================
# Script de inicialización de datos de prueba - AlpesPartner Ecosystem
# =============================================================================

set -e

echo "🚀 Iniciando configuración de datos de prueba para AlpesPartner Ecosystem..."

# Configuración de servicios
AFILIADOS_URL="http://localhost:8001"
CONVERSIONES_URL="http://localhost:8002" 
MARKETING_URL="http://localhost:8003"

# Función para esperar que un servicio esté disponible
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Esperando que $service_name esté disponible en $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$url/health" >/dev/null 2>&1; then
            echo "✅ $service_name está disponible"
            return 0
        fi
        
        echo "🔄 Intento $attempt/$max_attempts - $service_name no disponible, esperando..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name no está disponible después de $max_attempts intentos"
    return 1
}

# Función para crear datos de prueba
create_test_data() {
    echo "📊 Creando datos de prueba..."
    
    # 1. Crear afiliados de prueba
    echo "👥 Creando afiliados de prueba..."
    
    AFILIADO1_RESPONSE=$(curl -s -X POST "$AFILIADOS_URL/api/v1/afiliados" \
        -H "Content-Type: application/json" \
        -d '{
            "nombre": "María González",
            "email": "maria.gonzalez@email.com",
            "telefono": "+57 300 123 4567",
            "documento": {
                "tipo": "cedula",
                "numero": "1234567890"
            },
            "tipo_afiliado": "premium",
            "datos_bancarios": {
                "banco": "Banco Nacional",
                "tipo_cuenta": "ahorros",
                "numero_cuenta": "1234567890"
            },
            "configuracion_comisiones": {
                "comision_base": 15.0,
                "comision_premium": 20.0,
                "minimo_pago": 50000.0
            }
        }')
    
    AFILIADO1_ID=$(echo $AFILIADO1_RESPONSE | jq -r '.afiliado_id')
    echo "✅ Afiliado 1 creado: $AFILIADO1_ID"
    
    AFILIADO2_RESPONSE=$(curl -s -X POST "$AFILIADOS_URL/api/v1/afiliados" \
        -H "Content-Type: application/json" \
        -d '{
            "nombre": "Carlos Rodríguez",
            "email": "carlos.rodriguez@email.com",
            "telefono": "+57 310 987 6543",
            "documento": {
                "tipo": "cedula",
                "numero": "9876543210"
            },
            "tipo_afiliado": "estandar",
            "datos_bancarios": {
                "banco": "Banco Popular",
                "tipo_cuenta": "corriente",
                "numero_cuenta": "9876543210"
            },
            "configuracion_comisiones": {
                "comision_base": 12.0,
                "comision_premium": 18.0,
                "minimo_pago": 30000.0
            }
        }')
    
    AFILIADO2_ID=$(echo $AFILIADO2_RESPONSE | jq -r '.afiliado_id')
    echo "✅ Afiliado 2 creado: $AFILIADO2_ID"
    
    # 2. Crear campañas de marketing
    echo "📢 Creando campañas de marketing..."
    
    CAMPANA1_RESPONSE=$(curl -s -X POST "$MARKETING_URL/api/v1/campanas" \
        -H "Content-Type: application/json" \
        -d '{
            "nombre": "Campaña Black Friday 2023",
            "descripcion": "Promoción especial de Black Friday con descuentos hasta 50%",
            "fecha_inicio": "2023-11-24T00:00:00Z",
            "fecha_fin": "2023-11-27T23:59:59Z",
            "presupuesto": 500000.0,
            "moneda": "COP",
            "tipo_campana": "promocional",
            "canales": ["web", "email", "social"],
            "segmentacion": {
                "edad_minima": 18,
                "edad_maxima": 65,
                "ubicaciones": ["Bogotá", "Medellín", "Cali"]
            },
            "configuracion_comisiones": {
                "comision_conversion": 15.0,
                "comision_venta": 8.0,
                "bonus_objetivos": 25.0
            }
        }')
    
    CAMPANA1_ID=$(echo $CAMPANA1_RESPONSE | jq -r '.campana_id')
    echo "✅ Campaña 1 creada: $CAMPANA1_ID"
    
    CAMPANA2_RESPONSE=$(curl -s -X POST "$MARKETING_URL/api/v1/campanas" \
        -H "Content-Type: application/json" \
        -d '{
            "nombre": "Campaña Navideña Premium",
            "descripcion": "Campaña especial navideña para productos premium",
            "fecha_inicio": "2023-12-01T00:00:00Z",
            "fecha_fin": "2023-12-31T23:59:59Z",
            "presupuesto": 750000.0,
            "moneda": "COP",
            "tipo_campana": "premium",
            "canales": ["web", "mobile", "email"],
            "segmentacion": {
                "edad_minima": 25,
                "edad_maxima": 55,
                "ubicaciones": ["Bogotá", "Medellín"],
                "ingresos_minimos": 5000000
            },
            "configuracion_comisiones": {
                "comision_conversion": 20.0,
                "comision_venta": 12.0,
                "bonus_objetivos": 35.0
            }
        }')
    
    CAMPANA2_ID=$(echo $CAMPANA2_RESPONSE | jq -r '.campana_id')
    echo "✅ Campaña 2 creada: $CAMPANA2_ID"
    
    # 3. Crear conversiones de prueba
    echo "🎯 Creando conversiones de prueba..."
    
    CONVERSION1_RESPONSE=$(curl -s -X POST "$CONVERSIONES_URL/api/v1/conversiones" \
        -H "Content-Type: application/json" \
        -d "{
            \"afiliado_id\": \"$AFILIADO1_ID\",
            \"campana_id\": \"$CAMPANA1_ID\",
            \"tipo_conversion\": \"venta\",
            \"valor_conversion\": 250000.0,
            \"moneda\": \"COP\",
            \"canal_origen\": \"web\",
            \"datos_cliente\": {
                \"email\": \"cliente1@email.com\",
                \"ubicacion\": \"Bogotá\",
                \"dispositivo\": \"desktop\"
            },
            \"productos\": [
                {
                    \"id\": \"PROD001\",
                    \"nombre\": \"Laptop Gaming\",
                    \"categoria\": \"Tecnología\",
                    \"precio\": 250000.0,
                    \"cantidad\": 1
                }
            ],
            \"metadatos\": {
                \"utm_source\": \"google\",
                \"utm_campaign\": \"black_friday\",
                \"utm_medium\": \"cpc\"
            }
        }")
    
    CONVERSION1_ID=$(echo $CONVERSION1_RESPONSE | jq -r '.conversion_id')
    echo "✅ Conversión 1 creada: $CONVERSION1_ID"
    
    CONVERSION2_RESPONSE=$(curl -s -X POST "$CONVERSIONES_URL/api/v1/conversiones" \
        -H "Content-Type: application/json" \
        -d "{
            \"afiliado_id\": \"$AFILIADO2_ID\",
            \"campana_id\": \"$CAMPANA2_ID\",
            \"tipo_conversion\": \"lead\",
            \"valor_conversion\": 150000.0,
            \"moneda\": \"COP\",
            \"canal_origen\": \"mobile\",
            \"datos_cliente\": {
                \"email\": \"cliente2@email.com\",
                \"ubicacion\": \"Medellín\",
                \"dispositivo\": \"mobile\"
            },
            \"productos\": [
                {
                    \"id\": \"PROD002\",
                    \"nombre\": \"Smartphone Premium\",
                    \"categoria\": \"Tecnología\",
                    \"precio\": 150000.0,
                    \"cantidad\": 1
                }
            ],
            \"metadatos\": {
                \"utm_source\": \"facebook\",
                \"utm_campaign\": \"navidad_premium\",
                \"utm_medium\": \"social\"
            }
        }")
    
    CONVERSION2_ID=$(echo $CONVERSION2_RESPONSE | jq -r '.conversion_id')
    echo "✅ Conversión 2 creada: $CONVERSION2_ID"
    
    # 4. Crear comisiones (Marketing coordinará automáticamente)
    echo "💰 Creando comisiones automáticamente..."
    
    COMISION1_RESPONSE=$(curl -s -X POST "$MARKETING_URL/api/v1/comisiones" \
        -H "Content-Type: application/json" \
        -d "{
            \"afiliado_id\": \"$AFILIADO1_ID\",
            \"campana_id\": \"$CAMPANA1_ID\",
            \"conversion_id\": \"$CONVERSION1_ID\",
            \"monto_base\": {
                \"valor\": 250000.0,
                \"moneda\": \"COP\"
            },
            \"tipo_comision\": \"porcentual\",
            \"porcentaje\": 15.0,
            \"configuracion\": {
                \"aplicar_descuentos\": true,
                \"incluir_iva\": false
            },
            \"metadatos\": {
                \"canal_origen\": \"web\",
                \"categoria_producto\": \"tecnologia\"
            }
        }")
    
    COMISION1_ID=$(echo $COMISION1_RESPONSE | jq -r '.comision_id')
    echo "✅ Comisión 1 creada: $COMISION1_ID"
    
    COMISION2_RESPONSE=$(curl -s -X POST "$MARKETING_URL/api/v1/comisiones" \
        -H "Content-Type: application/json" \
        -d "{
            \"afiliado_id\": \"$AFILIADO2_ID\",
            \"campana_id\": \"$CAMPANA2_ID\",
            \"conversion_id\": \"$CONVERSION2_ID\",
            \"monto_base\": {
                \"valor\": 150000.0,
                \"moneda\": \"COP\"
            },
            \"tipo_comision\": \"porcentual\",
            \"porcentaje\": 20.0,
            \"configuracion\": {
                \"aplicar_descuentos\": false,
                \"incluir_iva\": true
            },
            \"metadatos\": {
                \"canal_origen\": \"mobile\",
                \"categoria_producto\": \"premium\"
            }
        }")
    
    COMISION2_ID=$(echo $COMISION2_RESPONSE | jq -r '.comision_id')
    echo "✅ Comisión 2 creada: $COMISION2_ID"
    
    # 5. Calcular comisiones
    echo "🧮 Calculando comisiones..."
    
    curl -s -X POST "$MARKETING_URL/api/v1/comisiones/$COMISION1_ID/calcular" \
        -H "Content-Type: application/json" \
        -d '{"forzar_recalculo": false}' > /dev/null
    echo "✅ Comisión 1 calculada"
    
    curl -s -X POST "$MARKETING_URL/api/v1/comisiones/$COMISION2_ID/calcular" \
        -H "Content-Type: application/json" \
        -d '{"forzar_recalculo": false}' > /dev/null
    echo "✅ Comisión 2 calculada"
    
    # Esperar un poco para que se procesen los eventos
    echo "⏳ Esperando procesamiento de eventos..."
    sleep 5
    
    # 6. Aprobar comisiones
    echo "✅ Aprobando comisiones..."
    
    curl -s -X POST "$MARKETING_URL/api/v1/comisiones/$COMISION1_ID/aprobar" \
        -H "Content-Type: application/json" \
        -d '{
            "comentarios": "Comisión aprobada automáticamente - cumple criterios",
            "metadatos_aprobacion": {
                "nivel_aprobacion": "automatico",
                "politica_aplicada": "estandar"
            }
        }' > /dev/null
    echo "✅ Comisión 1 aprobada"
    
    curl -s -X POST "$MARKETING_URL/api/v1/comisiones/$COMISION2_ID/aprobar" \
        -H "Content-Type: application/json" \
        -d '{
            "comentarios": "Comisión premium aprobada",
            "metadatos_aprobacion": {
                "nivel_aprobacion": "supervisor",
                "politica_aplicada": "premium"
            }
        }' > /dev/null
    echo "✅ Comisión 2 aprobada"
    
    # Guardar IDs para referencia futura
    cat > test_data_ids.json << EOF
{
    "afiliados": [
        {"id": "$AFILIADO1_ID", "nombre": "María González"},
        {"id": "$AFILIADO2_ID", "nombre": "Carlos Rodríguez"}
    ],
    "campanas": [
        {"id": "$CAMPANA1_ID", "nombre": "Campaña Black Friday 2023"},
        {"id": "$CAMPANA2_ID", "nombre": "Campaña Navideña Premium"}
    ],
    "conversiones": [
        {"id": "$CONVERSION1_ID", "afiliado": "$AFILIADO1_ID", "campana": "$CAMPANA1_ID"},
        {"id": "$CONVERSION2_ID", "afiliado": "$AFILIADO2_ID", "campana": "$CAMPANA2_ID"}
    ],
    "comisiones": [
        {"id": "$COMISION1_ID", "afiliado": "$AFILIADO1_ID", "monto_esperado": 37500.0},
        {"id": "$COMISION2_ID", "afiliado": "$AFILIADO2_ID", "monto_esperado": 30000.0}
    ]
}
EOF
    
    echo "💾 IDs guardados en test_data_ids.json"
    
    echo ""
    echo "🎉 ¡Datos de prueba creados exitosamente!"
    echo ""
    echo "📋 Resumen:"
    echo "   • 2 Afiliados creados"
    echo "   • 2 Campañas activas"  
    echo "   • 2 Conversiones registradas"
    echo "   • 2 Comisiones calculadas y aprobadas"
    echo ""
    echo "🔗 URLs de servicios:"
    echo "   • Afiliados:    $AFILIADOS_URL/docs"
    echo "   • Conversiones: $CONVERSIONES_URL/docs"
    echo "   • Marketing:    $MARKETING_URL/docs"
}

# Función principal
main() {
    echo "🔍 Verificando disponibilidad de servicios..."
    
    wait_for_service "$AFILIADOS_URL" "Afiliados" || exit 1
    wait_for_service "$CONVERSIONES_URL" "Conversiones" || exit 1  
    wait_for_service "$MARKETING_URL" "Marketing" || exit 1
    
    echo ""
    echo "✅ Todos los servicios están disponibles"
    echo ""
    
    create_test_data
    
    echo ""
    echo "🚀 ¡Ecosistema AlpesPartner listo para pruebas!"
    echo ""
    echo "🧪 Para ver las pruebas E2E, ejecuta:"
    echo "   ./scripts/run_e2e_tests.sh"
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

# Ejecutar función principal
main