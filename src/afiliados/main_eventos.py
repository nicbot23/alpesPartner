"""
API Simple para Afiliados con Eventos - Demostración
"""
import uvicorn
import asyncio
import json
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pulsar
from contextlib import asynccontextmanager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cliente Pulsar global
pulsar_client = None
producer_afiliados = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    global pulsar_client, producer_afiliados
    
    # Startup
    logger.info("Iniciando microservicio de Afiliados con eventos")
    
    try:
        # Inicializar cliente Pulsar
        pulsar_client = pulsar.Client('pulsar://alpes-pulsar:6650')
        
        # Crear producer para eventos de afiliados
        producer_afiliados = pulsar_client.create_producer(
            topic='persistent://public/default/afiliados.eventos'
        )
        
        logger.info("Cliente Pulsar y producers inicializados")
        
    except Exception as e:
        logger.error(f"Error inicializando Pulsar: {e}")
    
    yield
    
    # Shutdown
    logger.info("Deteniendo microservicio de Afiliados")
    
    try:
        if producer_afiliados:
            producer_afiliados.close()
        if pulsar_client:
            pulsar_client.close()
        logger.info("Cliente Pulsar cerrado")
    except Exception as e:
        logger.error(f"Error cerrando Pulsar: {e}")

# Crear aplicación FastAPI
app = FastAPI(
    title="AlpesPartner - Afiliados con Eventos",
    description="API del microservicio de Afiliados con publicación de eventos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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

async def publicar_evento_afiliado(evento_tipo: str, afiliado_data: dict):
    """Publicar evento de afiliado a Pulsar"""
    try:
        if producer_afiliados:
            evento = {
                "tipo": evento_tipo,
                "id": f"af-{datetime.now().strftime('%Y%m%d%H%M%S')}-{afiliado_data.get('nombre', 'unknown')[:10]}",
                "afiliado_id": afiliado_data.get('id', 'new-123'),
                "nombre": afiliado_data.get('nombre', ''),
                "email": afiliado_data.get('email', ''),
                "telefono": afiliado_data.get('telefono', ''),
                "categoria": afiliado_data.get('categoria', 'standard'),
                "region": afiliado_data.get('region', 'nacional'),
                "comision_porcentaje": afiliado_data.get('comision_porcentaje', 10.0),
                "fecha_registro": datetime.now().isoformat(),
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            
            producer_afiliados.send(json.dumps(evento).encode('utf-8'))
            logger.info(f"Evento {evento_tipo} publicado para afiliado {afiliado_data.get('nombre')}")
            return True
    except Exception as e:
        logger.error(f"Error publicando evento: {e}")
        return False

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "AlpesPartner - Servicio de Afiliados con Eventos",
        "version": "1.0.0",
        "status": "active",
        "eventos": "enabled"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "afiliados",
        "eventos": "enabled",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/afiliados")
async def listar_afiliados():
    """Listar afiliados"""
    return {
        "afiliados": [
            {
                "id": "1",
                "nombre": "Juan Pérez",
                "email": "juan@example.com",
                "telefono": "+57-300-123-4567",
                "categoria": "premium",
                "estado": "activo"
            },
            {
                "id": "2", 
                "nombre": "María García",
                "email": "maria@example.com",
                "telefono": "+57-301-987-6543",
                "categoria": "standard",
                "estado": "activo"
            }
        ]
    }

@app.post("/afiliados")
async def crear_afiliado(afiliado: dict):
    """Crear nuevo afiliado con publicación de eventos"""
    logger.info(f"Creando afiliado: {afiliado}")
    
    # Asignar ID único
    afiliado_id = f"af-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    afiliado_con_id = {**afiliado, "id": afiliado_id}
    
    # Publicar evento AfiliadoRegistrado
    await publicar_evento_afiliado("AfiliadoRegistrado", afiliado_con_id)
    
    # Simular proceso asíncrono - publicar evento de validación después de un momento
    asyncio.create_task(validar_afiliado_asincrono(afiliado_con_id))
    
    return {
        "message": "Afiliado creado exitosamente",
        "id": afiliado_id,
        "afiliado": afiliado_con_id,
        "eventos": "publicados"
    }

async def validar_afiliado_asincrono(afiliado_data: dict):
    """Validar afiliado de forma asíncrona y publicar evento"""
    try:
        # Simular validación que toma tiempo
        await asyncio.sleep(2)
        
        # Publicar evento de validación
        await publicar_evento_afiliado("AfiliadoValidado", {
            **afiliado_data,
            "estado_validacion": "aprobado",
            "observaciones": "Validación automática exitosa"
        })
        
        logger.info(f"Afiliado {afiliado_data['nombre']} validado asincrónicamente")
        
    except Exception as e:
        logger.error(f"Error en validación asíncrona: {e}")

@app.get("/afiliados/{afiliado_id}")
async def obtener_afiliado(afiliado_id: str):
    """Obtener afiliado por ID"""
    return {
        "id": afiliado_id,
        "nombre": "Afiliado Ejemplo",
        "email": "ejemplo@test.com",
        "telefono": "+57-300-000-0000",
        "categoria": "premium",
        "estado": "activo"
    }

@app.get("/afiliados/{afiliado_id}/comisiones")
async def obtener_comisiones_afiliado(afiliado_id: str):
    """Obtener comisiones de un afiliado"""
    return {
        "afiliado_id": afiliado_id,
        "comisiones": [
            {
                "id": "com-001",
                "campana_id": "camp-001",
                "monto": 15000,
                "porcentaje": 15.0,
                "fecha": "2024-01-15",
                "estado": "pagada"
            }
        ],
        "total_comisiones": 15000
    }

# ============================================
# CONSUMER DE EVENTOS DE MARKETING
# ============================================

async def consumir_eventos_marketing():
    """Consumer que escucha eventos de marketing para auto-registrar afiliados"""
    try:
        logger.info("🔗 Iniciando consumer de eventos de marketing...")
        
        consumer_client = pulsar.Client('pulsar://alpes-pulsar:6650')
        consumer = consumer_client.subscribe(
            topic='persistent://public/default/marketing.eventos',
            subscription_name='afiliados-marketing-consumer',
            consumer_type=pulsar.ConsumerType.Shared
        )
        
        logger.info("✅ Consumer de marketing iniciado correctamente")
        
        while True:
            try:
                mensaje = consumer.receive(timeout_millis=5000)
                data = json.loads(mensaje.data().decode('utf-8'))
                
                # Procesar solo eventos de CampanaCreada
                if data.get('tipo') == 'CampanaCreada':
                    await procesar_campana_creada(data)
                
                consumer.acknowledge(mensaje)
                
            except Exception as e:
                if "Timeout" not in str(e):
                    logger.error(f"Error en consumer de marketing: {e}")
                await asyncio.sleep(1)
                
    except Exception as e:
        logger.error(f"Error iniciando consumer de marketing: {e}")

async def procesar_campana_creada(evento_campana):
    """Procesar evento CampanaCreada y auto-registrar afiliado"""
    try:
        logger.info(f"🎯 Procesando CampanaCreada: {evento_campana.get('campana_id')}")
        
        # Extraer datos de la campaña
        campana_id = evento_campana.get('campana_id', 'unknown')
        campana_nombre = evento_campana.get('nombre', 'Campaña Auto')
        
        # Crear afiliado automáticamente para la campaña
        timestamp = datetime.now().strftime("%H%M%S")
        afiliado_data = {
            "nombre": f"Afiliado Auto {timestamp}",
            "email": f"auto.{timestamp}@{campana_id}.com",
            "telefono": f"+5730{timestamp}",
            "categoria": "premium",
            "comision_porcentaje": 18.0,
            "region": "nacional",
            "estado": "activo",
            "campana_asociada": campana_id,
            "origen": "automatico",
            "fecha_registro": datetime.now().isoformat()
        }
        
        # Simular guardado en BD
        afiliado_id = f"af-auto-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        afiliado_data["id"] = afiliado_id
        
        # Publicar evento AfiliadoRegistrado
        await publicar_evento_afiliado("AfiliadoRegistrado", afiliado_data)
        
        # Esperar un poco y publicar AfiliadoValidado
        await asyncio.sleep(2)
        await publicar_evento_afiliado("AfiliadoValidado", afiliado_data)
        
        logger.info(f"✅ Afiliado {afiliado_id} auto-registrado para campaña {campana_id}")
        
    except Exception as e:
        logger.error(f"Error procesando CampanaCreada: {e}")

# Iniciar consumer en background
@app.on_event("startup")
async def startup_consumer():
    """Iniciar consumer de marketing al arrancar la app"""
    asyncio.create_task(consumir_eventos_marketing())

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )