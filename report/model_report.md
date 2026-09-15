# AgriSmart AI - concise model report

## Task

Crop-disease image classification across 38 PlantVillage labels and 14 crops. The packaged Python interface is `predict(image_path) -> class_label`.

## Dataset and split

Saved experiments report 54,305 PlantVillage color images: 43,444 training images and 10,861 validation images. The validation directory was used for checkpoint selection and final reporting, so it is not an independent test. The exact downloaded dataset version, licence, split manifest, and correspondence with the organizer's final class contract require confirmation.

## Model and approach

Selected model: ConvNeXt-Tiny `convnext_tiny.fb_in22k_ft_in1k_384` at 384 x 384 pixels. Saved training configuration: AdamW with learning rate 0.0001 and weight decay 0.01, label-smoothed cross-entropy at 0.1, and cosine learning-rate scheduling. ResNet-18 at 224 x 224 is packaged as a fallback.

Serving loads compressed FP16 checkpoint tensors into the model parameter dtype, corrects EXIF orientation, converts images to RGB, applies ImageNet normalization, and caches the model per process.

## Reported results

| Model | Macro-F1 | Accuracy |
| --- | ---: | ---: |
| ResNet-18 | 0.9912 | 99.43% |
| ResNet-50 | 0.9946 | 99.67% |
| ConvNeXt-Tiny | 0.9969 | 99.85% (10,845 / 10,861) |

The ConvNeXt result is historical local validation, not an organizer-held-out score. Saved aggregate values are macro precision 0.9970, macro recall 0.9968, weighted F1 0.9985, and accuracy 0.9985. The full per-class table is in the root [README](../README.md#convnext-tiny-per-class-validation-metrics).

Organizer-held-out macro-F1, numeric confusion matrix, and per-class precision/recall are pending organizer evaluation.

## Baseline

The local ResNet-18 baseline achieved validation macro-F1 0.9912. The organizer baseline and score bands have not been supplied, so no official comparison is claimed.

## Inference

```powershell
python -m model.predict --image "C:\path\to\leaf.jpg"
python -m model.submission_check --labels "C:\path\to\organizer_classes.json"
```

## Limitations

- Severe lab-to-field domain shift.
- Validation was used for model selection; no independent core test metric is claimed.
- Exact organizer-label compatibility remains unresolved.
- Scores are not calibrated probabilities.
- The 0.75 threshold does not prevent incorrect high-score predictions.
- Photo-quality rules are heuristics, not semantic non-plant detection.
- Current compressed weights and preprocessing have not received a new full independent benchmark.
