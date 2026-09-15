# Tests

Run from the repository root with the project virtual environment active:

```powershell
python -m pytest -q tests
npm run test:frontend
```

Install Python requirements and frontend dependencies, then run `npm run build:all` first. The CV checkpoints are now tracked as `model/weights/cv/model_v*.pkl.gz`; Git LFS is not required for this version.

The checks cover pages/assets, A–D contracts, saved-model inference, the disease API-to-assistant connection, image validation/cleanup, concurrent cache initialization, forced reload, and fallback. The cache is per Python process, not shared between server workers. Gemini responses and regional translation fallback are mocked for offline tests; no live service verification is implied.

A's no-row model-scale test requires its saved artifact but not the raw CSV. Requests with `row_id` still require the exact pinned source CSV. C uses deterministic provider-shaped data or its explicit demo.

Tests do not train models, execute notebooks, authenticate field evidence, or prove real-world accuracy. The stored historical benchmark scores have not been independently reproduced for the newly FP16-compressed checkpoints. Sample inference explicitly skips if its permitted sample image is absent.

Standalone frontend check: `python tests/test_frontend.py`.

See the root [README](../README.md) for recorded results and operational limitations.
