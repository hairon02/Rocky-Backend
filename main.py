from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.movimiento_financiero import movimientoFinanciero
from routers.user import user
from auth import auth
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
app.include_router(user, tags=["Users"])
app.include_router(auth, tags=["Auth"])

@app.get("/")
async def root():
    return "hola"