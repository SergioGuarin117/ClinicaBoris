import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class AppointmentStatus(str, enum.Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    cancelada = "cancelada"
    completada = "completada"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    # ── Trazabilidad de usuario ──────────────────────────────────────────────
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="appointments")

    # ── Fecha y hora de la cita ──────────────────────────────────────────────
    fecha_cita = Column(DateTime(timezone=True), nullable=False)

    # ── Estado ───────────────────────────────────────────────────────────────
    estado = Column(
        Enum(AppointmentStatus),
        default=AppointmentStatus.pendiente,
        nullable=False,
        index=True,
    )

    # ── Campos de soporte ────────────────────────────────────────────────────
    motivo = Column(String(255), nullable=True)       # motivo de la consulta
    notas = Column(Text, nullable=True)               # notas internas del sistema

    # ── Auditoría ────────────────────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)