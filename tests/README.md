# Tests

Run from the repository root: `python -m unittest discover -s tests -v`.

These checks verify scaffold behavior, not model quality. Replace the inference placeholder check when the actual model is connected.

For a real prediction smoke test, place a properly sourced image from your permitted data at `tests/sample_leaf.jpg` locally. It is ignored by Git. No fake JPEG or copied dataset image is bundled.
