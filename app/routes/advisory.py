"""Atharva: bonus modules A-D. Put decision logic in services/."""
from flask import Blueprint

from .responses import not_implemented

bp = Blueprint("advisory", __name__)


@bp.post("/api/crops/recommend")
def recommend_crops():
    return not_implemented("crop_recommendation")


@bp.post("/api/irrigation/advise")
def advise_irrigation():
    return not_implemented("irrigation")


@bp.post("/api/weather/advise")
def advise_weather():
    return not_implemented("weather")


@bp.post("/api/sustainability/score")
def score_sustainability():
    return not_implemented("sustainability")
