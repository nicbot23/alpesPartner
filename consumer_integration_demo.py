#!/usr/bin/env python3
"""
Demo de Integración de Microservicios
=====================================

Este script demuestra cómo los microservicios de Afiliados y Conversiones 
pueden consumir eventos de Marketing para mostrar la integración completa.

Simula consumidores que reaccionan a eventos de campañas creadas.
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime
from typing import Dict, List

import pulsar
from pulsar.schema import AvroSchema, Record, String, Integer, Float

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =================== SCHEMAS DE EVENTOS ===================

class CampanaCreada(Record):
    """Evento de campaña creada - viene de Marketing"""
    id = String()
    campana_id = String()
    nombre = String()
    descripcion = String()
    tipo_campana = String()
    fecha_inicio = String()
    fecha_fin = String()
    estado = String()
    meta_conversiones = Integer()
    presupuesto = Float()
    created_by = String()
    timestamp = Integer()

class ComisionCalculada(Record):
    """Evento de comisión calculada - viene de Marketing"""
    id = String()
    campana_id = String()
    afiliado_id = String()
    user_id = String()
    conversion_id = String()
    monto_comision = Float()
    porcentaje_comision = Float()
    fecha_calculo = String()
    timestamp = Integer()

class NotificacionSolicitada(Record):
    """Evento de notificación solicitada - viene de Marketing"""
    id = String()
    destinatario = String()
    tipo_notificacion = String()
    plantilla = String()
    datos = String()
    prioridad = String()
    timestamp = Integer()

# =================== RESPUESTAS DE MICROSERVICIOS ===================

class AfiliadosAsignados(Record):
    """Evento generado por microservicio Afiliados"""
    id = String()
    campana_id = String()
    afiliados_asignados = String()  # JSON string con lista de afiliados
    total_afiliados = Integer()
    criterios_asignacion = String()
    timestamp = Integer()

class ConversionesActivadas(Record):
    """Evento generado por microservicio Conversiones"""
    id = String()
    campana_id = String()
    conversion_types = String()  # JSON string con tipos de conversión
    metas_establecidas = String()  # JSON string con metas
    timestamp = Integer()

# =================== SIMULADOR DE MICROSERVICIO AFILIADOS ===================

class SimuladorAfiliados:
    def __init__(self):
        self.client = None
        self.producer = None
        
    async def inicializar(self):
        """Inicializar cliente Pulsar"""
        try:
            self.client = pulsar.Client('pulsar://localhost:6650')
            self.producer = self.client.create_producer(
                'afiliados.eventos',
                schema=AvroSchema(AfiliadosAsignados)
            )
            logger.info("🔗 Simulador Afiliados inicializado")
        except Exception as e:
            logger.error(f"❌ Error inicializando Afiliados: {e}")
    
    async def procesar_campana_creada(self, evento: CampanaCreada):
        """Procesar evento de campaña creada"""
        try:
            logger.info(f"🎯 AFILIADOS: Procesando campaña {evento.nombre}")
            
            # Simular asignación de afiliados basado en tipo de campaña
            afiliados = self._generar_afiliados(evento.tipo_campana, evento.meta_conversiones)
            
            # Crear evento de respuesta
            evento_respuesta = AfiliadosAsignados(
                id=f"af-{evento.campana_id}",
                campana_id=evento.campana_id or evento.id,
                afiliados_asignados=json.dumps(afiliados),
                total_afiliados=len(afiliados),
                criterios_asignacion=f"tipo:{evento.tipo_campana},meta:{evento.meta_conversiones}",
                timestamp=int(time.time() * 1000)
            )
            
            # Publicar evento
            await asyncio.get_event_loop().run_in_executor(
                None, self.producer.send, evento_respuesta
            )
            
            logger.info(f"✅ AFILIADOS: {len(afiliados)} afiliados asignados a campaña {evento.nombre}")
            return len(afiliados)
            
        except Exception as e:
            logger.error(f"❌ Error en simulador afiliados: {e}")
            return 0
    
    def _generar_afiliados(self, tipo_campana: str, meta_conversiones: int) -> List[Dict]:
        """Generar afiliados basado en criterios"""
        # Calcular número de afiliados necesarios
        num_afiliados = min(max(meta_conversiones // 50, 3), 15)
        
        afiliados = []
        for i in range(num_afiliados):
            afiliado = {
                "id": f"af_{tipo_campana}_{i+1}",
                "nombre": f"Afiliado {tipo_campana.title()} {i+1}",
                "especialidad": tipo_campana,
                "rating": round(random.uniform(3.5, 5.0), 1),
                "activo": True
            }
            afiliados.append(afiliado)
        
        return afiliados

# =================== SIMULADOR DE MICROSERVICIO CONVERSIONES ===================

class SimuladorConversiones:
    def __init__(self):
        self.client = None
        self.producer = None
        
    async def inicializar(self):
        """Inicializar cliente Pulsar"""
        try:
            self.client = pulsar.Client('pulsar://localhost:6650')
            self.producer = self.client.create_producer(
                'conversiones.eventos',
                schema=AvroSchema(ConversionesActivadas)
            )
            logger.info("🔗 Simulador Conversiones inicializado")
        except Exception as e:
            logger.error(f"❌ Error inicializando Conversiones: {e}")
    
    async def procesar_campana_creada(self, evento: CampanaCreada):
        """Procesar evento de campaña creada"""
        try:
            logger.info(f"💰 CONVERSIONES: Configurando conversiones para {evento.nombre}")
            
            # Generar tipos de conversión basado en tipo de campaña
            conversiones = self._generar_conversiones(evento.tipo_campana, evento.presupuesto)
            metas = self._calcular_metas(evento.meta_conversiones, evento.presupuesto)
            
            # Crear evento de respuesta
            evento_respuesta = ConversionesActivadas(
                id=f"conv-{evento.campana_id}",
                campana_id=evento.campana_id or evento.id,
                conversion_types=json.dumps(conversiones),
                metas_establecidas=json.dumps(metas),
                timestamp=int(time.time() * 1000)
            )
            
            # Publicar evento
            await asyncio.get_event_loop().run_in_executor(
                None, self.producer.send, evento_respuesta
            )
            
            logger.info(f"✅ CONVERSIONES: {len(conversiones)} tipos de conversión activados")
            return len(conversiones)
            
        except Exception as e:
            logger.error(f"❌ Error en simulador conversiones: {e}")
            return 0
    
    def _generar_conversiones(self, tipo_campana: str, presupuesto: float) -> List[Dict]:
        """Generar tipos de conversión"""
        conversiones_base = {
            "digital": ["click", "view", "signup", "purchase"],
            "tradicional": ["call", "visit", "purchase", "referral"],
            "mixta": ["click", "view", "call", "visit", "signup", "purchase"]
        }
        
        tipos = conversiones_base.get(tipo_campana, ["click", "purchase"])
        
        conversiones = []
        for tipo in tipos:
            conversion = {
                "tipo": tipo,
                "valor_base": round(presupuesto / len(tipos) / 100, 2),
                "multiplicador": round(random.uniform(1.0, 2.5), 2),
                "activo": True
            }
            conversiones.append(conversion)
        
        return conversiones
    
    def _calcular_metas(self, meta_conversiones: int, presupuesto: float) -> Dict:
        """Calcular metas de conversión"""
        return {
            "conversiones_objetivo": meta_conversiones,
            "presupuesto_total": presupuesto,
            "costo_por_conversion": round(presupuesto / meta_conversiones, 2),
            "roi_esperado": "15-25%"
        }

# =================== MONITOR DE INTEGRACIÓN ===================

class MonitorIntegracion:
    def __init__(self):
        self.client = None
        self.consumer_marketing = None
        self.consumer_comisiones = None
        self.consumer_notificaciones = None
        self.simulador_afiliados = SimuladorAfiliados()
        self.simulador_conversiones = SimuladorConversiones()
        
        # Métricas
        self.eventos_procesados = {
            'campanias_creadas': 0,
            'afiliados_asignados': 0,
            'conversiones_activadas': 0,
            'comisiones_calculadas': 0,
            'notificaciones_enviadas': 0
        }
    
    async def inicializar(self):
        """Inicializar todos los consumidores"""
        try:
            self.client = pulsar.Client('pulsar://localhost:6650')
            
            # Inicializar simuladores
            await self.simulador_afiliados.inicializar()
            await self.simulador_conversiones.inicializar()
            
            # Crear consumidores
            self.consumer_marketing = self.client.subscribe(
                'marketing.eventos',
                subscription_name='integracion-campanias-sub',
                schema=AvroSchema(CampanaCreada)
            )
            
            self.consumer_comisiones = self.client.subscribe(
                'comisiones.eventos',
                subscription_name='integracion-comisiones-sub',
                schema=AvroSchema(ComisionCalculada)
            )
            
            self.consumer_notificaciones = self.client.subscribe(
                'sistema.eventos',
                subscription_name='integracion-notificaciones-sub',
                schema=AvroSchema(NotificacionSolicitada)
            )
            
            logger.info("🚀 Monitor de Integración inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando monitor: {e}")
    
    async def monitorear(self):
        """Monitorear eventos y mostrar integración"""
        logger.info("👁️  Iniciando monitoreo de integración de microservicios...")
        logger.info("=" * 80)
        
        while True:
            try:
                # Procesar eventos de marketing (campañas creadas)
                await self._procesar_eventos_marketing()
                
                # Procesar eventos de comisiones
                await self._procesar_eventos_comisiones()
                
                # Procesar eventos de notificaciones
                await self._procesar_eventos_notificaciones()
                
                # Mostrar métricas cada 10 eventos
                if sum(self.eventos_procesados.values()) % 10 == 0 and sum(self.eventos_procesados.values()) > 0:
                    self._mostrar_metricas()
                
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Deteniendo monitor...")
                break
            except Exception as e:
                logger.error(f"❌ Error en monitoreo: {e}")
                await asyncio.sleep(1)
    
    async def _procesar_eventos_marketing(self):
        """Procesar eventos de campañas creadas"""
        try:
            mensaje = self.consumer_marketing.receive(timeout_millis=100)
            evento = mensaje.value()
            
            logger.info(f"🎯 CAMPAÑA CREADA: {evento.nombre} (Presupuesto: ${evento.presupuesto})")
            
            # Simular respuesta de microservicios
            afiliados_asignados = await self.simulador_afiliados.procesar_campana_creada(evento)
            conversiones_activadas = await self.simulador_conversiones.procesar_campana_creada(evento)
            
            self.eventos_procesados['campanias_creadas'] += 1
            self.eventos_procesados['afiliados_asignados'] += afiliados_asignados
            self.eventos_procesados['conversiones_activadas'] += conversiones_activadas
            
            self.consumer_marketing.acknowledge(mensaje)
            
        except Exception as e:
            if "Timeout" not in str(e):
                logger.error(f"Error procesando eventos marketing: {e}")
    
    async def _procesar_eventos_comisiones(self):
        """Procesar eventos de comisiones calculadas"""
        try:
            mensaje = self.consumer_comisiones.receive(timeout_millis=100)
            evento = mensaje.value()
            
            logger.info(f"💰 COMISIÓN CALCULADA: ${evento.monto_comision} para campaña {evento.campana_id}")
            
            self.eventos_procesados['comisiones_calculadas'] += 1
            self.consumer_comisiones.acknowledge(mensaje)
            
        except Exception as e:
            if "Timeout" not in str(e):
                logger.error(f"Error procesando eventos comisiones: {e}")
    
    async def _procesar_eventos_notificaciones(self):
        """Procesar eventos de notificaciones"""
        try:
            mensaje = self.consumer_notificaciones.receive(timeout_millis=100)
            evento = mensaje.value()
            
            logger.info(f"📧 NOTIFICACIÓN ENVIADA: {evento.tipo_notificacion} a {evento.destinatario}")
            
            self.eventos_procesados['notificaciones_enviadas'] += 1
            self.consumer_notificaciones.acknowledge(mensaje)
            
        except Exception as e:
            if "Timeout" not in str(e):
                logger.error(f"Error procesando eventos notificaciones: {e}")
    
    def _mostrar_metricas(self):
        """Mostrar métricas de integración"""
        logger.info("=" * 80)
        logger.info("📊 MÉTRICAS DE INTEGRACIÓN DE MICROSERVICIOS")
        logger.info("=" * 80)
        
        for metrica, valor in self.eventos_procesados.items():
            logger.info(f"   {metrica.replace('_', ' ').title()}: {valor}")
        
        logger.info("=" * 80)
    
    async def cerrar(self):
        """Cerrar conexiones"""
        try:
            if self.consumer_marketing:
                self.consumer_marketing.close()
            if self.consumer_comisiones:
                self.consumer_comisiones.close()
            if self.consumer_notificaciones:
                self.consumer_notificaciones.close()
            if self.client:
                self.client.close()
            logger.info("🔌 Conexiones cerradas")
        except Exception as e:
            logger.error(f"Error cerrando conexiones: {e}")

# =================== FUNCIÓN PRINCIPAL ===================

async def main():
    """Función principal"""
    monitor = MonitorIntegracion()
    
    try:
        await monitor.inicializar()
        await monitor.monitorear()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupción por usuario")
    finally:
        await monitor.cerrar()

if __name__ == "__main__":
    print("""
🚀 DEMO DE INTEGRACIÓN DE MICROSERVICIOS
========================================

Este script demuestra cómo los microservicios se comunican:

1. 🎯 MARKETING: Crea campañas y publica eventos
2. 👥 AFILIADOS: Escucha campañas y asigna afiliados  
3. 💰 CONVERSIONES: Escucha campañas y configura conversiones
4. 📧 NOTIFICACIONES: Procesa solicitudes de notificación

Ejecuta en paralelo:
- Terminal 1: python3 consumer_integration_demo.py
- Terminal 2: python3 monitor_escenarios_completo.py

Presiona Ctrl+C para detener
""")
    
    asyncio.run(main())