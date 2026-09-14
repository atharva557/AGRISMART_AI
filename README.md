# AgriSmart AI — Smart Agricultural Diagnostics & Precision Advisory Platform

## Judge entry point and current evidence

**This is a working prototype.** Historical PlantVillage validation: **0.9969 macro-F1 / 99.85% accuracy** on 10,861 images. Historical field sample: **11/34 correct (32.4%)**. Neither is the organizers' held-out score. Current compressed checkpoints and EXIF-orientation handling have not received a new full benchmark.

**Still pending:** exact organizer labels/split and baseline, official field results, team-confirmed originality declaration, and the recorded demo URL. The model currently has 38 PlantVillage classes; compatibility with the final kickoff subset is unverified.

- [Concise model report](report/model_report.md) and [historical detailed evidence](report/historical_validation_report.md).
- [Submission checklist](docs/SUBMISSION_CHECKLIST.md), [originality draft and references](docs/ORIGINALITY.md), [four-minute demo script](docs/JUDGE_DEMO.md).
- **Demo URL:** pending recording. **Deployed app:** not supplied; run locally using the setup below.

### New farmer workflow

Start at `/disease`: choose an optional crop, upload one leaf photo and optionally add a live forecast or explicitly simulated weather example. Very small or nearly blank/dark/overexposed photos receive retake steps. Possible blur is advisory. A low model score or selected-crop mismatch withholds disease-specific guidance in both the result and assistant. Weather source, time window and simulation status travel with the same scan into the assistant.

These quality rules are experimental: they do not detect unrelated objects, calibrate confidence or establish improved field accuracy. Weather cannot establish irrigation volume or confirm a disease. Irrigation and sustainability inputs remain separate, explicit demonstrations. No sensor-feed integration (F) or continuous autonomous agent (G) is claimed.

### One prediction and evaluation

From the repository root, using an existing permitted photograph (sample images are local and absent from fresh clones):

```powershell
python -m model.predict --image "C:\path\to\leaf.jpg"
```

Default stdout is only the raw class label; `--details` adds diagnostics. Python interface: `from model.predict import predict; label = predict(image_path)`. Web uncertainty policy does not remove samples from the classifier's mandatory label output.

```powershell
# Loads saved weights; without organizer labels, reports pending and exits 2.
python -m model.submission_check
# When the exact organizer list is available:
python -m model.submission_check --labels "C:\path\to\organizer_classes.json"
# User-run independent local evaluation; never trains or executes notebooks:
python -m model.evaluate --manifest data/field_eval/manifest.csv --labels model/classes.json --dataset-name "Independent field development set" --output outputs/field_eval/run-01
```

See [evaluation protocol](docs/FIELD_EVALUATION.md) for the manifest contract, per-class metrics, confusion matrix and confidence-coverage analysis. Do not rename or silently discard classes to hide organizer incompatibility. Never train or tune on the organizers' held-out set.

> **Smart India Hackathon (SIH 2026)** | AI-Powered Multiclass Crop Pathology Detection & Precision Farming Advisory System

---

## 1. Executive Overview

**AgriSmart AI** is a hackathon prototype combining crop-image classification, experimental advisory tools and a contextual multilingual assistant. The main unresolved challenge is generalization from laboratory leaves to field photographs.

---

## 2. Core Functional Modules

