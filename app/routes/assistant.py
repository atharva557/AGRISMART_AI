"""Bonus E: farmer assistant API."""
from flask import Blueprint

from .responses import not_implemented

bp = Blueprint("assistant", __name__)


@bp.post("/api/assistant/chat")
def chat():
    return not_implemented("assistant")
