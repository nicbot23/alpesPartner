from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .api import config

# ==========================================
# CONFIGURACIÓN BD PRINCIPAL (DOMINIO campanias)
# ==========================================

DATABASE_URL = f"mysql+pymysql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = MetaData()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# CONFIGURACIÓN BD SAGAS (ORQUESTACIÓN)
# ==========================================

SAGAS_DATABASE_URL = f"mysql+pymysql://{config.sagas_db_user}:{config.sagas_db_password}@{config.sagas_db_host}:{config.sagas_db_port}/{config.sagas_db_name}"

sagas_engine = create_engine(SAGAS_DATABASE_URL)
SagasSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sagas_engine)

SagasBase = declarative_base()
sagas_metadata = MetaData()

def get_sagas_db():
    db = SagasSessionLocal()
    try:
        yield db
    finally:
        db.close()