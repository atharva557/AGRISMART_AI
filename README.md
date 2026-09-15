# AgriSmart AI

AI-powered crop disease detection and evidence-aware precision agriculture advisory.

AgriSmart AI combines a packaged computer-vision classifier with crop recommendation, irrigation, weather, sustainability, and multilingual farmer-assistance modules. The application is designed as a working hackathon prototype: model outputs are shown with confidence and limitations, simulated values remain visibly labelled, and uncertain diagnoses withhold disease-specific guidance.

## Submission status

| Item | Status |
| --- | --- |
| Core disease classifier and Python `predict(image_path) -> class_label` interface | Implemented |
| Web upload and farmer-facing diagnosis workflow | Implemented |
| Packaged model weights | Included |
| Bonus A: crop recommendation | Implemented as an experimental dataset-scoped classifier |
| Bonus B: smart irrigation | Implemented as an evidence-aware soil-water-balance calculation |
| Bonus C: weather intelligence | Implemented with Open-Meteo and an explicitly simulated offline mode |
| Bonus D: sustainability score | Implemented as a transparent resource-comparison formula |
| Bonus E: multilingual farmer assistant | Implemented with Gemini integration and an offline grounded fallback |
| Bonus F: IoT integration | Not claimed |
| Bonus G: autonomous agent | Not claimed |
| Organizer-held-out field score | Pending organizer evaluation |
| Demo video | Pending team upload |
| Deployed application | Run locally; public deployment not supplied |

## Quick start

### Requirements

- Python 3.11 or newer
- Node.js 16 or newer
- At least 1.5 GB free space for Python packages and model loading

### Install and run

```powershell
git clone https://github.com/atharva557/AGRISMART_AI.git
cd AGRISMART_AI

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

npm ci
npm run build:all

python run.py
```

Open `http://127.0.0.1:5000`.

The Gemini key is optional. Copy `.env.example` to `.env` and set `GEMINI_API_KEY` only when live generation is required. Without a key, the assistant uses its deterministic grounded fallback.

## Required prediction interface

Default CLI output is exactly one class label:

```powershell
python -m model.predict --image "C:\path\to\leaf.jpg"
```

Detailed diagnostics are optional:

```powershell
python -m model.predict --image "C:\path\to\leaf.jpg" --details
```

Python interface:

```python
from model.predict import predict

label = predict("path/to/leaf.jpg")
```

Check the packaged checkpoint and local label order:

```powershell
python -m model.submission_check
python -m model.submission_check --labels "C:\path\to\organizer_classes.json"
```

The current model contains 38 PlantVillage labels. Exact compatibility with the organizer's final shared class list must be checked with the second command. Labels must not be renamed or silently removed to hide incompatibility.

## Architecture

```text
Browser
  -> Flask routes and JSON validation
      -> Crop disease classifier (ConvNeXt-Tiny; ResNet-18 fallback)
      -> Crop recommendation model
      -> Soil-water-balance irrigation service
      -> Open-Meteo weather rules
      -> Sustainability formula
      -> Grounded multilingual farmer assistant
```

### Core image workflow

1. Validate file type, content, dimensions, pixel count, and basic image quality.
2. Apply EXIF orientation, RGB conversion, resize, tensor conversion, and ImageNet normalization.
3. Load and cache the packaged model.
4. Produce the exact raw class label, model score, top candidates, and model version.
5. Withhold disease-specific guidance when the score is below 0.75 or the selected crop conflicts with the prediction.

The 0.75 value is an uncalibrated model-score threshold, not a guarantee of correctness. The photo-quality checks are heuristics and are not a semantic non-plant detector.

## Complete reported metrics

All numbers below are preserved from saved user-run experiment outputs. Historical validation metrics are not organizer-held-out results and have not been independently reproduced for the current compressed FP16 checkpoints.

### Core crop-disease model comparison

PlantVillage color dataset used by the saved notebooks:

