import subprocess
import sys
import os

# ─── Streamlit Cloud Fix: Force headless OpenCV ───
# ultralytics pulls in opencv-python (full) which needs libGL.so.1
# Streamlit Cloud doesn't have that system library, so we swap to headless
if os.path.exists("/mount/src"):  # Only runs on Streamlit Cloud
    subprocess.run(
        [sys.executable, "-m", "pip", "install",
         "opencv-python-headless", "-q", "--force-reinstall", "--no-deps"],
        capture_output=True
    )

import streamlit as st
from ultralytics import YOLO
from PIL import Image
import tempfile

# ─── Page Configuration ───
st.set_page_config(
    page_title="Bovine Disease Diagnostic Center",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───
st.markdown("""
<style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    }

    /* Hide default Streamlit elements */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 1200px; }

    /* ── Hero Section ── */
    .hero-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        text-align: center;
        font-size: 1.15rem;
        color: #94a3b8;
        margin-bottom: 3rem;
        font-weight: 400;
    }

    /* ── Disease Cards ── */
    .disease-card {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1.25rem;
        padding: 2.5rem 2rem;
        text-align: center;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .disease-card:hover {
        border-color: #3b82f6;
        transform: translateY(-6px);
        box-shadow: 0 20px 40px -12px rgba(59, 130, 246, 0.2);
    }
    .card-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    .card-desc {
        font-size: 0.95rem;
        color: #94a3b8;
        line-height: 1.6;
    }

    /* ── Detection Page ── */
    .detect-header {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.25rem;
    }
    .detect-sub {
        text-align: center;
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* ── Results ── */
    .result-box {
        border-radius: 1rem;
        padding: 1.75rem;
        margin-top: 1.5rem;
        animation: fadeUp 0.5s ease;
    }
    .result-positive {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .result-negative {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .result-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .result-positive .result-title { color: #f87171; }
    .result-negative .result-title { color: #34d399; }
    .result-advice {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    .confidence-badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.75rem;
    }
    .result-positive .confidence-badge {
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
    }
    .result-negative .confidence-badge {
        background: rgba(16, 185, 129, 0.15);
        color: #6ee7b7;
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ── Buttons ── */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.85rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px -8px rgba(59, 130, 246, 0.5);
    }

    /* ── Back button ── */
    .back-link {
        color: #64748b;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.95rem;
        transition: color 0.2s;
    }
    .back-link:hover { color: #3b82f6; }

    /* ── Upload area ── */
    [data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.5);
        border: 2px dashed rgba(255, 255, 255, 0.12);
        border-radius: 1rem;
        padding: 1rem;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(59, 130, 246, 0.4);
    }

    /* ── Divider ── */
    hr { border-color: rgba(255, 255, 255, 0.06) !important; }

    /* ── Stats ── */
    .stat-box {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 0.75rem;
        padding: 1.25rem;
        text-align: center;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #3b82f6;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Model Loading ───
@st.cache_resource
def load_model(model_path):
    """Load a YOLO model with caching."""
    if os.path.exists(model_path):
        return YOLO(model_path)
    return None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LUMPY_MODEL_PATH = os.path.join(BASE_DIR, "runs", "lumpy_classification", "weights", "best.pt")
FMD_MODEL_PATH = os.path.join(BASE_DIR, "runs", "fmd_project", "fmd_classification", "weights", "best.pt")


# ─── Expert Advice (Local — no external API needed) ───
def get_expert_advice(condition_name, is_healthy):
    """Generate expert veterinary advice based on the detected condition."""
    if is_healthy:
        return (
            "The animal appears to be in good health based on the visual examination. "
            "Continue routine monitoring, maintain vaccination schedules, and ensure "
            "proper nutrition and hygiene. Regular veterinary check-ups are recommended "
            "to keep the herd healthy."
        )

    if "Lumpy" in condition_name:
        return (
            "Lumpy Skin Disease (LSD) symptoms have been detected. Immediately isolate "
            "the affected animal from the rest of the herd to prevent spread. Contact your "
            "local veterinary authority for confirmation and treatment. LSD is transmitted "
            "by biting insects — use insect repellents and control vectors around the farm. "
            "Supportive care includes wound management and anti-inflammatory medication "
            "as prescribed by your veterinarian."
        )
    elif "Foot" in condition_name:
        return (
            "Foot and Mouth Disease (FMD) symptoms have been detected. This is a highly "
            "contagious viral disease. Quarantine the affected animal immediately and notify "
            "your local veterinary services — FMD is a reportable disease in most countries. "
            "Do not move animals in or out of the premises. Disinfect all equipment, clothing, "
            "and vehicles. Provide soft feed and clean water to the affected animal. Follow "
            "your veterinarian's guidance on treatment and vaccination of the herd."
        )
    else:
        return (
            "An abnormal condition has been detected. Please isolate the animal as a "
            "precaution and consult a qualified veterinarian for a thorough examination "
            "and accurate diagnosis."
        )


# ─── Prediction Logic ───
def run_prediction(model, image_path, disease_type):
    """Run YOLO classification and return structured results."""
    results = model.predict(source=image_path, conf=0.25)
    result = results[0]
    top1_idx = result.probs.top1
    top1_conf = float(result.probs.top1conf)
    class_name = result.names[top1_idx]

    if disease_type == "lumpy":
        if "Lumpy" in class_name:
            pretty_name = "Lumpy Skin Disease Detected"
            is_healthy = False
        else:
            pretty_name = "Healthy — No LSD Symptoms Found"
            is_healthy = True
    else:
        if "Foot" in class_name or "1" in class_name:
            pretty_name = "Foot and Mouth Disease Detected"
            is_healthy = False
        else:
            pretty_name = "Healthy — No FMD Symptoms Found"
            is_healthy = True

    advice = get_expert_advice(pretty_name, is_healthy)
    return pretty_name, top1_conf, is_healthy, advice


# ─── Session State ───
if "page" not in st.session_state:
    st.session_state.page = "home"
if "disease" not in st.session_state:
    st.session_state.disease = None


def go_home():
    st.session_state.page = "home"
    st.session_state.disease = None

def go_detect(disease):
    st.session_state.page = "detect"
    st.session_state.disease = disease


# ═══════════════════════════════════════════════
#                   HOME PAGE
# ═══════════════════════════════════════════════
def render_home():
    st.markdown('<div class="hero-title">🐄 Bovine Disease Diagnostic Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Select a condition to begin the examination</div>', unsafe_allow_html=True)

    col1, spacer, col2 = st.columns([1, 0.15, 1])

    with col1:
        st.markdown("""
        <div class="disease-card">
            <div class="card-icon">🦶</div>
            <div class="card-title">Foot and Mouth Disease</div>
            <div class="card-desc">Examine cattle for vesicular lesions on the mouth, tongue, hooves, and teats</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start FMD Examination", key="btn_fmd"):
            go_detect("fmd")
            st.rerun()

    with col2:
        st.markdown("""
        <div class="disease-card">
            <div class="card-icon">🔬</div>
            <div class="card-title">Lumpy Skin Disease</div>
            <div class="card-desc">Analyze cattle skin surfaces for firm nodules, lesions, and pathological changes</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start LSD Examination", key="btn_lsd"):
            go_detect("lumpy")
            st.rerun()

    # ── Stats Section ──
    st.markdown("---")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-value">323</div>
            <div class="stat-label">Lumpy Skin Samples</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-value">212</div>
            <div class="stat-label">FMD Samples</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-value">487</div>
            <div class="stat-label">Healthy Baselines</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#               DETECTION PAGE
# ═══════════════════════════════════════════════
def render_detect():
    disease = st.session_state.disease
    display_name = "Foot and Mouth Disease" if disease == "fmd" else "Lumpy Skin Disease"
    model_path = FMD_MODEL_PATH if disease == "fmd" else LUMPY_MODEL_PATH

    # Back button
    if st.button("← Back to Selection", key="back_btn"):
        go_home()
        st.rerun()

    st.markdown(f'<div class="detect-header">Diagnostic Center</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="detect-sub">Examining for: {display_name}</div>', unsafe_allow_html=True)

    # Load model
    model = load_model(model_path)
    if model is None:
        st.error(f"⚠️ The {display_name} model is not yet available. Please ensure training is complete.")
        return

    # ── Upload Section ──
    uploaded_file = st.file_uploader(
        "Upload a sample image for examination",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        help="Supported formats: JPG, JPEG, PNG, BMP, WEBP"
    )

    if uploaded_file is not None:
        # Show preview
        image = Image.open(uploaded_file)
        col_img, col_info = st.columns([1.2, 1])

        with col_img:
            st.image(image, caption="Uploaded Sample", use_container_width=True)

        with col_info:
            st.markdown(f"""
            <div class="stat-box" style="margin-bottom: 1rem;">
                <div class="stat-label">File Name</div>
                <div style="color: #e2e8f0; font-weight: 500;">{uploaded_file.name}</div>
            </div>
            <div class="stat-box" style="margin-bottom: 1rem;">
                <div class="stat-label">Dimensions</div>
                <div style="color: #e2e8f0; font-weight: 500;">{image.width} × {image.height} px</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Examining For</div>
                <div style="color: #3b82f6; font-weight: 600;">{display_name}</div>
            </div>
            """, unsafe_allow_html=True)

        # Run examination
        if st.button("🔍 Run Examination", key="run_btn"):
            with st.spinner("Analyzing sample..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                try:
                    prediction, confidence, is_healthy, advice = run_prediction(
                        model, tmp_path, disease
                    )

                    # Display result
                    result_class = "result-negative" if is_healthy else "result-positive"
                    icon = "✅" if is_healthy else "⚠️"

                    st.markdown(f"""
                    <div class="result-box {result_class}">
                        <div class="result-title">{icon} {prediction}</div>
                        <div class="confidence-badge">Confidence: {confidence * 100:.1f}%</div>
                        <hr style="border-color: rgba(255,255,255,0.08); margin: 1rem 0;">
                        <div style="color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">Expert Veterinary Guidance</div>
                        <div class="result-advice">{advice}</div>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"An error occurred during examination: {str(e)}")

                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)


# ═══════════════════════════════════════════════
#                ROUTER
# ═══════════════════════════════════════════════
if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "detect":
    render_detect()
