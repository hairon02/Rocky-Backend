# config/db.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine_options = {}

# Asegurarse de que la URL sea compatible con SQLAlchemy y psycopg2
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    
    # ¡Esta es la parte crucial!
    # Forzamos explícitamente el modo SSL a través de los argumentos de conexión.
    # Esto tiene mayor precedencia y es más confiable que ponerlo en la URL.
    engine_options['connect_args'] = {
        'sslmode': 'require'
    }

# Crear el motor de la base de datos con las opciones explícitas
engine = create_engine(database_url, **engine_options)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
meta = MetaData()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()