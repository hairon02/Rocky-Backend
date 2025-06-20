from datetime import datetime, timedelta, timezone
from typing import Union
from typing_extensions import Annotated
import jwt
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from schemas.user import User
from config.db import conn, Session
from models.user import users
# Configuración de JWT
#Clave secreta para firmar los tokens JWT
SECRET_KEY = "2378c6013ee00036936669c834304c098a0ffbe2f148859bc47aed4473a1164d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de Passlib (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

auth = APIRouter()

# Modelo de Pydantic que se usará en el endpoint de token para el response
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None


# Funciones de hashing
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    user = conn.execute(users.select().where(users.c.username == username)).first()
    if user:
        return user._mapping
    return None

def get_user_by_email(email: str):
    with Session() as session:
        result = session.execute(users.select().where(users.c.email == email)).first()
        if result:
            return dict(result._mapping)
    raise HTTPException(status_code=404, detail="Item not found")

def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user

# Creación de tokens JWT
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Obtener el usuario actual desde el token
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Verificar si el usuario está activo
async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)],):
    if 'activo' in current_user and not current_user['activo']:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

# Endpoint para el login
@auth.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@auth.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@auth.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user['username']}]