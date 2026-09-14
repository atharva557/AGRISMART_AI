"""Model loading and caching manager for AgriSmart AI."""
import gzip
import io
import json
import logging
import os
import pickle
from threading import RLock
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import torch
import torch.nn as nn
from torchvision import models
import timm

logger = logging.getLogger(__name__)

CLASSES_PATH = Path(__file__).with_name("classes.json")
BASE_DIR = Path(__file__).resolve().parents[1]

# Checkpoint paths (Canonical location: model/weights/cv/)
PRIMARY_CHECKPOINT = BASE_DIR / "model" / "weights" / "cv" / "model_v3.pkl"
FALLBACK_CHECKPOINT = BASE_DIR / "model" / "weights" / "cv" / "model_v1.pkl"
ALT_PRIMARY = BASE_DIR / "model" / "weights" / "model_v3.pkl"
ALT_FALLBACK = BASE_DIR / "model" / "weights" / "model_v1.pkl"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# In-memory singleton cache
_CACHED_MODEL = None
_CACHED_BUNDLE: Optional[Dict[str, Any]] = None
_ACTIVE_VERSION: Optional[str] = None
_MODEL_LOCK = RLock()


class CPU_Unpickler(pickle.Unpickler):
    """Custom unpickler that safely redirects CUDA tensor storage to CPU."""
    def find_class(self, module, name):
        if module == "torch.storage" and name == "_load_from_bytes":
            return lambda b: torch.load(io.BytesIO(b), map_location="cpu", weights_only=False)
        return super().find_class(module, name)


def load_classes(path=CLASSES_PATH):
    """Load and validate the official class labels list."""
    classes = json.loads(Path(path).read_text(encoding="utf-8"))
    if not classes:
        raise NotImplementedError("Official class labels have not been added yet.")
    if not isinstance(classes, list) or not all(isinstance(label, str) for label in classes):
        raise ValueError("classes.json must contain an ordered list of class-label strings.")
    if len(classes) != len(set(classes)):
        raise ValueError("Class labels must be unique.")
    return classes


def _find_checkpoint(base_path: Path) -> Optional[Path]:
    """Find a checkpoint trying compressed .pkl.gz first, then standard .pkl."""
    gz_path = base_path.with_name(f"{base_path.name}.gz") if not str(base_path).endswith(".gz") else base_path
    if gz_path.exists():
        return gz_path
    if base_path.exists():
        return base_path
    return None


def _load_model_from_bundle(pkl_path: Path) -> Tuple[nn.Module, Dict[str, Any]]:
    """Instantiate the PyTorch architecture and load state dict from (possibly compressed) bundle."""
    open_fn = gzip.open if str(pkl_path).endswith(".gz") else open
    with open_fn(pkl_path, "rb") as f:
        if torch.cuda.is_available():
            try:
                bundle = pickle.load(f)
            except Exception:
                f.seek(0)
                bundle = CPU_Unpickler(f).load()
        else:
            bundle = CPU_Unpickler(f).load()

    arch = bundle["architecture"].lower()
    num_classes = bundle.get("num_classes", len(bundle.get("class_names", [])))

    if "convnext_tiny" in arch:
        model = timm.create_model(
            "convnext_tiny.fb_in22k_ft_in1k_384",
            pretrained=False,
            num_classes=num_classes
        )
    elif "resnet50" in arch:
        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif "resnet18" in arch:
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    else:
        raise ValueError(f"Unsupported model architecture in checkpoint: {arch}")

    # Handle float16 weights by casting to model's default parameter dtype
    state_dict = bundle["state_dict"]
    target_dtype = next(model.parameters()).dtype
    converted_state_dict = {
        k: v.to(dtype=target_dtype) if isinstance(v, torch.Tensor) and v.is_floating_point() else v
        for k, v in state_dict.items()
    }
    model.load_state_dict(converted_state_dict)
    model = model.to(DEVICE)
    model.eval()
    bundle["_checkpoint_path"] = str(pkl_path.resolve())
    return model, bundle


def get_model(force_reload: bool = False) -> Tuple[nn.Module, Dict[str, Any], str]:
    """Reuse one model per process and serialize concurrent initial loads."""
    with _MODEL_LOCK:
        return _get_model_locked(force_reload)


def _get_model_locked(force_reload: bool = False) -> Tuple[nn.Module, Dict[str, Any], str]:
    """
    Get the cached neural network model and metadata bundle.
    Tries primary v3 (ConvNeXt-Tiny) first, then falls back to v1 (ResNet-18).
    Supports transparent on-the-fly decompression of .pkl.gz archives.
    """
    global _CACHED_MODEL, _CACHED_BUNDLE, _ACTIVE_VERSION

    if _CACHED_MODEL is not None and not force_reload:
        return _CACHED_MODEL, _CACHED_BUNDLE, _ACTIVE_VERSION

    # Try Primary Checkpoint (v3)
    target_v3 = _find_checkpoint(PRIMARY_CHECKPOINT) or _find_checkpoint(ALT_PRIMARY)
    if target_v3:
        try:
            logger.info(f"Loading primary model (v3 ConvNeXt-Tiny) from {target_v3}")
            model, bundle = _load_model_from_bundle(target_v3)
            _CACHED_MODEL = model
            _CACHED_BUNDLE = bundle
            _ACTIVE_VERSION = "v3 (ConvNeXt-Tiny 384px)"
            return _CACHED_MODEL, _CACHED_BUNDLE, _ACTIVE_VERSION
        except Exception as e:
            logger.warning(f"Failed loading primary model v3: {e}. Attempting fallback...")

    # Try Fallback Checkpoint (v1)
    target_v1 = _find_checkpoint(FALLBACK_CHECKPOINT) or _find_checkpoint(ALT_FALLBACK)
    if target_v1:
        try:
            logger.info(f"Loading fallback model (v1 ResNet-18) from {target_v1}")
            model, bundle = _load_model_from_bundle(target_v1)
            _CACHED_MODEL = model
            _CACHED_BUNDLE = bundle
            _ACTIVE_VERSION = "v1 (ResNet-18 224px - Fallback)"
            return _CACHED_MODEL, _CACHED_BUNDLE, _ACTIVE_VERSION
        except Exception as e:
            logger.error(f"Failed loading fallback model v1: {e}")
            raise RuntimeError(f"Could not load fallback model checkpoint: {e}") from e

    raise FileNotFoundError(
        f"No model checkpoints found. Checked primary ({PRIMARY_CHECKPOINT}) and fallback ({FALLBACK_CHECKPOINT})."
    )
