"""Tests for Gemini LLM Integration — Mocks genai.Client for offline CI testing."""
import unittest
from unittest.mock import MagicMock, patch

from services.farmer_assistant import FarmerAssistant


def _mock_response(text):
    r = MagicMock()
    r.text = text
    return r


class GeminiLLMTests(unittest.TestCase):
    def setUp(self):
        self.assistant = FarmerAssistant(api_key="fake-key-for-tests")
        self.mock_client = MagicMock()
        self.assistant._client = self.mock_client
        self.sample_context = self.assistant.build_context(
            disease_label="Tomato___Early_blight",
            confidence=0.91,
            crop="Tomato",
            irrigation={"advice": "Delay irrigation", "reason": "rainfall likely in next 24h"},
        )

    def test_explain_calls_gemini_with_correct_model_and_system_instruction(self):
        self.mock_client.models.generate_content.return_value = _mock_response(
            "Your tomato has early blight. Remove affected leaves and avoid overhead watering."
        )

        result = self.assistant.explain(self.sample_context, lang="en")
        self.assertIn("early blight", result.lower())
        call_kwargs = self.mock_client.models.generate_content.call_args.kwargs
        self.assertEqual(call_kwargs["model"], self.assistant.model)
        self.assertIn("STRICT GROUNDING RULES", call_kwargs["config"].system_instruction)

    def test_chat_sends_grounded_context_in_prompt(self):
        self.mock_client.models.generate_content.return_value = _mock_response("Delay irrigation — rain is likely soon.")

        reply = self.assistant.chat("Should I water today?", self.sample_context, session_id="s1", lang="en")
        self.assertTrue("irrigation" in reply.lower() or "water" in reply.lower())
        call_kwargs = self.mock_client.models.generate_content.call_args.kwargs
        sent_contents = call_kwargs["contents"]
        last_text = sent_contents[-1]["parts"][0]["text"]
        self.assertIn("Tomato___Early_blight", last_text)
        self.assertIn("Should I water today?", last_text)

    def test_chat_history_uses_gemini_role_names(self):
        self.mock_client.models.generate_content.return_value = _mock_response("Second reply.")
        self.assistant._sessions["s2"] = [
            {"role": "user", "content": "first question"},
            {"role": "assistant", "content": "first reply"},
        ]
        self.assistant.chat("second question", self.sample_context, session_id="s2", lang="en")

        call_kwargs = self.mock_client.models.generate_content.call_args.kwargs
        sent_contents = call_kwargs["contents"]
        roles = [c["role"] for c in sent_contents]
        self.assertEqual(roles, ["user", "model", "user"])

    def test_llm_failure_falls_back_to_template(self):
        self.mock_client.models.generate_content.side_effect = Exception("simulated network error")
        result = self.assistant.explain(self.sample_context, lang="en")
        self.assertTrue("early" in result.lower() or "blight" in result.lower())

    def test_empty_gemini_response_triggers_fallback(self):
        self.mock_client.models.generate_content.return_value = _mock_response("")
        result = self.assistant.chat("Should I water today?", self.sample_context, session_id="s3", lang="en")
        self.assertIn("delay irrigation", result.lower())

    @patch('services.farmer_assistant.GEMINI_API_KEY', None)
    def test_no_api_key_never_touches_gemini(self):
        assistant = FarmerAssistant(api_key=None)
        self.assertIsNone(assistant._client)
        result = assistant.explain(self.sample_context, lang="en")
        self.assertTrue("early" in result.lower() or "blight" in result.lower())


if __name__ == "__main__":
    unittest.main()
