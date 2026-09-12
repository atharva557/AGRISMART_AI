# Datasets

Place local data here. Dataset contents are ignored by Git.

The brief specifies PlantVillage training/validation and an organizers' held-out field test. Follow the exact kickoff class list and split. Never use the held-out set for training or model tuning.

Record source URLs, licenses, split sizes, class mapping, and any additional public training data. Check extra data for evaluation overlap. Do not present local validation results as the official held-out score.

## Irrigation training files

Notebook 08 uses the original `D_moisture.txt` and `D_valve.txt` files from [Mendeley dataset cjb4vy4mzj, version 3](https://data.mendeley.com/datasets/cjb4vy4mzj/3), licensed CC BY 4.0. Put them in `data/irrigation/raw/`. They contain comma-separated data despite the `.txt` extension. File hashes and provenance are stored in `report/irrigation_dataset_manifest.json`.

The source downloads may require a browser. Do not rename unrelated data to these file names, regenerate the targets from moisture thresholds, or substitute a different version silently. Dataset files remain local and ignored by Git.

## Crop recommendation

Notebook 09 uses [Atharva Ingle's Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset), version 1, publisher-listed Apache 2.0. The inspected CSV has 2,200 rows and 22 labels. Store `Crop_recommendation.csv` in `data/crop_recommendation/raw/`; the original CSV and ZIP have been downloaded locally. The exact hash is in `report/bonus_modules_sources.json`. Fresh checkouts can use the notebook's versioned download or obtain it manually from Kaggle.

Do not infer kg/ha or ppm for source N/P/K, or a daily/seasonal period for rainfall; these are not established by the data card. All data files stay ignored.

## Weather and sustainability

Notebook 10 fetches [Open-Meteo forecasts](https://open-meteo.com/en/docs) when run in live mode and caches responses in `data/weather/cache/`. Keep attribution and acquisition times with exports. An explicit demo mode supplies simulated hourly examples without network access; live failures never silently become demo data.

Notebook 11 needs comparable farm resource records, not a public training dataset. Its default examples are visibly simulated. Measured runs require water applied in m³, electricity in kWh, nitrogen nutrient in kg N, cultivated area in ha, harvest in kg, dates, accounting scope, and baseline evidence. Do not commit private field records.
