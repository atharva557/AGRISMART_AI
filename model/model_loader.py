"""Model loading and caching manager for AgriSmart AI."""
import json
import logging
import os
import pickle
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
LEGACY_PRIMARY = BASE_DIR / "notebooks" / "cv_model_notebooks" / "model_v3.pkl"
LEGACY_FALLBACK = BASE_DIR / "notebooks" / "cv_model_notebooks" / "model_v1.pkl"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# In-memory singleton cache
_CACHED_MODEL = None
_CACHED_BUNDLE: Optional[Dict[str, Any]] = None
_ACTIVE_VERSION: Optional[str] = None


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


def _load_model_from_bundle(pkl_path: Path) -> Tuple[nn.Module, Dict[str, Any]]:
    """Instantiate the PyTorch architecture and load state dict from bundle."""
    with open(pkl_path, "rb") as f:
        bundle = pickle.load(f)

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

    model.load_state_dict(bundle["state_dict"])
    model = model.to(DEVICE)
    model.eval()
    return model, bundle


def get_model(force_reload: bool = False) -> Tuple[nn.Module, Dict[str, Any], str]:
    """
    Get the cached neural network model and metadata bundle.
    Tries primary v3 (ConvNeXt-Tiny) first, then falls back to v1 (ResNet-18).
    """
    global _CACHED_MODEL, _CACHED_BUNDLE, _ACTIVE_VERSION

    if _CACHED_MODEL is not None and not force_reload:
        return _CACHED_MODEL, _CACHED_BUNDLE, _ACTIVE_VERSION

    # Try Primary Checkpoint (v3)
    target_v3 = PRIMARY_CHECKPOINT if PRIMARY_CHECKPOINT.exists() else ALT_PRIMARY
    if target_v3.exists():
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
    target_v1 = FALLBACK_CHECKPOINT if FALLBACK_CHECKPOINT.exists() else ALT_FALLBACK
    if target_v1.exists():
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
