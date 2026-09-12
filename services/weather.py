"""Module C: timestamped Open-Meteo forecasts and explicit advisory rules."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .contracts import failure, finite_number, response, validate_envelope


ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "weather" / "cache"
API_URL = "https://api.open-meteo.com/v1/forecast"
SOURCE_URL = "https://open-meteo.com/en/docs"
MAX_CACHE_AGE_HOURS = 6
VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "precipitation_probability",
    "wind_speed_10m",
    "et0_fao_evapotranspiration",
]
EXPECTED_UNITS = dict(zip(VARIABLES, ["°C", "%", "mm", "%", "km/h", "mm"]))
RULES = {
    "cold_c": 5.0,
    "heat_c": 35.0,
    "rain_24h_mm": 20.0,
    "wind_kmh": 25.0,
    "humidity_pct": 85.0,
    "humidity_hours": 6,
    "high_et0_mm": 5.0,
    "low_rain_mm": 2.0,
}


def _utc(value: Any, field: str) -> datetime:
    if isinstance(value, datetime):
        stamp = value
    elif isinstance(value, str):
        try:
            stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{field}: invalid timestamp") from exc
    else:
        raise ValueError(f"{field}: timestamp required")
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc)


def _params(latitude: float, longitude: float) -> dict[str, Any]:
    return {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(VARIABLES),
        "forecast_days": 3,
        "timezone": "GMT",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }


def _fetch_forecast(latitude: float, longitude: float, now: datetime) -> dict[str, Any]:
    try:
        import requests
    except ImportError as exc:
        raise RuntimeError("Install the application requirements to fetch weather data.") from exc

    params = _params(latitude, longitude)
    cache_key = hashlib.sha256(json.dumps(params, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    cache_path = CACHE_DIR / f"{cache_key}.json"
    if cache_path.is_file():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            fetched_at = _utc(cached["fetched_at_utc"], "fetched_at_utc")
            age = (now - fetched_at).total_seconds() / 3600
            if cached.get("request") == params and 0 <= age <= MAX_CACHE_AGE_HOURS:
                cached["cache_used"] = True
                return cached
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            pass

    try:
        provider_response = requests.get(API_URL, params=params, timeout=(10, 30))
        provider_response.raise_for_status()
        payload = provider_response.json()
    except (requests.RequestException, ValueError) as exc:
        raise RuntimeError("Live forecast is unavailable; retry later.") from exc
    if payload.get("error"):
        raise RuntimeError(f"Weather provider error: {payload.get('reason', 'unknown error')}")

    envelope = {
        "source": SOURCE_URL,
        "request": params,
        "fetched_at_utc": now.isoformat(),
        "provider_run_time_utc": None,
        "cache_used": False,
        "payload": payload,
    }
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(envelope, indent=2, allow_nan=False), encoding="utf-8")
    return envelope


def _demo_forecast(latitude: float, longitude: float, now: datetime) -> dict[str, Any]:
    first_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    times = [(first_hour + timedelta(hours=index)).strftime("%Y-%m-%dT%H:%M") for index in range(48)]
    hourly = {
        "time": times,
        "temperature_2m": [29.0] * 48,
        "relative_humidity_2m": [88.0 if index < 7 else 68.0 for index in range(48)],
        "precipitation": [0.0] * 48,
        "precipitation_probability": [15.0] * 48,
        "wind_speed_10m": [12.0] * 48,
        "et0_fao_evapotranspiration": [0.24] * 48,
    }
    return {
        "source": "AgriSmart deterministic simulated weather fixture",
        "request": {"latitude": latitude, "longitude": longitude},
        "fetched_at_utc": now.isoformat(),
        "provider_run_time_utc": None,
        "cache_used": False,
        "payload": {
            "utc_offset_seconds": 0,
            "hourly_units": EXPECTED_UNITS,
            "hourly": hourly,
            "latitude": latitude,
            "longitude": longitude,
        },
    }


def _longest_run(values: list[bool]) -> int:
    best = current = 0
    for value in values:
        current = current + 1 if value else 0
        best = max(best, current)
    return best


def _analyse_forecast(envelope: dict[str, Any], now: datetime, horizon_hours: int) -> dict[str, Any]:
    fetched_at = _utc(envelope.get("fetched_at_utc"), "fetched_at_utc")
    age_hours = (now - fetched_at).total_seconds() / 3600
    if age_hours < 0:
        raise ValueError("Forecast acquisition time is in the future.")
    if age_hours > MAX_CACHE_AGE_HOURS:
        raise TimeoutError("Forecast acquisition is stale.")

    payload = envelope.get("payload")
    if not isinstance(payload, dict) or payload.get("utc_offset_seconds") != 0:
        raise ValueError("Provider payload must contain UTC forecast data.")
    units = payload.get("hourly_units")
    if not isinstance(units, dict) or any(units.get(name) != unit for name, unit in EXPECTED_UNITS.items()):
        raise ValueError("Provider returned unexpected weather units.")
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise ValueError("Provider hourly forecast is missing.")
    lengths = {len(hourly.get(name, [])) for name in ["time", *VARIABLES]}
    if len(lengths) != 1 or next(iter(lengths), 0) == 0:
        raise ValueError("Provider hourly arrays are incomplete.")

    rows = []
    for index, raw_time in enumerate(hourly["time"]):
        stamp = _utc(raw_time, "hourly.time")
        values = {name: finite_number(hourly[name][index], f"hourly.{name}") for name in VARIABLES}
        if not 0 <= values["relative_humidity_2m"] <= 100 or not 0 <= values["precipitation_probability"] <= 100:
            raise ValueError("Provider returned a percentage outside 0-100.")
        if values["precipitation"] < 0 or values["wind_speed_10m"] < 0 or values["et0_fao_evapotranspiration"] < 0:
            raise ValueError("Provider returned a negative weather quantity.")
        rows.append({"time": stamp, **values})
    times = [row["time"] for row in rows]
    if times != sorted(times) or len(times) != len(set(times)):
        raise ValueError("Provider forecast timestamps are duplicated or unordered.")

    first_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    expected = [first_hour + timedelta(hours=index) for index in range(horizon_hours)]
    row_by_time = {row["time"]: row for row in rows}
    if any(stamp not in row_by_time for stamp in expected):
        raise ValueError("A complete contiguous forecast window is unavailable.")
    window = [row_by_time[stamp] for stamp in expected]

    summary = {
        "minimum_temperature_c": min(row["temperature_2m"] for row in window),
        "maximum_temperature_c": max(row["temperature_2m"] for row in window),
        "precipitation_mm": sum(row["precipitation"] for row in window),
        "maximum_hourly_rain_probability_pct": max(row["precipitation_probability"] for row in window),
        "maximum_wind_kmh": max(row["wind_speed_10m"] for row in window),
        "et0_mm": sum(row["et0_fao_evapotranspiration"] for row in window),
        "consecutive_humid_hours": _longest_run([row["relative_humidity_2m"] >= RULES["humidity_pct"] for row in window]),
    }
    alerts = []

    def add(flag, observed, threshold, action):
        alerts.append({"flag": flag, "observed": round(float(observed), 3), "threshold": threshold, "action": action})

    if summary["minimum_temperature_c"] <= RULES["cold_c"]:
        add("COLD_CHECK", summary["minimum_temperature_c"], RULES["cold_c"], "Check local warnings and protection needs for cold-sensitive crop stages.")
    if summary["maximum_temperature_c"] >= RULES["heat_c"]:
        add("HEAT_CHECK", summary["maximum_temperature_c"], RULES["heat_c"], "Inspect plants for heat stress and check measured root-zone moisture.")
    if summary["precipitation_mm"] >= RULES["rain_24h_mm"]:
        add("RAIN_CHECK", summary["precipitation_mm"], RULES["rain_24h_mm"], "Inspect drainage and review irrigation timing against actual soil conditions.")
    if summary["maximum_wind_kmh"] >= RULES["wind_kmh"]:
        add("WIND_CHECK", summary["maximum_wind_kmh"], RULES["wind_kmh"], "Inspect plant supports and consult product-specific limits before spraying.")
    if summary["consecutive_humid_hours"] >= RULES["humidity_hours"]:
        add("HUMIDITY_SCOUTING", summary["consecutive_humid_hours"], RULES["humidity_hours"], "Scout foliage; humidity alone does not diagnose disease.")
    if summary["et0_mm"] >= RULES["high_et0_mm"] and summary["precipitation_mm"] < RULES["low_rain_mm"]:
        add("MOISTURE_CHECK", summary["et0_mm"], RULES["high_et0_mm"], "Check calibrated root-zone moisture; ET0 alone is not a watering instruction.")

    return {
        "summary": {name: round(float(value), 3) for name, value in summary.items()},
        "alerts": alerts,
        "message": "Review the flagged conditions." if alerts else "No configured threshold triggered; continue monitoring.",
        "rules": RULES,
        "fetched_at_utc": fetched_at.isoformat(),
        "valid_from_utc": expected[0].isoformat(),
        "valid_to_utc": (expected[-1] + timedelta(hours=1)).isoformat(),
        "requested_location": {key: envelope["request"][key] for key in ("latitude", "longitude")},
        "grid_location": {key: payload.get(key) for key in ("latitude", "longitude")},
        "units": EXPECTED_UNITS,
        "cache_used": bool(envelope.get("cache_used")),
        "hourly": [
            {"time_utc": row["time"].isoformat(), **{name: row[name] for name in VARIABLES}}
            for row in window
        ],
    }


def get_weather_advice(payload, *, forecast_envelope=None, now=None):
    errors = validate_envelope(payload, "C")
    if errors:
        return failure(payload, "C", "INVALID_INPUT", "; ".join(errors))
    inputs = payload["inputs"]
    mode = inputs.get("mode")
    if mode not in {"forecast_advisory", "demo_forecast"}:
        return failure(payload, "C", "UNSUPPORTED_CONTEXT", "Use forecast_advisory or the explicit demo_forecast mode.", field="inputs.mode")
    if mode == "demo_forecast" and payload.get("purpose") != "simulation":
        return failure(payload, "C", "UNSUPPORTED_CONTEXT", "demo_forecast requires purpose=simulation.", field="purpose")
    try:
        horizon_hours = int(inputs.get("horizon_hours", 24))
        if isinstance(inputs.get("horizon_hours", 24), bool) or horizon_hours != inputs.get("horizon_hours", 24) or not 1 <= horizon_hours <= 48:
            raise ValueError("inputs.horizon_hours: must be an integer from 1 to 48")
        farm = payload.get("farm")
        if not isinstance(farm, dict) or not isinstance(farm.get("location"), dict):
            return failure(payload, "C", "NEEDS_DATA", "Farm coordinates are required.", missing_inputs=["farm.location.latitude", "farm.location.longitude"])
        latitude = finite_number(farm["location"].get("latitude"), "farm.location.latitude", minimum=-90, maximum=90)
        longitude = finite_number(farm["location"].get("longitude"), "farm.location.longitude", minimum=-180, maximum=180)
        reference_time = _utc(now or datetime.now(timezone.utc), "now")
        provider_envelope = forecast_envelope
        if provider_envelope is None:
            provider_envelope = (
                _demo_forecast(latitude, longitude, reference_time)
                if mode == "demo_forecast"
                else _fetch_forecast(latitude, longitude, reference_time)
            )
        analysed = _analyse_forecast(provider_envelope, reference_time, horizon_hours)
    except TimeoutError as exc:
        return failure(payload, "C", "STALE_DATA", str(exc))
    except RuntimeError as exc:
        return failure(payload, "C", "DATA_UNAVAILABLE", str(exc))
    except (KeyError, TypeError, ValueError) as exc:
        return failure(payload, "C", "INVALID_INPUT", str(exc))

    crop_context = payload.get("crop_context")
    generic = not isinstance(crop_context, dict) or not crop_context.get("crop")
    return response(
        payload,
        "C",
        "SIMULATED" if mode == "demo_forecast" else "OK",
        scope=("simulated_weather" if mode == "demo_forecast" else ("generic_weather" if generic else "crop_context_weather")),
        data_kind="simulated" if mode == "demo_forecast" else "forecast",
        result=analysed,
        reasons=[{
            "code": "SIMULATED_RULES_APPLIED" if mode == "demo_forecast" else "FORECAST_RULES_APPLIED",
            "message": "Configured alert thresholds were evaluated over a complete future window.",
        }],
        sources=(
            [{"title": "AgriSmart simulated weather fixture", "fetched_at_utc": analysed["fetched_at_utc"]}]
            if mode == "demo_forecast"
            else [{"title": "Open-Meteo Forecast API", "url": SOURCE_URL, "fetched_at_utc": analysed["fetched_at_utc"]}]
        ),
        limitations=[
            "Values are a deterministic simulation, not a provider forecast." if mode == "demo_forecast" else "Forecast values are not field observations.",
            "Thresholds need crop- and location-specific validation.",
            "Maximum hourly precipitation probability is not a horizon-wide rain probability.",
        ],
    )
