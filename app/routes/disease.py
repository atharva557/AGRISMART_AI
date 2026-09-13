"""Mandatory core API. Connect trained inference here when available."""
import os.path

from flask import Blueprint,request

from .responses import not_implemented
from model.predict import predict as get_prediction
import config

bp = Blueprint("disease", __name__)


# TODO: Create a seperate ui for image upload or keep it as a SPA by adding upload ui in index.html
@bp.post("/api/disease/predict")
def predict():
    # prediction = get_prediction(config.Config.UPLOAD_FOLDER)
    # _,extension = os.path.split(request.files[])
    return not_implemented("disease")
