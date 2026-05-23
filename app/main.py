from contextlib import asynccontextmanager
from fastapi import FastAPI
import os
 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
from database import Base, engine
from routes.auth import router as auth_router
from routes.appointments import router as appointments_router
from routes.payments import router as payments_router
 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
 
 
# Crea las tablas si no existen (en producción usa Alembic)
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
 
app = FastAPI(
    title="ClinicaBoris API",
    version="1.0.0",
    lifespan=lifespan)
 
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "https://TU-APP.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.include_router(auth_router)
app.include_router(appointments_router)
app.include_router(payments_router)
 
if os.path.exists("/front/src"):
    @app.get("/")
    def serve_index():
        return FileResponse("/front/src/index.html")
 
    @app.get("/register")
    def serve_register():
        return FileResponse("/front/src/registro-paciente.html")
 
    @app.get("/login")
    def serve_login():
        return FileResponse("/front/src/login.html")
 
    @app.get("/dashboard")
    def serve_dashboard():
        return FileResponse("/front/src/registro.citas.html")
 
    app.mount("/static", StaticFiles(directory="/front/src"), name="static")