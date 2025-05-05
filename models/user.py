from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta, engine

users = Table("users", meta, Column("id", Integer, primary_key=True),
    Column("username", String(30)),
    Column("nombre", String(30)),
    Column("apellido", String(30)),
    Column("email", String(30), unique=True),
    Column("password", String(255))) #meta para que sqlalchemy tenga mas propiedades de la tabla

meta.create_all(engine)