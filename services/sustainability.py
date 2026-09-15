"""Module D: reproducible resource-intensity comparison."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .contracts import failure, finite_number, response, validate_envelope


FORMULA_VERSION = "1.0"
WEIGHTS = {"water": 0.40, "electricity": 0.30, "nitrogen": 0.30}
UNITS = {"water": ("m3", "m3/ha"), "electricity": ("kWh", "kWh/ha"), "nitrogen": ("kg_N", "kg N/ha")}
YIELD_RETENTION_FLOOR = 0.95


def _parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field}: ISO 8601 timestamp required")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field}: invalid ISO 8601 timestamp") from exc
    if stamp.tzinfo is None:
        raise ValueError(f"{field}: timezone offset required")
    return stamp


def _record(record: Any, name: str) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise KeyError(f"inputs.{name}")
    for field in ("crop", "location", "basis", "data_kind"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f"inputs.{name}.{field}: required non-empty text")
    if record["basis"] != "whole_crop_cycle":
        raise ValueError(f"inputs.{name}.basis: must be whole_crop_cycle")
    if record["data_kind"] not in {"simulated", "measured"}:
        raise ValueError(f"inputs.{name}.data_kind: must be simulated or measured")
    area = finite_number(record.get("area_ha"), f"inputs.{name}.area_ha", minimum=0.0001)
    start = _parse_time(record.get("period_start_utc"), f"inputs.{name}.period_start_utc")
    end = _parse_time(record.get("period_end_utc"), f"inputs.{name}.period_end_utc")
    if end <= start:
        raise ValueError(f"inputs.{name}: period_end_utc must be after period_start_utc")

    parsed = {**record, "area_ha": area, "start": start, "end": end}
    required_evidence_kind = "assumed" if record["data_kind"] == "simulated" else "observed"
    for resource, (unit, _) in UNITS.items():
        measurement = record.get(resource)
        if not isinstance(measurement, dict):
            raise KeyError(f"inputs.{name}.{resource}")
        if measurement.get("unit") != unit:
            raise ValueError(f"inputs.{name}.{resource}.unit: must be {unit}")
        parsed[f"{resource}_value"] = finite_number(measurement.get("value"), f"inputs.{name}.{resource}.value", minimum=0)
        scope = measurement.get("accounting_scope")
        if not isinstance(scope, str) or not scope.strip():
            raise ValueError(f"inputs.{name}.{resource}.accounting_scope: required")
        evidence = measurement.get("evidence")
        if not isinstance(evidence, dict) or evidence.get("kind") != required_evidence_kind:
            raise ValueError(
                f"inputs.{name}.{resource}.evidence.kind: must be {required_evidence_kind} "
                f"when data_kind is {record['data_kind']}"
            )
    harvest = record.get("harvest")
    if not isinstance(harvest, dict):
        raise KeyError(f"inputs.{name}.harvest")
    if harvest.get("unit") != "kg":
        raise ValueError(f"inputs.{name}.harvest.unit: must be kg")
    parsed["harvest_value"] = finite_number(harvest.get("value"), f"inputs.{name}.harvest.value", minimum=0)
    harvest_scope = harvest.get("accounting_scope")
    if not isinstance(harvest_scope, str) or not harvest_scope.strip():
        raise ValueError(f"inputs.{name}.harvest.accounting_scope: required")
    harvest_evidence = harvest.get("evidence")
    if not isinstance(harvest_evidence, dict) or harvest_evidence.get("kind") != required_evidence_kind:
        raise ValueError(
            f"inputs.{name}.harvest.evidence.kind: must be {required_evidence_kind} "
            f"when data_kind is {record['data_kind']}"
        )
    return parsed


def calculate_score(payload):
    errors = validate_envelope(payload, "D")
    if errors:
        return failure(payload, "D", "INVALID_INPUT", "; ".join(errors))
    inputs = payload["inputs"]
    if inputs.get("mode") != "resource_comparison":
        return failure(payload, "D", "UNSUPPORTED_CONTEXT", "Only resource_comparison mode is supported.", field="inputs.mode")
    try:
        baseline = _record(inputs.get("baseline"), "baseline")
        current = _record(inputs.get("current"), "current")
    except KeyError as exc:
        return failure(payload, "D", "NEEDS_DATA", "A required comparison field is missing.", missing_inputs=[str(exc).strip("'")])
    except (ValueError, TypeError) as exc:
        return failure(payload, "D", "INVALID_INPUT", str(exc))

    comparison_evidence = inputs.get("comparison_evidence")
    if not isinstance(comparison_evidence, dict) or not isinstance(comparison_evidence.get("note"), str) or not comparison_evidence["note"].strip():
        return failure(payload, "D", "NEEDS_DATA", "Comparison evidence and a non-empty note are required.", missing_inputs=["inputs.comparison_evidence.note"])

    mismatches = []
    for field in ("crop", "location", "basis", "data_kind"):
        if baseline[field] != current[field]:
            mismatches.append(field)
    if (baseline["end"] - baseline["start"]) != (current["end"] - current["start"]):
        mismatches.append("production_cycle_duration")
    for resource in UNITS:
        if baseline[resource]["accounting_scope"] != current[resource]["accounting_scope"]:
            mismatches.append(f"{resource}.accounting_scope")
    if mismatches:
        return failure(
            payload,
            "D",
            "UNSUPPORTED_CONTEXT",
            f"The comparison is not like-for-like: {', '.join(mismatches)}.",
            field="inputs.comparison_evidence",
        )
    expected_comparison_kind = "assumed" if baseline["data_kind"] == "simulated" else "observed"
    if comparison_evidence.get("kind") != expected_comparison_kind:
        return failure(
            payload,
            "D",
            "UNSUPPORTED_CONTEXT",
            f"comparison_evidence.kind must be {expected_comparison_kind} for {baseline['data_kind']} records.",
            field="inputs.comparison_evidence.kind",
        )
    if baseline["harvest_value"] <= 0:
        return failure(payload, "D", "NEEDS_DATA", "Positive baseline harvest is required.", missing_inputs=["inputs.baseline.harvest.value"])
    zero_baselines = [resource for resource in UNITS if baseline[f"{resource}_value"] <= 0]
    if zero_baselines:
        return failure(
            payload,
            "D",
            "NEEDS_DATA",
            "Every baseline resource must be positive for the published formula.",
            missing_inputs=[f"inputs.baseline.{name}.value" for name in zero_baselines],
        )

    components = []
    for resource, weight in WEIGHTS.items():
        baseline_intensity = baseline[f"{resource}_value"] / baseline["area_ha"]
        current_intensity = current[f"{resource}_value"] / current["area_ha"]
        reduction = (baseline_intensity - current_intensity) / baseline_intensity
        component_score = min(100.0, max(0.0, 50.0 + 50.0 * reduction))
        components.append({
            "component": resource,
            "unit": UNITS[resource][1],
            "baseline_per_ha": round(baseline_intensity, 6),
            "current_per_ha": round(current_intensity, 6),
            "difference_per_ha": round(baseline_intensity - current_intensity, 6),
            "relative_reduction_pct": round(100.0 * reduction, 6),
            "component_score": round(component_score, 6),
            "weight": weight,
            "weighted_points": round(component_score * weight, 6),
        })
    raw_score = sum(component["weighted_points"] for component in components)
    baseline_yield = baseline["harvest_value"] / baseline["area_ha"]
    current_yield = current["harvest_value"] / current["area_ha"]
    yield_retention = current_yield / baseline_yield
    yield_gate = yield_retention < YIELD_RETENTION_FLOOR
    final_score = min(raw_score, 50.0) if yield_gate else raw_score
    simulated = baseline["data_kind"] == "simulated"

    warnings = [
        "This is an indicative resource-use comparison, not a complete sustainability assessment.",
        "Resource differences do not establish savings caused by this software.",
    ]
    if yield_gate:
        warnings.append("Yield per hectare fell below 95% of baseline; the score was capped at 50.")
    return response(
        payload,
        "D",
        "SIMULATED" if simulated else "OK",
        scope="whole_crop_cycle_resource_comparison",
        data_kind="simulated" if simulated else "measured_input_comparison",
        result={
            "formula_version": FORMULA_VERSION,
            "score": round(final_score, 6),
            "raw_score": round(raw_score, 6),
            "yield_gate_applied": yield_gate,
            "yield_retention_ratio": round(yield_retention, 6),
            "baseline_yield_kg_ha": round(baseline_yield, 6),
            "current_yield_kg_ha": round(current_yield, 6),
            "components": components,
            "weights": WEIGHTS,
            "comparison_note": comparison_evidence["note"],
            "formula": {
                "intensity": "resource total / cultivated area",
                "component": "clip(50 + 50 * relative reduction, 0, 100)",
                "final": "weighted component sum, capped at 50 if yield retention is below 0.95",
            },
            "warnings": warnings,
        },
        reasons=[{"code": "FORMULA_APPLIED", "message": "The published version-1 formula was applied to like-for-like records."}],
        sources=[{"title": "Project sustainability formula", "reference": "notebooks/advisory_models/05_sustainability_score.ipynb"}],
        limitations=warnings,
    )
