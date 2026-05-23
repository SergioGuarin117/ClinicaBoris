from datetime import datetime
from typing import Optional
from enum import Enum
import os

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from database import get_db
from models.user import User

router = APIRouter(prefix="/api/payments", tags=["payments"])


# ─── Enums ────────────────────────────────────────────────────────

class PaymentStatus(str, Enum):
    pagado    = "pagado"
    pendiente = "pendiente"
    vencido   = "vencido"
    parcial   = "parcial"


class PaymentMethod(str, Enum):
    efectivo      = "efectivo"
    tarjeta       = "tarjeta"
    transferencia = "transferencia"
    mercadopago   = "mercadopago"
    otro          = "otro"


# ─── Schemas ──────────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    user_id:  int
    monto:    float
    concepto: str
    fecha:    str
    estado:   PaymentStatus = PaymentStatus.pagado
    metodo:   PaymentMethod = PaymentMethod.efectivo
    notas:    Optional[str] = None


class PaymentUpdate(BaseModel):
    monto:    Optional[float]         = None
    concepto: Optional[str]           = None
    fecha:    Optional[str]           = None
    estado:   Optional[PaymentStatus] = None
    metodo:   Optional[PaymentMethod] = None
    notas:    Optional[str]           = None


class MPCrearRequest(BaseModel):
    cita_id:  int
    user_id:  int
    tipo:     Optional[str] = "estandar"   # estandar | premium


# ─── Precios MercadoPago ──────────────────────────────────────────

PRECIOS = {"estandar": 300_000, "premium": 600_000}
TITULOS = {
    "estandar": "Consulta Estándar — Dr. Boris Viafara",
    "premium":  "Consulta Premium — Dr. Boris Viafara",
}


# ─── Crear tabla si no existe ─────────────────────────────────────
# Se agregan columnas MP sin romper la tabla original

def create_payments_table(db: Session):
    # Tabla original
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

    # Columnas nuevas para MercadoPago (se agregan solo si no existen)
    columnas_mp = [
        ("cita_id",          "INTEGER REFERENCES appointments(id) ON DELETE SET NULL"),
        ("tipo_consulta",    "TEXT"),
        ("mp_preference_id", "TEXT"),
        ("mp_pago_id",       "TEXT"),
    ]
    for col, tipo in columnas_mp:
        db.execute(text(f"""
            ALTER TABLE pagos ADD COLUMN IF NOT EXISTS {col} {tipo}
        """))

    db.commit()


# ─── Helper serializar ────────────────────────────────────────────

