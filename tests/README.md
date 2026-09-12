# Tests

Run from the repository root: `python -m unittest discover -s tests -v`.

These checks verify the Flask shell, A-D request/response behavior, saved A-model inference when its local artifact is present, B/D calculations, and C forecast rules using deterministic provider data. They do not execute notebooks, train models, or independently reproduce saved benchmark metrics. Replace the core inference placeholder check when the disease model is connected.

The current suite has 12 tests. It loads named request fixtures from `docs/examples/bonus_contract_examples.json`; the A exact-row test requires both the packaged model and the pinned original CSV at `data/crop_recommendation/raw/Crop_recommendation.csv`. With no CSV, that request correctly returns `DATA_UNAVAILABLE` rather than an experimental result. The separate A model-scale fixture omits `row_id` and can run without raw data. The model-dependent test is skipped only when the model artifact itself is missing.

Before running the full suite, obtain the pinned CSV as described in [data/README.md](../data/README.md). When the model is present but the CSV is absent, the exact-row test assertion fails; that fixture prerequisite does not prevent the dashboard's no-CSV A demonstration from working. No training is required to install the original source CSV.

C's tests inject complete provider-shaped data or use the explicit simulated demo, so they do not depend on live network availability. JSON `negative_acceptance_cases` describe current outcomes; `planned_acceptance_cases` are a roadmap, not additional passing tests. The suite does not cover all proposed field-safety checks, authenticate calibration/evidence records, or validate production performance.

For a real prediction smoke test, place a properly sourced image from your permitted data at `tests/sample_leaf.jpg` locally. It is ignored by Git. No fake JPEG or copied dataset image is bundled.
