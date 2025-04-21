from pydantic import BaseModel
from datetime import date

class MovimientoFinancieroBase(BaseModel):
    usuario_id: int | None = None
    fecha: date 
    tipo: str 
    concepto: str
    monto_presupuestado: float 
    monto_real: float 
    
class MovimientoFinanciero(MovimientoFinancieroBase):
    id: int 