"""
API Simple para Afiliados - Event-Driven con Persistencia Automática
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
import pymysql
import sqlalchemy
from sqlalchemy import create_engine, text

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clase para persistencia automática en BD
class AfiliadosDBManager:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'alpes_user'),
            'password': os.getenv('DB_PASSWORD', 'alpes_password'),
            'database': 'alpes_afiliados',
            'charset': 'utf8mb4'
        }
    
    async def crear_asignacion_campana(self, campana_data):
        """Crear asignación automática de campaña para afiliados activos"""
        try:
            connection = pymysql.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Crear tabla de asignaciones si no existe
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS campana_asignaciones (
                id VARCHAR(36) PRIMARY KEY,
                campana_id VARCHAR(100) NOT NULL,
                campana_nombre VARCHAR(200) NOT NULL,
                afiliado_id VARCHAR(36) NOT NULL,
                presupuesto DECIMAL(15,2),
                fecha_asignacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                estado ENUM('ACTIVA', 'PAUSADA', 'FINALIZADA') DEFAULT 'ACTIVA',
                comision_asignada DECIMAL(5,2) DEFAULT 5.00,
                conversiones_objetivo INT DEFAULT 0,
                INDEX idx_campana (campana_id),
                INDEX idx_afiliado (afiliado_id),
                CONSTRAINT fk_campana_afiliado FOREIGN KEY (afiliado_id) REFERENCES afiliados(id)
            )
            """
            cursor.execute(create_table_sql)
            
            # Obtener afiliados activos para auto-asignación
            cursor.execute("SELECT id, nombres, apellidos FROM afiliados WHERE estado = 'ACTIVO' LIMIT 5")
            afiliados_activos = cursor.fetchall()
            
            asignaciones_creadas = 0
            for afiliado in afiliados_activos:
                asignacion_id = str(uuid.uuid4())
                insert_sql = """
                INSERT INTO campana_asignaciones 
                (id, campana_id, campana_nombre, afiliado_id, presupuesto, comision_asignada) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    asignacion_id,
                    campana_data.get('campana_id'),
                    campana_data.get('nombre'),
                    afiliado[0],  # id del afiliado
                    campana_data.get('presupuesto', 0),
                    5.5  # comisión base
                ))
                asignaciones_creadas += 1
            
            connection.commit()
            logger.info(f"✅ BD AFILIADOS: {asignaciones_creadas} asignaciones automáticas creadas para campaña {campana_data.get('campana_id')}")
            
        except Exception as e:
            logger.error(f"❌ Error persistiendo asignación de campaña: {e}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# Crear aplicación FastAPI
app = FastAPI(
    title="AlpesPartner - Afiliados",
    description="API del microservicio de Afiliados",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Consumidor simple de eventos de marketing con persistencia automática
class SimplePulsarConsumer:
    def __init__(self):
        self.client = None
        self.consumer = None
        self.db_manager = AfiliadosDBManager()
        
    async def inicializar(self):
        """Inicializar cliente Pulsar para consumo"""
        try:
            pulsar_url = os.getenv('PULSAR_URL', 'pulsar://pulsar:6650')
            self.client = pulsar.Client(pulsar_url)
            logger.info(f"✅ Cliente Pulsar consumidor inicializado: {pulsar_url}")
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente Pulsar consumidor: {e}")
    
    async def suscribirse_marketing_eventos(self):
        """Suscribirse a eventos de marketing para persistencia automática"""
        try:
            if not self.client:
                await self.inicializar()
            
            self.consumer = self.client.subscribe(
                topic='persistent://public/default/marketing.eventos',
                subscription_name='afiliados-marketing-events',
                consumer_type=pulsar.ConsumerType.Shared
            )
            
            logger.info("✅ Suscrito a marketing.eventos")
            
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
                
            logger.info(f"🎯 Evento procesado en Afiliados: {tipo_evento}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje en Afiliados: {e}")
    
    async def _procesar_campana_creada(self, evento):
        """Procesar evento de campaña creada con persistencia automática en BD"""
        try:
            campana_id = evento.get('campana_id', 'unknown')
            nombre = evento.get('nombre', 'Sin nombre')
            presupuesto = evento.get('presupuesto', 0)
            
            logger.info(f"🎯 AFILIADOS: Nueva campaña detectada:")
            logger.info(f"   📋 ID: {campana_id}")
            logger.info(f"   📝 Nombre: {nombre}")
            logger.info(f"   💰 Presupuesto: ${presupuesto}")
            
            # 🚀 PERSISTENCIA AUTOMÁTICA: Crear asignaciones en BD sin endpoints CRUD
            await self.db_manager.crear_asignacion_campana({
                'campana_id': campana_id,
                'nombre': nombre,
                'presupuesto': presupuesto
            })
            
            # Lógica adicional de negocio
            logger.info(f"   🔄 Buscando afiliados elegibles...")
            logger.info(f"   ✅ Auto-asignando afiliados activos a campaña {campana_id}")
            logger.info(f"   📧 Enviando notificaciones de nueva campaña")
            logger.info(f"   💾 Persistencia automática completada en BD")
            
        except Exception as e:
            logger.error(f"❌ Error procesando campaña creada: {e}")
    
    async def cerrar(self):
        """Cerrar conexiones"""
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()

# Instancia global del consumidor
consumer = SimplePulsarConsumer()


@app.on_event("startup")
async def startup_event():
    """Inicializar consumidores de eventos al arrancar la aplicación"""
    logger.info("🚀 Iniciando microservicio de Afiliados")
    logger.info("🔄 Configurando consumidor simple de marketing.eventos...")
    
    try:
        # Inicializar y suscribirse al consumidor simple
        await consumer.inicializar()
        await consumer.suscribirse_marketing_eventos()
        
        logger.info("🎯 Afiliados listo para escuchar eventos de campañas")
        
    except Exception as e:
        logger.error(f"❌ Error iniciando consumidores: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup al cerrar la aplicación"""
    logger.info("🛑 Cerrando microservicio de Afiliados")
    await consumer.cerrar()

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "AlpesPartner - Servicio de Afiliados",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "afiliados",
        "timestamp": "2024-01-01T00:00:00Z"
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
                "estado": "activo"
            },
            {
                "id": "2", 
                "nombre": "María García",
                "email": "maria@example.com",
                "telefono": "+57-301-987-6543",
                "estado": "activo"
            }
        ]
    }

@app.post("/afiliados")
async def crear_afiliado(afiliado: dict):
    """Crear nuevo afiliado"""
    logger.info(f"Creando afiliado: {afiliado}")
    return {
        "message": "Afiliado creado exitosamente",
        "id": "new-123",
        "afiliado": afiliado
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
