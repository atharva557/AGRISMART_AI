"""Inference contract checks while the core is being implemented."""
import tempfile
import unittest
from pathlib import Path

from model.predict import predict


class PredictionContractTests(unittest.TestCase):
    def test_missing_image_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                predict(str(Path(directory) / "missing.jpg"))

    def test_placeholder_does_not_fabricate_a_prediction(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "placeholder.jpg"
            image.write_bytes(b"test fixture, not a real image")
            with self.assertRaises(NotImplementedError):
                predict(str(image))


if __name__ == "__main__":
    unittest.main()
