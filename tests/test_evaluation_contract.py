"""Metric calculations and label checks only; no model training or notebooks."""
import pytest
from model.evaluate import summarize
from model.submission_check import compare_labels


def test_metric_coverage_does_not_hide_high_confidence_errors():
    report = summarize([
        {"label": "a", "predicted_label": "a", "confidence": 0.9},
        {"label": "a", "predicted_label": "b", "confidence": 0.95},
        {"label": "b", "predicted_label": "b", "confidence": 0.6},
    ], ["a", "b"])
    assert report["macro_f1"] == pytest.approx(2/3)
    assert report["confusion_matrix"] == [[1, 1], [0, 1]]
    assert report["uncertainty"]["coverage"] == pytest.approx(2/3)
    assert report["uncertainty"]["accuracy_among_accepted"] == 0.5
    assert report["uncertainty"]["incorrect_accepted"] == 1


def test_missing_classes_and_no_accepted_predictions_are_visible():
    report = summarize([{"label": "a", "predicted_label": "a", "confidence": 0.2}], ["a", "b"])
    assert report["macro_f1"] == 0.5
    assert report["classes_without_test_samples"] == ["b"]
    assert report["uncertainty"]["accuracy_among_accepted"] is None


def test_unknown_predictions_cannot_be_silently_excluded():
    with pytest.raises(ValueError, match="never silently dropped"):
        summarize([{"label": "a", "predicted_label": "other", "confidence": 0.9}], ["a"])


def test_label_audit_distinguishes_missing_classes_and_order():
    assert compare_labels(["b", "a"], ["a", "b"]) == {
        "same_label_set": True, "same_order": False, "missing_from_model": [], "extra_model_labels": []}
    assert compare_labels(["a", "extra"], ["a", "missing"])["missing_from_model"] == ["missing"]
