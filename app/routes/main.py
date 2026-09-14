"""Pages and application health."""
from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.get("/")
def home():
    """Home/landing page"""
    return render_template("home.html")


@bp.get("/disease")
def disease_upload():
    """Disease detection upload page"""
    return render_template("disease_upload.html")


@bp.get("/disease/result")
def disease_result():
    """Disease detection result page"""
    return render_template("disease_result.html")


@bp.get("/advisory")
def advisory():
    """Advisory dashboard (modules A-D)"""
    return render_template("advisory.html")


@bp.get("/about")
def about():
    """About page with documentation"""
    return render_template("about.html")


@bp.get("/api/health")
def health():
    """Health check endpoint. Reports application availability and ML model status."""
    import os

    # Check whether the primary CV model checkpoint is present on disk.
    # We do NOT load the model here — that is handled lazily on first inference.
    from model.model_loader import PRIMARY_CHECKPOINT, FALLBACK_CHECKPOINT
    cv_ready = PRIMARY_CHECKPOINT.is_file() or FALLBACK_CHECKPOINT.is_file()

    # Check crop recommendation model
    from services.crop_recommendation import MODEL_PATH as CROP_MODEL_PATH
    crop_ready = CROP_MODEL_PATH.is_file()

    return {
        "status": "ok",
        "service": "agrismart",
        "models": {
            "cv_checkpoint_present": cv_ready,
            "crop_model_present": crop_ready,
        },
    }
