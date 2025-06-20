from sqlalchemy import create_engine, MetaData
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

load_dotenv()

database_url = os.getenv("DATABASE_URL")

# Si estamos en producción (la URL de Render existe), añadimos el parámetro sslmode.
if database_url and database_url.startswith("postgres://"):
    database_url = database_url + "?sslmode=require"
elif not database_url:
    # Lógica para desarrollo local (si aún quieres usar MySQL localmente)
    user = os.getenv("USER")
    password = os.getenv("PASSWORD", "")
    host = os.getenv("DATABASE_HOST")
    port = os.getenv("DATABASE_PORT")
    name = os.getenv("DATABASE_NAME")
    database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

engine = create_engine(database_url)

Session = sessionmaker(bind=engine)
meta = MetaData()
conn = engine.connect()