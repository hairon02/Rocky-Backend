# routers/user.py
from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db import get_db
from models.user import users
from schemas.user import User
from passlib.context import CryptContext
from starlette.status import HTTP_204_NO_CONTENT
from typing import List
from typing_extensions import Annotated
from auth import get_current_active_user, get_password_hash # Re-importar hash_password desde auth

user = APIRouter()

# pwd_context se mueve a auth.py, aquí solo usamos la función
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@user.get("/profile", response_model=User)
async def read_profile(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

@user.get("/users", response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    result = db.execute(users.select()).fetchall()
    users_list = [dict(row._asdict()) for row in result]
    return users_list

@user.post("/users", response_model=User)
def create_user(user: User, db: Session = Depends(get_db)):
    existing_user = db.execute(users.select().where(users.c.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")

    new_user = {"username": user.username, "nombre": user.nombre, "apellido": user.apellido, "email": user.email}
    new_user["password"] = get_password_hash(user.password) # Usamos la función de auth.py
    
    insert_statement = users.insert().values(new_user).returning(users)
    result = db.execute(insert_statement)
    db.commit()

    inserted_user = result.first()
    if inserted_user:
        return inserted_user._mapping
    
    raise HTTPException(status_code=500, detail="No se pudo crear el usuario.")

@user.get("/users/{id}", response_model=User)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.execute(users.select().where(users.c.id == id)).first()
    if user:
        return user._mapping
    raise HTTPException(status_code=404, detail="Item not found")

@user.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int, db: Session = Depends(get_db)):
    result = db.execute(users.delete().where(users.c.id == id))
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return Response(status_code=HTTP_204_NO_CONTENT)

@user.put("/users/{id}", response_model=User)
def update(id: int, user: User, db: Session = Depends(get_db)):
    update_values = {
        "username": user.username,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "email": user.email,
        "password": get_password_hash(user.password)
    }
    result = db.execute(users.update().values(update_values).where(users.c.id == id))
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_user = db.execute(users.select().where(users.c.id == id)).first()
    return updated_user._mapping

# El endpoint get_user_by_email ya está en auth.py, se puede eliminar de aquí si no se usa directamente.
# Si se necesita aquí, debe ser corregido así:
@user.get("/users/get_user_by_email/{email}", response_model=User)
def get_user_by_email_route(email: str, db: Session = Depends(get_db)):
    user_data = db.execute(users.select().where(users.c.email == email)).first()
    if user_data:
        return user_data._mapping
    raise HTTPException(status_code=404, detail="Item not found")