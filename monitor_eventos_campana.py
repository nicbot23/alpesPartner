#!/usr/bin/env python3
"""
Monitor de Eventos de Campaña - AlpesPartner
Monitorea los tópicos de Pulsar para verificar el flujo de eventos cuando se crea una campaña
"""

import asyncio
import json
import threading
import time
from datetime import datetime
from colorama import init, Fore, Back, Style
import subprocess
import signal
import sys

# Inicializar colorama
init(autoreset=True)

class EventMonitor:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def colored_output(self, text, color=Fore.WHITE, bg=Back.BLACK):
        """Función para texto coloreado"""
        return f"{color}{bg}{text}{Style.RESET_ALL}"
    
    def get_timestamp(self):
        """Obtiene timestamp actual"""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    def monitor_topic(self, topic_name, color, subscription_name):
        """Monitorea un tópico específico de Pulsar"""
        print(f"{self.colored_output(f'[{self.get_timestamp()}] Iniciando monitor para {topic_name}', color)}")
        
        cmd = [
            'docker', 'exec', '-i', 'alpes-pulsar',
            'bin/pulsar-client', 'consume',
            f'persistent://public/default/{topic_name}',
            '-s', subscription_name,
            '-p', 'Latest',  # Solo nuevos eventos
            '-n', '0'  # Infinito
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes.append(process)
            
            print(f"{self.colored_output(f'[{self.get_timestamp()}] ✅ Monitor {topic_name} iniciado', color)}")
            
            while self.running and process.poll() is None:
                line = process.stdout.readline()
                if line.strip():
                    timestamp = self.get_timestamp()
                    if line.startswith('----- got message -----'):
                        print(f"{self.colored_output(f'[{timestamp}] 🔥 EVENTO RECIBIDO EN {topic_name.upper()}', color, Back.BLACK)}")
                    elif 'messageId' in line or 'data:' in line or '{' in line:
                        # Filtrar solo líneas importantes
                        clean_line = line.strip()
                        if clean_line:
                            print(f"{self.colored_output(f'[{timestamp}] [{topic_name}]', color)} {clean_line}")
                            
        except Exception as e:
            print(f"{self.colored_output(f'[{self.get_timestamp()}] ❌ Error en monitor {topic_name}: {e}', Fore.RED)}")
    
    def start_monitoring(self):
        """Inicia el monitoreo de todos los tópicos"""
        topics = [
            ('marketing.eventos', Fore.CYAN, 'monitor-marketing-test'),
            ('comisiones.eventos', Fore.GREEN, 'monitor-comisiones-test'),
            ('afiliados.eventos', Fore.YELLOW, 'monitor-afiliados-test'),
            ('conversiones.eventos', Fore.MAGENTA, 'monitor-conversiones-test'),
            ('sistema.eventos', Fore.WHITE, 'monitor-sistema-test')
        ]
        
        print(f"{self.colored_output('='*80, Fore.BLUE, Back.WHITE)}")
        print(f"{self.colored_output('🚀 MONITOR DE EVENTOS - CAMPAÑA ALPESPARTNER', Fore.BLUE, Back.WHITE)}")
        print(f"{self.colored_output('='*80, Fore.BLUE, Back.WHITE)}")
        print()
        
        # Crear hilos para cada tópico
        threads = []
        for topic, color, subscription in topics:
            thread = threading.Thread(
                target=self.monitor_topic,
                args=(topic, color, subscription),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            time.sleep(0.5)  # Pequeña pausa entre inicios
        
        print()
        print(f"{self.colored_output('🔍 TODOS LOS MONITORES ACTIVOS - Esperando eventos...', Fore.GREEN, Back.BLACK)}")
        print(f"{self.colored_output('💡 Ejecuta una campaña desde otro terminal:', Fore.BLUE)}")
        print(f"{self.colored_output('   curl -X POST http://localhost:8003/campanas', Fore.WHITE)}")
        print(f"{self.colored_output('     -H \"Content-Type: application/json\" -d \"{{...}}\"', Fore.WHITE)}")
        print()
        print(f"{self.colored_output('⏹️  Presiona Ctrl+C para detener el monitoreo', Fore.RED)}")
        print(f"{self.colored_output('-'*80, Fore.WHITE)}")
        print()
        
        try:
            # Mantener el programa vivo
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Detiene todos los monitores"""
        print(f"\n{self.colored_output('🛑 Deteniendo monitores...', Fore.RED)}")
        self.running = False
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        print(f"{self.colored_output('✅ Monitores detenidos', Fore.GREEN)}")

def signal_handler(sig, frame):
    """Manejador de señales para cierre limpio"""
    print(f"\n{Fore.RED}🛑 Señal de interrupción recibida...")
    sys.exit(0)

if __name__ == "__main__":
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Crear y ejecutar monitor
    monitor = EventMonitor()
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        monitor.stop_monitoring()
    except Exception as e:
        print(f"{Fore.RED}❌ Error inesperado: {e}")
        monitor.stop_monitoring()