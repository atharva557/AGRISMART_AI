# Shared input contract for bonus modules A–D

Version: `0.1.0` — implemented integration contract, established 2026-09-12.

This specifies the interfaces implemented by Flask bonus modules A-D. Example numbers are simulated, and fixed timestamps are replay/test fixtures rather than live data. Do not interpret schema completeness or a successful response as proof of agricultural validity.

## Common request envelope

| Field | Definition |
| --- | --- |
| `contract_version` | Exactly `0.1.0`. Reject unsupported versions. |
| `request_id` | Client-generated non-empty identifier for tracing a request. |
| `module` | `A`, `B`, `C`, or `D`, matching the endpoint. |
| `as_of_utc` | Decision/reference instant, ISO 8601 with `Z` or explicit UTC offset. Runtime freshness uses server time; historical reference times are allowed only in an explicit experiment/replay. |
| `purpose` | `farm_advisory`, `simulation`, or `dataset_benchmark`. A benchmark is not a farm recommendation. |
| `farm` | `field_id`, `location` with decimal WGS84 `latitude` [-90,90] and `longitude` [-180,180], IANA `timezone`, and `area_ha` >0 when relevant. Use anonymous field IDs. Do not infer cultivated area from a map point. |
| `crop_context` | Known `crop`, `growth_stage`, and `stage_observed_at_utc`; include variety and planting date if available. A may instead have `candidate_crops` and planned planting dates. Unknown stage stays null. |
| `inputs` | Module-specific fields described below. |

All numbers must be finite JSON numbers; booleans are not measurements. Never substitute zero for unknown data. Reject unknown fields and unexpected units with explicit field paths. Missing agricultural evidence yields `NEEDS_DATA`, not a guessed recommendation.

`farm` and `crop_context` may be null for dataset benchmarks. C needs location but may omit crop context for generic weather. A needs planned candidates rather than an already planted crop. For B, recognized `sensor_percent` may be submitted to explain missing calibration, but cannot enter a VWC calculation; return `NEEDS_DATA`. Other unexpected units are invalid. Current draft examples illustrate shape and business rules; a machine validator is still to be implemented.

### Measurement object

Use `{value, unit, evidence}` for quantities. `evidence` contains:

- `kind`: `observed`, `forecast`, `reference`, `assumed`, or `dataset_record`.
- `source`: instrument, laboratory report, provider, reference URL, or dataset identifier.
- `method`: sampling, laboratory extraction, sensor calibration, aggregation method, or calculation.
- `observed_at_utc`: measurement instant, or null when the quantity describes a period.
- `period_start_utc` / `period_end_utc`: ordered period bounds for aggregates; null for instantaneous readings. Intervals use `(start, end]` for weather accumulations.
- `reference_id`: local evidence record, calibration ID, or published reference; null means supporting evidence is absent.

Observed data requires an observation time or explicit period. Forecast data requires the provider and forecast provenance described in C. Reference values need applicability to crop, stage, soil, and location. Assumptions remain visible in every derived output. Recording a reference ID does not authenticate it: the service must resolve approved references or return an unresolved-evidence status.

### Canonical units and prohibited conversions

| Quantity | Canonical unit | Constraint |
| --- | --- | --- |
| Temperature | `degC` | Convert an explicitly labeled Fahrenheit input in an adapter; never guess. |
| Relative humidity / precipitation probability | `%` | [0,100]; probability is not certainty or a confidence score for the entire day. |
| Rainfall / ET0 / irrigation depth | `mm` | Non-negative, with explicit period and aggregation. |
| Wind speed | `km/h` | Non-negative; preserve measurement height (normally 10 m in C). |
| Volumetric soil water content | `m3/m3` | [0,1], with soil-specific calibration and sampled depth. A raw sensor percentage cannot be converted by division by 100 alone. |
| Root depth / sensor depth | `m` | Positive root depth; non-negative depth bounds. |
| Irrigation water / cultivated area | `m3` / `ha` | Non-negative water, positive area. 1 mm over 1 ha = 10 m3; volume needs applicable wetted area. |
| Energy / nutrient input / harvest | `kWh` / `kg_N` / `kg` | Resource totals over a completed comparable production cycle. |
| Soil nutrients | Method-dependent | Preserve `mg/kg`, `kg/ha`, or a publisher's unresolved source scale distinctly. No automatic conversion across units, extraction methods, P vs P2O5, or K vs K2O. |
| pH | `pH` | [0,14]; record laboratory method such as extractant and soil:solution ratio. |

## A — Crop recommendation

Endpoint: `POST /api/crops/recommend`.

### Dataset benchmark mode (current trained model)

`purpose=dataset_benchmark`; `inputs.mode=source_dataset_classifier`. Require `dataset_id`, `dataset_version`, `dataset_sha256`, `row_id` (zero-based original CSV data row), and `features` in the artifact's order: N, P, K, temperature, humidity, ph, rainfall. The adapter verifies the dataset identity and row values locally; a caller-supplied compatibility boolean is insufficient. This path returns source-dataset crop candidates, never field suitability.

