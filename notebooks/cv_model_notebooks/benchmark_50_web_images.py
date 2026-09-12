import os
import time
import pickle
import requests
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
import timm

IMG_DIR = r"D:\Shlok\Code\AGRISMART_AI\notebooks\cv_model_notebooks\test_images"
os.makedirs(IMG_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

# 1. Fetch list of image files across classes from web repository
headers = {'User-Agent': 'Mozilla/5.0'}
base_api = "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color"

print("Fetching folder structure from PlantVillage web repository...")
r = requests.get(base_api, headers=headers)
folders = r.json()

target_count = 50
downloaded_manifest = []

# Distribute target across folders
per_folder = max(1, target_count // len(folders))
print(f"Sampling ~{per_folder}-2 images per class to reach 50 images...")

count = 0
for folder in folders:
    if count >= target_count:
        break
    folder_name = folder['name']
    folder_url = folder['url']
    
    fr = requests.get(folder_url, headers=headers)
    if fr.status_code != 200:
        continue
    files = [f for f in fr.json() if f['name'].lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Pick 1 or 2 images per category
    take = 2 if count + len(folders) - folders.index(folder) <= target_count else 1
    selected_files = files[:take]
    
    for f_info in selected_files:
        if count >= target_count:
            break
        img_url = f_info['download_url']
        filename = f"{count+1:02d}_{folder_name}.jpg"
        save_path = os.path.join(IMG_DIR, filename)
        
        # Download image
        img_data = requests.get(img_url, headers=headers).content
        with open(save_path, "wb") as f:
            f.write(img_data)
        
        downloaded_manifest.append({
            "id": count + 1,
            "filename": filename,
            "path": save_path,
            "ground_truth": folder_name
        })
        count += 1
        print(f"[{count:02d}/{target_count}] Downloaded: {filename}")

print(f"\nSuccessfully downloaded {len(downloaded_manifest)} images to {IMG_DIR}")

# 2. Model Loading Function
def load_bundle(pkl_path):
    with open(pkl_path, "rb") as f:
        bundle = pickle.load(f)
    arch = bundle["architecture"].lower()
    num_classes = bundle["num_classes"]

    if "convnext_tiny" in arch:
        model = timm.create_model('convnext_tiny.fb_in22k_ft_in1k_384', pretrained=False, num_classes=num_classes)
    elif "resnet50" in arch:
        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif "resnet18" in arch:
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    else:
        raise ValueError(f"Unknown arch: {arch}")

    model.load_state_dict(bundle["state_dict"])
    model = model.to(DEVICE)
    model.eval()
    return model, bundle

MODELS_CONFIG = {
    "v1_ResNet18": r"D:\Shlok\Code\AGRISMART_AI\notebooks\cv_model_notebooks\model_v1.pkl",
    "v2_ResNet50": r"D:\Shlok\Code\AGRISMART_AI\notebooks\cv_model_notebooks\model_v2.pkl",
    "v3_ConvNeXtTiny": r"D:\Shlok\Code\AGRISMART_AI\notebooks\cv_model_notebooks\model_v3.pkl"
}

loaded_models = {}
for name, pkl_path in MODELS_CONFIG.items():
    print(f"Loading {name} from {pkl_path}...")
    model, bundle = load_bundle(pkl_path)
    loaded_models[name] = (model, bundle)

# 3. Predict helper
def predict(image_path, model, bundle):
    img = Image.open(image_path).convert("RGB")
    img_size = bundle.get("img_size", 224)
    mean = bundle.get("normalize_mean", [0.485, 0.456, 0.406])
    std = bundle.get("normalize_std", [0.229, 0.224, 0.225])

    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    tensor = transform(img).unsqueeze(0).to(DEVICE)
    
    start = time.perf_counter()
    with torch.no_grad():
        with torch.amp.autocast("cuda", enabled=(DEVICE.type == "cuda")):
            outputs = model(tensor)
            probs = F.softmax(outputs, dim=1).squeeze(0).cpu()
    latency_ms = (time.perf_counter() - start) * 1000

    top_prob, top_idx = torch.max(probs, dim=0)
    top_label = bundle["class_names"][top_idx.item()]
    return top_label, top_prob.item(), latency_ms

# 4. Evaluation Loop
results = {name: {"correct": 0, "total_latency": 0.0, "total_conf": 0.0, "predictions": []} for name in MODELS_CONFIG}

print("\n--- Running Evaluation on 50 Test Images ---")
for item in downloaded_manifest:
    img_id = item["id"]
    gt = item["ground_truth"]
    path = item["path"]
    
    row_info = [f"Image {img_id:02d} [GT: {gt}]"]
    
    for m_name, (model, bundle) in loaded_models.items():
        pred_label, conf, latency = predict(path, model, bundle)
        is_correct = (pred_label.strip() == gt.strip())
        
        if is_correct:
            results[m_name]["correct"] += 1
        results[m_name]["total_latency"] += latency
        results[m_name]["total_conf"] += conf
        results[m_name]["predictions"].append({
            "id": img_id,
            "gt": gt,
            "pred": pred_label,
            "conf": conf,
            "latency_ms": latency,
            "correct": is_correct
        })
        status_icon = "CORRECT" if is_correct else "WRONG"
        row_info.append(f"{m_name}: {status_icon} ({conf*100:.1f}%, {latency:.1f}ms)")
    
    print(" | ".join(row_info))

# 5. Summary Statistics
print("\n" + "="*80)
print(f"{'Model Architecture':<22} | {'Accuracy':<10} | {'Mean Confidence':<18} | {'Avg Latency (ms)':<16}")
print("="*80)

for m_name in MODELS_CONFIG:
    acc = (results[m_name]["correct"] / target_count) * 100
    mean_conf = (results[m_name]["total_conf"] / target_count) * 100
    avg_lat = results[m_name]["total_latency"] / target_count
    print(f"{m_name:<22} | {acc:.1f}% ({results[m_name]['correct']}/{target_count}) | {mean_conf:.2f}%{'':<11} | {avg_lat:.2f} ms")

print("="*80)
