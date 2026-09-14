# Independent field evaluation

The purpose is to measure generalization and error handling without treating validation scores as an official test result. `model.evaluate` runs only saved-weight inference; notebooks and training remain user-run.

## Dataset contract

1. Obtain the exact kickoff class list, split and organizer baseline. Keep them verbatim. Run `python -m model.submission_check --labels PATH`. A mismatch is unresolved work, not permission to change disease names.
2. Prepare a separate permitted development set of field images with reviewed ground truth. Record source/version/license, acquisition conditions, class counts and exclusions beside the manifest.
3. Check overlap and near-duplicates against training and validation data. The command checks only repeated paths and identical image bytes within the evaluation manifest.
4. If choosing augmentation, cropping or thresholds using development results, reserve a separate final local test set. Never tune on the organizer-held-out set.

Manifest example (format only; images and labels must be supplied and verified):

```csv
image,label
images/leaf-001.jpg,Tomato___Early_blight
images/leaf-002.jpg,Apple___Apple_scab
```

Paths are relative to the manifest. The supplied JSON label list must match the saved checkpoint label set. Include independent coverage of every declared class; missing classes are listed and receive zero F1 in the declared-class macro average.

## User-run measurement

```powershell
python -m model.evaluate --manifest data/field_eval/manifest.csv --labels model/classes.json --dataset-name "Independent field development set" --output outputs/field_eval/run-01
```

Outputs: `metrics.json`, `predictions.csv`, `confusion_matrix.csv`. They record all-image macro-F1/accuracy, per-class precision/recall, every prediction, the actual loaded model version and image/checkpoint/manifest/label hashes. The command rejects unsupported labels, missing or unreadable files, duplicates and existing output directories. It never silently skips failures. Hashes identify bytes, not authenticity. Reports always label themselves as local user-run results.

Uncertainty metrics use the existing 0.75 confidence threshold: accepted count, coverage, incorrect accepted predictions and accuracy among accepted predictions. Null accepted accuracy means none accepted, not perfect safety. This section excludes web photo-quality and selected-crop checks; do not present it as full-workflow evaluation.

## Full farmer-flow validation

Prepare a reviewed set of clear leaves, genuinely blurred/dark/overexposed photos, multiple-leaf scenes, unrelated objects and unsupported crops. Record expected user actions and actual outputs. Measure false rejection of usable images, missed unusable photos, errors among accepted scans and retake frequency.

Current photo rules: minimum side 192 px; >98% grayscale pixels below 20 or above 245; grayscale standard deviation below 1; advisory blur warning for Laplacian variance below 20 after resizing to at most 512 px. These are project heuristics, not calibrated results. Textured unrelated objects can pass.

## Experiments for the team

Compare the existing model with one change at a time: reviewed leaf localization, field-like augmentation or permitted public field training images. Keep preprocessing, splits and versions explicit; retain changes only when independent results support them. No new training or field-performance experiment was executed for the workflow improvements.
