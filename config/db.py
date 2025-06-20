from sqlalchemy import create_engine, MetaData
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Usar la variable DATABASE_URL que Render proporciona.
# Si no existe (para desarrollo local), construye la URL a partir de las otras variables.
database_url = os.getenv("DATABASE_URL")
if not database_url:
    # Lógica para desarrollo local (si aún quieres usar MySQL localmente)
    # Asegúrate de tener un .env local para esto.
    user = os.getenv("USER")
    password = os.getenv("PASSWORD", "") # Añade PASSWORD a tu .env local
    host = os.getenv("DATABASE_HOST")
    port = os.getenv("DATABASE_PORT")
    name = os.getenv("DATABASE_NAME")
    database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

engine = create_engine(database_url)

Session = sessionmaker(bind=engine)
meta = MetaData()
conn = engine.connect()