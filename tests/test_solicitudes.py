from html.parser import HTMLParser

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.dependencies import get_usuario_actual
from app.main import app
import app.routes.solicitudes as solicitudes_routes
import app.services.solicitudes as solicitudes_service
from app.services.solicitudes import (
    ModoSeleccionServicioInvalido,
    OpcionServicioInvalida,
    _normalizar_opciones_servicio,
)


AREA = "Mantenimiento y Protección Civil"
SUBCATEGORIA = "infraestructura"
OPCIONES_VALIDAS = ["albanileria", "carpinteria"]
MENSAJE_RADIO = "Seleccione exactamente una opción para la subcategoría elegida."
MENSAJE_CHECKBOX = "Seleccione al menos una opción para la subcategoría elegida."
CAMPOS_OPCIONES = (
    "infraestructura",
    "equipo_parque_vehicular",
    "seguridad",
    "transporte",
    "diversos_limpieza",
    "prestamo_de",
    "correspondencia_paqueteria",
    "reproduccion_engargolado",
)


class InputParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "input":
            self.inputs.append(attributes)
        elif tag == "script":
            self.scripts.append(attributes)


class FakeSession:
    def __init__(self):
        self.solicitud = None

    def query(self, model):
        return self

    def count(self):
        return 0

    def add(self, solicitud):
        self.solicitud = solicitud

    def commit(self):
        pass

    def refresh(self, solicitud):
        pass


def normalizar(modo, **opciones):
    opciones_por_campo = {campo: None for campo in CAMPOS_OPCIONES}
    opciones_por_campo.update(opciones)
    return _normalizar_opciones_servicio(
        AREA,
        SUBCATEGORIA,
        modo,
        opciones_por_campo,
    )


def datos_formulario(modo, opciones=None, **extras):
    datos = {
        "area_solicitante": AREA,
        "nombre_usuario": "Usuario de prueba",
        "responsable_area_solicitante": "Responsable de prueba",
        "telefono": "0000000000",
        "descripcion_servicio": "Descripción de prueba",
        "subcategoria_servicio": SUBCATEGORIA,
        "modo_seleccion_servicio": modo,
        "infraestructura": opciones or [],
    }
    datos.update(extras)
    return datos


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[get_usuario_actual] = lambda: {
        "rol": "desarrollador",
        "nombre": "Usuario de prueba",
    }
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_checkbox_con_dos_opciones_es_aceptado_y_conserva_ambas():
    resultado = normalizar("checkbox", infraestructura=OPCIONES_VALIDAS)

    assert resultado[SUBCATEGORIA] == OPCIONES_VALIDAS


def test_checkbox_sin_opciones_devuelve_mensaje_requerido():
    with pytest.raises(OpcionServicioInvalida, match=MENSAJE_CHECKBOX):
        normalizar("checkbox")


def test_radio_con_una_opcion_es_aceptado():
    resultado = normalizar("radio", infraestructura=[OPCIONES_VALIDAS[0]])

    assert resultado[SUBCATEGORIA] == [OPCIONES_VALIDAS[0]]


def test_radio_con_dos_opciones_devuelve_mensaje_requerido():
    with pytest.raises(OpcionServicioInvalida, match=MENSAJE_RADIO):
        normalizar("radio", infraestructura=OPCIONES_VALIDAS)


def test_modo_desconocido_es_rechazado():
    with pytest.raises(ModoSeleccionServicioInvalido, match="Modo de selección"):
        normalizar("desconocido", infraestructura=[OPCIONES_VALIDAS[0]])


def test_opcion_ajena_a_subcategoria_es_rechazada():
    with pytest.raises(OpcionServicioInvalida, match="deben pertenecer"):
        normalizar(
            "checkbox",
            infraestructura=[OPCIONES_VALIDAS[0]],
            seguridad=["control_accesos"],
        )


def test_formulario_renderiza_modos_nativos_y_javascript_versionado(client):
    response = client.get("/solicitud")
    parser = InputParser()
    parser.feed(response.text)
    modos = [
        control
        for control in parser.inputs
        if control.get("name") == "modo_seleccion_servicio"
    ]

    assert response.status_code == 200
    assert {control.get("value") for control in modos} == {"radio", "checkbox"}
    assert all(control.get("type") == "radio" for control in modos)
    assert sum("checked" in control for control in modos) == 1
    assert any(script.get("src") == "/static/js/solicitud.js?v=2" for script in parser.scripts)


def test_post_checkbox_entrega_checkbox_al_backend(client, monkeypatch):
    recibido = {}
    db = FakeSession()
    crear_solicitud_original = solicitudes_routes.crear_solicitud

    def capturar_modo(db, **valores):
        recibido.update(valores)
        return crear_solicitud_original(db, **valores)

    app.dependency_overrides[get_db] = lambda: db
    monkeypatch.setattr(solicitudes_routes, "crear_solicitud", capturar_modo)
    monkeypatch.setattr(solicitudes_service, "agregar_solicitud", lambda solicitud: None)
    response = client.post(
        "/solicitud",
        data=datos_formulario("checkbox", OPCIONES_VALIDAS),
    )

    assert response.status_code == 200
    assert recibido["modo_seleccion_servicio"] == "checkbox"
    assert recibido[SUBCATEGORIA] == OPCIONES_VALIDAS
    assert db.solicitud.infraestructura == OPCIONES_VALIDAS


def test_post_con_modo_desconocido_devuelve_400(client):
    response = client.post(
        "/solicitud",
        data=datos_formulario("desconocido", [OPCIONES_VALIDAS[0]]),
    )

    assert response.status_code == 400
    assert "Modo de selección de servicio inválido." in response.text


def test_error_400_conserva_modo_multiple_y_opciones_elegidas(client):
    response = client.post(
        "/solicitud",
        data=datos_formulario(
            "checkbox",
            OPCIONES_VALIDAS,
            seguridad=["control_accesos"],
        ),
    )
    parser = InputParser()
    parser.feed(response.text)

    modo_checkbox = next(
        control
        for control in parser.inputs
        if control.get("name") == "modo_seleccion_servicio"
        and control.get("value") == "checkbox"
    )
    opciones_marcadas = {
        control.get("value")
        for control in parser.inputs
        if control.get("name") == SUBCATEGORIA and "checked" in control
    }

    assert response.status_code == 400
    assert "checked" in modo_checkbox
    assert opciones_marcadas == set(OPCIONES_VALIDAS)


def test_post_radio_con_una_opcion_continua_funcionando(client, monkeypatch):
    recibido = {}
    db = FakeSession()
    crear_solicitud_original = solicitudes_routes.crear_solicitud

    def capturar_modo(db, **valores):
        recibido.update(valores)
        return crear_solicitud_original(db, **valores)

    app.dependency_overrides[get_db] = lambda: db
    monkeypatch.setattr(solicitudes_routes, "crear_solicitud", capturar_modo)
    monkeypatch.setattr(solicitudes_service, "agregar_solicitud", lambda solicitud: None)
    response = client.post(
        "/solicitud",
        data=datos_formulario("radio", [OPCIONES_VALIDAS[0]]),
    )

    assert response.status_code == 200
    assert recibido["modo_seleccion_servicio"] == "radio"
    assert recibido[SUBCATEGORIA] == [OPCIONES_VALIDAS[0]]
    assert db.solicitud.infraestructura == [OPCIONES_VALIDAS[0]]
