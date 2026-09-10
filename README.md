# AgriSmart AI

Crop disease detection and smart agriculture advisory for the SIH 2026 internal hackathon.

**Status:** Flask project scaffold. Pages, static assets, and health checks work. The disease model and bonus modules are not implemented; feature endpoints return HTTP 501. No accuracy, evaluation, or resource-saving results are claimed.

## Structure

```text
run.py                     # Local entry point
config.py                  # Environment-based configuration
requirements.txt
app/
  __init__.py              # Flask application factory
  routes/                  # Pages, disease, A-D advisory, and assistant routes
  templates/               # index.html and result.html
  static/                  # CSS and browser JavaScript
model/
  train.py                 # Training entry point
  evaluate.py              # Evaluation entry point
  predict.py               # Single-image prediction interface
  model_loader.py          # Weight and class loading
  classes.json             # Official ordered labels, pending kickoff data
  weights/                 # Local weights, ignored by Git
notebooks/                 # Six empty experiment starting points
services/
  disease_info.py          # Sourced disease precautions
  crop_recommendation.py   # A
  irrigation.py            # B
  weather.py               # C
  sustainability.py        # D
  farmer_assistant.py      # E
utils/                     # Image preprocessing and metric helpers
data/                      # Local datasets, ignored by Git
outputs/                   # Local figures, metrics, and predictions
uploads/                   # Local uploads, ignored by Git
report/model_report.md     # Model report template
tests/                     # Application and inference contract checks
```

`run.py` avoids using the same name for the entry-point file and the `app/` package. Flask serves HTML and static files directly; Node.js and a separate frontend server are not needed.

## Setup

Requires Python 3.11 or later. From the repository root:

```sh
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe run.py
```

macOS / Linux:

```sh
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python run.py
```

Copy the environment example only on first setup; preserve any existing local values. No API keys are needed for the scaffold. Never commit real credentials.

Open http://127.0.0.1:5000. For optional local debug/reload mode, use `python -m flask --app run:app run --debug`. These commands start a development server; production deployment is pending.

## Team ownership

| Owner | Primary scope |
| --- | --- |
| Core ML teammate | `model/`, `notebooks/`, `utils/`, `report/`; core inference integration |
| Atharva | Crop recommendation, irrigation, weather, sustainability services; `app/routes/advisory.py` |
| Assistant teammate | `services/farmer_assistant.py`, `app/routes/assistant.py` |
| Integration teammate | Configuration, shared app setup, API contracts, deployment; support for core evaluation |
| Frontend teammate | `app/templates/`, `app/static/`, page integration |

Use feature branches and pull requests. Keep model code in `model/`, decision logic in `services/`, and request/response handling in routes. Coordinate shared-file changes before editing them.

## Endpoints and integration

| Method | Route | Current behavior |
| --- | --- | --- |
| GET | `/` | Home scaffold |
| GET | `/result` | Empty result template |
| GET | `/api/health` | JSON health status |
| POST | `/api/disease/predict` | 501, not implemented |
| POST | `/api/crops/recommend` | 501, not implemented |
| POST | `/api/irrigation/advise` | 501, not implemented |
| POST | `/api/weather/advise` | 501, not implemented |
| POST | `/api/sustainability/score` | 501, not implemented |
| POST | `/api/assistant/chat` | 501, not implemented |

Before implementation, agree on JSON fields for crop, growth stage, location, soil, water availability, and season. Include explicit units, moisture calibration/basis, source timestamps, and missing-input handling. The disease endpoint should accept a validated multipart `image` upload when implemented. Do not commit or publicly serve user uploads.

Advisory responses should include the recommendation, reasons, sources, and missing inputs. Module E should explain actual service outputs and sourced guidance. Module D must publish its exact formula and distinguish indicative scores from measured savings.

## Model and evaluation

The required inference entry point is `predict(image_path) -> class_label` in `model/predict.py`, with this CLI:

```sh
python -m model.predict --image path/to/leaf.jpg
```

It currently exits with an explicit error because no trained model is available. Add architecture dependencies when selected. Keep weights out of Git and document a reproducible download, checksum, and load path when ready.

Use the organizers' exact class list, interface, and split. `classes.json` is deliberately empty. Training/validation use the provided lab-condition data; official judging uses separate field-condition data. Never train or tune on the held-out judging set.

Report macro-F1, accuracy, confusion matrix, and per-class precision/recall. Keep local validation and official test results distinct. All results and baseline comparisons are pending. Record dataset sources, licenses, pretrained backbones, and any reused third-party code as they are added. No dataset or notebook solution is bundled.

## Checks and submission

With the Python environment active:

```sh
python -m unittest discover -s tests -v
```

These checks cover scaffold behavior, not model accuracy. The notebooks contain only starter headings; use `model/` for reusable experiment code. A real `tests/sample_leaf.jpg` can be added locally from permitted data; none is bundled.

Before submission, complete the core and report, add real evaluation evidence and source/license attributions, validate bonus modules, verify a clean setup can reproduce a prediction in approximately 10 minutes, and add the 3–5 minute demo video and deployment link if available. Follow the brief's 10–15 September work window and preserve authentic development history.
