from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import Base, engine
from routes.auth import router as auth_router
from routes.appointments import router as appointments_router
from routes.payments import router as payments_router
from routes.imagen_ia import router as ia_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="ClinicaBoris API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(appointments_router)
app.include_router(payments_router)
app.include_router(ia_router)

@app.get("/")
def serve_index():
    return FileResponse("/front/src/index.html")

@app.get("/login.html")
def serve_login():
    return FileResponse("/front/src/login.html")

@app.get("/registro-paciente.html")
def serve_registro():
    return FileResponse("/front/src/registro-paciente.html")

@app.get("/pre-reserva.html")
def serve_prereserva():
    return FileResponse("/front/src/pre-reserva.html")

@app.get("/pago-exitoso.html")
def serve_pago_exitoso():
    return FileResponse("/front/src/pago-exitoso.html")

@app.get("/pago-fallido.html")
def serve_pago_fallido():
    return FileResponse("/front/src/pago-fallido.html")

@app.get("/pago-pendiente.html")
def serve_pago_pendiente():
    return FileResponse("/front/src/pago-pendiente.html")

@app.get("/admin/{page}.html")
def serve_admin(page: str):
    return FileResponse(f"/front/src/admin/{page}.html")

@app.get("/cirujano/{page}.html")
def serve_cirujano(page: str):
    return FileResponse(f"/front/src/cirujano/{page}.html")

@app.get("/paciente/{page}.html")
def serve_paciente(page: str):
    return FileResponse(f"/front/src/paciente/{page}.html")

app.mount("/", StaticFiles(directory="/front/src", html=True), name="frontend")