```
                                  AGRISMART AI PLATFORM
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                                                                                         │
 │   Module 1: Plant Pathology Engine         Module 2: Crop Recommendation                │
 │   • ConvNeXt-Tiny (384px) SOTA Model       • 7-Feature Soil & Nutrient Matching         │
 │   • 38 Pathology Classes (14 Crops)        • Top-3 Ranked Crop Suitability Candidates   │
 │   • 99.85% Validation Accuracy             • Multi-Classifier Machine Learning Model    │
 │                                                                                         │
 │   Module 3: Smart Irrigation Balance       Module 4: Dynamic Weather Intelligence       │
 │   • Root-Zone Soil Water Balance           • Live Open-Meteo Forecast Integration       │
 │   • Water Deficit & Volume Calculations    • Real-Time Risk Alerts (Frost/Heat/Rain)    │
 │   • Evapotranspiration (ET₀) Tracking      • Proactive Field Protection Warnings        │
 │                                                                                         │
 │   Module 5: Sustainability Scoring         Module 6: Multilingual GenAI Assistant       │
 │   • Water, Energy & Nitrogen Benchmarking  • Powered by Google Gemini LLM               │
 │   • Resource Efficiency Optimization       • Grounded Agronomic Context & Symptoms     │
 │   • Yield Safeguard & Eco Ratings          • Multi-turn Q&A in Regional Languages       │
 │                                                                                         │
 └─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Module 1: Computer Vision Plant Pathology Diagnostic Engine
- **Primary Architecture:** High-precision **ConvNeXt-Tiny (384px)** deep learning model achieving **99.85% validation accuracy** and **0.9969 Macro-F1** across 38 crop pathology categories (14 distinct crops and healthy foliage).
- **Automated Fallback:** ResNet-18 (224px) baseline model ready for resource-constrained deployments.
- **Uncertainty policy:** A 75% model-score threshold withholds disease-specific guidance for uncertain predictions. This threshold is not a safety guarantee; incorrect high-score predictions remain possible.
- **Agronomic Knowledge Base:** Provides reference descriptions, symptoms and precautions from `DISEASE_KB`; these are not symptoms or severity measured from the uploaded image. Independent source validation remains pending.

### Module 2: Precision Crop Recommendation Engine
- **Multi-Nutrient Analysis:** Evaluates soil Nitrogen (N), Phosphorus (P), Potassium (K), pH, rainfall, temperature, and humidity.
- **Candidate Ranking:** Identifies and ranks the top-3 optimal crop candidates for specific field parameters.

### Module 3: Smart Irrigation & Soil-Water Advisory
- **Soil-Water Balance Modeling:** Implements a root-zone depletion formula accounting for field capacity, wilting point, effective root depth, and crop coefficient ($K_c$).
- **Volume Deficit Calculations:** Calculates precise irrigation requirements in liters and cubic meters ($m^3$) per hectare to prevent water stress and over-irrigation.

### Module 4: Dynamic Weather Intelligence & Agronomic Alerts
- **Live Forecast Tracking:** Integrates 24-hour Open-Meteo hourly meteorological data based on GPS coordinates.
- **Automated Risk Alerts:** Evaluates field risks including frost conditions, heat stress, heavy rainfall, high wind velocities, and excessive humidity.

### Module 5: Sustainability & Resource Optimization
- **Resource Comparison:** Compares supplied baseline/current water, electricity and nitrogen totals per hectare. Demo baselines are assumptions, not verified regional standards.
- **Sustainability Index:** Computes a composite efficiency score (0–100) with a yield-retention safeguard.

### Module 6: Multilingual GenAI Farmer Assistant
- **Contextual Agricultural AI:** Google Gemini receives the scan and reference facts, with template fallback. This reduces reliance on free-form generation but does not eliminate factual errors; disease-reference validation remains incomplete.
- **Regional Accessibility:** Supports multi-turn conversational guidance in **English, Hindi, Marathi, Telugu, Tamil, Gujarati, and Bengali**.

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Deep Learning & ML** | PyTorch, Torchvision, Timm (`convnext_tiny`), Scikit-Learn, Joblib, NumPy, Pandas |
| **Generative AI** | Google GenAI SDK (Gemini API), deep-translator |
| **Backend Framework** | Python 3.11+, Flask 3.1, Werkzeug |
| **Frontend & UI** | Tailwind CSS 3.3, Webpack 5, Vanilla ES6+ JavaScript, PostCSS, Autoprefixer |
| **External APIs** | Open-Meteo Weather Forecast API |

---

## 4. Quickstart & Installation

### Prerequisites
- **Python 3.11** or higher
- **Node.js (v16+)** & **npm** (for compiling frontend assets)
- Optional: CUDA-compatible GPU for accelerated deep learning inference

### Step-by-Step Setup

```powershell
# 1. Clone repository & enter directory
git clone https://github.com/atharva557/AGRISMART_AI.git
cd AGRISMART_AI

