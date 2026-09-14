<<<<<<< HEAD
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
=======
"""Mandatory core API. Connect trained inference here when available."""
import os
import os.path
>>>>>>> 635112f527443e4acb8b707fa1ce187e931d31c5

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from model.predict import predict_detailed

bp = Blueprint("disease", __name__)

# Maximum pixel count accepted before inference — guards against decompression bombs.
# PIL's default is ~89 M pixels. We use a lower explicit ceiling that still covers
# every realistic crop photo at high resolution.
_MAX_IMAGE_PIXELS = 50_000_000  # 50 megapixels — sufficient for any field camera

# Allowed file extensions (lower-cased).
_ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def _allowed_extension(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in _ALLOWED_EXTENSIONS


@bp.post("/api/disease/predict")
def predict():
<<<<<<< HEAD
    """Disease prediction endpoint with image upload and deep inference."""

    # ── 1. File presence check ──────────────────────────────────────────────
    if "image" not in request.files:
=======
    """Disease prediction endpoint with image upload handling"""
    
    # Check if file is present
    if 'image' not in request.files:
>>>>>>> 635112f527443e4acb8b707fa1ce187e931d31c5
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
<<<<<<< HEAD

    # ── 2. Extension whitelist ──────────────────────────────────────────────
    if not _allowed_extension(file.filename):
=======
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    if not '.' in file.filename or \
       file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
>>>>>>> 635112f527443e4acb8b707fa1ce187e931d31c5
        return jsonify({
            "status": "INVALID_INPUT",
            "message": "Unsupported file type. Please upload a JPG or PNG image.",
            "result": None,
        }), 422
<<<<<<< HEAD

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
=======
    
    # Save file temporarily
    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
>>>>>>> 635112f527443e4acb8b707fa1ce187e931d31c5
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    filepath = os.path.normpath(filepath)  # resolve any residual traversal sequences

    try:
        file.save(filepath)
<<<<<<< HEAD

        # ── 5. Validate the file is actually a readable image ────────────────
        # This check runs BEFORE inference. It catches:
        #   - Text/binary files renamed to .jpg
        #   - Truncated or corrupted files
        # We also enforce a pixel ceiling to prevent decompression-bomb attacks.
        try:
            from PIL import Image
            Image.MAX_IMAGE_PIXELS = _MAX_IMAGE_PIXELS
            with Image.open(filepath) as probe:
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

        # ── 6. Run neural network inference ─────────────────────────────────
        diagnostics = predict_detailed(filepath)
        _cleanup(filepath)

        label = diagnostics["label"]
        confidence = diagnostics["confidence"]
        crop = diagnostics["crop"]
        disease = diagnostics["disease"]

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

        return jsonify({
            "status": "OK",
            "result": {
                "disease_name": display_title,
                "raw_label": label,
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

    except Exception as exc:
        _cleanup(filepath)
        # Log the full traceback internally; return a safe generic message to the client.
        logger.error("Prediction failed for uploaded file: %s", exc, exc_info=True)
=======
        
        try:
            details = predict_detailed(filepath)
            
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                "status": "OK",
                "result": {
                    "disease": details["clean_label"],
                    "disease_name": details["clean_label"],
                    "confidence": details["confidence"],
                    "is_confident": details["is_confident"],
                    "recommendations": [
                        "Consult with a local agricultural expert for confirmation",
                        "Monitor affected plants closely",
                        "Isolate infected plants if possible"
                    ],
                    "description": f"Detected: {details['clean_label']}"
                },
                "limitations": [
                    "Model confidence threshold is 75%",
                    "Consult expert for low confidence predictions",
                    "Lab-trained model may have reduced accuracy on field photos"
                ]
            }), 200
            
        except NotImplementedError as e:
            # Model not yet implemented
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({
                "status": "DATA_UNAVAILABLE",
                "message": "Disease detection model is not yet implemented. The image upload works, but prediction is pending integration.",
                "result": None,
                "error": str(e)
            }), 503
            
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
>>>>>>> 635112f527443e4acb8b707fa1ce187e931d31c5
        return jsonify({
            "status": "ERROR",
            "message": "An error occurred while analysing the image. "
                       "Please try again with a clear, well-lit crop photograph.",
            "result": None,
        }), 500


def _cleanup(filepath: str) -> None:
    """Remove a temporary upload file, ignoring errors."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass
