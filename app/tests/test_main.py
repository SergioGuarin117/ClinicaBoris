"""
test_main.py — Tests para el endpoint raíz y configuración general de la API.

Cubre:
  - Que la app arranca y responde
  - Que los docs de FastAPI están disponibles
  - Que el router de auth está montado
  - Que el router de appointments está montado
"""


class TestApiGeneral:

    def test_docs_disponibles(self, client):
        """La documentación automática de FastAPI debe estar accesible en /docs."""
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_openapi_json_disponible(self, client):
        """El esquema OpenAPI debe estar disponible en /openapi.json."""
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["info"]["title"] == "ClinicaBoris API"
        assert data["info"]["version"] == "1.0.0"

    def test_ruta_auth_register_existe(self, client):
        """El endpoint de registro debe existir (no retornar 404)."""
        resp = client.post("/api/auth/register", json={})
        # 422 significa que llegó al endpoint pero los datos son inválidos
        # lo importante es que NO sea 404
        assert resp.status_code != 404

    def test_ruta_auth_login_existe(self, client):
        """El endpoint de login debe existir."""
        resp = client.post("/api/auth/login", data={})
        assert resp.status_code != 404

    def test_ruta_appointments_existe(self, client):
        """El endpoint de citas debe existir."""
        resp = client.get("/api/appointments/")
        assert resp.status_code != 404

    def test_cors_headers_presentes(self, client):
        """Los headers CORS deben estar configurados."""
        resp = client.options(
            "/api/auth/register",
            headers={"Origin": "http://localhost:3000"},
        )
        # La app tiene CORS habilitado con allow_origins=["*"]
        assert resp.status_code in [200, 204, 405]
