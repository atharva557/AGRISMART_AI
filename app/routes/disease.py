"""Disease detection API endpoint integrating trained CV model and agronomic KB."""
import os
import os.path
import logging

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from model.predict import predict_detailed
from services.disease_info import DISEASE_KB

logger = logging.getLogger(__name__)

bp = Blueprint("disease", __name__)


@bp.post("/api/disease/predict")
def predict():
    """Disease prediction endpoint with image upload and deep inference."""
    
    # Check if file is present
    if 'image' not in request.files:
        return jsonify({
            "status": "INVALID_INPUT",
            "message": "No image file provided",
            "result": None
        }), 422
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({
            "status": "INVALID_INPUT",
            "message": "No file selected",
            "result": None
        }), 422
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    if '.' not in file.filename or \
       file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({
            "status": "INVALID_INPUT",
            "message": "Invalid file type. Allowed: JPG, PNG",
            "result": None
        }), 422
    
    # Save file temporarily
    filename = secure_filename(file.filename)
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    
    try:
        file.save(filepath)
        
        # Run neural network inference
        diagnostics = predict_detailed(filepath)
        
        # Clean up uploaded temporary file
        if os.path.exists(filepath):
            os.remove(filepath)
            
        label = diagnostics["label"]
        confidence = diagnostics["confidence"]
        crop = diagnostics["crop"]
        disease = diagnostics["disease"]
        
        # Lookup verified knowledge base info
        kb_entry = DISEASE_KB.get(label, {})
        
        # Format human-readable title
        if "healthy" in label.lower():
            display_title = f"{crop} — Healthy Foliage"
            description = kb_entry.get("description", f"The leaf appears healthy with no visible signs of pathogen infection.")
            recommendations = kb_entry.get("precautions", [
                "Maintain standard watering and nutrient schedules.",
                "Continue routine scouting for early pest or fungal signs.",
                "Ensure good air circulation between crop beds."
            ])
            symptoms = ["Normal, green, uniform leaf tissue", "No visible necrotic spots or mildew"]
            severity = "none"
        else:
            display_title = f"{crop} — {disease}"
            description = kb_entry.get("description", f"Detected symptoms characteristic of {disease} on {crop}.")
            recommendations = kb_entry.get("precautions", [
                "Consult with a local agricultural extension officer for field confirmation.",
                "Isolate or prune visibly infected plant parts to prevent spreading.",
                "Avoid overhead irrigation to reduce foliage wetness."
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
                "top_candidates": diagnostics["top_candidates"]
            },
            "limitations": [
                "Model confidence threshold is 75%.",
                "Consult local agronomists for critical field decisions.",
                "In-field lighting and dirt may affect accuracy compared to lab benchmarks."
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({
            "status": "ERROR",
            "message": f"Prediction failed: {str(e)}",
            "result": None
        }), 500
