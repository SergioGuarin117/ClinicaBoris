import re
import os
import httpx
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from passlib.context import CryptContext
from jose import JWTError, jwt

from database import get_db
from models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ─── Configuración JWT ────────────────────────────────────────────────────────
SECRET_KEY = "clinicaboris-secret-key-cambiar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas

# ─── Configuración Google OAuth ───────────────────────────────────────────────
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL         = os.getenv("FRONTEND_URL", "http://localhost:8000")
GOOGLE_REDIRECT_URI  = f"{FRONTEND_URL}/api/auth/google/callback"

GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_URL  = "https://www.googleapis.com/oauth2/v3/userinfo"

# ─── Password hashing ────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

PASSWORD_RE = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
)
CEDULA_RE = re.compile(r'^\d{6,10}$')


# ─── Helpers JWT ─────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Lee el JWT del header Authorization y devuelve el usuario de la DB."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if not user or not user.is_active:
        raise credentials_exception
    return user


# ─── Dependencias de rol ──────────────────────────────────────────────────────
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores.",
        )
    return current_user


def require_paciente(current_user: User = Depends(get_current_user)) -> User:
    if current_user.rol != "paciente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a pacientes.",
        )
    return current_user


# ─── Schemas ─────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    nombre: str
    apellido: str
    cedula: str
    email: EmailStr
    telefono: Optional[str] = None
    password: str
    rol: str = "paciente"
    habeas_data: bool
    tipo_consulta: Optional[str] = None

    @field_validator("telefono", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

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

    @field_validator("tipo_consulta", mode="before")
    @classmethod
    def valid_tipo(cls, v):
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        allowed = {"estandar", "premium"}
        if v not in allowed:
            raise ValueError(f"tipo_consulta inválido. Permitidos: {allowed}")
        return v


class RegisterResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    cedula: str
    email: str
    telefono: Optional[str]
    rol: str
    habeas_data: bool
    tipo_consulta: Optional[str] = None

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre: str
    id: int


class MeResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    rol: str
    tipo_consulta: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Endpoints de autenticación clásica ──────────────────────────────────────

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registro de nuevo paciente",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Ya existe una cuenta con ese correo electrónico.")
    if db.query(User).filter(User.cedula == payload.cedula).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Ya existe una cuenta con esa cédula.")
    user = User(
        nombre=payload.nombre,
        apellido=payload.apellido,
        cedula=payload.cedula,
        email=payload.email,
        telefono=payload.telefono,
        hashed_password=pwd_context.hash(payload.password),
        rol=payload.rol,
        habeas_data=payload.habeas_data,
        tipo_consulta=payload.tipo_consulta,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login clásico — devuelve JWT con rol incluido",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Esta cuenta está desactivada.")

    token = create_access_token(data={"sub": str(user.id), "rol": user.rol})
    return LoginResponse(access_token=token, token_type="bearer",
                         rol=user.rol, nombre=user.nombre, id=user.id)


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Devuelve el usuario autenticado actual",
)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ─── Endpoints Google OAuth ───────────────────────────────────────────────────

@router.get(
    "/google",
    summary="Inicia el flujo de login con Google",
)
def google_login():
    """
    El botón del frontend apunta a este endpoint.
    Redirige al usuario a la pantalla de login de Google.
    """
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)


@router.get(
    "/google/callback",
    summary="Google redirige aquí tras autenticación exitosa",
)
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Google llama este endpoint con un código temporal.
    El backend lo intercambia por los datos del usuario,
    crea la cuenta si no existe, y redirige al frontend
    con el JWT en la URL para que lo guarde en localStorage.
    """

    # 1. Intercambiar código por token de Google
    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri":  GOOGLE_REDIRECT_URI,
            "grant_type":    "authorization_code",
        })

    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error al obtener token de Google.")

    google_token = token_response.json().get("access_token")

    # 2. Obtener datos del usuario desde Google
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            GOOGLE_USER_URL,
            headers={"Authorization": f"Bearer {google_token}"}
        )

    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error al obtener datos de Google.")

    google_data = user_response.json()
    email  = google_data.get("email")
    nombre = google_data.get("given_name") or google_data.get("name", "Usuario")
    apellido = google_data.get("family_name", "")

    # 3. Buscar o crear el usuario en la DB
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # Primera vez — se crea la cuenta automáticamente como paciente
        # sin cédula ni contraseña (es cuenta Google)
        user = User(
            nombre=nombre,
            apellido=apellido,
            email=email,
            cedula=f"GOOGLE-{email}",   # placeholder para cumplir el NOT NULL
            hashed_password="GOOGLE_AUTH",
            rol="paciente",
            habeas_data=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Esta cuenta está desactivada.")

    # 4. Generar JWT propio y redirigir al frontend
    token = create_access_token(data={"sub": str(user.id), "rol": user.rol})

    # El frontend recibe el token en la URL y lo guarda en localStorage
    if user.rol == "admin":
        redirect_url = f"{FRONTEND_URL}/dashboard-admin?token={token}"
    else:
        redirect_url = f"{FRONTEND_URL}/dashboard-paciente?token={token}"

    return RedirectResponse(redirect_url)