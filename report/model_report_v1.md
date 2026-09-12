# Model Report: Model v1 — Baseline ResNet-18

**Version:** 1.0 (Baseline Architecture)  
**File Checkpoint:** `notebooks/cv_model_notebooks/model_v1.pkl` (42.8 MB)  
**Evaluation Standard:** SIH 2026 Section 7.3 One-Page Model Report

---

## 1. Executive Summary Table

| Field | Specification / Value |
| :--- | :--- |
| **Task** | Multiclass crop-disease image classification across **38 classes** (14 crop types). |
| **Dataset & Split** | **PlantVillage Dataset** (Color, leaf specimen imagery, CC0 License).<br>• Total Images: **54,305**<br>• Train Set: **43,444 images** (80.0%)<br>• Validation Set: **10,861 images** (20.0%) |
| **Model / Approach** | • **Architecture:** ResNet-18 (ImageNet pretrained backbone)<br>• **Input Resolution:** $224 \times 224 \text{ px}$<br>• **Loss Function:** Standard Cross-Entropy Loss<br>• **Optimizer:** Adam ($\text{lr} = 10^{-4}$, $\beta_1=0.9, \beta_2=0.999$)<br>• **Batch Size & Epochs:** Batch Size = 32, Trained for 10 Epochs (Best: Epoch 7) |
| **Metric & Result** | • **Macro-F1 (Primary Metric): 0.9912**<br>• **Top-1 Validation Accuracy: 99.43% (10,799 / 10,861)**<br>• **Macro Precision:** 0.9910 \| **Macro Recall:** 0.9920<br>• **Average GPU Latency:** 7.57 ms / image |
| **Baseline Comparison** | Serves as the experimental **starting baseline**. High accuracy on clean lab photos, but weaker separation on visually similar foliar spot lesions. |
| **Limitations & Failure Cases** | • **Weakest Classes:** Corn Cercospora Leaf Spot (F1: 0.9020), Corn Northern Leaf Blight (F1: 0.9540).<br>• **Overconfidence:** Unsmoothed softmax outputs saturated near 99-100% even on ambiguous inputs.<br>• **Domain Shift (PlantDoc Test):** Drops to **14.7% Top-1** on unsegmented outdoor in-field photos due to 224px feature compression and lack of background invariance. |

---

## 2. Per-Class Validation Breakdown (PlantVillage: 10,861 Samples)

```text
Class Name                                          Precision   Recall   F1-Score   Support
-------------------------------------------------------------------------------------------
Apple___Apple_scab                                     1.0000   0.9841     0.9920       126
Apple___Black_rot                                      1.0000   1.0000     1.0000       125
Apple___Cedar_apple_rust                               1.0000   1.0000     1.0000        55
Apple___healthy                                        1.0000   0.9939     0.9970       329
Blueberry___healthy                                    1.0000   1.0000     1.0000       300
Cherry_(including_sour)___Powdery_mildew               1.0000   1.0000     1.0000       210
Cherry_(including_sour)___healthy                      1.0000   0.9882     0.9940       170
Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot     0.9670   0.8450     0.9020       103
Corn_(maize)___Common_rust_                            1.0000   0.9920     0.9960       239
Corn_(maize)___Northern_Leaf_Blight                    0.9200   0.9900     0.9540       197
Corn_(maize)___healthy                                 1.0000   1.0000     1.0000       233
Grape___Black_rot                                      1.0000   0.9830     0.9910       236
Grape___Esca_(Black_Measles)                           0.9860   1.0000     0.9930       276
Grape___Leaf_blight_(Isariopsis_Leaf_Spot)             1.0000   1.0000     1.0000       215
Grape___healthy                                        1.0000   1.0000     1.0000        84
Orange___Haunglongbing_(Citrus_greening)               1.0000   0.9970     0.9990      1102
Peach___Bacterial_spot                                 0.9980   0.9960     0.9970       459
Peach___healthy                                        0.9470   1.0000     0.9730        72
Pepper,_bell___Bacterial_spot                          1.0000   1.0000     1.0000       200
Pepper,_bell___healthy                                 0.9970   1.0000     0.9980       295
Potato___Early_blight                                  1.0000   1.0000     1.0000       200
Potato___Late_blight                                   0.9950   0.9950     0.9950       200
Potato___healthy                                       0.9390   1.0000     0.9690        31
Raspberry___healthy                                    1.0000   1.0000     1.0000        74
Soybean___healthy                                      0.9990   0.9990     0.9990      1018
Squash___Powdery_mildew                                1.0000   0.9950     0.9970       367
Strawberry___Leaf_scorch                               1.0000   1.0000     1.0000       222
Strawberry___healthy                                   1.0000   1.0000     1.0000        92
Tomato___Bacterial_spot                                1.0000   0.9930     0.9960       425
Tomato___Early_blight                                  0.9710   0.9900     0.9800       200
Tomato___Late_blight                                   0.9890   0.9820     0.9860       382
Tomato___Leaf_Mold                                     1.0000   0.9950     0.9970       191
Tomato___Septoria_leaf_spot                            0.9890   1.0000     0.9940       354
Tomato___Spider_mites Two-spotted_spider_mite          0.9940   0.9910     0.9930       335
Tomato___Target_Spot                                   0.9860   0.9790     0.9820       281
Tomato___Tomato_Yellow_Leaf_Curl_Virus                 0.9960   0.9990     0.9980      1071
Tomato___Tomato_mosaic_virus                           1.0000   1.0000     1.0000        74
Tomato___healthy                                       0.9880   1.0000     0.9940       318
-------------------------------------------------------------------------------------------
Overall Accuracy                                                              0.9943     10861
Macro Average                                          0.9910   0.9920     0.9912     10861
Weighted Average                                       0.9940   0.9940     0.9940     10861
```
