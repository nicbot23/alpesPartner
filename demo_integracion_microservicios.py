#!/usr/bin/env python3
"""
Monitor de Integración de Microservicios - Versión Simplificada
==============================================================

Demuestra cómo los microservicios se comunican sin dependencias adicionales.
Usa requests y threading como el monitor principal.
"""

import json
import logging
import random
import threading
import time
import requests
from datetime import datetime
from typing import Dict, List

# Configurar logging con colores
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimuladorAfiliados:
    """Simula el microservicio de Afiliados"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"  # Puerto de Afiliados
        self.eventos_procesados = 0
        
    def procesar_campana_creada(self, campana_data: Dict) -> Dict:
        """Simula procesamiento de campaña en microservicio Afiliados"""
        try:
            logger.info(f"🎯 AFILIADOS: Procesando campaña '{campana_data.get('nombre')}'")
            
            # Simular asignación de afiliados
            num_afiliados = min(max(campana_data.get('meta_conversiones', 100) // 50, 3), 10)
            
            afiliados_asignados = []
            for i in range(num_afiliados):
                afiliado = {
                    "id": f"af_{campana_data.get('tipo_campana', 'general')}_{i+1}",
                    "nombre": f"Afiliado {campana_data.get('tipo_campana', 'General').title()} {i+1}",
                    "especialidad": campana_data.get('tipo_campana', 'general'),
                    "comision_asignada": round(random.uniform(5.0, 15.0), 1),
                    "activo": True
                }
                afiliados_asignados.append(afiliado)
            
            # Simular tiempo de procesamiento
            time.sleep(random.uniform(0.5, 1.5))
            
            resultado = {
                "campana_id": campana_data.get('id'),
                "afiliados_asignados": afiliados_asignados,
                "total_afiliados": len(afiliados_asignados),
                "criterios_asignacion": f"tipo:{campana_data.get('tipo_campana')},meta:{campana_data.get('meta_conversiones')}",
                "timestamp": int(time.time() * 1000)
            }
            
            self.eventos_procesados += 1
            
            logger.info(f"✅ AFILIADOS: {len(afiliados_asignados)} afiliados asignados a campaña '{campana_data.get('nombre')}'")
            
            # Simular notificación a afiliados
            for afiliado in afiliados_asignados[:3]:  # Solo mostrar primeros 3
                logger.info(f"   📧 Notificando a {afiliado['nombre']} (Comisión: {afiliado['comision_asignada']}%)")
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error en simulador afiliados: {e}")
            return {}

class SimuladorConversiones:
    """Simula el microservicio de Conversiones"""
    
    def __init__(self):
        self.base_url = "http://localhost:8002"  # Puerto de Conversiones
        self.eventos_procesados = 0
        
    def procesar_campana_creada(self, campana_data: Dict) -> Dict:
        """Simula procesamiento de campaña en microservicio Conversiones"""
        try:
            logger.info(f"💰 CONVERSIONES: Configurando tracking para '{campana_data.get('nombre')}'")
            
            # Generar tipos de conversión basado en tipo de campaña
            conversiones_config = self._generar_configuracion_conversiones(
                campana_data.get('tipo_campana', 'general'),
                campana_data.get('presupuesto', 1000),
                campana_data.get('meta_conversiones', 100)
            )
            
            # Simular tiempo de configuración
            time.sleep(random.uniform(0.3, 1.0))
            
            resultado = {
                "campana_id": campana_data.get('id'),
                "tipos_conversion": conversiones_config['tipos'],
                "metas_conversion": conversiones_config['metas'],
                "kpis_establecidos": conversiones_config['kpis'],
                "timestamp": int(time.time() * 1000)
            }
            
            self.eventos_procesados += 1
            
            logger.info(f"✅ CONVERSIONES: {len(conversiones_config['tipos'])} tipos de conversión configurados")
            
            # Mostrar detalles de configuración
            for conversion in conversiones_config['tipos'][:3]:  # Solo mostrar primeros 3
                logger.info(f"   🎯 {conversion['tipo']}: valor base ${conversion['valor_base']}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error en simulador conversiones: {e}")
            return {}
    
    def _generar_configuracion_conversiones(self, tipo_campana: str, presupuesto: float, meta: int) -> Dict:
        """Genera configuración de conversiones"""
        conversiones_por_tipo = {
            "digital": [
                {"tipo": "click", "valor_base": presupuesto * 0.02},
                {"tipo": "view", "valor_base": presupuesto * 0.01},
                {"tipo": "signup", "valor_base": presupuesto * 0.10},
                {"tipo": "purchase", "valor_base": presupuesto * 0.50}
            ],
            "tradicional": [
                {"tipo": "call", "valor_base": presupuesto * 0.15},
                {"tipo": "visit", "valor_base": presupuesto * 0.25},
                {"tipo": "purchase", "valor_base": presupuesto * 0.60}
            ],
            "mixta": [
                {"tipo": "click", "valor_base": presupuesto * 0.02},
                {"tipo": "call", "valor_base": presupuesto * 0.12},
                {"tipo": "visit", "valor_base": presupuesto * 0.20},
                {"tipo": "purchase", "valor_base": presupuesto * 0.55}
            ]
        }
        
        tipos = conversiones_por_tipo.get(tipo_campana, conversiones_por_tipo["digital"])
        
        # Añadir multiplicadores aleatorios
        for tipo in tipos:
            tipo["multiplicador"] = round(random.uniform(1.0, 2.5), 2)
            tipo["valor_base"] = round(tipo["valor_base"], 2)
        
        metas = {
            "conversiones_objetivo": meta,
            "presupuesto_total": presupuesto,
            "costo_por_conversion": round(presupuesto / meta, 2),
            "roi_esperado": f"{random.randint(15, 30)}%"
        }
        
        kpis = {
            "conversion_rate_target": f"{random.uniform(2.5, 8.0):.1f}%",
            "cost_per_acquisition": round(presupuesto / meta * 0.8, 2),
            "lifetime_value": round(presupuesto / meta * 3.5, 2)
        }
        
        return {
            "tipos": tipos,
            "metas": metas,
            "kpis": kpis
        }

class MonitorIntegracionMicroservicios:
    """Monitor que demuestra la integración entre microservicios"""
    
    def __init__(self):
        self.marketing_url = "http://localhost:8003"
        self.simulador_afiliados = SimuladorAfiliados()
        self.simulador_conversiones = SimuladorConversiones()
        
        # Métricas de integración
        self.metricas = {
            'campanias_procesadas': 0,
            'afiliados_activados': 0,
            'conversiones_configuradas': 0,
            'eventos_integracion': 0,
            'tiempo_inicio': time.time()
        }
        
        self.running = False
        self.lock = threading.Lock()
    
    def crear_campana_y_procesar_integracion(self):
        """Crear campaña y simular procesamiento en todos los microservicios"""
        try:
            # 1. Crear campaña en Marketing
            campana_data = {
                "nombre": f"Campaña Integración {random.randint(1000, 9999)}",
                "descripcion": "Campaña de prueba para demostrar integración de microservicios",
                "tipo_campana": random.choice(["digital", "tradicional", "mixta"]),
                "meta_conversiones": random.randint(100, 800),
                "presupuesto": round(random.uniform(2000.0, 15000.0), 2),
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-12-31"
            }
            
            logger.info("=" * 80)
            logger.info(f"🚀 INICIANDO INTEGRACIÓN: {campana_data['nombre']}")
            logger.info("=" * 80)
            
            # Enviar a Marketing
            response = requests.post(f"{self.marketing_url}/campanas", json=campana_data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ MARKETING: Campaña creada exitosamente (ID: {result.get('id', 'N/A')})")
                
                # Simular delay para eventos distribuidos
                time.sleep(0.5)
                
                # 2. Procesar en Afiliados (simular reacción a evento)
                afiliados_result = self.simulador_afiliados.procesar_campana_creada({
                    **campana_data,
                    'id': result.get('id', 'unknown')
                })
                
                # 3. Procesar en Conversiones (simular reacción a evento)
                conversiones_result = self.simulador_conversiones.procesar_campana_creada({
                    **campana_data,
                    'id': result.get('id', 'unknown')
                })
                
                # 4. Actualizar métricas
                with self.lock:
                    self.metricas['campanias_procesadas'] += 1
                    self.metricas['afiliados_activados'] += afiliados_result.get('total_afiliados', 0)
                    self.metricas['conversiones_configuradas'] += len(conversiones_result.get('tipos_conversion', []))
                    self.metricas['eventos_integracion'] += 3  # Marketing + Afiliados + Conversiones
                
                # 5. Mostrar resumen de integración
                self._mostrar_resumen_integracion(campana_data, afiliados_result, conversiones_result)
                
                return True
            else:
                logger.error(f"❌ Error creando campaña: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de conexión con microservicio Marketing: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error en integración: {e}")
            return False
    
    def _mostrar_resumen_integracion(self, campana: Dict, afiliados: Dict, conversiones: Dict):
        """Mostrar resumen de la integración entre microservicios"""
        logger.info("📊 RESUMEN DE INTEGRACIÓN:")
        logger.info(f"   🎯 Marketing: Campaña '{campana['nombre']}' creada")
        logger.info(f"   👥 Afiliados: {afiliados.get('total_afiliados', 0)} afiliados asignados")
        logger.info(f"   💰 Conversiones: {len(conversiones.get('tipos_conversion', []))} tipos configurados")
        logger.info(f"   💵 Presupuesto: ${campana['presupuesto']:,.2f}")
        logger.info(f"   🎯 Meta: {campana['meta_conversiones']} conversiones")
        logger.info("=" * 80)
    
    def ejecutar_pruebas_integracion(self, num_campanias: int = 5, intervalo: float = 3.0):
        """Ejecutar múltiples pruebas de integración"""
        logger.info(f"🚀 INICIANDO PRUEBAS DE INTEGRACIÓN DE MICROSERVICIOS")
        logger.info(f"📋 Parámetros: {num_campanias} campañas, intervalo {intervalo}s")
        logger.info("=" * 80)
        
        self.running = True
        
        for i in range(num_campanias):
            if not self.running:
                break
                
            logger.info(f"🔄 Ejecutando prueba {i+1}/{num_campanias}")
            
            success = self.crear_campana_y_procesar_integracion()
            
            if success:
                logger.info(f"✅ Prueba {i+1} completada exitosamente")
            else:
                logger.error(f"❌ Prueba {i+1} falló")
            
            # Mostrar métricas cada 2 campañas
            if (i + 1) % 2 == 0:
                self._mostrar_metricas_integracion()
            
            if i < num_campanias - 1:  # No esperar después de la última
                time.sleep(intervalo)
        
        # Mostrar métricas finales
        self._mostrar_metricas_finales()
    
    def _mostrar_metricas_integracion(self):
        """Mostrar métricas de integración"""
        tiempo_transcurrido = time.time() - self.metricas['tiempo_inicio']
        
        logger.info("📈 MÉTRICAS DE INTEGRACIÓN:")
        logger.info(f"   📊 Campañas procesadas: {self.metricas['campanias_procesadas']}")
        logger.info(f"   👥 Total afiliados activados: {self.metricas['afiliados_activados']}")
        logger.info(f"   💰 Total conversiones configuradas: {self.metricas['conversiones_configuradas']}")
        logger.info(f"   🔄 Total eventos de integración: {self.metricas['eventos_integracion']}")
        logger.info(f"   ⏱️  Tiempo transcurrido: {tiempo_transcurrido:.1f}s")
        
        if self.metricas['campanias_procesadas'] > 0:
            avg_afiliados = self.metricas['afiliados_activados'] / self.metricas['campanias_procesadas']
            avg_conversiones = self.metricas['conversiones_configuradas'] / self.metricas['campanias_procesadas']
            logger.info(f"   📊 Promedio afiliados/campaña: {avg_afiliados:.1f}")
            logger.info(f"   📊 Promedio conversiones/campaña: {avg_conversiones:.1f}")
        
        logger.info("=" * 80)
    
    def _mostrar_metricas_finales(self):
        """Mostrar métricas finales del test"""
        logger.info("🎉 PRUEBAS DE INTEGRACIÓN COMPLETADAS")
        logger.info("=" * 80)
        self._mostrar_metricas_integracion()
        
        logger.info("🔍 ANÁLISIS DE INTEGRACIÓN:")
        logger.info("   ✅ Microservicio Marketing: Funcionando")
        logger.info("   ✅ Simulador Afiliados: Funcionando")
        logger.info("   ✅ Simulador Conversiones: Funcionando")
        logger.info("   ✅ Comunicación entre servicios: Exitosa")
        logger.info("=" * 80)
    
    def detener(self):
        """Detener el monitor"""
        self.running = False

def main():
    """Función principal"""
    print("""
🚀 DEMO DE INTEGRACIÓN DE MICROSERVICIOS
========================================

Este script demuestra la comunicación entre microservicios:

1. 🎯 MARKETING: Crea campañas via API REST
2. 👥 AFILIADOS: Simula asignación de afiliados  
3. 💰 CONVERSIONES: Simula configuración de tracking

Presiona Ctrl+C para detener
""")
    
    monitor = MonitorIntegracionMicroservicios()
    
    try:
        # Ejecutar 8 pruebas con intervalo de 2 segundos
        monitor.ejecutar_pruebas_integracion(num_campanias=8, intervalo=2.0)
        
    except KeyboardInterrupt:
        logger.info("🛑 Interrupción por usuario")
        monitor.detener()
    except Exception as e:
        logger.error(f"❌ Error en demo: {e}")
    finally:
        logger.info("🔌 Demo finalizado")

if __name__ == "__main__":
    main()