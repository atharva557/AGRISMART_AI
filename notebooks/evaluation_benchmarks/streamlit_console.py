import os
import time
import pickle
from PIL import Image
import streamlit as st
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
import timm

# Page setup
st.set_page_config(
    page_title="AgriSmart AI — Diagnostic Evaluation Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal clean styling
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 1rem;
    }
    .metric-card-alert {
        background-color: #fffbeb;
        border: 1px solid #fef3c7;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 1rem;
    }
    .metric-header {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 4px;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-value-alert {
        font-size: 1.35rem;
        font-weight: 700;
        color: #b45309;
    }
    .metric-subtext {
        font-size: 0.85rem;
        color: #475569;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CONFIDENCE_THRESHOLD = 0.75

AVAILABLE_MODELS = {
    "v3: ConvNeXt-Tiny (384px, State-of-the-Art)": {
        "file": "model_v3.pkl",
        "benchmark_f1": "0.9969",
        "benchmark_acc": "99.85%"
    },
    "v2: ResNet-50 (224px, Label Smoothing)": {
        "file": "model_v2.pkl",
        "benchmark_f1": "0.9946",
        "benchmark_acc": "99.67%"
    },
    "v1: ResNet-18 (224px, Baseline)": {
        "file": "model_v1.pkl",
        "benchmark_f1": "0.9912",
        "benchmark_acc": "99.43%"
    }
}


@st.cache_resource
def load_bundle(pkl_path: str):
    if not os.path.exists(pkl_path):
        return None, None
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
        raise ValueError(f"Unknown architecture: {arch}")

    model.load_state_dict(bundle["state_dict"])
    model = model.to(DEVICE)
    model.eval()
    return model, bundle


def predict_top1(image: Image.Image, model, bundle):
    img_size = bundle.get("img_size", 224)
    mean = bundle.get("normalize_mean", [0.485, 0.456, 0.406])
    std = bundle.get("normalize_std", [0.229, 0.224, 0.225])

    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    img_tensor = transform(image.convert("RGB")).unsqueeze(0).to(DEVICE)

    start_time = time.perf_counter()
    with torch.no_grad():
        with torch.amp.autocast("cuda", enabled=(DEVICE.type == "cuda")):
            outputs = model(img_tensor)
            probs = F.softmax(outputs, dim=1).squeeze(0).cpu()
    latency_ms = (time.perf_counter() - start_time) * 1000

    top_prob, top_idx = torch.max(probs, dim=0)
    top_label = bundle["class_names"][top_idx.item()]

    return top_label, top_prob.item(), latency_ms


# Header
st.title("Plant Pathology Inference & Benchmark Console")
st.markdown("Single-prediction diagnostic engine with automated confidence filtering.")
st.divider()

# Sidebar: System Configuration & Metadata
st.sidebar.markdown("### System Configuration")
selected_label = st.sidebar.selectbox("Active Checkpoint", list(AVAILABLE_MODELS.keys()))
model_meta = AVAILABLE_MODELS[selected_label]
def resolve_model_path(filename: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    weights_path = os.path.join(base_dir, "model", "weights", "cv", filename)
    if os.path.exists(weights_path):
        return weights_path
    if os.path.exists(filename):
        return filename
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

model_file = resolve_model_path(model_meta["file"])

st.sidebar.markdown("---")
st.sidebar.markdown("### Model Metadata")
st.sidebar.text(f"Compute Device: {str(DEVICE).upper()}")
st.sidebar.text(f"Target Checkpoint: {os.path.basename(model_file)}")
st.sidebar.text(f"Confidence Floor: {CONFIDENCE_THRESHOLD * 100:.0f}%")
st.sidebar.text(f"Reported Val F1: {model_meta['benchmark_f1']}")
st.sidebar.text(f"Reported Val Acc: {model_meta['benchmark_acc']}")

if os.path.exists(model_file):
    size_mb = os.path.getsize(model_file) / (1024 * 1024)
    st.sidebar.text(f"File Size: {size_mb:.1f} MB")
else:
    st.sidebar.error(f"Status: File '{os.path.basename(model_file)}' not found in model/weights/cv/.")

# Main Interface
col1, col2 = st.columns([1, 1.4], gap="large")

with col1:
    st.markdown("### Input Sample")
    uploaded_file = st.file_uploader(
        "Upload specimen image",
        type=["jpg", "jpeg", "png"],
        help="Standard JPG or PNG crop leaf imagery."
    )
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Specimen Image", use_container_width=True)

with col2:
    st.markdown("### Diagnostic Output")
    if uploaded_file is None:
        st.info("Awaiting image input. Provide a leaf specimen file to execute classification.")
    else:
        model, bundle = load_bundle(model_file)
        if model is None:
            st.error(f"Failed to load checkpoint '{model_file}'. Verify file location.")
        else:
            with st.spinner("Executing inference pass..."):
                top_label, top_prob, latency_ms = predict_top1(image, model, bundle)

            # Format raw label string into clean readable text
            if "___" in top_label:
                crop, condition = top_label.split("___", 1)
            else:
                crop, condition = "Specimen", top_label

            crop_clean = crop.replace("_", " ")
            condition_clean = condition.replace("_", " ")
            clean_prediction_name = f"{crop_clean} — {condition_clean}"

            # Conditional rendering based on confidence threshold
            if top_prob < CONFIDENCE_THRESHOLD:
                st.markdown(f"""
                <div class="metric-card-alert">
                    <div class="metric-header">Low Confidence Diagnosis</div>
                    <div class="metric-value-alert">Don't Know (Possible: {clean_prediction_name})</div>
                    <div class="metric-subtext">Peak candidate score is <b>{top_prob * 100:.2f}%</b> (below the <b>{CONFIDENCE_THRESHOLD * 100:.0f}%</b> threshold). &nbsp;|&nbsp; Latency: <b>{latency_ms:.2f} ms</b></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-header">Confirmed Diagnosis</div>
                    <div class="metric-value">{clean_prediction_name}</div>
                    <div class="metric-subtext">Confidence Score: <b>{top_prob * 100:.2f}%</b> &nbsp;|&nbsp; Latency: <b>{latency_ms:.2f} ms</b> &nbsp;|&nbsp; Input Res: <b>{bundle['img_size']}x{bundle['img_size']}px</b></div>
                </div>
                """, unsafe_allow_html=True)