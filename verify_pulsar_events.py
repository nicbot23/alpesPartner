#!/usr/bin/env python3
"""
Script para verificar eventos en todos los tópicos de Pulsar
"""
import pulsar
import json
import time
from datetime import datetime

def verificar_eventos():
    print("🚀 VERIFICACIÓN COMPLETA DE EVENTOS EN PULSAR")
    print("=" * 60)
    
    client = pulsar.Client('pulsar://localhost:6650')
    
    topics = [
        'marketing.eventos',
        'comisiones.eventos', 
        'sistema.eventos',
        'conversiones.eventos'
    ]
    
    total_mensajes = 0
    
    for topic in topics:
        print(f"\n📡 Verificando tópico: {topic}")
        print("-" * 40)
        
        try:
            # Crear consumer con subscription temporal
            consumer = client.subscribe(
                topic,
                subscription_name=f'verificador-{topic.replace(".", "-")}-{int(time.time())}',
                consumer_type=pulsar.ConsumerType.Shared,
                initial_position=pulsar.InitialPosition.Earliest
            )
            
            # Leer mensajes por 3 segundos
            mensajes_topic = 0
            timeout = time.time() + 3
            
            while time.time() < timeout:
                try:
                    msg = consumer.receive(timeout_millis=1000)
                    data = msg.data().decode('utf-8')
                    
                    # Intentar parsear como JSON
                    try:
                        event_data = json.loads(data)
                        print(f"   ✅ Evento: {event_data.get('tipo_evento', 'Sin tipo')}")
                        print(f"      📅 Timestamp: {event_data.get('timestamp', 'Sin timestamp')}")
                        if 'datos' in event_data:
                            if 'id' in event_data['datos']:
                                print(f"      🆔 ID: {event_data['datos']['id']}")
                            if 'nombre' in event_data['datos']:
                                print(f"      📝 Nombre: {event_data['datos']['nombre']}")
                    except json.JSONDecodeError:
                        print(f"   ✅ Mensaje (raw): {data[:100]}...")
                    
                    consumer.acknowledge(msg)
                    mensajes_topic += 1
                    total_mensajes += 1
                    
                except pulsar.exceptions.Timeout:
                    break
                    
            if mensajes_topic == 0:
                print("   ❌ No hay mensajes en este tópico")
            else:
                print(f"   📊 Total mensajes: {mensajes_topic}")
                
            consumer.close()
            
        except Exception as e:
            print(f"   ❌ Error accediendo al tópico: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN TOTAL: {total_mensajes} mensajes encontrados")
    
    client.close()

if __name__ == "__main__":
    verificar_eventos()