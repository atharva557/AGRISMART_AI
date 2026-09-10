"""Load trained weights and the exact organizer-provided class mapping."""
import json
from pathlib import Path

CLASSES_PATH = Path(__file__).with_name("classes.json")


def load_classes(path=CLASSES_PATH):
    classes = json.loads(Path(path).read_text(encoding="utf-8"))
    if not classes:
        raise NotImplementedError("Official class labels have not been added yet.")
    if not isinstance(classes, list) or not all(isinstance(label, str) for label in classes):
        raise ValueError("classes.json must contain an ordered list of class-label strings.")
    if len(classes) != len(set(classes)):
        raise ValueError("Class labels must be unique.")
    return classes


def load_model(weights_path=None):
    raise NotImplementedError("Select the architecture and implement trained weight loading.")
