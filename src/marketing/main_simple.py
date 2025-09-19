"""
API Simple para Marketing - Demostración con eventos reales
"""
import uvicorn
import asyncio
import os
import json
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import pulsar
from pulsar.schema import JsonSchema
import pymysql
import sqlalchemy
from sqlalchemy import create_engine, text

# Nuevas dependencias capa aplicación Campañas
from .modulos.campanas.aplicacion.comandos import CrearCampanaCommand
from .modulos.campanas.aplicacion.handlers import CrearCampanaHandler
from .modulos.campanas.infraestructura.publisher_pulsar import PulsarPublisherCampanas
from .modulos.campanas.infraestructura.repositorio_sql import RepositorioCampanasSQL
from .modulos.comisiones.infraestructura.publisher_pulsar import PulsarPublisherComisiones
from .modulos.comisiones.infraestructura.repositorio_sql import RepositorioComisionesSQL
from .modulos.comisiones.aplicacion.calculo_inicial_handler import CalcularComisionInicialHandler
from .modulos.comisiones.aplicacion.calculo_inicial_command import CalcularComisionInicialCommand

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

# Instancias globales (legacy + nuevas capas)
publisher = SimplePulsarPublisher()  # Legacy (mantener para otros endpoints si existieran)
publisher_campanas = PulsarPublisherCampanas()
repo_campanas = RepositorioCampanasSQL()
handler_crear_campana: CrearCampanaHandler | None = None
publisher_comisiones = PulsarPublisherComisiones()
repo_comisiones = RepositorioComisionesSQL()
handler_comision_inicial: CalcularComisionInicialHandler | None = None
task_consumidor_comandos = None

# Configuración de base de datos
class SimpleDBManager:
    def __init__(self):
        self.engine = None
        
    async def inicializar(self):
        """Inicializar conexión a MySQL"""
        try:
            db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://alpes:alpes@mysql-marketing:3306/alpes_marketing')
            self.engine = create_engine(db_url)
            # Probar conexión
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"✅ Base de datos conectada: {db_url.split('@')[1]}")
        except Exception as e:
            logger.error(f"❌ Error conectando a base de datos: {e}")
    
    async def guardar_campana(self, campana_data: dict):
        """Guardar campaña en base de datos"""
        try:
            if not self.engine:
                await self.inicializar()
            
            insert_sql = text("""
                INSERT INTO campanas (
                    id, nombre, descripcion, marca, categoria, tags,
                    fecha_inicio, fecha_fin, terminos_comision, restriccion_geografica,
                    estado, creada_en, version, activa
                ) VALUES (
                    :id, :nombre, :descripcion, :marca, :categoria, :tags,
                    :fecha_inicio, :fecha_fin, :terminos_comision, :restriccion_geografica,
                    :estado, :creada_en, :version, :activa
                )
            """)
            
            with self.engine.connect() as conn:
                conn.execute(insert_sql, campana_data)
                conn.commit()
            
            logger.info(f"💾 Campaña guardada en BD: {campana_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando campaña en BD: {e}")
            return False

