# Tests

Run from the repository root: `python -m unittest discover -s tests -v`.

These checks verify the Flask shell, A-D request/response behavior, saved A-model inference when its local artifact is present, B/D calculations, and C forecast rules using deterministic provider data. They do not execute notebooks, train models, or independently reproduce saved benchmark metrics. Replace the core inference placeholder check when the disease model is connected.

For a real prediction smoke test, place a properly sourced image from your permitted data at `tests/sample_leaf.jpg` locally. It is ignored by Git. No fake JPEG or copied dataset image is bundled.
