"""User-run manifest evaluation of saved weights. Never trains or imports notebooks."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

from model.submission_check import read_labels


def summarize(rows, labels, threshold=0.75):
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
    if not rows:
        raise ValueError("At least one prediction is required.")
    for row in rows:
        if row["label"] not in labels or row["predicted_label"] not in labels:
            raise ValueError("Every true and predicted label must appear in the evaluation label list; labels are never silently dropped.")
        confidence = row["confidence"]
        if isinstance(confidence, bool) or not isinstance(confidence, (float, int)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError("Confidence must be a finite number between zero and one.")
    truth = [row["label"] for row in rows]
    predicted = [row["predicted_label"] for row in rows]
    accepted = [row for row in rows if row["confidence"] >= threshold]
    wrong = sum(row["label"] != row["predicted_label"] for row in accepted)
    return {
        "sample_count": len(rows), "label_order": labels,
        "accuracy": accuracy_score(truth, predicted),
        "macro_f1": f1_score(truth, predicted, labels=labels, average="macro", zero_division=0),
        "confusion_matrix": confusion_matrix(truth, predicted, labels=labels).tolist(),
        "per_class": classification_report(truth, predicted, labels=labels, output_dict=True, zero_division=0),
        "classes_without_test_samples": [label for label in labels if label not in truth],
        "uncertainty": {"threshold": threshold, "accepted_count": len(accepted),
                        "coverage": len(accepted) / len(rows), "incorrect_accepted": wrong,
                        "accuracy_among_accepted": (len(accepted) - wrong) / len(accepted) if accepted else None,
                        "scope": "Confidence threshold only; excludes web photo triage and selected-crop checks."},
    }


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_manifest(path, labels):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"image", "label"}.issubset(reader.fieldnames or []):
            raise ValueError("Manifest must contain image,label columns.")
        rows = list(reader)
    if not rows:
        raise ValueError("Manifest is empty.")
    seen_paths, seen_hashes = set(), set()
    for row in rows:
        image = (path.parent / row["image"]).resolve()
        if row["label"] not in labels:
            raise ValueError(f"Unsupported ground-truth label: {row['label']}")
        if not image.is_file():
            raise ValueError(f"Image not found: {image}")
        image_hash = sha256(image)
        if image in seen_paths or image_hash in seen_hashes:
            raise ValueError("Duplicate image path or identical image bytes in manifest.")
        seen_paths.add(image)
        seen_hashes.add(image_hash)
        row["resolved_image"] = image
        row["image_sha256"] = image_hash
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="CSV with image,label; image paths are relative to this CSV")
    parser.add_argument("--labels", type=Path, required=True, help="Exact evaluation class list JSON")
    parser.add_argument("--output", type=Path, required=True, help="New output directory; existing directories are rejected")
    parser.add_argument("--dataset-name", required=True, help="Identify the independently prepared evaluation set")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output directory to preserve previous evidence.")
    labels = read_labels(args.labels)
    manifest = load_manifest(args.manifest, labels)
    from model.model_loader import get_model
    from model.predict import predict_detailed
    _, bundle, version = get_model()
    if set(bundle["class_names"]) != set(labels):
        parser.error("Checkpoint and evaluation labels differ. Run model.submission_check; do not rename or drop labels to hide the mismatch.")
    rows = []
    for row in manifest:
        result = predict_detailed(row["resolved_image"])
        rows.append({"image": row["image"], "image_sha256": row["image_sha256"], "label": row["label"],
                     "predicted_label": result["label"], "confidence": result["confidence"]})
    report = summarize(rows, labels)
    report.update({"dataset": args.dataset_name, "evaluation_kind": "local_user_run_not_official",
                   "created_at_utc": datetime.now(timezone.utc).isoformat(), "model": version,
                   "checkpoint_sha256": sha256(bundle["_checkpoint_path"]),
                   "manifest_sha256": sha256(args.manifest), "labels_sha256": sha256(args.labels),
                   "limitations": ["Manifest provenance and separation from training/tuning must be independently established.",
                                   "Exact-byte duplicate checks do not detect near-duplicates or training overlap.",
                                   "Missing test classes receive zero F1 and remain in the declared macro average."]})
    args.output.mkdir(parents=True)
    (args.output / "metrics.json").write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    with (args.output / "predictions.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (args.output / "confusion_matrix.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["true / predicted", *labels])
        writer.writerows([label, *row] for label, row in zip(labels, report["confusion_matrix"]))
    print(json.dumps({"macro_f1": report["macro_f1"], "accuracy": report["accuracy"], "samples": len(rows), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
