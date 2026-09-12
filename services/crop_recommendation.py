"""Module A: dataset-scoped crop candidate ranking."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import math
from pathlib import Path
from typing import Any

from .contracts import failure, finite_number, response, validate_envelope


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "model" / "weights" / "crop_recommendation" / "crop_recommendation.joblib"
DATA_PATH = ROOT / "data" / "crop_recommendation" / "raw" / "Crop_recommendation.csv"
REPORT_PATH = ROOT / "outputs" / "metrics" / "crop_training_report.json"
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
PINNED_DATASET_ID = "atharvaingle/crop-recommendation-dataset"
PINNED_DATASET_VERSION = 1
PINNED_DATASET_SHA256 = "54a5a6e5408668e668667efc50de2fc867c1b875e0431b4f54dd331b0a109a4e"
PINNED_MODEL_SHA256 = "995b640801d9db912f752dfd859192d7591c2f6540c7a45c9a0794371435846d"
SOURCE_URL = "https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset"


@lru_cache(maxsize=1)
def _load_artifact() -> dict[str, Any]:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model artifact is missing: {MODEL_PATH}")
    if _artifact_hash() != PINNED_MODEL_SHA256:
        raise ValueError("Crop model checksum does not match the evaluated artifact.")
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError("Install the application requirements to load the crop model.") from exc
    artifact = joblib.load(MODEL_PATH)
    required = {"pipeline", "features", "classes", "training_ranges", "dataset_sha256", "source"}
    if not isinstance(artifact, dict) or not required.issubset(artifact):
        raise ValueError("Crop model artifact has an unexpected format.")
    if artifact["features"] != FEATURES:
        raise ValueError("Crop model feature order does not match the application contract.")
    if artifact["dataset_sha256"] != PINNED_DATASET_SHA256:
        raise ValueError("Crop model was not trained from the pinned dataset bytes.")
    # Parallel workers can fail in restricted deployment sandboxes. Inference is
    # deterministic and small, so one worker is the safer serving configuration.
    if hasattr(artifact["pipeline"], "set_params"):
        available = artifact["pipeline"].get_params(deep=True)
        if "n_jobs" in available:
            artifact["pipeline"].set_params(n_jobs=1)
    return artifact


@lru_cache(maxsize=1)
def _artifact_hash() -> str:
    digest = hashlib.sha256()
    with MODEL_PATH.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_source_row(row_id: Any, values: dict[str, float]) -> bool:
    if row_id is None:
        return False
    if isinstance(row_id, bool) or not isinstance(row_id, int) or row_id < 0:
        raise ValueError("inputs.row_id: must be a non-negative integer")
    if not DATA_PATH.is_file():
        raise FileNotFoundError("Pinned crop source data are required to verify inputs.row_id.")
    digest = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
    if digest != PINNED_DATASET_SHA256:
        raise ValueError("Local crop source data do not match the pinned checksum.")
    import pandas as pd

    source = pd.read_csv(DATA_PATH)
    if row_id >= len(source):
        raise ValueError("inputs.row_id: outside the pinned source dataset")
    row = source.iloc[row_id]
    mismatches = [
        name for name in FEATURES
        if not math.isclose(values[name], float(row[name]), rel_tol=1e-9, abs_tol=1e-9)
    ]
    if mismatches:
        raise ValueError(f"inputs.features: values do not match pinned row {row_id}: {', '.join(mismatches)}")
    return True


def recommend_crops(payload):
    errors = validate_envelope(payload, "A")
    if errors:
        return failure(payload, "A", "INVALID_INPUT", "; ".join(errors))

    inputs = payload["inputs"]
    if inputs.get("mode") != "source_dataset_classifier":
        return failure(
            payload,
            "A",
            "UNSUPPORTED_CONTEXT",
            "Only the pinned source-dataset classifier is currently supported.",
            field="inputs.mode",
            limitations=["The current model is not independently validated for farm suitability."],
        )
    if inputs.get("dataset_id") != PINNED_DATASET_ID or inputs.get("dataset_version") != PINNED_DATASET_VERSION:
        return failure(payload, "A", "INVALID_INPUT", "Dataset identity does not match the trained artifact.", field="inputs.dataset_id")
    if inputs.get("dataset_sha256") != PINNED_DATASET_SHA256:
        return failure(payload, "A", "INVALID_INPUT", "Dataset checksum does not match the trained artifact.", field="inputs.dataset_sha256")
    if payload.get("purpose") not in {"dataset_benchmark", "simulation"}:
        return failure(
            payload,
            "A",
            "UNSUPPORTED_CONTEXT",
            "The source dataset does not establish field suitability; use dataset_benchmark or simulation.",
            field="purpose",
        )

    raw_features = inputs.get("features")
    if not isinstance(raw_features, dict):
        return failure(payload, "A", "NEEDS_DATA", "All seven model features are required.", missing_inputs=["inputs.features"])
    missing = [f"inputs.features.{name}" for name in FEATURES if raw_features.get(name) is None]
    if missing:
        return failure(payload, "A", "NEEDS_DATA", "All seven model features are required.", missing_inputs=missing)

    try:
        values = {name: finite_number(raw_features[name], f"inputs.features.{name}") for name in FEATURES}
    except (ValueError, TypeError) as exc:
        return failure(payload, "A", "INVALID_INPUT", str(exc))
    try:
        artifact = _load_artifact()
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        return failure(payload, "A", "DATA_UNAVAILABLE", str(exc))

    try:
        source_row_verified = _verify_source_row(inputs.get("row_id"), values)
    except FileNotFoundError as exc:
        return failure(payload, "A", "DATA_UNAVAILABLE", str(exc))
    except (ValueError, TypeError) as exc:
        return failure(payload, "A", "INVALID_INPUT", str(exc))

    outside = []
    for name, value in values.items():
        limits = artifact["training_ranges"][name]
        if value < float(limits["min"]) or value > float(limits["max"]):
            outside.append(name)
    if outside:
        return failure(
            payload,
            "A",
            "UNSUPPORTED_CONTEXT",
            "Inputs fall outside the model's observed training range.",
            field="inputs.features",
            missing_inputs=[f"inputs.features.{name}" for name in outside],
        )

    try:
        import numpy as np
        import pandas as pd

        frame = pd.DataFrame([values], columns=FEATURES)
        model = artifact["pipeline"]
        probabilities = model.predict_proba(frame)[0]
        order = np.argsort(-probabilities, kind="stable")[:3]
        candidates = [
            {"crop": str(model.classes_[index]), "model_score": round(float(probabilities[index]), 6)}
            for index in order
        ]
    except Exception as exc:  # A malformed or incompatible artifact is an availability failure.
        return failure(payload, "A", "DATA_UNAVAILABLE", f"Crop model inference failed: {exc}")

    return response(
        payload,
        "A",
        "EXPERIMENTAL",
        scope="source_dataset_crop_label_ranking",
        data_kind="dataset_benchmark",
        result={
            "candidates": candidates,
            "inputs": values,
            "model": "random_forest",
            "model_sha256": _artifact_hash(),
            "source_row_verified": source_row_verified,
            "reported_test_macro_f1": 0.9908691003415904,
            "score_meaning": "Relative model score, not calibrated probability of farm suitability.",
        },
        reasons=[{
            "code": "DATASET_SCOPED_RESULT",
            "message": "Candidates are ranked within the pinned source dataset's feature scales.",
        }],
        sources=[{
            "title": "Crop Recommendation Dataset, version 1",
            "url": SOURCE_URL,
            "sha256": PINNED_DATASET_SHA256,
        }],
        limitations=[
            "N/P/K physical units and rainfall aggregation period are unresolved.",
            "The random row holdout does not establish generalization to new farms or seasons.",
            "No yield, profitability, or independent agronomic suitability outcome is predicted.",
        ],
    )
