from fastapi import APIRouter, Response, status, HTTPException, Query
from config.db import conn, Session
from models.categoria import categoria
from schemas.categoria import Categoria
from starlette.status import HTTP_204_NO_CONTENT
from datetime import date
from typing import Optional
from sqlalchemy import asc


categoria_router = APIRouter()


@categoria_router.get("/categoria", response_model=list[Categoria])
def get_categorias():
    with Session() as session:
        result = session.execute(categoria.select()).fetchall()
        categorias_list = [row._mapping for row in result]
        return categorias_list

@categoria_router.post("/categoria", response_model=Categoria)
def create_categoria(cat: Categoria):
    nuevo = {
        "categoria": cat.categoria
    }
    result = conn.execute (categoria.insert().values(nuevo))
    conn.commit()

    categoriaOne = conn.execute(categoria.select().where(categoria.c.id == result.lastrowid)).first()._mapping
    return categoriaOne

@categoria_router.get("/categoria/{id}", response_model=Categoria)
def get_UnoCategoria(id:int):
    result = conn.execute(categoria.select().where(categoria.c.id == id)).first()
    if result:
        return result._mapping
    raise HTTPException(status_code = 404, detail= "Categoria no encontrado")