"""Module B: evidence-aware soil-water-balance irrigation advice."""

from __future__ import annotations

from typing import Any

from .contracts import failure, finite_number, response, validate_envelope


FAO_56_URL = "https://www.fao.org/4/X0490E/x0490e0e.htm"


def _measurement(container: dict[str, Any], name: str, unit: str, *, minimum=None, maximum=None) -> tuple[float, dict[str, Any]]:
    item = container.get(name)
    if not isinstance(item, dict):
        raise KeyError(f"inputs.{name}")
    if item.get("unit") != unit:
        raise ValueError(f"inputs.{name}.unit: must be {unit}")
    value = finite_number(item.get("value"), f"inputs.{name}.value", minimum=minimum, maximum=maximum)
    evidence = item.get("evidence")
    if not isinstance(evidence, dict) or evidence.get("kind") not in {"observed", "forecast", "reference", "assumed"}:
        raise ValueError(f"inputs.{name}.evidence: valid evidence metadata is required")
    return value, evidence


def _profile_measurement(profile: dict[str, Any], name: str) -> tuple[float, dict[str, Any]]:
    item = profile.get(name)
    if not isinstance(item, dict):
        raise KeyError(f"inputs.soil_profile.{name}")
    if item.get("unit") != "m3/m3":
        raise ValueError(f"inputs.soil_profile.{name}.unit: must be m3/m3")
    value = finite_number(item.get("value"), f"inputs.soil_profile.{name}.value", minimum=0, maximum=1)
    evidence = item.get("evidence")
    if not isinstance(evidence, dict) or evidence.get("kind") not in {"reference", "observed", "assumed"}:
        raise ValueError(f"inputs.soil_profile.{name}.evidence: valid evidence metadata is required")
    return value, evidence


def _weather_values(weather: Any) -> tuple[float, float, list[dict[str, Any]]]:
    if not isinstance(weather, dict):
        raise KeyError("inputs.weather")
    et0, et0_evidence = _measurement(weather, "et0_24h", "mm", minimum=0)
    rain, rain_evidence = _measurement(weather, "precipitation_24h", "mm", minimum=0)
    return et0, rain, [et0_evidence, rain_evidence]


