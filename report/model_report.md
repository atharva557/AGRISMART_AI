# AgriSmart AI: submission model summary

Updated 15 September 2026. Historical numbers below are reported evidence, not new verification of the submitted checkpoint.

| Required field | Evidence / current status |
|---|---|
| Task | Crop-disease classification; 38 PlantVillage labels across 14 crops. Exact kickoff label compatibility is pending. |
| Data and split | Reported 54,305 PlantVillage images: 43,444 training and 10,861 validation. Validation was used for checkpoint selection; it is not an independent test. Exact kickoff split/source/license confirmation is pending. |
| Approach | ConvNeXt-Tiny at 384 px; reported AdamW lr 0.0001, weight decay 0.01, label smoothing 0.1 and cosine schedule. ResNet-18 fallback at 224 px. Current serving uses compressed FP16 weights loaded into the model parameter dtype, RGB conversion and EXIF orientation handling. |
| Lab validation | Historical ConvNeXt macro-F1 0.9969 and accuracy 99.85%, on 10,861 samples. Not reproduced for current compressed weights/preprocessing. |
| Field evidence | Historical PlantDoc sample: 11/34 correct (32.4%) top-1, 20/34 (58.8%) top-3. Small nonrepresentative sample; field macro-F1/per-class precision and recall are not supplied in that report. Not an official score. |
| Official test | Organizer-held-out macro-F1, confusion matrix and per-class precision/recall: pending organizer evaluation. |
| Baseline | Local ResNet-18 validation macro-F1 0.9912. Organizer baseline and scoring bands not supplied; no official comparison claimed. |
| Inference | `python -m model.predict --image PATH` prints one label. Python: `model.predict.predict(image_path) -> str`. Cached primary model; fallback version is visible in detailed/API output. |
| Limitations | Lab-to-field gap, uncalibrated scores, unresolved organizer class contract, no semantic unrelated-object detector. Photo heuristics need independent validation. The 75% threshold does not eliminate high-confidence mistakes. |

[Historical detailed per-class values and field comparison](historical_validation_report.md). Historical CV confusion matrices are stored in training notebook outputs; those cells were not re-executed. The [evaluation protocol](../docs/FIELD_EVALUATION.md) explains exporting a fresh numeric confusion matrix and per-class metrics from a user-run independent test.

Farmer-facing policy: very small or nearly featureless/dark/overexposed photos request a retake; possible blur is advisory. Low scores or a selected-crop mismatch withhold disease-specific guidance, including in the assistant. These serving behaviors do not change the mandatory classifier label output or establish improved field accuracy.
