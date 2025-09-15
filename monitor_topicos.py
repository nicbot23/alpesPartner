#!/usr/bin/env python3
"""
Monitor Avanzado de Tópicos de Pulsar
=====================================

Monitorea eventos en tiempo real de todos los tópicos de los microservicios
para verificar que la comunicación entre servicios funciona correctamente.
"""

import requests
import json
import threading
import time
from datetime import datetime
import sys

class MonitorTopicos:
    def __init__(self):
        self.pulsar_admin_url = "http://localhost:8080"  # Pulsar Admin API
        self.marketing_url = "http://localhost:8003"
        
        # Tópicos a monitorear
        self.topicos = {
            'marketing.eventos': '🎯 Marketing',
            'comisiones.eventos': '💰 Comisiones', 
            'sistema.eventos': '📧 Sistema',
            'afiliados.eventos': '👥 Afiliados',
            'conversiones.eventos': '💱 Conversiones'
        }
        
        # Contadores de eventos
        self.contadores = {topico: 0 for topico in self.topicos.keys()}
        self.ultimo_evento = {topico: None for topico in self.topicos.keys()}
        
        self.running = False
        
    def verificar_pulsar_disponible(self):
        """Verificar si Pulsar Admin API está disponible"""
        try:
            response = requests.get(f"{self.pulsar_admin_url}/admin/v2/clusters", timeout=5)
            if response.status_code == 200:
                print("✅ Pulsar Admin API disponible")
                return True
            else:
                print(f"❌ Pulsar Admin API no responde correctamente: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error conectando con Pulsar Admin API: {e}")
            return False
    
    def obtener_estadisticas_topico(self, topico):
        """Obtener estadísticas de un tópico específico"""
        try:
            url = f"{self.pulsar_admin_url}/admin/v2/persistent/public/default/{topico}/stats"
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                stats = response.json()
                return {
                    'mensajes_totales': stats.get('msgInCounter', 0),
                    'throughput_in': stats.get('msgThroughputIn', 0),
                    'throughput_out': stats.get('msgThroughputOut', 0),
                    'storage_size': stats.get('storageSize', 0),
                    'subscriptions': len(stats.get('subscriptions', {}))
                }
            else:
                return None
        except Exception as e:
            return None
    
    def obtener_suscripciones_topico(self, topico):
        """Obtener suscripciones activas de un tópico"""
        try:
            url = f"{self.pulsar_admin_url}/admin/v2/persistent/public/default/{topico}/subscriptions"
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            return []
    
    def mostrar_estado_topicos(self):
        """Mostrar estado actual de todos los tópicos"""
        print("\n" + "="*100)
        print(f"🔍 ESTADO DE TÓPICOS PULSAR - {datetime.now().strftime('%H:%M:%S')}")
        print("="*100)
        
        for topico, descripcion in self.topicos.items():
            stats = self.obtener_estadisticas_topico(topico)
            subs = self.obtener_suscripciones_topico(topico)
            
            print(f"\n{descripcion} ({topico}):")
            
            if stats:
                print(f"   📊 Mensajes totales: {stats['mensajes_totales']}")
                print(f"   📈 Throughput IN: {stats['throughput_in']:.2f} msg/s")
                print(f"   📉 Throughput OUT: {stats['throughput_out']:.2f} msg/s")
                print(f"   💾 Tamaño almacenado: {stats['storage_size']} bytes")
                print(f"   👥 Suscripciones activas: {stats['subscriptions']}")
                
                if subs:
                    print(f"   🔗 Suscriptores: {', '.join(subs[:3])}{'...' if len(subs) > 3 else ''}")
            else:
                print(f"   ❌ No se pudieron obtener estadísticas")
    
    def crear_campana_test(self):
        """Crear una campaña de prueba para generar eventos"""
        try:
            data = {
                "nombre": f"Test Monitor {int(time.time())}",
                "descripcion": "Campaña para verificar eventos en tiempo real",
                "tipo_campana": "digital",
                "meta_conversiones": 100,
                "presupuesto": 5000.0,
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-12-31"
            }
            
            response = requests.post(f"{self.marketing_url}/campanas", json=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Campaña de prueba creada: {data['nombre']} (ID: {result.get('id', 'N/A')})")
                return True
            else:
                print(f"❌ Error creando campaña de prueba: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en campaña de prueba: {e}")
            return False
    
    def monitor_continuo(self, intervalo=5, auto_test=False):
        """Monitorear tópicos de forma continua"""
        print(f"🚀 INICIANDO MONITOR CONTINUO DE TÓPICOS")
        print(f"⏱️  Intervalo de actualización: {intervalo}s")
        print(f"🧪 Auto-test: {'Activado' if auto_test else 'Desactivado'}")
        print("Press Ctrl+C para detener")
        
        if not self.verificar_pulsar_disponible():
            print("❌ No se puede conectar con Pulsar. Verifica que esté funcionando.")
            return
        
        self.running = True
        contador_ciclos = 0
        
        try:
            while self.running:
                self.mostrar_estado_topicos()
                
                # Auto-test cada 3 ciclos
                if auto_test and contador_ciclos % 3 == 0:
                    print(f"\n🧪 Ejecutando auto-test (ciclo {contador_ciclos + 1})...")
                    self.crear_campana_test()
                
                contador_ciclos += 1
                
                print(f"\n⏳ Esperando {intervalo}s... (Ctrl+C para detener)")
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitor detenido por usuario")
        except Exception as e:
            print(f"\n❌ Error en monitor: {e}")
        finally:
            self.running = False
    
    def mostrar_resumen_topicos(self):
        """Mostrar un resumen rápido de todos los tópicos"""
        if not self.verificar_pulsar_disponible():
            return
            
        print("📋 RESUMEN RÁPIDO DE TÓPICOS:")
        print("-" * 50)
        
        for topico, descripcion in self.topicos.items():
            stats = self.obtener_estadisticas_topico(topico)
            if stats:
                print(f"{descripcion}: {stats['mensajes_totales']} mensajes, {stats['subscriptions']} suscriptores")
            else:
                print(f"{descripcion}: ❌ Sin datos")

def main():
    """Función principal"""
    monitor = MonitorTopicos()
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "resumen":
            monitor.mostrar_resumen_topicos()
        elif comando == "test":
            print("🧪 Ejecutando campaña de prueba...")
            monitor.crear_campana_test()
        elif comando == "continuo":
            auto_test = "--auto-test" in sys.argv
            monitor.monitor_continuo(intervalo=3, auto_test=auto_test)
        else:
            print(f"❌ Comando '{comando}' no reconocido")
    else:
        print("""
🔍 MONITOR DE TÓPICOS PULSAR
===========================

Comandos disponibles:

1. python3 monitor_topicos.py resumen
   → Mostrar resumen rápido de todos los tópicos

2. python3 monitor_topicos.py test  
   → Crear campaña de prueba para generar eventos

3. python3 monitor_topicos.py continuo
   → Monitor continuo cada 3 segundos

4. python3 monitor_topicos.py continuo --auto-test
   → Monitor continuo + auto-test cada 3 ciclos

Ejemplo de uso:
python3 monitor_topicos.py continuo --auto-test
""")

if __name__ == "__main__":
    main()