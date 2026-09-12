"""API tests for health, calculation, and result persistence."""

from __future__ import annotations

from fastapi.testclient import TestClient
from mpd_engine.units.conversions import inch_to_m, lpm_to_m3_s

from app.core.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def _well_payload() -> dict:
    return {
        "name": "EXAMPLE-1",
        "td_m": 3000.0,
        "hole_id_m": inch_to_m(12.25),
        "annular_section_type": "open_hole",
    }


def _scenario_payload() -> dict:
    return {
        "name": "drilling-400-lpm",
        "drillstring": {
            "components": [
                {
                    "name": "drillpipe",
                    "component_type": "drillpipe",
                    "od_m": inch_to_m(5.0),
                    "id_m": inch_to_m(4.276),
                    "length_m": 3000.0,
                }
            ]
        },
        "fluid": {
            "mud_density_kg_m3": 1200.0,
            "plastic_viscosity_pa_s": 0.02,
            "yield_stress_pa": 9.576,
            "temperature_c": 50.0,
            "rheology_model": "bingham_plastic",
        },
        "operating": {
            "flow_rate_m3_s": lpm_to_m3_s(400.0),
            "surface_backpressure_pa": 0.0,
            "operating_mode": "drilling",
            "max_surface_backpressure_pa": 3_447_378.646584,
        },
        "pressure_window": {
            "points": [
                {
                    "tvd_m": 100.0,
                    "pore_pressure_pa": 1_200_000.0,
                    "fracture_pressure_pa": 1_800_000.0,
                    "collapse_pressure_pa": 1_300_000.0,
                },
                {
                    "tvd_m": 3000.0,
                    "pore_pressure_pa": 36_000_000.0,
                    "fracture_pressure_pa": 54_000_000.0,
                    "collapse_pressure_pa": 38_000_000.0,
                },
            ]
        },
        "target_bottomhole_pressure_pa": 40_000_000.0,
        "depth_step_m": 500.0,
    }


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_calculation_endpoint_and_persistence() -> None:
    created = client.post("/api/v1/wells", json=_well_payload())
    assert created.status_code == 201, created.text
    well_id = created.json()["id"]

    listed = client.get("/api/v1/wells")
    assert listed.status_code == 200
    assert any(item["id"] == well_id for item in listed.json())

    fetched = client.get(f"/api/v1/wells/{well_id}")
    assert fetched.status_code == 200

    scenario = client.post(f"/api/v1/wells/{well_id}/scenarios", json=_scenario_payload())
    assert scenario.status_code == 201, scenario.text
    scenario_id = scenario.json()["id"]

    run = client.post(f"/api/v1/scenarios/{scenario_id}/calculate", json={})
    assert run.status_code == 201, run.text
    body = run.json()
    assert body["status"] == "completed"
    assert body["calculation_version"].startswith("1.0.0")
    run_id = body["id"]

    stored = client.get(f"/api/v1/runs/{run_id}")
    assert stored.status_code == 200
    results = client.get(f"/api/v1/runs/{run_id}/results")
    assert results.status_code == 200
    payload = results.json()
    summary = payload["summary"]
    assert summary["bottomhole_pressure_pa"] == (
        summary["hydrostatic_pressure_pa"]
        + summary["annular_friction_pressure_pa"]
        + summary["surface_backpressure_pa"]
    )
    assert payload["profile"]
    assert payload["warnings"]

    csv_response = client.post(f"/api/v1/runs/{run_id}/export/csv")
    assert csv_response.status_code == 200
    assert "annular_pressure_pa" in csv_response.text

    excel_response = client.post(f"/api/v1/runs/{run_id}/export/excel")
    assert excel_response.status_code == 200
    assert excel_response.content[:2] == b"PK"

    pdf_response = client.post(f"/api/v1/runs/{run_id}/export/pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.content.startswith(b"%PDF")


def test_invalid_geometry_returns_422() -> None:
    response = client.post(
        "/api/v1/wells",
        json={"name": "bad", "td_m": 1000.0, "hole_id_m": -0.2},
    )
    assert response.status_code == 422
