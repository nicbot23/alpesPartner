#!/usr/bin/env python3

"""
Sistema de Monitoreo y Pruebas CDC Avanzado
Genera eventos, monitorea outbox y verifica publicación en tiempo real
"""

import json
import time
import uuid
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import mysql.connector
from mysql.connector import Error
import pulsar

class CDCTestMonitor:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'alpes',
            'password': 'alpes',
            'database': 'alpes'
        }
        self.pulsar_url = 'pulsar://localhost:6650'
        self.topic_name = 'outbox-events'
        
    def get_db_connection(self):
        """Obtener conexión a la base de datos"""
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            return None

    def create_test_commission(self, conversion_id, affiliate_id, campaign_id, amount, currency):
        """Crear comisión a través de la API"""
        import requests
        
        try:
            response = requests.post('http://localhost:5001/commissions/calculate', 
                json={
                    "conversionId": conversion_id,
                    "affiliateId": affiliate_id,
                    "campaignId": campaign_id,
                    "grossAmount": amount,
                    "currency": currency
                }, timeout=10)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"❌ Error API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error llamando API: {e}")
            return None

    def insert_manual_event(self, event_type, commission_id, payload):
        """Insertar evento manual en outbox para testing"""
        connection = self.get_db_connection()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO outbox_event (
                id, aggregate_type, aggregate_id, event_type, payload, occurred_at, published
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            event_id = str(uuid.uuid4())
            occurred_at = datetime.utcnow()
            
            cursor.execute(query, (
                event_id, 'Commission', commission_id, event_type,
                json.dumps(payload), occurred_at, False
            ))
            
            connection.commit()
            print(f"✅ Evento manual insertado: {event_type} para {commission_id}")
            return event_id
            
        except Error as e:
            print(f"❌ Error insertando evento manual: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_outbox_stats(self):
        """Obtener estadísticas del outbox"""
        connection = self.get_db_connection()
        if not connection:
            return None
            
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Estadísticas generales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_events,
                    SUM(CASE WHEN published = 0 THEN 1 ELSE 0 END) as unpublished_events,
                    SUM(CASE WHEN published = 1 THEN 1 ELSE 0 END) as published_events
                FROM outbox_event
            """)
            stats = cursor.fetchone()
            
            # Eventos recientes no publicados
            cursor.execute("""
                SELECT id, aggregate_id, event_type, occurred_at, published
                FROM outbox_event 
                WHERE published = 0
                ORDER BY occurred_at DESC 
                LIMIT 10
            """)
            unpublished = cursor.fetchall()
            
            return {
                'stats': stats,
                'unpublished_events': unpublished
            }
            
        except Error as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def run_cdc_processor(self):
        """Ejecutar procesador CDC manual"""
        try:
            client = pulsar.Client(self.pulsar_url)
            producer = client.create_producer(self.topic_name)
            
            connection = self.get_db_connection()
            if not connection:
                return 0
                
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
            
            processed_count = 0
            
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
                    
                    processed_count += 1
                    print(f"✅ Procesado: {event['event_type']} -> {event['aggregate_id']}")
                    
                except Exception as e:
                    print(f"❌ Error procesando evento {event['id']}: {e}")
                    
            return processed_count
            
        except Exception as e:
            print(f"❌ Error en CDC processor: {e}")
            return 0
        finally:
            try:
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()
                if 'producer' in locals():
                    producer.close()
                if 'client' in locals():
                    client.close()
            except:
                pass

    def monitor_pulsar_consumption(self, duration_seconds=30):
        """Monitorear consumo de eventos desde Pulsar"""
        try:
            client = pulsar.Client(self.pulsar_url)
            consumer = client.subscribe(
                self.topic_name,
                subscription_name='test-monitor',
                consumer_type=pulsar.ConsumerType.Shared
            )
            
            print(f"🎧 Monitoreando Pulsar por {duration_seconds} segundos...")
            
            events_received = []
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                try:
                    msg = consumer.receive(timeout_millis=2000)
                    
                    event_data = json.loads(msg.data().decode('utf-8'))
                    events_received.append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'event_type': event_data.get('eventType'),
                        'aggregate_id': event_data.get('aggregateId'),
                        'event_id': event_data.get('eventId')
                    })
                    
                    consumer.acknowledge(msg)
                    print(f"📨 Recibido: {event_data.get('eventType')} para {event_data.get('aggregateId')}")
                    
                except pulsar.Timeout:
                    continue
                    
            return events_received
            
        except Exception as e:
            print(f"❌ Error monitoreando Pulsar: {e}")
            return []
        finally:
            try:
                if 'consumer' in locals():
                    consumer.close()
                if 'client' in locals():
                    client.close()
            except:
                pass

def generate_test_scenarios():
    """Generar escenarios de prueba diversos"""
    scenarios = []
    
    # Escenario 1: Comisiones normales
    for i in range(3):
        scenarios.append({
            'type': 'api_commission',
            'data': {
                'conversion_id': f'test-conv-{int(time.time())}-{i}',
                'affiliate_id': f'aff-{random.randint(100, 999)}',
                'campaign_id': f'camp-{random.randint(100, 999)}',
                'amount': round(random.uniform(100, 5000), 2),
                'currency': random.choice(['USD', 'EUR', 'GBP', 'CAD'])
            }
        })
    
    # Escenario 2: Eventos manuales para testing
    for i in range(2):
        commission_id = f'manual-test-{int(time.time())}-{i}'
        scenarios.append({
            'type': 'manual_event',
            'data': {
                'event_type': 'CommissionCalculated',
                'commission_id': commission_id,
                'payload': {
                    'eventVersion': 2,
                    'commissionId': commission_id,
                    'amount': round(random.uniform(50, 1000), 2),
                    'currency': random.choice(['USD', 'EUR']),
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            }
        })
    
    return scenarios

def main():
    """Función principal de pruebas"""
    print("🚀 SISTEMA DE PRUEBAS CDC AVANZADO - AlpesPartner")
    print("=" * 60)
    
    monitor = CDCTestMonitor()
    
    # Obtener estadísticas iniciales
    print("\n📊 Estado inicial del sistema:")
    initial_stats = monitor.get_outbox_stats()
    if initial_stats:
        stats = initial_stats['stats']
        print(f"   Total eventos: {stats['total_events']}")
        print(f"   No publicados: {stats['unpublished_events']}")
        print(f"   Publicados: {stats['published_events']}")
    
    # Generar escenarios de prueba
    print("\n🧪 Generando escenarios de prueba...")
    scenarios = generate_test_scenarios()
    
    events_created = 0
    
    # Ejecutar escenarios
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🔄 Escenario {i}/{len(scenarios)}: {scenario['type']}")
        
        if scenario['type'] == 'api_commission':
            data = scenario['data']
            result = monitor.create_test_commission(
                data['conversion_id'], data['affiliate_id'], 
                data['campaign_id'], data['amount'], data['currency']
            )
            if result:
                events_created += 1
                print(f"   ✅ Comisión creada: {result.get('commissionId', 'N/A')}")
            else:
                print("   ❌ Error creando comisión")
                
        elif scenario['type'] == 'manual_event':
            data = scenario['data']
            result = monitor.insert_manual_event(
                data['event_type'], data['commission_id'], data['payload']
            )
            if result:
                events_created += 1
                print(f"   ✅ Evento manual creado: {result}")
            else:
                print("   ❌ Error creando evento manual")
        
        # Pequeña pausa entre escenarios
        time.sleep(1)
    
    print(f"\n📈 Se generaron {events_created} nuevos eventos")
    
    # Monitoreo en tiempo real
    print("\n🔄 Iniciando ciclo de monitoreo CDC...")
    
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteración {iteration}/{max_iterations} ---")
        
        # Obtener estadísticas actuales
        current_stats = monitor.get_outbox_stats()
        if current_stats:
            stats = current_stats['stats']
            unpublished = current_stats['unpublished_events']
            
            print(f"📊 Total: {stats['total_events']} | No publicados: {stats['unpublished_events']} | Publicados: {stats['published_events']}")
            
            if stats['unpublished_events'] > 0:
                print(f"🔄 Procesando {stats['unpublished_events']} eventos no publicados...")
                
                # Ejecutar CDC processor
                processed = monitor.run_cdc_processor()
                print(f"✅ Procesados: {processed} eventos")
                
                if processed > 0:
                    # Monitorear recepción en Pulsar
                    print("📡 Verificando recepción en Pulsar...")
                    received_events = monitor.monitor_pulsar_consumption(duration_seconds=10)
                    print(f"📨 Eventos recibidos en Pulsar: {len(received_events)}")
                    
                    for event in received_events:
                        print(f"   • {event['event_type']} -> {event['aggregate_id']}")
                
            else:
                print("✅ Todos los eventos están publicados")
                break
        
        # Pausa antes de la siguiente iteración
        if iteration < max_iterations:
            print("⏳ Esperando 5 segundos antes de la siguiente verificación...")
            time.sleep(5)
    
    # Estadísticas finales
    print("\n📊 RESUMEN FINAL:")
    final_stats = monitor.get_outbox_stats()
    if final_stats:
        stats = final_stats['stats']
        print(f"   📈 Total eventos: {stats['total_events']}")
        print(f"   ✅ Publicados: {stats['published_events']}")
        print(f"   ⏳ Pendientes: {stats['unpublished_events']}")
        
        if stats['unpublished_events'] > 0:
            print("\n⚠️  Eventos pendientes de publicar:")
            for event in final_stats['unpublished_events']:
                print(f"   • {event['event_type']} - {event['aggregate_id']} ({event['occurred_at']})")
        else:
            print("\n🎉 ¡Todos los eventos han sido publicados exitosamente!")
    
    print("\n✅ Pruebas CDC completadas")

if __name__ == '__main__':
    main()