# Instancia global del DB manager
db_manager = SimpleDBManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando servicio marketing simple con eventos reales...")
    await publisher.inicializar()
    await db_manager.inicializar()
    await publisher_campanas.inicializar()
    await repo_campanas.inicializar()
    await publisher_comisiones.inicializar()
    await repo_comisiones.inicializar()
    global handler_crear_campana, handler_comision_inicial
    handler_comision_inicial = CalcularComisionInicialHandler(publisher=publisher_comisiones, repo=repo_comisiones)
    handler_crear_campana = CrearCampanaHandler(publicador=publisher_campanas, repositorio=repo_campanas, handler_comision=handler_comision_inicial)
    logger.info("✅ Handlers inicializados: handler_crear_campana=%s handler_comision_inicial=%s", bool(handler_crear_campana), bool(handler_comision_inicial))
    
    # Lanzar consumidor de comandos (CrearCampanaCommand) desde tópico marketing.campanas.comandos
    async def consumir_comandos():
        topico_cmd = os.getenv('CAMPANAS_COMMANDS_TOPIC', 'persistent://public/default/marketing.campanas.comandos')
        try:
            cliente = pulsar.Client(os.getenv('PULSAR_URL', 'pulsar://pulsar:6650'))
            consumidor = cliente.subscribe(topico_cmd, subscription_name='marketing-campanas-cmd-sub')
            logger.info(f"🛰️ Consumidor de comandos Campañas escuchando {topico_cmd}")
            while True:
                try:
                    msg = consumidor.receive(timeout_millis=30000)
                except pulsar.Timeout:
                    # No hay mensajes por ahora: continuar sin loguear error fatal
                    continue
                except Exception as e:
                    logger.error(f"[Campañas][CommandConsumer] Error recibiendo del tópico: {e}")
                    continue
                try:
                    data = json.loads(msg.data())
                    if data.get('command') == 'CrearCampana':
                        payload = data.get('payload', {})
                        comando = CrearCampanaCommand(
                            nombre=payload.get('nombre',''),
                            descripcion=payload.get('descripcion',''),
                            tipo_campana=payload.get('tipo_campana','PROMOCIONAL'),
                            fecha_inicio=payload.get('fecha_inicio','2024-01-01'),
                            fecha_fin=payload.get('fecha_fin','2024-12-31'),
                            meta_conversiones=payload.get('meta_conversiones',0),
                            presupuesto=float(payload.get('presupuesto',0.0)),
                            comision_porcentaje=float(payload.get('comision_porcentaje',0.05)),
                            marca=payload.get('marca','ALPES'),
                            categoria=payload.get('categoria','MARKETING'),
                            tags=payload.get('tags',[]),
                            afiliados=payload.get('afiliados',[]),
                            correlation_id=data.get('correlation_id')
                        )
                        try:
                            logger.info("[Campañas][CommandConsumer] Ejecutando handler_crear_campana correlation_id=%s", data.get('correlation_id'))
                            await handler_crear_campana.handle(comando)
                            logger.info("[Campañas][CommandConsumer] Handler crear campaña finalizado correlation_id=%s", data.get('correlation_id'))
                            logger.info(f"✅ Comando CrearCampana procesado correlation_id={data.get('correlation_id')}")
                        except Exception as e:
                            logger.error(f"❌ Error procesando comando CrearCampana: {e}")
                    consumidor.acknowledge(msg)
                except Exception as e:
                    logger.error(f"Error general en consumidor comandos: {e}")
        except Exception as e:
            logger.error(f"Fallo inicializando consumidor de comandos: {e}")

    global task_consumidor_comandos
    loop = asyncio.get_event_loop()
    task_consumidor_comandos = loop.create_task(consumir_comandos())
    
    yield
    
    # Shutdown
    logger.info("🔄 Cerrando servicio marketing...")
    await publisher.cerrar()
    await publisher_campanas.cerrar()
    await publisher_comisiones.cerrar()
    if task_consumidor_comandos:
        task_consumidor_comandos.cancel()

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
    """Crear nueva campaña delegando en capa aplicación (refactor DDD)."""
    logger.info(f"[API] Crear campaña (refactor) payload={campana}")
    if not handler_crear_campana:
        return {"success": False, "error": "Handler no inicializado"}

    comando = CrearCampanaCommand(
        nombre=campana.get('nombre', ''),
        descripcion=campana.get('descripcion', ''),
        tipo_campana=campana.get('tipo_campana', 'PROMOCIONAL'),
        fecha_inicio=campana.get('fecha_inicio', '2024-01-01'),
        fecha_fin=campana.get('fecha_fin', '2024-12-31'),
        meta_conversiones=campana.get('meta_conversiones', 100),
        presupuesto=float(campana.get('presupuesto', 0.0)),
        comision_porcentaje=float(campana.get('comision_porcentaje', 0.05)),
        marca=campana.get('marca', 'ALPES'),
        categoria=campana.get('categoria', 'MARKETING'),
        tags=campana.get('tags', []),
        afiliados=campana.get('afiliados', []),
        correlation_id=campana.get('correlation_id')
    )

    try:
        resultado = await handler_crear_campana.handle(comando)
        return {
            "success": True,
            "campaign_id": resultado.campaign_id,
            "message": f"Campaña '{comando.nombre}' creada exitosamente",
            "data": {
                "campaign_id": resultado.campaign_id,
                "nombre": comando.nombre,
                "presupuesto": comando.presupuesto,
                "meta_conversiones": comando.meta_conversiones,
                "afiliados_asignados": len(comando.afiliados),
                "comision_porcentaje": comando.comision_porcentaje,
                "fecha_creacion": resultado.creado_en,
                "eventos_generados": resultado.eventos_publicados,
                "correlation_id": resultado.correlation_id
            }
        }
    except Exception as e:
        logger.error(f"❌ Error creando campaña: {e}")
        return {"success": False, "error": str(e)}

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