- Reported total: 54,305 images
- Training directory: 43,444 images (80.0%)
- Validation directory: 10,861 images (20.0%)
- Classes: 38 plant-pathology labels across 14 crops
- The validation directory was used for model selection and final reporting; it is not an independent test set.
- The saved core notebooks do not establish a dataset checksum, split manifest, or fixed random seed.

| Model | Input | Macro-F1 | Accuracy | Average saved GPU latency |
| --- | ---: | ---: | ---: | ---: |
| ResNet-18 (v1 baseline) | 224 x 224 | 0.9912 | 99.43% | 7.6 ms |
| ResNet-50 (v2) | 224 x 224 | 0.9946 | 99.67% | 5.4 ms |
| ConvNeXt-Tiny (v3 selected) | 384 x 384 | 0.9969 | 99.85% (10,845 / 10,861) | 24.51 ms |

Selected v3 aggregate validation metrics:

| Metric | Value |
| --- | ---: |
| Macro precision | 0.9970 |
| Macro recall | 0.9968 |
| Macro-F1 | 0.9969 |
| Weighted F1 | 0.9985 |
| Accuracy | 0.9985 |
| Classes with F1 above 0.9900 | 33 / 38 |
| Lowest class F1 | 0.9608 |

#### ConvNeXt-Tiny per-class validation metrics

| Class | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Apple___Apple_scab | 1.0000 | 1.0000 | 1.0000 | 126 |
| Apple___Black_rot | 1.0000 | 1.0000 | 1.0000 | 125 |
| Apple___Cedar_apple_rust | 1.0000 | 1.0000 | 1.0000 | 55 |
| Apple___healthy | 1.0000 | 0.9939 | 0.9970 | 329 |
| Blueberry___healthy | 0.9934 | 1.0000 | 0.9967 | 300 |
| Cherry_(including_sour)___Powdery_mildew | 1.0000 | 1.0000 | 1.0000 | 210 |
| Cherry_(including_sour)___healthy | 1.0000 | 0.9941 | 0.9971 | 170 |
| Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot | 0.9703 | 0.9515 | 0.9608 | 103 |
| Corn_(maize)___Common_rust_ | 1.0000 | 0.9958 | 0.9979 | 239 |
| Corn_(maize)___Northern_Leaf_Blight | 0.9700 | 0.9848 | 0.9773 | 197 |
| Corn_(maize)___healthy | 1.0000 | 1.0000 | 1.0000 | 233 |
| Grape___Black_rot | 1.0000 | 1.0000 | 1.0000 | 236 |
| Grape___Esca_(Black_Measles) | 1.0000 | 1.0000 | 1.0000 | 276 |
| Grape___Leaf_blight_(Isariopsis_Leaf_Spot) | 1.0000 | 1.0000 | 1.0000 | 215 |
| Grape___healthy | 1.0000 | 1.0000 | 1.0000 | 84 |
| Orange___Haunglongbing_(Citrus_greening) | 1.0000 | 1.0000 | 1.0000 | 1,102 |
| Peach___Bacterial_spot | 1.0000 | 1.0000 | 1.0000 | 459 |
| Peach___healthy | 1.0000 | 1.0000 | 1.0000 | 72 |
| Pepper,_bell___Bacterial_spot | 1.0000 | 1.0000 | 1.0000 | 200 |
| Pepper,_bell___healthy | 1.0000 | 1.0000 | 1.0000 | 295 |
| Potato___Early_blight | 1.0000 | 1.0000 | 1.0000 | 200 |
| Potato___Late_blight | 0.9950 | 0.9950 | 0.9950 | 200 |
| Potato___healthy | 0.9677 | 0.9677 | 0.9677 | 31 |
| Raspberry___healthy | 1.0000 | 1.0000 | 1.0000 | 74 |
| Soybean___healthy | 1.0000 | 0.9990 | 0.9995 | 1,018 |
| Squash___Powdery_mildew | 1.0000 | 1.0000 | 1.0000 | 367 |
| Strawberry___Leaf_scorch | 1.0000 | 1.0000 | 1.0000 | 222 |
| Strawberry___healthy | 1.0000 | 1.0000 | 1.0000 | 92 |
| Tomato___Bacterial_spot | 1.0000 | 1.0000 | 1.0000 | 425 |
| Tomato___Early_blight | 0.9950 | 1.0000 | 0.9975 | 200 |
| Tomato___Late_blight | 0.9948 | 0.9974 | 0.9961 | 382 |
| Tomato___Leaf_Mold | 1.0000 | 1.0000 | 1.0000 | 191 |
| Tomato___Septoria_leaf_spot | 1.0000 | 1.0000 | 1.0000 | 354 |
| Tomato___Spider_mites Two-spotted_spider_mite | 1.0000 | 1.0000 | 1.0000 | 335 |
| Tomato___Target_Spot | 1.0000 | 1.0000 | 1.0000 | 281 |
| Tomato___Tomato_Yellow_Leaf_Curl_Virus | 1.0000 | 1.0000 | 1.0000 | 1,071 |
| Tomato___Tomato_mosaic_virus | 1.0000 | 1.0000 | 1.0000 | 74 |
| Tomato___healthy | 1.0000 | 1.0000 | 1.0000 | 318 |

The saved notebook computes a validation confusion matrix but does not export a numeric matrix artifact. The organizer-held-out macro-F1, confusion matrix, and per-class precision/recall remain pending organizer evaluation.

### Historical field stress test

The saved PlantDoc-style convenience sample contains 34 images. The historical sampler could draw from PlantDoc train and test directories, so these numbers are diagnostic evidence only and are not an official held-out benchmark.

| Model | Top-1 accuracy | Top-3 accuracy | Mean softmax score | Below 0.75 threshold |
| --- | ---: | ---: | ---: | ---: |
| ResNet-18 | 14.7% | 47.1% | 64.5% | 58.8% |
| ResNet-50 | 23.5% | 44.1% | 66.6% | 50.0% |
| ConvNeXt-Tiny | 32.4% (11 / 34) | 58.8% (20 / 34) | 65.0% | 44.1% |

This result demonstrates a substantial lab-to-field domain gap. Confidence gating withholds some low-score outputs but does not prevent incorrect high-score predictions.

### Bonus A: crop recommendation model

Source dataset: Atharva Ingle Crop Recommendation Dataset version 1, publisher-listed Apache 2.0, 2,200 rows, 22 balanced labels. Split: 1,320 training, 440 validation, and 440 test rows using seed 42.

Validation model comparison:

| Model | Macro-F1 | Accuracy | Top-3 accuracy |
| --- | ---: | ---: | ---: |
| Random forest | 0.995452 | 0.995455 | 1.000000 |
| Gaussian naive Bayes | 0.995443 | 0.995455 | 1.000000 |
| Logistic regression | 0.972596 | 0.972727 | 1.000000 |
| Majority baseline | 0.003953 | 0.045455 | 0.136364 |

Selected random-forest test metrics:

| Metric | Value |
| --- | ---: |
| Macro-F1 | 0.990869 |
| Accuracy | 0.990909 |
| Top-3 accuracy | 1.000000 |

Per-class test metrics:

| Crop | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| apple | 1.0000 | 1.0000 | 1.0000 | 20 |
| banana | 1.0000 | 1.0000 | 1.0000 | 20 |
| blackgram | 1.0000 | 1.0000 | 1.0000 | 20 |
| chickpea | 1.0000 | 1.0000 | 1.0000 | 20 |
| coconut | 1.0000 | 1.0000 | 1.0000 | 20 |
| coffee | 1.0000 | 1.0000 | 1.0000 | 20 |
| cotton | 1.0000 | 1.0000 | 1.0000 | 20 |
| grapes | 1.0000 | 1.0000 | 1.0000 | 20 |
| jute | 0.8696 | 1.0000 | 0.9302 | 20 |
| kidneybeans | 1.0000 | 1.0000 | 1.0000 | 20 |
| lentil | 1.0000 | 0.9500 | 0.9744 | 20 |
| maize | 1.0000 | 1.0000 | 1.0000 | 20 |
| mango | 1.0000 | 1.0000 | 1.0000 | 20 |
| mothbeans | 0.9524 | 1.0000 | 0.9756 | 20 |
| mungbean | 1.0000 | 1.0000 | 1.0000 | 20 |
| muskmelon | 1.0000 | 1.0000 | 1.0000 | 20 |
| orange | 1.0000 | 1.0000 | 1.0000 | 20 |
| papaya | 1.0000 | 1.0000 | 1.0000 | 20 |
| pigeonpeas | 1.0000 | 1.0000 | 1.0000 | 20 |
| pomegranate | 1.0000 | 1.0000 | 1.0000 | 20 |
| rice | 1.0000 | 0.8500 | 0.9189 | 20 |
| watermelon | 1.0000 | 1.0000 | 1.0000 | 20 |

Limitations: the source has unresolved N/P/K units and rainfall aggregation period, contains augmented data, and has no independent farm/season evaluation. Scores rank source-dataset labels; they are not calibrated probabilities of field suitability.

### Bonus B: irrigation controller experiment

The saved experiment uses the Mendeley Smart Irrigation Control System dataset version 3 from a strawberry field in Paraguay. It predicts the recorded controller's valve opening within the next hour; it does not learn an agronomically optimal irrigation dose. The serving application therefore uses a transparent soil-water-balance calculation instead of this classifier.

| Metric | Value |
| --- | ---: |
| Training rows | 2,408 |
| Validation rows | 435 |
| Test rows | 577 |
| Selected model | Random forest |
| Decision threshold | 0.85 |
| Test macro-F1 | 0.601253 |
| Test accuracy | 0.899480 |
| Positive precision | 0.277778 |
| Positive recall | 0.238095 |
| Positive F1 | 0.256410 |
| Average precision | 0.363945 |

Saved test confusion matrix:

| Actual / predicted | Closed | Opens |
| --- | ---: | ---: |
| Closed | 509 | 26 |
| Opens | 32 | 10 |

Only 10 of 42 positive test windows were detected. Windows are correlated and do not represent independent irrigation events.

### Bonus C: weather intelligence

This module is rule-based and has no trained-model accuracy metric. It checks complete Open-Meteo forecast windows for cold, heat, rain, wind, humidity, and reference evapotranspiration conditions. Live failures are reported as unavailable and are never silently replaced with simulated data.

### Bonus D: sustainability score

This module uses a reproducible project-defined formula rather than a trained model:

```text
resource_component = clip(50 + 50 * ((baseline_per_ha - current_per_ha) / baseline_per_ha), 0, 100)

raw_score =
    0.40 * water_component
  + 0.30 * electricity_component
  + 0.30 * nitrogen_component
```

If current yield per hectare is below 95% of baseline, the final score is capped at 50. The saved default simulated comparison scores 57.75 / 100. This is an indicative comparison, not an environmental certification or proof of software-caused savings.

### Bonus E: farmer assistant

No model-quality benchmark is claimed for generated text. Gemini calls and regional-language translation are optional; offline tests mock provider behavior. The deterministic fallback is grounded in the supplied scan/advisory context and refuses unsupported questions.

Supported interface languages include English, Hindi, Marathi, Gujarati, Telugu, Tamil, Kannada, Bengali, and Punjabi. Live translation quality must be checked before demonstration.

## Data sources and licences

