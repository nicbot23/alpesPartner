#!/bin/bash

# =============================================================================
# Script maestro de ejecución completa - AlpesPartner Ecosystem
# =============================================================================

set -e

echo "🚀 AlpesPartner Ecosystem - Ejecución Completa de Pruebas"
echo "$(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Contadores
TOTAL_STEPS=10
CURRENT_STEP=0
START_TIME=$(date +%s)

# Función de logging
log_step() {
    ((CURRENT_STEP++))
    local step_name=$1
    echo ""
    echo -e "${BLUE}[$CURRENT_STEP/$TOTAL_STEPS] 🔄 $step_name${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# Función para verificar dependencias
check_dependencies() {
    log_step "Verificando dependencias del sistema"
    
    local missing_deps=()
    
    for cmd in docker docker-compose curl jq bc; do
        if ! command -v $cmd &> /dev/null; then
            missing_deps+=($cmd)
        else
            log_success "$cmd está disponible"
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Dependencias faltantes: ${missing_deps[*]}"
        echo "Por favor instala las dependencias antes de continuar:"
        echo "  • Docker: https://docs.docker.com/get-docker/"
        echo "  • Docker Compose: https://docs.docker.com/compose/install/"
        echo "  • curl: apt install curl (Ubuntu) / brew install curl (macOS)"
        echo "  • jq: apt install jq (Ubuntu) / brew install jq (macOS)"
        echo "  • bc: apt install bc (Ubuntu) / brew install bc (macOS)"
        exit 1
    fi
    
    # Verificar Docker daemon
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon no está ejecutándose"
        exit 1
    fi
    
    log_success "Todas las dependencias están disponibles"
}

# Función para limpiar ambiente anterior
cleanup_environment() {
    log_step "Limpiando ambiente anterior"
    
    cd "$PROJECT_ROOT"
    
    # Parar contenedores existentes
    if docker-compose ps -q | grep -q .; then
        log_info "Parando contenedores existentes..."
        docker-compose down || true
        log_success "Contenedores detenidos"
    else
        log_info "No hay contenedores ejecutándose"
    fi
    
    # Limpiar archivos temporales
    rm -f test_data_ids.json e2e_test_report.json pulsar_events_*.log || true
    log_success "Archivos temporales limpiados"
    
    # Opcional: Limpiar volúmenes (descomenta si necesitas reset completo)
    # docker-compose down -v
    # log_success "Volúmenes limpiados"
}

# Función para construir y levantar servicios
deploy_ecosystem() {
    log_step "Construyendo y desplegando el ecosistema"
    
    cd "$PROJECT_ROOT"
    
    log_info "Construyendo imágenes Docker..."
    if docker-compose build --no-cache; then
        log_success "Imágenes construidas exitosamente"
    else
        log_error "Error construyendo imágenes Docker"
        exit 1
    fi
    
    log_info "Levantando servicios..."
    if docker-compose up -d; then
        log_success "Servicios desplegados"
    else
        log_error "Error desplegando servicios"
        exit 1
    fi
    
    # Mostrar estado de contenedores
    echo ""
    log_info "Estado de contenedores:"
    docker-compose ps
}

# Función para esperar que servicios estén listos
wait_for_services() {
    log_step "Esperando que los servicios estén listos"
    
    local services=("afiliados:8001" "conversiones:8002" "marketing:8003" "pulsar:8080")
    local max_attempts=60
    local attempt=1
    
    for service in "${services[@]}"; do
        local name=$(echo $service | cut -d: -f1)
        local port=$(echo $service | cut -d: -f2)
        local url="http://localhost:$port"
        
        log_info "Esperando $name en puerto $port..."
        
        while [ $attempt -le $max_attempts ]; do
            if [ "$name" = "pulsar" ]; then
                local health_url="$url/admin/v2/clusters"
            else
                local health_url="$url/health"
            fi
            
            if curl -sf "$health_url" >/dev/null 2>&1; then
                log_success "$name está disponible"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log_error "$name no está disponible después de $max_attempts intentos"
                log_info "Logs de $name:"
                docker-compose logs --tail=20 $name
                exit 1
            fi
            
            sleep 5
            ((attempt++))
        done
        
        attempt=1
    done
    
    log_success "Todos los servicios están disponibles"
}

# Función para configurar Pulsar
setup_pulsar() {
    log_step "Configurando tópicos y esquemas Apache Pulsar"
    
    cd "$PROJECT_ROOT"
    
    if [ -x "./scripts/setup_pulsar_topics.sh" ]; then
        if ./scripts/setup_pulsar_topics.sh; then
            log_success "Tópicos Pulsar configurados correctamente"
        else
            log_error "Error configurando tópicos Pulsar"
            exit 1
        fi
    else
        log_error "Script setup_pulsar_topics.sh no encontrado o no ejecutable"
        exit 1
    fi
}

# Función para poblar datos de prueba
populate_test_data() {
    log_step "Poblando datos de prueba"
    
    cd "$PROJECT_ROOT"
    
    if [ -x "./scripts/init_test_data.sh" ]; then
        if ./scripts/init_test_data.sh; then
            log_success "Datos de prueba creados exitosamente"
            
            # Mostrar resumen de datos creados
            if [ -f "test_data_ids.json" ]; then
                echo ""
                log_info "Resumen de datos creados:"
                local afiliados_count=$(jq '.afiliados | length' test_data_ids.json 2>/dev/null || echo "0")
                local campanas_count=$(jq '.campanas | length' test_data_ids.json 2>/dev/null || echo "0")
                local conversiones_count=$(jq '.conversiones | length' test_data_ids.json 2>/dev/null || echo "0")
                local comisiones_count=$(jq '.comisiones | length' test_data_ids.json 2>/dev/null || echo "0")
                
                echo "  • $afiliados_count afiliados creados"
                echo "  • $campanas_count campañas configuradas"
                echo "  • $conversiones_count conversiones registradas"
                echo "  • $comisiones_count comisiones procesadas"
            fi
        else
            log_error "Error poblando datos de prueba"
            exit 1
        fi
    else
        log_error "Script init_test_data.sh no encontrado o no ejecutable"
        exit 1
    fi
}

# Función para ejecutar pruebas E2E
run_e2e_tests() {
    log_step "Ejecutando casos de prueba End-to-End"
    
    cd "$PROJECT_ROOT"
    
    if [ -x "./scripts/run_e2e_tests.sh" ]; then
        if ./scripts/run_e2e_tests.sh; then
            log_success "Todas las pruebas E2E pasaron exitosamente"
            
            # Mostrar resumen del reporte
            if [ -f "e2e_test_report.json" ]; then
                echo ""
                log_info "Resumen de pruebas E2E:"
                local total_tests=$(jq '.total_tests' e2e_test_report.json 2>/dev/null || echo "0")
                local tests_passed=$(jq '.tests_passed' e2e_test_report.json 2>/dev/null || echo "0")
                local tests_failed=$(jq '.tests_failed' e2e_test_report.json 2>/dev/null || echo "0")
                local success_rate=$(jq '.success_rate' e2e_test_report.json 2>/dev/null || echo "0")
                
                echo "  • Total de pruebas: $total_tests"
                echo "  • Pruebas exitosas: $tests_passed"
                echo "  • Pruebas fallidas: $tests_failed"
                echo "  • Tasa de éxito: $success_rate%"
            fi
        else
            log_warning "Algunas pruebas E2E fallaron - revisar logs para detalles"
        fi
    else
        log_error "Script run_e2e_tests.sh no encontrado o no ejecutable"
        exit 1
    fi
}

# Función para validar eventos Pulsar
validate_pulsar_events() {
    log_step "Validando eventos en Apache Pulsar"
    
    local topics=("afiliados.eventos" "conversiones.eventos" "marketing.eventos" "comisiones.eventos")
    local total_events=0
    
    for topic in "${topics[@]}"; do
        local stats=$(curl -s "http://localhost:8080/admin/v2/persistent/public/default/$topic/stats" 2>/dev/null || echo "{}")
        local msg_count=$(echo "$stats" | jq -r '.msgInCounter // 0' 2>/dev/null || echo "0")
        
        if [ "$msg_count" -gt 0 ]; then
            log_success "$topic: $msg_count eventos procesados"
            total_events=$((total_events + msg_count))
        else
            log_warning "$topic: Sin eventos registrados"
        fi
    done
    
    if [ $total_events -gt 0 ]; then
        log_success "Total de eventos procesados: $total_events"
    else
        log_warning "No se encontraron eventos en los tópicos"
    fi
}

# Función para generar reporte de rendimiento
performance_report() {
    log_step "Generando reporte de rendimiento"
    
    local end_time=$(date +%s)
    local execution_time=$((end_time - START_TIME))
    local execution_minutes=$((execution_time / 60))
    local execution_seconds=$((execution_time % 60))
    
    # Obtener métricas de Docker
    local containers_running=$(docker-compose ps -q | wc -l)
    local total_memory=$(docker stats --no-stream --format "table {{.MemUsage}}" | tail -n +2 | awk '{print $1}' | sed 's/MiB//' | awk '{sum+=$1} END {print sum}' 2>/dev/null || echo "N/A")
    
    # Obtener métricas de Pulsar
    local pulsar_topics=$(curl -s "http://localhost:8080/admin/v2/persistent/public/default" 2>/dev/null | jq '. | length' 2>/dev/null || echo "0")
    
    echo ""
    log_info "📊 REPORTE DE RENDIMIENTO"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🕐 Tiempo de ejecución: ${execution_minutes}m ${execution_seconds}s"
    echo "🐳 Contenedores ejecutándose: $containers_running"
    echo "💾 Memoria total utilizada: ${total_memory}MB"
    echo "📢 Tópicos Pulsar configurados: $pulsar_topics"
    echo ""
    
    # Guardar reporte de rendimiento
    cat > performance_report.json << EOF
{
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "execution_time_seconds": $execution_time,
    "containers_running": $containers_running,
    "memory_used_mb": "$total_memory",
    "pulsar_topics": $pulsar_topics,
    "success": true
}
EOF
    
    log_success "Reporte de rendimiento guardado en performance_report.json"
}

# Función para mostrar URLs útiles
show_useful_urls() {
    log_step "URLs de acceso y administración"
    
    echo ""
    echo "🔗 SERVICIOS PRINCIPALES:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Afiliados API:      http://localhost:8001/docs"
    echo "📈 Conversiones API:   http://localhost:8002/docs"
    echo "💰 Marketing API:      http://localhost:8003/docs"
    echo ""
    echo "🛠️  HERRAMIENTAS DE ADMINISTRACIÓN:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🗄️  phpMyAdmin:        http://localhost:8082"
    echo "📡 Pulsar Manager:     http://localhost:9527"
    echo "💾 Redis Commander:    http://localhost:8081"
    echo ""
    echo "🧪 HERRAMIENTAS DE MONITOREO:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Monitor Pulsar:     ./scripts/monitor_pulsar.sh dashboard"
    echo "📋 Logs en tiempo real: docker-compose logs -f"
    echo "📈 Métricas Docker:    docker stats"
}

# Función principal
main() {
    echo "🎯 Iniciando ejecución completa del ecosistema AlpesPartner"
    echo ""
    
    # Ejecutar todos los pasos
    check_dependencies
    cleanup_environment
    deploy_ecosystem
    wait_for_services
    setup_pulsar
    populate_test_data
    run_e2e_tests
    validate_pulsar_events
    performance_report
    show_useful_urls
    
    # Reporte final
    local end_time=$(date +%s)
    local total_time=$((end_time - START_TIME))
    local total_minutes=$((total_time / 60))
    local total_seconds=$((total_time % 60))
    
    echo ""
    echo "🎉 ¡EJECUCIÓN COMPLETA EXITOSA!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    log_success "Ecosistema AlpesPartner desplegado y validado exitosamente"
    log_success "Tiempo total de ejecución: ${total_minutes}m ${total_seconds}s"
    echo ""
    echo "💡 Próximos pasos:"
    echo "  • Explorar las APIs usando las URLs de documentación"
    echo "  • Monitorear eventos en tiempo real con ./scripts/monitor_pulsar.sh"
    echo "  • Revisar los reportes generados (test_data_ids.json, e2e_test_report.json)"
    echo "  • Experimentar con nuevos casos de uso usando las APIs REST"
    echo ""
    echo "📚 Para más información, consulta: ECOSYSTEM_DOCS.md"
    echo ""
    echo "🛑 Para detener el ecosistema: docker-compose down"
    echo ""
}

# Manejo de interrupciones
trap 'echo ""; log_warning "Ejecución interrumpida por el usuario"; exit 1' INT

# Verificar que estamos en el directorio correcto
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "No se encontró docker-compose.yml en $PROJECT_ROOT"
    log_info "Asegúrate de ejecutar este script desde la raíz del proyecto"
    exit 1
fi

# Ejecutar función principal
main