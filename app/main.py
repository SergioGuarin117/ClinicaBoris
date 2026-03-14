from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routes.auth import router as auth_router
from routes.appointments import router as appointments_router

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Crea las tablas si no existen (en producción usa Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ClinicaBoris API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ajusta en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(appointments_router)

@app.get("/")
def serve_index():
    return FileResponse("/front/src/index.html")

@app.get("/register")
def serve_register():
    return FileResponse("/front/src/registro-paciente.html")

@app.get("/login")
def serve_login():
    return FileResponse("/front/src/login.html")

# Monta la carpeta del frontend
app.mount("/static", StaticFiles(directory="/front/src"), name="static")