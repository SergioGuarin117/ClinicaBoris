import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ─── Password hashing ────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PASSWORD_RE = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
)
CEDULA_RE = re.compile(r'^\d{6,10}$')


# ─── Schemas ─────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    nombre: str
    apellido: str
    cedula: str
    email: EmailStr
    telefono: str | None = None
    password: str
    rol: str = "paciente"
    habeas_data: bool

    @field_validator("nombre", "apellido")
    @classmethod
    def name_min_length(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Debe tener al menos 2 caracteres.")
        return v

    @field_validator("cedula")
    @classmethod
    def validate_cedula(cls, v: str) -> str:
        v = v.strip()
        if not CEDULA_RE.match(v):
            raise ValueError("La cédula debe contener entre 6 y 10 dígitos numéricos.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not PASSWORD_RE.match(v):
            raise ValueError(
                "La contraseña debe tener mínimo 8 caracteres, "
                "al menos una mayúscula, una minúscula, un número y un símbolo (@$!%*?&)."
            )
        return v

    @field_validator("habeas_data")
    @classmethod
    def must_accept_habeas(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Debes aceptar la política de tratamiento de datos (Habeas Data).")
        return v

    @field_validator("rol")
    @classmethod
    def valid_rol(cls, v: str) -> str:
        allowed = {"paciente", "medico", "admin"}
        if v not in allowed:
            raise ValueError(f"Rol inválido. Permitidos: {allowed}")
        return v


class RegisterResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    cedula: str
    email: str
    telefono: str | None
    rol: str
    habeas_data: bool

    model_config = {"from_attributes": True}


# ─── Endpoint ─────────────────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registro de nuevo paciente",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Crea una cuenta de paciente.

    Validaciones aplicadas:
    - Correo electrónico único y con formato válido.
    - Cédula única y con 6-10 dígitos.
    - Contraseña segura (mayúscula, minúscula, número y símbolo).
    - Aceptación obligatoria de Habeas Data.
    """

    # Verificar unicidad de email
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo electrónico.",
        )

    # Verificar unicidad de cédula
    if db.query(User).filter(User.cedula == payload.cedula).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con esa cédula.",
        )

    user = User(
        nombre=payload.nombre,
        apellido=payload.apellido,
        cedula=payload.cedula,
        email=payload.email,
        telefono=payload.telefono,
        hashed_password=pwd_context.hash(payload.password),
        rol=payload.rol,
        habeas_data=payload.habeas_data,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user