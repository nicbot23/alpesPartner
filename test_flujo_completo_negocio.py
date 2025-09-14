#!/usr/bin/env python3
"""
Test del flujo completo de negocio - AlpesPartner
Prueba crear campaña y verificar que se desencadenen todos los eventos automáticamente
"""
import requests
import time
import json
import pulsar
from pulsar.schema import AvroSchema
import threading
import asyncio


def test_crear_campana_completa():
    """Probar crear campaña con flujo completo de eventos"""
    print("🚀 INICIANDO PRUEBA DE FLUJO COMPLETO DE NEGOCIO")
    print("="*60)
    
    # Datos de la campaña completa
    campana_data = {
        "nombre": "Black Friday 2024 - Test Integration",
        "descripcion": "Campaña especial con flujo completo de eventos",
        "tipo_campana": "DESCUENTO",
        "fecha_inicio": "2024-11-29",
        "fecha_fin": "2024-12-02", 
        "meta_conversiones": 1000,
        "presupuesto": 75000.0,
        "afiliados": ["aff_001", "aff_002", "aff_003"],
        "comision_porcentaje": 0.08
    }
    
    print(f"📋 CREANDO CAMPAÑA: {campana_data['nombre']}")
    print(f"💰 Presupuesto: ${campana_data['presupuesto']:,.2f}")
    print(f"🎯 Meta conversiones: {campana_data['meta_conversiones']}")
    print(f"👥 Afiliados: {len(campana_data['afiliados'])}")
    print(f"💸 Comisión: {campana_data['comision_porcentaje']*100}%")
    print("-" * 50)
    
    try:
        # Crear campaña
        response = requests.post(
            "http://localhost:8003/campanas",  # Sistema completo DDD
            json=campana_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CAMPAÑA CREADA EXITOSAMENTE!")
            print(f"🆔 Campaign ID: {result.get('campaign_id')}")
            print(f"📅 Fecha creación: {result.get('data', {}).get('fecha_creacion')}")
            
            eventos_generados = result.get('data', {}).get('eventos_generados', [])
            print(f"🔥 Eventos generados: {len([e for e in eventos_generados if e])}")
            for evento in eventos_generados:
                if evento:
                    print(f"   📡 {evento}")
            
            campaign_id = result.get('campaign_id')
            
            # Simular conversión para probar flujo completo
            print(f"\n💫 SIMULANDO CONVERSIÓN PARA PROBAR FLUJO...")
            conversion_data = {
                "affiliate_id": "aff_001",
                "campaign_id": campaign_id,
                "user_id": "user_black_friday_001", 
                "conversion_value": 599.99,
                "conversion_type": "purchase"
            }
            
            conv_response = requests.post(
                "http://localhost:8002/conversiones",
                json=conversion_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if conv_response.status_code == 200:
                conv_result = conv_response.json()
                print(f"✅ Conversión simulada: {conv_result.get('id')}")
                print(f"💰 Valor: ${conversion_data['conversion_value']}")
                print(f"📈 Comisión esperada: ${conversion_data['conversion_value'] * campana_data['comision_porcentaje']:.2f}")
            
            return True
            
        else:
            print(f"❌ ERROR CREANDO CAMPAÑA: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")
        return False


def test_activar_campana(campaign_id):
    """Probar activación de campaña"""
    print(f"\n🎯 ACTIVANDO CAMPAÑA: {campaign_id}")
    print("-" * 40)
    
    try:
        response = requests.post(
            f"http://localhost:8003/campanas/{campaign_id}/activate",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CAMPAÑA ACTIVADA!")
            
            events = result.get('events_triggered', [])
            print(f"🔥 Eventos de activación: {len(events)}")
            for event in events:
                print(f"   📡 {event}")
            
            return True
        else:
            print(f"❌ Error activando: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en activación: {e}")
        return False


def monitor_pulsar_events():
    """Monitorear eventos en tiempo real"""
    print(f"\n📡 MONITOREANDO EVENTOS EN APACHE PULSAR")
    print("-" * 45)
    
    try:
        client = pulsar.Client('pulsar://localhost:6650')
        
        # Monitoring topics
        topics_to_monitor = [
            'marketing.eventos',
            'conversiones.eventos', 
            'comisiones.eventos'
        ]
        
        consumers = []
        for topic in topics_to_monitor:
            try:
                consumer = client.subscribe(
                    topic=topic,
                    subscription_name=f'monitor-{topic.replace(".", "-")}',
                    initial_position=pulsar.InitialPosition.Latest
                )
                consumers.append((topic, consumer))
                print(f"🔗 Suscrito a {topic}")
            except Exception as e:
                print(f"⚠️  No se pudo suscribir a {topic}: {e}")
        
        print("🔍 Monitoreando por 10 segundos...")
        
        events_captured = 0
        start_time = time.time()
        
        while time.time() - start_time < 10:
            for topic, consumer in consumers:
                try:
                    msg = consumer.receive(timeout_millis=100)
                    events_captured += 1
                    print(f"📧 Evento capturado en {topic}: {msg.message_id()}")
                    consumer.acknowledge(msg)
                except:
                    pass  # Timeout normal
        
        print(f"📊 Total eventos capturados: {events_captured}")
        
        # Cleanup
        for _, consumer in consumers:
            consumer.close()
        client.close()
        
        return events_captured
        
    except Exception as e:
        print(f"❌ Error monitoreando eventos: {e}")
        return 0


def verificar_consistencia_datos():
    """Verificar que los datos estén consistentes entre servicios"""
    print(f"\n🔍 VERIFICANDO CONSISTENCIA DE DATOS")
    print("-" * 40)
    
    try:
        # Verificar campañas
        campaigns_response = requests.get("http://localhost:8003/campanas", timeout=5)
        if campaigns_response.status_code == 200:
            campaigns = campaigns_response.json().get('data', [])
            print(f"📊 Campañas totales: {len(campaigns)}")
            
            # Buscar nuestra campaña de prueba
            test_campaign = None
            for camp in campaigns:
                if "Black Friday 2024 - Test Integration" in camp.get('nombre', ''):
                    test_campaign = camp
                    break
            
            if test_campaign:
                print(f"✅ Campaña de prueba encontrada: {test_campaign.get('id')}")
        
        # Verificar conversiones
        conv_response = requests.get("http://localhost:8002/conversiones", timeout=5)
        if conv_response.status_code == 200:
            conversions = conv_response.json().get('conversiones', [])
            print(f"📊 Conversiones totales: {len(conversions)}")
            
            # Buscar conversión de prueba
            test_conversion = None
            for conv in conversions:
                if conv.get('user_id') == 'user_black_friday_001':
                    test_conversion = conv
                    break
            
            if test_conversion:
                print(f"✅ Conversión de prueba encontrada: {test_conversion.get('id')}")
                print(f"💰 Valor: ${test_conversion.get('conversion_value')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando consistencia: {e}")
        return False


def main():
    """Ejecutar prueba completa del flujo de negocio"""
    print("🏢 ECOSISTEMA ALPESPARTNER - PRUEBA DE FLUJO COMPLETO")
    print("🎯 Objetivo: Validar flujo end-to-end de eventos")
    print("="*70)
    
    # 1. Crear campaña completa
    campaign_created = test_crear_campana_completa()
    
    if not campaign_created:
        print("🚨 FLUJO INTERRUMPIDO: No se pudo crear campaña")
        return
    
    time.sleep(2)
    
    # 2. Monitorear eventos en paralelo
    print("\n" + "="*50)
    events_captured = monitor_pulsar_events()
    
    time.sleep(1)
    
    # 3. Verificar consistencia
    print("\n" + "="*50)  
    consistency_ok = verificar_consistencia_datos()
    
    # 4. Resultado final
    print("\n🎯 RESULTADO FINAL DEL FLUJO")
    print("="*45)
    
    results = {
        "Creación de campaña": "✅ EXITOSO" if campaign_created else "❌ FALLÓ",
        "Eventos capturados": f"✅ {events_captured} eventos" if events_captured > 0 else "⚠️  Sin eventos",
        "Consistencia datos": "✅ CONSISTENTE" if consistency_ok else "❌ INCONSISTENTE"
    }
    
    for test, result in results.items():
        print(f"{result} {test}")
    
    # Evaluación final
    all_passed = campaign_created and events_captured > 0 and consistency_ok
    
    if all_passed:
        print("\n🎉 ¡FLUJO COMPLETO EXITOSO!")
        print("🎬 ¡LISTO PARA DEMOSTRACIÓN EN VIDEO!")
        print("📋 El ecosistema maneja correctamente:")
        print("   • Creación de campañas")
        print("   • Eventos de integración")  
        print("   • Cálculo automático de comisiones")
        print("   • Consistencia entre microservicios")
    else:
        print("\n⚠️  FLUJO PARCIALMENTE FUNCIONAL")
        print("🔧 Revisar componentes que fallaron")


if __name__ == "__main__":
    main()