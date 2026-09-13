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
    """Health check endpoint"""
    return {"status": "ok", "service": "agrismart"}
