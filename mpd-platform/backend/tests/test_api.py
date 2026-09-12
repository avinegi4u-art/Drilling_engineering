"""API tests for health, CRUD, calculation, persistence, and errors."""

from __future__ import annotations

from fastapi.testclient import TestClient
from mpd_engine.units.conversions import inch_to_m, lpm_to_m3_s


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


def _error(response) -> dict:
    body = response.json()
    assert "error" in body, body
    assert "code" in body["error"] and "message" in body["error"], body
    return body["error"]


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_well_crud(client: TestClient) -> None:
    created = client.post("/api/v1/wells", json=_well_payload())
    assert created.status_code == 201, created.text
    well_id = created.json()["id"]
    assert created.json()["well"]["name"] == "EXAMPLE-1"

    listed = client.get("/api/v1/wells")
    assert listed.status_code == 200
    assert any(item["id"] == well_id for item in listed.json())

    fetched = client.get(f"/api/v1/wells/{well_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == well_id


def test_missing_well_returns_structured_404(client: TestClient) -> None:
    response = client.get("/api/v1/wells/does-not-exist")
    assert response.status_code == 404
    error = _error(response)
    assert error["code"] == "NOT_FOUND"
    assert error["message"] == "Well not found"


def test_invalid_geometry_returns_structured_422(client: TestClient) -> None:
    response = client.post(
        "/api/v1/wells",
        json={"name": "bad", "td_m": 1000.0, "hole_id_m": -0.2},
    )
    assert response.status_code == 422
    error = _error(response)
    assert error["code"] == "INVALID_GEOMETRY"
    assert "hole_id_m" in str(error["message"])


def test_validation_error_envelope(client: TestClient) -> None:
    response = client.post("/api/v1/wells", json={"name": "incomplete"})
    assert response.status_code == 422
    error = _error(response)
    assert error["code"] in {"INVALID_GEOMETRY", "VALIDATION_ERROR"}


def test_scenario_and_calculation_persistence(client: TestClient) -> None:
    created = client.post("/api/v1/wells", json=_well_payload())
    well_id = created.json()["id"]

    missing_well = client.post(
        "/api/v1/wells/missing/scenarios", json=_scenario_payload()
    )
    assert missing_well.status_code == 404
    assert _error(missing_well)["code"] == "NOT_FOUND"

    scenario = client.post(f"/api/v1/wells/{well_id}/scenarios", json=_scenario_payload())
    assert scenario.status_code == 201, scenario.text
    scenario_id = scenario.json()["id"]
    assert scenario.json()["well_id"] == well_id

    listed = client.get(f"/api/v1/wells/{well_id}/scenarios")
    assert listed.status_code == 200
    assert any(item["id"] == scenario_id for item in listed.json())

    fetched = client.get(f"/api/v1/scenarios/{scenario_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "drilling-400-lpm"

    missing_scenario = client.get("/api/v1/scenarios/missing")
    assert missing_scenario.status_code == 404
    assert _error(missing_scenario)["code"] == "NOT_FOUND"

    run = client.post(f"/api/v1/scenarios/{scenario_id}/calculate", json={})
    assert run.status_code == 201, run.text
    body = run.json()
    assert body["status"] == "completed"
    assert body["calculation_version"].startswith("1.0.0")
    assert body["assumptions"]
    run_id = body["id"]

    runs = client.get("/api/v1/runs")
    assert runs.status_code == 200
    assert any(item["id"] == run_id for item in runs.json())

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


def test_missing_run_returns_structured_404(client: TestClient) -> None:
    response = client.get("/api/v1/runs/missing/results")
    assert response.status_code == 404
    assert _error(response)["code"] == "NOT_FOUND"


def test_invalid_scenario_inputs_return_422(client: TestClient) -> None:
    created = client.post("/api/v1/wells", json=_well_payload())
    well_id = created.json()["id"]
    payload = _scenario_payload()
    payload["drillstring"]["components"][0]["length_m"] = 10.0
    response = client.post(f"/api/v1/wells/{well_id}/scenarios", json=payload)
    assert response.status_code == 422
    error = _error(response)
    assert error["code"] == "INVALID_INPUT"
