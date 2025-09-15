#!/usr/bin/env python3
"""
Script de Prueba del Flujo Completo de Eventos - AlpesPartner
===========================================================

Este script automatiza y valida el flujo completo de eventos:
1. Crear una campaña en Marketing
2. Validar que conversiones escuche automáticamente y genere conversiones
3. Validar que comisiones se calculen automáticamente
4. Validar que afiliados se registren automáticamente
5. Monitorear todos los eventos generados

Flujo Esperado:
--------------
POST /campanas → CampanaCreada → ConversionDetectada → ComisionCalculada + AfiliadoRegistrado

Uso:
    python script_flujo_eventos.py
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime, timedelta
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

# Configuración
MARKETING_URL = "http://localhost:8003"
CONVERSIONES_URL = "http://localhost:8002"
AFILIADOS_URL = "http://localhost:8001"
PULSAR_CONTAINER = "alpes-pulsar"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MonitorEventos:
    """Clase para monitorear eventos de Pulsar en tiempo real"""
    
    def __init__(self):
        self.eventos_detectados = {}
        self.monitores_activos = []
        
    def iniciar_monitor_topico(self, topico, nombre_monitor):
        """Iniciar monitor de un tópico específico"""
        def monitor():
            try:
                cmd = [
                    "docker", "exec", "-i", PULSAR_CONTAINER,
                    "bin/pulsar-client", "consume",
                    f"persistent://public/default/{topico}",
                    "-s", f"{nombre_monitor}-script-monitor",
                    "-p", "Earliest",
                    "-n", "0"
                ]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                logger.info(f"🔍 Monitor iniciado para tópico: {topico}")
                
                for line in iter(process.stdout.readline, ''):
                    if line.strip():
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        evento_info = f"[{timestamp}] {topico}: {line.strip()}"
                        
                        if topico not in self.eventos_detectados:
                            self.eventos_detectados[topico] = []
                        
                        self.eventos_detectados[topico].append(evento_info)
                        logger.info(f"📨 EVENTO DETECTADO en {topico}: {line.strip()}")
                        
            except Exception as e:
                logger.error(f"Error en monitor {topico}: {e}")
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        self.monitores_activos.append(thread)
        
    def iniciar_todos_los_monitores(self):
        """Iniciar monitores para todos los tópicos relevantes"""
        topicos = [
            ("marketing.eventos", "marketing"),
            ("conversiones.eventos", "conversiones"), 
            ("comisiones.eventos", "comisiones"),
            ("afiliados.eventos", "afiliados"),
            ("sistema.eventos", "sistema")
        ]
        
        for topico, nombre in topicos:
            self.iniciar_monitor_topico(topico, nombre)
            time.sleep(0.5)  # Espaciar los inicios
            
        logger.info("🚀 Todos los monitores de eventos iniciados")

    def obtener_resumen_eventos(self):
        """Obtener resumen de eventos detectados"""
        resumen = {}
        for topico, eventos in self.eventos_detectados.items():
            resumen[topico] = len(eventos)
        return resumen


class ProbadorFlujoEventos:
    """Clase principal para probar el flujo completo de eventos"""
    
    def __init__(self):
        self.monitor = MonitorEventos()
        self.session = None
        self.campana_id = None
        
    async def verificar_servicios(self):
        """Verificar que todos los servicios estén activos"""
        logger.info("🔍 Verificando servicios...")
        
        servicios = [
            ("Marketing", MARKETING_URL),
            ("Conversiones", CONVERSIONES_URL),
            ("Afiliados", AFILIADOS_URL)
        ]
        
        for nombre, url in servicios:
            try:
                async with self.session.get(f"{url}/") as response:
                    if response.status == 200:
                        logger.info(f"   ✅ {nombre} está activo ({url})")
                    else:
                        logger.warning(f"   ⚠️ {nombre} responde con status {response.status}")
            except Exception as e:
                logger.error(f"   ❌ {nombre} no disponible: {e}")
                return False
                
        return True
    
    async def crear_campana_prueba(self):
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
            async with self.session.post(
                f"{MARKETING_URL}/api/v1/campanas",
                json=campana_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 201:
                    response_data = await response.json()
                    self.campana_id = response_data.get("id")
                    logger.info(f"   ✅ Campaña creada exitosamente: {self.campana_id}")
                    logger.info(f"   📝 Nombre: {campana_data['nombre']}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"   ❌ Error creando campaña: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"   ❌ Excepción creando campaña: {e}")
            return False
    
    async def validar_eventos_automaticos(self, tiempo_espera=30):
        """Validar que todos los eventos automáticos se generen"""
        logger.info(f"⏳ Esperando {tiempo_espera}s para que se procesen todos los eventos automáticos...")
        
        eventos_esperados = {
            "marketing.eventos": ["CampanaCreada"],
            "conversiones.eventos": ["ConversionDetectada"],
            "comisiones.eventos": ["ComisionCalculada"],
            "afiliados.eventos": ["AfiliadoRegistrado"]
        }
        
        # Esperar tiempo para procesamiento
        await asyncio.sleep(tiempo_espera)
        
        # Verificar eventos detectados
        logger.info("📊 RESUMEN DE EVENTOS DETECTADOS:")
        resumen = self.monitor.obtener_resumen_eventos()
        
        todos_ok = True
        for topico, eventos_esperados_lista in eventos_esperados.items():
            cantidad = resumen.get(topico, 0)
            if cantidad > 0:
                logger.info(f"   ✅ {topico}: {cantidad} eventos detectados")
            else:
                logger.warning(f"   ⚠️ {topico}: No se detectaron eventos")
                todos_ok = False
                
        return todos_ok
    
    async def verificar_datos_generados(self):
        """Verificar que se generaron datos en todos los servicios"""
        logger.info("🔍 Verificando datos generados en servicios...")
        
        verificaciones = []
        
        # Verificar conversiones
        try:
            async with self.session.get(f"{CONVERSIONES_URL}/api/v1/conversiones") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"   ✅ Conversiones: {len(data)} registros encontrados")
                    verificaciones.append(True)
                else:
                    logger.warning(f"   ⚠️ Error consultando conversiones: {response.status}")
                    verificaciones.append(False)
        except Exception as e:
            logger.error(f"   ❌ Error verificando conversiones: {e}")
            verificaciones.append(False)
            
        # Verificar afiliados
        try:
            async with self.session.get(f"{AFILIADOS_URL}/api/v1/afiliados") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"   ✅ Afiliados: {len(data)} registros encontrados")
                    verificaciones.append(True)
                else:
                    logger.warning(f"   ⚠️ Error consultando afiliados: {response.status}")
                    verificaciones.append(False)
        except Exception as e:
            logger.error(f"   ❌ Error verificando afiliados: {e}")
            verificaciones.append(False)
            
        return all(verificaciones)
    
    async def ejecutar_prueba_completa(self):
        """Ejecutar la prueba completa del flujo de eventos"""
        logger.info("🎯 INICIANDO PRUEBA COMPLETA DEL FLUJO DE EVENTOS")
        logger.info("=" * 60)
        
        # Crear sesión HTTP
        self.session = aiohttp.ClientSession()
        
        try:
            # 1. Iniciar monitores de eventos
            logger.info("1️⃣ Iniciando monitores de eventos...")
            self.monitor.iniciar_todos_los_monitores()
            await asyncio.sleep(3)  # Dar tiempo a los monitores
            
            # 2. Verificar servicios
            logger.info("\n2️⃣ Verificando servicios...")
            if not await self.verificar_servicios():
                logger.error("❌ Algunos servicios no están disponibles")
                return False
                
            # 3. Crear campaña
            logger.info("\n3️⃣ Creando campaña de prueba...")
            if not await self.crear_campana_prueba():
                logger.error("❌ Error creando campaña")
                return False
                
            # 4. Validar eventos automáticos
            logger.info("\n4️⃣ Validando eventos automáticos...")
            eventos_ok = await self.validar_eventos_automaticos()
            
            # 5. Verificar datos generados
            logger.info("\n5️⃣ Verificando datos generados...")
            datos_ok = await self.verificar_datos_generados()
            
            # Resumen final
            logger.info("\n" + "=" * 60)
            logger.info("📋 RESUMEN DE LA PRUEBA:")
            logger.info(f"   🎯 Campaña creada: {'✅' if self.campana_id else '❌'}")
            logger.info(f"   📨 Eventos detectados: {'✅' if eventos_ok else '⚠️'}")
            logger.info(f"   💾 Datos generados: {'✅' if datos_ok else '⚠️'}")
            
            exito_total = self.campana_id and eventos_ok and datos_ok
            
            if exito_total:
                logger.info("🎉 ¡PRUEBA COMPLETADA EXITOSAMENTE!")
                logger.info("   Todos los microservicios están funcionando correctamente")
                logger.info("   El flujo de eventos automático está operativo")
            else:
                logger.warning("⚠️ PRUEBA COMPLETADA CON ADVERTENCIAS")
                logger.info("   Revisar logs anteriores para identificar problemas")
                
            return exito_total
            
        finally:
            await self.session.close()


async def main():
    """Función principal"""
    print("🚀 SCRIPT DE PRUEBA - FLUJO COMPLETO DE EVENTOS")
    print("=" * 60)
    print("Este script probará el flujo automático completo:")
    print("  📱 Crear campaña → 📊 Conversión → 💰 Comisión → 👤 Afiliado")
    print("=" * 60)
    
    probador = ProbadorFlujoEventos()
    resultado = await probador.ejecutar_prueba_completa()
    
    if resultado:
        print("\n🎉 ¡ÉXITO! El sistema de eventos funciona correctamente")
        return 0
    else:
        print("\n⚠️ ADVERTENCIA: Revisar problemas detectados")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Prueba interrumpida por el usuario")
        exit(130)
    except Exception as e:
        print(f"\n❌ Error ejecutando prueba: {e}")
        exit(1)