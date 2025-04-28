from fastapi import APIRouter, Response, status, HTTPException, Query
from config.db import conn
from models.movimiento_financiero import movimiento_financiero
from schemas.movimiento_financiero import MovimientoFinanciero, MovimientoFinancieroBase, EstadoFinancieroResponse
from starlette.status import HTTP_204_NO_CONTENT
from datetime import date
from typing import Optional
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

@movimientoFinanciero.get("/estado_financiero", response_model=EstadoFinancieroResponse)
def calcular_estado_financiero(
    usuario_id: int,
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None)
):
    try:
        query = movimiento_financiero.select().where(
            movimiento_financiero.c.usuario_id == usuario_id
        )

        if fecha_inicio and fecha_fin:
            query = query.where(
                movimiento_financiero.c.fecha.between(fecha_inicio, fecha_fin)
            )

        movimientos = conn.execute(query).fetchall()

        if not movimientos:
            raise HTTPException(status_code=404, detail="No se encontraron movimientos para este usuario.")

        ingresos = sum(m._mapping["monto_real"] for m in movimientos if m._mapping["tipo"] == "ingreso")
        egresos = sum(m._mapping["monto_real"] for m in movimientos if m._mapping["tipo"] == "egreso")

        saldo = ingresos - egresos

        if saldo >= 0:
            estado = "Positivo"
            mensaje = "Tu situación financiera es buena. Sigue así!"
        else:
            estado = "Negativo"
            mensaje = "Tienes más gastos que ingresos. Revisa tus finanzas."

        return {
            "estado": estado,
            "mensaje": mensaje,
            "total_ingresos": ingresos,
            "total_egresos": egresos,
            "saldo_final": saldo
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")