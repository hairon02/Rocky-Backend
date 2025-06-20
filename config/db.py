# config/db.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine_options = {}

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    engine_options['connect_args'] = {
        'sslmode': 'require'
    }

# --- AÑADE ESTA LÍNEA ---
# Con esto, nos aseguramos de que cada conexión esté viva antes de usarla.
engine_options['pool_pre_ping'] = True
# -------------------------

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