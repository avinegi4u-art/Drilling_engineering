# mpd-engine

Standalone Managed Pressure Drilling (MPD) hydraulics calculation engine.

This package is independent of FastAPI and Streamlit. It can be imported from
scripts, notebooks, the API, the dashboard, or future background jobs.

**Decision support only.** The engine does not send commands to field equipment.

## Version 1 scope

Steady-state, single-phase, Bingham Plastic hydraulics in SI units.

Hydraulics equations are implemented in later phases. This package currently
provides:

- Validated domain models
- Unit conversions
- Input validation helpers
