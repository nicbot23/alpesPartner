"""
API Simple para Marketing - Demostración con eventos reales
"""
import uvicorn
import asyncio
import os
import json
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import pulsar
from pulsar.schema import JsonSchema

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cliente Pulsar global
pulsar_client = None

class SimplePulsarPublisher:
    def __init__(self):
        self.client = None
        self.producers = {}
    
    async def inicializar(self):
        """Inicializar cliente Pulsar"""
        try:
            pulsar_url = os.getenv('PULSAR_URL', 'pulsar://pulsar:6650')
            self.client = pulsar.Client(pulsar_url)
            logger.info(f"✅ Cliente Pulsar inicializado: {pulsar_url}")
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente Pulsar: {e}")
    
    async def publicar_evento(self, topico: str, evento_dict):
        """Publicar evento como JSON simple"""
        try:
            if not self.client:
                await self.inicializar()
            
            if topico not in self.producers:
                self.producers[topico] = self.client.create_producer(
                    topic=topico
                )
            
            producer = self.producers[topico]
            
            # Convertir a JSON y enviar
            mensaje_json = json.dumps(evento_dict).encode('utf-8')
            producer.send(mensaje_json)
            
            logger.info(f"📡 Evento publicado en {topico}: {evento_dict.get('tipo', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error publicando evento en {topico}: {e}")
            return False
    
    async def cerrar(self):
        """Cerrar cliente"""
        if self.client:
            self.client.close()

# Instancia global del publicador
publisher = SimplePulsarPublisher()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando servicio marketing simple con eventos reales...")
    await publisher.inicializar()
    
    yield
    
    # Shutdown
    logger.info("🔄 Cerrando servicio marketing...")
    await publisher.cerrar()

# Crear aplicación FastAPI con lifespan
app = FastAPI(
    title="AlpesPartner - Marketing",
    description="API del microservicio de Marketing con eventos reales",
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

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "AlpesPartner - Servicio de Marketing",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "marketing",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/campanas")
async def listar_campanas():
    """Listar campañas de marketing"""
    return {
        "campanas": [
            {
                "id": "camp-1",
                "nombre": "Campaña Primavera 2024",
                "descripcion": "Promoción especial de primavera",
                "estado": "activa",
                "fecha_inicio": "2024-03-01",
                "fecha_fin": "2024-05-31"
            },
            {
                "id": "camp-2",
                "nombre": "Black Friday 2024",
                "descripcion": "Descuentos especiales Black Friday",
                "estado": "planificada",
                "fecha_inicio": "2024-11-20",
                "fecha_fin": "2024-11-30"
            }
        ]
    }

@app.get("/comisiones")
async def listar_comisiones():
    """Listar comisiones"""
    return {
        "comisiones": [
            {
                "id": "com-1",
                "afiliado_id": "1",
                "conversion_id": "conv-1",
                "valor": 15.00,
                "porcentaje": 10.0,
                "estado": "calculada"
            },
            {
                "id": "com-2",
                "afiliado_id": "2",
                "conversion_id": "conv-2", 
                "valor": 25.00,
                "porcentaje": 10.0,
                "estado": "pagada"
            }
        ]
    }

@app.post("/campanas")
async def crear_campana(campana: dict):
    """Crear nueva campaña con eventos reales en Pulsar"""
    logger.info(f"Creando campaña: {campana}")
    
    campaign_id = f"camp-{campana.get('nombre', 'default').replace(' ', '-').lower()}"
    timestamp = int(datetime.now().timestamp() * 1000)
    eventos_publicados = []
    
    try:
        # 1. Publicar evento CampanaCreada
        evento_campana = {
            "tipo": "CampanaCreada",
            "id": campaign_id,
            "campana_id": campaign_id,
            "nombre": campana.get('nombre', ''),
            "descripcion": campana.get('descripcion', ''),
            "tipo_campana": campana.get('tipo_campana', 'DESCUENTO'),
            "fecha_inicio": campana.get('fecha_inicio', ''),
            "fecha_fin": campana.get('fecha_fin', ''),
            "estado": "creada",
            "meta_conversiones": campana.get('meta_conversiones', 100),
            "presupuesto": float(campana.get('presupuesto', 0.0)),
            "created_by": "api-user",
            "timestamp": timestamp
        }
        
        if await publisher.publicar_evento('marketing.eventos', evento_campana):
            eventos_publicados.append("CampanaCreada")
        
        # 2. Publicar evento ComisionCalculada (configuración inicial)
        evento_comision = {
            "tipo": "ComisionCalculada",
            "id": f"comision-{campaign_id}",
            "campana_id": campaign_id,
            "afiliado_id": "afiliado-default",
            "user_id": "system",
            "conversion_id": "config-inicial",
            "monto_comision": 0.0,
            "porcentaje_comision": float(campana.get('comision_porcentaje', 0.05) * 100),
            "fecha_calculo": datetime.now().isoformat(),
            "timestamp": timestamp
        }
        
        if await publisher.publicar_evento('comisiones.eventos', evento_comision):
            eventos_publicados.append("ComisionesConfiguradas")
        
        # 3. Publicar evento NotificacionSolicitada
        evento_notificacion = {
            "tipo": "NotificacionSolicitada",
            "id": f"notif-{campaign_id}",
            "destinatario": "marketing-team@alpes.com",
            "tipo_notificacion": "email",
            "plantilla": "nueva-campana",
            "datos": {
                "campana": campana.get("nombre"),
                "presupuesto": campana.get("presupuesto", 0)
            },
            "prioridad": "alta",
            "timestamp": timestamp
        }
        
        if await publisher.publicar_evento('sistema.eventos', evento_notificacion):
            eventos_publicados.append("NotificacionSolicitada")
        
        # Si hay afiliados, simular evento de configuración
        if campana.get('afiliados'):
            eventos_publicados.append("AfiliacionesConfiguradas")
        
        logger.info(f"✅ Campaña creada: {campaign_id}")
        logger.info(f"🔥 Eventos publicados en Pulsar: {eventos_publicados}")
        
    except Exception as e:
        logger.error(f"❌ Error publicando eventos: {e}")
        # Continuar con respuesta aunque falle la publicación
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "message": f"Campaña '{campana.get('nombre')}' creada exitosamente",
        "data": {
            "campaign_id": campaign_id,
            "nombre": campana.get('nombre'),
            "presupuesto": campana.get('presupuesto'),
            "meta_conversiones": campana.get('meta_conversiones'),
            "afiliados_asignados": len(campana.get('afiliados', [])),
            "comision_porcentaje": campana.get('comision_porcentaje'),
            "fecha_creacion": datetime.now().isoformat(),
            "eventos_generados": eventos_publicados
        }
    }

@app.post("/campanas/{campaign_id}/activate")
async def activar_campana(campaign_id: str):
    """Activar una campaña específica"""
    logger.info(f"Activando campaña: {campaign_id}")
    
    return {
        "success": True,
        "message": f"Campaña {campaign_id} activada exitosamente",
        "events_triggered": [
            "CampanaActivada",
            "NotificacionesAfiliados",
            "ConfiguracionSegmentacion"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
