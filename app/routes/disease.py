"""Mandatory core API. Connect trained inference here when available."""
from flask import Blueprint

from .responses import not_implemented

bp = Blueprint("disease", __name__)


@bp.post("/api/disease/predict")
def predict():
    return not_implemented("disease")
