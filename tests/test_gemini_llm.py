"""
tests/test_gemini_llm.py

Tests the Gemini-backed LLM mode of FarmerAssistant WITHOUT making real
network calls — we mock `genai.Client` so these run offline / in CI. The
mocked response objects are shaped exactly like Gemini's real SDK response
(per https://ai.google.dev/gemini-api/docs/text-generation — `response.text`
is the documented way to read the output), so a passing test here means our
calling code (model name, contents shape, system_instruction wiring, role
mapping for multi-turn history) is correct against the real contract — only
the network round-trip itself is stubbed out.

The DEFAULT test suite (tests/test_farmer_assistant.py) runs in template
mode and needs no key/network at all — these tests specifically exercise
the LLM code path.
"""

import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest  # noqa: E402

from services.farmer_assistant import FarmerAssistant  # noqa: E402


@pytest.fixture
def mock_gemini_client():
    """A FarmerAssistant with a fake Gemini client wired in, so _llm_generate
    is exercised without any real API key or network call."""
    assistant = FarmerAssistant(api_key="fake-key-for-tests")
    mock_client = MagicMock()
    assistant._client = mock_client
    return assistant, mock_client


@pytest.fixture
def sample_context():
    a = FarmerAssistant(api_key=None)  # template-mode instance just to build context
    return a.build_context(
        disease_label="Tomato___Early_blight",
        confidence=0.91,
        crop="Tomato",
        irrigation={"advice": "Delay irrigation", "reason": "rainfall likely in next 24h"},
    )


def _mock_response(text):
    r = MagicMock()
    r.text = text
    return r


def test_explain_calls_gemini_with_correct_model_and_system_instruction(mock_gemini_client, sample_context):
    assistant, mock_client = mock_gemini_client
    mock_client.models.generate_content.return_value = _mock_response(
        "Your tomato has early blight. Remove affected leaves and avoid overhead watering."
    )

    result = assistant.explain(sample_context, lang="en")

    assert "early blight" in result.lower()
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == assistant.model
    assert "STRICT GROUNDING RULES" in call_kwargs["config"].system_instruction


def test_chat_sends_grounded_context_in_prompt(mock_gemini_client, sample_context):
    assistant, mock_client = mock_gemini_client
    mock_client.models.generate_content.return_value = _mock_response("Delay irrigation — rain is likely soon.")

    reply = assistant.chat("Should I water today?", sample_context, session_id="s1", lang="en")

    assert "irrigation" in reply.lower() or "water" in reply.lower()
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    sent_contents = call_kwargs["contents"]
    # last content entry should contain our grounded context JSON + the question
    last_text = sent_contents[-1]["parts"][0]["text"]
    assert "Tomato___Early_blight" in last_text
    assert "Should I water today?" in last_text


def test_chat_history_uses_gemini_role_names(mock_gemini_client, sample_context):
    """Gemini expects role 'model' for the assistant turn, not 'assistant' —
    verify our history translation does this correctly."""
    assistant, mock_client = mock_gemini_client
    mock_client.models.generate_content.return_value = _mock_response("Second reply.")

    # seed a fake prior turn directly into session history
    assistant._sessions["s2"] = [
        {"role": "user", "content": "first question"},
        {"role": "assistant", "content": "first reply"},
    ]
    assistant.chat("second question", sample_context, session_id="s2", lang="en")

    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    sent_contents = call_kwargs["contents"]
    roles = [c["role"] for c in sent_contents]
    assert roles == ["user", "model", "user"]  # translated + new turn appended


def test_llm_failure_falls_back_to_template(mock_gemini_client, sample_context):
    assistant, mock_client = mock_gemini_client
    mock_client.models.generate_content.side_effect = Exception("simulated network error")

    # Should not raise — falls back to template mode and still answers.
    result = assistant.explain(sample_context, lang="en")
    assert "early" in result.lower() or "blight" in result.lower()


def test_empty_gemini_response_triggers_fallback(mock_gemini_client, sample_context):
    assistant, mock_client = mock_gemini_client
    mock_client.models.generate_content.return_value = _mock_response("")  # empty text

    result = assistant.chat("Should I water today?", sample_context, session_id="s3", lang="en")
    # falls back to template QA, which still answers from the grounded context
    assert "delay irrigation" in result.lower()


def test_no_api_key_never_touches_gemini(sample_context):
    """With no key at all, FarmerAssistant must run in pure template mode —
    no client created, no network attempted."""
    assistant = FarmerAssistant(api_key=None)
    assert assistant._client is None
    result = assistant.explain(sample_context, lang="en")
    assert "early" in result.lower() or "blight" in result.lower()