# 2. (Optional) Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install Python dependencies
python -m pip install -r requirements.txt

# 4. Install Node.js packages & build frontend production assets
npm install
npm run build:all

# 5. Configure environment variables (Optional: Add Gemini API key for Assistant)
copy .env.example .env

# 6. Launch the AgriSmart AI web server
python run.py
```

Access the application in your browser at: **`http://127.0.0.1:5000`**

---

## 5. Web Interface Routes & REST API

### Web Interface Views

| Page | URL Route | Description |
| :--- | :--- | :--- |
| **Home** | `/` | Platform landing page, system health indicator, and overview |
| **Disease Detection** | `/disease` | Drag-and-drop leaf photo diagnosis with live results |
| **Advisory Suite** | `/advisory` | Precision advisory tools (Crop, Irrigation, Weather, Sustainability) |
| **About & Docs** | `/about` | Architecture overview, dataset provenance, and team methodology |

### REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status check |
| `POST` | `/api/disease/predict` | Upload leaf image (multipart) -> Full pathology diagnostic report |
| `POST` | `/api/crops/recommend` | Soil nutrients & weather inputs -> Ranked top-3 crop recommendations |
| `POST` | `/api/irrigation/advise` | Root-zone soil parameters -> Water deficit & required volume ($m^3$) |
| `POST` | `/api/weather/advise` | Coordinates -> Live forecast summary & agricultural hazard alerts |
| `POST` | `/api/sustainability/score` | Resource consumption vs baseline -> Sustainability efficiency score |
| `POST` | `/api/assistant/chat` | Multi-turn contextual chat with grounded GenAI Farmer Assistant |

---

## 6. Model Benchmarks (Plant Pathology Classifier)

Historical reported results on **10,861 validation samples** (PlantVillage 80/20 train-val split). These scores have not been independently revalidated for the current FP16-compressed checkpoints or EXIF-orientation handling and do not establish field-photo accuracy:

| Model Architecture | Input Resolution | Macro-F1 | Top-1 Accuracy | Avg GPU Latency | Checkpoint Location |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ConvNeXt-Tiny (Champion)** | **384 × 384** | **0.9969** | **99.85%** | **24.5 ms** | `model/weights/cv/model_v3.pkl.gz` |
| **ResNet-50 (Enhanced)** | 224 × 224 | 0.9946 | 99.67% | 5.4 ms | `model/weights/cv/model_v2.pkl.gz` |
| **ResNet-18 (Baseline)** | 224 × 224 | 0.9912 | 99.43% | 7.6 ms | `model/weights/cv/model_v1.pkl.gz` |

The first prediction lazily loads the model; subsequent predictions reuse it. Concurrent first-time loads are serialized. This cache is per server process, with ResNet-18 as a fallback if ConvNeXt cannot load. Git LFS is no longer required for the compressed checkpoints.

See [inference reliability fixes and verification](docs/INFERENCE_HARDENING.md) for upload errors, cache lifecycle, test commands, and remaining limitations.

---

## 7. Project Directory Structure

