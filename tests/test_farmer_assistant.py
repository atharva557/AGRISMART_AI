"""
tests/test_farmer_assistant.py

Runs entirely offline / without GEMINI_API_KEY — exercises the
deterministic template fallback so CI / judges can verify Bonus E works
even with no internet or API key configured.

Run with:  pytest tests/test_farmer_assistant.py -v
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest  # noqa: E402

from services.farmer_assistant import FarmerAssistant  # noqa: E402
from services.disease_info import get_disease_info, DISEASE_KB  # noqa: E402
from utils.translation_utils import translate_text, SUPPORTED_LANGUAGES  # noqa: E402


@pytest.fixture
def assistant():
    # Force template mode regardless of the environment's API key so this
    # test suite is deterministic and offline.
    a = FarmerAssistant(api_key=None)
    a._client = None
    return a


@pytest.fixture
def sample_context(assistant):
    return assistant.build_context(
        disease_label="Tomato___Early_blight",
        confidence=0.91,
        crop="Tomato",
        stage="Growing",
        irrigation={"advice": "Delay irrigation", "reason": "rainfall likely in next 24h"},
        weather={"temp_c": "28-32", "rain_probability": "High"},
        sustainability={"score": 78, "note": "Estimated reduction in unnecessary water use this week"},
    )


def test_disease_kb_has_shared_class_list_entries():
    # Sanity check a few of the labels named in Section 4.1 of the brief.
    assert "Tomato___Early_blight" in DISEASE_KB
    assert "Potato___Late_blight" in DISEASE_KB
    assert get_disease_info("Nonexistent___Class")["severity"] == "unknown"


def test_build_context_is_grounded_only_in_given_facts(sample_context):
    core = sample_context["core_detection"]
    assert core["predicted_class"] == "Tomato___Early_blight"
    assert core["confidence"] == 0.91
    assert "precautions" in core and len(core["precautions"]) > 0
    assert sample_context["irrigation_recommendation_bonus_B"]["advice"] == "Delay irrigation"


def test_explain_template_mode_mentions_grounded_facts(assistant, sample_context):
    text = assistant.explain(sample_context, lang="en")
    assert "Early" in text or "blight" in text.lower()
    assert "Delay irrigation" in text
    assert "78" in text  # sustainability score passed through


def test_explain_healthy_case(assistant):
    ctx = assistant.build_context(disease_label="Tomato___healthy", confidence=0.98, crop="Tomato")
    text = assistant.explain(ctx, lang="en")
    assert "healthy" in text.lower()


def test_chat_answers_from_context_not_invented(assistant, sample_context):
    reply = assistant.chat("Should I water today?", sample_context, session_id="test-1", lang="en")
    assert "Delay irrigation" in reply


def test_chat_refuses_ungrounded_question(assistant, sample_context):
    reply = assistant.chat("What is the current market price of tomatoes?", sample_context, session_id="test-2")
    assert "don't have" in reply.lower() or "extension officer" in reply.lower()


def test_chat_session_memory_is_isolated(assistant, sample_context):
    assistant.chat("hello", sample_context, session_id="s1")
    assistant.chat("hi again", sample_context, session_id="s2")
    assert len(assistant._sessions["s1"]) == 2
    assert len(assistant._sessions["s2"]) == 2
    assistant.reset_session("s1")
    assert "s1" not in assistant._sessions


def test_translation_falls_back_gracefully_when_offline():
    # Should never raise, even without network — worst case returns English.
    text = translate_text("Delay irrigation", target_lang="hi")
    assert isinstance(text, str) and len(text) > 0


def test_supported_languages_includes_key_indian_languages():
    for code in ["hi", "gu", "mr", "ta", "te", "kn", "bn", "pa"]:
        assert code in SUPPORTED_LANGUAGES
