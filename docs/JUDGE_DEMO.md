# Four-minute judge demo

**Recording URL: pending.** This is a script, not a completed video. Show actual observed outputs, and do not present staged examples as independent model evaluation.

Prepare the running application, a permitted clear leaf photograph, a deliberately blank/too-small photo and the model report. Use the explicitly simulated weather mode if offline. Verify regional-language output before showing it as working; English templates can run without live generation.

| Time | Show | Suggested narration |
|---|---|---|
| 0:00–0:25 | Disease page | “AgriSmart helps a farmer inspect a leaf photo and decide what to do next. Generalizing to field images is the main challenge, so a model match is not a confirmed diagnosis.” |
| 0:25–1:05 | Choose the known crop, upload a clear leaf, analyse | “The saved model is running on this image. We preserve its raw label for evaluation and show a possible match or verification steps.” Read the actual result. |
| 1:05–1:35 | Repeat with explicitly simulated Pune weather | “This scan includes a labelled weather example, with its source and valid time window. Alerts do not confirm disease or prescribe water volume.” Use a live forecast instead only if actually available. |
| 1:35–2:05 | Assistant follow-up about weather or precautions; optional language switch | “The assistant uses this scan and weather without entering them twice. Live generation has a template fallback; grounding does not guarantee every answer is correct.” |
| 2:05–2:35 | Blank/tiny image; selected-crop mismatch if prediction differs | “Unusable photos get specific retake steps. Low scores and crop mismatch withhold disease-specific guidance in both the page and assistant.” This is not semantic non-plant detection. |
| 2:35–3:10 | Irrigation advanced inputs and sustainability comparison | “These are assumed-value demonstrations. The resource score compares water, electricity and nitrogen per hectare and includes a yield safeguard. Computed differences are not measured savings caused by our software.” |
| 3:10–3:45 | Model report; independent evaluation output if available | “Historical lab validation was 99.85% accuracy. A small historical field sample was 11 of 34 correct. Official field macro-F1 is pending. Our tooling records per-class metrics and mistakes even among high-score predictions.” Do not show fixture-test numbers as model performance. |
| 3:45–4:00 | Exact-label CLI and README | “Judges can load the included weights with one command. Our next model work is improving field generalization and independently validating photo/uncertainty handling.” |

Record the 3–5-minute video and add a judge-accessible URL to the README and checklist. Check viewing permissions. No upload or publication has been performed.
