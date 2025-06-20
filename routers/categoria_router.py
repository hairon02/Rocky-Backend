# routers/categoria_router.py
from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db import get_db
from models.categoria import categoria
from schemas.categoria import Categoria
from typing import List

categoria_router = APIRouter()

@categoria_router.get("/categoria", response_model=List[Categoria])
def get_categorias(db: Session = Depends(get_db)):
    result = db.execute(categoria.select()).fetchall()
    categorias_list = [row._mapping for row in result]
    return categorias_list

@categoria_router.post("/categoria", response_model=Categoria)
def create_categoria(cat: Categoria, db: Session = Depends(get_db)):
    nuevo = {"categoria": cat.categoria}
    result = db.execute(categoria.insert().values(nuevo).returning(categoria))
    db.commit()

    inserted_categoria = result.first()
    if not inserted_categoria:
        raise HTTPException(status_code=500, detail="No se pudo crear la categoría")

    return inserted_categoria._mapping

@categoria_router.get("/categoria/{id}", response_model=Categoria)
def get_UnoCategoria(id: int, db: Session = Depends(get_db)):
    result = db.execute(categoria.select().where(categoria.c.id == id)).first()
    if result:
        return result._mapping
    raise HTTPException(status_code=404, detail="Categoria no encontrada")