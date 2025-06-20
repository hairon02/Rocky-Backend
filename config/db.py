# config/db.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine_args = {}

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    # Forzar el modo SSL 'require' para la conexión a Render
    engine_args['connect_args'] = {'sslmode': 'require'}
elif not database_url:
    # Si DATABASE_URL no está definida, construye la URL para MySQL
    user = os.getenv("USER")
    password = os.getenv("PASSWORD", "")
    host = os.getenv("DATABASE_HOST")
    port = os.getenv("DATABASE_PORT")
    name = os.getenv("DATABASE_NAME")
    database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

# Crear el motor de la base de datos con los argumentos
engine = create_engine(database_url, **engine_args)
Session = sessionmaker(bind=engine)
meta = MetaData()
conn = engine.connect()

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()