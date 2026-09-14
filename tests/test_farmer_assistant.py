"""Tests for Farmer Assistant (Bonus E) — Runs offline with deterministic fallback."""
import unittest
from unittest.mock import patch

from services.disease_info import DISEASE_KB, get_disease_info
from services.farmer_assistant import FarmerAssistant
from utils.translation_utils import SUPPORTED_LANGUAGES, translate_text


class FarmerAssistantTests(unittest.TestCase):
    def setUp(self):
        self.assistant = FarmerAssistant(api_key=None)
        self.assistant._client = None
        self.sample_context = self.assistant.build_context(
            disease_label="Tomato___Early_blight",
            confidence=0.91,
            crop="Tomato",
            stage="Growing",
            irrigation={"advice": "Delay irrigation", "reason": "rainfall likely in next 24h"},
            weather={"temp_c": "28-32", "rain_probability": "High"},
            sustainability={"score": 78, "note": "Estimated reduction in unnecessary water use this week"},
        )

    def test_disease_kb_has_shared_class_list_entries(self):
        self.assertIn("Tomato___Early_blight", DISEASE_KB)
        self.assertIn("Potato___Late_blight", DISEASE_KB)
        self.assertEqual(get_disease_info("Nonexistent___Class")["severity"], "unknown")

    def test_build_context_is_grounded_only_in_given_facts(self):
        core = self.sample_context["core_detection"]
        self.assertEqual(core["predicted_class"], "Tomato___Early_blight")
        self.assertEqual(core["confidence"], 0.91)
        self.assertTrue("precautions" in core and len(core["precautions"]) > 0)
        self.assertEqual(self.sample_context["irrigation_recommendation_bonus_B"]["advice"], "Delay irrigation")

    def test_explain_template_mode_mentions_grounded_facts(self):
        text = self.assistant.explain(self.sample_context, lang="en")
        self.assertTrue("Early" in text or "blight" in text.lower())
        self.assertIn("Delay irrigation", text)
        self.assertIn("78", text)

    def test_explain_healthy_case(self):
        ctx = self.assistant.build_context(disease_label="Tomato___healthy", confidence=0.98, crop="Tomato")
        text = self.assistant.explain(ctx, lang="en")
        self.assertIn("healthy", text.lower())

    def test_chat_answers_from_context_not_invented(self):
        reply = self.assistant.chat("Should I water today?", self.sample_context, session_id="test-1", lang="en")
        self.assertIn("Delay irrigation", reply)

    def test_chat_refuses_ungrounded_question(self):
        reply = self.assistant.chat("What is the current market price of tomatoes?", self.sample_context, session_id="test-2")
        self.assertTrue("don't have" in reply.lower() or "extension officer" in reply.lower())

    def test_chat_session_memory_is_isolated(self):
        self.assistant.chat("hello", self.sample_context, session_id="s1")
        self.assistant.chat("hi again", self.sample_context, session_id="s2")
        self.assertEqual(len(self.assistant._sessions["s1"]), 2)
        self.assertEqual(len(self.assistant._sessions["s2"]), 2)
        self.assistant.reset_session("s1")
        self.assertNotIn("s1", self.assistant._sessions)

    @patch('utils.translation_utils._BACKEND_AVAILABLE', False)
    def test_translation_falls_back_gracefully_when_offline(self):
        text = translate_text("Delay irrigation", target_lang="hi")
        self.assertTrue(isinstance(text, str) and len(text) > 0)

    def test_supported_languages_includes_key_indian_languages(self):
        for code in ["hi", "gu", "mr", "ta", "te", "kn", "bn", "pa"]:
            self.assertIn(code, SUPPORTED_LANGUAGES)


if __name__ == "__main__":
    unittest.main()
