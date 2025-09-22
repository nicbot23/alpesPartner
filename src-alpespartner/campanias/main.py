from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings
from typing import Any

# API Routes
from campanias.api.v1.campanias import router as campanias_router
from campanias.api.v1.sagas import router as sagas_router

from campanias.consumidores import suscribirse_a_topico, suscribirse_eventos_saga

# Eventos que consume este microservicio (dominio)
from campanias.modulos.dominio.eventos import (
    CampaniaCreada, CampaniaActivada, AfiliadoAgregadoACampania, CampaniaEliminada
)

# Eventos de integración para Pulsar (con esquema Avro)
from campanias.modulos.infraestructura.schema.v1.eventos import (
    EventoCampaniaCreada, EventoCampaniaActivada, EventoAfiliadoAgregado
)

# Eventos de otros microservicios que nos interesan
from campanias.eventos import (
    EventoAfiliado, EventoComision, EventoConversion, EventoNotificacion
)

# Comandos que puede recibir (dominio)
from campanias.comandos import (
    ComandoCrearCampania as ComandoCrearCampaniaDominio, 
    ComandoActivarCampania as ComandoActivarCampaniaDominio, 
    ComandoAgregarAfiliado as ComandoAgregarAfiliadoDominio,
    ComandoLanzarCampaniaCompleta as ComandoLanzarCampaniaCompletaDominio, 
    ComandoCancelarSaga as ComandoCancelarSagaDominio
)

# Comandos de integración para Pulsar (con esquema Avro)
from campanias.modulos.infraestructura.schema.v1.comandos import (
    ComandoCrearCampania, ComandoActivarCampania, ComandoAgregarAfiliado,
    ComandoLanzarCampaniaCompleta, ComandoCancelarSaga
)

# Consumidores y despachadores
from campanias.consumidores import suscribirse_a_topico
from campanias.despachadores import Despachador
from campanias import utils

# ==========================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ==========================================

class Config(BaseSettings):
    APP_VERSION: str = "1.0.0"
    APP_NAME: str = "campanias AlpesPartner"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

settings = Config()

app_configs: dict[str, Any] = {
    "title": settings.APP_NAME,
    "version": settings.APP_VERSION,
    "description":"Microservicio de campanias para AlpesPartner. Monitoreo de Sagas en tiempo real 🎭",
    "docs_url": "/docs",
    "redoc_url": "/redoc"
}

# Lista global para manejar las tareas asíncronas
tasks: list[asyncio.Task] = []