def advise_irrigation(payload):
    errors = validate_envelope(payload, "B")
    if errors:
        return failure(payload, "B", "INVALID_INPUT", "; ".join(errors))
    inputs = payload["inputs"]
    if inputs.get("mode") != "soil_water_balance":
        return failure(payload, "B", "UNSUPPORTED_CONTEXT", "Only soil_water_balance advice is exposed for farm decisions.", field="inputs.mode")

    missing = []
    moisture = inputs.get("soil_moisture")
    if not isinstance(moisture, dict):
        missing.append("inputs.soil_moisture")
    else:
        if moisture.get("unit") != "m3/m3":
            missing.append("inputs.soil_moisture.calibration_reference")
        if not moisture.get("calibration_reference"):
            missing.append("inputs.soil_moisture.calibration_reference")
    for name in ("soil_profile", "root_depth", "allowable_depletion_fraction", "crop_coefficient", "weather", "recent_water_events", "application_efficiency", "target_area_ha"):
        if inputs.get(name) is None:
            missing.append(f"inputs.{name}")
    if missing:
        return failure(
            payload,
            "B",
            "NEEDS_DATA",
            "Calibrated soil, weather, recent-water, and application inputs are required.",
            missing_inputs=sorted(set(missing)),
            limitations=["Raw sensor percentages are not converted to volumetric water content."],
        )

    try:
        theta = finite_number(moisture.get("value"), "inputs.soil_moisture.value", minimum=0, maximum=1)
        moisture_evidence = moisture.get("evidence")
        if not isinstance(moisture_evidence, dict) or moisture_evidence.get("kind") not in {"observed", "assumed"}:
            raise ValueError("inputs.soil_moisture.evidence: observed or assumed evidence is required")
        profile = inputs["soil_profile"]
        if not isinstance(profile, dict):
            raise ValueError("inputs.soil_profile: must be an object")
        field_capacity, fc_evidence = _profile_measurement(profile, "field_capacity")
        wilting_point, wp_evidence = _profile_measurement(profile, "wilting_point")
        root_depth, root_evidence = _measurement(inputs, "root_depth", "m", minimum=0.01, maximum=3)
        depletion_fraction, p_evidence = _measurement(inputs, "allowable_depletion_fraction", "fraction", minimum=0.01, maximum=1)
        crop_coefficient, kc_evidence = _measurement(inputs, "crop_coefficient", "fraction", minimum=0, maximum=2.5)
        efficiency, efficiency_evidence = _measurement(inputs, "application_efficiency", "fraction", minimum=0.01, maximum=1)
        et0_mm, rain_mm, weather_evidence = _weather_values(inputs["weather"])
        recent = inputs["recent_water_events"]
        if not isinstance(recent, dict):
            raise ValueError("inputs.recent_water_events: must be an object")
        recent_water_mm, recent_evidence = _measurement(recent, "effective_water_mm", "mm", minimum=0)
        target_area_ha = finite_number(inputs["target_area_ha"], "inputs.target_area_ha", minimum=0.0001)
        farm = payload.get("farm")
        if isinstance(farm, dict) and farm.get("area_ha") is not None:
            field_area = finite_number(farm["area_ha"], "farm.area_ha", minimum=0.0001)
            if target_area_ha > field_area:
                raise ValueError("inputs.target_area_ha: cannot exceed farm.area_ha")
        if field_capacity <= wilting_point:
            raise ValueError("inputs.soil_profile: field capacity must exceed wilting point")
        if theta < wilting_point or theta > field_capacity:
            raise ValueError("inputs.soil_moisture.value: must lie between wilting point and field capacity for this model")
    except KeyError as exc:
        return failure(payload, "B", "NEEDS_DATA", "A required measurement is missing.", missing_inputs=[str(exc).strip("'")])
    except (ValueError, TypeError) as exc:
        return failure(payload, "B", "INVALID_INPUT", str(exc))

    total_available_water_mm = 1000.0 * (field_capacity - wilting_point) * root_depth
    readily_available_water_mm = depletion_fraction * total_available_water_mm
    current_depletion_mm = 1000.0 * (field_capacity - theta) * root_depth
    crop_et_mm = et0_mm * crop_coefficient
    projected_depletion_mm = max(0.0, current_depletion_mm + crop_et_mm - rain_mm - recent_water_mm)
    irrigate = projected_depletion_mm >= readily_available_water_mm
    net_depth_mm = min(projected_depletion_mm, total_available_water_mm) if irrigate else 0.0
    gross_depth_mm = net_depth_mm / efficiency if irrigate else 0.0
    volume_m3 = gross_depth_mm * target_area_ha * 10.0

    evidence_items = [
        moisture_evidence,
        fc_evidence,
        wp_evidence,
        root_evidence,
        p_evidence,
        kc_evidence,
        efficiency_evidence,
        recent_evidence,
        *weather_evidence,
    ]
    simulated = payload.get("purpose") == "simulation" or any(item.get("kind") == "assumed" for item in evidence_items)
    status = "SIMULATED" if simulated else "OK"
    action = "IRRIGATE" if irrigate else "WAIT"

    return response(
        payload,
        "B",
        status,
        scope="soil_water_balance_advisory",
        data_kind="simulated" if simulated else "evidence_backed_inputs",
        result={
            "action": action,
            "total_available_water_mm": round(total_available_water_mm, 3),
            "readily_available_water_mm": round(readily_available_water_mm, 3),
            "current_depletion_mm": round(current_depletion_mm, 3),
            "forecast_crop_et_mm": round(crop_et_mm, 3),
            "forecast_precipitation_mm": round(rain_mm, 3),
            "recent_effective_water_mm": round(recent_water_mm, 3),
            "projected_depletion_mm": round(projected_depletion_mm, 3),
            "net_depth_mm": round(net_depth_mm, 3),
            "gross_depth_mm": round(gross_depth_mm, 3),
            "volume_m3": round(volume_m3, 3),
            "target_area_ha": target_area_ha,
            "method": "FAO-56-style root-zone depletion calculation",
        },
        reasons=[{
            "code": "DEPLETION_THRESHOLD_REACHED" if irrigate else "DEPLETION_WITHIN_ALLOWANCE",
            "message": (
                "Projected depletion reaches the configured readily available water threshold."
                if irrigate
                else "Projected depletion remains below the configured readily available water threshold."
            ),
        }],
        sources=[{"title": "FAO Irrigation and Drainage Paper 56, Chapter 8", "url": FAO_56_URL}],
        limitations=[
            "The result depends on local calibration and the supplied crop/soil parameters.",
            "Forecast precipitation is not guaranteed effective rainfall.",
            "This advisory does not actuate a pump and does not demonstrate water savings.",
        ],
    )
