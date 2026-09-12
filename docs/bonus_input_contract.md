# Shared input contract for bonus modules A–D

API version: `0.1.0`. Documentation reviewed against the Flask services on 2026-09-12.

This guide describes the **current implementation**, not a completed field-safety specification. A-D are connected to the Flask dashboard and API. Sections marked **planned** are not enforced yet. Example numbers are experiments or simulations; successful JSON validation does not authenticate measurements or establish agricultural validity.

| Module | Supported API mode | Method | Successful status |
| --- | --- | --- | --- |
| A | `source_dataset_classifier` | Saved random forest; seven source-scale features | `EXPERIMENTAL` |
| B | `soil_water_balance` | Root-zone depletion calculation | `SIMULATED` or `OK` |
| C | `forecast_advisory`, `demo_forecast` | Forecast validation and alert rules | `OK` or `SIMULATED` |
| D | `resource_comparison` | Resource-intensity formula and yield check | `SIMULATED` or `OK` |

## Common request envelope

| Field | Definition |
| --- | --- |
| `contract_version` | Exactly `0.1.0`. Reject unsupported versions. |
| `request_id` | Client-generated non-empty identifier for tracing a request. |
| `module` | `A`, `B`, `C`, or `D`, matching the endpoint. |
| `as_of_utc` | Optional decision/reference metadata. The common validator does not require or parse it. C uses server time, not this value, to select its live window. |
| `purpose` | `farm_advisory`, `simulation`, or `dataset_benchmark`. A benchmark is not a farm recommendation. |
| `farm` | C requires `location.latitude` [-90,90] and `location.longitude` [-180,180]. B checks `area_ha` when supplied. `field_id` and `timezone` are optional descriptive metadata, not currently authenticated or validated. |
| `crop_context` | Optional descriptive metadata. C uses the presence of `crop` to choose its response scope; thresholds do not yet vary by crop or stage. |
| `inputs` | Module-specific fields described below. |

The common validator requires `contract_version`, `request_id`, `module`, `purpose`, and an `inputs` object. Module validators check the measurements they consume for finite numbers, supported units, and documented ranges; booleans are not measurements. Unknown fields are currently ignored rather than rejected. Do not substitute zero for unknown data; zero is valid only when it represents a known quantity, such as no recent water.

`farm` and `crop_context` may be null for A. B needs `target_area_ha` in its inputs, even if farm metadata is absent. C requires coordinates but can return generic weather without a crop. B returns `NEEDS_DATA` for soil moisture not labelled `m3/m3`, including raw `sensor_percent`; it never divides a sensor percentage by 100 to invent calibration.

### Measurement object

B and D use `{value, unit, evidence}` measurement objects. The following provenance fields are recommended for responsible use:

- `kind`: `observed`, `forecast`, `reference`, `assumed`, or `dataset_record`.
- `source`: instrument, laboratory report, provider, reference URL, or dataset identifier.
- `method`: sampling, laboratory extraction, sensor calibration, aggregation method, or calculation.
- `observed_at_utc`: measurement instant, or null when the quantity describes a period.
- `period_start_utc` / `period_end_utc`: ordered period bounds for aggregates; null for instantaneous readings. Intervals use `(start, end]` for weather accumulations.
- `reference_id`: local evidence record, calibration ID, or published reference; null means supporting evidence is absent.

**Current enforcement:** B checks allowed evidence kinds and a non-empty moisture `calibration_reference`. D requires `assumed` evidence for simulated records and `observed` evidence for measured records. Neither service resolves reference IDs, checks laboratory/sensor records, or validates evidence observation times. Source, method, sampling depths, and evidence periods are descriptive metadata unless explicitly checked below. A uses numeric features instead of measurement objects; C obtains provider data itself.

**Planned:** authenticate supporting records, require appropriate observation/aggregation times, and verify crop/stage/soil applicability. A supplied reference ID is not proof of calibration or field validity.

### Units, interpretation, and prohibited conversions

