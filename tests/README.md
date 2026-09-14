# Tests

Run from the repository root with the project virtual environment activated.

## Prerequisites

Install `requirements.txt`, then build the frontend and obtain the existing runtime checkpoints:

```powershell
npm install
npm run build:all
git lfs pull --include="model/weights/cv/model_v3.pkl,model/weights/cv/model_v1.pkl" --exclude=""
```

The checkpoints are downloaded, not trained. ResNet-50 (`model_v2.pkl`) is not needed by the Flask primary/fallback path. On CPU-only machines, install compatible CPU PyTorch/torchvision wheels before the remaining requirements.

## Checks

```powershell
python -m pytest tests -q
npm run test:frontend
# Optional standalone route/template/asset check:
python tests/test_frontend.py
```

The Python suite checks routes and compiled assets, A-D contracts and calculations, sample-image CV inference, and the assistant's fallback/mocked Gemini behavior. The JavaScript tests check that the disease assistant preserves `raw_label`, including punctuation, instead of passing the readable disease name to the knowledge base.

A's model-dependent test omits `row_id`, so it does not need the raw CSV. Exact-row requests still require the pinned CSV described in [data/README.md](../data/README.md). C uses injected provider data or its explicit simulated demo. Gemini tests mock generation, and the regional-language fallback test disables the translator rather than making a live request.

These checks never execute notebooks or train models. A sample-image prediction does not independently reproduce the saved accuracy/F1 benchmarks or establish field reliability. The suite also does not authenticate calibration/evidence records or cover every proposed field-safety gate. JSON `planned_acceptance_cases` remain a roadmap, not claims of passing tests.
