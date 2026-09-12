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

    def test_unimplemented_team_modules_remain_explicit_placeholders(self):
        for path in ("disease/predict", "assistant/chat"):
            with self.subTest(path=path):
                response = self.client.post(f"/api/{path}", json={})
                self.assertEqual(response.status_code, 501)
                self.assertEqual(response.json["error"]["code"], "NOT_IMPLEMENTED")

    def test_bonus_routes_validate_json(self):
        for path in ("crops/recommend", "irrigation/advise", "weather/advise", "sustainability/score"):
            with self.subTest(path=path):
                response = self.client.post(f"/api/{path}", data="not json", content_type="text/plain")
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json["status"], "INVALID_INPUT")


if __name__ == "__main__":
    unittest.main()