| Quantity | Unit / representation | Interpretation and limits |
| --- | --- | --- |
| Temperature | C provider data: `°C`; A: source-scale numeric feature | No public Fahrenheit conversion adapter exists. A does not accept a temperature measurement object. |
| Relative humidity / precipitation probability | `%` | [0,100]; probability is not certainty or a confidence score for the entire day. |
| Rainfall / ET0 / irrigation depth | `mm` | Non-negative, with explicit period and aggregation. |
| Wind speed | `km/h` | Non-negative; preserve measurement height (normally 10 m in C). |
| Volumetric soil water content | `m3/m3` | [0,1], with soil-specific calibration and sampled depth. A raw sensor percentage cannot be converted by division by 100 alone. |
| Root depth / sensor depth | `m` | B checks root depth; sensor-depth metadata is not checked yet. |
| Irrigation water / cultivated area | `m3` / `ha` | Non-negative water, positive area. 1 mm over 1 ha = 10 m3; volume needs applicable wetted area. |
| Energy / nutrient input / harvest | `kWh` / `kg_N` / `kg` | D checks totals and period ordering; verifying cycle completion and recorded totals is planned. |
| Soil nutrients | Method-dependent | Preserve `mg/kg`, `kg/ha`, or a publisher's unresolved source scale distinctly. No automatic conversion across units, extraction methods, P vs P2O5, or K vs K2O. |
| pH | A: source-scale numeric `ph` feature | A checks the artifact's observed training range, not an independently defined soil-lab mapping. |

## A — Crop recommendation

Endpoint: `POST /api/crops/recommend`.

### Dataset benchmark mode (current trained model)

Use `purpose=dataset_benchmark` or `simulation` and `inputs.mode=source_dataset_classifier`. Require the pinned `dataset_id`, `dataset_version`, `dataset_sha256`, and a numeric `features` object containing `N`, `P`, `K`, `temperature`, `humidity`, `ph`, and `rainfall`. The service verifies the model checksum, artifact schema, feature order, source identity, and per-feature training ranges.

`row_id` is **optional**. When supplied, it must be a non-negative integer identifying a zero-based CSV data row. The service requires the original local CSV, verifies its checksum, and compares all seven values with that row. Without `row_id`, the service accepts in-range experiment values and reports `source_row_verified=false`; it does not establish that the combination occurred in the source data. The dashboard omits `row_id`, so its model-scale demo works without downloading raw data. The exact-row JSON fixture needs `data/crop_recommendation/raw/Crop_recommendation.csv`.

The model's source N/P/K have unresolved physical units. Rainfall has an unresolved aggregation period; temperature and humidity also lack a documented aggregation basis. Do not invent daily or seasonal definitions or treat in-range numbers as validated farm inputs.

### Farm suitability (not implemented)

The service returns `UNSUPPORTED_CONTEXT` for `inputs.mode=field_suitability` or any other unsupported mode, before validating its agricultural inputs. A source-classifier request with `purpose=farm_advisory` is also unsupported.

**Planned:** independently documented crop profiles or a suitable model with matched measurement units, climate aggregation, growing period, soil/drainage, and water availability, followed by field/season validation. Yield, profit, and rotation advice require their own evidence.

`result` contains three ranked `candidates` (`crop`, uncalibrated `model_score`), consumed `inputs`, `model`, `model_sha256`, `source_row_verified`, `reported_test_macro_f1`, and `score_meaning`. Success always returns `EXPERIMENTAL` with `data_kind=dataset_benchmark`, including when the request purpose is simulation. These are model-scale experiments, never farm suitability or farmer success probabilities.

## B — Irrigation

Endpoint: `POST /api/irrigation/advise`.

### Soil-water-balance advice

`inputs.mode=soil_water_balance`. Require:

| Input | Current validation |
| --- | --- |
| `soil_moisture` | `m3/m3`, [0,1], within supplied WP/FC, non-empty `calibration_reference`, evidence kind `observed` or `assumed`. Reference authenticity is not checked. |
| `soil_profile.field_capacity`, `wilting_point` | Measurement objects in `m3/m3`; 0 <= WP < FC <= 1; evidence kind `reference`, `observed`, or `assumed`. |
| `root_depth` | Measurement in `m`, [0.01,3]. |
| `allowable_depletion_fraction` | Measurement in `fraction`, [0.01,1], including both boundaries. |
| `crop_coefficient` | Measurement in `fraction`, [0,2.5], including zero. |
| `weather` | Objects `et0_24h` and `precipitation_24h`, each a non-negative `mm` measurement. The service consumes supplied totals; it does not call C or align hourly intervals automatically. |
| `recent_water_events` | Object containing non-negative `effective_water_mm` measurement in `mm`, not a list of individual events. |
| `application_efficiency` | Measurement in `fraction`, [0.01,1]. |
| `target_area_ha` | Numeric area >=0.0001 ha; cannot exceed `farm.area_ha` when that value is supplied. |

Unless restricted above, B measurement evidence kinds may be `observed`, `forecast`, `reference`, or `assumed`. Any consumed `assumed` evidence, or `purpose=simulation`, labels the response `SIMULATED`; otherwise it returns `OK` with `data_kind=evidence_backed_inputs`. This label reflects supplied metadata, not authenticated field evidence.

Implemented calculation, with depths in mm:

