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
import time

# ─── Page Configuration ───
st.set_page_config(
    page_title="CattleSense",
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
UDDER_MODEL_PATH = os.path.join(BASE_DIR, "runs", "classify", "runs", "udder_project", "udder_classification2", "weights", "best.pt")


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
    elif "Mastitis" in condition_name or "Udder" in condition_name:
        return (
            "Bovine Mastitis or Udder Disease has been detected. This bacterial infection "
            "causes inflammation of the mammary gland and udder tissue. Isolate the cow "
            "to prevent spreading during milking. Contact your veterinarian for a culture test "
            "to determine the specific bacteria and the appropriate antibiotic treatment. "
            "Ensure milking equipment is thoroughly cleaned and sanitized."
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
    elif disease_type == "fmd":
        if "Foot" in class_name or "1" in class_name:
            pretty_name = "Foot and Mouth Disease Detected"
            is_healthy = False
        else:
            pretty_name = "Healthy — No FMD Symptoms Found"
            is_healthy = True
    else:
        if "mastitis" in class_name.lower():
            pretty_name = "Bovine Mastitis Detected"
            is_healthy = False
        else:
            pretty_name = "Healthy — No Udder Disease Found"
            is_healthy = True

    probs_dict = {result.names[i]: float(result.probs.data[i]) for i in range(len(result.names))}
    
    # Calculate healthy vs unhealthy probabilities
    healthy_prob = 0.0
    unhealthy_prob = 0.0
    for c_name, prob in probs_dict.items():
        c_name_lower = c_name.lower()
        if "normal" in c_name_lower or "0" in c_name_lower:
            healthy_prob += prob
        else:
            unhealthy_prob += prob
            
    # Normalize just in case
    total = healthy_prob + unhealthy_prob
    if total > 0:
        healthy_prob /= total
        unhealthy_prob /= total

    advice = get_expert_advice(pretty_name, is_healthy)
    return pretty_name, top1_conf, is_healthy, advice, healthy_prob, unhealthy_prob


# ─── Session State ───
if "page" not in st.session_state:
    st.session_state.page = "home"
if "disease" not in st.session_state:
    st.session_state.disease = None


def go_home():
    st.session_state.page = "home"
    st.session_state.disease = None

def go_external():
    st.session_state.page = "external"
    st.session_state.disease = None

def go_internal():
    st.session_state.page = "internal"
    st.session_state.disease = None

def go_detect(disease):
    st.session_state.page = "detect"
    st.session_state.disease = disease


# ═══════════════════════════════════════════════
#                   HOME PAGE
# ═══════════════════════════════════════════════
def render_home():
    st.markdown('<div class="hero-title">🐄 CattleSense</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Select a category to begin</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="disease-card">
            <div class="card-icon">👁️</div>
            <div class="card-title">External Diseases</div>
            <div class="card-desc">Examine cattle for external diseases like FMD, LSD, and Udder Disease using Computer Vision</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore External Diseases", key="btn_ext"):
            go_external()
            st.rerun()

    with col2:
        st.markdown("""
        <div class="disease-card">
            <div class="card-icon">🫀</div>
            <div class="card-title">Internal Diseases</div>
            <div class="card-desc">Diagnose internal conditions based on clinical symptoms and physiological data</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Internal Diseases", key="btn_int"):
            go_internal()
            st.rerun()


# ═══════════════════════════════════════════════
#             EXTERNAL DISEASES PAGE
# ═══════════════════════════════════════════════
def render_external():
    if st.button("← Back to Categories", key="back_to_home_ext"):
        go_home()
        st.rerun()

    st.markdown('<div class="hero-title">🐄 External Diseases</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Select a condition to begin the examination</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

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

    with col3:
        st.markdown("""
        <div class="disease-card">
            <div class="card-icon">🐄</div>
            <div class="card-title">Udder Disease</div>
            <div class="card-desc">Inspect bovine udders for inflammation, swelling, and signs of mastitis</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Udder Examination", key="btn_udder"):
            go_detect("udder")
            st.rerun()

    # ── Stats Section ──
    st.markdown("---")
    s1, s2, s3, s4 = st.columns(4)
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
            <div class="stat-value">120</div>
            <div class="stat-label">Udder Samples</div>
        </div>
        """, unsafe_allow_html=True)
    with s4:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-value">547</div>
            <div class="stat-label">Healthy Baselines</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#             INTERNAL DISEASES PAGE
# ═══════════════════════════════════════════════
def render_internal():
    if st.button("← Back to Categories", key="back_to_home_int"):
        go_home()
        st.rerun()

    st.markdown('<div class="hero-title">🫀 Internal Diseases</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Internal disease diagnosis module</div>', unsafe_allow_html=True)
    st.info("The internal diseases module is currently under development. Stay tuned for updates!")


# ═══════════════════════════════════════════════
#               DETECTION PAGE
# ═══════════════════════════════════════════════
def render_detect():
    disease = st.session_state.disease
    if disease == "fmd":
        display_name = "Foot and Mouth Disease"
        model_path = FMD_MODEL_PATH
    elif disease == "lumpy":
        display_name = "Lumpy Skin Disease"
        model_path = LUMPY_MODEL_PATH
    else:
        display_name = "Udder Disease (Mastitis)"
        model_path = UDDER_MODEL_PATH

    # Back button
    if st.button("← Back to External Diseases", key="back_btn"):
        go_external()
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
                    prediction, confidence, is_healthy, advice, healthy_prob, unhealthy_prob = run_prediction(
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
                    
                    # ── Probability Graph Section ──
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<h3 style="color:#f8fafc; font-size:1.25rem;">Health Status Analysis</h3>', unsafe_allow_html=True)
                    
                    hist_data = [
                        ("Unhealthy (Disease Symptoms)", unhealthy_prob * 100, "#ef4444" if unhealthy_prob > healthy_prob else "#fca5a5"),
                        ("Healthy (No Symptoms)", healthy_prob * 100, "#10b981" if healthy_prob > unhealthy_prob else "#6ee7b7")
                    ]
                    
                    graph_html = '<div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.75rem; padding: 1.5rem; margin-top: 0.5rem;">'
                    for label, pct, bar_color in hist_data:
                        graph_html += f"""
<div style="margin-bottom: 0.75rem;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem; font-size: 0.9rem;">
        <span style="color: #e2e8f0;">{label}</span>
        <span style="color: #94a3b8; font-weight: 600;">{pct:.1f}%</span>
    </div>
    <div style="width: 100%; background: rgba(0, 0, 0, 0.3); border-radius: 0.25rem; height: 12px; overflow: hidden;">
        <div style="width: {pct}%; background: {bar_color}; height: 100%; border-radius: 0.25rem; transition: width 0.5s ease;"></div>
    </div>
</div>
"""
                    graph_html += '</div>'
                    
                    st.markdown(graph_html, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.4); padding: 1.25rem; border-radius: 0.75rem; border-left: 4px solid #3b82f6; margin-top: 1rem;">
                        <div style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
                            <b>Analysis Explanation:</b> This histogram groups the AI model's raw probabilities into two overall categories: 
                            <b>Healthy</b> and <b>Unhealthy</b>. 
                            The model estimates a <b>{unhealthy_prob * 100:.1f}%</b> probability that the animal exhibits symptoms of the selected disease, 
                            and a <b>{healthy_prob * 100:.1f}%</b> probability that the animal is healthy.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"An error occurred during examination: {str(e)}")

                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)


if "splashed" not in st.session_state:
    st.session_state.splashed = False

# ═══════════════════════════════════════════════
#                ROUTER
# ═══════════════════════════════════════════════
if not st.session_state.splashed:
    # Splash Screen
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        logo_path = os.path.join(BASE_DIR, "cattlesense_logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        st.markdown("<h2 style='text-align: center; color: #f8fafc;'>Initializing CattleSense...</h2>", unsafe_allow_html=True)
    time.sleep(1)
    st.session_state.splashed = True
    st.rerun()
else:
    if st.session_state.page == "home":
        render_home()
    elif st.session_state.page == "external":
        render_external()
    elif st.session_state.page == "internal":
        render_internal()
    elif st.session_state.page == "detect":
        render_detect()
