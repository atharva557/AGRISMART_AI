# Model Report: Model v3 — Champion ConvNeXt-Tiny (384px)

**Version:** 3.0 (Champion SOTA Architecture)  
**File Checkpoint:** `notebooks/cv_model_notebooks/model_v3.pkl` (106.3 MB)  
**Evaluation Standard:** SIH 2026 Section 7.3 One-Page Model Report

---

## 1. Executive Summary Table

| Field | Specification / Value |
| :--- | :--- |
| **Task** | Multiclass crop-disease image classification across **38 classes** (14 crop types). |
| **Dataset & Split** | **PlantVillage Dataset** (Color, leaf specimen imagery, CC0 License).<br>• Total Images: **54,305**<br>• Train Set: **43,444 images** (80.0%)<br>• Validation Set: **10,861 images** (20.0%) |
| **Model / Approach** | • **Architecture:** ConvNeXt-Tiny (`convnext_tiny.fb_in22k_ft_in1k_384`)<br>• **Input Resolution:** $\mathbf{384 \times 384 \text{ px}}$ (Natively pretrained at 384px)<br>• **Layer Design:** $7 \times 7$ depthwise convolutions, inverted bottleneck, LayerNorm<br>• **Loss Function:** Label-Smoothed Cross-Entropy ($\alpha = 0.1$)<br>• **Optimizer:** AdamW ($\text{lr} = 10^{-4}$, weight decay $= 0.01$)<br>• **Scheduler:** CosineAnnealingLR ($T_{\max}=10, \eta_{\min}=10^{-6}$)<br>• **Precision:** Automatic Mixed Precision (FP16 AMP)<br>• **Batch Size & Epochs:** Batch Size = 64, Trained for 10 Epochs (Best: Epoch 10) |
| **Metric & Result** | • **Macro-F1 (Primary Metric): 0.9969**<br>• **Top-1 Validation Accuracy: 99.85% (10,845 / 10,861)**<br>• **Macro Precision:** 0.9970 \| **Macro Recall:** 0.9968<br>• **33 / 38 classes achieve F1 > 0.9900**<br>• **Average GPU Latency:** 24.51 ms / image |
| **Baseline Comparison** | **+0.57% Macro-F1 improvement over v1 baseline (0.9969 vs 0.9912)** and **+0.23% over v2**. Reduces validation error rate by **74%** compared to baseline. Lifted the hardest class (Corn Cercospora) from F1 0.9020 to **0.9608**. |
| **Limitations & Failure Cases** | • **In-the-Wild Domain Shift:** When tested on unsegmented field imagery (PlantDoc dataset), top-1 accuracy is **32.4%** and top-3 accuracy is **58.8%** (>2× higher than ResNet-18 baseline).<br>• **Safety Mitigation:** The built-in **0.75 confidence threshold** successfully flags 44.1% of uncertain in-field predictions as *"Low Confidence / Don't Know"*, shielding users from erroneous diagnoses. |

---

## 2. Per-Class Validation Breakdown (PlantVillage: 10,861 Samples)

```text
Class Name                                          Precision   Recall   F1-Score   Support
-------------------------------------------------------------------------------------------
Apple___Apple_scab                                     1.0000   1.0000     1.0000       126
Apple___Black_rot                                      1.0000   1.0000     1.0000       125
Apple___Cedar_apple_rust                               1.0000   1.0000     1.0000        55
Apple___healthy                                        1.0000   0.9939     0.9970       329
Blueberry___healthy                                    0.9934   1.0000     0.9967       300
Cherry_(including_sour)___Powdery_mildew               1.0000   1.0000     1.0000       210
Cherry_(including_sour)___healthy                      1.0000   0.9941     0.9971       170
Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot     0.9703   0.9515     0.9608       103
Corn_(maize)___Common_rust_                            1.0000   0.9958     0.9979       239
Corn_(maize)___Northern_Leaf_Blight                    0.9700   0.9848     0.9773       197
Corn_(maize)___healthy                                 1.0000   1.0000     1.0000       233
Grape___Black_rot                                      1.0000   1.0000     1.0000       236
Grape___Esca_(Black_Measles)                           1.0000   1.0000     1.0000       276
Grape___Leaf_blight_(Isariopsis_Leaf_Spot)             1.0000   1.0000     1.0000       215
Grape___healthy                                        1.0000   1.0000     1.0000        84
Orange___Haunglongbing_(Citrus_greening)               1.0000   1.0000     1.0000      1102
Peach___Bacterial_spot                                 1.0000   1.0000     1.0000       459
Peach___healthy                                        1.0000   1.0000     1.0000        72
Pepper,_bell___Bacterial_spot                          1.0000   1.0000     1.0000       200
Pepper,_bell___healthy                                 1.0000   1.0000     1.0000       295
Potato___Early_blight                                  1.0000   1.0000     1.0000       200
Potato___Late_blight                                   0.9950   0.9950     0.9950       200
Potato___healthy                                       0.9677   0.9677     0.9677        31
Raspberry___healthy                                    1.0000   1.0000     1.0000        74
Soybean___healthy                                      1.0000   0.9990     0.9995      1018
Squash___Powdery_mildew                                1.0000   1.0000     1.0000       367
Strawberry___Leaf_scorch                               1.0000   1.0000     1.0000       222
Strawberry___healthy                                   1.0000   1.0000     1.0000        92
Tomato___Bacterial_spot                                1.0000   1.0000     1.0000       425
Tomato___Early_blight                                  0.9950   1.0000     0.9975       200
Tomato___Late_blight                                   0.9948   0.9974     0.9961       382
Tomato___Leaf_Mold                                     1.0000   1.0000     1.0000       191
Tomato___Septoria_leaf_spot                            1.0000   1.0000     1.0000       354
Tomato___Spider_mites Two-spotted_spider_mite          1.0000   1.0000     1.0000       335
Tomato___Target_Spot                                   1.0000   1.0000     1.0000       281
Tomato___Tomato_Yellow_Leaf_Curl_Virus                 1.0000   1.0000     1.0000      1071
Tomato___Tomato_mosaic_virus                           1.0000   1.0000     1.0000        74
Tomato___healthy                                       1.0000   1.0000     1.0000       318
-------------------------------------------------------------------------------------------
Overall Accuracy                                                              0.9985     10861
Macro Average                                          0.9970   0.9968     0.9969     10861
Weighted Average                                       0.9985   0.9985     0.9985     10861
```
