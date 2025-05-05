from fastapi.testclient import TestClient
from main import app  # Asegúrate que aquí esté tu app principal de FastAPI
import datetime

client = TestClient(app)

def test_calcular_estado_financiero():
    params = {
        "usuario_id": 1
    }
    response = client.get("/estado_financiero", params=params)
    if response.status_code == 200:
        data = response.json()
        assert "estado" in data
        assert "saldo_final" in data
    else:
        assert response.status_code == 404

def test_resumen_mensual():
    params = {
        "usuario_id": 1,
        "anio": datetime.date.today().year,
        "mes": datetime.date.today().month
    }
    response = client.get("/resumen_mensual", params=params)
    if response.status_code == 200:
        data = response.json()
        assert "total_ingresos" in data
    else:
        assert response.status_code == 404

def test_get_progreso_financiero():
    today = datetime.date.today()
    params = {
        "usuario_id": 1,
        "fecha_inicio": str(today.replace(day=1)),
        "fecha_fin": str(today)
    }
    response = client.get("/progreso_financiero", params=params)
    if response.status_code == 200:
        data = response.json()
        assert "progreso" in data
    else:
        assert response.status_code == 404
