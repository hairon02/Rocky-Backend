from fastapi import FastAPI
from routers.movimiento_financiero import movimientoFinanciero

app = FastAPI(
    title="Rocky API",
    description="a REST API using python and mysql",
)

app.include_router(movimientoFinanciero, tags=["movimientoFinanciero"])
@app.get("/")
async def root():
    return "hola"