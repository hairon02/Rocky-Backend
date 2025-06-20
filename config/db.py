from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)

    if "sslmode=" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url += f"{separator}sslmode=require"

else:
    user = os.getenv("USER")
    password = os.getenv("PASSWORD", "")
    host = os.getenv("DATABASE_HOST")
    port = os.getenv("DATABASE_PORT")
    name = os.getenv("DATABASE_NAME")
    database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

# 👇 Aquí se usa el database_url ya corregido
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
meta = MetaData()
conn = engine.connect()
