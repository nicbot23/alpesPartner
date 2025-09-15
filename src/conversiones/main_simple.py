"""
Microservicio de Conversiones - Versión Simplificada
"""
import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@app.on_event("startup")
async def startup_event():
    """Inicializar consumidores de eventos al arrancar la aplicación"""
    logger.info("🚀 Iniciando microservicio de Conversiones")
    logger.info("🔄 Configurando consumidores de eventos...")
    
    # Importar y configurar consumidores
    try:
        from .consumidores import iniciar_consumidores_background
        
        # Iniciar consumidores en background
        await iniciar_consumidores_background()
        
        logger.info("🎯 Conversiones listo para escuchar eventos de campañas")
        
    except Exception as e:
        logger.error(f"❌ Error iniciando consumidores: {e}")


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
