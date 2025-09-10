#!/usr/bin/env python3

"""
Simulador manual de CDC - Lee eventos del outbox y los publica en Pulsar
Este script demuestra el patrón CDC leyendo la tabla outbox_event 
y publicando los eventos en Pulsar
"""

import json
import time
import mysql.connector
from mysql.connector import Error
import pulsar

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='alpes',
            password='alpes',
            database='alpes'
        )
        return connection
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

def get_pulsar_client():
    """Obtener cliente de Pulsar"""
    try:
        client = pulsar.Client('pulsar://localhost:6650')
        return client
    except Exception as e:
        print(f"❌ Error conectando a Pulsar: {e}")
        return None

def process_outbox_events():
    """Procesar eventos del outbox y publicarlos en Pulsar"""
    connection = get_db_connection()
    if not connection:
        return

    client = get_pulsar_client()
    if not client:
        connection.close()
        return

    try:
        # Crear producer para el topic outbox-events
        producer = client.create_producer('outbox-events')
        
        cursor = connection.cursor(dictionary=True)
        
        # Buscar eventos no publicados
        query = """
        SELECT id, aggregate_type, aggregate_id, event_type, payload, occurred_at
        FROM outbox_event 
        WHERE published = FALSE
        ORDER BY occurred_at ASC
        """
        
        cursor.execute(query)
        events = cursor.fetchall()
        
        print(f"📋 Encontrados {len(events)} eventos no publicados")
        
        for event in events:
            try:
                # Crear mensaje para Pulsar
                message_data = {
                    "eventId": event['id'],
                    "aggregateType": event['aggregate_type'],
                    "aggregateId": event['aggregate_id'],
                    "eventType": event['event_type'],
                    "payload": json.loads(event['payload']),
                    "occurredAt": event['occurred_at'].isoformat() if event['occurred_at'] else None
                }
                
                # Publicar en Pulsar
                producer.send(json.dumps(message_data).encode('utf-8'))
                
                # Marcar como publicado
                update_query = "UPDATE outbox_event SET published = TRUE WHERE id = %s"
                cursor.execute(update_query, (event['id'],))
                connection.commit()
                
                print(f"✅ Evento publicado: {event['event_type']} para {event['aggregate_id']}")
                
            except Exception as e:
                print(f"❌ Error procesando evento {event['id']}: {e}")
                
    except Exception as e:
        print(f"❌ Error general: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
        producer.close()
        client.close()

def main():
    """Función principal"""
    print("🚀 Iniciando simulador CDC manual...")
    print("📡 Buscando eventos no publicados en outbox_event...")
    
    try:
        process_outbox_events()
        print("✅ Procesamiento CDC completado")
        
    except KeyboardInterrupt:
        print("\n⏹️  Detenido por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    main()
