"""HTTP adapters for bonus modules A-D."""
from flask import Blueprint, request

from services.contracts import http_status
from services.crop_recommendation import recommend_crops as recommend_crops_service
from services.irrigation import advise_irrigation as advise_irrigation_service
from services.sustainability import calculate_score as calculate_score_service
from services.weather import get_weather_advice as get_weather_advice_service

bp = Blueprint("advisory", __name__)


@bp.post("/api/crops/recommend")
def recommend_crops():
    result = recommend_crops_service(request.get_json(silent=True))
    return result, http_status(result)


@bp.post("/api/irrigation/advise")
def advise_irrigation():
    result = advise_irrigation_service(request.get_json(silent=True))
    return result, http_status(result)


@bp.post("/api/weather/advise")
def advise_weather():
    result = get_weather_advice_service(request.get_json(silent=True))
    return result, http_status(result)


@bp.post("/api/sustainability/score")
def score_sustainability():
    result = calculate_score_service(request.get_json(silent=True))
    return result, http_status(result)
