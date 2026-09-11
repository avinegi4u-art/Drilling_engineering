# Drilling_engineering

Drilling engineer related software.

## Drilling Engineering Toolkit

A small FastAPI web application providing common drilling-engineering
calculators (wellbore hydraulics and well control) with a modern browser UI.

### Calculators

| Calculator | Formula | Output |
| --- | --- | --- |
| Hydrostatic pressure | `0.052 × MW × TVD` | psi |
| Equivalent circulating density (ECD) | `MW + APL / (0.052 × TVD)` | ppg |
| Buoyancy factor | `(65.5 − MW) / 65.5` | dimensionless |
| Annular velocity | `24.51 × Q / (Dh² − Dp²)` | ft/min |
| Dogleg severity | minimum-curvature dogleg angle, normalized per 100 ft | deg/100ft |
| Kill mud weight | `MW + SIDPP / (0.052 × TVD)` | ppg |

Units are oilfield standard: mud weight in ppg, depth/length in ft, pressure in
psi, diameters in inches, flow rate in gpm.

## Getting started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload --port 8000
```

Then open http://localhost:8000 in your browser.

### API

Interactive API docs are available at http://localhost:8000/docs. Example:

```bash
curl -X POST http://localhost:8000/api/hydrostatic-pressure \
  -H 'Content-Type: application/json' \
  -d '{"mud_weight_ppg": 9.5, "tvd_ft": 10000}'
# -> {"value": 4940.0, "unit": "psi"}
```

## Testing

```bash
pytest
```

## Project layout

```
app/
  main.py           FastAPI app: API routes + serves the frontend
  calculations.py   Pure drilling-engineering formulas
  static/           Frontend (HTML/CSS/JS)
tests/              Unit and API tests
requirements.txt    Python dependencies
.cursor/            Cloud Agent environment configuration
```
