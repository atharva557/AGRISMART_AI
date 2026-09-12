# Bonus modules A, C, and D

These notebooks were prepared for manual execution and have since been run by the user. Their reusable A-D logic is integrated into the Flask services. No notebook cells or training were run during the service integration or verification described here. Notebook dependencies are listed in `requirements-notebooks.txt`.

| Module | Notebook | Method | Inputs | Local outputs after running |
| --- | --- | --- | --- | --- |
| A | `09_crop_recommendation_training.ipynb` | Majority, logistic regression, Gaussian naive Bayes, random forest; validation selection and held-out test | Version-1 Kaggle crop dataset | Model, class mapping, source hash, split IDs, metrics, confusion matrix |
| C | `10_weather_advisory.ipynb` | Forecast client plus explicit rules; no training | Coordinates; Open-Meteo hourly forecast or explicit simulated demo | Source-stamped advisory JSON, hourly data, plot |
| D | `11_sustainability_scoring.ipynb` | Published formula and yield check; no training | Comparable whole-cycle baseline/current resource totals, area, yield, evidence notes | Component scores, scenario comparisons, formula report, sensitivity plot |

## Crop dataset

[Atharva Ingle's dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) has 2,200 rows and 22 crop labels in the inspected version. The publisher lists Apache 2.0. The original CSV and archive are downloaded locally under `data/crop_recommendation/raw/`; Git ignores them. A fresh checkout can download version 1 through the notebook or manually. `bonus_modules_sources.json` pins the exact CSV hash.

The source is useful for a prototype but does not supply soil-lab unit conversions or a defined rainfall period. Avoid claiming field readiness or substituting next-day weather. Random holdout scores are within-source estimates; they do not validate new farms, climates, or crop seasons.

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

## Team integration

Review user-run results before moving functions into their corresponding `services/` files. Preserve units, missing-input handling, timestamps, source attribution, and formula/model versions. Notebook 09 does not accept notebook 10's rainfall period automatically. Notebook 11 needs observed resource totals and a defensible baseline, not irrigation predictions or suggested volumes.
