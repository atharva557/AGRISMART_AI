"""Conservative photo triage; these heuristics do not identify plants or disease."""
import numpy as np
from PIL import Image, ImageOps

RETAKE_STEPS = [
    "Photograph one affected leaf in daylight, avoiding glare and deep shadow.",
    "Move closer so the leaf fills the frame, tap to focus, and hold the camera steady.",
    "If another clear photo is inconclusive, ask a local agricultural extension officer to inspect the plant.",
]


def assess_photo(image):
    image = ImageOps.exif_transpose(image).convert("RGB")
    width, height = image.size
    gray = image.convert("L")
    gray.thumbnail((512, 512), Image.Resampling.BILINEAR)
    pixels = np.asarray(gray, dtype=np.float32)
    spread = float(pixels.std())
    lap = (-4 * pixels[1:-1, 1:-1] + pixels[:-2, 1:-1] + pixels[2:, 1:-1]
           + pixels[1:-1, :-2] + pixels[1:-1, 2:])
    sharpness = float(lap.var()) if lap.size else 0.0
    issues = []
    if min(width, height) < 192:
        issues.append("The photo is too small. Use an original image at least 192 pixels on each side.")
    if float((pixels < 20).mean()) > 0.98:
        issues.append("The photo is almost entirely dark. Retake it in daylight.")
    elif float((pixels > 245).mean()) > 0.98:
        issues.append("The photo is almost entirely overexposed. Move out of glare and retake it.")
    elif spread < 1.0:
        issues.append("The photo contains almost no visible detail. Retake a focused photo of the leaf.")
    warnings = []
    if not issues and sharpness < 20:
        warnings.append("The photo may be blurred or have little texture. Check that the symptoms are in focus.")
    return {
        "status": "RETAKE_REQUIRED" if issues else "CHECK_FOCUS" if warnings else "PASS",
        "issues": issues, "warnings": warnings, "next_steps": RETAKE_STEPS,
        "measurements": {"width": width, "height": height, "gray_std": round(spread, 2),
                         "laplacian_variance": round(sharpness, 2)},
        "method": "photo-triage-v1",
        "limitation": "Experimental image-quality rules; not a plant detector, calibrated blur detector, or accuracy guarantee.",
    }
