from fastapi import APIRouter, Response, status, HTTPException
from config.db import conn
from models.movimiento_financiero import movimiento_financiero
from schemas.movimiento_financiero import MovimientoFinanciero, MovimientoFinancieroBase
from starlette.status import HTTP_204_NO_CONTENT

movimientoFinanciero = APIRouter()


@movimientoFinanciero.get("/movimientoFinanciero", response_model=list[MovimientoFinanciero])
def get_movimientos_financieros():
    result = conn.execute(movimiento_financiero.select().order_by(movimiento_financiero.c.fecha)).fetchall()
    movimientos_list = [row._mapping for row in result]
    return movimientos_list

@movimientoFinanciero.post("/movimientoFinanciero", response_model = MovimientoFinanciero)
def create_movimientoFinanciero(movimiento: MovimientoFinancieroBase):
    nuevo_movimiento = {
        "usuario_id": movimiento.usuario_id,
        "fecha": movimiento.fecha,
        "tipo": movimiento.tipo,
        "concepto": movimiento.concepto,
        "monto_presupuestado": movimiento.monto_presupuestado,
        "monto_real": movimiento.monto_real
    }
    print("Insertando:", nuevo_movimiento)

    result = conn.execute(movimiento_financiero.insert().values(nuevo_movimiento))
    conn.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found") 
    
    movimientoFinanciero = conn.execute(movimiento_financiero.select().where(movimiento_financiero.c.id == result.lastrowid)).first()._mapping
    return movimientoFinanciero
   

@movimientoFinanciero.get("/movimientoFinanciero/{id}", response_model = MovimientoFinanciero)
def get_movimientoFinanciero(id: int):
    movimientoFinanciero = conn.execute(movimiento_financiero.select().where(movimiento_financiero.c.id == id)).first()
    if movimientoFinanciero:
        return movimientoFinanciero._mapping
    raise HTTPException(status_code = 404, detail= "Movimiento Financiero no encontrado")

@movimientoFinanciero.put("/movimientoFinanciero/{id}", response_model = MovimientoFinanciero)
def update(id: int, movimiento: MovimientoFinancieroBase):
    result = conn.execute(movimiento_financiero.update().values(
                                            usuario_id = movimiento.usuario_id,
                                            fecha = movimiento.fecha,
                                            tipo = movimiento.tipo,
                                            concepto = movimiento.concepto,
                                            monto_presupuestado = movimiento.monto_presupuestado,
                                            monto_real = movimiento.monto_real).where(movimiento_financiero.c.id == id))
    conn.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Movimiento Financiero no encontrado")

    result = conn.execute(movimiento_financiero.select().where(movimiento_financiero.c.id == id)).first()._mapping
    return result

@movimientoFinanciero.delete("/movimientoFinanciero/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete(id: int):
    result = conn.execute(movimiento_financiero.delete().where(movimiento_financiero.c.id == id))
    conn.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code =  404, detail = "Movimiento Financiero no encotrado")
    return Response(status_code = HTTP_204_NO_CONTENT)
