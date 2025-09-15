#!/bin/bash

# =============================================================================
# Script de configuración de tópicos Pulsar - AlpesPartner Ecosystem
# =============================================================================

set -e

echo "🚀 Configurando tópicos de eventos Apache Pulsar para AlpesPartner..."

# Configuración de Pulsar
PULSAR_ADMIN_URL="http://localhost:8080"
PULSAR_BROKER_URL="pulsar://localhost:6650"
TENANT="public"
NAMESPACE="default"

# Función para esperar que Pulsar esté disponible
wait_for_pulsar() {
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Esperando que Apache Pulsar esté disponible..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$PULSAR_ADMIN_URL/admin/v2/clusters" >/dev/null 2>&1; then
            echo "✅ Apache Pulsar está disponible"
            return 0
        fi
        
        echo "🔄 Intento $attempt/$max_attempts - Pulsar no disponible, esperando..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo "❌ Apache Pulsar no está disponible después de $max_attempts intentos"
    return 1
}

# Función para crear un tópico con configuración específica
create_topic() {
    local topic_name=$1
    local partitions=${2:-4}
    local retention_time=${3:-"7d"}
    local retention_size=${4:-"1GB"}
    local description=$5
    
    local full_topic="persistent://$TENANT/$NAMESPACE/$topic_name"
    
    echo "📢 Creando tópico: $topic_name"
    echo "   📋 Descripción: $description"
    echo "   🔢 Particiones: $partitions"
    echo "   ⏰ Retención tiempo: $retention_time"
    echo "   💾 Retención tamaño: $retention_size"
    
    # Crear el tópico con particiones
    if curl -s -X PUT "$PULSAR_ADMIN_URL/admin/v2/persistent/$TENANT/$NAMESPACE/$topic_name/partitions" \
        -H "Content-Type: application/json" \
        -d "$partitions" >/dev/null 2>&1; then
        echo "   ✅ Tópico creado con éxito"
    else
        echo "   ℹ️  Tópico ya existe o se creó automáticamente"
    fi
    
    # Configurar políticas de retención
    curl -s -X POST "$PULSAR_ADMIN_URL/admin/v2/persistent/$TENANT/$NAMESPACE/$topic_name/retention" \
        -H "Content-Type: application/json" \
        -d "{
            \"retentionTimeInMinutes\": $(echo $retention_time | sed 's/d//' | awk '{print $1*24*60}'),
            \"retentionSizeInMB\": $(echo $retention_size | sed 's/GB//' | awk '{print $1*1024}')
        }" >/dev/null 2>&1
    
    # Configurar persistencia
    curl -s -X POST "$PULSAR_ADMIN_URL/admin/v2/persistent/$TENANT/$NAMESPACE/$topic_name/persistence" \
        -H "Content-Type: application/json" \
        -d '{
            "bookkeeperEnsemble": 1,
            "bookkeeperWriteQuorum": 1,
            "bookkeeperAckQuorum": 1,
            "managedLedgerMaxMarkDeleteRate": 10.0
        }' >/dev/null 2>&1
    
    # Configurar deduplicación
    curl -s -X POST "$PULSAR_ADMIN_URL/admin/v2/persistent/$TENANT/$NAMESPACE/$topic_name/deduplication" \
        -H "Content-Type: application/json" \
        -d 'true' >/dev/null 2>&1
    
    echo "   🛡️  Configuración de persistencia y deduplicación aplicada"
    echo ""
}

# Función para crear un schema para un tópico
create_schema() {
    local topic_name=$1
    local schema_name=$2
    local schema_content=$3
    
    echo "📝 Aplicando schema para $topic_name..."
    
    curl -s -X POST "$PULSAR_ADMIN_URL/admin/v2/schemas/$TENANT/$NAMESPACE/$topic_name/schema" \
        -H "Content-Type: application/json" \
        -d "{
            \"type\": \"JSON\",
            \"schema\": \"$schema_content\",
            \"properties\": {
                \"__jsr310ConversionEnabled\": \"false\"
            }
        }" >/dev/null 2>&1
    
    echo "   ✅ Schema $schema_name aplicado"
}

# Función para configurar subscripciones
create_subscription() {
    local topic_name=$1
    local subscription_name=$2
    local subscription_type=${3:-"Shared"}
    
    echo "📋 Creando subscripción: $subscription_name para $topic_name"
    
    curl -s -X PUT "$PULSAR_ADMIN_URL/admin/v2/persistent/$TENANT/$NAMESPACE/$topic_name/subscription/$subscription_name" \
        -H "Content-Type: application/json" \
        -d "{\"messageId\": {\"ledgerId\": 0, \"entryId\": 0}}" >/dev/null 2>&1
    
    echo "   ✅ Subscripción creada (tipo: $subscription_type)"
}

