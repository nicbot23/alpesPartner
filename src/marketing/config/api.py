import os
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "marketing")
    db_user: str = os.getenv("DB_USER", "admin")
    db_password: str = os.getenv("DB_PASSWORD", "admin123")
    
    pulsar_host: str = os.getenv("PULSAR_HOST", "localhost")
    pulsar_port: int = int(os.getenv("PULSAR_PORT", "6650"))
    
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8003"))


config = Config()