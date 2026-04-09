"""
test_auth.py — Tests para los endpoints de autenticación de ClinicaBoris.
"""
import pytest


def payload_valido(**overrides):
    base = {
        "nombre": "Ana",
        "apellido": "García",
        "cedula": "9876543210",
        "email": "ana@clinicaboris.com",
        "password": "Segura@123",
        "habeas_data": True,
        "rol": "paciente",
    }
    base.update(overrides)
    return base


class TestRegistro:

    @pytest.mark.asyncio
    async def test_registro_exitoso(self, client):
        resp = await client.post("/api/auth/register", json=payload_valido())
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "ana@clinicaboris.com"
        assert data["nombre"] == "Ana"
        assert data["apellido"] == "García"
        assert data["rol"] == "paciente"
        assert data["habeas_data"] is True
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_registro_retorna_id(self, client):
        resp = await client.post("/api/auth/register", json=payload_valido())
        assert resp.status_code == 201
        assert isinstance(resp.json()["id"], int)
        assert resp.json()["id"] > 0

    @pytest.mark.asyncio
    async def test_registro_con_telefono(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(telefono="3001234567"),
        )
        assert resp.status_code == 201
        assert resp.json()["telefono"] == "3001234567"

    @pytest.mark.asyncio
    async def test_registro_email_duplicado(self, client):
        await client.post("/api/auth/register", json=payload_valido())
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(cedula="1111111111"),
        )
        assert resp.status_code == 409
        assert "correo" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_registro_cedula_duplicada(self, client):
        await client.post("/api/auth/register", json=payload_valido())
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(email="otro@test.com"),
        )
        assert resp.status_code == 409
        assert "cédula" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_registro_sin_habeas_data(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(habeas_data=False),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_registro_password_debil_sin_mayuscula(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(password="debil@123"),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_registro_password_debil_sin_simbolo(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(password="SinSimbolo1"),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_registro_password_muy_corta(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(password="Ab@1"),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_registro_cedula_muy_corta(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(cedula="123"),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_registro_cedula_muy_larga(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(cedula="12345678901"),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_registro_cedula_con_letras(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(cedula="ABC12345"),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_registro_nombre_muy_corto(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(nombre="A"),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_registro_rol_invalido(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(rol="superuser"),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_registro_email_invalido(self, client):
        resp = await client.post(
            "/api/auth/register",
            json=payload_valido(email="no-es-un-email"),
        )
        assert resp.status_code == 422


class TestLogin:

    @pytest.mark.asyncio
    async def test_login_exitoso(self, client, usuario_registrado):
        resp = await client.post(
            "/api/auth/login",
            data={
                "username": usuario_registrado["email"],
                "password": usuario_registrado["password"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["rol"] == "paciente"
        assert data["nombre"] == usuario_registrado["nombre"]
        assert data["id"] == usuario_registrado["id"]

    @pytest.mark.asyncio
    async def test_login_password_incorrecto(self, client, usuario_registrado):
        resp = await client.post(
            "/api/auth/login",
            data={
                "username": usuario_registrado["email"],
                "password": "WrongPass@999",
            },
        )
        assert resp.status_code == 401
        assert "contraseña" in resp.json()["detail"].lower() or "correo" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_email_inexistente(self, client):
        resp = await client.post(
            "/api/auth/login",
            data={
                "username": "noexiste@test.com",
                "password": "Cualquier@123",
            },
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_token_es_string(self, client, usuario_registrado):
        resp = await client.post(
            "/api/auth/login",
            data={
                "username": usuario_registrado["email"],
                "password": usuario_registrado["password"],
            },
        )
        token = resp.json()["access_token"]
        assert isinstance(token, str)
        assert len(token) > 20


class TestMe:

    @pytest.mark.asyncio
    async def test_me_con_token_valido(self, client, usuario_registrado, auth_headers):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == usuario_registrado["email"]
        assert data["nombre"] == usuario_registrado["nombre"]
        assert data["rol"] == "paciente"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_me_sin_token(self, client):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_con_token_invalido(self, client):
        resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer token.falso.inventado"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_no_expone_password(self, client, auth_headers):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        data = resp.json()
        assert "password" not in data
        assert "hashed_password" not in data