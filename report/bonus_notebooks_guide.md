# Bonus modules A-D: demo and notebook guide

Last documentation review: 2026-09-12. The [API guide](../docs/bonus_input_contract.md) is the reference for current serving behavior; notebook experiments are not a guarantee of field performance.

These notebooks were prepared for manual execution and have since been run by the user. Their reusable A-D logic is integrated into the Flask services. No notebook cells or training were run during the service integration or verification described here. Notebook dependencies are listed in `requirements-notebooks.txt`.

| Module | Notebook | Method | Inputs | Local outputs after running |
| --- | --- | --- | --- | --- |
| A | `09_crop_recommendation_training.ipynb` | Majority, logistic regression, Gaussian naive Bayes, random forest; validation selection and held-out test | Version-1 Kaggle crop dataset | Model, class mapping, source hash, split IDs, metrics, confusion matrix |
| B baseline | `07_irrigation_baseline.ipynb` | Rule-based simulation; no training | Assumed crop-stage, moisture, and weather inputs | Decision explanations, comparison chart, sanity checks |
| B ML experiment | `08_irrigation_model_training.ipynb` | Majority/moisture-split baselines, logistic regression, random forest | Pinned Mendeley moisture and valve series | Controller-behavior model, chronological evaluation, reports |
| C | `10_weather_advisory.ipynb` | Forecast client plus explicit rules; no training | Coordinates; Open-Meteo hourly forecast or explicit simulated demo | Source-stamped advisory JSON, hourly data, plot |
| D | `11_sustainability_scoring.ipynb` | Published formula and yield check; no training | Comparable whole-cycle baseline/current resource totals, area, yield, evidence notes | Component scores, scenario comparisons, formula report, sensitivity plot |

## Quick demo without running notebooks

1. From the repository root, install `requirements.txt` in the project environment and start `python run.py`.
2. Open `http://127.0.0.1:5000`. A's default values run the packaged model and return three crop labels marked `EXPERIMENTAL`; the dashboard does not require the raw source CSV.
3. B's default assumed inputs return `SIMULATED`, `IRRIGATE`, gross depth **42.5 mm**, and volume **425 m3** for one hectare. This is a calculation example, not a verified farm dose.
4. C can request live weather when the provider is reachable. For offline presentation, select its explicit simulated demo; live failures remain unavailable rather than silently becoming simulated forecasts.
5. D's default resource comparison returns `SIMULATED` and **57.75/100**. Explain the component differences and yield check, not measured savings caused by the app.

The [JSON examples](../docs/examples/bonus_contract_examples.json) include equivalent supported demonstrations and selected failure cases. A's exact-row example additionally requires the pinned local CSV; the separate A model-scale example does not. Default coordinates and thresholds are demonstration choices, not validated local crop advice.

## Model quality in plain language

- **A:** saved macro-F1 **0.990869** on a random holdout of its 2,200-row source dataset. This is strong source-label performance, but unresolved nutrient units/rainfall periods and no independent farm/season evaluation prevent farm-readiness claims.
- **B ML:** saved macro-F1 **0.601253** and positive recall **0.238095**; it detected 10 of 42 positive test windows. It learns one controller's behavior, not ideal watering. The application therefore uses a separate water-balance calculation instead of serving this model.
- **C and D:** no trained ML model is needed for the implemented rules/formula. Passing rule/formula checks does not demonstrate forecast accuracy or environmental impact.

Metrics are from user-run saved reports, not new training or a reproduced evaluation. Full evidence and limitations are in the [A/B audit](bonus_ab_data_audit.md).

## Crop dataset

[Atharva Ingle's dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) has 2,200 rows and 22 crop labels in the inspected version. The publisher lists Apache 2.0. The original CSV and archive are downloaded locally under `data/crop_recommendation/raw/`; Git ignores them. A fresh checkout can download version 1 through the notebook or manually. `bonus_modules_sources.json` pins the exact CSV hash.

The source is useful for a prototype but does not supply soil-lab unit conversions or a defined rainfall period. Avoid claiming field readiness or substituting next-day weather. Random holdout scores are within-source estimates; they do not validate new farms, climates, or crop seasons.

## Irrigation experiments versus the API

Notebook 07 demonstrates assumed rule-based scenarios. Notebook 08 uses [Mendeley version 3](https://data.mendeley.com/datasets/cjb4vy4mzj/3) for controller-behavior ML experiments; source-file instructions are in the [dataset selection](irrigation_data_selection.md) and [manifest](irrigation_dataset_manifest.json).

The Flask B endpoint accepts calibrated-VWC-shaped inputs and supplied soil/crop/weather parameters, then calculates depletion, action, depth, and volume. It checks numeric ranges, units, evidence kinds, and the presence of a calibration reference, but does not verify that reference or the age/depth applicability of readings. There is no pump control or API serving mode for the saved B classifier. Field use requires additional validation described in the API guide.

## Weather

[Open-Meteo](https://open-meteo.com/en/docs) supplies forecasts, with [terms](https://open-meteo.com/en/terms) governing access and attribution. The notebook requests explicit units, preserves acquisition and validity times, rejects stale/missing input, and uses a location-specific cache. It does not claim acquisition time is the model's forecast issue time.

Default coordinates represent Pune; edit them before running. Set `MODE = "demo"` for a deliberately simulated offline example. Thresholds are editable demonstration policy. Weather scenarios are not training data, and successful rule assertions do not demonstrate forecast accuracy. Hourly forecast intervals require alignment before irrigation integration.

## Sustainability formula

Normalize irrigation m³, electricity kWh, and nitrogen nutrient kg by cultivated area. For each component:

`r = (baseline_per_ha - current_per_ha) / baseline_per_ha`

`component = clip(50 + 50*r, 0, 100)`

`raw_score = 0.40*water_component + 0.30*electricity_component + 0.30*nitrogen_component`

50 means baseline parity. If current yield per hectare is below 95% of baseline, cap the score at 50. Missing evidence or non-positive resource baselines withhold scoring. The weights and yield cutoff are project assumptions. Area normalization does not remove soil, rainfall, season, and management confounding.

The [FAO productivity reference](https://www.fao.org/in-action/remote-sensing-for-water-productivity/wapor-data/) informs terminology only. The project score is not an FAO standard. Default records are simulated. No software-attributable water savings, carbon reductions, or comprehensive environmental certification are established.

## Current integration and next steps

Reusable logic is already connected through `services/` -> `app/routes/advisory.py` -> dashboard forms/results. The serving application does not execute notebooks or train models. A's evaluated model and compact evidence are packaged; raw datasets, the saved B model, and most generated outputs stay local and ignored.

Serving uses the pinned `requirements.txt`; manual notebook work uses `requirements-notebooks.txt`. Only the user runs notebook cells or training. Changing or retraining A's artifact also requires reviewing its checksum, source metadata, serving compatibility, and evaluation evidence rather than replacing the packaged binary silently.

Remaining work includes stricter schemas, evidence/reference verification, B reading-age/root-zone checks and forecast alignment, D completed-cycle/baseline verification, and independent field evaluation. Notebook 09 does not accept C's rainfall period automatically. D needs actual resource totals and a defensible baseline, not B's suggested volume. These gaps must remain visible in reports and demos.
