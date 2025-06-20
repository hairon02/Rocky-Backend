from fastapi import APIRouter, Response, status, HTTPException, Depends
from config.db import conn, Session
from models.user import users
from schemas.user import User
from passlib.context import CryptContext
from starlette.status import HTTP_204_NO_CONTENT
from typing import List
from typing_extensions import Annotated
from auth import get_current_active_user

user = APIRouter()  # definir subrutas

# Configuración de bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Funciones de hashing
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


@user.get("/profile", response_model=User)
async def read_profile(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@user.get("/users", response_model=List[User])  # Para una peticion get
def get_users():
    result = conn.execute(users.select()).fetchall()
    users_list = [dict(row._asdict()) for row in result]
    return users_list


@user.post("/users", response_model=User)  # PAra una peticion get
def create_user(user: User):
    existing_user = conn.execute(users.select().where(users.c.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")

    new_user = {"username": user.username, "nombre": user.nombre, "apellido": user.apellido, "email": user.email}  # uso de diccionarios
    new_user["password"] = hash_password(user.password)
    
    # Modificación clave: Usar returning() para obtener la fila insertada directamente
    insert_statement = users.insert().values(new_user).returning(users)
    result = conn.execute(insert_statement)
    conn.commit()

    # El resultado ya es la fila insertada, no necesitamos otra consulta
    inserted_user = result.first()
    if inserted_user:
        return inserted_user._mapping
    
    # Fallback por si algo extremadamente raro ocurre
    raise HTTPException(status_code=500, detail="No se pudo crear el usuario.")


@user.get("/users/{id}", response_model=User)
def get_user(id: int):
    user = conn.execute(users.select().where(users.c.id == id)).first()
    if user:
        user_dict = dict(user._asdict())
        return user_dict
    raise HTTPException(status_code=404, detail="Item not found")


@user.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int):
    result = conn.execute(users.delete().where(users.c.id == id))
    conn.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


@user.put("/users/{id}", response_model=User)
def update(id: int, user: User):
    result = conn.execute(
        users.update().values(username=user.username, nombre=user.nombre, apellido=user.apellido, email=user.email,
                              password=hash_password(user.password)).where(users.c.id == id))
    conn.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    user = conn.execute(users.select().where(users.c.id == id)).first()
    user_dict = dict(user._asdict())
    return user_dict


@user.get("/users/get_user_by_name/{Name}{Apellido}", response_model=User)
def get_user_by_name(name: str, apellido: str):
    user = conn.execute(users.select().where(users.c.nombre == name, users.c.apellido == apellido)).first()
    if user:
        user_dict = dict(user._asdict())
        return user_dict

    raise HTTPException(status_code=404, detail="Item not found")


@user.get("/users/get_user_by_username/{Username}", response_model=User)
def get_user_by_username(user: str):
    user = conn.execute(users.select().where(users.c.username == user)).first()
    if user:
        user_dict = dict(user._asdict())
        return user_dict

    raise HTTPException(status_code=404, detail="Item not found")

@user.get("/users/get_user_by_email/{Email}", response_model=User)
def get_user_by_email(email: str):
    with Session() as session:
        result = session.execute(users.select().where(users.c.email == email)).first()
        if result:
            user_dict = dict(result._mapping)
            return user_dict

    raise HTTPException(status_code=404, detail="Item not found")