The model's source N/P/K have unresolved physical units. Rainfall has mm as its unit but an unresolved aggregation period; temperature and humidity also lack a documented aggregation basis. Store this uncertainty in model metadata, not as an invented daily or seasonal definition. Exact source rows are sufficient for a demonstration; arbitrary farm readings are not.

### Farm suitability mode (data gaps must be resolved first)

`inputs.mode=field_suitability`. Require independently defined candidate profiles or a model whose input definitions match the field measurements. Inputs include soil nutrient and pH measurement objects; a climate summary with explicit period, temperature/humidity aggregation, and rainfall total; planned growing period; candidate crops; soil texture/drainage; and water availability with its period. Market, yield, and rotation claims require additional evidence.

The current classifier has **no approved farm-input mapping**. Return `UNSUPPORTED_CONTEXT` for a structurally complete farm request until provenance and independent suitability validation exist. Return `NEEDS_DATA` when required inputs are absent. Do not fabricate compatibility by choosing a rainfall period that produces desirable predictions.

Response payload: ranked `candidates` with `crop`, `model_score` (uncalibrated), supporting reasons, constraints, and applicability scope. Store predicted label agreement separately from suitability, yield, or profit. Source-dataset scores are not farmer success probabilities.

## B — Irrigation

Endpoint: `POST /api/irrigation/advise`.

### Soil-water-balance advice

`inputs.mode=soil_water_balance`. Require:

| Input | Required evidence / validation |
| --- | --- |
| `soil_moisture` | VWC measurement, timestamp, sensor ID, calibration reference, upper/lower sensing depths, and method for representing the root zone. A point reading does not automatically represent the entire root zone. |
| `soil_profile.field_capacity`, `wilting_point` | Same VWC basis and applicable soil/layer definition; 0 <= WP < FC <= 1. |
| `root_depth` | Crop/stage-specific reference or measurement. Do not use maximum mature rooting depth for seedlings. |
| `allowable_depletion_fraction` | 0 < p < 1, with crop/stage applicability and reference. |
| `crop_coefficient` | Positive Kc with stage/reference for ETc approximation; disclose the assumptions. |
| `weather` | C's hourly ET0 and precipitation, complete interval coverage aligned to the decision time, and source/freshness metadata. No double counting measured and forecast rainfall. |
| `recent_water_events` | Recorded irrigation/rain events since the moisture measurement, or an explicit statement that none occurred; unknown events require remeasurement or state reconstruction. |
| `application_efficiency` | (0,1], system-specific evidence; required for gross depth/volume. |
| `target_area_ha` | Positive applicable irrigation area, required for volume; cannot exceed field area. |

Demonstration freshness policy: moisture <=2 hours old, forecast acquisition <=6 hours old, and no future observation timestamps. These are configurable project policies, not universal agronomic constants. Reference soil/stage values need applicable evidence rather than arbitrary timestamp expiry. Unsupported calibration, salinity, drainage, layered soil, or root-zone assumptions must be disclosed and can block quantitative dosing.

