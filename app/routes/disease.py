"""Mandatory core API. Connect trained inference here when available."""
import os
import os.path

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from model.predict import predict_detailed

bp = Blueprint("disease", __name__)


@bp.post("/api/disease/predict")
def predict():
    """Disease prediction endpoint with image upload handling"""
    
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
    if not '.' in file.filename or \
       file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({
            "status": "INVALID_INPUT",
            "message": "Invalid file type. Allowed: JPG, PNG",
            "result": None
        }), 422
    
    # Save file temporarily
    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    
    try:
        file.save(filepath)
        
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
        return jsonify({
            "status": "ERROR",
            "message": f"Prediction failed: {str(e)}",
            "result": None
        }), 500
