from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator

from app.database import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    user_id: int
    fecha_cita: datetime
    motivo: Optional[str] = None
    notas: Optional[str] = None

    @field_validator("fecha_cita")
    @classmethod
    def fecha_no_en_pasado(cls, v: datetime) -> datetime:
        if v < datetime.now(tz=v.tzinfo):
            raise ValueError("La fecha de la cita no puede ser en el pasado.")
        return v


class AppointmentUpdate(BaseModel):
    fecha_cita: Optional[datetime] = None
    estado: Optional[AppointmentStatus] = None
    motivo: Optional[str] = None
    notas: Optional[str] = None

    @field_validator("fecha_cita")
    @classmethod
    def fecha_no_en_pasado(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v < datetime.now(tz=v.tzinfo):
            raise ValueError("La fecha de la cita no puede ser en el pasado.")
        return v


class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    fecha_cita: datetime
    estado: AppointmentStatus
    motivo: Optional[str]
    notas: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_appointment_or_404(appointment_id: int, db: Session) -> Appointment:
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con id={appointment_id} no encontrada.",
        )
    return appt


def get_user_or_404(user_id: int, db: Session) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id={user_id} no encontrado.",
        )
    return user


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva cita",
)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    """
    Crea una cita para un usuario existente.
    Estado inicial: **pendiente**.
    """
    get_user_or_404(payload.user_id, db)

    appt = Appointment(
        user_id=payload.user_id,
        fecha_cita=payload.fecha_cita,
        estado=AppointmentStatus.pendiente,
        motivo=payload.motivo,
        notas=payload.notas,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@router.get(
    "/",
    response_model=list[AppointmentResponse],
    summary="Listar citas",
)
def list_appointments(
    user_id: Optional[int] = Query(None, description="Filtrar por paciente"),
    estado: Optional[AppointmentStatus] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
):
    """
    Devuelve todas las citas.
    Permite filtrar por **user_id** y/o **estado**.
    """
    q = db.query(Appointment)
    if user_id is not None:
        q = q.filter(Appointment.user_id == user_id)
    if estado is not None:
        q = q.filter(Appointment.estado == estado)
    return q.order_by(Appointment.fecha_cita).all()


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Obtener cita por ID",
)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return get_appointment_or_404(appointment_id, db)


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Actualizar cita (estado, fecha, notas…)",
)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza campos de una cita existente.
    Úsalo para cambiar el estado a **confirmada**, **cancelada** o **completada**.
    """
    appt = get_appointment_or_404(appointment_id, db)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appt, field, value)

    db.commit()
    db.refresh(appt)
    return appt


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar cita",
)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = get_appointment_or_404(appointment_id, db)
    db.delete(appt)
    db.commit()