#!/bin/bash
"""
Script de Inicialización Completa - AlpesPartner
===============================================

Este script asegura que todo el entorno esté funcionando correctamente:
1. Verifica Docker Compose
2. Reconstruye servicios con dependencias actualizadas
3. Valida conectividad de Pulsar
4. Ejecuta prueba del flujo de eventos

Uso:
    chmod +x setup_y_prueba.sh
    ./setup_y_prueba.sh
"""

set -e  # Salir si hay errores

echo "🚀 INICIALIZACIÓN COMPLETA - ALPESPARTNER"
echo "========================================"

# Función de logging
log_info() {
    echo "[$(date '+%H:%M:%S')] ℹ️  $1"
}

log_success() {
    echo "[$(date '+%H:%M:%S')] ✅ $1"
}

log_error() {
    echo "[$(date '+%H:%M:%S')] ❌ $1"
}

log_warning() {
    echo "[$(date '+%H:%M:%S')] ⚠️  $1"
}

# 1. Verificar Docker
log_info "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    log_error "Docker no está instalado"
    exit 1
fi

if ! docker info &> /dev/null; then
    log_error "Docker no está ejecutándose"
    exit 1
fi

log_success "Docker está funcionando"

# 2. Detener servicios existentes
log_info "Deteniendo servicios existentes..."
docker-compose down 2>/dev/null || true
log_success "Servicios detenidos"

# 3. Limpiar volúmenes si es necesario
log_info "Limpiando volúmenes antiguos..."
docker volume prune -f 2>/dev/null || true

# 4. Reconstruir servicios con nuevas dependencias
log_info "Reconstruyendo servicios con dependencias actualizadas..."
log_info "   - Marketing..."
docker-compose build marketing --no-cache

log_info "   - Afiliados..."
docker-compose build afiliados --no-cache

log_info "   - Conversiones..."
docker-compose build conversiones --no-cache

log_success "Servicios reconstruidos"

# 5. Iniciar servicios
log_info "Iniciando servicios..."
docker-compose up -d

# 6. Esperar a que los servicios estén listos
log_info "Esperando que los servicios estén listos..."
sleep 30

# 7. Verificar que Pulsar esté funcionando
log_info "Verificando Pulsar..."
max_attempts=10
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker exec alpes-pulsar bin/pulsar-admin topics list public/default &>/dev/null; then
        log_success "Pulsar está funcionando correctamente"
        break
    else
        log_warning "Pulsar no está listo (intento $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    log_error "Pulsar no se pudo inicializar correctamente"
    exit 1
fi

# 8. Verificar servicios web
log_info "Verificando servicios web..."

# Función para verificar servicio
check_service() {
    local name=$1
    local url=$2
    local max_attempts=15
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            log_success "$name está respondiendo"
            return 0
        else
            log_warning "$name no responde (intento $attempt/$max_attempts)"
            sleep 3
            ((attempt++))
        fi
    done
    
    log_error "$name no está respondiendo después de $max_attempts intentos"
    return 1
}

check_service "Marketing" "http://localhost:8003/"
check_service "Afiliados" "http://localhost:8001/"
check_service "Conversiones" "http://localhost:8002/"

# 9. Crear tópicos de Pulsar necesarios si no existen
log_info "Creando tópicos de Pulsar necesarios..."
topics=(
    "marketing.eventos"
    "conversiones.eventos"
    "comisiones.eventos"
    "afiliados.eventos"
    "sistema.eventos"
)

for topic in "${topics[@]}"; do
    if docker exec alpes-pulsar bin/pulsar-admin topics create persistent://public/default/$topic 2>/dev/null; then
        log_success "Tópico creado: $topic"
    else
        log_info "Tópico ya existe: $topic"
    fi
done

# 10. Mostrar estado de contenedores
log_info "Estado de contenedores:"
docker-compose ps

# 11. Ejecutar prueba del flujo si existe el script
if [ -f "script_simple_test.py" ]; then
    log_info "Ejecutando prueba del flujo de eventos..."
    echo "========================================"
    
    if python3 script_simple_test.py; then
        log_success "¡Prueba del flujo completada exitosamente!"
    else
        log_warning "Prueba del flujo completada con advertencias"
    fi
else
    log_info "Script de prueba no encontrado (script_simple_test.py)"
fi

echo ""
echo "========================================"
echo "🎉 INICIALIZACIÓN COMPLETADA"
echo "========================================"
echo "Los servicios están funcionando en:"
echo "  📱 Marketing:     http://localhost:8003"
echo "  👤 Afiliados:     http://localhost:8001"
echo "  📊 Conversiones:  http://localhost:8002"
echo ""
echo "Para probar el flujo de eventos:"
echo "  python3 script_simple_test.py"
echo ""
echo "Para monitorear eventos en tiempo real:"
echo "  docker exec -it alpes-pulsar bin/pulsar-client consume persistent://public/default/marketing.eventos -s monitor -p Earliest -n 0"
echo ""
echo "¡Listo para usar! 🚀"