```
AGRISMART_AI/
├── app/                        # Flask Web Application
│   ├── routes/                 # API & view blueprints (disease, advisory, assistant, main)
│   ├── static/                 # Static CSS, JS, images, and compiled dist bundles
│   └── templates/              # Jinja2 HTML templates & reusable UI components
├── model/                      # ML Inference & Checkpoints
│   ├── classes.json            # 38 local model labels; organizer alignment pending
│   ├── model_loader.py         # Singleton cached PyTorch model loader
│   ├── predict.py              # CLI & Python inference engine
│   └── weights/                # Serialized model checkpoints
│       ├── cv/                 # ConvNeXt-Tiny (v3), ResNet-50 (v2), ResNet-18 (v1)
│       └── crop_recommendation/# Random Forest crop ranking weights
├── services/                   # Business Logic & Advisory Services
│   ├── crop_recommendation.py  # Precision crop matching logic
│   ├── disease_info.py         # Curated agronomic pathology knowledge base (DISEASE_KB)
│   ├── farmer_assistant.py     # GenAI Assistant integration
│   ├── irrigation.py           # Soil-water balance calculation
│   ├── sustainability.py       # Resource optimization scoring
│   └── weather.py              # Live Open-Meteo forecast rules & alerts
├── report/                     # Model evaluation reports and dataset audit documentation
├── notebooks/                  # Model training, EDA, and research notebooks
├── tests/                      # Automated test suite and frontend verification scripts
├── docs/                       # Technical specs, roadmaps, and archived logs
│   ├── CV_ENHANCEMENTS.md      # Computer Vision advancement roadmap
│   ├── DEPLOYMENT.md           # Production deployment guide
│   └── MODULE_REFERENCE.md     # In-depth module technical reference
├── run.py                      # Flask development server entrypoint
├── config.py                   # Application configuration
├── requirements.txt            # Python dependencies
└── package.json                # Frontend asset build configuration
```

---

## 8. Testing & Verification

Run the verification suites from the project root:

```powershell
# Run frontend route & template verification
python tests/test_frontend.py

# Run all Python tests (including pytest-style workflow and metric tests)
python -m pytest -q tests
npm run test:frontend
```

---

## 9. Research Notebooks & Technical Reports Reference

A structured overview of all research notebooks, evaluation scripts, and engineering reports available across the repository.

### Plant Pathology Research & Training Notebooks (`notebooks/plant_pathology/`)

- **[`01_train_resnet18.ipynb`](./notebooks/plant_pathology/01_train_resnet18.ipynb)**: ResNet-18 baseline model training pipeline on the 38-class dataset. Establishes baseline accuracy (99.43%) with lightweight computational footprint for edge deployment.
- **[`02_train_resnet50.ipynb`](./notebooks/plant_pathology/02_train_resnet50.ipynb)**: Deeper ResNet-50 architecture exploration achieving 99.67% validation accuracy with detailed cross-entropy loss tracking and learning rate scheduling.
- **[`03_train_convnext_tiny.ipynb`](./notebooks/plant_pathology/03_train_convnext_tiny.ipynb)**: Champion **ConvNeXt-Tiny (384px)** training pipeline. Includes advanced data augmentations, cosine annealing learning rate schedules, and achieving 99.85% top-1 accuracy (0.9969 Macro-F1).
- **[`sys_gpu_check.ipynb`](./notebooks/plant_pathology/sys_gpu_check.ipynb)**: Hardware diagnostics and CUDA acceleration verification notebook for training and inference environments.

### Advisory Engines & Simulation Notebooks (`notebooks/advisory_models/`)

- **[`01_crop_recommendation.ipynb`](./notebooks/advisory_models/01_crop_recommendation.ipynb)**: Multi-feature exploratory data analysis, feature importance extraction, and multi-class classification model training for soil nutrient matching.
- **[`02_irrigation_training.ipynb`](./notebooks/advisory_models/02_irrigation_training.ipynb)**: Soil moisture dynamics modeling, evapotranspiration calculation formulas, and water requirement estimation algorithms.
- **[`03_irrigation_simulation.ipynb`](./notebooks/advisory_models/03_irrigation_simulation.ipynb)**: Daily root-zone soil water balance simulation across distinct soil textures (Sandy, Loam, Clay) and crop growth stages.
- **[`04_weather_advisory.ipynb`](./notebooks/advisory_models/04_weather_advisory.ipynb)**: Weather risk rule validation, threshold tuning for frost/heat/storm alerts, and Open-Meteo API response schema testing.
- **[`05_sustainability_score.ipynb`](./notebooks/advisory_models/05_sustainability_score.ipynb)**: Resource consumption benchmarking formulas, efficiency index modeling (0–100 score), and penalty curves for excess nitrogen/water use.

### Evaluation & Benchmarking Tools (`notebooks/evaluation_benchmarks/`)