```text
TAW = 1000 * (FC - WP) * root_depth
RAW = allowable_depletion_fraction * TAW
current_depletion = 1000 * (FC - soil_moisture) * root_depth
projected_depletion = max(0, current_depletion + Kc * ET0 - rain - recent_effective_water)
action = IRRIGATE if projected_depletion >= RAW, otherwise WAIT
net_depth = min(projected_depletion, TAW) if IRRIGATE, otherwise 0
gross_depth = net_depth / application_efficiency
volume_m3 = gross_depth * target_area_ha * 10
```

The root-zone equations follow a [FAO-56-style approach](https://www.fao.org/4/X0490E/x0490e0e.htm), but do not validate local coefficients or calibration. All supplied forecast rain is subtracted; runoff, drainage, layered soils, and effective-rainfall estimation are not modelled independently.

`result` contains `action`, TAW/RAW, current/projected depletion, forecast crop ET/rain, recent effective water, `net_depth_mm`, `gross_depth_mm`, `volume_m3`, `target_area_ha`, and `method`. `reasons` is in the common envelope. No `recheck_at_utc` is returned. Missing efficiency withholds the entire result with `NEEDS_DATA`; partial soil-status results are not implemented. Advice never actuates a pump.

**Planned field-use gates:** reject stale/future moisture observations, check forecast acquisition age and interval alignment, verify calibration and sampled-depth/root-zone applicability, prevent double-counted water, and add a recheck policy. The previously proposed two-hour moisture limit is not currently enforced; C's six-hour forecast limit does not automatically apply to B's supplied totals.

### Controller-behavior ML experiment (notebook only)

Notebook 08's saved random forest predicts an observed valve start within 60 minutes from the Mendeley series. Its weak positive-event detection and non-portable sensor scale are documented in the [A/B audit](../report/bonus_ab_data_audit.md). It is deliberately excluded from farm decisions and is not packaged as a serving artifact.

The API does **not** expose `controller_behavior_experiment`; it returns `UNSUPPORTED_CONTEXT` for that mode. The saved model's prediction is not the soil-water-balance `action`.

## C — Weather

Endpoint: `POST /api/weather/advise`.

Request `inputs.mode=forecast_advisory`, common coordinates, and optional `horizon_hours` (default 24; integer 1–48). Without a crop, scope is `generic_weather`; with `crop_context.crop`, it is `crop_context_weather`. Current thresholds are identical for both scopes, not crop/stage-specific recommendations.

Thresholds are applied unchanged to the selected horizon; rainfall/ET0 thresholds are not scaled or independently validated for every 1–48-hour window. Use the default 24-hour horizon for the documented demo.

For offline presentations, `mode=demo_forecast` is accepted only with `purpose=simulation`. It produces a deterministic, explicitly simulated weather window and never presents itself as provider data. A live provider failure never silently switches to this mode.

The backend obtains the forecast, caches it by location/query for up to six hours, and validates UTC data, acquisition age, units, finite values, percentages, non-negative quantities, array lengths, timestamp ordering, and contiguous requested coverage. Stale cache entries trigger a fresh fetch. Acquisition time is separate from the nullable provider-run time in the internal envelope; the public result does not expose that run time.

The API starts at the next rounded UTC hour and returns the requested number of hourly rows, with `valid_from_utc` and `valid_to_utc` labels. This is not exactly the interval from now to now plus the horizon. Rainfall/ET0 accumulation conventions must be reviewed and aligned before a C-to-B adapter is used; no such automatic adapter exists. ET0 is reference evapotranspiration, not measured crop consumption. Forecast rain is not multiplied by its probability.

`result` includes `summary`, `alerts` (`flag`, `observed`, `threshold`, `action`), configured `rules`, hourly values, acquisition/validity times, units, requested/grid locations, cache usage, and a message. Invalid or incomplete provider payloads currently return `INVALID_INPUT`; provider/network failure returns `DATA_UNAVAILABLE`, and stale data reaching analysis returns `STALE_DATA`. Live failure never silently becomes a simulation. No threshold firing is not proof of safe conditions.

## D — Sustainability comparison

Endpoint: `POST /api/sustainability/score`.

Request inputs: `mode=resource_comparison`, `baseline`, `current`, and `comparison_evidence`. Both records contain crop/location, `basis=whole_crop_cycle`, period bounds, positive area, harvest kg, water m3, electricity kWh, nitrogen nutrient kg_N, and evidence/accounting scope for every total. Resource baselines and baseline harvest must be positive for the present formula. Current harvest/resources can be zero.

Record keys are `crop`, `location`, `basis`, `data_kind` (`simulated` or `measured`), `area_ha` (>=0.0001), `period_start_utc`, `period_end_utc`, and measurement objects `water`, `electricity`, `nitrogen`, and `harvest`. Each total requires a non-empty `accounting_scope`. The Flask service parses these records and independently implements notebook 11's formula; it does not execute or import notebook cells.

**Current comparability checks:** period bounds must have timezone offsets and end after start; both records must have exactly matching crop, location, basis, data kind, duration, and water/electricity/nitrogen accounting-scope strings. Harvest scope is required but not cross-matched yet. Totals must be non-negative; baseline resources and baseline harvest must be positive. Evidence kinds and the comparison note are checked, but underlying records, season/soil comparability, scope completeness, and whether the cycles have actually ended are not verified.

`comparison_evidence` requires a non-empty `note` and a `kind` matching the records (`assumed` for simulation, `observed` for measurement). `references` are optional and not resolved. Simulated and measured records cannot be mixed. Successful status is derived from record `data_kind`, not from `purpose` alone; callers must accurately label assumptions. Do not relabel proposed irrigation, forecasts, or model scores as observed resource totals. Verification of these provenance claims is **planned**, not an existing automatic gate.

Implemented formula: normalize totals by area; for each resource use `clip(50 + 50 * relative_reduction, 0, 100)`. Weight water 0.40, electricity 0.30, and nitrogen 0.30. If yield per hectare is below 95% of baseline, cap the score at 50. The weights and cutoff are project assumptions; 50 means baseline parity. The documented simulated example scores **57.75**.

`result` contains `components`, `weights`, `raw_score`, final `score`, yield-retention fields, `formula_version`, `formula`, `comparison_note`, and `warnings`. Evidence references are not echoed or authenticated. No automatic kg-CO2e conversion exists. Lower recorded inputs do not prove software-caused savings or overall sustainability. **Planned:** completed-cycle gates, evidence resolution, harvest-scope matching, and a reviewed baseline-selection policy.

## Common response contract and errors

All service responses carry `contract_version`, `request_id`, `module`, `generated_at_utc`, `status`, `scope`, `data_kind`, `result`, `reasons`, `missing_inputs`, `sources`, and `limitations`. For withheld results, `result=null`. Reasons include `code` and `message`; a separate `field` path is supplied for some errors, while others include paths in the message. Missing-input lists identify known required fields. Model checksum, formula version, or weather rules/validity are included in the module result as described above.

| Status | Current meaning | HTTP |
| --- | --- | --- |
| `OK` | Supported output with stated limitations | 200 |
| `EXPERIMENTAL` | Source-dataset prediction only | 200 |
| `SIMULATED` | Assumed/demo inputs; output must remain labeled | 200 |
| `NEEDS_DATA` | Required measurements, metadata, or evidence absent | 422 |
| `INVALID_INPUT` | Wrong type, range, ordering, unit, or incompatible fields | 422 |
| `UNSUPPORTED_CONTEXT` | Well-formed request outside model/reference applicability | 422 |
| `STALE_DATA` | Forecast acquisition exceeds C's analysis policy; B reading-age gates are not implemented | 422 |
| `DATA_UNAVAILABLE` | Required model/source CSV unavailable, or live provider/network failure | 503 |

A-D use the HTTP mappings above. The mandatory disease endpoint and bonus E remain HTTP 501 placeholders. Authentication and production API limits are separate work.

## Cross-module boundaries and remaining work

1. A rainfall period must match A's model/profile definition. C's daily forecast cannot silently fill it.
2. B source sensor percentage and calibrated VWC are separate representations; no implicit conversion.
3. B observed-controller ML stays in its notebook experiment; the API uses calculations and never controls a pump.
4. Supply D with recorded totals, not B's proposed volumes or C's rainfall estimates relabelled as measured savings.
5. B labels consumed assumptions as simulated; C requires an explicit simulated demo mode; D derives the label from its records. A always reports a dataset-scoped experiment.
6. Supplied evidence metadata are not authenticated. Extend existing validators instead of claiming that JSON structure proves field validity.
7. Fixed example dates are test metadata. C uses server time; B does not check reading age, and D does not check cycle completion yet.
8. Neither JSON structure nor a supplied reference ID proves a farm is represented by training data.

Request fixtures and **current** expected outcomes are in [bonus_contract_examples.json](examples/bonus_contract_examples.json). Its separate `planned_acceptance_cases` list records desired gates that are not implemented. Tests use these fixtures without executing notebooks or training; see [tests/README.md](../tests/README.md). Frontend integration is complete, while strict unknown-field schemas, reference verification, cross-module interval adapters, and field validation remain work for a later implementation task.
