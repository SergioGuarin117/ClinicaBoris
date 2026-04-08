"""
conftest.py — Configuración compartida para todos los tests de ClinicaBoris.

Usa SQLite en memoria para no necesitar PostgreSQL durante las pruebas.
Cada test recibe una base de datos limpia gracias al fixture 'client'.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Base de datos en memoria — no necesita Docker ni PostgreSQL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def client():
    """
    Crea un cliente de prueba con base de datos SQLite limpia por cada test.
    Al terminar, elimina todas las tablas para que el siguiente test empiece fresco.
    """
    # Importar aquí para que las variables de entorno estén listas
    from database import Base, get_db
    from main import app

    # Crear todas las tablas en SQLite
    Base.metadata.create_all(bind=engine)

    # Sobreescribir la dependencia de DB para usar SQLite en vez de PostgreSQL
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    # Limpiar después de cada test
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def usuario_registrado(client):
    """
    Crea un usuario paciente de prueba y lo devuelve junto con sus credenciales.
    Útil para tests que necesitan un usuario ya existente.
    """
    payload = {
        "nombre": "Carlos",
        "apellido": "Pérez",
        "cedula": "1234567890",
        "email": "carlos@test.com",
        "password": "Test@1234",
        "habeas_data": True,
        "rol": "paciente",
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 201, f"No se pudo crear usuario de prueba: {resp.text}"
    return {**resp.json(), "password": "Test@1234", "email": "carlos@test.com"}


@pytest.fixture(scope="function")
def token_paciente(client, usuario_registrado):
    """Devuelve un JWT válido para el usuario paciente de prueba."""
    resp = client.post(
        "/api/auth/login",
        data={
            "username": usuario_registrado["email"],
            "password": usuario_registrado["password"],
        },
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(token_paciente):
    """Headers de autorización listos para usar en requests."""
    return {"Authorization": f"Bearer {token_paciente}"}
