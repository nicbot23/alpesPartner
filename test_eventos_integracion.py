#!/usr/bin/env python3
"""
Test de comunicación de eventos entre microservicios
Simula el flujo completo de eventos en el ecosistema AlpesPartner
"""
import pulsar
import time
import json
import asyncio
from pulsar.schema import AvroSchema, Record, String, Integer, Float


# Schemas de eventos para la demostración
class AfiliadoRegistrado(Record):
    id = String()
    user_id = String()
    email = String()
    nombre = String()
    apellido = String()
    numero_documento = String()
    tipo_documento = String()
    telefono = String()
    fecha_afiliacion = String()
    estado = String()
    timestamp = Integer()


class ConversionDetected(Record):
    id = String()
    conversion_id = String()
    affiliate_id = String()
    campaign_id = String()
    user_id = String()
    conversion_value = Float()
    conversion_type = String()
    source_url = String()
    destination_url = String()
    timestamp = Integer()


class CampanaCreada(Record):
    id = String()
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


def test_pulsar_connection():
    """Probar conexión básica a Pulsar"""
    try:
        client = pulsar.Client('pulsar://localhost:6650')
        print("✅ Conexión a Pulsar exitosa")
        client.close()
        return True
    except Exception as e:
        print(f"❌ Error conectando a Pulsar: {e}")
        return False


def enviar_evento_afiliado():
    """Enviar evento de afiliado registrado"""
    try:
        client = pulsar.Client('pulsar://localhost:6650')
        producer = client.create_producer(
            topic='afiliados.eventos',
            schema=AvroSchema(AfiliadoRegistrado)
        )
        
        evento = AfiliadoRegistrado(
            id="af-001",
            user_id="user-123",
            email="test@example.com",
            nombre="Juan",
            apellido="Pérez",
            numero_documento="12345678",
            tipo_documento="CC",
            telefono="300123456",
            fecha_afiliacion="2024-01-15",
            estado="ACTIVO",
            timestamp=int(time.time() * 1000)
        )
        
        producer.send(evento)
        print("✅ Evento AfiliadoRegistrado enviado")
        
        producer.close()
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error enviando evento de afiliado: {e}")
        return False


def enviar_evento_campana():
    """Enviar evento de campaña creada"""
    try:
        client = pulsar.Client('pulsar://localhost:6650')
        producer = client.create_producer(
            topic='marketing.eventos',
            schema=AvroSchema(CampanaCreada)
        )
        
        evento = CampanaCreada(
            id="camp-001",
            nombre="Campaña Black Friday",
            descripcion="Promoción especial noviembre",
            tipo_campana="DESCUENTO",
            fecha_inicio="2024-11-01",
            fecha_fin="2024-11-30",
            estado="ACTIVA",
            meta_conversiones=1000,
            presupuesto=50000.0,
            created_by="admin",
            timestamp=int(time.time() * 1000)
        )
        
        producer.send(evento)
        print("✅ Evento CampanaCreada enviado")
        
        producer.close()
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error enviando evento de campaña: {e}")
        return False


def enviar_evento_conversion():
    """Enviar evento de conversión detectada"""
    try:
        client = pulsar.Client('pulsar://localhost:6650')
        producer = client.create_producer(
            topic='conversiones.eventos',
            schema=AvroSchema(ConversionDetected)
        )
        
        evento = ConversionDetected(
            id="conv-001",
            conversion_id="conversion-123",
            affiliate_id="af-001",
            campaign_id="camp-001",
            user_id="user-123",
            conversion_value=150.50,
            conversion_type="VENTA",
            source_url="https://partner.com/promo",
            destination_url="https://store.com/product",
            timestamp=int(time.time() * 1000)
        )
        
        producer.send(evento)
        print("✅ Evento ConversionDetected enviado")
        
        producer.close()
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error enviando evento de conversión: {e}")
        return False


def consumir_eventos_demo():
    """Consumir eventos de todos los topics para demo"""
    try:
        client = pulsar.Client('pulsar://localhost:6650')
        
        # Consumer para afiliados
        consumer_afiliados = client.subscribe(
            topic='afiliados.eventos',
            subscription_name='demo-test-afiliados',
            schema=AvroSchema(AfiliadoRegistrado)
        )
        
        # Consumer para marketing
        consumer_marketing = client.subscribe(
            topic='marketing.eventos', 
            subscription_name='demo-test-marketing',
            schema=AvroSchema(CampanaCreada)
        )
        
        # Consumer para conversiones
        consumer_conversiones = client.subscribe(
            topic='conversiones.eventos',
            subscription_name='demo-test-conversiones',
            schema=AvroSchema(ConversionDetected)
        )
        
        print("🔍 Consumiendo eventos por 10 segundos...")
        
        start_time = time.time()
        while time.time() - start_time < 10:
            try:
                # Intentar recibir de cada consumer
                for consumer_name, consumer in [
                    ("afiliados", consumer_afiliados),
                    ("marketing", consumer_marketing),
                    ("conversiones", consumer_conversiones)
                ]:
                    try:
                        msg = consumer.receive(timeout_millis=100)
                        data = msg.value()
                        print(f"📧 Evento recibido en {consumer_name}: {type(data).__name__}")
                        consumer.acknowledge(msg)
                    except:
                        pass  # Timeout es normal
                        
            except Exception as e:
                print(f"Error en consumer: {e}")
                
        print("⏰ Tiempo de consumo completado")
        
        consumer_afiliados.close()
        consumer_marketing.close() 
        consumer_conversiones.close()
        client.close()
        
    except Exception as e:
        print(f"❌ Error en consumidor demo: {e}")


def main():
    """Ejecutar test completo de eventos"""
    print("🚀 Iniciando prueba de comunicación por eventos...")
    print("=" * 60)
    
    # 1. Probar conexión
    if not test_pulsar_connection():
        return
    
    print("\n📤 ENVIANDO EVENTOS...")
    print("-" * 30)
    
    # 2. Enviar eventos
    enviar_evento_afiliado()
    time.sleep(1)
    
    enviar_evento_campana() 
    time.sleep(1)
    
    enviar_evento_conversion()
    time.sleep(2)
    
    print("\n📥 CONSUMIENDO EVENTOS...")
    print("-" * 30)
    
    # 3. Consumir eventos
    consumir_eventos_demo()
    
    print("\n✅ Prueba de eventos completada!")


if __name__ == "__main__":
    main()