"""Prediction interface for single-image judging and application integration."""
import argparse
import sys
from pathlib import Path
import pickle


MODEL_PATH = Path(__file__).resolve().parents[1] / "notebooks" / "cv_model_notebooks" / "model_v3.pkl"

def predict(image_path: str) -> str:
    """Return an exact official class label once trained inference is implemented."""
    if not Path(image_path).is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")
    with MODEL_PATH.open("rb") as file:
        model = pickle.load(file)


def main():
    parser = argparse.ArgumentParser(description="Predict a crop disease from an image")
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    try:
        label = predict(args.image)
    except (FileNotFoundError, NotImplementedError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