The intended explanation uses TAW=1000(FC-WP)×root_depth and RAW=p×TAW, with units and applicability as described in [FAO-56 chapter 8](https://www.fao.org/4/X0490E/x0490e0e.htm). These equations do not validate a sensor or determine local coefficients. A full implementation must account for timing, effective rainfall, storage capacity, runoff/drainage, and relevant boundary conditions.

Response payload: `action`, `reasons`, `recheck_at_utc`, estimated `net_depth_mm` and `gross_depth_mm`, and `volume_m3` only when enough evidence exists. Missing efficiency can withhold gross depth/volume while preserving justified soil-status information. Advice never actuates a pump automatically.

### Controller-behavior experiment (current trained model)

`purpose=dataset_benchmark`; `inputs.mode=controller_behavior_experiment`. Use the pinned Mendeley source and a decision timestamp. Build the seven causal features from the original series, with fresh closed-valve status and historical coverage; do not accept a caller's fabricated feature vector as a field input. Future valve readings are labels during evaluation only.

Output is `predicted_observed_valve_start_within_60_min` with an uncalibrated score and the model's saved decision threshold. It is not the watering action from the soil-water-balance path. The trained sensor scale is not portable to another sensor or farm without evidence.

## C — Weather

Endpoint: `POST /api/weather/advise`.

Request inputs: `mode=forecast_advisory`, requested horizon in hours, and common location. Crop/stage is required for crop-specific alerts; generic conditions may be returned with `scope=generic_weather` when it is absent.

For offline presentations, `mode=demo_forecast` is accepted only with `purpose=simulation`. It produces a deterministic, explicitly simulated weather window and never presents itself as provider data. A live provider failure never silently switches to this mode.

The backend obtains the forecast; do not trust a browser-provided cache age. Every internal forecast object carries `provider`, `fetched_at_utc`, `provider_run_time_utc` (nullable), requested coordinates, returned grid coordinates, units, and hourly interval start/end. Record acquisition time separately from model initialization. Validate contiguous coverage and values before computing totals. Do not extrapolate a partial hour without an explicit policy.

The current notebook reports the next 24 complete hourly intervals, which can begin after the request instant. Preserve that exact `valid_from_utc` and `valid_to_utc`; do not label it as precisely the next 24 hours from now. A B adapter must align the horizon before using these data. ET0 is reference evapotranspiration, not measured crop consumption. Do not multiply forecast precipitation by its probability by default.

Reject stale/missing data or return `DATA_UNAVAILABLE`; never silently fall back to simulation. Rules include observed value, units, threshold, source or assumption ID, crop applicability, and validity. No threshold firing means no configured alert, not proof of safe conditions.

## D — Sustainability comparison

Endpoint: `POST /api/sustainability/score`.

Request inputs: `mode=resource_comparison`, `baseline`, `current`, and `comparison_evidence`. Both records contain crop/location, `basis=whole_crop_cycle`, period bounds, positive area, harvest kg, water m3, electricity kWh, nitrogen nutrient kg_N, and evidence/accounting scope for every total. Resource baselines and baseline harvest must be positive for the present formula. Current harvest/resources can be zero.

Record keys are `crop`, `location`, `basis`, `data_kind`, `area_ha`, `period_start_utc`, `period_end_utc`, and measurement objects named `water`, `electricity`, `nitrogen`, and `harvest`. Each total carries `accounting_scope`. An adapter maps these to notebook 11's flat numeric fields after validation; do not pass nested objects straight into that function.

Only completed measured cycles may produce a measured-input comparison. Use the same crop, comparable duration and growing conditions, matched accounting scopes, and consistent organic/mineral nitrogen coverage. Do not hide diesel pumping by reporting only lower electricity. Normalize by area, then apply the documented version-1 formula and 95% yield-retention check. These checks support comparability; they do not remove all confounding.

`comparison_evidence` explains how the baseline was chosen and references supporting records. A checkbox alone cannot establish comparability. Simulation and measurement cannot be mixed to claim measured savings. Forecasts, proposed irrigation quantities, probabilities, and A/B model scores cannot become resource totals.

Response payload: component intensities and differences, weights, raw/final score, yield check, formula version, evidence references, and limitations. 50 means baseline parity. No automatic kg-CO2e conversion. Lower recorded resource inputs do not prove software-caused savings or overall sustainability.

## Common response contract and errors

All responses carry `contract_version`, `request_id`, `module`, `generated_at_utc`, `status`, `scope`, `data_kind`, `result`, `reasons`, `missing_inputs`, `sources`, and `limitations`. Add model/formula/rule version and forecast validity when applicable. For withheld results, `result=null`; each reason includes a stable code and JSON field path. Never return a fabricated score of zero for a missing result.

| Status | Intended meaning | Proposed HTTP |
| --- | --- | --- |
| `OK` | Supported output with stated limitations | 200 |
| `EXPERIMENTAL` | Source-dataset prediction only | 200 |
| `SIMULATED` | Assumed/demo inputs; output must remain labeled | 200 |
| `NEEDS_DATA` | Required measurements, metadata, or evidence absent | 422 |
| `INVALID_INPUT` | Wrong type, range, ordering, unit, or incompatible fields | 422 |
| `UNSUPPORTED_CONTEXT` | Well-formed request outside model/reference applicability | 422 |
| `STALE_DATA` | Outdated observations or forecast | 422 |
| `DATA_UNAVAILABLE` | Provider failure or missing forecast coverage | 503 |

A-D use the HTTP mappings above. The mandatory disease endpoint and bonus E remain HTTP 501 placeholders. Authentication and production API limits are separate work.

## Cross-module rules and acceptance cases

1. A rainfall period must match A's model/profile definition. C's daily forecast cannot silently fill it.
2. B source sensor percentage and calibrated VWC are separate representations; no implicit conversion.
3. B observed-controller prediction is separate from agronomic advice; no prediction-to-pump link.
4. D accepts documented totals, not B's proposed volumes or C's rainfall estimates as measured savings.
5. Every simulated input remains simulated in the result and exports.
6. Missing evidence returns its field path and a concrete next action, not a default coefficient.
7. Fixed example dates support replay only. Real-time requests check server time and require fresh evidence.
8. Neither JSON structure nor a supplied reference ID proves a farm is represented by training data.

Example requests and expected eligibility outcomes are in `docs/examples/bonus_contract_examples.json`. They are design fixtures; they do not invoke or demonstrate a working endpoint. Build service validators and adapters against these cases before frontend integration.
