# Drilling engineering — MPD Hydraulics Platform

Apache-licensed workspace for drilling-engineering software.

The first application in this repository is a **Managed Pressure Drilling (MPD)
Hydraulics Dashboard**. It is **engineering decision support only**. It does
not send commands to chokes, pumps, or other field equipment.

## Current status

**Phase 1 is implemented:** project layout, Python packaging, validated domain
models, SI unit conversions, and engine unit tests.

Not implemented yet: hydraulics equations, FastAPI persistence, Streamlit
workflows, exports, Docker services, WITSML, or any control interface.

## Layout

```text
mpd-platform/
├── backend/          FastAPI service (Phase 4)
├── engine/           Calculation engine (independent of UI and API)
├── dashboard/        Streamlit UI (Phase 5)
├── examples/         Synthetic sample data only
└── docker-compose.yml
```

The calculation engine (`mpd-platform/engine`) has no FastAPI or Streamlit
imports. Engineering equations will live only under `mpd_engine/hydraulics`
and `mpd_engine/mpd`.

## Version 1 engineering assumptions

These assumptions are part of the public contract. Failed inputs raise
validation errors; they are not replaced with defaults.

- SI units internally (Pa, kg/m³, m, m³/s, Pa·s)
- Vertical well, one or more well sections
- Constant mud density
- Bingham Plastic rheology only
- Incompressible single-phase fluid
- No temperature correction, gas influx, cuttings, surge/swab, or transients
- No automated choke control

Display units (psi, ppg, L/min, ft, cP, mm) are converted at the application
boundary by `mpd_engine.units.conversions`.

## Development

Requires Python 3.12+.

```bash
python3 -m pip install -e "./mpd-platform/engine[dev]"
make test-engine
```

Equivalent pytest command:

```bash
cd mpd-platform/engine && python3 -m pytest -v
```

## Sample data

`mpd-platform/examples/sample_well.json` is a **synthetic** vertical well used
by tests. It is not field data.

## License

Apache License 2.0. See `LICENSE`.
