#!/usr/bin/env python3
"""
🔍 MONITOR SIMPLE EN TIEMPO REAL - EVENTOS PULSAR
=================================================
Monitor simple que permanece abierto para ver eventos en tiempo real
"""
import pulsar
import json
import threading
import time
from datetime import datetime

class MonitorSimple:
    def __init__(self):
        self.client = None
        self.consumers = {}
        self.running = True
        self.event_count = 0
        
        # Configuración de tópicos
        self.topics_config = {
            'marketing.eventos': {'emoji': '📈', 'name': 'MARKETING'},
            'comisiones.eventos': {'emoji': '💰', 'name': 'COMISIONES'},
            'sistema.eventos': {'emoji': '🔔', 'name': 'SISTEMA'},
            'conversiones.eventos': {'emoji': '📊', 'name': 'CONVERSIONES'}
        }
    
    def conectar_pulsar(self):
        """Conectar a Pulsar"""
        try:
            print("🔗 Conectando a Apache Pulsar...")
            self.client = pulsar.Client('pulsar://localhost:6650')
            print("✅ Conectado a Pulsar exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error conectando a Pulsar: {e}")
            return False
    
    def suscribir_topicos(self):
        """Suscribirse a todos los tópicos"""
        for topic, config in self.topics_config.items():
            try:
                subscription_name = f'monitor-simple-{topic.replace(".", "-")}-{int(time.time())}'
                
                consumer = self.client.subscribe(
                    topic,
                    subscription_name=subscription_name,
                    consumer_type=pulsar.ConsumerType.Shared,
                    initial_position=pulsar.InitialPosition.Latest  # Solo eventos nuevos
                )
                
                self.consumers[topic] = {
                    'consumer': consumer,
                    'config': config,
                    'count': 0
                }
                
                print(f"{config['emoji']} Suscrito a {topic} ({config['name']})")
                
            except Exception as e:
                print(f"❌ Error suscribiéndose a {topic}: {e}")
    
    def monitor_topic(self, topic):
        """Monitor individual para cada tópico"""
        consumer_info = self.consumers[topic]
        consumer = consumer_info['consumer']
        config = consumer_info['config']
        
        while self.running:
            try:
                # Recibir mensaje con timeout
                msg = consumer.receive(timeout_millis=1000)
                
                # Incrementar contadores
                self.event_count += 1
                consumer_info['count'] += 1
                
                # Parsear mensaje
                data = msg.data().decode('utf-8')
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                
                try:
                    event_data = json.loads(data)
                    tipo_evento = event_data.get('tipo_evento', 'Evento desconocido')
                    
                    # Mostrar evento formateado
                    print(f"\n{'='*60}")
                    print(f"{config['emoji']} {config['name']} - {timestamp}")
                    print(f"📡 EVENTO: {tipo_evento}")
                    
                    # Mostrar datos principales
                    if 'datos' in event_data:
                        datos = event_data['datos']
                        if 'id' in datos:
                            print(f"🆔 ID: {datos['id']}")
                        if 'nombre' in datos:
                            print(f"📝 Nombre: {datos['nombre']}")
                        if 'presupuesto' in datos:
                            print(f"💰 Presupuesto: ${datos['presupuesto']:,}")
                        if 'comision' in datos:
                            print(f"💸 Comisión: {datos['comision']}%")
                    
                    print(f"📊 Total eventos en {topic}: {consumer_info['count']}")
                    print(f"{'='*60}")
                    
                except json.JSONDecodeError:
                    print(f"{config['emoji']} {config['name']} - RAW: {data[:100]}...")
                
                # Acknowledge message
                consumer.acknowledge(msg)
                
            except pulsar.exceptions.Timeout:
                # Normal timeout, continuar
                continue
            except Exception as e:
                if self.running:
                    print(f"❌ Error en {topic}: {e}")
                break
    
    def mostrar_header(self):
        """Mostrar header del monitor"""
        print(f"\n{'🔍'*20} MONITOR EN TIEMPO REAL {'🔍'*20}")
        print("🎯 OBJETIVO: Ver eventos distribuidos en vivo")
        print("📡 BROKER: Apache Pulsar")
        print(f"⏰ INICIO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        print("\n📋 TÓPICOS MONITOREADOS:")
        for topic, config in self.topics_config.items():
            print(f"   {config['emoji']} {topic} ({config['name']})")
        
        print("\n💡 INSTRUCCIONES:")
        print("   1. Deja este monitor abierto")
        print("   2. En otra terminal ejecuta: curl -X POST http://localhost:8003/campanas ...")
        print("   3. Observa los eventos aparecer automáticamente")
        print("   4. Presiona Ctrl+C para salir")
        
        print("\n🚀 ¡MONITOR ACTIVO! Esperando eventos...")
        print("="*70 + "\n")
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas periódicas"""
        while self.running:
            time.sleep(30)  # Cada 30 segundos
            if self.running and self.event_count > 0:
                print(f"\n📊 ESTADÍSTICAS ({datetime.now().strftime('%H:%M:%S')}):")
                print(f"   Total eventos: {self.event_count}")
                for topic, consumer_info in self.consumers.items():
                    config = consumer_info['config']
                    count = consumer_info['count']
                    print(f"   {config['emoji']} {topic}: {count} eventos")
                print()
    
    def iniciar_monitor(self):
        """Iniciar el monitor en tiempo real"""
        self.mostrar_header()
        
        # Conectar a Pulsar
        if not self.conectar_pulsar():
            return
        
        # Suscribirse a tópicos
        self.suscribir_topicos()
        
        if not self.consumers:
            print("❌ No se pudo suscribir a ningún tópico")
            return
        
        print("✅ Monitor iniciado - Esperando eventos...\n")
        
        # Iniciar threads para cada tópico
        threads = []
        
        # Thread para estadísticas
        stats_thread = threading.Thread(target=self.mostrar_estadisticas, daemon=True)
        stats_thread.start()
        threads.append(stats_thread)
        
        # Thread para cada tópico
        for topic in self.consumers.keys():
            thread = threading.Thread(target=self.monitor_topic, args=(topic,), daemon=True)
            thread.start()
            threads.append(thread)
        
        try:
            # Mantener el programa corriendo
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo monitor...")
            self.running = False
            
            # Cerrar consumers
            for consumer_info in self.consumers.values():
                try:
                    consumer_info['consumer'].close()
                except:
                    pass
            
            # Cerrar client
            if self.client:
                self.client.close()
            
            print("✅ Monitor detenido")
            print("📊 RESUMEN FINAL:")
            print(f"   Total eventos procesados: {self.event_count}")
            for topic, consumer_info in self.consumers.items():
                config = consumer_info['config']
                count = consumer_info['count']
                print(f"   {config['emoji']} {topic}: {count} eventos")

def main():
    """Función principal"""
    monitor = MonitorSimple()
    monitor.iniciar_monitor()

if __name__ == "__main__":
    main()