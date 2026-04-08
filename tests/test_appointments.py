"""
test_appointments.py — Tests para los endpoints de citas de ClinicaBoris.

Cubre:
  - Crear cita para usuario existente
  - Crear cita para usuario inexistente (404)
  - Crear cita con fecha en el pasado (422)
  - Listar todas las citas
  - Filtrar citas por user_id y estado
  - Obtener cita por ID
  - Actualizar estado de cita
  - Eliminar cita
  - Cita no encontrada (404)
"""
import pytest
from datetime import datetime, timedelta, timezone


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def fecha_futura(dias=7) -> str:
    """Devuelve una fecha ISO en el futuro (por defecto 7 días)."""
    dt = datetime.now(timezone.utc) + timedelta(days=dias)
    return dt.isoformat()


def fecha_pasada(dias=1) -> str:
    """Devuelve una fecha ISO en el pasado."""
    dt = datetime.now(timezone.utc) - timedelta(days=dias)
    return dt.isoformat()


def crear_cita(client, user_id: int, dias=7, motivo="Consulta general") -> dict:
    """Helper para crear una cita y retornar sus datos."""
    resp = client.post(
        "/api/appointments/",
        json={
            "user_id": user_id,
            "fecha_cita": fecha_futura(dias),
            "motivo": motivo,
        },
    )
    assert resp.status_code == 201, f"No se pudo crear cita: {resp.text}"
    return resp.json()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS DE CREACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrearCita:

    def test_crear_cita_exitosa(self, client, usuario_registrado):
        """Crear cita para usuario existente debe retornar 201 con estado pendiente."""
        resp = client.post(
            "/api/appointments/",
            json={
                "user_id": usuario_registrado["id"],
                "fecha_cita": fecha_futura(5),
                "motivo": "Revisión post-operatoria",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["user_id"] == usuario_registrado["id"]
        assert data["estado"] == "pendiente"
        assert data["motivo"] == "Revisión post-operatoria"
        assert "id" in data
        assert "created_at" in data

    def test_crear_cita_estado_inicial_es_pendiente(self, client, usuario_registrado):
        """El estado inicial de cualquier cita nueva siempre debe ser 'pendiente'."""
        cita = crear_cita(client, usuario_registrado["id"])
        assert cita["estado"] == "pendiente"

    def test_crear_cita_con_notas(self, client, usuario_registrado):
        """Crear cita con campo notas debe guardarse correctamente."""
        resp = client.post(
            "/api/appointments/",
            json={
                "user_id": usuario_registrado["id"],
                "fecha_cita": fecha_futura(3),
                "motivo": "Control",
                "notas": "Paciente alérgico a penicilina",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["notas"] == "Paciente alérgico a penicilina"

    def test_crear_cita_sin_motivo(self, client, usuario_registrado):
        """El motivo es opcional, debe crearse sin él."""
        resp = client.post(
            "/api/appointments/",
            json={
                "user_id": usuario_registrado["id"],
                "fecha_cita": fecha_futura(4),
            },
        )
        assert resp.status_code == 201
        assert resp.json()["motivo"] is None

    def test_crear_cita_usuario_inexistente(self, client):
        """Crear cita para un user_id que no existe debe retornar 404."""
        resp = client.post(
            "/api/appointments/",
            json={
                "user_id": 99999,
                "fecha_cita": fecha_futura(5),
            },
        )
        assert resp.status_code == 404
        assert "99999" in resp.json()["detail"]

    def test_crear_cita_fecha_en_pasado(self, client, usuario_registrado):
        """Crear cita con fecha pasada debe retornar 422."""
        resp = client.post(
            "/api/appointments/",
            json={
                "user_id": usuario_registrado["id"],
                "fecha_cita": fecha_pasada(2),
            },
        )
        assert resp.status_code == 422

    def test_crear_cita_retorna_id_unico(self, client, usuario_registrado):
        """Dos citas creadas deben tener IDs diferentes."""
        cita1 = crear_cita(client, usuario_registrado["id"], dias=5)
        cita2 = crear_cita(client, usuario_registrado["id"], dias=10)
        assert cita1["id"] != cita2["id"]


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS DE LISTADO
# ═══════════════════════════════════════════════════════════════════════════════

class TestListarCitas:

    def test_listar_citas_vacio(self, client):
        """Sin citas en la DB debe retornar lista vacía."""
        resp = client.get("/api/appointments/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_listar_citas_con_datos(self, client, usuario_registrado):
        """Con citas creadas debe retornar todas."""
        crear_cita(client, usuario_registrado["id"], dias=3)
        crear_cita(client, usuario_registrado["id"], dias=6)
        resp = client.get("/api/appointments/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_filtrar_por_user_id(self, client, usuario_registrado):
        """Filtrar por user_id debe retornar solo las citas de ese usuario."""
        crear_cita(client, usuario_registrado["id"], dias=3)
        crear_cita(client, usuario_registrado["id"], dias=6)
        resp = client.get(f"/api/appointments/?user_id={usuario_registrado['id']}")
        assert resp.status_code == 200
        citas = resp.json()
        assert len(citas) == 2
        for cita in citas:
            assert cita["user_id"] == usuario_registrado["id"]

    def test_filtrar_por_user_id_inexistente(self, client, usuario_registrado):
        """Filtrar por user_id que no tiene citas debe retornar lista vacía."""
        crear_cita(client, usuario_registrado["id"])
        resp = client.get("/api/appointments/?user_id=99999")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_filtrar_por_estado_pendiente(self, client, usuario_registrado):
        """Filtrar por estado=pendiente debe retornar solo citas pendientes."""
        crear_cita(client, usuario_registrado["id"], dias=3)
        crear_cita(client, usuario_registrado["id"], dias=6)
        resp = client.get("/api/appointments/?estado=pendiente")
        assert resp.status_code == 200
        citas = resp.json()
        assert len(citas) == 2
        for cita in citas:
            assert cita["estado"] == "pendiente"

    def test_citas_ordenadas_por_fecha(self, client, usuario_registrado):
        """Las citas deben venir ordenadas por fecha_cita ascendente."""
        crear_cita(client, usuario_registrado["id"], dias=10)
        crear_cita(client, usuario_registrado["id"], dias=3)
        resp = client.get("/api/appointments/")
        citas = resp.json()
        assert citas[0]["fecha_cita"] < citas[1]["fecha_cita"]


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS DE OBTENER POR ID
# ═══════════════════════════════════════════════════════════════════════════════

class TestObtenerCita:

    def test_obtener_cita_existente(self, client, usuario_registrado):
        """Obtener una cita por ID válido debe retornar sus datos."""
        cita = crear_cita(client, usuario_registrado["id"])
        resp = client.get(f"/api/appointments/{cita['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == cita["id"]
        assert resp.json()["user_id"] == usuario_registrado["id"]

    def test_obtener_cita_inexistente(self, client):
        """Obtener cita con ID que no existe debe retornar 404."""
        resp = client.get("/api/appointments/99999")
        assert resp.status_code == 404
        assert "99999" in resp.json()["detail"]


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS DE ACTUALIZACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class TestActualizarCita:

    def test_confirmar_cita(self, client, usuario_registrado):
        """Cambiar estado a 'confirmada' debe funcionar correctamente."""
        cita = crear_cita(client, usuario_registrado["id"])
        resp = client.patch(
            f"/api/appointments/{cita['id']}",
            json={"estado": "confirmada"},
        )
        assert resp.status_code == 200
        assert resp.json()["estado"] == "confirmada"

    def test_cancelar_cita(self, client, usuario_registrado):
        """Cambiar estado a 'cancelada' debe funcionar correctamente."""
        cita = crear_cita(client, usuario_registrado["id"])
        resp = client.patch(
            f"/api/appointments/{cita['id']}",
            json={"estado": "cancelada"},
        )
        assert resp.status_code == 200
        assert resp.json()["estado"] == "cancelada"

    def test_completar_cita(self, client, usuario_registrado):
        """Cambiar estado a 'completada' debe funcionar correctamente."""
        cita = crear_cita(client, usuario_registrado["id"])
        resp = client.patch(
            f"/api/appointments/{cita['id']}",
            json={"estado": "completada"},
        )
        assert resp.status_code == 200
        assert resp.json()["estado"] == "completada"

    def test_actualizar_notas(self, client, usuario_registrado):
        """Actualizar las notas de una cita debe persistir el cambio."""
        cita = crear_cita(client, usuario_registrado["id"])
        resp = client.patch(
            f"/api/appointments/{cita['id']}",
            json={"notas": "Nuevo seguimiento requerido"},
        )
        assert resp.status_code == 200
        assert resp.json()["notas"] == "Nuevo seguimiento requerido"

    def test_actualizar_cita_inexistente(self, client):
        """Actualizar una cita que no existe debe retornar 404."""
        resp = client.patch(
            "/api/appointments/99999",
            json={"estado": "confirmada"},
        )
        assert resp.status_code == 404

    def test_actualizar_fecha_en_pasado(self, client, usuario_registrado):
        """Actualizar la fecha a una fecha pasada debe retornar 422."""
        cita = crear_cita(client, usuario_registrado["id"])
        resp = client.patch(
            f"/api/appointments/{cita['id']}",
            json={"fecha_cita": fecha_pasada(1)},
        )
        assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS DE ELIMINACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class TestEliminarCita:

    def test_eliminar_cita_existente(self, client, usuario_registrado):
        """Eliminar cita existente debe retornar 204 sin contenido."""
        cita = crear_cita(client, usuario_registrado["id"])
        resp = client.delete(f"/api/appointments/{cita['id']}")
        assert resp.status_code == 204

    def test_cita_eliminada_no_existe(self, client, usuario_registrado):
        """Después de eliminar, obtener la cita debe retornar 404."""
        cita = crear_cita(client, usuario_registrado["id"])
        client.delete(f"/api/appointments/{cita['id']}")
        resp = client.get(f"/api/appointments/{cita['id']}")
        assert resp.status_code == 404

    def test_eliminar_cita_inexistente(self, client):
        """Eliminar una cita que no existe debe retornar 404."""
        resp = client.delete("/api/appointments/99999")
        assert resp.status_code == 404

    def test_eliminar_reduce_total_citas(self, client, usuario_registrado):
        """Eliminar una cita debe reducir el total de citas en la lista."""
        crear_cita(client, usuario_registrado["id"], dias=3)
        cita2 = crear_cita(client, usuario_registrado["id"], dias=6)
        client.delete(f"/api/appointments/{cita2['id']}")
        resp = client.get("/api/appointments/")
        assert len(resp.json()) == 1