# ==========================================
# GESTIÓN DEL CICLO DE VIDA DE LA APLICACIÓN
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación FastAPI.
    - Al inicio: crea suscripciones a tópicos de eventos
    - Al cierre: cancela todas las tareas asíncronas
    """
    
    print("🚀 Iniciando microservicio de campanias...")
    
    # ==========================================
    # SUSCRIPCIONES A EVENTOS DE DOMINIO PROPIOS
    # ==========================================
    
    # Eventos que publicamos nosotros para integración
    # Suscribe to each event topic individually, passing the correct schema class
    task_eventos_campania_creada = asyncio.create_task(
        suscribirse_a_topico(
            "eventos-campania-creada",
            "sub-eventos-campania-creada-integracion",
            EventoCampaniaCreada
        )
    )
    task_eventos_campania_activada = asyncio.create_task(
        suscribirse_a_topico(
            "eventos-campania-activada",
            "sub-eventos-campania-activada-integracion",
            EventoCampaniaActivada
        )
    )
    task_eventos_afiliado_agregado = asyncio.create_task(
        suscribirse_a_topico(
            "eventos-afiliado-agregado",
            "sub-eventos-afiliado-agregado-integracion",
            EventoAfiliadoAgregado
        )
    )
    
    # ==========================================
    # SUSCRIPCIONES A COMANDOS EXTERNOS
    # ==========================================
    
    # Comandos que otros servicios pueden enviarnos
    task_comandos_crear = asyncio.create_task(
        suscribirse_a_topico(
            "comando-crear-campania", 
            "sub-com-campanias-crear", 
            ComandoCrearCampania
        )
    )
    
    task_comandos_activar = asyncio.create_task(
        suscribirse_a_topico(
            "comando-activar-campania", 
            "sub-com-campanias-activar", 
            ComandoActivarCampania
        )
    )
    
    task_comandos_agregar_afiliado = asyncio.create_task(
        suscribirse_a_topico(
            "comando-agregar-afiliado-campania", 
            "sub-com-campanias-afiliado", 
            ComandoAgregarAfiliado
        )
    )

#nuevo
    task_lanzar_campania = asyncio.create_task(
        suscribirse_a_topico(
            topico="comando-lanzar-campania-completa",   # o el que uses
            suscripcion="campanias-bff-comandos",
            schema=ComandoLanzarCampaniaCompleta,        # lo que ya tienes
        )
    )
    
    # ==========================================
    # SUSCRIPCIONES A COMANDOS DEL BFF (SAGAS)
    # ==========================================
    
    # Comando principal del BFF para lanzar campanias completas
    task_comando_bff_lanzar = asyncio.create_task(
        suscribirse_a_topico(
            "comando-lanzar-campania-completa", 
            "sub-campanias-bff-lanzar", 
            ComandoLanzarCampaniaCompleta
        )
    )
    
    # Comando del BFF para cancelar sagas
    task_comando_bff_cancelar = asyncio.create_task(
        suscribirse_a_topico(
            "comando-cancelar-saga", 
            "sub-campanias-bff-cancelar", 
            ComandoCancelarSaga
        )
    )
    
    # ==========================================
    # SUSCRIPCIONES A EVENTOS DE OTROS MICROSERVICIOS
    # ==========================================
    
    # Eventos de afiliados (cuando se registran, actualizan, etc.)
    task_eventos_afiliados = asyncio.create_task(
        suscribirse_a_topico(
            "eventos-afiliado", 
            "sub-campanias-afiliados", 
            EventoAfiliado
        )
    )
    
    # Eventos de comisiones (cambios en estructura de comisiones)
    task_eventos_comisiones = asyncio.create_task(
        suscribirse_a_topico(
            "eventos-comision", 
            "sub-campanias-comisiones", 
            EventoComision
        )
    )
    
    # Eventos de conversiones (métricas de rendimiento)
    task_eventos_conversiones = asyncio.create_task(
        suscribirse_a_topico(
            "eventos-conversion", 
            "sub-campanias-conversiones", 
            EventoConversion
        )
    )
    
    # Eventos de notificaciones (confirmaciones de envío)
    task_eventos_notificaciones = asyncio.create_task(
        suscribirse_a_topico(
            "eventos-notificacion", 
            "sub-campanias-notificaciones", 
            EventoNotificacion
        )
    )

#NUEVO
    task_eventos_saga_campania = asyncio.create_task(
        suscribirse_eventos_saga(
            topico="eventos-saga-campania",
            suscripcion="campanias-saga-eventos"
        )
    )
    
    # Agregar todas las tareas a la lista global
    tasks.extend([
        task_eventos_campania_creada,
        task_eventos_campania_activada,
        task_eventos_afiliado_agregado,
        task_comandos_crear,
        task_comandos_activar,
        task_comandos_agregar_afiliado,
        task_comando_bff_lanzar,          # ← antes faltaban en la lista
        task_comando_bff_cancelar,
        task_eventos_afiliados,
        task_eventos_comisiones,
        task_eventos_conversiones,
        task_eventos_notificaciones,
        task_lanzar_campania,
        task_eventos_saga_campania
    ])

    asyncio.create_task(suscribirse_eventos_saga())
    
    print("✅ Suscripciones a eventos configuradas:")
    print("   - eventos-campania (eventos propios)")
    print("   - comando-crear-campania")
    print("   - comando-activar-campania") 
    print("   - comando-agregar-afiliado-campania")
    print("   - comando-lanzar-campania-completa")
    print("   - comando-cancelar-saga")
    print("   - eventos-afiliado")
    print("   - eventos-comision")
    print("   - eventos-conversion")
    print("   - eventos-notificacion")
    
    # ==========================================
    # YIELD: La aplicación está lista
    # ==========================================
    
    yield
    
    # ==========================================
    # LIMPIEZA AL CIERRE
    # ==========================================
    
    print("🛑 Cerrando microservicio de campanias...")
    
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    print("✅ Microservicio de campanias cerrado correctamente")

# ==========================================
# CREACIÓN DE LA APLICACIÓN FASTAPI
# ==========================================

app = FastAPI(lifespan=lifespan, **app_configs)

# ==========================================
# REGISTRO DE ROUTERS
# ==========================================

# Router principal de campanias
app.include_router(campanias_router, prefix="/api/v1", tags=["campanias"])

# Router de monitoreo de sagas
app.include_router(sagas_router, prefix="/api/v1", tags=["sagas"])

# ==========================================
# ENDPOINTS DE SALUD Y PRUEBAS
# ==========================================

@app.get("/health", tags=["health"])
async def health_check():
    """Health check del microservicio de campanias"""
    return {
        "servicio": "campanias",
        "estado": "activo",
        "version": settings.APP_VERSION,
        "descripcion": "Microservicio de gestión de campanias de marketing",
        "eventos_publicados": [
            "CampaniaCreada",
            "CampaniaActivada", 
            "AfiliadoAgregadoACampania",
            "CampaniaEliminada"
        ],
        "eventos_consumidos": [
            "EventoAfiliado",
            "EventoComision", 
            "EventoConversion",
            "EventoNotificacion"
        ],
        "comandos_soportados": [
            "ComandoCrearCampania",
            "ComandoActivarCampania",
            "ComandoAgregarAfiliado"
        ]
    }

@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "mensaje": "Microservicio de campanias AlpesPartner",
        "version": settings.APP_VERSION,
        "documentacion": "/docs",
        "health": "/health"
    }

# ==========================================
# ENDPOINTS DE PRUEBA (SOLO EN DESARROLLO)
# ==========================================

@app.get("/prueba-campania-creada", include_in_schema=False, tags=["testing"])
async def prueba_campania_creada() -> dict[str, str]:
    """Endpoint de prueba para simular evento CampaniaCreada"""
    
    if not settings.DEBUG:
        return {"error": "Endpoint solo disponible en modo DEBUG"}
    
    payload = CampaniaCreada(
        id="test-campania-123",
        nombre="Campaña de Prueba",
        tipo="promocional",
        canal_publicidad="web",
        objetivo="incrementar_ventas",
        fecha_creacion=utils.time_millis(),
        codigo_campana="CAMP-TEST123"
    )
    
    despachador = Despachador()
    despachador.publicar_mensaje(payload, "eventos-campania")
    
    return {
        "status": "ok",
        "mensaje": "Evento CampaniaCreada publicado",
        "evento": "CampaniaCreada",
        "id_campania": "test-campania-123"
    }

@app.get("/prueba-campania-activada", include_in_schema=False, tags=["testing"])
async def prueba_campania_activada() -> dict[str, str]:
    """Endpoint de prueba para simular evento CampaniaActivada"""
    
    if not settings.DEBUG:
        return {"error": "Endpoint solo disponible en modo DEBUG"}
    
    payload = CampaniaActivada(
        id="test-campania-123",
        fecha_activacion=utils.time_millis(),
        canal_publicidad="web"
    )
    
    despachador = Despachador()
    despachador.publicar_mensaje(payload, "eventos-campania")
    
    return {
        "status": "ok",
        "mensaje": "Evento CampaniaActivada publicado",
        "evento": "CampaniaActivada",
        "id_campania": "test-campania-123"
    }

# ==========================================
# CONFIGURACIÓN PARA EJECUCIÓN DIRECTA
# ==========================================

if __name__ == "__main__":
    import uvicorn
    
    print(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📡 Servidor en http://{settings.HOST}:{settings.PORT}")
    print(f"📚 Documentación en http://{settings.HOST}:{settings.PORT}/docs")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )