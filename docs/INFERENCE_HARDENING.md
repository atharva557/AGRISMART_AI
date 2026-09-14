# Disease inference: reliability fixes

This update builds on the FP16/gzip checkpoints introduced in `8d66086`. It keeps the new UI and compressed weights; no models were trained, notebooks executed, or checkpoints changed by this update.

## What changed

- **Thread-safe caching:** a lock serializes initial model loading. Later requests reuse the same model and metadata instead of rebuilding the network. ConvNeXt-Tiny remains primary, with ResNet-18 as fallback if the primary cannot load.
- **Upload handling:** UUID-prefixed filenames avoid collisions. JPEG/PNG content is checked before inference, with a 50-megapixel ceiling. Temporary uploads are cleaned up on success and failure.
- **Safe errors:** model availability and invalid-image failures have clearer HTTP responses. Internal prediction exception details are logged rather than returned to users.
- **Assistant grounding:** the frontend requires the official classifier label; it does not guess it from the readable disease name. Missing explanation context no longer leaves a chat loading indicator behind.
- **Startup resilience:** the health endpoint checks checkpoint presence without importing PyTorch. Other pages and health checks remain available when inference dependencies are missing.
- **Reliable tests:** frontend checks now assert failures rather than returning numbers to pytest. Regional translation fallback and no-key Gemini tests are isolated from network/environment dependencies. Missing sample images explicitly skip the sample test.
- **CLI compatibility:** inference output uses plain text rather than emoji, avoiding a common Windows console encoding issue. The official label and diagnostic information are preserved.

## Operational behavior

The cache is **per Python process**, not shared across server workers. Each worker loads its own model on its first prediction. There is no TTL or automatic checkpoint-change detection: restart the server after replacing weights, or deliberately call the internal `get_model(force_reload=True)` API. Only model initialization is serialized; inference is not globally locked.

The loader prefers `.pkl.gz` checkpoints, decompresses on initial load, and casts stored floating-point weights to the network's parameter dtype. Git LFS is not required for the current compressed artifacts. Only load trusted pickle checkpoints.

| Disease upload outcome | HTTP status |
| --- | --- |
| Successful prediction | 200 |
| Missing image, unsupported extension/content, unreadable image, or excessive pixel count | 422 |
| Request exceeds the configured 10 MiB body limit | 413 |
| Inference dependencies or model unavailable | 503 |
| Unexpected prediction failure | 500 |

Checkpoint presence in `/api/health` is not proof that a checkpoint is loadable or that predictions are accurate.

## Run and verify

From the repository root in PowerShell, after dependencies are installed:

```powershell
npm run build:all
.\.venv\Scripts\python.exe -m pytest -q tests
npm run test:frontend
.\.venv\Scripts\python.exe run.py
```

Open `http://127.0.0.1:5000`. Rebuild the frontend after editing its source; generated bundles are not committed. See [test prerequisites and scope](../tests/README.md).

Verification on 2026-09-14:

- Python: **45 tests and 14 subtests passed**, without warnings.
- JavaScript: **4 tests passed**; production CSS/JavaScript build succeeded.
- Two real disease API uploads used the compressed ConvNeXt checkpoint and triggered **one checkpoint load**. Both returned `Tomato___Early_blight` with confidence `0.9068` on the same bundled sample.
- The prediction's official label flowed into the offline assistant explanation and chat, both HTTP 200. No temporary upload files remained.
- Tests cover concurrent initial loading, cache reuse/refresh, fallback, compressed checkpoint selection, FP16 casting, invalid uploads, and startup with inference dependencies blocked.

These are integration/reliability checks, **not a new accuracy benchmark**. The historical validation scores have not been independently revalidated for FP16 weights. GPU performance, live Gemini, live translation, live weather, and field-photo accuracy were not verified by this update. A–D contract tests passed, but do not establish field readiness or authenticate their input evidence.