- **[`streamlit_console.py`](./notebooks/evaluation_benchmarks/streamlit_console.py)**: Interactive evaluation console for real-time model testing, top-5 probability inspection, and fallback mechanism verification.
- **[`benchmark_plantdoc.py`](./notebooks/evaluation_benchmarks/benchmark_plantdoc.py)**: Out-of-domain robustness benchmark evaluating trained classifiers against complex in-field imagery from the PlantDoc dataset.
- **[`benchmark_web_images.py`](./notebooks/evaluation_benchmarks/benchmark_web_images.py)**: Real-world image evaluation script testing resilience against background clutter, varied lighting, and diverse camera resolutions.
- **`model_summaries/` & `test_images/`**: Architectural layer summaries, FLOP calculations, and curated multi-class test image suites.

### Model Performance & Data Audit Reports (`report/`)

- **[`report/model_report.md`](./report/model_report.md)**: Comprehensive architectural benchmark comparing ConvNeXt-Tiny, ResNet-50, and ResNet-18 across accuracy, Macro-F1, loss curves, and latency metrics.
- **[`report/model_report_v3.md`](./report/model_report_v3.md)**: Dedicated evaluation report for the champion ConvNeXt-Tiny (384px) model (99.85% validation accuracy, 0.9969 Macro-F1).
- **[`report/model_report_v2.md`](./report/model_report_v2.md)**: Detailed training metrics, confusion matrix breakdown, and per-class precision/recall for ResNet-50 (v2).
- **[`report/model_report_v1.md`](./report/model_report_v1.md)**: Baseline training documentation and performance statistics for ResNet-18 (v1).
- **[`report/bonus_ab_data_audit.md`](./report/bonus_ab_data_audit.md)**: Agronomic dataset audit, feature correlation analysis, and data cleaning verification for advisory modules.
- **[`report/bonus_notebooks_guide.md`](./report/bonus_notebooks_guide.md)**: Technical guide covering advisory simulation pipelines and algorithmic logic.
- **[`report/irrigation_data_selection.md`](./report/irrigation_data_selection.md)**: Agronomic dataset selection rationale and manifest for root-zone soil water balance calculations.

### Technical Documentation & Engineering Reports (`docs/`)

- **[`docs/MODULE_REFERENCE.md`](./docs/MODULE_REFERENCE.md)**: Deep-dive architecture and technical specification for all 6 functional platform modules.
- **[`docs/CV_ENHANCEMENTS.md`](./docs/CV_ENHANCEMENTS.md)**: Implementation roadmap for Grad-CAM Explainable AI (XAI), Out-of-Distribution (OOD) leaf validation filters, and blur detection.
- **[`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md)**: Comprehensive production deployment guide covering Gunicorn, Nginx reverse proxying, Docker containerization, and systemd service management.
- **[`docs/SETUP_INSTRUCTIONS.md`](./docs/SETUP_INSTRUCTIONS.md)**: Step-by-step local workstation setup, GPU CUDA environment configuration, and dependency management.
- **[`docs/FRONTEND_README.md`](./docs/FRONTEND_README.md)**: Modernized UI design system, Tailwind CSS styling architecture, and reusable Jinja2 component guide.
- **[`docs/BUILD_README.md`](./docs/BUILD_README.md)**: Webpack 5 module bundler guide for compiling modular ES6 JavaScript pipelines.
- **[`docs/bonus_input_contract.md`](./docs/bonus_input_contract.md)**: API request/response JSON schema definitions for advisory engines.

---

## 10. License & Attribution

- **Core datasets:** PlantVillage and historical PlantDoc samples. Exact distributions, source versions, licenses and kickoff split correspondence need team confirmation.
- **Bonus datasets:** source identifiers, versions, hashes and reported licensing are in [data instructions](data/README.md), [bonus source manifest](report/bonus_modules_sources.json) and [irrigation manifest](report/irrigation_dataset_manifest.json).
- **Weather Provider:** Open-Meteo Forecast API; retain provider attribution and review applicable use conditions.
- **Originality and reuse:** [Team-review declaration draft](docs/ORIGINALITY.md). AI coding assistance was used; the reference inventory requires team completion before submission.
