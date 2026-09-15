"""Functional checks for bonus modules A-D without running notebooks or training."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import unittest

from services.crop_recommendation import MODEL_PATH, recommend_crops
from services.irrigation import advise_irrigation
from services.sustainability import calculate_score
from services.weather import EXPECTED_UNITS, VARIABLES, get_weather_advice


ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "tests" / "fixtures" / "bonus_contract_examples.json").read_text(encoding="utf-8"))["cases"]
CASE_BY_NAME = {case["name"]: case["request"] for case in CASES}


def measurement(value, unit, kind="assumed"):
    return {
        "value": value,
        "unit": unit,
        "evidence": {
            "kind": kind,
            "source": "Automated test fixture",
            "method": "Deterministic test value",
            "observed_at_utc": "2026-09-12T00:00:00Z",
            "period_start_utc": None,
            "period_end_utc": None,
            "reference_id": "test-reference",
        },
    }


class BonusServiceTests(unittest.TestCase):
    @unittest.skipUnless(MODEL_PATH.is_file(), "Local crop model artifact is not installed")
    def test_a_returns_ranked_experimental_candidates(self):
        payload = deepcopy(CASE_BY_NAME["A verified source row"])
        payload["inputs"].pop("row_id", None)
        result = recommend_crops(payload)
        self.assertEqual(result["status"], "EXPERIMENTAL")
        self.assertEqual(len(result["result"]["candidates"]), 3)
        self.assertGreaterEqual(result["result"]["candidates"][0]["model_score"], result["result"]["candidates"][1]["model_score"])

    def test_b_rejects_uncalibrated_sensor_percentage(self):
        result = advise_irrigation(deepcopy(CASE_BY_NAME["B raw sensor with missing evidence"]))
        self.assertEqual(result["status"], "NEEDS_DATA")
        self.assertIn("inputs.soil_moisture.calibration_reference", result["missing_inputs"])

    def test_b_calculates_a_simulated_water_balance(self):
        payload = {
            "contract_version": "0.1.0",
            "request_id": "test-B-valid",
            "module": "B",
            "purpose": "simulation",
            "as_of_utc": "2026-09-12T00:00:00Z",
            "farm": {"field_id": "test", "area_ha": 1.0},
            "crop_context": {"crop": "tomato", "growth_stage": "vegetative"},
            "inputs": {
                "mode": "soil_water_balance",
                "soil_moisture": {**measurement(0.20, "m3/m3"), "calibration_reference": "test-calibration"},
                "soil_profile": {
                    "field_capacity": measurement(0.30, "m3/m3"),
                    "wilting_point": measurement(0.14, "m3/m3"),
                },
                "root_depth": measurement(0.30, "m"),
                "allowable_depletion_fraction": measurement(0.40, "fraction"),
                "crop_coefficient": measurement(0.80, "fraction"),
                "weather": {
                    "et0_24h": measurement(5.0, "mm", "forecast"),
                    "precipitation_24h": measurement(0.0, "mm", "forecast"),
                },
                "recent_water_events": {"effective_water_mm": measurement(0.0, "mm")},
                "application_efficiency": measurement(0.80, "fraction"),
                "target_area_ha": 1.0,
            },
        }
        result = advise_irrigation(payload)
        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(result["result"]["action"], "IRRIGATE")
        self.assertGreater(result["result"]["volume_m3"], 0)

    def test_c_applies_rules_to_complete_provider_data(self):
        now = datetime(2026, 9, 12, 0, 20, tzinfo=timezone.utc)
        first = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        times = [(first + timedelta(hours=index)).strftime("%Y-%m-%dT%H:%M") for index in range(48)]
        hourly = {"time": times}
        hourly.update({name: [0.0] * 48 for name in VARIABLES})
        hourly["temperature_2m"] = [36.0] * 48
        hourly["relative_humidity_2m"] = [60.0] * 48
        hourly["precipitation_probability"] = [10.0] * 48
        hourly["wind_speed_10m"] = [10.0] * 48
        hourly["et0_fao_evapotranspiration"] = [0.1] * 48
        envelope = {
            "source": "test provider",
            "request": {"latitude": 18.5204, "longitude": 73.8567},
            "fetched_at_utc": now.isoformat(),
            "cache_used": False,
            "payload": {
                "utc_offset_seconds": 0,
                "hourly_units": EXPECTED_UNITS,
                "hourly": hourly,
                "latitude": 18.5,
                "longitude": 73.9,
            },
        }
        payload = deepcopy(CASE_BY_NAME["C generic forecast request"])
        result = get_weather_advice(payload, forecast_envelope=envelope, now=now)
        self.assertEqual(result["status"], "OK")
        self.assertIn("HEAT_CHECK", {alert["flag"] for alert in result["result"]["alerts"]})

    def test_c_explicit_demo_never_claims_live_data(self):
        payload = deepcopy(CASE_BY_NAME["C generic forecast request"])
        payload["purpose"] = "simulation"
        payload["inputs"]["mode"] = "demo_forecast"
        result = get_weather_advice(payload, now=datetime(2026, 9, 12, 0, 20, tzinfo=timezone.utc))
        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(result["data_kind"], "simulated")
        self.assertIn("deterministic simulation", result["limitations"][0])

    def test_d_reproduces_documented_simulation_score(self):
        result = calculate_score(deepcopy(CASE_BY_NAME["D assumed resource comparison"]))
        self.assertEqual(result["status"], "SIMULATED")
        self.assertAlmostEqual(result["result"]["score"], 57.75)


if __name__ == "__main__":
    unittest.main()
