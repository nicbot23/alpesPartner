import os
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # Configuración BD principal (dominio de campanias)
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "campanias")
    db_user: str = os.getenv("DB_USER", "campanias")
    db_password: str = os.getenv("DB_PASSWORD", "campanias123")
    
    # Configuración BD sagas (orquestación y logs)
    sagas_db_host: str = os.getenv("SAGAS_DB_HOST", "localhost")
    sagas_db_port: int = int(os.getenv("SAGAS_DB_PORT", "3306"))
    sagas_db_name: str = os.getenv("SAGAS_DB_NAME", "sagas")
    sagas_db_user: str = os.getenv("SAGAS_DB_USER", "sagas")
    sagas_db_password: str = os.getenv("SAGAS_DB_PASSWORD", "sagas123")
    
    # Configuración de entorno para sagas
    sagas_storage_type: str = os.getenv("SAGAS_STORAGE_TYPE", "mysql")  # mysql | sqlite
    
    pulsar_host: str = os.getenv("PULSAR_HOST", "localhost")
    pulsar_port: int = int(os.getenv("PULSAR_PORT", "6650"))
    
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))


config = Config()