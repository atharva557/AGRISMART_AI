"""Upload/API regression checks using mocked inference, never training."""
import io
from pathlib import Path
import tempfile
import subprocess
import sys
import textwrap
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw
from app import create_app


def image_bytes():
    buffer = io.BytesIO()
    photo = Image.new("RGB", (256, 256), "green")
    ImageDraw.Draw(photo).ellipse((30, 30, 220, 220), fill="olive")
    photo.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def diagnostics(label="Tomato___Early_blight"):
    crop, disease = label.split("___")
    return {"label": label, "crop": crop, "disease": disease.replace("_", " "),
            "confidence": 0.91, "confidence_percentage": "91.0%", "is_confident": True,
            "confidence_threshold": 0.75, "latency_ms": 1, "model_version": "test",
            "top_candidates": [{"label": label, "confidence": 0.91}]}


class DiseaseRegressionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.client = create_app({"TESTING": True, "UPLOAD_FOLDER": self.directory.name}).test_client()

    def upload(self, data=None, filename="leaf.png"):
        return self.client.post("/api/disease/predict", data={
            "image": (data if data is not None else image_bytes(), filename)
        }, content_type="multipart/form-data")

    def assert_clean(self):
        self.assertEqual(list(Path(self.directory.name).iterdir()), [])

    def test_prediction_preserves_frontend_and_assistant_contract(self):
        with patch("model.predict.predict_detailed", return_value=diagnostics()):
            response = self.upload()
        self.assertEqual(response.status_code, 200)
        result = response.json["result"]
        for field in ("raw_label", "crop", "disease", "severity", "symptoms",
                      "recommendations", "model_version", "top_candidates"):
            self.assertTrue(result[field])
        with patch("app.routes.assistant.assistant.explain", return_value="Grounded guidance"):
            explained = self.client.post("/api/assistant/explain", json={
                "disease_label": result["raw_label"], "crop": result["crop"],
                "confidence": result["confidence"], "lang": "en"})
        self.assertEqual(explained.status_code, 200)
        self.assertEqual(explained.json["context"]["core_detection"]["predicted_class"], result["raw_label"])
        self.assert_clean()

    def test_healthy_results_have_no_disease_severity(self):
        with patch("model.predict.predict_detailed", return_value=diagnostics("Tomato___healthy")):
            response = self.upload()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["result"]["severity"], "none")
        self.assert_clean()

    def test_fake_image_is_rejected_before_inference(self):
        with patch("model.predict.predict_detailed") as inference:
            response = self.upload(io.BytesIO(b"not an image"))
        self.assertEqual(response.status_code, 422)
        inference.assert_not_called()
        self.assert_clean()

    def test_unique_names_and_cleanup_on_success(self):
        paths = []
        def infer(path):
            paths.append(path)
            return diagnostics()
        with patch("model.predict.predict_detailed", side_effect=infer):
            self.assertEqual(self.upload().status_code, 200)
            self.assertEqual(self.upload().status_code, 200)
        self.assertNotEqual(paths[0], paths[1])
        self.assert_clean()

    def test_errors_are_safe_and_uploads_are_cleaned(self):
        for error, status in ((FileNotFoundError("private checkpoint path"), 503),
                              (ValueError("private internal details"), 500)):
            with self.subTest(error=type(error).__name__):
                with patch("model.predict.predict_detailed", side_effect=error):
                    response = self.upload()
                self.assertEqual(response.status_code, status)
                self.assertNotIn("private", str(response.json))
                self.assert_clean()

    def test_image_pixel_ceiling_is_enforced(self):
        with patch("app.routes.disease._MAX_IMAGE_PIXELS", 10), patch("model.predict.predict_detailed") as inference:
            response = self.upload()
        self.assertEqual(response.status_code, 422)
        inference.assert_not_called()
        self.assert_clean()

    def test_upload_size_limit(self):
        client = create_app({"TESTING": True, "MAX_CONTENT_LENGTH": 32}).test_client()
        response = client.post("/api/disease/predict", data={"image": (image_bytes(), "leaf.png")},
                               content_type="multipart/form-data")
        self.assertEqual(response.status_code, 413)

    def test_app_and_health_work_without_inference_dependencies(self):
        script = textwrap.dedent('''
            import os
            os.environ['GEMINI_API_KEY'] = ''
            os.environ['ASSISTANT_API_KEY'] = ''
            import sys
            import importlib.abc
            class BlockInference(importlib.abc.MetaPathFinder):
                def find_spec(self, fullname, path=None, target=None):
                    if fullname.split('.')[0] in {'torch', 'torchvision', 'timm'}:
                        raise ImportError('Inference dependencies unavailable for this test')
            sys.meta_path.insert(0, BlockInference())
            from app import create_app
            client = create_app({'TESTING': True}).test_client()
            assert client.get('/api/health').status_code == 200
            assert client.post('/api/disease/predict').status_code == 422
            import io
            from PIL import Image
            image = io.BytesIO()
            Image.new('RGB', (8, 8)).save(image, format='PNG')
            image.seek(0)
            response = client.post('/api/disease/predict', data={'image': (image, 'leaf.png')}, content_type='multipart/form-data')
            assert response.status_code == 503, response.json
            assert 'torch' not in sys.modules
        ''')
        result = subprocess.run([sys.executable, "-B", "-c", script],
                                cwd=Path(__file__).resolve().parents[1],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
