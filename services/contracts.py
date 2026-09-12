"""Shared response and validation helpers for bonus modules A-D."""

from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any


CONTRACT_VERSION = "0.1.0"

HTTP_STATUS_BY_RESULT = {
    "OK": 200,
    "EXPERIMENTAL": 200,
    "SIMULATED": 200,
    "NEEDS_DATA": 422,
    "INVALID_INPUT": 422,
    "UNSUPPORTED_CONTEXT": 422,
    "STALE_DATA": 422,
    "DATA_UNAVAILABLE": 503,
}


def generated_at_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def finite_number(value: Any, field: str, *, minimum=None, maximum=None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field}: must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field}: must be finite")
    if minimum is not None and number < minimum:
        raise ValueError(f"{field}: must be at least {minimum}")
    if maximum is not None and number > maximum:
        raise ValueError(f"{field}: must be at most {maximum}")
    return number


def validate_envelope(payload: Any, module: str) -> list[str]:
    errors = []
    if not isinstance(payload, dict):
        return ["request body: must be a JSON object"]
    if payload.get("contract_version") != CONTRACT_VERSION:
        errors.append(f"contract_version: must be {CONTRACT_VERSION}")
    request_id = payload.get("request_id")
    if not isinstance(request_id, str) or not request_id.strip():
        errors.append("request_id: required non-empty text")
    if payload.get("module") != module:
        errors.append(f"module: must be {module}")
    if payload.get("purpose") not in {"farm_advisory", "simulation", "dataset_benchmark"}:
        errors.append("purpose: must be farm_advisory, simulation, or dataset_benchmark")
    if not isinstance(payload.get("inputs"), dict):
        errors.append("inputs: required object")
    return errors


def response(
    payload: Any,
    module: str,
    status: str,
    *,
    scope: str,
    data_kind: str,
    result: Any = None,
    reasons: list[dict[str, Any]] | None = None,
    missing_inputs: list[str] | None = None,
    sources: list[dict[str, Any]] | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    request_id = payload.get("request_id") if isinstance(payload, dict) else None
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "module": module,
        "generated_at_utc": generated_at_utc(),
        "status": status,
        "scope": scope,
        "data_kind": data_kind,
        "result": result,
        "reasons": reasons or [],
        "missing_inputs": missing_inputs or [],
        "sources": sources or [],
        "limitations": limitations or [],
    }


def failure(
    payload: Any,
    module: str,
    status: str,
    message: str,
    *,
    field: str | None = None,
    scope: str = "withheld",
    missing_inputs: list[str] | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    reason = {"code": status, "message": message}
    if field:
        reason["field"] = field
    return response(
        payload,
        module,
        status,
        scope=scope,
        data_kind="none",
        reasons=[reason],
        missing_inputs=missing_inputs,
        limitations=limitations,
    )


def http_status(result: dict[str, Any]) -> int:
    return HTTP_STATUS_BY_RESULT.get(result.get("status"), 500)
