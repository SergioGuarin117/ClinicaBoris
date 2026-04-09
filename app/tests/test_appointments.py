"""
test_appointments.py — Tests para los endpoints de citas de ClinicaBoris.
"""
import pytest
from datetime import datetime, timedelta, timezone


def fecha_futura(dias=7) -> str:
    dt = datetime.now(timezone.utc) + timedelta(days=dias)
    return dt.isoformat()


def fecha_pasada(dias=1) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=dias)
    return dt.isoformat()


async def crear_cita(client, user_id: int, dias=7, motivo="Consulta general") -> dict:
    resp = await client.post(
        "/api/appointments/",
        json={
            "user_id": user_id,
            "fecha_cita": fecha_futura(dias),
            "motivo": motivo,
        },
    )
    assert resp.status_code == 201, f"No se pudo crear cita: {resp.text}"
    return resp.json()


class TestCrearCita:

    @pytest.mark.asyncio
    async def test_crear_cita_exitosa(self, client, usuario_registrado):
        resp = await client.post(
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

    @pytest.mark.asyncio
    async def test_crear_cita_estado_inicial_es_pendiente(self, client, usuario_registrado):
        cita = await crear_cita(client, usuario_registrado["id"])
        assert cita["estado"] == "pendiente"

    @pytest.mark.asyncio
    async def test_crear_cita_con_notas(self, client, usuario_registrado):
        resp = await client.post(
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

    @pytest.mark.asyncio
    async def test_crear_cita_sin_motivo(self, client, usuario_registrado):
        resp = await client.post(
            "/api/appointments/",
            json={
                "user_id": usuario_registrado["id"],
                "fecha_cita": fecha_futura(4),
            },
        )
        assert resp.status_code == 201
        assert resp.json()["motivo"] is None

    @pytest.mark.asyncio
    async def test_crear_cita_usuario_inexistente(self, client):
        resp = await client.post(
            "/api/appointments/",
            json={
                "user_id": 99999,
                "fecha_cita": fecha_futura(5),
            },
        )
        assert resp.status_code == 404
        assert "99999" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_crear_cita_fecha_en_pasado(self, client, usuario_registrado):
        resp = await client.post(
            "/api/appointments/",
            json={
                "user_id": usuario_registrado["id"],
                "fecha_cita": fecha_pasada(2),
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_crear_cita_retorna_id_unico(self, client, usuario_registrado):
        cita1 = await crear_cita(client, usuario_registrado["id"], dias=5)
        cita2 = await crear_cita(client, usuario_registrado["id"], dias=10)
        assert cita1["id"] != cita2["id"]


class TestListarCitas:

    @pytest.mark.asyncio
    async def test_listar_citas_vacio(self, client):
        resp = await client.get("/api/appointments/")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_listar_citas_con_datos(self, client, usuario_registrado):
        await crear_cita(client, usuario_registrado["id"], dias=3)
        await crear_cita(client, usuario_registrado["id"], dias=6)
        resp = await client.get("/api/appointments/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    @pytest.mark.asyncio
    async def test_filtrar_por_user_id(self, client, usuario_registrado):
        await crear_cita(client, usuario_registrado["id"], dias=3)
        await crear_cita(client, usuario_registrado["id"], dias=6)
        resp = await client.get(f"/api/appointments/?user_id={usuario_registrado['id']}")
        assert resp.status_code == 200
        citas = resp.json()
        assert len(citas) == 2
        for cita in citas:
            assert cita["user_id"] == usuario_registrado["id"]

    @pytest.mark.asyncio
    async def test_filtrar_por_user_id_inexistente(self, client, usuario_registrado):
        await crear_cita(client, usuario_registrado["id"])
        resp = await client.get("/api/appointments/?user_id=99999")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_filtrar_por_estado_pendiente(self, client, usuario_registrado):
        await crear_cita(client, usuario_registrado["id"], dias=3)
        await crear_cita(client, usuario_registrado["id"], dias=6)
        resp = await client.get("/api/appointments/?estado=pendiente")
        assert resp.status_code == 200
        citas = resp.json()
        assert len(citas) == 2
        for cita in citas:
            assert cita["estado"] == "pendiente"

    @pytest.mark.asyncio
    async def test_citas_ordenadas_por_fecha(self, client, usuario_registrado):
        await crear_cita(client, usuario_registrado["id"], dias=10)
        await crear_cita(client, usuario_registrado["id"], dias=3)
        resp = await client.get("/api/appointments/")
        citas = resp.json()
        assert citas[0]["fecha_cita"] < citas[1]["fecha_cita"]


class TestObtenerCita:

    @pytest.mark.asyncio
    async def test_obtener_cita_existente(self, client, usuario_registrado):
        cita = await crear_cita(client, usuario_registrado["id"])
        resp = await client.get(f"/api/appointments/{cita['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == cita["id"]
        assert resp.json()["user_id"] == usuario_registrado["id"]

    @pytest.mark.asyncio
    async def test_obtener_cita_inexistente(self, client):
        resp = await client.get("/api/appointments/99999")
        assert resp.status_code == 404
        assert "99999" in resp.json()["detail"]


class TestActualizarCita:

    @pytest.mark.asyncio
    async def test_confirmar_cita(self, client, usuario_registrado):
        cita = await crear_cita(client, usuario_registrado["id"])
        resp = await client.patch(
            f"/api/appointments/{cita['id']}",
            json={"estado": "confirmada"},
        )
        assert resp.status_code == 200
        assert resp.json()["estado"] == "confirmada"

    @pytest.mark.asyncio
    async def test_cancelar_cita(self, client, usuario_registrado):
        cita = await crear_cita(client, usuario_registrado["id"])
        resp = await client.patch(
            f"/api/appointments/{cita['id']}",
            json={"estado": "cancelada"},
        )
        assert resp.status_code == 200
        assert resp.json()["estado"] == "cancelada"

    @pytest.mark.asyncio
    async def test_completar_cita(self, client, usuario_registrado):
        cita = await crear_cita(client, usuario_registrado["id"])
        resp = await client.patch(
            f"/api/appointments/{cita['id']}",
            json={"estado": "completada"},
        )
        assert resp.status_code == 200
        assert resp.json()["estado"] == "completada"

    @pytest.mark.asyncio
    async def test_actualizar_notas(self, client, usuario_registrado):
        cita = await crear_cita(client, usuario_registrado["id"])
        resp = await client.patch(
            f"/api/appointments/{cita['id']}",
            json={"notas": "Nuevo seguimiento requerido"},
        )
        assert resp.status_code == 200
        assert resp.json()["notas"] == "Nuevo seguimiento requerido"

    @pytest.mark.asyncio
    async def test_actualizar_cita_inexistente(self, client):
        resp = await client.patch(
            "/api/appointments/99999",
            json={"estado": "confirmada"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_actualizar_fecha_en_pasado(self, client, usuario_registrado):
        cita = await crear_cita(client, usuario_registrado["id"])
        resp = await client.patch(
            f"/api/appointments/{cita['id']}",
            json={"fecha_cita": fecha_pasada(1)},
        )
        assert resp.status_code == 422


class TestEliminarCita:

    @pytest.mark.asyncio
    async def test_eliminar_cita_existente(self, client, usuario_registrado):
        cita = await crear_cita(client, usuario_registrado["id"])
        resp = await client.delete(f"/api/appointments/{cita['id']}")
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_cita_eliminada_no_existe(self, client, usuario_registrado):
        cita = await crear_cita(client, usuario_registrado["id"])
        await client.delete(f"/api/appointments/{cita['id']}")
        resp = await client.get(f"/api/appointments/{cita['id']}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_eliminar_cita_inexistente(self, client):
        resp = await client.delete("/api/appointments/99999")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_eliminar_reduce_total_citas(self, client, usuario_registrado):
        await crear_cita(client, usuario_registrado["id"], dias=3)
        cita2 = await crear_cita(client, usuario_registrado["id"], dias=6)
        await client.delete(f"/api/appointments/{cita2['id']}")
        resp = await client.get("/api/appointments/")
        assert len(resp.json()) == 1