from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def configurar_api() -> FastAPI:
    """Configura la aplicación FastAPI del BFF"""
    
    app = FastAPI(
        title="AlpesPartner BFF",
        description="Backend For Frontend - Simple orquestador para campanias",
        version="1.0.0",
        docs_url="/bff/docs",
        redoc_url="/bff/redoc"
    )
    
    # CORS middleware para permitir requests desde frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, especificar dominios
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app