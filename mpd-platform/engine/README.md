# mpd-engine

Standalone Managed Pressure Drilling (MPD) hydraulics calculation engine.

This package is independent of FastAPI and Streamlit. It can be imported from
Python scripts, Jupyter notebooks, API services, dashboards, and future
background jobs.

## Version 1 scope

Steady-state, single-phase, Bingham Plastic hydraulics in SI units.

Public entry point: `mpd_engine.services.run_hydraulics`.

Annular friction uses a narrow-slot Bingham approximation and is marked as an
engineering screening correlation, not a validated field model.
