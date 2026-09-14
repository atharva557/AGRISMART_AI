# Computer Vision Pipeline: Proposed Enhancements & Field-Readiness Roadmap

> **AgriSmart AI — SIH 2026** | Technical Proposal for Advancing Crop Pathology Diagnosis & Explainability

---

## 1. Executive Summary

The current core Computer Vision engine utilizes a champion **ConvNeXt-Tiny (384px)** architecture (with a baseline **ResNet-18** fallback) achieving **99.85% validation accuracy** across 38 crop pathology categories. While lab-benchmark performance is high, real-world deployment on mobile field photos presents challenges such as out-of-distribution non-plant uploads, motion blur, outdoor glare, and lack of visual interpretability.

This document outlines five high-impact enhancements to elevate the computer vision system into a robust, competition-winning, enterprise-grade diagnostic engine.

---

## 2. Proposed Technical Enhancements

```
+---------------------------------------------------------------------------------------------+
|                                 ENHANCED INFERENCE PIPELINE                                 |
+---------------------------------------------------------------------------------------------+
|  [Uploaded Photo]                                                                           |
|         │                                                                                   |
|         ▼                                                                                   |
|  [1. Quality & Blur Filter] ──(Fail: Blurry/Dark)──► Instant User Feedback ("Retake Photo") |
|         │ (Pass)                                                                            |
|         ▼                                                                                   |
|  [2. Non-Foliage / OOD Gate] ──(Fail: Non-Plant)──► Rejection ("No crop foliage detected")  |
|         │ (Pass)                                                                            |
|         ▼                                                                                   |
|  [3. Test-Time Augmentation (TTA)] ──► Multi-Angle Logit Averaging (ConvNeXt-Tiny)         |
|         │                                                                                   |
|         ▼                                                                                   |
|  [4. Grad-CAM Saliency Engine] ──► Generates Lesion Focus Heatmap Overlay                   |
|         │                                                                                   |
|         ▼                                                                                   |
|  [5. GenAI Assistant Grounding] ──► 1-Click Multi-turn Regional Q&A                         |
+---------------------------------------------------------------------------------------------+
```

---

### Enhancement 1: Explainable AI (Grad-CAM Saliency Heatmaps)

#### 🎯 Problem Statement
Deep neural networks act as black-box predictors. In hackathon evaluations and agronomic field verification, judges and agricultural experts need to verify that the model is making decisions based on actual biological symptoms (e.g., concentric fungal rings, bacterial halos) rather than background artifacts (dirt, fingers, shadow edges, or lab bench borders).

#### 🛠️ Technical Implementation
- Hook into the final convolutional stage of ConvNeXt-Tiny (`model.stages[-1].blocks[-1]`) or ResNet (`model.layer4`).
- Calculate gradients of the target class score with respect to feature activation maps:
  $$L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right)$$
  where $\alpha_k^c = \frac{1}{Z}\sum_i \sum_j \frac{\partial y^c}{\partial A_{i,j}^k}$.
- Overlay the resulting heatmap using a customized colormap onto the original leaf image and return it as a base64/URL asset to the web client.

#### 📈 Expected Impact
- **Trust & Interpretability:** Visual validation for agronomists and farmers.
- **Judge Appeal:** Demonstrates state-of-the-art Explainable AI (XAI).

---

### Enhancement 2: Out-of-Distribution (OOD) & Non-Plant Rejection Gate

#### 🎯 Problem Statement
Standard Softmax outputs are normalized probabilities that always sum to 1. If a user uploads an invalid photo (a human face, vehicle, animal, or indoor object), the model is forced to assign it to one of the 38 crop classes with arbitrary probability.

#### 🛠️ Technical Implementation
Implement a two-stage gate prior to final diagnosis:
1. **Foliage Color-Space & Vegetation Masking:** Convert to HSV/LAB color space to verify the presence of green, chlorotic yellow, or necrotic brown leaf surface area above a minimum threshold (e.g., $> 20\%$ frame coverage).
2. **Entropy Thresholding:** Calculate the Shannon entropy of the Softmax distribution:
   $$H(P) = -\sum_{i=1}^{C} P_i \log(P_i)$$
   High entropy across all classes indicates extreme uncertainty and triggers an Out-of-Distribution rejection.

