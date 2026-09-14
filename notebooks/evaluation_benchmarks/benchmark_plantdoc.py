import os
import time
import pickle
import json
import requests
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
import timm

IMG_DIR = r"D:\Shlok\Code\AGRISMART_AI\notebooks\cv_model_notebooks\test_images_external_datasets"
os.makedirs(IMG_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

# Mapping from PlantDoc directory names to our 38 PlantVillage classes
LABEL_MAPPING = {
    "Apple Scab Leaf": "Apple___Apple_scab",
    "Apple leaf": "Apple___healthy",
    "Apple rust leaf": "Apple___Cedar_apple_rust",
    "Bell_pepper leaf spot": "Pepper,_bell___Bacterial_spot",
    "Bell_pepper leaf": "Pepper,_bell___healthy",
    "Blueberry leaf": "Blueberry___healthy",
    "Cherry leaf": "Cherry_(including_sour)___healthy",
    "Corn Gray leaf spot": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn leaf blight": "Corn_(maize)___Northern_Leaf_Blight",
    "Corn rust leaf": "Corn_(maize)___Common_rust_",
    "grape leaf black rot": "Grape___Black_rot",
    "grape leaf": "Grape___healthy",
    "Peach leaf": "Peach___healthy",
    "Potato leaf early blight": "Potato___Early_blight",
    "Potato leaf late blight": "Potato___Late_blight",
    "Raspberry leaf": "Raspberry___healthy",
    "Soyabean leaf": "Soybean___healthy",
    "Squash Powdery mildew leaf": "Squash___Powdery_mildew",
    "Strawberry leaf": "Strawberry___healthy",
    "Tomato Early blight leaf": "Tomato___Early_blight",
    "Tomato Septoria leaf spot": "Tomato___Septoria_leaf_spot",
    "Tomato leaf bacterial spot": "Tomato___Bacterial_spot",
    "Tomato leaf late blight": "Tomato___Late_blight",
    "Tomato leaf mosaic virus": "Tomato___Tomato_mosaic_virus",
    "Tomato leaf yellow virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato leaf": "Tomato___healthy",
    "Tomato mold leaf": "Tomato___Leaf_Mold"
}

headers = {'User-Agent': 'Mozilla/5.0'}
base_api = "https://api.github.com/repos/pratikkayal/PlantDoc-Dataset/contents/test"

print("Fetching external in-the-wild dataset files (PlantDoc)...")
r = requests.get(base_api, headers=headers)
folders = r.json()

target_count = 50
downloaded_manifest = []

# Fetch images from each folder
count = 0
for folder in folders:
    if count >= target_count:
        break
    folder_name = folder['name']
    if folder_name not in LABEL_MAPPING:
        continue
    mapped_gt = LABEL_MAPPING[folder_name]
    folder_url = folder['url']
    
    fr = requests.get(folder_url, headers=headers)
    if fr.status_code != 200:
        continue
    files = [f for f in fr.json() if f['name'].lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Take up to 2 images per category to reach 50
    take = min(len(files), 2)
    selected_files = files[:take]
    
    for f_info in selected_files:
        if count >= target_count:
            break
        img_url = f_info['download_url']
        filename = f"{count+1:02d}_{folder_name.replace(' ', '_')}.jpg"
        save_path = os.path.join(IMG_DIR, filename)
        
        try:
            img_data = requests.get(img_url, headers=headers).content
            with open(save_path, "wb") as f:
                f.write(img_data)
            
            # Verify it's a readable image
            with Image.open(save_path) as test_im:
                test_im.verify()
                
            downloaded_manifest.append({
                "id": count + 1,
                "filename": filename,
                "path": save_path,
                "dataset_source": "PlantDoc (In-the-Wild / Field Condition)",
                "raw_label": folder_name,
                "ground_truth": mapped_gt
            })
            count += 1
            print(f"[{count:02d}/{target_count}] Downloaded: {filename} -> GT: {mapped_gt}")
        except Exception as e:
            if os.path.exists(save_path):
                os.remove(save_path)
            continue

# If still short of 50, fetch additional from train folder of PlantDoc
if count < target_count:
    train_api = "https://api.github.com/repos/pratikkayal/PlantDoc-Dataset/contents/train"
    tr_r = requests.get(train_api, headers=headers)
    if tr_r.status_code == 200:
        for folder in tr_r.json():
            if count >= target_count:
                break
            folder_name = folder['name']
            if folder_name not in LABEL_MAPPING:
                continue
            mapped_gt = LABEL_MAPPING[folder_name]
            fr = requests.get(folder['url'], headers=headers)
            if fr.status_code != 200:
                continue
            files = [f for f in fr.json() if f['name'].lower().endswith(('.jpg', '.jpeg', '.png'))]
            for f_info in files[:2]:
                if count >= target_count:
                    break
                img_url = f_info['download_url']
                filename = f"{count+1:02d}_{folder_name.replace(' ', '_')}_train.jpg"
                save_path = os.path.join(IMG_DIR, filename)
                try:
                    img_data = requests.get(img_url, headers=headers).content
                    with open(save_path, "wb") as f:
                        f.write(img_data)
                    with Image.open(save_path) as test_im:
                        test_im.verify()
                    downloaded_manifest.append({
                        "id": count + 1,
                        "filename": filename,
                        "path": save_path,
                        "dataset_source": "PlantDoc (In-the-Wild / Field Condition)",
                        "raw_label": folder_name,
                        "ground_truth": mapped_gt
                    })
                    count += 1
                    print(f"[{count:02d}/{target_count}] Downloaded: {filename} -> GT: {mapped_gt}")
                except Exception:
                    if os.path.exists(save_path):
                        os.remove(save_path)
                    continue

print(f"\nSuccessfully collected {len(downloaded_manifest)} external field images in {IMG_DIR}")

# 2. Model Loading
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
    print(f"Loading {name}...")
    model, bundle = load_bundle(pkl_path)
    loaded_models[name] = (model, bundle)

# 3. Predict Top-K
def predict_topk(image_path, model, bundle, k=3):
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

    topk_probs, topk_indices = torch.topk(probs, k)
    topk_preds = [(bundle["class_names"][idx.item()], prob.item()) for idx, prob in zip(topk_indices, topk_probs)]
    
    return topk_preds, latency_ms

# 4. Evaluation Loop
results = {name: {
    "correct_top1": 0,
    "correct_top3": 0,
    "total_latency": 0.0,
    "total_conf": 0.0,
    "high_conf_correct": 0,
    "high_conf_wrong": 0,
    "low_conf_gated": 0,
    "predictions": []
} for name in MODELS_CONFIG}

CONFIDENCE_THRESHOLD = 0.75
total_samples = len(downloaded_manifest)

print(f"\n--- Running Evaluation on {total_samples} External In-The-Wild Images ---")
for item in downloaded_manifest:
    img_id = item["id"]
    gt = item["ground_truth"]
    path = item["path"]
    
    row_info = [f"Img {img_id:02d} [{gt.split('___')[-1][:15]}]"]
    
    for m_name, (model, bundle) in loaded_models.items():
        topk_preds, latency = predict_topk(path, model, bundle, k=3)
        top1_label, top1_prob = topk_preds[0]
        top3_labels = [p[0] for p in topk_preds]
        
        is_top1 = (top1_label.strip() == gt.strip())
        is_top3 = any(l.strip() == gt.strip() for l in top3_labels)
        
        if is_top1:
            results[m_name]["correct_top1"] += 1
            if top1_prob >= CONFIDENCE_THRESHOLD:
                results[m_name]["high_conf_correct"] += 1
        else:
            if top1_prob >= CONFIDENCE_THRESHOLD:
                results[m_name]["high_conf_wrong"] += 1
        
        if is_top3:
            results[m_name]["correct_top3"] += 1
            
        if top1_prob < CONFIDENCE_THRESHOLD:
            results[m_name]["low_conf_gated"] += 1
            
        results[m_name]["total_latency"] += latency
        results[m_name]["total_conf"] += top1_prob
        
        results[m_name]["predictions"].append({
            "id": img_id,
            "gt": gt,
            "top1_pred": top1_label,
            "top1_conf": top1_prob,
            "top3": topk_preds,
            "latency_ms": latency,
            "is_top1": is_top1,
            "is_top3": is_top3
        })
        
        status = "TOP1" if is_top1 else ("TOP3" if is_top3 else "MISS")
        row_info.append(f"{m_name}: {status} ({top1_prob*100:.1f}%)")
    
    print(" | ".join(row_info))

# 5. Comparative Report Generation
summary_lines = []
summary_lines.append("AgriSmart AI — External Dataset (In-the-Wild) Cross-Evaluation Report")
summary_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
summary_lines.append(f"Source Dataset: PlantDoc (In-the-Field / Complex Backgrounds)")
summary_lines.append(f"Total Test Images: {total_samples}\n")

header_table = f"{'Model Architecture':<18} | {'Top-1 Acc':<10} | {'Top-3 Acc':<10} | {'Mean Conf':<11} | {'Safe Gate (<75%)':<16} | {'Avg Latency':<12}"
summary_lines.append("="*len(header_table))
summary_lines.append(header_table)
summary_lines.append("="*len(header_table))

for m_name in MODELS_CONFIG:
    res = results[m_name]
    top1_acc = (res["correct_top1"] / total_samples) * 100
    top3_acc = (res["correct_top3"] / total_samples) * 100
    mean_conf = (res["total_conf"] / total_samples) * 100
    gated_ratio = (res["low_conf_gated"] / total_samples) * 100
    avg_lat = res["total_latency"] / total_samples
    
    line = f"{m_name:<18} | {top1_acc:.1f}% ({res['correct_top1']}/{total_samples}) | {top3_acc:.1f}% ({res['correct_top3']}/{total_samples}) | {mean_conf:.1f}%{'':<5} | {gated_ratio:.1f}% ({res['low_conf_gated']}/{total_samples}){'':<4} | {avg_lat:.2f} ms"
    summary_lines.append(line)

summary_lines.append("="*len(header_table))

report_text = "\n".join(summary_lines)
print("\n" + report_text)

# Save Report File
report_file = r"D:\Shlok\Code\AGRISMART_AI\notebooks\cv_model_notebooks\model_summary_external_benchmark.txt"
with open(report_file, "w", encoding="utf-8") as f:
    f.write(report_text)
print(f"\nReport saved to: {report_file}")
