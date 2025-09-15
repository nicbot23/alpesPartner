from pydantic_settings import BaseSettings
from typing import Any

class Config(BaseSettings):
    APP_VERSION: str = "1"
    APP_NAME: str = "Conversiones AlpesPartner"
    DATABASE_URL: str = "mysql+pymysql://alpes:alpes@mysql-conversiones:3306/alpes_conversiones"
    PULSAR_URL: str = "pulsar://pulsar:6650"
    
    # Atributos adicionales necesarios
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Atributos para Pulsar
    pulsar_host: str = "pulsar"
    pulsar_port: int = 6650
    
    class Config:
        env_file = ".env"

settings = Config()

app_configs: dict[str, Any] = {
    "title": settings.APP_NAME,
    "version": settings.APP_VERSION,
    "description": "Microservicio de Conversiones - AlpesPartner"
}