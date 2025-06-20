# config/db.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# La URL de la base de datos se toma directamente de las variables de entorno.
# Asegúrate de que en Render esta URL ya incluye ?sslmode=require al final.
database_url = os.getenv("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    # Reemplaza el dialecto para que SQLAlchemy use psycopg2
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
meta = MetaData()

# Función para obtener una sesión de base de datos por petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()