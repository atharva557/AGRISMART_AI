# Originality declaration and reference inventory

**Draft for team review; not a signed or verified declaration.** Repository history begins on 11 September 2026, within the brief's 10–15 September window. Commit timestamps alone cannot prove authorship or when all work was created.

Proposed declaration to confirm or correct:

> We will identify our team's work during the allowed window and disclose substantive third-party code, notebooks, datasets and pretrained models. AI coding assistance was used for implementation, documentation and verification. We distinguish historical/local results from the organizers' held-out evaluation and will not claim originality for reused components.

| Component | Reference / disclosure needed |
|---|---|
| CV backbones | PyTorch/Torchvision ResNet-18/50 and timm ConvNeXt-Tiny `convnext_tiny.fb_in22k_ft_in1k_384`. Record pretrained-weight provenance and applicable licenses. |
| Core images | PlantVillage distribution and train/validation folders. Confirm exact source/version, license and kickoff split correspondence. |
| Historical field sample | PlantDoc; benchmark code references `pratikkayal/PlantDoc-Dataset`. Document sampled files and permissions; historical script paths are machine-specific. |
| Crop dataset | `atharvaingle/crop-recommendation-dataset`, version 1. Source hashes and publisher-listed licensing are recorded in `data/README.md` and `report/bonus_modules_sources.json`. |
| Irrigation research | Mendeley `cjb4vy4mzj`, version 3; see `report/irrigation_dataset_manifest.json`. Serving uses a water-balance formula, not the experimental controller model. |
| Services | Open-Meteo, Google GenAI SDK/service and deep-translator. Retain provider attribution and review applicable use conditions. |
| Libraries | Flask, Pillow, NumPy, pandas, scikit-learn, joblib, Tailwind CSS and Webpack; see dependency files. |
| AI assistance | Code/documentation edits and automated verification. The team must review and be able to explain the submitted work. |

**Team action:** add every copied/adapted code or notebook URL, corresponding files and extent of reuse; identify team-authored contributions and confirm timeframe. This inventory cannot certify that no other third-party material was used. Do not replace it with an unsupported “entirely original” assertion.
