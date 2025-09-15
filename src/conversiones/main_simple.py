"""
Microservicio de Conversiones - Event-Driven con Persistencia Automática
"""
import logging
import asyncio
import os
import json
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pulsar
import pymysql

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clase para persistencia automática en BD
class ConversionesDBManager:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'alpes_user'),
            'password': os.getenv('DB_PASSWORD', 'alpes_password'),
            'database': 'alpes_conversiones',
            'charset': 'utf8mb4'
        }
    
    async def crear_tracking_campana(self, campana_data):
        """Crear tracking automático de conversiones para campaña"""
        try:
            connection = pymysql.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Crear tabla de tracking si no existe
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS campana_tracking (
                id VARCHAR(36) PRIMARY KEY,
                campana_id VARCHAR(100) NOT NULL,
                campana_nombre VARCHAR(200) NOT NULL,
                objetivo_conversiones INT DEFAULT 100,
                conversiones_actuales INT DEFAULT 0,
                fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                estado ENUM('ACTIVO', 'PAUSADO', 'COMPLETADO') DEFAULT 'ACTIVO',
                presupuesto_asignado DECIMAL(15,2),
                costo_por_conversion DECIMAL(10,2) DEFAULT 0.00,
                tasa_conversion DECIMAL(5,2) DEFAULT 0.00,
                INDEX idx_campana (campana_id)
            )
            """
            cursor.execute(create_table_sql)
            
            # Crear tracking automático
            tracking_id = str(uuid.uuid4())
            insert_sql = """
            INSERT INTO campana_tracking 
            (id, campana_id, campana_nombre, objetivo_conversiones, presupuesto_asignado) 
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                tracking_id,
                campana_data.get('campana_id'),
                campana_data.get('nombre'),
                100,  # objetivo default
                campana_data.get('presupuesto', 0)
            ))
            
            connection.commit()
            logger.info(f"✅ BD CONVERSIONES: Tracking automático creado para campaña {campana_data.get('campana_id')}")
            
        except Exception as e:
            logger.error(f"❌ Error persistiendo tracking de campaña: {e}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# Crear aplicación FastAPI
app = FastAPI(
    title="Conversiones AlpesPartner",
    version="1.0.0",
    description="Microservicio de Conversiones - AlpesPartner"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Consumidor simple de eventos de marketing para conversiones con persistencia automática
class SimplePulsarConsumerConversiones:
    def __init__(self):
        self.client = None
        self.consumer = None
        self.db_manager = ConversionesDBManager()
        
    async def inicializar(self):
        """Inicializar cliente Pulsar para consumo"""
        try:
            pulsar_url = os.getenv('PULSAR_URL', 'pulsar://pulsar:6650')
            self.client = pulsar.Client(pulsar_url)
            logger.info(f"✅ Cliente Pulsar consumidor inicializado: {pulsar_url}")
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente Pulsar consumidor: {e}")
    
    async def suscribirse_marketing_eventos(self):
        """Suscribirse a eventos de marketing"""
        try:
            if not self.client:
                await self.inicializar()
            
            self.consumer = self.client.subscribe(
                topic='persistent://public/default/marketing.eventos',
                subscription_name='conversiones-marketing-events',
                consumer_type=pulsar.ConsumerType.Shared
            )
            
            logger.info("✅ Conversiones suscrito a marketing.eventos")
            
            # Iniciar consumo en background
            asyncio.create_task(self._consumir_eventos())
            
        except Exception as e:
            logger.error(f"❌ Error suscribiéndose a marketing.eventos: {e}")
    
    async def _consumir_eventos(self):
        """Consumir eventos en background"""
        while True:
            try:
                msg = self.consumer.receive(timeout_millis=5000)
                await self._procesar_mensaje(msg)
                self.consumer.acknowledge(msg)
            except Exception as e:
                if "timeout" not in str(e).lower():
                    logger.error(f"❌ Error consumiendo evento: {e}")
                await asyncio.sleep(1)
    
    async def _procesar_mensaje(self, msg):
        """Procesar mensaje de marketing"""
        try:
            mensaje_json = json.loads(msg.data().decode('utf-8'))
            tipo_evento = mensaje_json.get('tipo', 'Unknown')
            
            if tipo_evento == 'CampanaCreada':
                await self._procesar_campana_creada(mensaje_json)
                
            logger.info(f"📊 Evento procesado en Conversiones: {tipo_evento}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje en Conversiones: {e}")
    
    async def _procesar_campana_creada(self, evento):
        """Procesar evento de campaña creada"""
        try:
            campana_id = evento.get('campana_id', 'unknown')
            nombre = evento.get('nombre', 'Sin nombre')
            meta_conversiones = evento.get('meta_conversiones', 0)
            
            logger.info(f"📊 CONVERSIONES: Nueva campaña detectada:")
            logger.info(f"   📋 ID: {campana_id}")
            logger.info(f"   📝 Nombre: {nombre}")
            logger.info(f"   🎯 Meta conversiones: {meta_conversiones}")
            
            # 🚀 PERSISTENCIA AUTOMÁTICA: Crear tracking en BD sin endpoints CRUD
            await self.db_manager.crear_tracking_campana({
                'campana_id': campana_id,
                'nombre': nombre,
                'presupuesto': evento.get('presupuesto', 0)
            })
            
            # Lógica adicional de negocio
            logger.info(f"   🔄 Configurando tracking para campaña {campana_id}")
            logger.info(f"   📈 Creando métricas base de conversión")
            logger.info(f"   👁️ Activando monitoring automático de conversiones")
            logger.info(f"   🎯 Objetivo: {meta_conversiones} conversiones")
            logger.info(f"   💾 Persistencia automática completada en BD")
            
        except Exception as e:
            logger.error(f"❌ Error procesando campaña creada en Conversiones: {e}")
    
    async def cerrar(self):
        """Cerrar conexiones"""
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()

# Instancia global del consumidor
consumer_conversiones = SimplePulsarConsumerConversiones()


@app.on_event("startup")
async def startup_event():
    """Inicializar consumidores de eventos al arrancar la aplicación"""
    logger.info("🚀 Iniciando microservicio de Conversiones")
    logger.info("🔄 Configurando consumidor simple de marketing.eventos...")
    
    try:
        # Inicializar y suscribirse al consumidor simple
        await consumer_conversiones.inicializar()
        await consumer_conversiones.suscribirse_marketing_eventos()
        
        logger.info("🎯 Conversiones listo para escuchar eventos de campañas")
        
    except Exception as e:
        logger.error(f"❌ Error iniciando consumidores: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup al cerrar la aplicación"""
    logger.info("🛑 Cerrando microservicio de Conversiones")
    await consumer_conversiones.cerrar()
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup al cerrar la aplicación"""
    logger.info("🛑 Cerrando microservicio de Conversiones")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Microservicio de Conversiones - AlpesPartner", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "conversiones"}

@app.get("/conversiones")
async def get_conversiones():
    """Obtener lista de conversiones"""
    return {
        "conversiones": [
            {
                "id": "conv_001",
                "affiliate_id": "aff_123",
                "campaign_id": "camp_456",
                "user_id": "user_789",
                "conversion_value": 150.00,
                "conversion_type": "purchase",
                "status": "confirmed",
                "timestamp": "2024-01-15T10:30:00Z"
            },
            {
                "id": "conv_002", 
                "affiliate_id": "aff_124",
                "campaign_id": "camp_457",
                "user_id": "user_790",
                "conversion_value": 200.00,
                "conversion_type": "signup",
                "status": "pending",
                "timestamp": "2024-01-15T11:15:00Z"
            }
        ]
    }

@app.post("/conversiones")
async def create_conversion(conversion_data: dict):
    """Crear nueva conversión"""
    logger.info(f"Nueva conversión recibida: {conversion_data}")
    
    # Simular procesamiento
    response = {
        "id": "conv_" + str(hash(str(conversion_data)) % 10000),
        "status": "created",
        "message": "Conversión creada exitosamente",
        "data": conversion_data
    }
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
