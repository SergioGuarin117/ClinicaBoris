from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import Base, engine
from routes.auth import router as auth_router
from routes.appointments import router as appointments_router
from routes.imagen_ia import router as ia_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ClinicaBoris API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(appointments_router)
app.include_router(ia_router)

@app.get("/")
def serve_index():
    return FileResponse("/front/src/index.html")

@app.get("/register")
def serve_register():
    return FileResponse("/front/src/registro-paciente.html")

@app.get("/login")
def serve_login():
    return FileResponse("/front/src/login.html")

app.mount("/static", StaticFiles(directory="/front/src"), name="static")
