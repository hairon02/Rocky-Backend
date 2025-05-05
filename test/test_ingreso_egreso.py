from fastapi.testclient import TestClient
from main import app  # Asegúrate que aquí esté tu app principal de FastAPI
import datetime

client = TestClient(app)

def test_get_movimientos_financieros():
    response = client.get("/movimientoFinanciero")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_movimientoFinanciero():
    movimiento_data = {
        "usuario_id": 1,
        "fecha": str(datetime.date.today()),
        "tipo": "ingreso",
        "concepto": "Salario",
        "monto_presupuestado": 5000.0,
        "monto_real": 5000.0
    }
    response = client.post("/movimientoFinanciero", json=movimiento_data)
    assert response.status_code == 200
    data = response.json()
    assert data["usuario_id"] == movimiento_data["usuario_id"]
    assert data["tipo"] == movimiento_data["tipo"]
    assert data["monto_real"] == movimiento_data["monto_real"]

def test_get_movimientoFinanciero_by_id():
    # Asumimos que el ID 1 existe
    response = client.get("/movimientoFinanciero/1")
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
    else:
        assert response.status_code == 404

def test_update_movimientoFinanciero():
    update_data = {
        "usuario_id": 1,
        "fecha": str(datetime.date.today()),
        "tipo": "egreso",
        "concepto": "Compra",
        "monto_presupuestado": 2000.0,
        "monto_real": 1900.0
    }
    response = client.put("/movimientoFinanciero/1", json=update_data)
    if response.status_code == 200:
        data = response.json()
        assert data["tipo"] == update_data["tipo"]
    else:
        assert response.status_code == 404

def test_delete_movimientoFinanciero():
    response = client.delete("/movimientoFinanciero/1")
    assert response.status_code in [204, 404]