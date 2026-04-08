"""
test_auth.py — Tests para los endpoints de autenticación de ClinicaBoris.

Cubre:
  - Registro exitoso de paciente
  - Validaciones del formulario de registro (cédula, contraseña, habeas data)
  - Registro duplicado (email y cédula)
  - Login exitoso con JWT
  - Login con credenciales incorrectas
  - Endpoint /me con token válido e inválido
"""
import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def payload_valido(**overrides):
    """Devuelve un payload de registro válido con campos opcionales sobreescribibles."""
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


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS DE REGISTRO
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegistro:

    def test_registro_exitoso(self, client):
        """Un usuario con datos válidos debe registrarse con status 201."""
        resp = client.post("/api/auth/register", json=payload_valido())
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "ana@clinicaboris.com"
        assert data["nombre"] == "Ana"
        assert data["apellido"] == "García"
        assert data["rol"] == "paciente"
        assert data["habeas_data"] is True
        # La contraseña nunca debe aparecer en la respuesta
        assert "password" not in data
        assert "hashed_password" not in data

    def test_registro_retorna_id(self, client):
        """El registro debe devolver un ID numérico asignado por la DB."""
        resp = client.post("/api/auth/register", json=payload_valido())
        assert resp.status_code == 201
        assert isinstance(resp.json()["id"], int)
        assert resp.json()["id"] > 0

    def test_registro_con_telefono(self, client):
        """El teléfono es opcional pero debe guardarse si se envía."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(telefono="3001234567"),
        )
        assert resp.status_code == 201
        assert resp.json()["telefono"] == "3001234567"

    def test_registro_email_duplicado(self, client):
        """Registrar el mismo email dos veces debe retornar 409."""
        client.post("/api/auth/register", json=payload_valido())
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(cedula="1111111111"),  # cédula diferente, mismo email
        )
        assert resp.status_code == 409
        assert "correo" in resp.json()["detail"].lower()

    def test_registro_cedula_duplicada(self, client):
        """Registrar la misma cédula dos veces debe retornar 409."""
        client.post("/api/auth/register", json=payload_valido())
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(email="otro@test.com"),  # email diferente, misma cédula
        )
        assert resp.status_code == 409
        assert "cédula" in resp.json()["detail"].lower()

    def test_registro_sin_habeas_data(self, client):
        """Registrarse sin aceptar habeas data debe ser rechazado."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(habeas_data=False),
        )
        assert resp.status_code == 422

    def test_registro_password_debil_sin_mayuscula(self, client):
        """Contraseña sin mayúscula debe ser rechazada."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(password="debil@123"),
        )
        assert resp.status_code == 422

    def test_registro_password_debil_sin_simbolo(self, client):
        """Contraseña sin símbolo especial debe ser rechazada."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(password="SinSimbolo1"),
        )
        assert resp.status_code == 422

    def test_registro_password_muy_corta(self, client):
        """Contraseña menor a 8 caracteres debe ser rechazada."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(password="Ab@1"),
        )
        assert resp.status_code == 422

    def test_registro_cedula_muy_corta(self, client):
        """Cédula con menos de 6 dígitos debe ser rechazada."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(cedula="123"),
        )
        assert resp.status_code == 422

    def test_registro_cedula_muy_larga(self, client):
        """Cédula con más de 10 dígitos debe ser rechazada."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(cedula="12345678901"),
        )
        assert resp.status_code == 422

    def test_registro_cedula_con_letras(self, client):
        """Cédula con letras debe ser rechazada."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(cedula="ABC12345"),
        )
        assert resp.status_code == 422

    def test_registro_nombre_muy_corto(self, client):
        """Nombre con menos de 2 caracteres debe ser rechazado."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(nombre="A"),
        )
        assert resp.status_code == 422

    def test_registro_rol_invalido(self, client):
        """Un rol no permitido debe ser rechazado."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(rol="superuser"),
        )
        assert resp.status_code == 422

    def test_registro_email_invalido(self, client):
        """Un email con formato incorrecto debe ser rechazado."""
        resp = client.post(
            "/api/auth/register",
            json=payload_valido(email="no-es-un-email"),
        )
        assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS DE LOGIN
# ═══════════════════════════════════════════════════════════════════════════════

class TestLogin:

    def test_login_exitoso(self, client, usuario_registrado):
        """Login con credenciales correctas debe retornar token JWT."""
        resp = client.post(
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

    def test_login_password_incorrecto(self, client, usuario_registrado):
        """Login con contraseña incorrecta debe retornar 401."""
        resp = client.post(
            "/api/auth/login",
            data={
                "username": usuario_registrado["email"],
                "password": "WrongPass@999",
            },
        )
        assert resp.status_code == 401
        assert "contraseña" in resp.json()["detail"].lower() or "correo" in resp.json()["detail"].lower()

    def test_login_email_inexistente(self, client):
        """Login con email que no existe debe retornar 401."""
        resp = client.post(
            "/api/auth/login",
            data={
                "username": "noexiste@test.com",
                "password": "Cualquier@123",
            },
        )
        assert resp.status_code == 401

    def test_login_token_es_string(self, client, usuario_registrado):
        """El token devuelto debe ser una cadena no vacía."""
        resp = client.post(
            "/api/auth/login",
            data={
                "username": usuario_registrado["email"],
                "password": usuario_registrado["password"],
            },
        )
        token = resp.json()["access_token"]
        assert isinstance(token, str)
        assert len(token) > 20


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS DEL ENDPOINT /me
# ═══════════════════════════════════════════════════════════════════════════════

class TestMe:

    def test_me_con_token_valido(self, client, usuario_registrado, auth_headers):
        """/me con token válido debe retornar los datos del usuario actual."""
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == usuario_registrado["email"]
        assert data["nombre"] == usuario_registrado["nombre"]
        assert data["rol"] == "paciente"
        assert "id" in data

    def test_me_sin_token(self, client):
        """/me sin token debe retornar 401."""
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_con_token_invalido(self, client):
        """/me con token falso debe retornar 401."""
        resp = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer token.falso.inventado"},
        )
        assert resp.status_code == 401

    def test_me_no_expone_password(self, client, auth_headers):
        """La respuesta de /me nunca debe contener la contraseña."""
        resp = client.get("/api/auth/me", headers=auth_headers)
        data = resp.json()
        assert "password" not in data
        assert "hashed_password" not in data
