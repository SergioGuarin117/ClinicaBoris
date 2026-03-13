from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    cedula = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    telefono = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    rol = Column(String, default="paciente", nullable=False)   # paciente | admin | medico
    habeas_data = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ── Relación con citas ───────────────────────────────────────────────────
    appointments = relationship(
        "Appointment",
        back_populates="user",
        foreign_keys="Appointment.user_id",
        cascade="all, delete-orphan",
    )