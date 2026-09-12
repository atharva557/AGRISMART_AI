# AgriSmart AI

Crop disease detection and smart agriculture advisory for the SIH 2026 internal hackathon.

**Status:** Bonus modules A-D are integrated into the Flask API and interactive dashboard. A exposes an explicitly dataset-scoped crop classifier, B provides an evidence-aware soil-water-balance advisory, C validates and evaluates live Open-Meteo forecasts, and D applies a published resource-intensity formula. The mandatory crop-disease core and bonus E remain placeholders. Saved A/B benchmark results and limitations are documented in the [A/B audit](report/bonus_ab_data_audit.md); they do not establish field suitability, optimal irrigation, or measured resource savings.

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
  weights/                 # Evaluated A serving artifact; other local weights ignored
notebooks/                 # Core starters and bonus A-D experiment notebooks
services/
  disease_info.py          # Sourced disease precautions
  crop_recommendation.py   # A dataset-scoped model serving and validation
  irrigation.py            # B calibrated soil-water-balance logic
  weather.py               # C forecast fetching, validation, and alerts
  sustainability.py        # D transparent whole-cycle comparison
  contracts.py             # A-D response envelope and HTTP status mapping
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
| GET | `/` | Interactive A-D dashboard |
| GET | `/result` | Empty result template |
| GET | `/api/health` | JSON health status |
| POST | `/api/disease/predict` | 501, not implemented |
| POST | `/api/crops/recommend` | A: experimental top-three dataset-label ranking |
| POST | `/api/irrigation/advise` | B: soil-water-balance action and volume calculation |
| POST | `/api/weather/advise` | C: fresh forecast summary and threshold-based alerts |
| POST | `/api/sustainability/score` | D: simulated or measured-input resource comparison |
| POST | `/api/assistant/chat` | 501, not implemented |

The A-D endpoints require the versioned request envelope and explicit units/evidence described in [the shared input contract](docs/bonus_input_contract.md). They return `422` when data are missing, invalid, stale, or unsupported, and `503` when a required model/provider is unavailable. The disease endpoint should accept a validated multipart `image` upload when implemented. Do not commit or publicly serve user uploads.

Advisory responses should include the recommendation, reasons, sources, and missing inputs. Module E should explain actual service outputs and sourced guidance. Module D must publish its exact formula and distinguish indicative scores from measured savings.

The [A-D shared input contract](docs/bonus_input_contract.md) defines units, evidence, time periods, missing-data handling, and cross-module boundaries. [Example requests](docs/examples/bonus_contract_examples.json) cover supported demonstrations and deliberate rejection cases. The [A/B data audit](report/bonus_ab_data_audit.md) records trained artifacts and saved results, checks source integrity, and identifies field-input gaps.

## Model and evaluation

The required inference entry point is `predict(image_path) -> class_label` in `model/predict.py`, with this CLI:

```sh
python -m model.predict --image path/to/leaf.jpg
```

It currently exits with an explicit error because no trained model is available. Add architecture dependencies when selected. Keep weights out of Git and document a reproducible download, checksum, and load path when ready.

Use the organizers' exact class list, interface, and split. `classes.json` is deliberately empty. Training/validation use the provided lab-condition data; official judging uses separate field-condition data. Never train or tune on the held-out judging set.

Report macro-F1, accuracy, confusion matrix, and per-class precision/recall. Keep local validation and official test results distinct. Core evaluation integration remains pending in this local scaffold; saved bonus benchmark results are summarized in the A/B audit. Record dataset sources, licenses, pretrained backbones, and any reused third-party code as they are added. External datasets are stored locally in ignored directories.

## Checks and submission

With the Python environment active:

```sh
python -m unittest discover -s tests -v
```

These checks cover the Flask shell, A model inference, B and D formulas, C rule evaluation with deterministic provider data, and explicit A-D failure states. They do not retrain models or independently reproduce saved benchmark metrics. The first six core notebooks contain starter headings; use `model/` for reusable core experiment code. A real `tests/sample_leaf.jpg` can be added locally from permitted data; none is bundled.

## Irrigation notebook

