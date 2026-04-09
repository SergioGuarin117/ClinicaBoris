import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Establecer variable de entorno ANTES de importar cualquier cosa del proyecto
# Esto hace que database.py use SQLite en vez de PostgreSQL
os.environ["DATABASE_URL"] = "sqlite://"

SQLALCHEMY_DATABASE_URL = "sqlite://"  # En memoria pura, sin archivo

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest_asyncio.fixture
async def client():
    # Importar DESPUÉS de setear DATABASE_URL
    from database import Base, get_db
    from main import app

    # Crear todas las tablas en SQLite en memoria
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