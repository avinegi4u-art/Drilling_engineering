"""API-level tests exercising the FastAPI endpoints end to end."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_index_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "Drilling Engineering Toolkit" in res.text


def test_hydrostatic_pressure_endpoint():
    res = client.post(
        "/api/hydrostatic-pressure", json={"mud_weight_ppg": 9.5, "tvd_ft": 10000}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["value"] == 4940.0
    assert body["unit"] == "psi"


def test_ecd_endpoint():
    res = client.post(
        "/api/ecd",
        json={"mud_weight_ppg": 9.5, "annular_pressure_loss_psi": 250, "tvd_ft": 10000},
    )
    assert res.status_code == 200
    assert res.json()["value"] == 9.9808


def test_annular_velocity_validation_error():
    res = client.post(
        "/api/annular-velocity",
        json={"flow_rate_gpm": 500, "hole_diameter_in": 5.0, "pipe_diameter_in": 8.5},
    )
    assert res.status_code == 422


def test_dogleg_endpoint():
    res = client.post(
        "/api/dogleg-severity",
        json={
            "inclination_1_deg": 10,
            "azimuth_1_deg": 0,
            "inclination_2_deg": 20,
            "azimuth_2_deg": 0,
            "course_length_ft": 100,
        },
    )
    assert res.status_code == 200
    assert res.json()["value"] == 10.0


def test_kill_mud_weight_endpoint():
    res = client.post(
        "/api/kill-mud-weight",
        json={"current_mud_weight_ppg": 9.5, "sidpp_psi": 300, "tvd_ft": 10000},
    )
    assert res.status_code == 200
    assert res.json()["unit"] == "ppg"