#### 📈 Expected Impact
- Eliminates false positive predictions on irrelevant or non-agricultural images.
- Increases system credibility during live judge demos.

---

### Enhancement 3: Pre-Inference Image Quality & Blur Detection

#### 🎯 Problem Statement
Field conditions frequently produce blurred images from smartphone camera shake or inadequate focus, which degrades classification reliability.

#### 🛠️ Technical Implementation
Run a lightweight, millisecond-level quality check before invoking the PyTorch model:
1. **Blur Detection via Laplacian Variance:**
   $$\text{Focus Measure} = \text{Var}\left(\nabla^2 I\right)$$
   If $\text{Focus Measure} < \tau_{\text{blur}}$ (e.g., threshold of 100), reject early and prompt the user to retake the photo.
2. **Exposure & Lighting Check:** Verify mean pixel luminance is within normal range ($40 \le \bar{Y} \le 235$) to prevent processing completely dark or heavily overexposed glare shots.

#### 📈 Expected Impact
- Rejects unreadable inputs in $< 5\text{ ms}$ without consuming GPU inference resources.
- Educates farmers on capturing usable diagnostic photos.

---

### Enhancement 4: Test-Time Augmentation (TTA)

#### 🎯 Problem Statement
Outdoor leaves may be oriented at off-angles or captured under asymmetrical shadows, causing slight variance in classification confidence.

#### 🛠️ Technical Implementation
During inference, generate 4 rapid augmentations:
1. Original image
2. Horizontal flip
3. Subtle $+5^\circ$ affine rotation
4. Subtle $-5^\circ$ affine rotation

Average the predicted probability vectors:
$$P_{\text{ensemble}} = \frac{1}{N} \sum_{n=1}^{N} \text{Softmax}\left(\mathcal{M}\left(T_n(I)\right)\right)$$

#### 📈 Expected Impact
- Boosts top-1 accuracy on in-the-wild test sets (PlantDoc) by **$1.5\% - 2.5\%$**.
- Stabilizes confidence scores on edge-case symptoms.

---

### Enhancement 5: Seamless GenAI Agronomic Assistant Grounding

#### 🎯 Problem Statement
Identifying a disease is only the first step; farmers often have follow-up questions tailored to their local region, language, and budget.

#### 🛠️ Technical Implementation
- Add an interactive button on the diagnostic report:
  `[ 💬 Ask Farmer Assistant About This Disease ]`
- Clicking the button automatically seeds the **Farmer Assistant (Module E)** with the detected crop, disease, severity, and localized weather context.
- The farmer can immediately ask multi-turn follow-up questions in **Hindi, Marathi, Gujarati, Telugu, Tamil, Bengali, or English**.

#### 📈 Expected Impact
- Complete synergy between Computer Vision (Core) and GenAI Assistant (Bonus E).
- Provides end-to-end value from identification to actionable local cure.

---

## 3. Implementation Priority & Effort Matrix

| Enhancement | Difficulty | Latency Cost | Impact on Judges / Field Use | Recommended Priority |
| :--- | :--- | :--- | :--- | :--- |
| **OOD / Non-Plant Rejection** | Easy | $< 2\text{ ms}$ | High (prevents demo failures) | **Phase 1 (Immediate)** |
| **Image Quality / Blur Check** | Easy | $< 5\text{ ms}$ | High (field practicality) | **Phase 1 (Immediate)** |
| **GenAI Assistant Integration** | Easy | $0\text{ ms}$ (Frontend/API) | Very High (synergy) | **Phase 1 (Immediate)** |
| **Grad-CAM Saliency Heatmaps** | Medium | $\approx 25\text{ ms}$ | Maximum (Explainability XAI) | **Phase 2** |
| **Test-Time Augmentation (TTA)** | Easy | $\approx 35\text{ ms}$ | Moderate (+2% accuracy) | **Phase 2** |

---

## 4. Conclusion

Implementing these enhancements transitions AgriSmart AI from a standard laboratory benchmark model into a robust, explainable, and production-ready precision agriculture platform tailored for real-world Indian farm conditions.
