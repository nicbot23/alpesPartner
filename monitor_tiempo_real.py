#!/usr/bin/env python3
"""
🔍 MONITOR EN TIEMPO REAL - EVENTOS PULSAR
==========================================
Monitor que permanece abierto para ver eventos en tiempo real
Ideal para demostraciones en vivo
"""
import pulsar
import json
import threading
import time
from datetime import datetime
from colorama import Fore, Back, Style, init

# Inicializar colorama
init(autoreset=True)

class MonitorEventosReal:
    def __init__(self):
        self.client = None
        self.consumers = {}
        self.running = True
        self.event_count = 0
        
        # Configuración de tópicos y colores
        self.topics_config = {
            'marketing.eventos': {
                'color': Fore.GREEN,
                'emoji': '📈',
                'description': 'MARKETING'
            },
            'comisiones.eventos': {
                'color': Fore.YELLOW,
                'emoji': '💰',
                'description': 'COMISIONES'
            },
            'sistema.eventos': {
                'color': Fore.BLUE,
                'emoji': '🔔',
                'description': 'SISTEMA'
            },
            'conversiones.eventos': {
                'color': Fore.MAGENTA,
                'emoji': '📊',
                'description': 'CONVERSIONES'
            }
        }
    
    def conectar_pulsar(self):
        """Conectar a Pulsar"""
        try:
            print(f"{Fore.CYAN}🔗 Conectando a Apache Pulsar...")
            self.client = pulsar.Client('pulsar://localhost:6650')
            print(f"{Fore.GREEN}✅ Conectado a Pulsar exitosamente")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error conectando a Pulsar: {e}")
            return False
    
    def suscribir_topicos(self):
        """Suscribirse a todos los tópicos"""
        for topic, config in self.topics_config.items():
            try:
                subscription_name = f'monitor-real-{topic.replace(".", "-")}-{int(time.time())}'
                
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
                
                print(f"{config['color']}{config['emoji']} Suscrito a {topic}")
                
            except Exception as e:
                print(f"{Fore.RED}❌ Error suscribiéndose a {topic}: {e}")
    
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
                    print(f"\n{config['color']}{Back.BLACK}{'='*60}")
                    print(f"{config['color']}{config['emoji']} {config['description']} - {timestamp}")
                    print(f"{config['color']}📡 EVENTO: {tipo_evento}")
                    
                    # Mostrar datos principales
                    if 'datos' in event_data:
                        datos = event_data['datos']
                        if 'id' in datos:
                            print(f"{config['color']}🆔 ID: {datos['id']}")
                        if 'nombre' in datos:
                            print(f"{config['color']}📝 Nombre: {datos['nombre']}")
                        if 'presupuesto' in datos:
                            print(f"{config['color']}💰 Presupuesto: ${datos['presupuesto']:,}")
                        if 'comision' in datos:
                            print(f"{config['color']}💸 Comisión: {datos['comision']}%")
                    
                    print(f"{config['color']}📊 Total eventos en {topic}: {consumer_info['count']}")
                    print(f"{config['color']}{'='*60}{Style.RESET_ALL}")
                    
                except json.JSONDecodeError:
                    print(f"{config['color']}{config['emoji']} {config['description']} - RAW: {data[:100]}...")
                
                # Acknowledge message
                consumer.acknowledge(msg)
                
            except pulsar.exceptions.Timeout:
                # Normal timeout, continuar
                continue
            except Exception as e:
                if self.running:
                    print(f"{Fore.RED}❌ Error en {topic}: {e}")
                break
    
    def mostrar_header(self):
        """Mostrar header del monitor"""
        print(f"\n{Fore.CYAN}{Back.BLACK}{'🔍'*20} MONITOR EN TIEMPO REAL {'🔍'*20}")
        print(f"{Fore.WHITE}🎯 OBJETIVO: Ver eventos distribuidos en vivo")
        print(f"{Fore.WHITE}📡 BROKER: Apache Pulsar")
        print(f"{Fore.WHITE}⏰ INICIO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.CYAN}{'='*70}")
        
        print(f"\n{Fore.WHITE}📋 TÓPICOS MONITOREADOS:")
        for topic, config in self.topics_config.items():
            print(f"   {config['color']}{config['emoji']} {topic} ({config['description']})")
        
        print(f"\n{Fore.YELLOW}💡 INSTRUCCIONES:")
        print(f"{Fore.WHITE}   1. Deja este monitor abierto")
        print(f"{Fore.WHITE}   2. En otra terminal ejecuta: curl -X POST http://localhost:8003/campanas ...")
        print(f"{Fore.WHITE}   3. Observa los eventos aparecer automáticamente")
        print(f"{Fore.WHITE}   4. Presiona Ctrl+C para salir")
        
        print(f"\n{Fore.GREEN}🚀 ¡MONITOR ACTIVO! Esperando eventos...")
        print(f"{Fore.CYAN}{'='*70}\n")
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas periódicas"""
        while self.running:
            time.sleep(30)  # Cada 30 segundos
            if self.running:
                print(f"\n{Fore.CYAN}📊 ESTADÍSTICAS ({datetime.now().strftime('%H:%M:%S')}):")
                print(f"{Fore.WHITE}   Total eventos: {self.event_count}")
                for topic, consumer_info in self.consumers.items():
                    config = consumer_info['config']
                    count = consumer_info['count']
                    print(f"   {config['color']}{config['emoji']} {topic}: {count} eventos")
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
            print(f"{Fore.RED}❌ No se pudo suscribir a ningún tópico")
            return
        
        print(f"{Fore.GREEN}✅ Monitor iniciado - Esperando eventos...\n")
        
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
            print(f"\n{Fore.YELLOW}🛑 Deteniendo monitor...")
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
            
            print(f"{Fore.GREEN}✅ Monitor detenido")
            print(f"{Fore.CYAN}📊 RESUMEN FINAL:")
            print(f"{Fore.WHITE}   Total eventos procesados: {self.event_count}")
            for topic, consumer_info in self.consumers.items():
                config = consumer_info['config']
                count = consumer_info['count']
                print(f"   {config['color']}{config['emoji']} {topic}: {count} eventos")

def main():
    """Función principal"""
    monitor = MonitorEventosReal()
    monitor.iniciar_monitor()

if __name__ == "__main__":
    main()