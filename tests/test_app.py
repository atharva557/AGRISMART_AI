"""Page and API integration checks."""
import unittest

from app import create_app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True}).test_client()

    def test_pages_and_assets_load(self):
        for path in ("/", "/result", "/static/css/style.css", "/static/js/app.js"):
            with self.subTest(path=path):
                response = self.client.get(path)
                try:
                    self.assertEqual(response.status_code, 200)
                finally:
                    response.close()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_features_remain_explicit_placeholders(self):
        for path in ("disease/predict", "crops/recommend", "irrigation/advise",
                     "weather/advise", "sustainability/score", "assistant/chat"):
            with self.subTest(path=path):
                response = self.client.post(f"/api/{path}", json={})
                self.assertEqual(response.status_code, 501)
                self.assertEqual(response.json["error"]["code"], "NOT_IMPLEMENTED")


if __name__ == "__main__":
    unittest.main()
