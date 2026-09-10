"""Pages and application health."""
from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/result")
def result():
    return render_template("result.html")


@bp.get("/api/health")
def health():
    return {"status": "ok", "service": "agrismart"}
