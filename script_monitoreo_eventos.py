#!/usr/bin/env python3
"""
Script para generar una campaña y monitorear eventos en tiempo real
Demuestra el flujo automático de eventos en el sistema de microservicios
"""

import requests
import time
import subprocess
import threading
import signal
import sys
import json
from datetime import datetime

# Configuración
MARKETING_URL = "http://localhost:8003"
CONVERSIONES_URL = "http://localhost:8002"
AFILIADOS_URL = "http://localhost:8001"

def log_evento(mensaje):
    """Log con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}")

def crear_campana():
    """Crear una nueva campaña"""
    log_evento("🚀 Creando nueva campaña...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    campana_data = {
        "nombre": f"Campaña Monitor Eventos {timestamp}",
        "descripcion": f"Campaña para monitoreo de eventos - {timestamp}",
        "comision": 15.5,
        "presupuesto": 12000.0
    }
    
    try:
        response = requests.post(f"{MARKETING_URL}/campanas", json=campana_data, timeout=10)
        if response.status_code in [200, 201]:
            campana = response.json()
            log_evento(f"✅ Campaña creada exitosamente:")
            log_evento(f"   - ID: {campana.get('id', 'N/A')}")
            log_evento(f"   - Nombre: {campana.get('nombre', 'N/A')}")
            log_evento(f"   - Comisión: {campana.get('comision', 'N/A')}%")
            log_evento(f"   - Presupuesto: ${campana.get('presupuesto', 'N/A')}")
            return campana
        else:
            log_evento(f"❌ Error al crear campaña: {response.status_code}")
            log_evento(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        log_evento(f"❌ Error de conexión al crear campaña: {str(e)}")
        return None

def monitorear_topico(topico, duracion=30):
    """Monitorear un tópico específico por un tiempo determinado"""
    def monitor():
        log_evento(f"👁️  Iniciando monitoreo del tópico: {topico}")
        cmd = [
            "docker", "exec", "-i", "alpes-pulsar",
            "bin/pulsar-client", "consume",
            f"persistent://public/default/{topico}",
            "-s", f"monitor-{topico}-{int(time.time())}",
            "-p", "Earliest",
            "-n", "0"  # Consume indefinidamente
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
            
            start_time = time.time()
            eventos_encontrados = 0
            
            while time.time() - start_time < duracion:
                if process.poll() is not None:
                    break
                    
                try:
                    line = process.stdout.readline()
                    if line:
                        line = line.strip()
                        if "key:" in line or "properties:" in line or "value:" in line:
                            eventos_encontrados += 1
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            log_evento(f"📨 [{topico}] Evento #{eventos_encontrados} detectado ({timestamp})")
                            log_evento(f"   💬 {line}")
                        elif "INFO" in line and "Connected" in line:
                            log_evento(f"🔗 [{topico}] Conectado al tópico")
                        elif "subscrib" in line.lower():
                            log_evento(f"📥 [{topico}] Suscripción establecida")
                except:
                    continue
            
            process.terminate()
            log_evento(f"⏹️  [{topico}] Monitoreo finalizado - {eventos_encontrados} eventos detectados")
            
        except Exception as e:
            log_evento(f"❌ Error monitoreando {topico}: {str(e)}")
    
    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    return thread

def verificar_microservicios():
    """Verificar que todos los microservicios estén activos"""
    log_evento("🔍 Verificando estado de microservicios...")
    
    servicios = [
        ("Marketing", MARKETING_URL),
        ("Conversiones", CONVERSIONES_URL),
        ("Afiliados", AFILIADOS_URL)
    ]
    
    activos = 0
    for nombre, url in servicios:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                log_evento(f"✅ {nombre}: ACTIVO")
                activos += 1
            else:
                log_evento(f"⚠️  {nombre}: Respuesta inesperada ({response.status_code})")
        except Exception as e:
            log_evento(f"❌ {nombre}: NO DISPONIBLE ({str(e)})")
    
    return activos == len(servicios)

def main():
    """Función principal"""
    log_evento("=" * 60)
    log_evento("🎯 MONITOR DE EVENTOS - ALPES PARTNER")
    log_evento("   Generación de campaña y monitoreo automático")
    log_evento("=" * 60)
    
    # Verificar microservicios
    if not verificar_microservicios():
        log_evento("❌ No todos los microservicios están disponibles")
        log_evento("💡 Asegúrate de ejecutar: docker-compose up -d")
        return
    
    log_evento("✅ Todos los microservicios están activos")
    log_evento("")
    
    # Iniciar monitoreo de todos los tópicos
    log_evento("🎬 Iniciando monitoreo de eventos...")
    topicos = ["marketing.eventos", "conversiones.eventos", "afiliados.eventos", "comisiones.eventos"]
    
    threads = []
    for topico in topicos:
        thread = monitorear_topico(topico, duracion=45)
        threads.append(thread)
        time.sleep(1)  # Pequeña pausa entre inicializaciones
    
    log_evento("")
    log_evento("⏱️  Esperando 5 segundos para estabilizar monitoreo...")
    time.sleep(5)
    
    # Crear campaña (esto debería disparar los eventos automáticamente)
    log_evento("")
    campana = crear_campana()
    
    if campana:
        log_evento("")
        log_evento("🔄 Flujo automático iniciado! Los eventos deberían aparecer en:")
        log_evento("   1️⃣  marketing.eventos → CampanaCreada")
        log_evento("   2️⃣  conversiones.eventos → ConversionDetectada") 
        log_evento("   3️⃣  afiliados.eventos → AfiliadoRegistrado")
        log_evento("   4️⃣  comisiones.eventos → ComisionCalculada")
        log_evento("")
        log_evento("👀 Monitoreando eventos por 40 segundos más...")
        log_evento("   (Presiona Ctrl+C para detener)")
        
        try:
            time.sleep(40)
        except KeyboardInterrupt:
            log_evento("\n⏹️  Monitoreo interrumpido por el usuario")
    else:
        log_evento("❌ No se pudo crear la campaña, deteniendo monitoreo...")
    
    log_evento("")
    log_evento("🏁 Monitoreo finalizado")
    log_evento("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_evento("\n👋 Monitoreo cancelado por el usuario")
        sys.exit(0)
    except Exception as e:
        log_evento(f"❌ Error inesperado: {str(e)}")
        sys.exit(1)