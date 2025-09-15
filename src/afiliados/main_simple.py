"""
API Simple para Afiliados - Demostración
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
