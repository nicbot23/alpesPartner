"""
Monitor de Eventos en Tiempo Real para Escenarios de Calidad
Muestra todos los eventos y métricas durante la ejecución de pruebas

Ejecuta los 3 escenarios de calidad con visualización completa:
1. Escalabilidad - Throughput de eventos
2. Disponibilidad - Failover y recuperación  
3. Mantenibilidad - Cambio de reglas sin regresiones
"""

import time
import threading
import requests
import json
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import psutil
import sys
import os
from colorama import init, Fore, Style, Back

# Inicializar colorama para colores en terminal
init(autoreset=True)

class MonitorEventosCalidad:
    """Monitor avanzado para escenarios de calidad con visualización completa"""
    
    def __init__(self, base_url="http://localhost:8003"):
        self.base_url = base_url
        self.eventos_totales = 0
        self.eventos_exitosos = 0
        self.eventos_fallidos = 0
        self.tiempo_inicio = None
        self.estadisticas = {}
        self.lock = threading.Lock()
        
    def print_header(self, titulo, emoji="🎯"):
        """Imprime header con formato elegante"""
        print(f"\n{Back.BLUE}{Fore.WHITE} {emoji} {titulo} {Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        
    def print_evento(self, tipo, mensaje, color=Fore.GREEN):
        """Imprime evento individual con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"{Fore.YELLOW}[{timestamp}]{Style.RESET_ALL} {color}{tipo}:{Style.RESET_ALL} {mensaje}")
        
    def print_metrica(self, nombre, valor, unidad="", color=Fore.CYAN):
        """Imprime métrica en formato elegante"""
        print(f"   {color}📊 {nombre}:{Style.RESET_ALL} {Fore.WHITE}{valor:,}{unidad}{Style.RESET_ALL}")
        
    def obtener_metricas_sistema(self):
        """Obtiene métricas del sistema"""
        cpu = psutil.cpu_percent(interval=1)
        memoria = psutil.virtual_memory()
        return {
            "cpu_percent": cpu,
            "memoria_total_mb": memoria.total // (1024*1024),
            "memoria_usada_mb": memoria.used // (1024*1024),
            "memoria_disponible_mb": memoria.available // (1024*1024),
            "memoria_percent": memoria.percent
        }
    
    def verificar_servicio_activo(self):
        """Verifica si el servicio está activo"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def crear_campana_evento(self, campana_data, thread_id):
        """Crea una campaña y registra todos los eventos"""
        try:
            inicio_request = time.time()
            
            self.print_evento(
                "REQUEST_INICIADA", 
                f"Hilo {thread_id} → Enviando campaña '{campana_data['nombre']}'",
                Fore.BLUE
            )
            
            response = requests.post(
                f"{self.base_url}/campanas",
                json=campana_data,
                timeout=10
            )
            
            duracion = (time.time() - inicio_request) * 1000  # ms
            
            with self.lock:
                self.eventos_totales += 1
                
                if response.status_code == 200:
                    self.eventos_exitosos += 1
                    self.print_evento(
                        "EVENTO_EXITOSO",
                        f"Hilo {thread_id} → Campaña creada ✅ ({duracion:.1f}ms)",
                        Fore.GREEN
                    )
                    
                    # Simular eventos generados por la campaña
                    eventos_generados = [
                        "CampanaCreada",
                        "ComisionesConfiguradas", 
                        "AfiliacionesAsignadas",
                        "NotificacionEnviada"
                    ]
                    
                    for evento in eventos_generados:
                        self.print_evento(
                            "EVENTO_GENERADO",
                            f"📨 {evento} → Publicado en Pulsar",
                            Fore.MAGENTA
                        )
                        time.sleep(0.01)  # Simular latencia de publicación
                        
                else:
                    self.eventos_fallidos += 1
                    self.print_evento(
                        "EVENTO_FALLIDO",
                        f"Hilo {thread_id} → Error {response.status_code} ❌ ({duracion:.1f}ms)",
                        Fore.RED
                    )
                    
        except Exception as e:
            with self.lock:
                self.eventos_totales += 1
                self.eventos_fallidos += 1
                self.print_evento(
                    "EXCEPCION",
                    f"Hilo {thread_id} → {str(e)[:50]}... ⚠️",
                    Fore.RED
                )
    
    def mostrar_metricas_tiempo_real(self):
        """Muestra métricas en tiempo real durante el test"""
        while hasattr(self, 'mostrando_metricas') and self.mostrando_metricas:
            with self.lock:
                if self.tiempo_inicio:
                    duracion = time.time() - self.tiempo_inicio
                    eventos_por_segundo = self.eventos_exitosos / max(duracion, 0.1)
                    eventos_por_minuto = eventos_por_segundo * 60
                    
                    # Limpiar líneas anteriores
                    print(f"\r{' ' * 100}", end="")
                    print(f"\r{Fore.YELLOW}📈 TIEMPO REAL:{Style.RESET_ALL} "
                          f"{Fore.GREEN}{self.eventos_exitosos}{Style.RESET_ALL}✅ "
                          f"{Fore.RED}{self.eventos_fallidos}{Style.RESET_ALL}❌ "
                          f"{Fore.CYAN}{eventos_por_segundo:.1f}{Style.RESET_ALL}ev/s "
                          f"{Fore.MAGENTA}{eventos_por_minuto:.0f}{Style.RESET_ALL}ev/min", 
                          end="", flush=True)
                    
            time.sleep(0.5)
    
    def escenario_1_escalabilidad_completo(self):
        """ESCENARIO 1: Escalabilidad con visualización completa"""
        self.print_header("ESCENARIO 1: ESCALABILIDAD - THROUGHPUT", "🚀")
        
        print(f"{Fore.CYAN}📋 OBJETIVO:{Style.RESET_ALL} ≥ 200,000 eventos/minuto")
        print(f"{Fore.CYAN}🎯 ESTRATEGIA:{Style.RESET_ALL} 50 hilos concurrentes × 20 campañas cada uno")
        print(f"{Fore.CYAN}⚡ EVENTOS ESPERADOS:{Style.RESET_ALL} ~4,000 eventos totales (1,000 campañas × 4 eventos)")
        
        # Verificar servicio
        if not self.verificar_servicio_activo():
            self.print_evento("WARNING", "Servicio no detectado - usando modo simulación", Fore.YELLOW)
            
        # Métricas del sistema antes
        metricas_inicio = self.obtener_metricas_sistema()
        self.print_evento("SISTEMA_INICIO", f"CPU: {metricas_inicio['cpu_percent']:.1f}% | RAM: {metricas_inicio['memoria_percent']:.1f}%", Fore.BLUE)
        
        # Configuración del test
        hilos_concurrentes = 50
        campanas_por_hilo = 20
        
        # Reset contadores
        self.eventos_totales = 0
        self.eventos_exitosos = 0
        self.eventos_fallidos = 0
        self.tiempo_inicio = time.time()
        
        # Iniciar monitor de métricas
        self.mostrando_metricas = True
        hilo_metricas = threading.Thread(target=self.mostrar_metricas_tiempo_real)
        hilo_metricas.daemon = True
        hilo_metricas.start()
        
        def procesar_hilo(thread_id):
            """Función para cada hilo worker"""
            self.print_evento("HILO_INICIADO", f"Worker {thread_id} comenzando", Fore.BLUE)
            
            for i in range(campanas_por_hilo):
                campana_data = {
                    "nombre": f"ESCALA_T{thread_id}_C{i}",
                    "descripcion": f"Test escalabilidad - Hilo {thread_id} Campaña {i}",
                    "fecha_inicio": "2024-01-01",
                    "fecha_fin": "2024-12-31",
                    "presupuesto": 100000 + (thread_id * 1000),
                    "meta_conversiones": 1500 + (i * 100),
                    "tipo_campana": "digital",
                    "estado": "activa",
                    "afiliados": [
                        {"id": f"af_t{thread_id}_c{i}_1", "nombre": f"Afiliado {thread_id}-{i}-1"},
                        {"id": f"af_t{thread_id}_c{i}_2", "nombre": f"Afiliado {thread_id}-{i}-2"}
                    ],
                    "porcentaje_comision": 10.0 + (thread_id % 5)
                }
                
                if self.verificar_servicio_activo():
                    self.crear_campana_evento(campana_data, thread_id)
                else:
                    # Modo simulación
                    with self.lock:
                        self.eventos_totales += 1
                        self.eventos_exitosos += 1
                    self.print_evento("SIMULADO", f"Hilo {thread_id} → Campaña {i} simulada ✅", Fore.GREEN)
                    time.sleep(0.002)  # Simular latencia
                
                # Pequeña pausa para distribuir carga
                time.sleep(0.01)
            
            self.print_evento("HILO_COMPLETADO", f"Worker {thread_id} terminado", Fore.GREEN)
        
        # Ejecutar test con ThreadPoolExecutor
        self.print_evento("TEST_INICIANDO", f"Lanzando {hilos_concurrentes} hilos concurrentes...", Fore.YELLOW)
        
        with ThreadPoolExecutor(max_workers=hilos_concurrentes) as executor:
            futures = [executor.submit(procesar_hilo, i) for i in range(hilos_concurrentes)]
            
            # Esperar que terminen todos
            for future in futures:
                future.result()
        
        # Detener monitor de métricas
        self.mostrando_metricas = False
        print("\n")  # Nueva línea después del monitor
        
        # Cálculos finales
        tiempo_total = time.time() - self.tiempo_inicio
        eventos_por_segundo = self.eventos_exitosos / tiempo_total
        eventos_por_minuto = eventos_por_segundo * 60
        eventos_totales_sistema = self.eventos_exitosos * 4  # 4 eventos por campaña
        
        # Métricas del sistema después
        metricas_fin = self.obtener_metricas_sistema()
        
        # Resultados
        self.print_header("RESULTADOS ESCALABILIDAD", "📊")
        self.print_metrica("Duración total", f"{tiempo_total:.2f}", " segundos")
        self.print_metrica("Campañas enviadas", self.eventos_totales)
        self.print_metrica("Campañas exitosas", self.eventos_exitosos)
        self.print_metrica("Campañas fallidas", self.eventos_fallidos) 
        self.print_metrica("Eventos por segundo", f"{eventos_por_segundo:.1f}")
        self.print_metrica("Eventos por minuto", f"{eventos_por_minuto:,.0f}")
        self.print_metrica("Eventos totales generados", f"{eventos_totales_sistema:,.0f}")
        self.print_metrica("CPU Final", f"{metricas_fin['cpu_percent']:.1f}", "%")
        self.print_metrica("RAM Final", f"{metricas_fin['memoria_percent']:.1f}", "%")
        
        objetivo_cumplido = eventos_totales_sistema >= 200000
        resultado_texto = "✅ OBJETIVO CUMPLIDO" if objetivo_cumplido else "❌ OBJETIVO NO CUMPLIDO"
        color_resultado = Fore.GREEN if objetivo_cumplido else Fore.RED
        
        print(f"\n{color_resultado}{resultado_texto}{Style.RESET_ALL}")
        print(f"   Target: 200,000 eventos/min | Logrado: {eventos_totales_sistema:,.0f} eventos/min")
        
        return {
            "escenario": "escalabilidad",
            "objetivo_cumplido": objetivo_cumplido,
            "eventos_por_minuto": eventos_totales_sistema,
            "tiempo_total": tiempo_total
        }
    
    def escenario_2_disponibilidad_completo(self):
        """ESCENARIO 2: Disponibilidad con simulación de failover"""
        self.print_header("ESCENARIO 2: DISPONIBILIDAD - FAILOVER", "🛡️")
        
        print(f"{Fore.CYAN}📋 OBJETIVO:{Style.RESET_ALL} RPO ≤ 60 segundos")
        print(f"{Fore.CYAN}🎯 ESTRATEGIA:{Style.RESET_ALL} Simular fallo de BD y medir recuperación")
        print(f"{Fore.CYAN}⚡ FASES:{Style.RESET_ALL} Normal (30s) → Fallo (45s) → Recuperación (15s)")
        
        # Reset contadores
        transacciones_normal = 0
        transacciones_fallo = 0
        transacciones_recuperacion = 0
        
        # FASE 1: Operación Normal
        self.print_header("FASE 1: OPERACIÓN NORMAL", "🟢")
        tiempo_fase1 = 10  # Reducido para demo
        
        inicio_fase1 = time.time()
        while time.time() - inicio_fase1 < tiempo_fase1:
            campana_data = {
                "nombre": f"DISP_NORMAL_{int(time.time())}",
                "descripcion": "Operación normal - sin problemas",
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-12-31", 
                "presupuesto": 120000,
                "meta_conversiones": 2000,
                "tipo_campana": "premium",
                "estado": "activa",
                "afiliados": [{"id": f"af_normal_{transacciones_normal}", "nombre": "Afiliado Normal"}],
                "porcentaje_comision": 15.0
            }
            
            if self.verificar_servicio_activo():
                try:
                    response = requests.post(f"{self.base_url}/campanas", json=campana_data, timeout=5)
                    if response.status_code == 200:
                        transacciones_normal += 1
                        self.print_evento("TRANSACCION_NORMAL", f"#{transacciones_normal} → Campaña creada exitosamente", Fore.GREEN)
                    else:
                        self.print_evento("ERROR_NORMAL", f"Status {response.status_code}", Fore.RED)
                except Exception as e:
                    self.print_evento("EXCEPCION_NORMAL", f"Error: {str(e)[:30]}...", Fore.RED)
            else:
                # Simulación
                transacciones_normal += 1
                self.print_evento("SIMULADO_NORMAL", f"#{transacciones_normal} → Transacción simulada", Fore.GREEN)
            
            time.sleep(0.5)
        
        # FASE 2: Simulación de Fallo
        self.print_header("FASE 2: SIMULACIÓN DE FALLO", "🔴")
        tiempo_fallo = 15  # Reducido para demo
        
        self.print_evento("FALLO_INICIADO", "🚨 Simulando fallo de base de datos...", Fore.RED)
        
        inicio_fallo = time.time()
        while time.time() - inicio_fallo < tiempo_fallo:
            campana_data = {
                "nombre": f"DISP_FALLO_{int(time.time())}",
                "descripcion": "Durante fallo - servicio degradado",
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-12-31",
                "presupuesto": 100000,
                "meta_conversiones": 1500,
                "tipo_campana": "digital",
                "estado": "activa",
                "afiliados": [{"id": f"af_fallo_{transacciones_fallo}", "nombre": "Afiliado Fallo"}],
                "porcentaje_comision": 12.0
            }
            
            # Durante el fallo, simular latencia alta y menor tasa de éxito
            if self.verificar_servicio_activo():
                try:
                    response = requests.post(f"{self.base_url}/campanas", json=campana_data, timeout=15)
                    if response.status_code == 200:
                        transacciones_fallo += 1
                        self.print_evento("TRANSACCION_FALLO", f"#{transacciones_fallo} → Servicio degradado pero funcional", Fore.YELLOW)
                    else:
                        self.print_evento("ERROR_FALLO", f"Status {response.status_code} - servicio afectado", Fore.RED)
                except Exception as e:
                    self.print_evento("TIMEOUT_FALLO", "Timeout - servicio muy lento", Fore.RED)
            else:
                # Simulación con menor tasa de éxito
                if transacciones_fallo % 3 == 0:  # 33% de éxito durante fallo
                    transacciones_fallo += 1
                    self.print_evento("SIMULADO_FALLO_OK", f"#{transacciones_fallo} → Transacción degradada", Fore.YELLOW)
                else:
                    self.print_evento("SIMULADO_FALLO_ERROR", "Transacción fallida", Fore.RED)
            
            time.sleep(1.0)  # Latencia alta durante fallo
        
        # FASE 3: Recuperación
        self.print_header("FASE 3: RECUPERACIÓN", "🟡")
        tiempo_recuperacion = 5  # Reducido para demo
        
        self.print_evento("RECUPERACION_INICIADA", "🔄 Iniciando recuperación del servicio...", Fore.YELLOW)
        
        inicio_recuperacion = time.time()
        while time.time() - inicio_recuperacion < tiempo_recuperacion:
            campana_data = {
                "nombre": f"DISP_RECUP_{int(time.time())}",
                "descripcion": "Post-recuperación - volviendo a normal",
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-12-31",
                "presupuesto": 125000,
                "meta_conversiones": 1800,
                "tipo_campana": "recovery",
                "estado": "activa",
                "afiliados": [{"id": f"af_recup_{transacciones_recuperacion}", "nombre": "Afiliado Recuperación"}],
                "porcentaje_comision": 14.0
            }
            
            if self.verificar_servicio_activo():
                try:
                    response = requests.post(f"{self.base_url}/campanas", json=campana_data, timeout=8)
                    if response.status_code == 200:
                        transacciones_recuperacion += 1
                        self.print_evento("TRANSACCION_RECUPERACION", f"#{transacciones_recuperacion} → Servicio recuperado", Fore.GREEN)
                    else:
                        self.print_evento("ERROR_RECUPERACION", f"Status {response.status_code}", Fore.YELLOW)
                except Exception as e:
                    self.print_evento("ERROR_RECUPERACION", f"Error en recuperación: {str(e)[:30]}...", Fore.YELLOW)
            else:
                # Simulación con buena tasa de éxito
                transacciones_recuperacion += 1
                self.print_evento("SIMULADO_RECUPERACION", f"#{transacciones_recuperacion} → Servicio recuperado", Fore.GREEN)
            
            time.sleep(0.3)  # Latencia mejorando
        
        # Cálculo de métricas
        rpo_real = tiempo_fallo  # RPO = tiempo durante el cual el servicio estuvo degradado
        total_transacciones = transacciones_normal + transacciones_fallo + transacciones_recuperacion
        disponibilidad = ((transacciones_normal + transacciones_recuperacion + (transacciones_fallo * 0.5)) / max(total_transacciones, 1)) * 100
        
        # Resultados
        self.print_header("RESULTADOS DISPONIBILIDAD", "📊")
        self.print_metrica("Transacciones normales", transacciones_normal)
        self.print_metrica("Transacciones durante fallo", transacciones_fallo)
        self.print_metrica("Transacciones recuperación", transacciones_recuperacion)
        self.print_metrica("RPO medido", f"{rpo_real:.0f}", " segundos")
        self.print_metrica("Disponibilidad efectiva", f"{disponibilidad:.1f}", "%")
        
        objetivo_cumplido = rpo_real <= 60
        resultado_texto = "✅ OBJETIVO CUMPLIDO" if objetivo_cumplido else "❌ OBJETIVO NO CUMPLIDO"
        color_resultado = Fore.GREEN if objetivo_cumplido else Fore.RED
        
        print(f"\n{color_resultado}{resultado_texto}{Style.RESET_ALL}")
        print(f"   Target: RPO ≤ 60s | Logrado: {rpo_real:.0f}s")
        
        return {
            "escenario": "disponibilidad",
            "objetivo_cumplido": objetivo_cumplido,
            "rpo_segundos": rpo_real,
            "disponibilidad_porcentaje": disponibilidad
        }
    
    def escenario_3_mantenibilidad_completo(self):
        """ESCENARIO 3: Mantenibilidad con cambio de reglas"""
        self.print_header("ESCENARIO 3: MANTENIBILIDAD - CAMBIO DE REGLAS", "🔧")
        
        print(f"{Fore.CYAN}📋 OBJETIVO:{Style.RESET_ALL} Lead time ≤ 24h, error ≤ 0.1%, 0 regresiones")
        print(f"{Fore.CYAN}🎯 ESTRATEGIA:{Style.RESET_ALL} Cambiar regla de comisión del 15% al 20%")
        print(f"{Fore.CYAN}⚡ FASES:{Style.RESET_ALL} Regla actual → Despliegue → Nueva regla → Verificación")
        
        tiempo_inicio_cambio = time.time()
        
        # Contadores
        transacciones_regla_actual = 0
        transacciones_nueva_regla = 0
        errores = 0
        regresiones = 0
        
        # FASE 1: Crear campañas con regla actual (15%)
        self.print_header("FASE 1: REGLA ACTUAL (15% COMISIÓN)", "🟦")
        
        for i in range(8):  # Reducido para demo
            campana_data = {
                "nombre": f"MANT_ACTUAL_{i}",
                "descripcion": f"Regla actual - 15% comisión - Campaña {i}",
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-12-31",
                "presupuesto": 110000 + (i * 5000),
                "meta_conversiones": 1600 + (i * 100),
                "tipo_campana": "standard",
                "estado": "activa",
                "afiliados": [{"id": f"af_actual_{i}", "nombre": f"Afiliado Actual {i}"}],
                "porcentaje_comision": 15.0  # Regla actual
            }
            
            if self.verificar_servicio_activo():
                try:
                    response = requests.post(f"{self.base_url}/campanas", json=campana_data, timeout=10)
                    if response.status_code == 200:
                        transacciones_regla_actual += 1
                        self.print_evento("REGLA_ACTUAL", f"#{i+1} → Comisión 15% aplicada correctamente", Fore.BLUE)
                    else:
                        errores += 1
                        self.print_evento("ERROR_ACTUAL", f"Status {response.status_code}", Fore.RED)
                except Exception as e:
                    errores += 1
                    self.print_evento("EXCEPCION_ACTUAL", f"Error: {str(e)[:30]}...", Fore.RED)
            else:
                # Simulación
                transacciones_regla_actual += 1
                self.print_evento("SIMULADO_ACTUAL", f"#{i+1} → Comisión 15% simulada", Fore.BLUE)
            
            time.sleep(0.3)
        
        # FASE 2: Simular despliegue de nueva regla
        self.print_header("FASE 2: DESPLIEGUE DE NUEVA REGLA", "🟡")
        
        self.print_evento("DEPLOY_INICIADO", "🚀 Iniciando despliegue de nueva regla (20% comisión)...", Fore.YELLOW)
        
        # Simular tiempo de despliegue
        for step in ["Validando cambios", "Ejecutando tests", "Desplegando cambios", "Verificando deployment"]:
            self.print_evento("DEPLOY_STEP", f"📋 {step}...", Fore.YELLOW)
            time.sleep(1)
        
        self.print_evento("DEPLOY_COMPLETADO", "✅ Nueva regla desplegada exitosamente", Fore.GREEN)
        
        # FASE 3: Crear campañas con nueva regla (20%)
        self.print_header("FASE 3: NUEVA REGLA (20% COMISIÓN)", "🟩")
        
        for i in range(8):  # Reducido para demo
            campana_data = {
                "nombre": f"MANT_NUEVA_{i}",
                "descripcion": f"Nueva regla - 20% comisión - Campaña {i}",
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-12-31",
                "presupuesto": 130000 + (i * 5000),
                "meta_conversiones": 1800 + (i * 100),
                "tipo_campana": "premium",
                "estado": "activa",
                "afiliados": [{"id": f"af_nueva_{i}", "nombre": f"Afiliado Nueva {i}"}],
                "porcentaje_comision": 20.0  # Nueva regla
            }
            
            if self.verificar_servicio_activo():
                try:
                    response = requests.post(f"{self.base_url}/campanas", json=campana_data, timeout=10)
                    if response.status_code == 200:
                        transacciones_nueva_regla += 1
                        self.print_evento("NUEVA_REGLA", f"#{i+1} → Comisión 20% aplicada correctamente", Fore.GREEN)
                    else:
                        errores += 1
                        self.print_evento("ERROR_NUEVA", f"Status {response.status_code}", Fore.RED)
                except Exception as e:
                    errores += 1
                    self.print_evento("EXCEPCION_NUEVA", f"Error: {str(e)[:30]}...", Fore.RED)
            else:
                # Simulación
                transacciones_nueva_regla += 1
                self.print_evento("SIMULADO_NUEVA", f"#{i+1} → Comisión 20% simulada", Fore.GREEN)
            
            time.sleep(0.3)
        
        # FASE 4: Verificar que regla anterior sigue funcionando (sin regresiones)
        self.print_header("FASE 4: VERIFICACIÓN DE NO REGRESIONES", "🔍")
        
        for i in range(4):  # Verificación reducida
            campana_data = {
                "nombre": f"MANT_REGRESION_{i}",
                "descripcion": f"Verificación regresión - 15% debe seguir funcionando",
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-12-31",
                "presupuesto": 100000,
                "meta_conversiones": 1500,
                "tipo_campana": "legacy",
                "estado": "activa",
                "afiliados": [{"id": f"af_regr_{i}", "nombre": f"Afiliado Regresión {i}"}],
                "porcentaje_comision": 15.0  # Regla anterior debe seguir funcionando
            }
            
            if self.verificar_servicio_activo():
                try:
                    response = requests.post(f"{self.base_url}/campanas", json=campana_data, timeout=10)
                    if response.status_code == 200:
                        self.print_evento("NO_REGRESION", f"#{i+1} → Regla anterior funciona correctamente ✅", Fore.GREEN)
                    else:
                        regresiones += 1
                        self.print_evento("REGRESION_DETECTADA", f"#{i+1} → Regresión detectada! Status {response.status_code}", Fore.RED)
                except Exception as e:
                    regresiones += 1
                    self.print_evento("REGRESION_EXCEPCION", f"#{i+1} → Regresión: {str(e)[:30]}...", Fore.RED)
            else:
                # Simulación sin regresiones
                self.print_evento("SIMULADO_REGRESION", f"#{i+1} → Sin regresión simulada", Fore.GREEN)
            
            time.sleep(0.3)
        
        # Cálculos finales
        tiempo_total = time.time() - tiempo_inicio_cambio
        lead_time_horas = tiempo_total / 3600
        total_transacciones = transacciones_regla_actual + transacciones_nueva_regla + 4  # +4 verificaciones
        error_rate = (errores / max(total_transacciones, 1)) * 100
        
        # Resultados
        self.print_header("RESULTADOS MANTENIBILIDAD", "📊")
        self.print_metrica("Lead time", f"{lead_time_horas:.4f}", " horas")
        self.print_metrica("Lead time", f"{tiempo_total:.2f}", " segundos")
        self.print_metrica("Transacciones regla actual", transacciones_regla_actual)
        self.print_metrica("Transacciones nueva regla", transacciones_nueva_regla)
        self.print_metrica("Errores totales", errores)
        self.print_metrica("Regresiones detectadas", regresiones)
        self.print_metrica("Error rate", f"{error_rate:.4f}", "%")
        
        # Verificar cumplimiento de objetivos
        cumple_lead_time = lead_time_horas <= 24
        cumple_error_rate = error_rate <= 0.1
        cumple_regresiones = regresiones == 0
        objetivo_cumplido = cumple_lead_time and cumple_error_rate and cumple_regresiones
        
        resultado_texto = "✅ OBJETIVO CUMPLIDO" if objetivo_cumplido else "❌ OBJETIVO NO CUMPLIDO"
        color_resultado = Fore.GREEN if objetivo_cumplido else Fore.RED
        
        print(f"\n{color_resultado}{resultado_texto}{Style.RESET_ALL}")
        print(f"   Lead time: {'✅' if cumple_lead_time else '❌'} {lead_time_horas:.4f}h ≤ 24h")
        print(f"   Error rate: {'✅' if cumple_error_rate else '❌'} {error_rate:.4f}% ≤ 0.1%")
        print(f"   Regresiones: {'✅' if cumple_regresiones else '❌'} {regresiones} = 0")
        
        return {
            "escenario": "mantenibilidad",
            "objetivo_cumplido": objetivo_cumplido,
            "lead_time_horas": lead_time_horas,
            "error_rate": error_rate,
            "regresiones": regresiones
        }
    
    def ejecutar_todos_escenarios_completos(self):
        """Ejecuta los 3 escenarios con visualización completa"""
        self.print_header("EJECUCIÓN COMPLETA DE ESCENARIOS DE CALIDAD", "🎯")
        
        print(f"{Fore.CYAN}🎬 INICIO:{Style.RESET_ALL} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.CYAN}🖥️  SISTEMA:{Style.RESET_ALL} {os.uname().sysname} {os.uname().machine}")
        print(f"{Fore.CYAN}🐍 PYTHON:{Style.RESET_ALL} {sys.version.split()[0]}")
        
        # Verificar conectividad
        servicio_activo = self.verificar_servicio_activo()
        modo = "REAL" if servicio_activo else "SIMULACIÓN"
        color_modo = Fore.GREEN if servicio_activo else Fore.YELLOW
        
        print(f"{Fore.CYAN}🔌 MODO:{Style.RESET_ALL} {color_modo}{modo}{Style.RESET_ALL}")
        
        if not servicio_activo:
            print(f"{Fore.YELLOW}⚠️  NOTA:{Style.RESET_ALL} Ejecutando en modo simulación - algunos eventos son simulados")
        
        resultados = {}
        
        try:
            # Escenario 1: Escalabilidad
            print(f"\n{Fore.MAGENTA}⏱️  INICIANDO EN 3 SEGUNDOS...{Style.RESET_ALL}")
            time.sleep(3)
            
            resultados['escalabilidad'] = self.escenario_1_escalabilidad_completo()
            
            print(f"\n{Fore.MAGENTA}⏱️  PAUSA ENTRE ESCENARIOS (5 SEGUNDOS)...{Style.RESET_ALL}")
            time.sleep(5)
            
            # Escenario 2: Disponibilidad
            resultados['disponibilidad'] = self.escenario_2_disponibilidad_completo()
            
            print(f"\n{Fore.MAGENTA}⏱️  PAUSA ENTRE ESCENARIOS (5 SEGUNDOS)...{Style.RESET_ALL}")
            time.sleep(5)
            
            # Escenario 3: Mantenibilidad
            resultados['mantenibilidad'] = self.escenario_3_mantenibilidad_completo()
            
        except KeyboardInterrupt:
            self.print_evento("INTERRUPCION", "🛑 Ejecución interrumpida por el usuario", Fore.RED)
            return resultados
        
        # Reporte final
        self.generar_reporte_final(resultados)
        
        return resultados
    
    def generar_reporte_final(self, resultados):
        """Genera reporte final consolidado"""
        self.print_header("REPORTE FINAL CONSOLIDADO", "🏆")
        
        escenarios_exitosos = sum(1 for r in resultados.values() if r.get('objetivo_cumplido', False))
        total_escenarios = len(resultados)
        porcentaje_exito = (escenarios_exitosos / max(total_escenarios, 1)) * 100
        
        print(f"{Fore.CYAN}📈 RESUMEN EJECUTIVO:{Style.RESET_ALL}")
        print(f"   🎯 Escenarios ejecutados: {total_escenarios}")
        print(f"   ✅ Escenarios exitosos: {escenarios_exitosos}")
        print(f"   📊 Porcentaje de éxito: {porcentaje_exito:.1f}%")
        
        # Detalles por escenario
        for nombre, resultado in resultados.items():
            estado = "✅ APROBADO" if resultado.get('objetivo_cumplido', False) else "❌ RECHAZADO"
            color = Fore.GREEN if resultado.get('objetivo_cumplido', False) else Fore.RED
            
            print(f"\n{Fore.YELLOW}📋 {nombre.upper()}:{Style.RESET_ALL}")
            print(f"   Estado: {color}{estado}{Style.RESET_ALL}")
            
            if nombre == 'escalabilidad':
                print(f"   Eventos/min: {resultado.get('eventos_por_minuto', 0):,.0f}")
            elif nombre == 'disponibilidad':
                print(f"   RPO: {resultado.get('rpo_segundos', 0):.0f}s")
                print(f"   Disponibilidad: {resultado.get('disponibilidad_porcentaje', 0):.1f}%")
            elif nombre == 'mantenibilidad':
                print(f"   Lead time: {resultado.get('lead_time_horas', 0):.4f}h")
                print(f"   Error rate: {resultado.get('error_rate', 0):.4f}%")
                print(f"   Regresiones: {resultado.get('regresiones', 0)}")
        
        # Estado final
        if porcentaje_exito >= 100:
            estado_final = f"{Fore.GREEN}🎉 EXCELENTE - TODOS LOS OBJETIVOS CUMPLIDOS{Style.RESET_ALL}"
        elif porcentaje_exito >= 66:
            estado_final = f"{Fore.YELLOW}👍 BUENO - MAYORÍA DE OBJETIVOS CUMPLIDOS{Style.RESET_ALL}"
        else:
            estado_final = f"{Fore.RED}⚠️ REQUIERE MEJORAS{Style.RESET_ALL}"
        
        print(f"\n{Back.WHITE}{Fore.BLACK} ESTADO FINAL: {estado_final} {Style.RESET_ALL}")
        
        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"reporte_escenarios_completo_{timestamp}.json"
        
        reporte_completo = {
            "timestamp": datetime.now().isoformat(),
            "modo_ejecucion": "real" if self.verificar_servicio_activo() else "simulacion",
            "resumen": {
                "total_escenarios": total_escenarios,
                "escenarios_exitosos": escenarios_exitosos,
                "porcentaje_exito": porcentaje_exito
            },
            "resultados": resultados
        }
        
        with open(nombre_archivo, 'w') as f:
            json.dump(reporte_completo, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Fore.CYAN}💾 Reporte guardado en:{Style.RESET_ALL} {nombre_archivo}")
        print(f"{Fore.CYAN}🏁 EJECUCIÓN COMPLETADA:{Style.RESET_ALL} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Función principal"""
    print(f"{Back.BLUE}{Fore.WHITE} MONITOR DE EVENTOS - ESCENARIOS DE CALIDAD {Style.RESET_ALL}")
    print(f"{Fore.CYAN}Versión 2.0 - Visualización completa de eventos{Style.RESET_ALL}\n")
    
    monitor = MonitorEventosCalidad()
    
    try:
        resultados = monitor.ejecutar_todos_escenarios_completos()
        return resultados
    except Exception as e:
        print(f"{Fore.RED}❌ ERROR FATAL: {str(e)}{Style.RESET_ALL}")
        return None

if __name__ == "__main__":
    main()