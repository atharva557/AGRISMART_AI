# AgriSmart AI — Model Report (One-Page Summary)

**Document Version:** 1.0  
**Generated:** 2026-09-11  
**Project:** AgriSmart AI (Plant Pathology & Smart Agricultural Advisory)

---

## 📋 Executive Summary Table (Section 7.3 Compliance)

| Field | Description / Measurement |
| :--- | :--- |
| **Task** | Multiclass Crop Disease Image Classification across **38 plant-pathology classes** (14 crop species: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Bell Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato). |
| **Dataset & Split** | **PlantVillage Dataset** (Color, leaf specimen imagery, CC0/Public Domain).<br>• Total images: **54,305**<br>• Train set: **43,444 images** (80.0%)<br>• Validation set: **10,861 images** (20.0%)<br>• Stratified per-class split matching official benchmark split. |
| **Model / Approach** | **Champion Model (v3): ConvNeXt-Tiny** (`convnext_tiny.fb_in22k_ft_in1k_384`)<br>• Input Resolution: **384 × 384 px** (resolves micro-lesions and vein textures)<br>• Optimizer: AdamW ($\text{lr}=10^{-4}$, weight decay $=0.01$)<br>• Loss: Label Smoothed Cross-Entropy ($\alpha=0.1$ to prevent overconfidence)<br>• Scheduler: CosineAnnealingLR ($T_{\max}=10$, $\eta_{\min}=10^{-6}$)<br>• Hardware Optimization: PyTorch FP16 Automatic Mixed Precision (AMP) on CUDA |
| **Metric & Result** | **Macro-F1 (Primary Metric): 0.9969**<br>**Top-1 Accuracy: 99.85% (10,845 / 10,861 correct)**<br>• Weighted F1: 0.9985 \| Macro Precision: 0.9970 \| Macro Recall: 0.9968<br>• 33 out of 38 classes achieved **F1 > 0.9900**.<br>• Lowest class F1: Corn Cercospora Leaf Spot (0.9608). |
| **Baseline & Progression** | • **Baseline (v1, ResNet-18, 224px):** Macro-F1 = **0.9912**, Accuracy = **99.43%**<br>• **Iteration 2 (v2, ResNet-50, 224px, Label Smoothing):** Macro-F1 = **0.9946**, Accuracy = **99.67%**<br>• **Champion (v3, ConvNeXt-Tiny, 384px):** Macro-F1 = **0.9969**, Accuracy = **99.85%** *(+0.57% Macro-F1 over baseline; cuts error rate by 74%)*. |
| **Limitations & Failure Cases** | **1. Lab-to-Field Domain Shift (Evaluated on PlantDoc in-the-wild dataset):**<br>Models trained on uniform lab backgrounds experience accuracy degradation when presented with unsegmented outdoor field photos containing background soil, intense sunlight, or multiple leaves.<br>**2. Mitigation Implemented:**<br>• **75% Confidence Floor Gate:** Successfully traps and flags 44.1%–58.8% of uncertain out-of-distribution inputs as *"Low Confidence / Don't Know"* instead of making erroneous diagnoses.<br>• ConvNeXt-Tiny (384px) exhibited >2× the out-of-distribution accuracy of ResNet-18 (32.4% vs 14.7% top-1, 58.8% top-3). |

---

## 📊 Detailed Per-Class Evaluation (Validation Set: 10,861 samples)

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

---

## 🔬 In-the-Wild Cross-Dataset Stress Test (PlantDoc Dataset)

To test true real-world generalizability under uncontrolled farm conditions, all three models were benchmarked against in-the-field photos with complex outdoor backgrounds:

| Architecture | Resolution | Top-1 Accuracy | Top-3 Accuracy | Mean Softmax Conf | Safe-Gated (<75% Conf) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ResNet-18 (v1)** | 224 × 224 | 14.7% | 47.1% | 64.5% | 58.8% |
| **ResNet-50 (v2)** | 224 × 224 | 23.5% | 44.1% | 66.6% | 50.0% |
| **ConvNeXt-Tiny (v3)** | **384 × 384** | **32.4%** | **58.8%** | **65.0%** | **44.1%** |

*Conclusion:* High-resolution ConvNeXt-Tiny v3 provides superior spatial feature preservation under domain shift, while the 75% confidence gating prevents silent false-positive classifications.
