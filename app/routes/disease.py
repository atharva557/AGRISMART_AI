"""Disease detection API endpoint integrating trained CV model and agronomic KB.

Security measures implemented:
- File extension whitelist (png, jpg, jpeg)
- PIL image open + convert validation before inference (rejects non-images)
- PIL decompression-bomb protection via MAX_IMAGE_PIXELS limit
- UUID-prefixed filenames prevent collisions and path traversal
- Werkzeug secure_filename() sanitises original filename
- Temporary file always deleted on both success and error paths
- Internal exception details are NOT exposed in user-facing error messages
"""
import logging
import os
import uuid
import json
from pathlib import Path

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from services.disease_info import get_disease_info
from services.photo_quality import assess_photo
from services.diagnosis_assessment import diagnosis_assessment

logger = logging.getLogger(__name__)

bp = Blueprint("disease", __name__)

# Maximum pixel count accepted before inference — guards against decompression bombs.
# PIL's default is ~89 M pixels. We use a lower explicit ceiling that still covers
# every realistic crop photo at high resolution.
_MAX_IMAGE_PIXELS = 50_000_000  # 50 megapixels — sufficient for any field camera

# Allowed file extensions (lower-cased).
_ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


@bp.get("/api/disease/classes")
def classes():
    labels = json.loads((Path(__file__).resolve().parents[2] / "model/classes.json").read_text(encoding="utf-8"))
    return jsonify({"labels": labels, "crops": sorted({label.split("___")[0] for label in labels}),
                    "scope": "Local model classes; organizer label alignment is pending."})


