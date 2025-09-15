#!/usr/bin/env python3
"""
Script Simplificado de Prueba - AlpesPartner
===========================================

Script sencillo para probar el flujo completo de eventos usando requests.
Ideal para ejecutar sin dependencias adicionales.

Uso:
    python script_simple_test.py
"""

import requests
import json
import time
import logging
import subprocess
import threading
from datetime import datetime, timedelta

# Configuración
MARKETING_URL = "http://localhost:8003"
CONVERSIONES_URL = "http://localhost:8002"
AFILIADOS_URL = "http://localhost:8001"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verificar_servicios():
    """Verificar que todos los servicios estén activos"""
    logger.info("🔍 Verificando servicios...")
    
    servicios = [
        ("Marketing", MARKETING_URL),
        ("Conversiones", CONVERSIONES_URL),
        ("Afiliados", AFILIADOS_URL)
    ]
    
    for nombre, url in servicios:
        try:
            response = requests.get(f"{url}/", timeout=10)
            if response.status_code == 200:
                logger.info(f"   ✅ {nombre} está activo ({url})")
            else:
                logger.warning(f"   ⚠️ {nombre} responde con status {response.status_code}")
        except Exception as e:
            logger.error(f"   ❌ {nombre} no disponible: {e}")
            return False
            
    return True


def crear_campana_prueba():
    """Crear una campaña de prueba que active todo el flujo"""
    logger.info("🚀 Creando campaña de prueba...")
    
    # Generar datos únicos para la campaña
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    campana_data = {
        "nombre": f"Campaña Auto Test {timestamp}",
        "descripcion": "Campaña generada automáticamente para probar flujo de eventos",
        "tipo": "conversion_tracking",
        "fecha_inicio": datetime.now().isoformat(),
        "fecha_fin": (datetime.now() + timedelta(days=30)).isoformat(),
        "presupuesto": 5000.0,
        "objetivo_conversiones": 100,
        "comision_porcentaje": 15.0,
        "activa": True,
        "parametros_targeting": {
            "edad_min": 18,
            "edad_max": 65,
            "intereses": ["tecnologia", "marketing", "ecommerce"],
            "ubicaciones": ["Colombia", "Mexico", "Peru"]
        }
    }
    
    try:
        response = requests.post(
            f"{MARKETING_URL}/campanas",
            json=campana_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            campana_id = response_data.get("campaign_id") or response_data.get("id")
            logger.info(f"   ✅ Campaña creada exitosamente: {campana_id}")
            logger.info(f"   📝 Nombre: {campana_data['nombre']}")
            return campana_id
        else:
            logger.error(f"   ❌ Error creando campaña: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"   ❌ Excepción creando campaña: {e}")
        return None


def verificar_datos_generados(tiempo_espera=20):
    """Verificar que se generaron datos en todos los servicios"""
    logger.info(f"⏳ Esperando {tiempo_espera}s para procesamiento automático...")
    time.sleep(tiempo_espera)
    
    logger.info("🔍 Verificando datos generados en servicios...")
    
    resultados = {}
    
    # Verificar conversiones
    try:
        response = requests.get(f"{CONVERSIONES_URL}/conversiones", timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 1
            logger.info(f"   ✅ Conversiones: {count} registros encontrados")
            resultados["conversiones"] = count
        else:
            logger.warning(f"   ⚠️ Error consultando conversiones: {response.status_code}")
            resultados["conversiones"] = 0
    except Exception as e:
        logger.error(f"   ❌ Error verificando conversiones: {e}")
        resultados["conversiones"] = 0
        
    # Verificar afiliados
    try:
        response = requests.get(f"{AFILIADOS_URL}/afiliados", timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 1
            logger.info(f"   ✅ Afiliados: {count} registros encontrados")
            resultados["afiliados"] = count
        else:
            logger.warning(f"   ⚠️ Error consultando afiliados: {response.status_code}")
            resultados["afiliados"] = 0
    except Exception as e:
        logger.error(f"   ❌ Error verificando afiliados: {e}")
        resultados["afiliados"] = 0
        
    return resultados


def iniciar_monitor_pulsar():
    """Iniciar un monitor básico de Pulsar para eventos"""
    logger.info("🔍 Iniciando monitor de eventos Pulsar...")
    
    def monitor_eventos():
        try:
            # Intentar monitorear el tópico principal de marketing
            cmd = [
                "docker", "exec", "-i", "alpes-pulsar",
                "bin/pulsar-client", "consume",
                "persistent://public/default/marketing.eventos",
                "-s", "test-monitor",
                "-p", "Earliest",
                "-n", "5"  # Solo 5 mensajes para prueba
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                logger.info("   ✅ Monitor Pulsar ejecutado correctamente")
                if result.stdout:
                    logger.info(f"   📨 Eventos detectados: {result.stdout.count('key:')}")
            else:
                logger.warning(f"   ⚠️ Monitor Pulsar: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.info("   ⏰ Monitor Pulsar timeout (normal en pruebas)")
        except Exception as e:
            logger.error(f"   ❌ Error en monitor Pulsar: {e}")
    
    # Ejecutar en hilo separado para no bloquear
    thread = threading.Thread(target=monitor_eventos, daemon=True)
    thread.start()
    return thread


def ejecutar_prueba_completa():
    """Ejecutar la prueba completa del flujo de eventos"""
    logger.info("🎯 INICIANDO PRUEBA SIMPLIFICADA DEL FLUJO DE EVENTOS")
    logger.info("=" * 60)
    
    exito = True
    
    try:
        # 1. Verificar servicios
        logger.info("1️⃣ Verificando servicios...")
        if not verificar_servicios():
            logger.error("❌ Algunos servicios no están disponibles")
            return False
            
        # 2. Iniciar monitor de eventos
        logger.info("\n2️⃣ Iniciando monitor de eventos...")
        monitor_thread = iniciar_monitor_pulsar()
        time.sleep(2)
        
        # 3. Crear campaña
        logger.info("\n3️⃣ Creando campaña de prueba...")
        campana_id = crear_campana_prueba()
        if not campana_id:
            logger.error("❌ Error creando campaña")
            exito = False
            
        # 4. Verificar datos generados
        logger.info("\n4️⃣ Verificando procesamiento automático...")
        resultados = verificar_datos_generados()
        
        # Resumen final
        logger.info("\n" + "=" * 60)
        logger.info("📋 RESUMEN DE LA PRUEBA:")
        logger.info(f"   🎯 Campaña creada: {'✅' if campana_id else '❌'}")
        logger.info(f"   📊 Conversiones: {resultados.get('conversiones', 0)} registros")
        logger.info(f"   👤 Afiliados: {resultados.get('afiliados', 0)} registros")
        
        # Evaluar éxito
        datos_generados = sum(resultados.values()) > 0
        exito_total = campana_id and datos_generados
        
        if exito_total:
            logger.info("🎉 ¡PRUEBA COMPLETADA EXITOSAMENTE!")
            logger.info("   El flujo de eventos automático está funcionando")
        elif campana_id:
            logger.warning("⚠️ PRUEBA PARCIALMENTE EXITOSA")
            logger.info("   Campaña creada pero eventos automáticos pueden tardar más")
        else:
            logger.error("❌ PRUEBA FALLIDA")
            logger.info("   Verificar configuración de servicios")
            
        return exito_total
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando prueba: {e}")
        return False


def main():
    """Función principal"""
    print("🚀 SCRIPT DE PRUEBA SIMPLIFICADO - ALPESPARTNER")
    print("=" * 50)
    print("Probando flujo: Campaña → Conversión → Comisión → Afiliado")
    print("=" * 50)
    
    resultado = ejecutar_prueba_completa()
    
    if resultado:
        print("\n🎉 ¡ÉXITO! El sistema funciona correctamente")
        return 0
    else:
        print("\n⚠️ REVIZAR: Pueden haber problemas de configuración")
        return 1


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n🛑 Prueba interrumpida por el usuario")
        exit(130)
    except Exception as e:
        print(f"\n❌ Error ejecutando prueba: {e}")
        exit(1)