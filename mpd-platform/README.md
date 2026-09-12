# MPD Hydraulics Dashboard

Web-based Managed Pressure Drilling (MPD) hydraulics application for
engineering decision support.

This application **does not** implement automatic choke control and **does
not** send commands to field equipment.

## Architecture

The calculation engine (`engine/mpd_engine`) is independent of FastAPI and
Streamlit. Engineering equations are not duplicated in API routes or
dashboard pages.

```text
dashboard (Streamlit)  -->  backend (FastAPI)  -->  mpd_engine
                                     |
                                     v
                               PostgreSQL
```

Internal units are SI (`m`, `Pa`, `kg/m³`, `m³/s`). Convert at the UI/API
boundary.

## Version 1 engineering assumptions

- Steady-state, single-phase hydraulics
- Vertical well (TVD = MD)
- One well section with constant annular diameter
- Constant mud density
- Bingham Plastic rheology
- Incompressible single-phase drilling fluid
- No temperature correction, gas influx, cuttings loading, surge/swab, or transients
- No automated control

Annular friction uses a **narrow-slot Bingham Plastic approximation**. That
correlation is an engineering screening model and is marked for independent
validation. Version 1 does not switch to a turbulent Blasius model
automatically, because dropping the yield-stress term at Re = 2100 would
create a non-physical friction decrease. A warning is issued when the
plastic-viscosity Reynolds number exceeds 2100.

## Repository layout

```text
mpd-platform/
├── backend/          FastAPI + SQLAlchemy + Alembic
├── engine/           Standalone hydraulics engine
├── dashboard/        Streamlit UI
├── examples/         Invented sample data only
├── docker-compose.yml
├── Makefile
└── .env.example
```

## Development

Python 3.12+ is required.

```bash
cd mpd-platform
python3 -m venv .venv
source .venv/bin/activate
make install-engine
make install-backend
make test-engine
make test-backend
make lint-engine
make typecheck-engine
```

Run the API and dashboard locally. Tests use in-memory SQLite.
Runtime PostgreSQL is configured with `DATABASE_URL` or `POSTGRES_*`
(see `.env.example`). For a local SQLite API process:

```bash
export DATABASE_URL=sqlite:///./mpd.db
make api
# in another shell
make dashboard
```

Open http://localhost:8501 and http://localhost:8000/docs.

Copy `.env.example` to `.env` before using Docker Compose. Do not put secrets
in source files.

```bash
docker compose up --build
```

Sample well data lives in `examples/sample_well.json`. It is invented
development data, not field measurements.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness |
| POST | `/api/v1/wells` | Create well |
| GET | `/api/v1/wells` | List wells |
| GET | `/api/v1/wells/{well_id}` | Get well |
| POST | `/api/v1/wells/{well_id}/scenarios` | Create scenario |
| GET | `/api/v1/wells/{well_id}/scenarios` | List scenarios for a well |
| GET | `/api/v1/scenarios/{scenario_id}` | Get scenario |
| POST | `/api/v1/scenarios/{scenario_id}/calculate` | Run hydraulics (synchronous) |
| GET | `/api/v1/runs` | List calculation runs |
| GET | `/api/v1/runs/{run_id}` | Run metadata |
| GET | `/api/v1/runs/{run_id}/results` | Results |
| POST | `/api/v1/runs/{run_id}/export/csv` | CSV |
| POST | `/api/v1/runs/{run_id}/export/excel` | Excel |
| POST | `/api/v1/runs/{run_id}/export/pdf` | PDF |

Version 1 has no authentication and no background job queue.

## Safety

Failed validation raises errors. The engine does not substitute default
values for invalid inputs. Warnings are engineering review notices, not
operational commands.
