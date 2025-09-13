"""
Inicialización del módulo de infraestructura de Afiliados
"""

from .modelos import AfiliadosBase, AfiliadoDTO, ReferenciaDTO, OutboxAfiliadosDTO
from .db import (
    afiliados_engine, AfiliadosSessionLocal, crear_tablas_afiliados,
    obtener_session_afiliados, AfiliadosDBManager, afiliados_db_manager,
    AFILIADOS_DATABASE_URL, AFILIADOS_DB_CONFIG
)
from .mapeadores import (
    MapeadorAfiliado, MapeadorReferencia, MapeadorOutboxAfiliados
)
from .repositorios import RepositorioAfiliadosSQLAlchemy

__all__ = [
    # Modelos
    'AfiliadosBase',
    'AfiliadoDTO',
    'ReferenciaDTO', 
    'OutboxAfiliadosDTO',
    
    # Base de datos
    'afiliados_engine',
    'AfiliadosSessionLocal',
    'crear_tablas_afiliados',
    'obtener_session_afiliados',
    'AfiliadosDBManager',
    'afiliados_db_manager',
    'AFILIADOS_DATABASE_URL',
    'AFILIADOS_DB_CONFIG',
    
    # Mapeadores
    'MapeadorAfiliado',
    'MapeadorReferencia',
    'MapeadorOutboxAfiliados',
    
    # Repositorios
    'RepositorioAfiliadosSQLAlchemy'
]