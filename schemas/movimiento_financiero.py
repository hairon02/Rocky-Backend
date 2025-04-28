from pydantic import BaseModel
from datetime import date
from typing import Optional
from fastapi import Query

class MovimientoFinancieroBase(BaseModel):
    usuario_id: int | None = None
    fecha: date 
    tipo: str 
    concepto: str
    monto_presupuestado: float 
    monto_real: float 
    
class MovimientoFinanciero(MovimientoFinancieroBase):
    id: int

class EstadoFinancieroResponse(BaseModel):
    estado: str  # "Positivo" o "Negativo"
    mensaje: str
    total_ingresos: float
    total_egresos: float
    saldo_final: float