def serialize_payment(row) -> dict:
    d = {
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
    # Campos MP opcionales
    for campo in ("cita_id", "tipo_consulta", "mp_preference_id", "mp_pago_id"):
        try:
            d[campo] = getattr(row, campo, None)
        except Exception:
            d[campo] = None
    return d


# ═══════════════════════════════════════════════════════════════════
#  MERCADOPAGO
# ═══════════════════════════════════════════════════════════════════

# ─── POST /api/payments/mp/crear ─────────────────────────────────

@router.post("/mp/crear", summary="Crear preferencia MercadoPago")
def mp_crear(body: MPCrearRequest, db: Session = Depends(get_db)):
    create_payments_table(db)

    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not access_token:
        raise HTTPException(500, "MERCADOPAGO_ACCESS_TOKEN no configurado en .env")

    user = db.get(User, body.user_id)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    # Verificar que la cita existe
    cita = db.execute(
        text("SELECT id FROM appointments WHERE id = :id"),
        {"id": body.cita_id}
    ).fetchone()
    if not cita:
        raise HTTPException(404, "Cita no encontrada")

    monto  = PRECIOS.get(body.tipo, PRECIOS["estandar"])
    titulo = TITULOS.get(body.tipo, TITULOS["estandar"])

    base_url     = os.getenv("BASE_URL",     "http://localhost:8000")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5500")

    try:
        import mercadopago
        sdk = mercadopago.SDK(access_token)

        preference_data = {
            "items": [{
                "id":         str(body.cita_id),
                "title":      titulo,
                "quantity":   1,
                "unit_price": float(monto),
                "currency_id": "COP",
            }],
            "payer": {
                "name":  user.nombre,
                "email": user.email,
            },
            "back_urls": {
                "success": f"{base_url}/api/payments/mp/success",
                "failure": f"{base_url}/api/payments/mp/failure",
                "pending": f"{base_url}/api/payments/mp/pending",
            },
            #"auto_return":          "approved",
            "external_reference":   f"cita_{body.cita_id}_user_{body.user_id}",
            "notification_url":     f"{base_url}/api/payments/mp/webhook",
            "metadata": {
                "cita_id": body.cita_id,
                "user_id": body.user_id,
                "tipo":    body.tipo,
            },
        }

        result   = sdk.preference().create(preference_data)
        response = result["response"]

        if result["status"] not in (200, 201):
            raise HTTPException(500, f"MercadoPago error: {response}")

        preference_id = response["id"]
        init_point    = response["init_point"]
        sandbox_url   = response["sandbox_init_point"]

    except ImportError:
        raise HTTPException(500, "Librería mercadopago no instalada. Ejecuta: pip install mercadopago")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error al crear preferencia: {str(e)}")

    # Guardar en tabla pagos como pendiente
    row = db.execute(text("""
        INSERT INTO pagos
            (user_id, cita_id, monto, concepto, fecha, estado, metodo, tipo_consulta, mp_preference_id)
        VALUES
            (:user_id, :cita_id, :monto, :concepto, NOW()::date, 'pendiente', 'mercadopago', :tipo, :pref_id)
        RETURNING id
    """), {
        "user_id": body.user_id,
        "cita_id": body.cita_id,
        "monto":   monto,
        "concepto": titulo,
        "tipo":    body.tipo,
        "pref_id": preference_id,
    }).fetchone()
    db.commit()

    return {
        "pago_id":       row.id,
        "preference_id": preference_id,
        "init_point":    init_point,
        "sandbox_url":   sandbox_url,
        "monto":         monto,
        "tipo":          body.tipo,
    }


# ─── GET /api/payments/mp/success ────────────────────────────────

@router.get("/mp/success", summary="Callback pago aprobado")
def mp_success(
    payment_id:         Optional[str] = Query(None),
    external_reference: Optional[str] = Query(None),
    status:             Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    create_payments_table(db)

    if external_reference:
        try:
            cita_id = int(external_reference.split("_")[1])
            db.execute(text("""
                UPDATE pagos
                SET estado = 'pagado', mp_pago_id = :pid, updated_at = NOW()
                WHERE cita_id = :cita_id AND metodo = 'mercadopago'
            """), {"pid": payment_id or "", "cita_id": cita_id})
            db.commit()
        except Exception:
            pass

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5500")
    return RedirectResponse(
        url=(f"{frontend_url}/FRONT/src/pago-exitoso.html"
             f"?payment_id={payment_id or ''}"
             f"&ref={external_reference or ''}"
             f"&status={status or 'approved'}"),
        status_code=302,
    )


# ─── GET /api/payments/mp/failure ────────────────────────────────

@router.get("/mp/failure", summary="Callback pago rechazado")
def mp_failure(
    external_reference: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    create_payments_table(db)

    if external_reference:
        try:
            cita_id = int(external_reference.split("_")[1])
            db.execute(text("""
                UPDATE pagos
                SET estado = 'rechazado', updated_at = NOW()
                WHERE cita_id = :cita_id AND metodo = 'mercadopago'
            """), {"cita_id": cita_id})
            db.commit()
        except Exception:
            pass

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5500")
    return RedirectResponse(
        url=f"{frontend_url}/FRONT/src/pago-fallido.html?ref={external_reference or ''}",
        status_code=302,
    )


# ─── GET /api/payments/mp/pending ────────────────────────────────

@router.get("/mp/pending", summary="Callback pago pendiente")
def mp_pending(
    external_reference: Optional[str] = Query(None),
):
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5500")
    return RedirectResponse(
        url=f"{frontend_url}/FRONT/src/pago-pendiente.html?ref={external_reference or ''}",
        status_code=302,
    )


# ─── POST /api/payments/mp/webhook ───────────────────────────────

@router.post("/mp/webhook", summary="Webhook IPN MercadoPago")
async def mp_webhook(request: Request, db: Session = Depends(get_db)):
    create_payments_table(db)

    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"ok": False}, status_code=400)

    topic  = data.get("type")  or data.get("topic", "")
    action = data.get("action", "")

    if topic == "payment" or action in ("payment.updated", "payment.created"):
        payment_id = (data.get("data") or {}).get("id") or data.get("id")
        if payment_id:
            try:
                import mercadopago
                sdk    = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN", ""))
                result = sdk.payment().get(payment_id)
                mp_data = result.get("response", {})
                ext_ref = mp_data.get("external_reference", "")
                mp_status = mp_data.get("status", "")

                estado_map = {
                    "approved":     "pagado",
                    "pending":      "pendiente",
                    "in_process":   "pendiente",
                    "rejected":     "rechazado",
                    "cancelled":    "cancelado",
                    "refunded":     "reembolsado",
                    "charged_back": "contracargo",
                }

                cita_id = int(ext_ref.split("_")[1])
                db.execute(text("""
                    UPDATE pagos
                    SET estado = :estado, mp_pago_id = :pid, updated_at = NOW()
                    WHERE cita_id = :cita_id AND metodo = 'mercadopago'
                """), {
                    "estado":   estado_map.get(mp_status, mp_status),
                    "pid":      str(payment_id),
                    "cita_id":  cita_id,
                })
                db.commit()
            except Exception:
                pass

    return JSONResponse({"ok": True}, status_code=200)


# ═══════════════════════════════════════════════════════════════════
#  RUTAS ORIGINALES (sin cambios)
# ═══════════════════════════════════════════════════════════════════

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
                p.created_at,
                p.cita_id,
                p.tipo_consulta,
                p.mp_preference_id,
                p.mp_pago_id
            FROM pagos p
            JOIN users u ON u.id = p.user_id
            {where}
            ORDER BY p.fecha DESC, p.id DESC
        """), params).fetchall()

        kpis = db.execute(text("""
            SELECT estado, COUNT(*) AS n, COALESCE(SUM(monto),0) AS total
            FROM pagos GROUP BY estado
        """)).fetchall()

        resumen = {r.estado: {"count": int(r.n), "total": float(r.total)} for r in kpis}

        return JSONResponse({
            "pagos":   [serialize_payment(r) for r in rows],
            "resumen": resumen,
        })

    except Exception as exc:
        return JSONResponse({"error": str(exc), "pagos": [], "resumen": {}}, status_code=500)


# ─── POST /api/payments — crear pago manual ───────────────────────

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