# Función principal de configuración
setup_pulsar_topics() {
    echo "🔧 Configurando tópicos y esquemas..."
    echo ""
    
    # 1. Tópico para eventos de Afiliados
    create_topic "afiliados.eventos" 4 "30d" "2GB" "Eventos del microservicio Afiliados (creación, actualización, eliminación)"
    
    # Schema para eventos de afiliados
    local afiliados_schema='{
        "type": "object",
        "properties": {
            "evento_id": {"type": "string"},
            "tipo_evento": {"type": "string", "enum": ["afiliado_creado", "afiliado_actualizado", "afiliado_eliminado"]},
            "fecha_evento": {"type": "string", "format": "date-time"},
            "afiliado_id": {"type": "string"},
            "datos_afiliado": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string"},
                    "email": {"type": "string"},
                    "tipo_afiliado": {"type": "string"},
                    "configuracion_comisiones": {"type": "object"}
                }
            },
            "metadatos": {"type": "object"}
        },
        "required": ["evento_id", "tipo_evento", "fecha_evento", "afiliado_id"]
    }'
    
    create_schema "afiliados.eventos" "AfiliadoEvento" "$afiliados_schema"
    create_subscription "afiliados.eventos" "marketing-consumer" "Shared"
    create_subscription "afiliados.eventos" "audit-consumer" "Shared"
    
    # 2. Tópico para eventos de Conversiones
    create_topic "conversiones.eventos" 6 "90d" "5GB" "Eventos del microservicio Conversiones (registro, validación, procesamiento)"
    
    # Schema para eventos de conversiones
    local conversiones_schema='{
        "type": "object",
        "properties": {
            "evento_id": {"type": "string"},
            "tipo_evento": {"type": "string", "enum": ["conversion_registrada", "conversion_validada", "conversion_procesada"]},
            "fecha_evento": {"type": "string", "format": "date-time"},
            "conversion_id": {"type": "string"},
            "afiliado_id": {"type": "string"},
            "campana_id": {"type": "string"},
            "datos_conversion": {
                "type": "object",
                "properties": {
                    "tipo_conversion": {"type": "string"},
                    "valor_conversion": {"type": "number"},
                    "moneda": {"type": "string"},
                    "canal_origen": {"type": "string"}
                }
            },
            "metadatos": {"type": "object"}
        },
        "required": ["evento_id", "tipo_evento", "fecha_evento", "conversion_id", "afiliado_id"]
    }'
    
    create_schema "conversiones.eventos" "ConversionEvento" "$conversiones_schema"
    create_subscription "conversiones.eventos" "marketing-consumer" "Shared"
    create_subscription "conversiones.eventos" "analytics-consumer" "Shared"
    
    # 3. Tópico para eventos de Marketing
    create_topic "marketing.eventos" 4 "60d" "3GB" "Eventos del microservicio Marketing (campañas, segmentación, coordinación)"
    
    # Schema para eventos de marketing
    local marketing_schema='{
        "type": "object",
        "properties": {
            "evento_id": {"type": "string"},
            "tipo_evento": {"type": "string", "enum": ["campana_creada", "campana_activada", "campana_pausada", "segmentacion_actualizada"]},
            "fecha_evento": {"type": "string", "format": "date-time"},
            "campana_id": {"type": "string"},
            "datos_campana": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string"},
                    "tipo_campana": {"type": "string"},
                    "presupuesto": {"type": "number"},
                    "configuracion_comisiones": {"type": "object"}
                }
            },
            "metadatos": {"type": "object"}
        },
        "required": ["evento_id", "tipo_evento", "fecha_evento"]
    }'
    
    create_schema "marketing.eventos" "MarketingEvento" "$marketing_schema"
    create_subscription "marketing.eventos" "afiliados-consumer" "Shared"
    create_subscription "marketing.eventos" "conversiones-consumer" "Shared"
    
    # 4. Tópico para eventos de Comisiones
    create_topic "comisiones.eventos" 8 "365d" "10GB" "Eventos del módulo Comisiones (cálculo, aprobación, pago)"
    
    # Schema para eventos de comisiones
    local comisiones_schema='{
        "type": "object",
        "properties": {
            "evento_id": {"type": "string"},
            "tipo_evento": {"type": "string", "enum": ["comision_creada", "comision_calculada", "comision_aprobada", "comision_rechazada", "comision_pagada"]},
            "fecha_evento": {"type": "string", "format": "date-time"},
            "comision_id": {"type": "string"},
            "afiliado_id": {"type": "string"},
            "campana_id": {"type": "string"},
            "conversion_id": {"type": "string"},
            "datos_comision": {
                "type": "object",
                "properties": {
                    "monto_calculado": {"type": "number"},
                    "moneda": {"type": "string"},
                    "estado": {"type": "string"},
                    "tipo_comision": {"type": "string"}
                }
            },
            "metadatos": {"type": "object"}
        },
        "required": ["evento_id", "tipo_evento", "fecha_evento", "comision_id", "afiliado_id"]
    }'
    
    create_schema "comisiones.eventos" "ComisionEvento" "$comisiones_schema"
    create_subscription "comisiones.eventos" "afiliados-consumer" "Shared"
    create_subscription "comisiones.eventos" "payment-consumer" "Shared"
    create_subscription "comisiones.eventos" "reporting-consumer" "Shared"
    
    # 5. Tópico para eventos de Auditoría
    create_topic "auditoria.eventos" 4 "1y" "50GB" "Eventos de auditoría y compliance del ecosistema"
    
    # Schema para eventos de auditoría
    local auditoria_schema='{
        "type": "object",
        "properties": {
            "evento_id": {"type": "string"},
            "tipo_evento": {"type": "string"},
            "fecha_evento": {"type": "string", "format": "date-time"},
            "servicio_origen": {"type": "string"},
            "usuario_id": {"type": "string"},
            "accion": {"type": "string"},
            "recurso_afectado": {"type": "string"},
            "datos_antes": {"type": "object"},
            "datos_despues": {"type": "object"},
            "metadatos": {"type": "object"}
        },
        "required": ["evento_id", "tipo_evento", "fecha_evento", "servicio_origen", "accion"]
    }'
    
    create_schema "auditoria.eventos" "AuditoriaEvento" "$auditoria_schema"
    create_subscription "auditoria.eventos" "compliance-consumer" "Shared"
    create_subscription "auditoria.eventos" "security-consumer" "Shared"
    
    # 6. Tópico para eventos del Sistema
    create_topic "sistema.eventos" 2 "7d" "1GB" "Eventos del sistema (health checks, métricas, alertas)"
    
    # Schema para eventos del sistema
    local sistema_schema='{
        "type": "object",
        "properties": {
            "evento_id": {"type": "string"},
            "tipo_evento": {"type": "string", "enum": ["health_check", "metrica", "alerta", "error"]},
            "fecha_evento": {"type": "string", "format": "date-time"},
            "servicio": {"type": "string"},
            "nivel": {"type": "string", "enum": ["info", "warning", "error", "critical"]},
            "mensaje": {"type": "string"},
            "metricas": {"type": "object"},
            "metadatos": {"type": "object"}
        },
        "required": ["evento_id", "tipo_evento", "fecha_evento", "servicio", "nivel"]
    }'
    
    create_schema "sistema.eventos" "SistemaEvento" "$sistema_schema"
    create_subscription "sistema.eventos" "monitoring-consumer" "Shared"
    create_subscription "sistema.eventos" "alerting-consumer" "Shared"
}

