from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Date, Text, Float
from config.db import meta, engine

movimiento_financiero = Table("movimiento_financiero", meta, 
    Column("id", Integer, primary_key=True, autoincrement=True), 
    Column("usuario_id", Integer),
    Column("fecha", Date),
    Column("tipo", String(10)),
    Column("concepto", Text),
    Column("monto_presupuestado", Float),
    Column("monto_real", Float)) #meta para que sqlalchemy tenga mas propiedades de la tabla

meta.create_all(engine) # Una vez conectado a mysql, quiero que crees esta tabla