def _allowed_extension(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in _ALLOWED_EXTENSIONS


@bp.post("/api/disease/predict")
def predict():
    """Disease prediction endpoint with image upload and deep inference."""

    # ── 1. File presence check ──────────────────────────────────────────────
    if "image" not in request.files:
        return jsonify({
            "status": "INVALID_INPUT",
            "message": "No image file provided. Send a multipart/form-data request with field name 'image'.",
            "result": None,
        }), 422

    file = request.files["image"]

    if file.filename == "":
        return jsonify({
            "status": "INVALID_INPUT",
            "message": "No file selected.",
            "result": None,
        }), 422

    # ── 2. Extension whitelist ──────────────────────────────────────────────
    if not _allowed_extension(file.filename):
        return jsonify({
            "status": "INVALID_INPUT",
            "message": "Unsupported file type. Please upload a JPG or PNG image.",
            "result": None,
        }), 422

    # ── 3. Lazy import of deep learning inference module ────────────────────
    try:
        from model.predict import predict_detailed
    except ImportError as exc:
        logger.error("Inference dependency missing: %s", exc)
        return jsonify({
            "status": "ERROR",
            "message": "Inference engine dependencies are not installed. Run 'pip install -r requirements.txt'.",
            "result": None,
        }), 503

    # ── 4. Save to a UUID-prefixed temporary path ───────────────────────────
    safe_name = secure_filename(file.filename)
    filename = f"{uuid.uuid4().hex}_{safe_name}"
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    filepath = os.path.join(upload_folder, filename)
    filepath = os.path.normpath(filepath)  # resolve any residual traversal sequences

    try:
        os.makedirs(upload_folder, exist_ok=True)
        file.save(filepath)

        # ── 5. Validate the file is actually a readable image ────────────────
        # This check runs BEFORE inference. It catches:
        #   - Text/binary files renamed to .jpg
        #   - Truncated or corrupted files
        # We also enforce a pixel ceiling to prevent decompression-bomb attacks.
        try:
            from PIL import Image
            with Image.open(filepath) as probe:
                if probe.format not in {"JPEG", "PNG"} or probe.width * probe.height > _MAX_IMAGE_PIXELS:
                    raise ValueError("Unsupported format or image pixel limit exceeded")
                probe.verify()  # raises if not a valid image
        except Exception as img_err:
            _cleanup(filepath)
            logger.warning("Uploaded file is not a valid image: %s", img_err)
            return jsonify({
                "status": "INVALID_INPUT",
                "message": "The uploaded file could not be read as a valid image. "
                           "Please upload a clear JPG or PNG photograph.",
                "result": None,
            }), 422

        with Image.open(filepath) as photo:
            quality = assess_photo(photo)
        if quality["status"] == "RETAKE_REQUIRED":
            return jsonify({"status": "RETAKE_REQUIRED", "result": None,
                            "message": "Please retake the photo before analysis.", "photo_quality": quality}), 200

        selected_crop = request.form.get("crop", "").strip()
        if selected_crop:
            labels = json.loads((Path(__file__).resolve().parents[2] / "model/classes.json").read_text(encoding="utf-8"))
            if selected_crop not in {label.split("___")[0] for label in labels}:
                return jsonify({"status": "INVALID_INPUT", "message": "Choose a supported crop or leave it unspecified.", "result": None}), 422

        # ── 6. Run neural network inference ─────────────────────────────────
        diagnostics = predict_detailed(filepath)
        _cleanup(filepath)

        label = diagnostics["label"]
        confidence = diagnostics["confidence"]
        crop = diagnostics["crop"]
        disease = diagnostics["disease"]
        assessment = diagnosis_assessment(confidence, crop_mismatch=bool(selected_crop and selected_crop != label.split("___")[0]))

        # ── 7. Knowledge-base lookup ─────────────────────────────────────────
        kb_entry = get_disease_info(label)

        # ── 8. Build user-facing response ────────────────────────────────────
        if "healthy" in label.lower():
            display_title = f"{crop} — Healthy Foliage"
            description = kb_entry.get(
                "description",
                "The leaf appears healthy with no visible signs of pathogen infection.",
            )
            recommendations = kb_entry.get("precautions", [
                "Maintain standard watering and nutrient schedules.",
                "Continue routine scouting for early pest or fungal signs.",
                "Ensure good air circulation between crop beds.",
            ])
            symptoms = kb_entry.get("symptoms", [
                "Normal green coloration",
                "No visible necrotic spots or mildew",
            ])
            severity = "none"
        else:
            display_title = f"{crop} — {disease}"
            description = kb_entry.get(
                "description",
                f"Detected symptoms characteristic of {disease} on {crop}.",
            )
            recommendations = kb_entry.get("precautions", [
                "Consult with a local agricultural extension officer for field confirmation.",
                "Isolate or prune visibly infected plant parts to prevent spreading.",
                "Avoid overhead irrigation to reduce foliage wetness.",
            ])
            symptoms = kb_entry.get("symptoms", ["Visible discoloration or lesions on leaf surface."])
            severity = kb_entry.get("severity", "moderate")

        if assessment["withheld"]:
            display_title = "Photo needs verification"
            description = assessment["message"]
            symptoms = []
            severity = "unknown"
            recommendations = assessment["next_steps"]

        return jsonify({
            "status": "OK",
            "result": {
                "disease_name": display_title,
                "raw_label": label,
                "selected_crop": selected_crop or None,
                "assessment": assessment,
                "photo_quality": quality,
                "crop": crop,
                "disease": disease,
                "confidence": confidence,
                "confidence_percentage": diagnostics["confidence_percentage"],
                "is_confident": diagnostics["is_confident"],
                "confidence_threshold": diagnostics["confidence_threshold"],
                "latency_ms": diagnostics["latency_ms"],
                "model_version": diagnostics["model_version"],
                "description": description,
                "symptoms": symptoms,
                "severity": severity,
                "recommendations": recommendations,
                "top_candidates": diagnostics["top_candidates"],
            },
            "limitations": [
                "Model confidence threshold is 75%.",
                "Consult local agronomists for critical field decisions.",
                "In-field lighting and dirt may affect accuracy compared to lab benchmarks.",
            ],
        }), 200

    except (FileNotFoundError, RuntimeError) as exc:
        logger.error("Inference model unavailable: %s", exc, exc_info=True)
        return jsonify({"status": "DATA_UNAVAILABLE", "message": "The inference model is unavailable. Check the installed checkpoints and dependencies.", "result": None}), 503
    except Exception as exc:
        _cleanup(filepath)
        # Log the full traceback internally; return a safe generic message to the client.
        logger.error("Prediction failed for uploaded file: %s", exc, exc_info=True)
        return jsonify({
            "status": "ERROR",
            "message": "An error occurred while analysing the image. "
                       "Please try again with a clear, well-lit crop photograph.",
            "result": None,
        }), 500
    finally:
        _cleanup(filepath)


def _cleanup(filepath: str) -> None:
    """Remove a temporary upload file, ignoring errors."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass
