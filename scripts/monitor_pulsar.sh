#!/bin/bash

# =============================================================================
# Script de monitoreo de eventos Pulsar en tiempo real - AlpesPartner Ecosystem
# =============================================================================

set -e

echo "📊 Monitor de eventos Apache Pulsar - AlpesPartner Ecosystem"

# Configuración
PULSAR_ADMIN_URL="http://localhost:8080"
PULSAR_BROKER_URL="pulsar://localhost:6650"
REFRESH_INTERVAL=${1:-5}  # Intervalo de actualización en segundos
TENANT="public"
NAMESPACE="default"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Función para logging con timestamp
log_with_time() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")  echo -e "${BLUE}[$timestamp] ℹ️  $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}[$timestamp] ✅ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}[$timestamp] ⚠️  $message${NC}" ;;
        "ERROR") echo -e "${RED}[$timestamp] ❌ $message${NC}" ;;
        "METRIC") echo -e "${PURPLE}[$timestamp] 📊 $message${NC}" ;;
        "EVENT") echo -e "${CYAN}[$timestamp] 🔔 $message${NC}" ;;
    esac
}

# Función para verificar conectividad con Pulsar
check_pulsar_connectivity() {
    if curl -sf "$PULSAR_ADMIN_URL/admin/v2/clusters" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Función para obtener estadísticas de un tópico
get_topic_stats() {
    local topic=$1
    local full_topic="persistent://$TENANT/$NAMESPACE/$topic"
    
    local stats=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/persistent/$TENANT/$NAMESPACE/$topic/stats" 2>/dev/null || echo "{}")
    
    if [ "$stats" != "{}" ] && [ "$stats" != "null" ]; then
        echo "$stats"
    else
        echo "{\"msgInCounter\": 0, \"msgOutCounter\": 0, \"storageSize\": 0, \"subscriptions\": {}}"
    fi
}

# Función para obtener información de subscripciones
get_subscription_info() {
    local topic=$1
    local stats=$(get_topic_stats "$topic")
    
    local subscriptions=$(echo "$stats" | jq -r '.subscriptions // {} | keys[]' 2>/dev/null || echo "")
    
    if [ -n "$subscriptions" ]; then
        echo "$subscriptions" | while IFS= read -r sub; do
            local sub_stats=$(echo "$stats" | jq -r ".subscriptions[\"$sub\"]" 2>/dev/null || echo "{}")
            local msg_backlog=$(echo "$sub_stats" | jq -r '.msgBacklog // 0' 2>/dev/null || echo "0")
            local consumers=$(echo "$sub_stats" | jq -r '.consumers // [] | length' 2>/dev/null || echo "0")
            
            echo "      📋 $sub: $msg_backlog mensajes pendientes, $consumers consumidores"
        done
    else
        echo "      📋 Sin subscripciones activas"
    fi
}

# Función para mostrar métricas en tiempo real
show_realtime_metrics() {
    # Limpiar pantalla
    clear
    
    echo "📊 MONITOR PULSAR - AlpesPartner Ecosystem"
    echo "$(date)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Verificar conectividad
    if ! check_pulsar_connectivity; then
        log_with_time "ERROR" "No se puede conectar a Pulsar Admin API"
        return 1
    fi
    
    log_with_time "SUCCESS" "Conectado a Apache Pulsar"
    echo ""
    
    # Tópicos a monitorear
    local topics=("afiliados.eventos" "conversiones.eventos" "marketing.eventos" "comisiones.eventos" "auditoria.eventos" "sistema.eventos")
    
    # Estadísticas globales
    local total_messages_in=0
    local total_messages_out=0
    local total_storage_size=0
    local total_subscriptions=0
    
    echo "📢 ESTADÍSTICAS POR TÓPICO:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    for topic in "${topics[@]}"; do
        local stats=$(get_topic_stats "$topic")
        
        # Extraer métricas
        local msg_in=$(echo "$stats" | jq -r '.msgInCounter // 0' 2>/dev/null || echo "0")
        local msg_out=$(echo "$stats" | jq -r '.msgOutCounter // 0' 2>/dev/null || echo "0")
        local storage_size=$(echo "$stats" | jq -r '.storageSize // 0' 2>/dev/null || echo "0")
        local subscription_count=$(echo "$stats" | jq -r '.subscriptions // {} | length' 2>/dev/null || echo "0")
        
        # Acumular totales
        total_messages_in=$((total_messages_in + msg_in))
        total_messages_out=$((total_messages_out + msg_out))
        total_storage_size=$((total_storage_size + storage_size))
        total_subscriptions=$((total_subscriptions + subscription_count))
        
        # Calcular rate (aproximado)
        local processing_rate="N/A"
        if [ "$msg_in" -gt 0 ]; then
            processing_rate=$(echo "scale=2; $msg_out * 100 / $msg_in" | bc -l 2>/dev/null || echo "N/A")
            if [ "$processing_rate" != "N/A" ]; then
                processing_rate="${processing_rate}%"
            fi
        fi
        
        # Formatear tamaño de almacenamiento
        local storage_formatted=""
        if [ "$storage_size" -gt 1048576 ]; then
            storage_formatted="$(echo "scale=2; $storage_size / 1048576" | bc -l) MB"
        elif [ "$storage_size" -gt 1024 ]; then
            storage_formatted="$(echo "scale=2; $storage_size / 1024" | bc -l) KB"
        else
            storage_formatted="${storage_size} B"
        fi
        
        # Mostrar métricas del tópico
        echo "   🔹 $topic"
        echo "      📥 Mensajes entrantes: $msg_in"
        echo "      📤 Mensajes procesados: $msg_out"
        echo "      💾 Almacenamiento: $storage_formatted"
        echo "      📊 Tasa procesamiento: $processing_rate"
        echo "      🔢 Subscripciones: $subscription_count"
        
        # Mostrar información de subscripciones
        get_subscription_info "$topic"
        echo ""
    done
    
    # Resumen global
    echo "🌐 RESUMEN GLOBAL:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   📊 Total mensajes producidos: $total_messages_in"
    echo "   📊 Total mensajes consumidos: $total_messages_out"
    echo "   📊 Total almacenamiento: $(echo "scale=2; $total_storage_size / 1048576" | bc -l) MB"
    echo "   📊 Total subscripciones: $total_subscriptions"
    
    # Calcular throughput global
    local global_throughput="N/A"
    if [ "$total_messages_in" -gt 0 ]; then
        global_throughput=$(echo "scale=2; $total_messages_out * 100 / $total_messages_in" | bc -l 2>/dev/null || echo "N/A")
        if [ "$global_throughput" != "N/A" ]; then
            global_throughput="${global_throughput}%"
        fi
    fi
    echo "   📊 Throughput global: $global_throughput"
    
    # Estado del cluster
    echo ""
    echo "🏗️  ESTADO DEL CLUSTER:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Obtener información del cluster
    local cluster_info=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/clusters" 2>/dev/null || echo "[]")
    local cluster_count=$(echo "$cluster_info" | jq '. | length' 2>/dev/null || echo "0")
    echo "   🏗️  Clusters configurados: $cluster_count"
    
    # Obtener información de brokers
    local brokers_info=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/brokers/standalone" 2>/dev/null || echo "[]")
    local broker_count=$(echo "$brokers_info" | jq '. | length' 2>/dev/null || echo "0")
    echo "   🖥️  Brokers activos: $broker_count"
    
    # Estado de BookKeeper (si está disponible)
    local bk_health=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/bookies/health" 2>/dev/null || echo "[]")
    local bk_count=$(echo "$bk_health" | jq '. | length' 2>/dev/null || echo "0")
    echo "   📚 BookKeeper nodes: $bk_count"
    
    echo ""
    echo "🔄 Actualizando cada $REFRESH_INTERVAL segundos... (Ctrl+C para salir)"
    echo "🔗 URLs: Admin: $PULSAR_ADMIN_URL | Manager: http://localhost:9527"
}

# Función para generar alertas basadas en métricas
check_alerts() {
    local topics=("afiliados.eventos" "conversiones.eventos" "marketing.eventos" "comisiones.eventos")
    
    for topic in "${topics[@]}"; do
        local stats=$(get_topic_stats "$topic")
        
        # Verificar backlog alto
        local subscriptions=$(echo "$stats" | jq -r '.subscriptions // {} | keys[]' 2>/dev/null || echo "")
        if [ -n "$subscriptions" ]; then
            echo "$subscriptions" | while IFS= read -r sub; do
                local msg_backlog=$(echo "$stats" | jq -r ".subscriptions[\"$sub\"].msgBacklog // 0" 2>/dev/null || echo "0")
                
                if [ "$msg_backlog" -gt 100 ]; then
                    log_with_time "WARNING" "Alto backlog en $topic/$sub: $msg_backlog mensajes"
                fi
            done
        fi
        
        # Verificar uso de almacenamiento
        local storage_size=$(echo "$stats" | jq -r '.storageSize // 0' 2>/dev/null || echo "0")
        if [ "$storage_size" -gt 104857600 ]; then  # 100MB
            local storage_mb=$(echo "scale=2; $storage_size / 1048576" | bc -l)
            log_with_time "WARNING" "Alto uso de almacenamiento en $topic: ${storage_mb}MB"
        fi
    done
}

# Función para logging continuo de eventos
continuous_event_logging() {
    local log_file="pulsar_events_$(date +%Y%m%d_%H%M%S).log"
    
    log_with_time "INFO" "Iniciando logging continuo en: $log_file"
    
    while true; do
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        
        # Obtener métricas de todos los tópicos
        local topics=("afiliados.eventos" "conversiones.eventos" "marketing.eventos" "comisiones.eventos")
        
        for topic in "${topics[@]}"; do
            local stats=$(get_topic_stats "$topic")
            local msg_in=$(echo "$stats" | jq -r '.msgInCounter // 0' 2>/dev/null || echo "0")
            local msg_out=$(echo "$stats" | jq -r '.msgOutCounter // 0' 2>/dev/null || echo "0")
            
            # Log en formato JSON
            echo "{\"timestamp\":\"$timestamp\",\"topic\":\"$topic\",\"messages_in\":$msg_in,\"messages_out\":$msg_out}" >> "$log_file"
        done
        
        # Verificar alertas
        check_alerts
        
        sleep "$REFRESH_INTERVAL"
    done
}

# Función para mostrar ayuda
show_help() {
    echo "📊 Monitor de eventos Pulsar - AlpesPartner"
    echo ""
    echo "Uso: $0 [COMANDO] [OPCIONES]"
    echo ""
    echo "Comandos:"
    echo "  dashboard [intervalo]     - Mostrar dashboard en tiempo real (default: 5s)"
    echo "  log [intervalo]          - Logging continuo de eventos"
    echo "  stats [tópico]           - Mostrar estadísticas de un tópico específico"
    echo "  alert                    - Verificar alertas una vez"
    echo "  topics                   - Listar todos los tópicos disponibles"
    echo "  help                     - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 dashboard 3           - Dashboard con actualización cada 3 segundos"
    echo "  $0 stats comisiones.eventos - Estadísticas del tópico de comisiones"
    echo "  $0 log 10                - Log cada 10 segundos"
}

# Función para mostrar estadísticas de un tópico específico
show_topic_stats() {
    local topic=$1
    
    if [ -z "$topic" ]; then
        echo "❌ Debe especificar un tópico"
        echo "Tópicos disponibles: afiliados.eventos, conversiones.eventos, marketing.eventos, comisiones.eventos"
        exit 1
    fi
    
    echo "📊 Estadísticas detalladas de: $topic"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local stats=$(get_topic_stats "$topic")
    
    if [ "$stats" = "{\"msgInCounter\": 0, \"msgOutCounter\": 0, \"storageSize\": 0, \"subscriptions\": {}}" ]; then
        log_with_time "WARNING" "Tópico $topic no encontrado o sin actividad"
        return 1
    fi
    
    # Mostrar estadísticas en formato legible
    echo "$stats" | jq . 2>/dev/null || echo "Error parsing JSON stats"
    
    echo ""
    log_with_time "INFO" "Estadísticas obtenidas para $topic"
}

# Función para listar tópicos
list_topics() {
    echo "📋 Tópicos disponibles en el cluster:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local topics=$(curl -s "$PULSAR_ADMIN_URL/admin/v2/persistent/$TENANT/$NAMESPACE" 2>/dev/null || echo "[]")
    
    if [ "$topics" != "[]" ] && [ -n "$topics" ]; then
        echo "$topics" | jq -r '.[]' 2>/dev/null | while IFS= read -r topic; do
            local topic_name=$(basename "$topic")
            echo "   📢 $topic_name"
        done
    else
        log_with_time "WARNING" "No se encontraron tópicos o error de conexión"
    fi
}

# Función principal
main() {
    local command=${1:-"dashboard"}
    local param=${2:-$REFRESH_INTERVAL}
    
    # Verificar conectividad inicial
    if ! check_pulsar_connectivity; then
        log_with_time "ERROR" "No se puede conectar a Pulsar en $PULSAR_ADMIN_URL"
        log_with_time "INFO" "Verifica que Apache Pulsar esté ejecutándose"
        exit 1
    fi
    
    case $command in
        "dashboard")
            REFRESH_INTERVAL=$param
            log_with_time "INFO" "Iniciando dashboard (intervalo: ${REFRESH_INTERVAL}s)"
            
            # Configurar trap para limpiar al salir
            trap 'echo ""; log_with_time "INFO" "Dashboard detenido"; exit 0' INT
            
            while true; do
                show_realtime_metrics
                sleep "$REFRESH_INTERVAL"
            done
            ;;
            
        "log")
            REFRESH_INTERVAL=$param
            continuous_event_logging
            ;;
            
        "stats")
            show_topic_stats "$param"
            ;;
            
        "alert")
            log_with_time "INFO" "Verificando alertas..."
            check_alerts
            ;;
            
        "topics")
            list_topics
            ;;
            
        "help"|"-h"|"--help")
            show_help
            ;;
            
        *)
            echo "❌ Comando desconocido: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Verificar dependencias
for cmd in curl jq bc; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ $cmd no está instalado. Por favor instálalo primero."
        exit 1
    fi
done

# Ejecutar función principal
main "$@"