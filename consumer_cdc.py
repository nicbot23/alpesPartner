#!/usr/bin/env python3

"""
Consumidor de eventos CDC de Pulsar
Este script lee los eventos publicados en el topic outbox-events
"""

import json
import pulsar

def consume_outbox_events():
    """Consumir eventos del topic outbox-events"""
    try:
        client = pulsar.Client('pulsar://localhost:6650')
        
        # Crear consumidor
        consumer = client.subscribe(
            'outbox-events',
            subscription_name='cdc-event-consumer',
            consumer_type=pulsar.ConsumerType.Shared
        )
        
        print("🎧 Iniciando consumidor de eventos CDC...")
        print("📡 Escuchando en topic: outbox-events")
        print("🔄 Presiona Ctrl+C para detener\n")
        
        message_count = 0
        
        try:
            while True:
                msg = consumer.receive(timeout_millis=5000)  # 5 segundos timeout
                
                try:
                    # Decodificar mensaje
                    event_data = json.loads(msg.data().decode('utf-8'))
                    message_count += 1
                    
                    print(f"📨 Mensaje #{message_count}")
                    print(f"   🆔 Event ID: {event_data.get('eventId')}")
                    print(f"   📂 Aggregate Type: {event_data.get('aggregateType')}")
                    print(f"   🎯 Aggregate ID: {event_data.get('aggregateId')}")
                    print(f"   🏷️  Event Type: {event_data.get('eventType')}")
                    print(f"   ⏰ Occurred At: {event_data.get('occurredAt')}")
                    print(f"   📋 Payload: {json.dumps(event_data.get('payload'), indent=2)}")
                    print("   " + "="*60)
                    
                    # Acknowledger mensaje
                    consumer.acknowledge(msg)
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Error decodificando mensaje: {e}")
                    consumer.acknowledge(msg)
                    
        except pulsar.Timeout:
            print(f"\n⏰ Timeout - No hay más mensajes. Total procesados: {message_count}")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Consumidor detenido por el usuario. Total procesados: {message_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        try:
            consumer.close()
            client.close()
            print("🔌 Conexiones cerradas")
        except:
            pass

if __name__ == '__main__':
    consume_outbox_events()
