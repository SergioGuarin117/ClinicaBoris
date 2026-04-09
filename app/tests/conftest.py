import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

os.environ["DATABASE_URL"] = "sqlite://"

engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest_asyncio.fixture
async def client():
    from database import Base, get_db
    from main import app

    Base.metadata.create_all(bind=engine_test)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def usuario_registrado(client):
    payload = {
        "nombre": "Ana",
        "apellido": "García",
        "cedula": "9876543210",
        "email": "ana@clinicaboris.com",
        "password": "Segura@123",
        "habeas_data": True,
        "rol": "paciente",
    }
    resp = await client.post("/api/auth/register", json=payload)
    data = resp.json()
    data["password"] = "Segura@123"
    return data


@pytest_asyncio.fixture
async def auth_headers(client, usuario_registrado):
    resp = await client.post(
        "/api/auth/login",
        data={
            "username": usuario_registrado["email"],
            "password": usuario_registrado["password"],
        },
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}