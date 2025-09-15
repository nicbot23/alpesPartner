#!/bin/bash

echo "🚀 Iniciando Pulsar y configurando tópicos..."

# Iniciar Pulsar en segundo plano
echo "⏳ Iniciando Pulsar standalone..."
bin/pulsar standalone &
PULSAR_PID=$!

# Esperar a que Pulsar esté completamente listo
echo "⏳ Esperando que Pulsar esté listo..."
sleep 30

# Verificar que el proceso siga corriendo
if ! kill -0 $PULSAR_PID 2>/dev/null; then
    echo "❌ Error: Pulsar no se inició correctamente"
    exit 1
fi

echo "✅ Pulsar está listo!"

# Crear los tópicos necesarios
echo "📝 Creando tópicos de eventos..."

# Tópicos principales
bin/pulsar-admin topics create persistent://public/default/marketing.eventos || echo "Tópico marketing.eventos ya existe"
bin/pulsar-admin topics create persistent://public/default/conversiones.eventos || echo "Tópico conversiones.eventos ya existe"
bin/pulsar-admin topics create persistent://public/default/afiliados.eventos || echo "Tópico afiliados.eventos ya existe"
bin/pulsar-admin topics create persistent://public/default/comisiones.eventos || echo "Tópico comisiones.eventos ya existe"
bin/pulsar-admin topics create persistent://public/default/sistema.eventos || echo "Tópico sistema.eventos ya existe"

echo "🎯 Listando tópicos creados:"
bin/pulsar-admin topics list public/default

echo "✅ Configuración de tópicos completada!"

# Esperar que el proceso de Pulsar termine
wait $PULSAR_PID