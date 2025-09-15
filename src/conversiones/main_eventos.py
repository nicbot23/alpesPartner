"""
Microservicio de Conversiones - Versión con Eventos
====================================================
Versión simplificada del microservicio de conversiones que publica eventos a Pulsar
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

import pulsar
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# MODELOS DE DATOS
# ============================================

class ConversionRequest(BaseModel):
    campana_id: str
    afiliado_id: str
    user_id: str
    valor_conversion: float
    moneda: str = "COP"
    tipo_conversion: str = "venta"
    metadata: Optional[Dict[str, Any]] = None

class ConversionResponse(BaseModel):
    id: str
    status: str
    message: str
    data: Dict[str, Any]

# ============================================
# CLIENTE PULSAR GLOBAL
# ============================================

pulsar_client = None
pulsar_producer = None

async def init_pulsar_client():
    """Inicializar cliente Pulsar"""
    global pulsar_client, pulsar_producer
    try:
        logger.info("Inicializando cliente Pulsar para conversiones...")
        pulsar_client = pulsar.Client('pulsar://alpes-pulsar:6650')
        
        pulsar_producer = pulsar_client.create_producer(
            topic='persistent://public/default/conversiones.eventos',
            producer_name='conversiones-producer',
            send_timeout_millis=60000,
            block_if_queue_full=True
        )
        
        logger.info("Cliente Pulsar inicializado correctamente para conversiones")
        return True
        
    except Exception as e:
        logger.error(f"Error inicializando Pulsar: {e}")
        return False

async def close_pulsar_client():
    """Cerrar cliente Pulsar"""
    global pulsar_client, pulsar_producer
    try:
        if pulsar_producer:
            pulsar_producer.close()
            logger.info("Producer Pulsar cerrado")
        
        if pulsar_client:
            pulsar_client.close()
            logger.info("Cliente Pulsar cerrado")
            
    except Exception as e:
        logger.error(f"Error cerrando Pulsar: {e}")

# ============================================
# FUNCIONES DE EVENTOS
# ============================================

async def publicar_evento_conversion(conversion_data: Dict[str, Any]):
    """Publicar evento de conversión registrada"""
    global pulsar_producer
    
    if not pulsar_producer:
        logger.warning("Producer Pulsar no disponible, no se puede publicar evento")
        return
    
    try:
        evento = {
            "tipo": "ConversionRegistrada",
            "id": f"{conversion_data['id']}-ConversionRegistrada",
            "conversion_id": conversion_data['id'],
            "campana_id": conversion_data['campana_id'],
            "afiliado_id": conversion_data['afiliado_id'],
            "user_id": conversion_data['user_id'],
            "valor_conversion": conversion_data['valor_conversion'],
            "moneda": conversion_data['moneda'],
            "tipo_conversion": conversion_data['tipo_conversion'],
            "fecha_conversion": datetime.now().isoformat(),
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        
        # Incluir metadata si existe
        if conversion_data.get('metadata'):
            evento['metadata'] = conversion_data['metadata']
        
        mensaje_json = json.dumps(evento, ensure_ascii=False)
        
        pulsar_producer.send(mensaje_json.encode('utf-8'))
        
        logger.info(f"Evento ConversionRegistrada publicado para conversión {conversion_data['id']}")
        
    except Exception as e:
        logger.error(f"Error publicando evento de conversión: {e}")

# ============================================
# BASE DE DATOS SIMULADA
# ============================================

# Base de datos en memoria para conversiones
conversiones_db = {}
conversion_counter = 0

def generar_id_conversion() -> str:
    """Generar ID único para conversión"""
    global conversion_counter
    conversion_counter += 1
    return f"conv_{conversion_counter}"

def guardar_conversion(conversion_data: Dict[str, Any]) -> str:
    """Guardar conversión en base de datos simulada"""
    conversion_id = generar_id_conversion()
    
    conversion_record = {
        "id": conversion_id,
        "campana_id": conversion_data["campana_id"],
        "afiliado_id": conversion_data["afiliado_id"],
        "user_id": conversion_data["user_id"],
        "valor_conversion": conversion_data["valor_conversion"],
        "moneda": conversion_data["moneda"],
        "tipo_conversion": conversion_data["tipo_conversion"],
        "metadata": conversion_data.get("metadata", {}),
        "fecha_creacion": datetime.now().isoformat(),
        "estado": "registrada"
    }
    
    conversiones_db[conversion_id] = conversion_record
    logger.info(f"Conversión guardada: {conversion_record}")
    
    return conversion_id

# ============================================
# GESTIÓN DEL CICLO DE VIDA
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando microservicio de Conversiones con eventos")
    
    # Inicializar Pulsar
    pulsar_ok = await init_pulsar_client()
    if not pulsar_ok:
        logger.warning("Pulsar no disponible, eventos no se publicarán")
    
    logger.info("Microservicio de Conversiones iniciado correctamente")
    
    yield
    
    # Inicializar consumer de afiliados
    await startup_consumer()
    
    # Shutdown
    logger.info("Deteniendo microservicio de Conversiones")
    await close_pulsar_client()
    logger.info("Microservicio de Conversiones detenido")

# ============================================
# CONSUMIDOR DE EVENTOS DE AFILIADOS
# ============================================

import asyncio
import random

# Consumer global para afiliados
consumer_afiliados = None

async def consumir_eventos_afiliados():
    """Consumir eventos del tópico de afiliados"""
    global pulsar_client, consumer_afiliados
    
    try:
        if not pulsar_client:
            logger.error("Cliente Pulsar no disponible para consumer")
            return
            
        # Crear consumer para el tópico de afiliados
        consumer_afiliados = pulsar_client.subscribe(
            topic="persistent://public/default/afiliados.eventos",
            subscription_name="conversiones-subscription",
            consumer_type=pulsar.ConsumerType.Shared
        )
        
        logger.info("Consumer de afiliados iniciado correctamente")
        
        def procesar_mensaje():
            """Función que procesa mensajes en un loop separado"""
            while True:
                try:
                    # Recibir mensaje (bloqueante)
                    msg = consumer_afiliados.receive()
                    data = json.loads(msg.data().decode('utf-8'))
                    
                    logger.info(f"Evento recibido de afiliados: {data}")
                    
                    # Procesar solo eventos de afiliado registrado y validado
                    if data.get('tipo') in ['AfiliadoRegistrado', 'AfiliadoValidado']:
                        # Ejecutar procesamiento síncrono
                        procesar_afiliado_registrado_sync(data)
                    
                    # Confirmar procesamiento del mensaje
                    consumer_afiliados.acknowledge(msg)
                    
                except Exception as e:
                    logger.error(f"Error procesando mensaje de afiliados: {e}")
        
        # Ejecutar procesamiento en un thread separado
        import threading
        consumer_thread = threading.Thread(target=procesar_mensaje, daemon=True)
        consumer_thread.start()
        logger.info("Consumer thread iniciado en segundo plano")
                
    except Exception as e:
        logger.error(f"Error en consumer de afiliados: {e}")

def procesar_afiliado_registrado_sync(data):
    """Procesar evento de afiliado registrado y generar conversión automática (versión síncrona)"""
    try:
        afiliado_id = data.get('afiliado_id')
        campana_id = data.get('campana_id')
        user_id = data.get('user_id', f"user_{afiliado_id}")
        
        if not afiliado_id or not campana_id:
            logger.warning(f"Datos incompletos en evento de afiliado: {data}")
            return
        
        # Generar conversión automática para el afiliado
        conversion_data = {
            "afiliado_id": afiliado_id,
            "campana_id": campana_id,
            "user_id": user_id,
            "valor_conversion": round(random.uniform(100, 1000), 2),  # Monto aleatorio simulado
            "moneda": "COP",
            "tipo_conversion": "venta_online",
            "automatica": True,
            "metadata": {
                "generado_por": "evento_afiliado",
                "evento_origen": data.get('tipo', 'AfiliadoRegistrado')
            }
        }
        
        logger.info(f"Generando conversión automática para afiliado {afiliado_id}: {conversion_data}")
        
        # Guardar conversión en base de datos
        conversion_id = guardar_conversion(conversion_data)
        conversion_data["id"] = conversion_id
        
        # Publicar evento de conversión registrada (función síncrona)
        publicar_evento_conversion_sync(conversion_data)
        
        logger.info(f"Conversión automática {conversion_id} generada exitosamente para afiliado {afiliado_id}")
        
    except Exception as e:
        logger.error(f"Error procesando afiliado registrado: {e}")

def publicar_evento_conversion_sync(conversion_data: Dict[str, Any]):
    """Versión síncrona de publicar evento de conversión"""
    global pulsar_producer
    
    if not pulsar_producer:
        logger.warning("Producer Pulsar no disponible, no se puede publicar evento")
        return
    
    try:
        evento = {
            "tipo": "ConversionRegistrada",
            "id": f"{conversion_data['id']}-ConversionRegistrada",
            "conversion_id": conversion_data['id'],
            "campana_id": conversion_data['campana_id'],
            "afiliado_id": conversion_data['afiliado_id'],
            "user_id": conversion_data['user_id'],
            "valor_conversion": conversion_data['valor_conversion'],
            "moneda": conversion_data['moneda'],
            "tipo_conversion": conversion_data['tipo_conversion'],
            "fecha_conversion": datetime.now().isoformat(),
            "timestamp": int(datetime.now().timestamp() * 1000),
            "automatica": conversion_data.get('automatica', False)
        }
        
        # Incluir metadata si existe
        if conversion_data.get('metadata'):
            evento['metadata'] = conversion_data['metadata']
        
        mensaje_json = json.dumps(evento, ensure_ascii=False)
        pulsar_producer.send(mensaje_json.encode('utf-8'))
        
        logger.info(f"Evento ConversionRegistrada publicado para conversión {conversion_data['id']}")
        
    except Exception as e:
        logger.error(f"Error publicando evento de conversión: {e}")

async def startup_consumer():
    """Inicializar consumer en segundo plano"""
    try:
        # Crear tarea en background para el consumer
        consumer_task = asyncio.create_task(consumir_eventos_afiliados())
        logger.info("Consumer de afiliados iniciado en segundo plano")
        return consumer_task
    except Exception as e:
        logger.error(f"Error iniciando consumer de afiliados: {e}")

# ============================================
# APLICACIÓN FASTAPI
# ============================================

app = FastAPI(
    title="Microservicio de Conversiones",
    description="Microservicio para gestionar conversiones con eventos",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Microservicio de Conversiones con Eventos",
        "version": "1.0.0",
        "eventos": True
    }

@app.get("/health")
async def health():
    """Endpoint de salud"""
    return {
        "status": "healthy",
        "service": "conversiones",
        "pulsar_connected": pulsar_producer is not None
    }

@app.post("/conversiones", response_model=ConversionResponse)
async def crear_conversion(conversion_request: ConversionRequest):
    """Crear nueva conversión"""
    logger.info(f"Nueva conversión recibida: {conversion_request.dict()}")
    
    try:
        # Guardar conversión en base de datos
        conversion_id = guardar_conversion(conversion_request.dict())
        
        # Preparar datos para evento
        conversion_data = {
            "id": conversion_id,
            **conversion_request.dict()
        }
        
        # Publicar evento de conversión registrada
        await publicar_evento_conversion(conversion_data)
        
        # Respuesta exitosa
        response_data = {
            "id": conversion_id,
            "status": "created",
            "message": "Conversión creada exitosamente",
            "data": conversion_data
        }
        
        logger.info(f"Conversión {conversion_id} creada exitosamente")
        return response_data
        
    except Exception as e:
        logger.error(f"Error creando conversión: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/conversiones/{conversion_id}")
async def obtener_conversion(conversion_id: str):
    """Obtener conversión por ID"""
    if conversion_id not in conversiones_db:
        raise HTTPException(status_code=404, detail="Conversión no encontrada")
    
    return {
        "conversion": conversiones_db[conversion_id]
    }

@app.get("/conversiones")
async def listar_conversiones():
    """Listar todas las conversiones"""
    return {
        "conversiones": list(conversiones_db.values()),
        "total": len(conversiones_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_eventos:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )