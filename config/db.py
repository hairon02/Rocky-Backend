from sqlalchemy import create_engine, MetaData
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine("mysql+pymysql://" + os.getenv("USER") + ":@" + os.getenv("DATABASE_HOST") + ":" + os.getenv("DATABASE_PORT") + "/" + os.getenv("DATABASE_NAME")) #necesita el url, usuario, contra, servidor, bd, puerto
meta = MetaData() 
conn = engine.connect()