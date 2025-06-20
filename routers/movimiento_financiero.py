# routers/movimiento_financiero.py
from fastapi import APIRouter, Response, status, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from config.db import get_db, engine
from models.movimiento_financiero import movimiento_financiero
from schemas.movimiento_financiero import MovimientoFinanciero, MovimientoFinancieroBase, EstadoFinancieroResponse
from starlette.status import HTTP_204_NO_CONTENT
from datetime import date
from typing import Optional
from sqlalchemy import asc, desc

movimientoFinanciero = APIRouter()

@movimientoFinanciero.get("/movimientoFinanciero/list/{id}", response_model=list[MovimientoFinanciero])
def get_movimientos_financieros(id: int, db: Session = Depends(get_db)):
    result = db.execute(movimiento_financiero.select().where(movimiento_financiero.c.usuario_id == id).order_by(desc(movimiento_financiero.c.fecha))).fetchall()
    movimientos_list = [row._mapping for row in result]
    return movimientos_list

@movimientoFinanciero.post("/movimientoFinanciero", response_model=MovimientoFinanciero)
def create_movimientoFinanciero(movimiento: MovimientoFinancieroBase, db: Session = Depends(get_db)):
    nuevo_movimiento = movimiento.model_dump()
    
    insert_statement = movimiento_financiero.insert().values(nuevo_movimiento).returning(movimiento_financiero)
    result = db.execute(insert_statement)
    db.commit()
    
    new_movimiento = result.first()
    if not new_movimiento:
        raise HTTPException(status_code=500, detail="No se pudo crear el movimiento financiero.")
    
    return new_movimiento._mapping

@movimientoFinanciero.get("/movimientoFinanciero/{id}", response_model=MovimientoFinanciero)
def get_movimientoFinanciero(id: int, db: Session = Depends(get_db)):
    result = db.execute(movimiento_financiero.select().where(movimiento_financiero.c.id == id)).first()
    if result:
        return result._mapping
    raise HTTPException(status_code=404, detail="Movimiento Financiero no encontrado")

@movimientoFinanciero.put("/movimientoFinanciero/{id}", response_model=MovimientoFinanciero)
def update(id: int, movimiento: MovimientoFinancieroBase, db: Session = Depends(get_db)):
    result = db.execute(movimiento_financiero.update().values(movimiento.model_dump()).where(movimiento_financiero.c.id == id))
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Movimiento Financiero no encontrado")

    updated_movimiento = db.execute(movimiento_financiero.select().where(movimiento_financiero.c.id == id)).first()
    return updated_movimiento._mapping

@movimientoFinanciero.delete("/movimientoFinanciero/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int, db: Session = Depends(get_db)):
    result = db.execute(movimiento_financiero.delete().where(movimiento_financiero.c.id == id))
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Movimiento Financiero no encontrado")
    return Response(status_code=HTTP_204_NO_CONTENT)

# ... (Las demás funciones como calcular_estado_financiero también deben usar 'db: Session = Depends(get_db)' y 'db.execute')
# Ejemplo para calcular_estado_financiero:
@movimientoFinanciero.get("/estado_financiero", response_model=EstadoFinancieroResponse)
def calcular_estado_financiero(
    usuario_id: int,
    db: Session = Depends(get_db),
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

        movimientos = db.execute(query).fetchall()

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
        
@movimientoFinanciero.get("/resumen_mensual")
def resumen_mensual(usuario_id: int, anio: int, mes: int):
    try:
        # Calcular el rango de fechas del mes
        fecha_inicio = date(anio, mes, 1)
        if mes == 12:
            fecha_fin = date(anio + 1, 1, 1)
        else:
            fecha_fin = date(anio, mes + 1, 1)

        query = movimiento_financiero.select().where(
            movimiento_financiero.c.usuario_id == usuario_id,
            movimiento_financiero.c.fecha >= fecha_inicio,
            movimiento_financiero.c.fecha < fecha_fin
        )

        movimientos = engine.connect().execute(query).fetchall()

        if not movimientos:
            raise HTTPException(status_code=404, detail="No se encontraron movimientos para este mes.")

        ingresos = sum(m._mapping["monto_real"] for m in movimientos if m._mapping["tipo"] == "ingreso")
        egresos = sum(m._mapping["monto_real"] for m in movimientos if m._mapping["tipo"] == "egreso")
        saldo = ingresos - egresos

        return {
            "usuario_id": usuario_id,
            "mes": mes,
            "anio": anio,
            "total_ingresos": ingresos,
            "total_egresos": egresos,
            "saldo_final": saldo
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@movimientoFinanciero.get("/progreso_financiero")
def get_progreso_financiero(usuario_id: int, fecha_inicio: date, fecha_fin: date):
    # Obtener los movimientos del usuario dentro del rango de fechas
    query = movimiento_financiero.select().where(
        movimiento_financiero.c.usuario_id == usuario_id,
        movimiento_financiero.c.fecha >= fecha_inicio,
        movimiento_financiero.c.fecha <= fecha_fin
    ).order_by(asc(movimiento_financiero.c.fecha))

    with engine.connect() as conn:
        movimientos = conn.execute(query).fetchall()

    if not movimientos:
        raise HTTPException(status_code=404, detail="No se encontraron movimientos financieros en el rango de fechas.")

    # Calcular saldo acumulado
    saldo = 0
    progreso = []
    for movimiento in movimientos:
        movimiento = movimiento._mapping
        if movimiento['tipo'].lower() == "ingreso":
            saldo += movimiento['monto_real']
        elif movimiento['tipo'].lower() == "egreso":
            saldo -= movimiento['monto_real']

        progreso.append({
            "fecha": movimiento['fecha'],
            "saldo": saldo
        })

    return {
        "usuario_id": usuario_id,
        "progreso": progreso
    }
