from pydantic import BaseModel
from datetime import date
from typing import Optional
from fastapi import Query

class MovimientoFinancieroBase(BaseModel):
    usuario_id: int | None = None
    categoria_id: int
    fecha: date 
    tipo: str 
    concepto: str
    monto_presupuestado: float 
    monto_real: float 

    class Config:
        from_attributes = True

    
class MovimientoFinanciero(MovimientoFinancieroBase):
    id: int

class EstadoFinancieroResponse(BaseModel):
    estado: str  # "Positivo" o "Negativo"
    mensaje: str
    total_ingresos: float
    total_egresos: float
    saldo_final: float

    class Config:
        from_attributes = True
