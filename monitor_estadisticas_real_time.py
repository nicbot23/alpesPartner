#!/usr/bin/env python3
"""
Monitor Específico de Tópicos
=============================

Muestra eventos en tiempo real de tópicos específicos con mejor formato.
"""

import requests
import time
from datetime import datetime

def monitorear_estadisticas_topicos():
    """Monitorear estadísticas en tiempo real"""
    pulsar_admin_url = "http://localhost:8080"
    
    topicos = {
        'marketing.eventos': '🎯',
        'comisiones.eventos': '💰', 
        'sistema.eventos': '📧',
        'afiliados.eventos': '👥',
        'conversiones.eventos': '💱'
    }
    
    print("🔍 MONITOR DE ESTADÍSTICAS DE TÓPICOS EN TIEMPO REAL")
    print("=" * 70)
    
    while True:
        try:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Actualizando estadísticas...")
            print("-" * 70)
            
            total_mensajes = 0
            for topico, icono in topicos.items():
                try:
                    url = f"{pulsar_admin_url}/admin/v2/persistent/public/default/{topico}/stats"
                    response = requests.get(url, timeout=3)
                    
                    if response.status_code == 200:
                        stats = response.json()
                        mensajes = stats.get('msgInCounter', 0)
                        throughput_in = stats.get('msgThroughputIn', 0)
                        subs = len(stats.get('subscriptions', {}))
                        
                        print(f"{icono} {topico:20} | Mensajes: {mensajes:>8,} | Rate: {throughput_in:>6.1f} msg/s | Subs: {subs}")
                        total_mensajes += mensajes
                    else:
                        print(f"{icono} {topico:20} | ❌ No disponible")
                        
                except Exception as e:
                    print(f"{icono} {topico:20} | ❌ Error: {str(e)[:30]}...")
            
            print("-" * 70)
            print(f"📊 TOTAL SISTEMA: {total_mensajes:,} mensajes procesados")
            
            time.sleep(5)  # Actualizar cada 5 segundos
            
        except KeyboardInterrupt:
            print(f"\n🛑 Monitor detenido")
            break
        except Exception as e:
            print(f"\n❌ Error general: {e}")
            time.sleep(3)

if __name__ == "__main__":
    monitorear_estadisticas_topicos()