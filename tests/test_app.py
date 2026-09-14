"""Page and API integration checks."""
import unittest

from app import create_app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True}).test_client()

    def test_pages_and_assets_load(self):
        for path in ("/", "/disease", "/advisory", "/about"):
            with self.subTest(path=path):
                response = self.client.get(path)
                try:
                    self.assertEqual(response.status_code, 200)
                finally:
                    response.close()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "agrismart")
        # Health endpoint should also report model file availability
        self.assertIn("models", data)
        self.assertIn("cv_checkpoint_present", data["models"])
        self.assertIn("crop_model_present", data["models"])

    def test_implemented_api_validations(self):
        # Disease predict without image returns 422
        resp = self.client.post("/api/disease/predict")
        self.assertEqual(resp.status_code, 422)

        # Assistant chat without body returns 400
        resp = self.client.post("/api/assistant/chat", json={})
        self.assertEqual(resp.status_code, 400)

    def test_advisory_routes_validate_json(self):
        for path in ("crops/recommend", "irrigation/advise", "weather/advise", "sustainability/score"):
            with self.subTest(path=path):
                response = self.client.post(f"/api/{path}", data="not json", content_type="text/plain")
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json["status"], "INVALID_INPUT")


if __name__ == "__main__":
    unittest.main()

