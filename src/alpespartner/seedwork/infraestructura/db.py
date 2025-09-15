import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
DATABASE_URL=os.getenv('DATABASE_URL','mysql+pymysql://alpes:alpes@localhost:3306/alpes')
engine=create_engine(DATABASE_URL,pool_pre_ping=True,future=True)
SessionLocal=sessionmaker(bind=engine,expire_on_commit=False,future=True)
