"""Inference engine for crop leaf disease detection."""
import argparse
import sys
import time
from pathlib import Path
from typing import Dict, Any, Union

from PIL import Image, ImageOps
import torch
import torch.nn.functional as F
from torchvision import transforms

try:
    from .model_loader import get_model, DEVICE
except ImportError:
    try:
        from model.model_loader import get_model, DEVICE
    except ImportError:
        from model_loader import get_model, DEVICE

CONFIDENCE_THRESHOLD = 0.75


def get_image_transform(img_size: int, mean: list, std: list) -> transforms.Compose:
    """Build the standard evaluation transform for image input."""
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])


def predict_detailed(image_input: Union[str, Path, Image.Image], top_k: int = 3) -> Dict[str, Any]:
    """
    Run neural network inference on an image and return comprehensive prediction diagnostics.
    """
    # Load or convert PIL Image
    if isinstance(image_input, (str, Path)):
        img_path = Path(image_input)
        if not img_path.is_file():
            raise FileNotFoundError(f"Image not found: {img_path}")
        with Image.open(img_path) as source:
            if source.width * source.height > 50_000_000:
                raise ValueError("Image exceeds the 50 megapixel limit")
            image = ImageOps.exif_transpose(source).convert("RGB")
    elif isinstance(image_input, Image.Image):
        if image_input.width * image_input.height > 50_000_000:
            raise ValueError("Image exceeds the 50 megapixel limit")
        image = ImageOps.exif_transpose(image_input).convert("RGB")
    else:
        raise ValueError("image_input must be a filepath string, Path, or PIL.Image instance")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer")

    # Retrieve cached model and bundle
    model, bundle, version = get_model()

    img_size = bundle.get("img_size", 384)
    mean = bundle.get("normalize_mean", [0.485, 0.456, 0.406])
    std = bundle.get("normalize_std", [0.229, 0.224, 0.225])
    class_names = bundle.get("class_names", [])

    transform = get_image_transform(img_size, mean, std)
    tensor = transform(image).unsqueeze(0).to(DEVICE)

    start_time = time.perf_counter()
    with torch.no_grad():
        with torch.amp.autocast(DEVICE.type, enabled=(DEVICE.type == "cuda")):
            logits = model(tensor)
            probabilities = F.softmax(logits, dim=1).squeeze(0).cpu()
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Top-1 result
    top_prob, top_idx = torch.max(probabilities, dim=0)
    top_label = class_names[top_idx.item()]
    confidence = float(top_prob.item())

    # Top-K ranked candidates
    k = min(top_k, len(class_names))
    topk_probs, topk_indices = torch.topk(probabilities, k=k)
    candidates = [
        {
            "label": class_names[idx.item()],
            "confidence": round(float(prob.item()), 4),
            "percentage": f"{float(prob.item()) * 100:.1f}%"
        }
        for prob, idx in zip(topk_probs, topk_indices)
    ]

    # Parse crop and disease names
    parts = top_label.split("___")
    crop_name = parts[0].replace("_", " ") if len(parts) > 0 else "Unknown"
    disease_name = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"

    return {
        "label": top_label,
        "crop": crop_name,
        "disease": disease_name,
        "confidence": round(confidence, 4),
        "confidence_percentage": f"{confidence * 100:.1f}%",
        "is_confident": confidence >= CONFIDENCE_THRESHOLD,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "latency_ms": latency_ms,
        "model_version": version,
        "top_candidates": candidates,
        "device": str(DEVICE).upper()
    }


def predict(image_path: str) -> str:
    """Return the exact predicted class label string."""
    result = predict_detailed(image_path)
    return result["label"]


def main():
    parser = argparse.ArgumentParser(description="Predict crop disease from an image")
    parser.add_argument("--image", required=True, help="Path to leaf image file")
    parser.add_argument("--top_k", type=int, default=3, help="Number of top candidates to display")
    parser.add_argument("--details", action="store_true", help="Print diagnostics; default stdout is only the class label")
    args = parser.parse_args()

    try:
        diagnostics = predict_detailed(args.image, top_k=args.top_k)
        if not args.details:
            print(diagnostics["label"])
            return 0
        print(f"\nPredicted Class: {diagnostics['label']}")
        print(f"Confidence:      {diagnostics['confidence_percentage']} (Threshold: {diagnostics['confidence_threshold'] * 100:.0f}%)")
        print(f"Latency:         {diagnostics['latency_ms']} ms ({diagnostics['device']})")
        print(f"Model:           {diagnostics['model_version']}")
        print("\nTop Candidates:")
        for i, c in enumerate(diagnostics['top_candidates'], 1):
            print(f"  {i}. {c['label']}: {c['percentage']}")
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
