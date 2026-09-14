"""Image triage and uncertainty integration, using fixtures and mocked inference."""
import io
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image
from app import create_app
from services.diagnosis_assessment import diagnosis_assessment
from services.photo_quality import assess_photo
from services.farmer_assistant import FarmerAssistant
from test_disease_regressions import diagnostics, image_bytes


def test_unusable_photo_does_not_call_classifier():
    with tempfile.TemporaryDirectory() as directory:
        client = create_app({"TESTING": True, "UPLOAD_FOLDER": directory}).test_client()
        for color in ("black", "white", "green"):
            stream = io.BytesIO()
            Image.new("RGB", (256, 256), color).save(stream, format="PNG")
            stream.seek(0)
            with patch("model.predict.predict_detailed") as inference:
                response = client.post("/api/disease/predict", data={"image": (stream, "leaf.png")})
            assert response.status_code == 200
            assert response.json["status"] == "RETAKE_REQUIRED"
            assert response.json["result"] is None
            assert response.json["photo_quality"]["next_steps"]
            inference.assert_not_called()
            assert list(Path(directory).iterdir()) == []


def test_quality_rules_do_not_claim_nonplant_detection():
    from PIL import ImageDraw
    image = Image.new("RGB", (256, 256), "gray")
    ImageDraw.Draw(image).rectangle((30, 30, 180, 180), fill="blue")
    result = assess_photo(image)
    assert result["status"] != "RETAKE_REQUIRED"
    assert "not a plant detector" in result["limitation"]
    assert assess_photo(image.resize((100, 100)))["status"] == "RETAKE_REQUIRED"


def test_selected_crop_mismatch_withholds_disease_guidance():
    with tempfile.TemporaryDirectory() as directory:
        client = create_app({"TESTING": True, "UPLOAD_FOLDER": directory}).test_client()
        with patch("model.predict.predict_detailed", return_value=diagnostics()):
            response = client.post("/api/disease/predict", data={"image": (image_bytes(), "leaf.png"), "crop": "Apple"})
        result = response.json["result"]
        assert result["assessment"]["state"] == "CROP_MISMATCH"
        assert result["severity"] == "unknown"
        assert result["symptoms"] == []
        assert "Photograph" in result["recommendations"][0]
        assert result["raw_label"] == "Tomato___Early_blight"  # raw inference is never relabelled


def test_inconclusive_explanation_and_chat_never_call_llm_for_treatment():
    assistant = FarmerAssistant(api_key="test")
    assistant._client = MagicMock()
    for label in ("Tomato___Early_blight", "Tomato___healthy"):
        context = assistant.build_context(label, 0.4)
        assert context["core_detection"]["predicted_class"] is None
        for text in (assistant.explain(context), assistant.chat("Which chemical should I use?", context)):
            assert "cannot be determined" in text
            assert "Photograph" in text
            assert "looks healthy" not in text
    assistant._client.models.generate_content.assert_not_called()


def test_unknown_or_nonfinite_confidence_is_inconclusive():
    for confidence in (None, float("nan"), float("inf"), -0.1, 1.1, True):
        assert diagnosis_assessment(confidence)["withheld"] is True
    assert diagnosis_assessment(0.75)["state"] == "SUGGESTION"


def test_weather_context_retains_simulation_label_in_assistant():
    assistant = FarmerAssistant(api_key=None)
    assistant._client = None
    weather = {"status": "SIMULATED", "source": "Test fixture", "advisory_actions": ["Scout foliage."]}
    context = assistant.build_context("Tomato___Early_blight", 0.91, weather=weather)
    assert context["weather_bonus_C"] == weather
    assert "Simulated weather example" in assistant.explain(context)
    assert "Simulated weather example" in assistant.chat("What about rain?", context)
