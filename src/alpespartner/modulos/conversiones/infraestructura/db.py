"""
Configuración de base de datos separada para Conversiones
Implementa descentralización completa con su propia conexión
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuración separada para microservicio Conversiones
CONVERSIONES_DB_USERNAME = os.getenv('CONVERSIONES_DB_USERNAME', default="alpes")
CONVERSIONES_DB_PASSWORD = os.getenv('CONVERSIONES_DB_PASSWORD', default="alpes")
CONVERSIONES_DB_HOSTNAME = os.getenv('CONVERSIONES_DB_HOSTNAME', default="localhost")
CONVERSIONES_DB_PORT = os.getenv('CONVERSIONES_DB_PORT', default="3307")  # Puerto separado
CONVERSIONES_DB_NAME = os.getenv('CONVERSIONES_DB_NAME', default="alpes_conversiones")

# URL de conexión separada
CONVERSIONES_DATABASE_URL = os.getenv(
    'CONVERSIONES_DATABASE_URL',
    f'mysql+pymysql://{CONVERSIONES_DB_USERNAME}:{CONVERSIONES_DB_PASSWORD}@{CONVERSIONES_DB_HOSTNAME}:{CONVERSIONES_DB_PORT}/{CONVERSIONES_DB_NAME}'
)

# Engine y SessionLocal separados
conversiones_engine = create_engine(
    CONVERSIONES_DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    echo=os.getenv('SQL_DEBUG', 'false').lower() == 'true'
)

ConversionesSessionLocal = sessionmaker(
    bind=conversiones_engine,
    expire_on_commit=False,
    future=True
)


def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    try:
        from .modelos import ConversionesBase
        ConversionesBase.metadata.create_all(bind=conversiones_engine)
        print("✅ Base de datos de Conversiones inicializada correctamente")
    except Exception as e:
        print(f"❌ Error inicializando base de datos de Conversiones: {e}")
        raise


def get_conversiones_session():
    """Obtiene una sesión de base de datos para Conversiones."""
    session = ConversionesSessionLocal()
    try:
        yield session
    finally:
        session.close()