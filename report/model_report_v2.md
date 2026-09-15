# Model Report: Model v2 — Enhanced ResNet-50

> **Historical experiment record.** Use [`model_report.md`](model_report.md) for submission. These values come from saved notebook outputs and were not reproduced for the currently packaged compressed checkpoint.

**Version:** 2.0 (Label Smoothing & Stronger Augmentation)  
**Historical Checkpoint:** `model_v2.pkl` (90.3 MB uncompressed); current packaged path is `model/weights/cv/model_v2.pkl.gz`.
**Evaluation Standard:** SIH 2026 Section 7.3 One-Page Model Report

---

## 1. Executive Summary Table

| Field | Specification / Value |
| :--- | :--- |
| **Task** | Multiclass crop-disease image classification across **38 classes** (14 crop types). |
| **Dataset & Split** | Reported PlantVillage color dataset; exact source version and license confirmation are pending.<br>• Total Images: **54,305**<br>• Train Set: **43,444 images** (80.0%)<br>• Validation Set: **10,861 images** (20.0%)<br>• Validation was used for checkpoint selection and is not an independent test. |
| **Model / Approach** | • **Architecture:** ResNet-50 (Deeper residual capacity)<br>• **Input Resolution:** $224 \times 224 \text{ px}$<br>• **Loss Function:** Label-Smoothed Cross-Entropy ($\alpha = 0.1$)<br>• **Augmentations:** Random Perspective (0.2), Color Jitter, Random Rotation ($20^\circ$), Random Resized Crop<br>• **Optimizer:** Adam ($\text{lr} = 10^{-4}$)<br>• **Batch Size & Epochs:** Batch Size = 32, Trained for 10 Epochs (Best: Epoch 9) |
| **Metric & Result** | • **Macro-F1 (Primary Metric): 0.9946**<br>• **Top-1 Validation Accuracy: 99.67% (10,825 / 10,861)**<br>• **Macro Precision:** 0.9940 \| **Macro Recall:** 0.9950<br>• **Average GPU Latency:** 5.36 ms / image (Fastest inference throughput) |
| **Baseline Comparison** | **+0.34 percentage points Macro-F1 over v1** (0.9946 vs 0.9912). Corn Cercospora F1 rose from 0.9020 to 0.9240. Calibration was not measured, so no probability-calibration improvement is claimed. |
| **Limitations & Failure Cases** | • **Weakest Classes:** Corn Cercospora Leaf Spot (F1: 0.9240), Corn Northern Leaf Blight (F1: 0.9590), Potato Healthy (F1: 0.9840).<br>• **Resolution Bottleneck:** 224px may lose fine lesion detail.<br>• **Domain Shift:** A 34-image PlantDoc convenience sample produced **23.5%** top-1 and **44.1%** top-3. The sample is too small and its historical script could use both train and test directories, so it is not a clean held-out benchmark. |

---

## 2. Per-Class Validation Breakdown (PlantVillage: 10,861 Samples)

```text
Class Name                                          Precision   Recall   F1-Score   Support
-------------------------------------------------------------------------------------------
Apple___Apple_scab                                     1.0000   1.0000     1.0000       126
Apple___Black_rot                                      1.0000   1.0000     1.0000       125
Apple___Cedar_apple_rust                               1.0000   1.0000     1.0000        55
Apple___healthy                                        1.0000   1.0000     1.0000       329
Blueberry___healthy                                    1.0000   1.0000     1.0000       300
Cherry_(including_sour)___Powdery_mildew               1.0000   1.0000     1.0000       210
Cherry_(including_sour)___healthy                      1.0000   0.9882     0.9940       170
Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot     0.9070   0.9420     0.9240       103
Corn_(maize)___Common_rust_                            1.0000   1.0000     1.0000       239
Corn_(maize)___Northern_Leaf_Blight                    0.9690   0.9490     0.9590       197
Corn_(maize)___healthy                                 0.9960   1.0000     0.9980       233
Grape___Black_rot                                      0.9960   1.0000     0.9980       236
Grape___Esca_(Black_Measles)                           1.0000   1.0000     1.0000       276
Grape___Leaf_blight_(Isariopsis_Leaf_Spot)             1.0000   1.0000     1.0000       215
Grape___healthy                                        1.0000   1.0000     1.0000        84
Orange___Haunglongbing_(Citrus_greening)               1.0000   1.0000     1.0000      1102
Peach___Bacterial_spot                                 1.0000   0.9980     0.9990       459
Peach___healthy                                        0.9860   1.0000     0.9930        72
Pepper,_bell___Bacterial_spot                          1.0000   1.0000     1.0000       200
Pepper,_bell___healthy                                 0.9970   1.0000     0.9980       295
Potato___Early_blight                                  1.0000   1.0000     1.0000       200
Potato___Late_blight                                   1.0000   0.9950     0.9970       200
Potato___healthy                                       0.9690   1.0000     0.9840        31
Raspberry___healthy                                    1.0000   1.0000     1.0000        74
Soybean___healthy                                      1.0000   0.9990     1.0000      1018
Squash___Powdery_mildew                                1.0000   1.0000     1.0000       367
Strawberry___Leaf_scorch                               1.0000   1.0000     1.0000       222
Strawberry___healthy                                   1.0000   1.0000     1.0000        92
Tomato___Bacterial_spot                                1.0000   0.9950     0.9980       425
Tomato___Early_blight                                  0.9950   0.9750     0.9850       200
Tomato___Late_blight                                   0.9950   0.9970     0.9960       382
Tomato___Leaf_Mold                                     1.0000   1.0000     1.0000       191
Tomato___Septoria_leaf_spot                            0.9920   0.9940     0.9930       354
Tomato___Spider_mites Two-spotted_spider_mite          1.0000   0.9880     0.9940       335
Tomato___Target_Spot                                   0.9690   1.0000     0.9840       281
Tomato___Tomato_Yellow_Leaf_Curl_Virus                 1.0000   0.9990     1.0000      1071
Tomato___Tomato_mosaic_virus                           1.0000   1.0000     1.0000        74
Tomato___healthy                                       1.0000   1.0000     1.0000       318
-------------------------------------------------------------------------------------------
Overall Accuracy                                                              0.9967     10861
Macro Average                                          0.9940   0.9950     0.9946     10861
Weighted Average                                       0.9970   0.9970     0.9970     10861
```
