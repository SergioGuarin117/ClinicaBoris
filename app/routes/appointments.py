from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, field_validator

from database import get_db
from models.appointment import Appointment, AppointmentStatus
from models.user import User

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


# ─── Dashboard — /citas (DEBE ir antes de /{appointment_id}) ──────────────────

CAMPOS_VALIDOS  = {"fecha", "estado"}
ORDENES_VALIDOS = {"asc", "desc"}

@router.get("/citas", tags=["dashboard"], summary="Citas para el panel admin")
def get_citas_dashboard(
    estado: str = Query("todas"),
    campo:  str = Query("fecha"),
    orden:  str = Query("asc"),
    buscar: str = Query(""),
    db: Session = Depends(get_db),
):
    if campo not in CAMPOS_VALIDOS:  campo = "fecha"
    if orden not in ORDENES_VALIDOS: orden = "asc"

    try:
        conteos_raw = db.execute(
            text("SELECT estado::text, COUNT(*) AS n FROM appointments GROUP BY estado")
        ).fetchall()
        conteos = {r.estado: r.n for r in conteos_raw}

        conditions: list[str] = []
        params: dict = {}

        if estado and estado != "todas":
            conditions.append("a.estado = :estado::appointmentstatus")
            params["estado"] = estado

        if buscar:
            conditions.append("(u.nombre ILIKE :buscar OR u.apellido ILIKE :buscar)")
            params["buscar"] = f"%{buscar}%"

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        order_col = "a.fecha_cita" if campo == "fecha" else "a.estado"

        rows = db.execute(text(f"""
            SELECT
                a.id,
                a.fecha_cita::date::text                                        AS fecha,
                TO_CHAR(a.fecha_cita AT TIME ZONE 'America/Bogota', 'HH24:MI') AS hora,
                u.nombre || ' ' || u.apellido                                   AS paciente,
                u.cedula,
                u.telefono,
                a.estado::text                                                  AS estado,
                a.motivo,
                a.notas
            FROM appointments a
            JOIN users u ON u.id = a.user_id
            {where}
            ORDER BY {order_col} {orden.upper()}, a.id ASC
        """), params).fetchall()

        return JSONResponse({
            "citas": [dict(r._mapping) for r in rows],
            "conteos": {
                "confirmada": int(conteos.get("confirmada", 0)),
                "pendiente":  int(conteos.get("pendiente",  0)),
                "completada": int(conteos.get("completada", 0)),
                "cancelada":  int(conteos.get("cancelada",  0)),
            },
        })

    except Exception as exc:
        return JSONResponse(
            {"error": str(exc), "citas": [], "conteos": {}},
            status_code=500,
        )


# ─── Estadísticas — /estadisticas ─────────────────────────────────────────────

