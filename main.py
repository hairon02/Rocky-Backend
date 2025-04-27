from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.movimiento_financiero import movimientoFinanciero

app = FastAPI(
    title="Rocky API",
    description="a REST API using python and mysql",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción pon solo ["http://localhost:5173"] o tu dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movimientoFinanciero, tags=["movimientoFinanciero"])
@app.get("/")
async def root():
    return "hola"