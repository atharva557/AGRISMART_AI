"""Check saved-model labels against local and organizer lists. No training."""
import argparse
import json
from pathlib import Path


def read_labels(path):
    labels = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if (not isinstance(labels, list) or not labels or
            not all(isinstance(x, str) and x.strip() for x in labels) or len(labels) != len(set(labels))):
        raise ValueError("Labels must be a nonempty JSON array of unique, nonempty strings.")
    return labels


def compare_labels(model_labels, expected_labels):
    return {"same_label_set": set(model_labels) == set(expected_labels),
            "same_order": model_labels == expected_labels,
            "missing_from_model": sorted(set(expected_labels) - set(model_labels)),
            "extra_model_labels": sorted(set(model_labels) - set(expected_labels))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, help="Exact organizer JSON class list, when available")
    args = parser.parse_args()
    from model.model_loader import get_model, CLASSES_PATH
    _, bundle, version = get_model()
    actual = bundle["class_names"]
    local = compare_labels(actual, read_labels(CLASSES_PATH))
    organizer = compare_labels(actual, read_labels(args.labels)) if args.labels else None
    print(json.dumps({"model": version, "checkpoint": bundle["_checkpoint_path"],
                      "local_labels": local, "organizer_labels": organizer,
                      "status": "PENDING_ORGANIZER_LABELS" if organizer is None else "CHECKED",
                      "note": "No labels were remapped and no weights were changed. String-output evaluation needs the same label set; tensor consumers also need the same order."}, indent=2))
    return 0 if local["same_order"] and organizer and organizer["same_label_set"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