@router.get("/estadisticas", tags=["dashboard"], summary="Estadísticas para el panel")
def get_estadisticas(db: Session = Depends(get_db)):
    try:
        # ── Estados ───────────────────────────────────────────
        estados_raw = db.execute(text("""
            SELECT estado::text, COUNT(*) AS n
            FROM appointments GROUP BY estado
        """)).fetchall()
        estados = {r.estado: int(r.n) for r in estados_raw}

        # ── Citas por día — últimos 7 días ────────────────────
        dias_raw = db.execute(text("""
            SELECT
                TO_CHAR(fecha_cita AT TIME ZONE 'America/Bogota', 'Dy') AS dia,
                COUNT(*) AS n
            FROM appointments
            WHERE fecha_cita >= NOW() - INTERVAL '7 days'
            GROUP BY DATE_TRUNC('day', fecha_cita AT TIME ZONE 'America/Bogota'),
                     TO_CHAR(fecha_cita AT TIME ZONE 'America/Bogota', 'Dy')
            ORDER BY DATE_TRUNC('day', fecha_cita AT TIME ZONE 'America/Bogota')
        """)).fetchall()
        dias   = [r.dia for r in dias_raw] or ["Sin datos"]
        dia_counts = [int(r.n) for r in dias_raw] or [0]

        # ── Citas por franja horaria ───────────────────────────
        horas_raw = db.execute(text("""
            SELECT
                CASE
                    WHEN EXTRACT(HOUR FROM fecha_cita AT TIME ZONE 'America/Bogota') BETWEEN 7  AND 8  THEN '07–09'
                    WHEN EXTRACT(HOUR FROM fecha_cita AT TIME ZONE 'America/Bogota') BETWEEN 9  AND 10 THEN '09–11'
                    WHEN EXTRACT(HOUR FROM fecha_cita AT TIME ZONE 'America/Bogota') BETWEEN 11 AND 12 THEN '11–13'
                    WHEN EXTRACT(HOUR FROM fecha_cita AT TIME ZONE 'America/Bogota') BETWEEN 13 AND 14 THEN '13–15'
                    WHEN EXTRACT(HOUR FROM fecha_cita AT TIME ZONE 'America/Bogota') BETWEEN 15 AND 16 THEN '15–17'
                    WHEN EXTRACT(HOUR FROM fecha_cita AT TIME ZONE 'America/Bogota') BETWEEN 17 AND 18 THEN '17–19'
                    ELSE 'Otro'
                END AS franja,
                COUNT(*) AS n
            FROM appointments
            GROUP BY franja
            ORDER BY franja
        """)).fetchall()
        horas      = [r.franja for r in horas_raw] or ["Sin datos"]
        hora_counts = [int(r.n) for r in horas_raw] or [0]

        # ── Crecimiento acumulado de pacientes (últimos 6 meses) ──
        pac_raw = db.execute(text("""
            SELECT
                TO_CHAR(DATE_TRUNC('month', created_at), 'Mon') AS mes,
                COUNT(*) AS n
            FROM users
            WHERE created_at >= NOW() - INTERVAL '6 months'
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY DATE_TRUNC('month', created_at)
        """)).fetchall()
        meses = [r.mes for r in pac_raw] or ["Sin datos"]
        # acumulado
        pac_acum: list[int] = []
        total = 0
        for r in pac_raw:
            total += int(r.n)
            pac_acum.append(total)
        if not pac_acum:
            pac_acum = [0]

        # ── Métricas globales ─────────────────────────────────
        total_pacientes = int(db.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0)

        nuevos_mes = int(db.execute(text("""
            SELECT COUNT(*) FROM users
            WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', NOW())
        """)).scalar() or 0)

        citas_mes = int(db.execute(text("""
            SELECT COUNT(*) FROM appointments
            WHERE DATE_TRUNC('month', fecha_cita) = DATE_TRUNC('month', NOW())
        """)).scalar() or 0)

        completadas = estados.get("completada", 0)
        canceladas  = estados.get("cancelada",  0)
        total_citas = sum(estados.values())
        tasa = round(completadas / total_citas * 100) if total_citas else 0

        return JSONResponse({
            "estados":        estados,
            "especialidades": [],        # no tienes tabla de especialidades
            "espCounts":      [],
            "dias":           dias,
            "diaCounts":      dia_counts,
            "horas":          horas,
            "horaCounts":     hora_counts,
            "meses":          meses,
            "pacAcum":        pac_acum,
            "totalPacientes": total_pacientes,
            "nuevosEsteMes":  nuevos_mes,
            "citasMes":       citas_mes,
            "tasaAsistencia": tasa,
            "cancelaciones":  canceladas,
        })

    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
class UserBusquedaResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    cedula: str
    email: str
    telefono: Optional[str]

    model_config = {"from_attributes": True}
@router.get(
    "/buscar-usuario",
    response_model=UserBusquedaResponse,
    summary="Buscar paciente por cédula",
)
def buscar_usuario_por_cedula(
    cedula: str = Query(..., description="Cédula del paciente"),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.cedula == cedula).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún paciente con cédula '{cedula}'.",
        )
    return user
# ─── Endpoints CRUD ───────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva cita",
)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
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

# ─── Buscar usuario por cédula (para el panel admin) ─────────────────────────
# Pega este endpoint al final de routes/appointments.py

class UserBusquedaResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    cedula: str
    email: str
    telefono: Optional[str]

    model_config = {"from_attributes": True}


