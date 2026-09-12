# A/B input and dataset audit

Audit date: 2026-09-12. Contract: [version 0.1.0](../docs/bonus_input_contract.md).

The audit reads existing data, saved training reports, split row IDs, and model file bytes. It does not execute notebooks, deserialize models, run inference, or retrain. Metrics below are from the user's saved runs, not newly reproduced results. Exact measurements and artifact fingerprints are in [bonus_ab_data_audit.json](bonus_ab_data_audit.json).

## Trained model inventory

| Module | Saved selected model | Evidence | Current scope |
| --- | --- | --- | --- |
| A | Random forest | Export exists; SHA-256 matches the hash in the saved training report | Source-dataset crop-label benchmark |
| B | Random forest, threshold 0.85 | Export exists; saved run reports training/evaluation; current file fingerprint recorded by this audit | Observed controller behavior on one strawberry field |
| C | No trained model needed | Forecast client and rule outputs were saved by the user | Weather advisory prototype |
| D | No trained model needed | Formula output was saved by the user | Simulated resource-use comparison |

The irrigation training report does not include an artifact hash. This audit fingerprints the file now but cannot retroactively prove it is the exact file evaluated in that report. Future export metadata should bind artifact, source data, feature order, training configuration, and evaluation together.

## A — Crop recommendation

Source: [Atharva Ingle's Kaggle dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset), version 1. Its original downloaded bytes match the recorded manifest. Publisher metadata describes augmented rainfall, climate, and fertilizer data; it does not establish independent suitability outcomes.

Verified locally:

- 2,200 rows; 22 labels with 100 rows each.
- No missing fields, non-finite numeric values, or exact duplicate rows.
- No identical seven-feature vectors with conflicting labels.
- Saved splits contain 1,320 training, 440 validation, and 440 test rows; no shared row IDs, duplicated IDs, or omitted source rows.
- Saved test macro-F1: **0.990869**; accuracy: **0.990909**; top-three label accuracy: **1.0**.

These checks establish source-file integrity and disjoint row partitions. They cannot rule out related augmented examples or establish generalization to independent farms. The source lacks the identifiers needed for a farm/season split.

### Blocking input gaps

| Gap | Why it matters | Required resolution |
| --- | --- | --- |
| N/P/K physical units and laboratory extraction methods unresolved | A soil report in mg/kg or kg/ha cannot be mapped reliably to arbitrary source ratios | Find authoritative original measurement definitions or use a source/model with documented units and methods |
| Rainfall aggregation period unresolved | Daily forecast, seasonal total, and climate normal have different meanings | Establish the exact source period; no automatic C-to-A rainfall mapping |
| Temperature/humidity aggregation basis unresolved | Instantaneous readings can differ substantially from growing-season averages | Establish period/statistic and match incoming measurements |
| No independent field/season suitability labels | High label accuracy does not show a crop is suitable or profitable | Build an independently reviewed scenario/field evaluation with evidence-backed expected suitability |
| Missing agronomic context | Stage, season, drainage, irrigation access, and rotation can change suitability | Define supported contexts and independently documented crop profiles |

**Decision:** preserve the trained classifier as an experimental benchmark. Field suitability is not yet supported. An `inputs_compatible=true` checkbox or an in-range numerical value does not resolve the gaps.

## B — Irrigation

Source: [Mendeley cjb4vy4mzj, version 3](https://data.mendeley.com/datasets/cjb4vy4mzj/3). The publisher describes soil-moisture readings and commanded valve relay states from a strawberry field in Paraguay. It gives sensor percentages rather than a general calibration to volumetric water content.

Verified locally:

- Both source files match their manifest hashes, with no missing fields, exact duplicate rows, duplicate timestamps, or out-of-order timestamps.
- Moisture: 4,293 rows; source values 68.57–86.94; median sampling interval about 19.92 minutes.
- Valve: 17,427 rows; 14,038 closed and 3,389 open records; median interval 5 minutes.
- Both streams contain a gap of roughly **63 hours**. Continuous sampling must not be assumed, and interpolation across outages needs explicit justification.
- Saved chronological split: 2,408 training, 435 validation, 577 test windows. These are saved report counts, not a newly reconstructed training pipeline.
- Saved test macro-F1: **0.601253**; positive precision **0.277778**; positive recall **0.238095**.
- Saved confusion matrix: TN=509, FP=26, FN=32, TP=10. The model detected **10 of 42 positive windows**. Overlapping windows are correlated and are not 42 independent watering events.

### Blocking input/target gaps

| Gap | Why it matters | Required resolution |
| --- | --- | --- |
| Commanded relay state is the target | A command is neither independently confirmed water application nor agronomically ideal need | Label this model as controller behavior; define soil-water-balance advice separately |
| No verified portable sensor calibration | Dividing 80% by 100 cannot establish 0.8 m3/m3 VWC | Soil/sensor-specific calibration and sampled-depth/root-zone representativeness evidence |
| Missing root, soil, stage, and crop-water parameters | The current features cannot calculate a defensible irrigation dose | Evidence for FC, WP, current rooting depth, depletion fraction, crop coefficient, and application efficiency |
| No forecast features or local weather applicability | Learned controller behavior cannot automatically account for upcoming rain | Align actual forecast intervals with the current water-balance state |
| Temporal gaps and correlated examples | Inflated confidence and invalid rolling histories are possible | Keep freshness/coverage gates; add event-level/blocked validation before claiming robust event detection |
| Weak positive detection | High overall accuracy is dominated by closed-valve periods | Improve only on training/validation data under a predeclared objective; preserve test-set status |

**Decision:** retain the ML artifact for an experimental source-data demo. Use a separately validated soil-water-balance path for irrigation advice. Notebook 07's assumed profiles remain demonstrations until field calibration and parameter evidence exist. No current model supports autonomous pump control or measured water-savings claims.

The physical-input basis for a soil-water balance is described in [FAO-56 chapter 8](https://www.fao.org/4/X0490E/x0490e0e.htm). A published equation does not validate local parameters or an implementation.

## Next implementation requirements

1. Implement validators/adapters for the contract and its explicit failure cases; keep endpoint status and evidence scope visible.
2. For A, resolve source semantics or select independently documented suitability profiles/data before accepting live farm inputs. Preserve the existing model and its benchmark.
3. For B, establish soil/sensor calibration and parameter evidence, then review water-balance behavior against controlled scenarios. Keep controller ML outside the irrigation-action path.
4. Bind future model exports to evaluation hashes and publish only results actually produced by user-run experiments.
5. Validate cross-module time periods and units before frontend connection. Weather forecasts cannot silently become A climate features or D measured savings.

No new training, model execution, Git commit, or Git push was performed for this audit.
