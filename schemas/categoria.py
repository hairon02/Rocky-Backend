from typing import Optional
from pydantic import BaseModel

class Categoria(BaseModel):
    id: Optional[int] = None
    categoria: str