"""Check cache and fallback behavior without constructing or training models."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from model import model_loader as loader
import torch


class ModelCacheTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        primary = Path(directory.name) / "v3.pkl"
        fallback = Path(directory.name) / "v1.pkl"
        # Existing files are only path fixtures; deserialization is mocked.
        primary.touch()
        fallback.touch()
        for name, value in (("_CACHED_MODEL", None), ("_CACHED_BUNDLE", None),
                            ("_ACTIVE_VERSION", None), ("PRIMARY_CHECKPOINT", primary),
                            ("FALLBACK_CHECKPOINT", fallback)):
            mock = patch.object(loader, name, value)
            mock.start()
            self.addCleanup(mock.stop)

    def test_repeated_calls_reuse_model_and_bundle(self):
        model, bundle = object(), {"class_names": ["Tomato___healthy"]}
        with patch.object(loader, "_load_model_from_bundle", return_value=(model, bundle)) as load:
            first = loader.get_model()
            second = loader.get_model()
        load.assert_called_once()
        self.assertIs(first[0], second[0])
        self.assertIs(first[1], second[1])

    def test_simultaneous_first_requests_only_load_once(self):
        def slow_load(_):
            time.sleep(0.02)
            return object(), {}
        with patch.object(loader, "_load_model_from_bundle", side_effect=slow_load) as load:
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda _: loader.get_model(), range(16)))
        load.assert_called_once()
        self.assertTrue(all(result[0] is results[0][0] for result in results))

    def test_primary_failure_uses_and_caches_fallback(self):
        fallback_model = object()
        with patch.object(loader, "_load_model_from_bundle", side_effect=[ValueError("bad primary"), (fallback_model, {})]) as load:
            first = loader.get_model()
            second = loader.get_model()
        self.assertEqual(load.call_count, 2)
        self.assertIs(first[0], fallback_model)
        self.assertIs(second[0], fallback_model)
        self.assertIn("Fallback", first[2])

    def test_force_reload_refreshes_cache(self):
        with patch.object(loader, "_load_model_from_bundle", side_effect=[(object(), {}), (object(), {})]) as load:
            first = loader.get_model()
            second = loader.get_model(force_reload=True)
        self.assertEqual(load.call_count, 2)
        self.assertIsNot(first[0], second[0])

    def test_compressed_checkpoint_is_preferred_and_cached(self):
        compressed = loader.PRIMARY_CHECKPOINT.with_name(loader.PRIMARY_CHECKPOINT.name + ".gz")
        compressed.touch()
        with patch.object(loader, "_load_model_from_bundle", return_value=(object(), {})) as load:
            loader.get_model()
            loader.get_model()
        load.assert_called_once_with(compressed)

    def test_fp16_weights_are_cast_to_model_dtype(self):
        class TinyModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.fc = torch.nn.Linear(1, 2)

        original = TinyModel()
        half_weights = {key: value.half() for key, value in original.state_dict().items()}
        bundle = {"architecture": "resnet18", "num_classes": 2, "state_dict": half_weights}
        with patch.object(loader.gzip, "open"), patch.object(loader, "CPU_Unpickler") as unpickler, \
                patch.object(loader.torch.cuda, "is_available", return_value=False), \
                patch.object(loader.models, "resnet18", return_value=TinyModel()):
            unpickler.return_value.load.return_value = bundle
            model, _ = loader._load_model_from_bundle(Path("fixture.pkl.gz"))
        self.assertEqual(next(model.parameters()).dtype, torch.float32)
        self.assertFalse(model.training)
        for key, value in model.state_dict().items():
            torch.testing.assert_close(value.cpu(), half_weights[key].float())
