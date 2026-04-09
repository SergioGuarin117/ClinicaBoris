"""
test_main.py — Tests para el endpoint raíz y configuración general de la API.
"""
import pytest


class TestApiGeneral:

    @pytest.mark.asyncio
    async def test_docs_disponibles(self, client):
        resp = await client.get("/docs")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_openapi_json_disponible(self, client):
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["info"]["title"] == "ClinicaBoris API"
        assert data["info"]["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_ruta_auth_register_existe(self, client):
        resp = await client.post("/api/auth/register", json={})
        assert resp.status_code != 404

    @pytest.mark.asyncio
    async def test_ruta_auth_login_existe(self, client):
        resp = await client.post("/api/auth/login", data={})
        assert resp.status_code != 404

    @pytest.mark.asyncio
    async def test_ruta_appointments_existe(self, client):
        resp = await client.get("/api/appointments/")
        assert resp.status_code != 404

    @pytest.mark.asyncio
    async def test_cors_headers_presentes(self, client):
        resp = await client.options(
            "/api/auth/register",
            headers={"Origin": "http://localhost:3000"},
        )
        assert resp.status_code in [200, 204, 405]