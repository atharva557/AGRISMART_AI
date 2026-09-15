# AgriSmart AI — Concise Model Report

## Task

Crop-disease image classification across 38 PlantVillage labels and 14 crops. The packaged Python interface is `predict(image_path) -> class_label`.

## Dataset and Splits

* **Controlled Training/Validation:** 54,305 curated PlantVillage color images (43,444 training images and 10,861 validation images).
* **In-the-Wild Benchmark:** Combined PlantVillage and PlantDoc field evaluation dataset (84 deterministic test samples across 37 distinct crop-disease classes with complex backgrounds and lighting).

## Model Architecture & Approach

* **Primary Production Model:** ConvNeXt-Tiny (`convnext_tiny.fb_in22k_ft_in1k_384`) at $384 \times 384$ pixels.
* **Lightweight Fallback:** ResNet-18 at $224 \times 224$ pixels ($19.8\text{ MB}$ footprint).
* **Inference Serving:** Loads compressed FP16 checkpoint tensors with automatic device casting, corrects EXIF orientation, converts images to RGB, applies standard ImageNet normalization, and caches the model singleton per process with cross-platform CPU/GPU execution.

## Benchmark Performance Comparison

| Model | Architecture | Input Size | Top-1 Field Accuracy | Top-3 Field Accuracy | Macro F1-Score | PlantVillage Val Accuracy | Latency (GPU) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model v1** | ResNet-18 | $224 \times 224$ | 65.48% (55/84) | 78.57% (66/84) | 0.7237 | 99.43% | 7.60 ms |
| **Model v2** | ResNet-50 | $224 \times 224$ | 69.05% (58/84) | 77.38% (65/84) | 0.7553 | 99.67% | **5.40 ms** |
| **Model v3 (Selected)** | **ConvNeXt-Tiny** | **$384 \times 384$** | **72.62% (61/84)** | **83.33% (70/84)** | **0.7866** | **99.85%** | 20.26 ms |

> Detailed confusion matrix heatmaps and comparison figures are available in [`outputs/figures/`](../outputs/figures/) and documented in [`outputs/metrics/CV_MODELS_BENCHMARK_REPORT.md`](../outputs/metrics/CV_MODELS_BENCHMARK_REPORT.md).

## Inference CLI

```powershell
# Single label output
python -m model.predict --image "data/sample_leaves/sample_leaf.jpg"

# Full diagnostic JSON with confidence and Top-3 ranked candidates
python -m model.predict --image "data/sample_leaves/sample_leaf.jpg" --details

# Verify checkpoint integrity and class alignment
python -m model.submission_check
```

## Known Limitations & Safeguards

- Lab-trained models may experience accuracy drop on field photographs with soil or sun glares.
- The 0.75 confidence threshold is uncalibrated and withholds disease-specific recommendations when confidence is low.
- Photo-quality checks are heuristics designed to flag blurry or dark photos.
- Cross-platform verified across Windows, Linux, and macOS (with and without GPU).
