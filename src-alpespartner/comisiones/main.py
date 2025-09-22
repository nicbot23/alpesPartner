from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(
    title="Comisiones Microservice",
    description="Microservicio de gestión de comisiones para AlpesPartner",
    version="1.0.0"
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
    return {"message": "Comisiones Microservice", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "comisiones"}

@app.get("/comisiones")
async def listar_comisiones():
    return {"comisiones": [], "message": "Lista de comisiones"}

if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
