from datetime import datetime
from typing import Optional
from enum import Enum
 
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
 
from database import get_db
from models.user import User
 
router = APIRouter(prefix="/api/payments", tags=["payments"])
 
 
# ─── Enum de estados ──────────────────────────────────────────────
 
class PaymentStatus(str, Enum):
    pagado    = "pagado"
    pendiente = "pendiente"
    vencido   = "vencido"
    parcial   = "parcial"
 
 
class PaymentMethod(str, Enum):
    efectivo      = "efectivo"
    tarjeta       = "tarjeta"
    transferencia = "transferencia"
    otro          = "otro"
 
 
# ─── Schemas ──────────────────────────────────────────────────────
 
class PaymentCreate(BaseModel):
    user_id:  int
    monto:    float
    concepto: str
    fecha:    str               # formato "YYYY-MM-DD"
    estado:   PaymentStatus  = PaymentStatus.pagado
    metodo:   PaymentMethod  = PaymentMethod.efectivo
    notas:    Optional[str]  = None
 
 
class PaymentUpdate(BaseModel):
    monto:    Optional[float]         = None
    concepto: Optional[str]           = None
    fecha:    Optional[str]           = None
    estado:   Optional[PaymentStatus] = None
    metodo:   Optional[PaymentMethod] = None
    notas:    Optional[str]           = None
 
 
# ─── Crear tabla si no existe ─────────────────────────────────────
 
def create_payments_table(db: Session):
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS pagos (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            monto      NUMERIC(12,2) NOT NULL,
            concepto   TEXT NOT NULL,
            fecha      DATE NOT NULL,
            estado     TEXT NOT NULL DEFAULT 'pagado',
            metodo     TEXT NOT NULL DEFAULT 'efectivo',
            notas      TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))
    db.commit()
 
 
# ─── Helper serializar ────────────────────────────────────────────
 
def serialize_payment(row) -> dict:
    return {
        "id":         row.id,
        "user_id":    row.user_id,
        "paciente":   row.paciente,
        "cedula":     row.cedula,
        "monto":      float(row.monto),
        "concepto":   row.concepto,
        "fecha":      str(row.fecha),
        "estado":     row.estado,
        "metodo":     row.metodo,
        "notas":      row.notas,
        "created_at": str(row.created_at),
    }
 
 
# ─── GET /api/payments — listar todos ─────────────────────────────
 
@router.get("/", summary="Listar pagos")
def list_payments(
    estado: str = Query("todos"),
    buscar: str = Query(""),
    db: Session = Depends(get_db),
):
    create_payments_table(db)
    try:
        conditions = []
        params = {}
 
        if estado and estado != "todos":
            conditions.append("p.estado = :estado")
            params["estado"] = estado
 
        if buscar:
            conditions.append("(u.nombre ILIKE :buscar OR u.apellido ILIKE :buscar OR u.cedula ILIKE :buscar)")
            params["buscar"] = f"%{buscar}%"
 
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
 
        rows = db.execute(text(f"""
            SELECT
                p.id,
                p.user_id,
                u.nombre || ' ' || u.apellido AS paciente,
                u.cedula,
                p.monto,
                p.concepto,
                p.fecha::text AS fecha,
                p.estado,
                p.metodo,
                p.notas,
                p.created_at
            FROM pagos p
            JOIN users u ON u.id = p.user_id
            {where}
            ORDER BY p.fecha DESC, p.id DESC
        """), params).fetchall()
 
        # KPIs
        kpis = db.execute(text("""
            SELECT
                estado,
                COUNT(*)            AS n,
                COALESCE(SUM(monto),0) AS total
            FROM pagos
            GROUP BY estado
        """)).fetchall()
 
        resumen = {r.estado: {"count": int(r.n), "total": float(r.total)} for r in kpis}
 
        return JSONResponse({
            "pagos":   [serialize_payment(r) for r in rows],
            "resumen": resumen,
        })
 
    except Exception as exc:
        return JSONResponse({"error": str(exc), "pagos": [], "resumen": {}}, status_code=500)
 
 
# ─── POST /api/payments — crear pago ──────────────────────────────
 
@router.post("/", status_code=status.HTTP_201_CREATED, summary="Crear pago")
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    create_payments_table(db)
 
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"Usuario con id={payload.user_id} no encontrado.")
 
    try:
        row = db.execute(text("""
            INSERT INTO pagos (user_id, monto, concepto, fecha, estado, metodo, notas)
            VALUES (:user_id, :monto, :concepto, :fecha, :estado, :metodo, :notas)
            RETURNING id, user_id, monto, concepto, fecha::text, estado, metodo, notas, created_at
        """), {
            "user_id":  payload.user_id,
            "monto":    payload.monto,
            "concepto": payload.concepto,
            "fecha":    payload.fecha,
            "estado":   payload.estado.value,
            "metodo":   payload.metodo.value,
            "notas":    payload.notas,
        }).fetchone()
        db.commit()
 
        return {
            "id":        row.id,
            "user_id":   row.user_id,
            "paciente":  f"{user.nombre} {user.apellido}",
            "cedula":    user.cedula,
            "monto":     float(row.monto),
            "concepto":  row.concepto,
            "fecha":     row.fecha,
            "estado":    row.estado,
            "metodo":    row.metodo,
            "notas":     row.notas,
            "created_at": str(row.created_at),
        }
 
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
 
 
# ─── PATCH /api/payments/{id} — actualizar pago ───────────────────
 
@router.patch("/{payment_id}", summary="Actualizar pago")
def update_payment(payment_id: int, payload: PaymentUpdate, db: Session = Depends(get_db)):
    create_payments_table(db)
 
    exists = db.execute(text("SELECT id FROM pagos WHERE id = :id"), {"id": payment_id}).fetchone()
    if not exists:
        raise HTTPException(status_code=404, detail=f"Pago con id={payment_id} no encontrado.")
 
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar.")
 
    # Convertir enums a string
    if "estado" in data and data["estado"]:
        data["estado"] = data["estado"].value if hasattr(data["estado"], "value") else data["estado"]
    if "metodo" in data and data["metodo"]:
        data["metodo"] = data["metodo"].value if hasattr(data["metodo"], "value") else data["metodo"]
 
    sets = ", ".join([f"{k} = :{k}" for k in data.keys()])
    data["payment_id"] = payment_id
    data["updated_at"] = datetime.now()
 
    try:
        db.execute(text(f"""
            UPDATE pagos SET {sets}, updated_at = :updated_at
            WHERE id = :payment_id
        """), data)
        db.commit()
 
        row = db.execute(text("""
            SELECT p.*, u.nombre || ' ' || u.apellido AS paciente, u.cedula
            FROM pagos p JOIN users u ON u.id = p.user_id
            WHERE p.id = :id
        """), {"id": payment_id}).fetchone()
 
        return serialize_payment(row)
 
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
 
 
# ─── DELETE /api/payments/{id} — eliminar pago ────────────────────
 
@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar pago")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    create_payments_table(db)
 
    exists = db.execute(text("SELECT id FROM pagos WHERE id = :id"), {"id": payment_id}).fetchone()
    if not exists:
        raise HTTPException(status_code=404, detail=f"Pago con id={payment_id} no encontrado.")
 
    try:
        db.execute(text("DELETE FROM pagos WHERE id = :id"), {"id": payment_id})
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))