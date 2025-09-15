#!/bin/bash

echo "🎯 ==============================="
echo "🔥 MONITOR DE EVENTOS EN TIEMPO REAL"
echo "🎯 ==============================="
echo ""

# Verificar que Pulsar esté corriendo
if ! docker ps | grep -q "alpes-pulsar"; then
    echo "❌ Error: Pulsar no está corriendo"
    exit 1
fi

echo "📋 Tópicos disponibles:"
docker exec alpes-pulsar bin/pulsar-admin topics list public/default
echo ""

echo "🔍 Estadísticas de eventos por tópico:"
echo ""

# Marketing
echo "📈 MARKETING.EVENTOS:"
MARKETING_STATS=$(docker exec alpes-pulsar bin/pulsar-admin topics stats persistent://public/default/marketing.eventos 2>/dev/null | grep -E "(msgInCounter|msgOutCounter)" | head -2)
echo "   $MARKETING_STATS"

# Conversiones  
echo "📈 CONVERSIONES.EVENTOS:"
CONVERSIONES_STATS=$(docker exec alpes-pulsar bin/pulsar-admin topics stats persistent://public/default/conversiones.eventos 2>/dev/null | grep -E "(msgInCounter|msgOutCounter)" | head -2)
echo "   $CONVERSIONES_STATS"

# Afiliados
echo "📈 AFILIADOS.EVENTOS:"
AFILIADOS_STATS=$(docker exec alpes-pulsar bin/pulsar-admin topics stats persistent://public/default/afiliados.eventos 2>/dev/null | grep -E "(msgInCounter|msgOutCounter)" | head -2)
echo "   $AFILIADOS_STATS"

# Comisiones
echo "📈 COMISIONES.EVENTOS:"
COMISIONES_STATS=$(docker exec alpes-pulsar bin/pulsar-admin topics stats persistent://public/default/comisiones.eventos 2>/dev/null | grep -E "(msgInCounter|msgOutCounter)" | head -2)
echo "   $COMISIONES_STATS"

# Sistema
echo "📈 SISTEMA.EVENTOS:"
SISTEMA_STATS=$(docker exec alpes-pulsar bin/pulsar-admin topics stats persistent://public/default/sistema.eventos 2>/dev/null | grep -E "(msgInCounter|msgOutCounter)" | head -2)
echo "   $SISTEMA_STATS"

echo ""
echo "🎯 ==============================="
echo "✅ RESUMEN EXITOSO"
echo "🎯 ==============================="

echo ""
echo "📋 Para monitorear eventos en tiempo real, ejecuta:"
echo "   docker exec -i alpes-pulsar bin/pulsar-client consume persistent://public/default/marketing.eventos -s monitor-marketing -p Earliest -n 0"
echo "   docker exec -i alpes-pulsar bin/pulsar-client consume persistent://public/default/conversiones.eventos -s monitor-conversiones -p Earliest -n 0"
echo "   docker exec -i alpes-pulsar bin/pulsar-client consume persistent://public/default/afiliados.eventos -s monitor-afiliados -p Earliest -n 0"