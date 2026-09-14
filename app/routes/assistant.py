"""Bonus E: farmer assistant API.

Routes
------
GET  /api/assistant/languages  → supported language codes/names
POST /api/assistant/explain    → grounded plain-language explanation
POST /api/assistant/chat       → grounded multi-turn Q&A
POST /api/assistant/reset      → clear a chat session's memory
"""

import logging

from flask import Blueprint, request, jsonify

from services.farmer_assistant import FarmerAssistant
from utils.translation_utils import SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

bp = Blueprint("assistant", __name__)
assistant = FarmerAssistant()  # picks up GEMINI_API_KEY / ASSISTANT_API_KEY from env automatically


@bp.get("/api/assistant/languages")
def languages():
    return jsonify({"languages": SUPPORTED_LANGUAGES})


@bp.post("/api/assistant/explain")
def explain():
    data = request.get_json(force=True, silent=True) or {}
    lang = data.get("lang", "en")

    if "disease_label" not in data:
        return jsonify({"error": "disease_label is required"}), 400

    context = assistant.build_context(
        disease_label=data.get("disease_label"),
        confidence=data.get("confidence"),
        crop=data.get("crop"),
        stage=data.get("stage"),
        soil=data.get("soil"),
        irrigation=data.get("irrigation"),
        weather=data.get("weather"),
        sustainability=data.get("sustainability"),
        crop_recommendation=data.get("crop_recommendation"),
        assessment=data.get("assessment"),
    )
    explanation = assistant.explain(context, lang=lang)
    return jsonify({"explanation": explanation, "lang": lang, "context": context})


@bp.post("/api/assistant/chat")
def chat():
    data = request.get_json(force=True, silent=True) or {}
    message = data.get("message")
    context = data.get("context")
    session_id = data.get("session_id", "default")
    lang = data.get("lang", "en")

    if not message:
        return jsonify({"error": "message is required"}), 400
    if not context:
        return jsonify({"error": "context is required — call /api/assistant/explain first "
                                  "and pass the 'context' object it returns"}), 400

    reply = assistant.chat(message, context, session_id=session_id, lang=lang)
    return jsonify({"reply": reply, "lang": lang, "session_id": session_id})


@bp.post("/api/assistant/reset")
def reset():
    data = request.get_json(force=True, silent=True) or {}
    assistant.reset_session(data.get("session_id", "default"))
    return jsonify({"status": "ok"})
