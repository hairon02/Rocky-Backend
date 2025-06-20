from fastapi import APIRouter, Response, status, HTTPException, Query, Depends
from config.db import conn, Session, get_db
from models.categoria import categoria
from schemas.categoria import Categoria
from starlette.status import HTTP_204_NO_CONTENT
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session as ss
from sqlalchemy import asc


categoria_router = APIRouter()


@categoria_router.get("/categoria", response_model=list[Categoria])
def get_categorias():
    with Session() as session:
        result = session.execute(categoria.select()).fetchall()
        categorias_list = [row._mapping for row in result]
        return categorias_list


@categoria_router.post("/categoria", response_model=Categoria)
def create_categoria(cat: Categoria, db: ss = Depends(get_db)):
    nuevo = {"categoria": cat.categoria}
    result = db.execute(categoria.insert().values(nuevo))
    db.commit()

    inserted_id = result.inserted_primary_key[0]

    categoria_one = db.execute(
        categoria.select().where(categoria.c.id == inserted_id)
    ).first()

    return categoria_one._mapping

@categoria_router.get("/categoria/{id}", response_model=Categoria)
def get_UnoCategoria(id:int):
    result = conn.execute(categoria.select().where(categoria.c.id == id)).first()
    if result:
        return result._mapping
    raise HTTPException(status_code = 404, detail= "Categoria no encontrado")