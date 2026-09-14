"""Prediction interface for single-image judging and application integration."""
import argparse
import sys
from pathlib import Path
import io
import pickle
import timm
import torch
from PIL import Image
from torchvision import transforms

MODEL_PATH = Path(__file__).parent / "weights" / "cv" / "model_v3.pkl"

# Explicit pixel ceiling guards against decompression-bomb payloads.
# PIL's built-in default (~89 M px) is preserved by keeping this at the same
# value used by the upload route. Both layers enforce the same limit.
_MAX_IMAGE_PIXELS = 50_000_000
Image.MAX_IMAGE_PIXELS = _MAX_IMAGE_PIXELS


class CPU_Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "torch.storage" and name == "_load_from_bytes":
            return lambda b: torch.load(io.BytesIO(b), map_location="cpu")
        return super().find_class(module, name)


def predict_detailed(image_path: str):
    """Load model, preprocess image, run prediction, and return disease info dictionary."""
    if not Path(image_path).is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Step 1: Select compute device (CPU or GPU) and load saved checkpoint bundle
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    with MODEL_PATH.open("rb") as file:
        if torch.cuda.is_available():
            pkl_file = pickle.load(file)
        else:
            pkl_file = CPU_Unpickler(file).load()

    # Step 2: Extract model parameters from checkpoint
    img_size = pkl_file.get("img_size", 384)
    mean = pkl_file.get("normalize_mean", [0.485, 0.456, 0.406])
    std = pkl_file.get("normalize_std", [0.229, 0.224, 0.225])
    num_classes = pkl_file["num_classes"]
    arch = pkl_file["architecture"].lower()

    # Step 3: Instantiate model architecture and load trained weights
    if "convnext_tiny" in arch:
        model = timm.create_model("convnext_tiny.fb_in22k_ft_in1k_384", pretrained=False, num_classes=num_classes)
    else:
        model = timm.create_model(pkl_file["architecture"], pretrained=False, num_classes=num_classes)

    model.load_state_dict(pkl_file["state_dict"])
    model = model.to(device)
    model.eval()

    # Step 4: Preprocess input image (RGB convert, resize to 384x384, normalize)
    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean, std)
    ])

    img = Image.open(image_path).convert("RGB")
    img_tensor = transform(img).unsqueeze(0).to(device)

    # Step 5: Run inference pass and calculate confidence score
    with torch.no_grad():
        output = model(img_tensor)
        probs = torch.softmax(output, dim=1)
        confidence, max_prob = torch.max(probs, dim=1)
        conf_val = confidence.item()
        idx = max_prob.item()

    # Step 6: Format raw dataset label into clean display string
    raw_label = pkl_file["class_names"][idx]
    if "___" in raw_label:
        crop, condition = raw_label.split("___", 1)
        clean_label = f"{crop.replace('_', ' ').strip()} - {condition.replace('_', ' ').strip()}"
    else:
        clean_label = raw_label.replace("_", " ").strip()

    return {
        "raw_label": raw_label,
        "clean_label": clean_label,
        "confidence": conf_val,
        "is_confident": conf_val >= 0.75
    }


def predict(image_path: str) -> str:
    """Return clean human-readable class label for single image prediction."""
    return predict_detailed(image_path)["clean_label"]


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
