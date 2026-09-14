"""Inference verification tests."""
from pathlib import Path
import tempfile
import unittest

from model.predict import predict_detailed


class PredictionContractTests(unittest.TestCase):
    def test_missing_image_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                predict_detailed(str(Path(directory) / "missing.jpg"))

    def test_sample_image_inference_returns_valid_prediction(self):
        sample_img = Path("notebooks/evaluation_benchmarks/test_images/01_Apple___Apple_scab.jpg")
        if sample_img.is_file():
            result = predict_detailed(str(sample_img))
            self.assertIn("label", result)
            self.assertIn("confidence", result)
            self.assertIn("crop", result)
            self.assertIn("disease", result)
            self.assertGreaterEqual(result["confidence"], 0.0)
            self.assertLessEqual(result["confidence"], 1.0)


if __name__ == "__main__":
    unittest.main()

