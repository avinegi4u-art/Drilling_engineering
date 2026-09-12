# MPD Hydraulics Dashboard

Web-based Managed Pressure Drilling (MPD) hydraulics application for
engineering decision support.

This application **does not** implement automatic choke control and **does
not** send commands to field equipment.

## Current status: Phase 1

Phase 1 provides the project skeleton and a standalone calculation-engine
foundation:

- Validated SI domain models (well, drillstring, fluid, pressure window,
  operating conditions)
- Unit conversions (psi, kPa, bar, ppg, kg/m³, L/min, bbl/min, ft, m, mm,
  inch, cP)
- Input validation (NaN/Inf, geometry, depth monotonicity, TVD ≤ MD,
  pressure-window ordering)
- Engine unit tests

Hydraulics equations, FastAPI persistence, Streamlit pages, and exports
are implemented in later phases. Placeholder modules exist so the folder
layout is stable.

## Architecture

The calculation engine (`engine/mpd_engine`) is independent of FastAPI and
Streamlit. It can be imported from:

- Python scripts
- Jupyter notebooks
- FastAPI endpoints (later)
- Streamlit pages (later)
- Future background jobs

Engineering equations must not be placed in Streamlit pages or API route
files.

Internal units are SI:

| Quantity | Internal unit |
| --- | --- |
| Length | m |
| Pressure | Pa |
| Density | kg/m³ |
| Flow | m³/s |
| Viscosity | Pa·s |

Convert at the application boundary. Never mix units inside an engineering
calculation.

## Version 1 engineering assumptions

- Steady-state, single-phase hydraulics
- Vertical well (TVD = MD)
- One well section
- Constant mud density
- Bingham Plastic rheology
- Incompressible single-phase drilling fluid
- No temperature effects
- No gas influx
- No cuttings-loading correction
- No surge and swab
- No transient multiphase model
- No automated control

These assumptions will be attached to stored calculation results in a later
phase.

## Repository layout

```text
mpd-platform/
├── backend/          FastAPI service (Phase 4)
├── engine/           Standalone hydraulics engine (Phase 1 in progress)
├── dashboard/        Streamlit UI (Phase 5)
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
make test-engine
make lint-engine
make typecheck-engine
```

Copy `.env.example` to `.env` before using Docker Compose. Do not put
secrets in source files.

Sample well data lives in `examples/sample_well.json`. It is invented
development data, not field measurements.

## Safety

Failed validation raises errors. The engine does not substitute default
values for invalid inputs. Warnings added in later phases are engineering
review notices, not operational commands.