| Component | Source | Licence / status |
| --- | --- | --- |
| Core training/validation | PlantVillage color images | Exact downloaded distribution, licence, and kickoff correspondence require team confirmation |
| Historical field sample | PlantDoc | Historical diagnostic sample; exact sample manifest was not preserved |
| Crop recommendation | [Atharva Ingle Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset), version 1 | Publisher-listed Apache 2.0 |
| Irrigation experiment | [Mendeley Smart Irrigation Control System Data](https://data.mendeley.com/datasets/cjb4vy4mzj/3), version 3, DOI 10.17632/cjb4vy4mzj.3 | CC BY 4.0 |
| Weather | [Open-Meteo](https://open-meteo.com/en/docs) | Provider terms apply; source and timestamps are returned |
| Sustainability terminology | [FAO WaPOR](https://www.fao.org/in-action/remote-sensing-for-water-productivity/wapor-data/) | Concept reference only; the score is project-defined |
| CV backbones | PyTorch/Torchvision ResNet-18/50 and timm ConvNeXt-Tiny | Pretrained/open-source components; upstream licences apply |
| Generative assistant | Google GenAI SDK and Gemini API | Provider terms apply |

Dataset contents remain outside Git where licensing, privacy, or size requires it. Source hashes and saved experiment metadata are retained in the repository's machine-readable report JSON and output files.

## Web routes and APIs

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/` | Home |
| GET | `/disease` | Disease upload workflow |
| GET | `/advisory` | Advisory modules A-E |
| GET | `/about` | Project overview |
| GET | `/api/health` | Check service and model-file presence |
| POST | `/api/disease/predict` | Classify an uploaded image |
| POST | `/api/crops/recommend` | Rank experimental crop candidates |
| POST | `/api/irrigation/advise` | Calculate irrigation advice |
| POST | `/api/weather/advise` | Evaluate live or simulated weather |
| POST | `/api/sustainability/score` | Compare whole-cycle resources |
| POST | `/api/assistant/chat` | Grounded conversational assistance |

## Verification

```powershell
python -m pytest -q tests
npm run test:frontend
python -m compileall -q app model services tests
```

The test suite covers routes and assets, upload validation and cleanup, model-cache behavior, saved-model inference, evaluation contracts, advisory contracts, assistant grounding, regional-language fallbacks, and frontend context preservation. Mocked provider tests do not prove live weather, Gemini, or translation availability.

## Repository structure

```text
app/            Flask routes, templates, and web assets
model/          inference, evaluation, labels, and packaged checkpoints
services/       advisory and assistant business logic
notebooks/      historical user-run training and research records
outputs/        saved metrics and figures
report/         required concise report and machine-readable evidence
tests/          Python, frontend, and contract fixtures
data/           local dataset instructions; dataset contents are ignored
```

## Known limitations

- Official organizer-held-out metrics and baseline comparison are not yet available.
- The 38-class model may not match the organizer's final class contract.
- Very high laboratory validation performance does not transfer reliably to field photographs.
- The confidence threshold is uncalibrated.
- No semantic unrelated-object or unsupported-crop detector is implemented.
- Disease reference guidance requires local agronomic review.
- Crop recommendation lacks independently validated physical input semantics and farm outcomes.
- Irrigation results depend on locally calibrated measurements and parameters.
- Weather alerts use project-defined thresholds.
- Sustainability examples do not establish causal savings or carbon impact.
- No IoT actuation or autonomous agent is claimed.

## Originality and reuse declaration

This repository contains team-authored integration, application, validation, documentation, and experiment work developed for the hackathon. It uses open-source libraries, pretrained model architectures, public datasets, and external APIs identified above. AI coding assistance was used for implementation, documentation, and verification. The team does not claim ownership of third-party libraries, pretrained architectures, datasets, or provider services.

Any directly copied or adapted third-party notebook/code not already disclosed above must be added by the team before submission. Commit timestamps document repository activity but are not, by themselves, proof of authorship.

## Model report

The required concise report is available at [report/model_report.md](report/model_report.md). The complete reported metric tables are maintained in this README so judges can evaluate the repository from a single entry point.