`notebooks/07_irrigation_baseline.ipynb` contains an offline, rule-based irrigation prototype with assumed crop-stage profiles, simulated soil/weather inputs, decision explanations, a comparison chart, and sanity checks. It does not train a model or demonstrate real water savings. The Flask service now implements a stricter calibrated soil-water-balance path and labels assumed inputs as simulation.

Install the separate notebook dependencies and open JupyterLab from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-notebooks.txt
.\.venv\Scripts\python.exe -m jupyterlab notebooks/07_irrigation_baseline.ipynb
```

On macOS/Linux, use `python` with the virtual environment activated. In JupyterLab or VS Code, select the project's Python environment and run all cells. Edit the final example to try another simulated farm. Source references and validation limitations are included in the notebook.

## Train an irrigation model

`notebooks/08_irrigation_model_training.ipynb` is the supervised training notebook for the user to run. It uses [Mendeley field data, version 3](https://data.mendeley.com/datasets/cjb4vy4mzj/3) to predict an observed irrigation start within the next hour when the valve is currently closed. It learns one field's controller behavior, not universally optimal irrigation needs.

1. Install `requirements-notebooks.txt` using the project's Python environment.
2. Open notebook 08 and run the cells yourself. The loader tries the official file downloads.
3. If downloads are blocked, use the source page to download `D_moisture.txt` and `D_valve.txt` into `data/irrigation/raw/`, then rerun the loader. Preserve the original file bytes so the published checksums match.
4. Review the chronological split, train the models, and inspect the validation comparison before final test evaluation.
5. The final cell saves a model under `model/weights/irrigation/` and metrics/figures under `outputs/`.

The notebook compares majority and single-moisture-split baselines with logistic regression and random forest. Model and decision-threshold selection use validation data only. The user's saved run selected random forest; its test results and limitations are in the [A/B audit](report/bonus_ab_data_audit.md). No training or notebook-cell execution was performed while preparing notebook 08 or auditing its saved results.

See [dataset selection and limitations](report/irrigation_data_selection.md) and the [source-file manifest](report/irrigation_dataset_manifest.json). The saved classifier remains a controller-behavior benchmark; the Flask farm-advisory path deliberately uses the transparent water balance instead.

## Bonus notebooks: A, C, D

Use the same `requirements-notebooks.txt` environment and run the notebooks yourself:

| Module | Notebook | What it prepares |
| --- | --- | --- |
| A — Crop recommendation | [09_crop_recommendation_training.ipynb](notebooks/09_crop_recommendation_training.ipynb) | Source validation, four classifier baselines, validation selection, held-out evaluation, top-three candidates, model export |
| C — Weather advisory | [10_weather_advisory.ipynb](notebooks/10_weather_advisory.ipynb) | Open-Meteo forecasts, configurable alert rules, explicit offline demo, timestamps, units, caching, plots |
| D — Sustainability | [11_sustainability_scoring.ipynb](notebooks/11_sustainability_scoring.ipynb) | Transparent resource-use formula, comparable baseline inputs, yield check, simulated scenarios, report export |

Notebook 09 uses a verified 2,200-row crop dataset. Its nutrient scales and rainfall aggregation period need validation before real farm inputs or weather integration. Notebook 10 defaults to live forecasts for editable Pune coordinates; select `MODE = "demo"` for offline simulated inputs. Notebook 11 uses simulated records by default; its custom score does not establish measured savings. Only notebook 09 trains a model.

The user has executed these notebooks and produced local artifacts. The evaluated A serving model, its training report, validation comparison, and confusion matrix are deliberately packaged so a clean checkout can run A; other generated artifacts remain ignored. Reusable A-D logic is connected to the Flask endpoints, and the API preserves the notebook limitations and data-kind labels. See the [bonus notebook guide](report/bonus_notebooks_guide.md) and [source manifest](report/bonus_modules_sources.json) for details.

Before submission, complete the mandatory disease core and report, add its real evaluation evidence, verify a clean setup can reproduce both core and bonus predictions in approximately 10 minutes, and add the 3–5 minute demo video and deployment link. Follow the brief's 10–15 September work window and preserve authentic development history.
