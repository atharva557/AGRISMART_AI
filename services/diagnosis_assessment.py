"""Shared uncertainty policy for farmer-facing results and explanations."""
import math
from .photo_quality import RETAKE_STEPS

CONFIDENCE_THRESHOLD = 0.75


def diagnosis_assessment(confidence, *, crop_mismatch=False):
    valid = (isinstance(confidence, (int, float)) and not isinstance(confidence, bool)
             and math.isfinite(confidence) and 0 <= confidence <= 1)
    withheld = crop_mismatch or not valid or confidence < CONFIDENCE_THRESHOLD
    return {
        "state": "CROP_MISMATCH" if crop_mismatch else "INCONCLUSIVE" if withheld else "SUGGESTION",
        "withheld": withheld,
        "message": ("The predicted crop differs from the crop you selected. Check the crop and retake the photo."
                    if crop_mismatch else "A disease cannot be determined reliably from this photo."
                    if withheld else "Possible match. A model score is not a confirmed field diagnosis."),
        "next_steps": list(RETAKE_STEPS) if withheld else [
            "Compare the leaf with the listed symptoms and inspect nearby plants.",
            "Confirm the cause with a local agricultural extension officer before choosing a treatment.",
        ],
        "confidence_meaning": "Uncalibrated model score; it is not the probability that a diagnosis is correct.",
    }
