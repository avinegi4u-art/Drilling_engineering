# mpd-engine

Standalone Managed Pressure Drilling (MPD) hydraulics calculation engine.

This package is independent of FastAPI and Streamlit. It can be imported from
Python scripts, Jupyter notebooks, API services, dashboards, and future
background jobs.

## Version 1 scope

Steady-state, single-phase, Bingham Plastic hydraulics in SI units.

Hydraulics functions are implemented in a later phase. Phase 1 provides:

- Validated domain models
- Unit conversions
- Input validation helpers
