# Notebook index and evidence status

These notebooks are historical, user-run experiment records. Saved outputs are available for review; they were inspected statically on 15 September 2026 without executing cells or retraining models.

## Core plant-pathology experiments

- [`plant_pathology/01_train_resnet18.ipynb`](plant_pathology/01_train_resnet18.ipynb): ResNet-18 baseline; saved best validation macro-F1 0.9912.
- [`plant_pathology/02_train_resnet50.ipynb`](plant_pathology/02_train_resnet50.ipynb): ResNet-50 iteration; saved best validation macro-F1 0.9946.
- [`plant_pathology/03_train_convnext_tiny.ipynb`](plant_pathology/03_train_convnext_tiny.ipynb): ConvNeXt-Tiny iteration; saved best validation macro-F1 0.9969.
- [`plant_pathology/sys_gpu_check.ipynb`](plant_pathology/sys_gpu_check.ipynb): optional environment check.

The vision notebooks select checkpoints and report final metrics on the same validation directory. They do not include an independent test split, dataset checksum, split manifest, or fixed random seed. Set `PLANTVILLAGE_DIR` to a folder containing `train/` and `val/` before a user-run retraining session. Treat the saved results as historical validation evidence. Use [`../model/evaluate.py`](../model/evaluate.py) and [`../docs/FIELD_EVALUATION.md`](../docs/FIELD_EVALUATION.md) for a new independent, manifest-backed evaluation.

## Advisory experiments

- [`advisory_models/01_crop_recommendation.ipynb`](advisory_models/01_crop_recommendation.ipynb): crop recommendation with a held-out test and saved source/split evidence.
- [`advisory_models/02_irrigation_training.ipynb`](advisory_models/02_irrigation_training.ipynb): chronological controller-behavior experiment.
- [`advisory_models/03_irrigation_simulation.ipynb`](advisory_models/03_irrigation_simulation.ipynb): water-balance simulation.
- [`advisory_models/04_weather_advisory.ipynb`](advisory_models/04_weather_advisory.ipynb): forecast client and explicit advisory rules.
- [`advisory_models/05_sustainability_score.ipynb`](advisory_models/05_sustainability_score.ipynb): project formula and sensitivity examples.

The advisory notebooks have saved outputs and no saved exception outputs. Modules C and D are rules/formulas rather than trained ML. Their default records are demonstrations and do not establish farm impact.

## Historical benchmark utilities

`evaluation_benchmarks/benchmark_plantdoc.py` produced the saved 34-image PlantDoc comparison. Its historical sampling could include files from PlantDoc's train directory when the test directory did not reach the target, so the result is a small convenience-sample stress test rather than a clean held-out benchmark. `benchmark_web_images.py` samples the PlantVillage GitHub repository and is therefore a source-domain smoke test despite its filename. Both scripts retain historical context; use the manifest-based evaluator for new reported results.