# Función para mostrar configuración final
show_topics_summary() {
    echo "📊 Resumen de tópicos configurados:"
    echo ""
    
    # Obtener lista de tópicos
    local topics=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/persistent/$TENANT/$NAMESPACE" 2>/dev/null | jq -r '.[]' 2>/dev/null || echo "")
    
    if [ -n "$topics" ]; then
        echo "$topics" | while IFS= read -r topic; do
            if [[ "$topic" == *".eventos" ]]; then
                local topic_name=$(basename "$topic")
                local partitions=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/persistent/$topic/partitions" 2>/dev/null || echo "N/A")
                echo "   📢 $topic_name (particiones: $partitions)"
                
                # Mostrar subscripciones
                local subscriptions=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/persistent/$topic/subscriptions" 2>/dev/null | jq -r '.[]' 2>/dev/null || echo "")
                if [ -n "$subscriptions" ]; then
                    echo "$subscriptions" | while IFS= read -r sub; do
                        echo "      📋 Subscripción: $sub"
                    done
                fi
                echo ""
            fi
        done
    else
        echo "   ⚠️  No se pudieron listar los tópicos (Pulsar puede estar iniciándose)"
    fi
    
    echo ""
    echo "🔗 URLs de administración:"
    echo "   • Pulsar Admin: $PULSAR_ADMIN_URL"
    echo "   • Pulsar Manager: http://localhost:9527"
    echo ""
    echo "🧪 Para probar los eventos:"
    echo "   • Pulsar Client: pulsar-client --url $PULSAR_BROKER_URL"
    echo "   • Python: import pulsar; client = pulsar.Client('$PULSAR_BROKER_URL')"
}

# Función principal
main() {
    echo "🔍 Verificando disponibilidad de Apache Pulsar..."
    
    wait_for_pulsar || exit 1
    
    echo ""
    echo "✅ Apache Pulsar está disponible"
    echo ""
    
    setup_pulsar_topics
    
    echo ""
    echo "⏳ Esperando que se apliquen las configuraciones..."
    sleep 3
    
    show_topics_summary
    
    echo ""
    echo "🎉 ¡Configuración de tópicos Pulsar completada!"
    echo ""
    echo "💡 Los microservicios pueden ahora:"
    echo "   • Publicar eventos en sus tópicos correspondientes"
    echo "   • Suscribirse a eventos de otros servicios"
    echo "   • Usar schemas JSON para validación automática"
    echo "   • Beneficiarse de persistencia y deduplicación"
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