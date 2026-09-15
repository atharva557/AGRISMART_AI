"""
Confusion Matrix & Benchmark Evaluation Generator for AgriSmart AI Vision Models
Evaluates Model v1 (ResNet-18), Model v2 (ResNet-50), and Model v3 (ConvNeXt-Tiny).
Generates high-resolution confusion matrix heatmaps and comprehensive performance reports.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, f1_score, precision_score, recall_score
import torch
import torch.nn.functional as F

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from model.model_loader import _load_model_from_bundle, load_classes, DEVICE
from model.predict import get_image_transform

# Paths
CV_WEIGHTS_DIR = PROJECT_ROOT / "model" / "weights" / "cv"
TEST_IMG_DIR = PROJECT_ROOT / "notebooks" / "evaluation_benchmarks" / "test_images"
EXTERNAL_IMG_DIR = PROJECT_ROOT / "notebooks" / "evaluation_benchmarks" / "test_images_external_datasets"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

# PlantDoc dataset name mappings to 38 PlantVillage official classes
PLANTDOC_MAPPING = {
    "Apple_Scab_Leaf": "Apple___Apple_scab",
    "Apple_leaf": "Apple___healthy",
    "Apple_rust_leaf": "Apple___Cedar_apple_rust",
    "Bell_pepper_leaf_spot": "Pepper,_bell___Bacterial_spot",
    "Bell_pepper_leaf": "Pepper,_bell___healthy",
    "Blueberry_leaf": "Blueberry___healthy",
    "Cherry_leaf": "Cherry_(including_sour)___healthy",
    "Corn_Gray_leaf_spot": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_leaf_blight": "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_rust_leaf": "Corn_(maize)___Common_rust_",
    "grape_leaf_black_rot": "Grape___Black_rot",
    "grape_leaf": "Grape___healthy",
    "Peach_leaf": "Peach___healthy",
    "Potato_leaf_early_blight": "Potato___Early_blight",
    "Potato_leaf_late_blight": "Potato___Late_blight",
    "Raspberry_leaf": "Raspberry___healthy",
    "Soyabean_leaf": "Soybean___healthy",
    "Squash_Powdery_mildew_leaf": "Squash___Powdery_mildew",
    "Strawberry_leaf": "Strawberry___healthy",
    "Tomato_Early_blight_leaf": "Tomato___Early_blight",
    "Tomato_Septoria_leaf_spot": "Tomato___Septoria_leaf_spot",
    "Tomato_leaf_bacterial_spot": "Tomato___Bacterial_spot",
    "Tomato_leaf_late_blight": "Tomato___Late_blight",
    "Tomato_leaf_mosaic_virus": "Tomato___Tomato_mosaic_virus",
    "Tomato_leaf_yellow_virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato_leaf": "Tomato___healthy",
    "Tomato_mold_leaf": "Tomato___Leaf_Mold"
}


def load_test_dataset(include_external: bool = True) -> List[Tuple[Path, str]]:
    """Load benchmark dataset with ground truth labels."""
    samples = []
    classes = load_classes()
    class_set = set(classes)

    # 1. Standard PlantVillage sample test images
    if TEST_IMG_DIR.is_dir():
        for img_file in sorted(TEST_IMG_DIR.glob("*.jpg")):
            # Filename pattern: 01_Apple___Apple_scab.jpg -> Apple___Apple_scab
            parts = img_file.stem.split("_", 1)
            if len(parts) == 2:
                raw_label = parts[1]
                if raw_label in class_set:
                    samples.append((img_file, raw_label))

    # 2. External PlantDoc in-the-wild test images
    if include_external and EXTERNAL_IMG_DIR.is_dir():
        for img_file in sorted(EXTERNAL_IMG_DIR.glob("*.jpg")):
            parts = img_file.stem.split("_", 1)
            if len(parts) == 2:
                key = parts[1]
                mapped_label = PLANTDOC_MAPPING.get(key)
                if mapped_label and mapped_label in class_set:
                    samples.append((img_file, mapped_label))

    return samples


def evaluate_model(model_name: str, checkpoint_file: str, dataset: List[Tuple[Path, str]], classes: List[str]) -> Dict[str, Any]:
    """Run full evaluation on a specific model checkpoint."""
    ckpt_path = CV_WEIGHTS_DIR / checkpoint_file
    if not ckpt_path.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")

    print(f"\n==========================================")
    print(f" Loading & Evaluating {model_name}...")
    print(f" Checkpoint: {ckpt_path.name}")
    print(f"==========================================")

    model, bundle = _load_model_from_bundle(ckpt_path)
    model.eval()

    img_size = bundle.get("img_size", 384)
    mean = bundle.get("normalize_mean", [0.485, 0.456, 0.406])
    std = bundle.get("normalize_std", [0.229, 0.224, 0.225])
    transform = get_image_transform(img_size, mean, std)

    class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}

    y_true = []
    y_pred = []
    top3_correct = 0
    latencies = []

    for img_path, true_label in dataset:
        with Image.open(img_path) as img:
            image = ImageOps.exif_transpose(img).convert("RGB")
            tensor = transform(image).unsqueeze(0).to(DEVICE)

        start = time.perf_counter()
        with torch.no_grad():
            with torch.amp.autocast(DEVICE.type, enabled=(DEVICE.type == "cuda")):
                logits = model(tensor)
                probs = F.softmax(logits, dim=1).squeeze(0).cpu()
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)

        top1_idx = torch.argmax(probs).item()
        top3_indices = torch.topk(probs, k=min(3, len(probs))).indices.tolist()

        pred_label = classes[top1_idx]
        true_idx = class_to_idx[true_label]

        y_true.append(true_label)
        y_pred.append(pred_label)

        if true_idx in top3_indices:
            top3_correct += 1

    # Metrics calculation
    accuracy = accuracy_score(y_true, y_pred)
    top3_acc = top3_correct / len(dataset) if dataset else 0.0
    macro_precision = precision_score(y_true, y_pred, zero_division=0, average="macro")
    macro_recall = recall_score(y_true, y_pred, zero_division=0, average="macro")
    macro_f1 = f1_score(y_true, y_pred, zero_division=0, average="macro")
    weighted_f1 = f1_score(y_true, y_pred, zero_division=0, average="weighted")
    avg_latency = float(np.mean(latencies))

    # Present classes in evaluation
    unique_classes = sorted(list(set(y_true + y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=unique_classes)

    print(f"Top-1 Accuracy:     {accuracy * 100:.2f}% ({sum(np.array(y_true) == np.array(y_pred))}/{len(dataset)})")
    print(f"Top-3 Accuracy:     {top3_acc * 100:.2f}%")
    print(f"Macro F1-Score:     {macro_f1:.4f}")
    print(f"Avg Inference Time: {avg_latency:.2f} ms")

    return {
        "model_name": model_name,
        "checkpoint": checkpoint_file,
        "architecture": bundle.get("architecture", "unknown"),
        "img_size": img_size,
        "total_samples": len(dataset),
        "accuracy": round(float(accuracy), 4),
        "top3_accuracy": round(float(top3_acc), 4),
        "macro_precision": round(float(macro_precision), 4),
        "macro_recall": round(float(macro_recall), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "avg_latency_ms": round(avg_latency, 2),
        "confusion_matrix": cm.tolist(),
        "evaluated_classes": unique_classes,
        "y_true": y_true,
        "y_pred": y_pred,
    }


def plot_single_confusion_matrix(result: Dict[str, Any], save_path: Path):
    """Plot and save a standalone confusion matrix heatmap."""
    classes = result["evaluated_classes"]
    cm = np.array(result["confusion_matrix"])

    # Clean short labels for readable plot axes
    short_labels = [c.replace("___", "\n").replace("_", " ") for c in classes]

    plt.figure(figsize=(14, 12))
    sns.set_theme(style="white")

    ax = sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=short_labels,
        yticklabels=short_labels,
        cbar=True,
        linewidths=0.5,
        linecolor="#e0e0e0"
    )

    plt.title(
        f"Confusion Matrix — {result['model_name']} ({result['architecture'].upper()})\n"
        f"Top-1 Accuracy: {result['accuracy']*100:.1f}% | Top-3 Accuracy: {result['top3_accuracy']*100:.1f}% | Macro F1: {result['macro_f1']:.3f}",
        fontsize=14,
        fontweight="bold",
        pad=20
    )
    plt.xlabel("Predicted Class", fontsize=12, fontweight="bold", labelpad=10)
    plt.ylabel("True Ground-Truth Class", fontsize=12, fontweight="bold", labelpad=10)
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_comparison_confusion_matrices(results: List[Dict[str, Any]], save_path: Path):
    """Plot all 3 models side-by-side in a comparative multi-panel figure."""
    n_models = len(results)
    fig, axes = plt.subplots(1, n_models, figsize=(8 * n_models, 9))
    if n_models == 1:
        axes = [axes]

    for ax, res in zip(axes, results):
        classes = res["evaluated_classes"]
        cm = np.array(res["confusion_matrix"])
        short_labels = [c.split("___")[-1][:12] for c in classes]

        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="YlGnBu" if "v3" in res["model_name"].lower() else "Blues",
            xticklabels=short_labels,
            yticklabels=short_labels,
            cbar=False,
            ax=ax,
            linewidths=0.3,
            annot_kws={"size": 7}
        )
        ax.set_title(
            f"{res['model_name']}\nAccuracy: {res['accuracy']*100:.1f}% | Latency: {res['avg_latency_ms']}ms",
            fontsize=12,
            fontweight="bold"
        )
        ax.set_xlabel("Predicted", fontsize=10)
        ax.set_ylabel("Ground Truth", fontsize=10)
        ax.tick_params(axis='x', rotation=90, labelsize=7)
        ax.tick_params(axis='y', rotation=0, labelsize=7)

    plt.suptitle("AgriSmart AI — Computer Vision Model Performance Comparison", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def generate_accuracy_bar_chart(results: List[Dict[str, Any]], save_path: Path):
    """Plot an overall comparison bar chart for all models."""
    models = [r["model_name"] for r in results]
    top1_acc = [r["accuracy"] * 100 for r in results]
    top3_acc = [r["top3_accuracy"] * 100 for r in results]
    f1_scores = [r["macro_f1"] * 100 for r in results]
    latencies = [r["avg_latency_ms"] for r in results]

    x = np.arange(len(models))
    width = 0.25

    fig, ax1 = plt.subplots(figsize=(10, 6))

    rects1 = ax1.bar(x - width, top1_acc, width, label='Top-1 Accuracy (%)', color='#2b5c8f')
    rects2 = ax1.bar(x, top3_acc, width, label='Top-3 Accuracy (%)', color='#4682b4')
    rects3 = ax1.bar(x + width, f1_scores, width, label='Macro F1-Score (%)', color='#2e8b57')

    ax1.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
    ax1.set_title('CV Model Performance Benchmark Summary', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=11, fontweight='bold')
    ax1.set_ylim(0, 115)
    ax1.legend(loc='upper left')
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    # Add values on top of bars
    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            ax1.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def main():
    classes = load_classes()
    dataset = load_test_dataset(include_external=True)

    print(f"Loaded {len(dataset)} test images across {len(set(label for _, label in dataset))} unique classes.")
    if not dataset:
        print("No test images found to evaluate.")
        return

    model_configs = [
        ("Model v1 (ResNet-18)", "model_v1.pkl.gz"),
        ("Model v2 (ResNet-50)", "model_v2.pkl.gz"),
        ("Model v3 (ConvNeXt-Tiny)", "model_v3.pkl.gz"),
    ]

    results = []
    for model_name, ckpt_file in model_configs:
        res = evaluate_model(model_name, ckpt_file, dataset, classes)
        results.append(res)

        # Plot individual confusion matrix
        safe_name = model_name.lower().split()[1].replace("(", "").replace(")", "").replace("-", "_")
        single_plot_path = FIGURES_DIR / f"confusion_matrix_{safe_name}.png"
        plot_single_confusion_matrix(res, single_plot_path)

    # Plot multi-model comparative matrix
    comp_plot_path = FIGURES_DIR / "confusion_matrix_comparison_all_models.png"
    plot_comparison_confusion_matrices(results, comp_plot_path)

    # Plot benchmark comparison bar chart
    bar_chart_path = FIGURES_DIR / "cv_models_benchmark_comparison.png"
    generate_accuracy_bar_chart(results, bar_chart_path)

    # Save metrics JSON report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_test_images": len(dataset),
        "device": str(DEVICE),
        "models": [
            {k: v for k, v in r.items() if k not in ("y_true", "y_pred", "confusion_matrix")}
            for r in results
        ]
    }

    report_path = METRICS_DIR / "cv_models_evaluation_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved comprehensive metrics report to {report_path}")

    # Print summary table
    print("\n" + "=" * 80)
    print("                 BENCHMARK SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Model':<25} | {'Architecture':<15} | {'Top-1 Acc':<10} | {'Top-3 Acc':<10} | {'Macro F1':<10} | {'Latency':<10}")
    print("-" * 80)
    for r in results:
        print(f"{r['model_name']:<25} | {r['architecture']:<15} | {r['accuracy']*100:>8.2f}% | {r['top3_accuracy']*100:>8.2f}% | {r['macro_f1']:>10.4f} | {r['avg_latency_ms']:>7.2f} ms")
    print("=" * 80)


if __name__ == "__main__":
    main()
