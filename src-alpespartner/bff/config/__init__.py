import os
from dataclasses import dataclass

def _env_url(name: str, default: str) -> str:
    # Acepta *_URL o *_ADDRESS
    return os.getenv(name) or os.getenv(name.replace("_URL", "_ADDRESS")) or default

@dataclass
class ConfiguracionBFF:
    """Configuración del BFF AlpesPartner"""
    
    # API Configuration
    host: str = "0.0.0.0"
    puerto: int = int(os.getenv("BFF_PORT", "8002"))
    
    # Microservices URLs
    url_campanias: str = os.getenv("CAMPANIAS_URL", "http://localhost:8001")
    url_sagas: str = os.getenv("SAGAS_URL", "http://localhost:8002")
    url_afiliados: str = os.getenv("AFILIADOS_URL", "http://localhost:8003")
    url_comisiones: str = os.getenv("COMISIONES_URL", "http://localhost:8004")
    url_conversiones: str = os.getenv("CONVERSIONES_URL", "http://localhost:8005")
    url_notificaciones: str = os.getenv("NOTIFICACIONES_URL", "http://localhost:8006")
    
    # HTTP Client Configuration
    timeout_segundos: int = int(os.getenv("HTTP_TIMEOUT", "30"))
    reintentos: int = int(os.getenv("HTTP_RETRIES", "3"))
    
    # Saga Configuration
    intervalo_polling_saga: int = int(os.getenv("SAGA_POLLING_INTERVAL", "5"))  # segundos
    timeout_saga_segundos: int = int(os.getenv("SAGA_TIMEOUT", "300"))  # 5 minutos
    
    # Pulsar Configuration
    #pulsar_host: str = os.getenv("PULSAR_HOST", "alpespartner-broker")
    pulsar_host: str = (
        os.getenv("BROKER_HOST")
        or os.getenv("PULSAR_HOST")
        or os.getenv("PULSAR_ADDRESS")
        or "alpespartner-broker"
    )


config = ConfiguracionBFF()