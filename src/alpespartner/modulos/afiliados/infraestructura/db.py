"""
Configuración de base de datos para el microservicio Afiliados
Base de datos separada e independiente
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from .modelos import AfiliadosBase


# Configuración específica para Afiliados
AFILIADOS_DB_CONFIG = {
    'host': os.getenv('AFILIADOS_DB_HOST', 'localhost'),
    'port': os.getenv('AFILIADOS_DB_PORT', '3308'),  # Puerto diferente
    'user': os.getenv('AFILIADOS_DB_USER', 'afiliados_user'),
    'password': os.getenv('AFILIADOS_DB_PASSWORD', 'afiliados_pass'),
    'database': os.getenv('AFILIADOS_DB_NAME', 'afiliados_db')
}

# Construcción de URL de conexión
AFILIADOS_DATABASE_URL = (
    f"mysql+pymysql://{AFILIADOS_DB_CONFIG['user']}:"
    f"{AFILIADOS_DB_CONFIG['password']}@"
    f"{AFILIADOS_DB_CONFIG['host']}:"
    f"{AFILIADOS_DB_CONFIG['port']}/"
    f"{AFILIADOS_DB_CONFIG['database']}"
    f"?charset=utf8mb4"
)

# Engine con configuración optimizada
afiliados_engine = create_engine(
    AFILIADOS_DATABASE_URL,
    echo=os.getenv('AFILIADOS_DB_ECHO', 'False').lower() == 'true',
    pool_size=int(os.getenv('AFILIADOS_DB_POOL_SIZE', '10')),
    max_overflow=int(os.getenv('AFILIADOS_DB_MAX_OVERFLOW', '20')),
    pool_pre_ping=True,
    pool_recycle=3600,  # Reciclar conexiones cada hora
    connect_args={
        "charset": "utf8mb4",
        "connect_timeout": 30,
        "read_timeout": 30,
        "write_timeout": 30
    }
)

# Session factory para Afiliados
AfiliadosSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=afiliados_engine
)


def crear_tablas_afiliados():
    """Crea todas las tablas del esquema de Afiliados."""
    AfiliadosBase.metadata.create_all(bind=afiliados_engine)


def obtener_session_afiliados():
    """
    Dependency para obtener una sesión de base de datos de Afiliados.
    
    Yields:
        Session: Sesión de SQLAlchemy para Afiliados
    """
    session = AfiliadosSessionLocal()
    try:
        yield session
    finally:
        session.close()


class AfiliadosDBManager:
    """Manager para operaciones de base de datos de Afiliados."""
    
    def __init__(self):
        self.engine = afiliados_engine
        self.session_factory = AfiliadosSessionLocal
    
    def crear_session(self):
        """Crea una nueva sesión de base de datos."""
        return self.session_factory()
    
    def inicializar_esquema(self):
        """Inicializa el esquema de base de datos."""
        crear_tablas_afiliados()
    
    def verificar_conexion(self) -> bool:
        """
        Verifica si la conexión a la base de datos está disponible.
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"Error conectando a base de datos Afiliados: {e}")
            return False
    
    def obtener_info_conexion(self) -> dict:
        """
        Obtiene información sobre la configuración de conexión.
        
        Returns:
            dict: Información de la conexión (sin credenciales)
        """
        return {
            'host': AFILIADOS_DB_CONFIG['host'],
            'port': AFILIADOS_DB_CONFIG['port'],
            'database': AFILIADOS_DB_CONFIG['database'],
            'user': AFILIADOS_DB_CONFIG['user'],
            'url_safe': f"mysql://{AFILIADOS_DB_CONFIG['host']}:{AFILIADOS_DB_CONFIG['port']}/{AFILIADOS_DB_CONFIG['database']}"
        }


# Instancia global del manager
afiliados_db_manager = AfiliadosDBManager()