import subprocess
import sys
import os
import re

# ─── Streamlit Cloud Fix: Force headless OpenCV ───
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
import pickle
import pandas as pd

# ─── Page Configuration ───
st.set_page_config(
    page_title="CattleSense — AI Bovine Diagnostic Platform",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Helper for Clean HTML Rendering (Strips Markdown Code-Block Indentation) ───
def render_html(html_str):
    cleaned = re.sub(r'^[ \t]+', '', html_str, flags=re.MULTILINE)
    st.markdown(cleaned.strip(), unsafe_allow_html=True)


# ─── Luxury Dark Green & White Design System (CSS) ───
render_html("""
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Manrope:wght@600;700;800&display=swap');

    /* ── Global Styles ── */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0E2B23 0%, #15392F 50%, #0E2B23 100%);
        background-attachment: fixed;
    }

    /* Hide default Streamlit overhead */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1200px;
    }

    /* ── Top Navigation Bar ── */
    .top-nav {
        background: rgba(14, 43, 35, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 0.75rem 1.5rem;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .nav-brand {
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        font-size: 1.35rem;
        color: #FFFFFF;
    }
    .nav-brand span {
        color: #34D399;
    }

    /* ── Hero Titles ── */
    .hero-title {
        font-family: 'Manrope', sans-serif;
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

    /* ── Seamless Equal-Height White Card Wrapper ── */
    .home-card-top {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-bottom: none !important;
        border-top-left-radius: 24px !important;
        border-top-right-radius: 24px !important;
        padding: 2.25rem 1.5rem 1rem 1.5rem !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        height: 240px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
        box-sizing: border-box !important;
    }

    .home-card-bottom {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-top: none !important;
        border-bottom-left-radius: 24px !important;
        border-bottom-right-radius: 24px !important;
        padding: 0 1.5rem 2rem 1.5rem !important;
        box-shadow: 0 15px 30px -5px rgba(0, 0, 0, 0.15) !important;
        box-sizing: border-box !important;
    }

    .card-icon {
        font-size: 3.25rem;
        margin-bottom: 0.75rem;
        line-height: 1;
    }
    .card-title {
        font-family: 'Manrope', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.5rem;
    }
    .card-desc {
        font-size: 0.92rem;
        color: #4B5563;
        line-height: 1.55;
    }

    /* ── Category Screen Cards ── */
    .cat-card-top {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-bottom: none !important;
        border-top-left-radius: 24px !important;
        border-top-right-radius: 24px !important;
        padding: 2.25rem 1.5rem 1rem 1.5rem !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        height: 250px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
        box-sizing: border-box !important;
    }

    .cat-card-bottom {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-top: none !important;
        border-bottom-left-radius: 24px !important;
        border-bottom-right-radius: 24px !important;
        padding: 0 1.5rem 2rem 1.5rem !important;
        box-shadow: 0 15px 30px -5px rgba(0, 0, 0, 0.15) !important;
        box-sizing: border-box !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 0.85rem 1.5rem !important;
        font-size: 0.98rem !important;
        font-weight: 700 !important;
        font-family: 'Manrope', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35) !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important;
    }

    .sec-button button {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #F8FAFC !important;
        box-shadow: none !important;
        font-weight: 600 !important;
    }
    .sec-button button:hover {
        background: rgba(255, 255, 255, 0.16) !important;
        border-color: #34D399 !important;
        color: #34D399 !important;
    }

    /* ── Header Detection Texts ── */
    .detect-header {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.25rem;
        font-family: 'Manrope', sans-serif;
    }
    .detect-sub {
        text-align: center;
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* ── White Stat Cards ── */
    .stat-box {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .stat-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #059669;
        font-family: 'Manrope', sans-serif;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        margin-top: 0.25rem;
    }

    /* ── Chatbot UI Box ── */
    .chat-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }

    /* ── File Uploader Override ── */
    [data-testid="stFileUploader"] {
        background: #FFFFFF !important;
        border: 2px dashed #10B981 !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06) !important;
    }
    [data-testid="stFileUploader"] label {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    /* ── Results Box ── */
    .result-box {
        border-radius: 20px;
        padding: 1.75rem;
        margin-top: 1.5rem;
        background: #FFFFFF;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        color: #1F2937;
    }
    .result-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-family: 'Manrope', sans-serif;
    }
    .result-positive .result-title { color: #DC2626; }
    .result-negative .result-title { color: #059669; }
    .result-advice {
        color: #374151;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    .confidence-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    .result-positive .confidence-badge {
        background: #FEE2E2;
        color: #991B1B;
    }
    .result-negative .confidence-badge {
        background: #D1FAE5;
        color: #065F46;
    }

    hr { border-color: rgba(255, 255, 255, 0.1) !important; }
</style>
""")


# ─── Navigation Header Component ───
def render_navbar():
    render_html("""
    <div style="background: rgba(14, 43, 35, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 0.75rem 1.5rem; margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between;">
        <div style="font-family: 'Manrope', sans-serif; font-weight: 800; font-size: 1.35rem; color: #FFFFFF;">
            🐄 <span style="color: #34D399;">CattleSense</span>
        </div>
    </div>
    """)
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 1])
    with col_nav1:
        render_html('<div class="sec-button">')
        if st.button("🏠 Home", key="nav_home"):
            go_home()
            st.rerun()
        render_html('</div>')
    with col_nav2:
        render_html('<div class="sec-button">')
        if st.button("👁️ External", key="nav_ext"):
            go_external()
            st.rerun()
        render_html('</div>')
    with col_nav3:
        render_html('<div class="sec-button">')
        if st.button("🫀 Internal", key="nav_int"):
            go_internal()
            st.rerun()
        render_html('</div>')
    with col_nav4:
        render_html('<div class="sec-button">')
        if st.button("💬 Chatbot", key="nav_chat"):
            go_chatbot()
            st.rerun()
        render_html('</div>')
    render_html("<br>")


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
BLOAT_MODEL_PATH = os.path.join(BASE_DIR, "runs", "internal_models", "bloat_model.pkl")
MILK_FEVER_MODEL_PATH = os.path.join(BASE_DIR, "runs", "internal_models", "milk_fever_model.pkl")
KETOSIS_MODEL_PATH = os.path.join(BASE_DIR, "runs", "internal_models", "ketosis_model.pkl")


# ─── Expert Advice (Local — no external API needed) ───
def get_expert_advice(condition_name, is_healthy, confidence=0.0):
    """Generate expert veterinary advice based on the detected condition and severity."""
    if confidence >= 0.85:
        severity = "Severe"
    elif confidence >= 0.65:
        severity = "Moderate"
    else:
        severity = "Mild"

    if is_healthy:
        if confidence >= 0.80:
            return (
                "The animal appears to be in excellent health with high confidence. "
                "Continue routine monitoring, maintain vaccination schedules, and ensure "
                "proper nutrition and hygiene."
            )
        else:
            return (
                "The animal is likely healthy, but confidence is moderate. "
                "Monitor closely for any developing symptoms over the next 48 hours, "
                "and ensure regular veterinary check-ups to keep the herd healthy."
            )

    if "Lumpy" in condition_name:
        if severity == "Severe":
            return (
                "CRITICAL: Severe Lumpy Skin Disease (LSD) symptoms detected. Immediate quarantine "
                "and veterinary intervention are required. Implement strict insect vector control and provide "
                "supportive care like wound management and anti-inflammatory medication."
            )
        elif severity == "Moderate":
            return (
                "Clear symptoms of Lumpy Skin Disease (LSD) have been detected. Immediately isolate "
                "the affected animal to prevent spread. Contact your local veterinary authority for confirmation. "
                "LSD is transmitted by biting insects — use insect repellents."
            )
        else:
            return (
                "Potential early signs of Lumpy Skin Disease detected. Isolate the animal and monitor closely. "
                "Bug control is critical. Contact a vet if symptoms progress."
            )
            
    elif "Foot" in condition_name:
        if severity == "Severe":
            return (
                "CRITICAL: Severe and undeniable Foot and Mouth Disease (FMD) detected. High risk of herd infection. "
                "Absolute lockdown of premises required immediately. Contact government veterinary authorities urgently."
            )
        elif severity == "Moderate":
            return (
                "Foot and Mouth Disease (FMD) symptoms have been detected. This is a highly "
                "contagious viral disease. Quarantine the affected animal immediately and notify "
                "your local veterinary services. Do not move animals in or out of the premises."
            )
        else:
            return (
                "Potential early Foot and Mouth Disease (FMD) signs. Isolate immediately and observe. "
                "Do not allow movement off the farm. Provide soft feed and clean water."
            )
            
    elif "Mastitis" in condition_name or "Udder" in condition_name:
        if severity == "Severe":
            return (
                "CRITICAL: Severe Udder Disease / Mastitis detected with high inflammation. Stop milking this cow "
                "with shared equipment immediately. Urgent antibiotic treatment is likely necessary."
            )
        elif severity == "Moderate":
            return (
                "Bovine Mastitis or Udder Disease has been detected. Isolate the cow "
                "to prevent spreading during milking. Contact your veterinarian for a culture test "
                "to determine the specific bacteria and the appropriate antibiotic treatment."
            )
        else:
            return (
                "Mild signs of Bovine Mastitis. Ensure thorough cleaning of milking equipment, "
                "monitor the cow's milk output, and maintain excellent hygiene."
            )
            
    elif "Bloat" in condition_name:
        if severity == "Severe":
            return (
                "CRITICAL EMERGENCY: Severe Bloat (Ruminal Tympany) is a life-threatening emergency! Immediate veterinary action is required. "
                "Relieving gas pressure via a stomach tube or trocar may be necessary to prevent suffocation."
            )
        elif severity == "Moderate":
            return (
                "Bloat (Ruminal Tympany) is present. Do not allow the cow to lie down; keep it moving if possible. "
                "Call a veterinarian immediately for treatment."
            )
        else:
            return (
                "Mild Bloat detected. Keep the cow moving and observe closely. Do not feed legumes or concentrate feed "
                "until symptoms completely subside."
            )
            
    elif "Milk Fever" in condition_name:
        if severity == "Severe":
            return (
                "CRITICAL EMERGENCY: Severe Milk Fever (downer cow) detected. Immediate treatment with intravenous "
                "calcium borogluconate by a veterinarian is critical. Prop the cow up in a sternal sitting position to prevent pneumonia."
            )
        elif severity == "Moderate":
            return (
                "Milk Fever (Hypocalcemia) detected. The cow is likely weak and struggling. Do not attempt to drench. "
                "Keep warm and call a vet for immediate calcium treatment."
            )
        else:
            return (
                "Mild signs of Milk Fever. The cow may be wobbly but standing. Oral calcium supplementation "
                "may be sufficient, but consult your vet immediately."
            )
            
    elif "Ketosis" in condition_name:
        if severity == "Severe":
            return (
                "CRITICAL EMERGENCY: Severe Ketosis (Acetonemia) detected. The cow is likely showing severe neurological signs or total feed refusal. "
                "Immediate intravenous glucose therapy by a veterinarian is required."
            )
        elif severity == "Moderate":
            return (
                "Ketosis detected. The cow is losing condition and milk production is dropping. "
                "Consult a veterinarian. Treatment usually involves oral propylene glycol or intravenous dextrose."
            )
        else:
            return (
                "Mild or early signs of Ketosis detected. Closely monitor feed intake and adjust the diet to ensure adequate energy. "
                "Consider oral energy supplements."
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

    # Align probabilities directly with prediction confidence for 100% exact match
    if is_healthy:
        healthy_prob = top1_conf
        unhealthy_prob = max(0.0, 1.0 - healthy_prob)
    else:
        unhealthy_prob = top1_conf
        healthy_prob = max(0.0, 1.0 - unhealthy_prob)

    advice = get_expert_advice(pretty_name, is_healthy, top1_conf)
    return pretty_name, top1_conf, is_healthy, advice, healthy_prob, unhealthy_prob


# ─── Gemini Cattle Health Chatbot Engine ───
def query_gemini_cattle_bot(user_prompt, history_messages, api_key=None):
    """
    Query Google Gemini LLM with strict Cattle-Only domain guardrails.
    """
    prompt_lower = user_prompt.strip().lower()

    # Friendly conversational greetings
    greeting_triggers = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "who are you", "what can you do", "help", "start"]

    is_greeting = any(prompt_lower == gt or prompt_lower.startswith(gt + " ") or prompt_lower.endswith(" " + gt) for gt in greeting_triggers)

    if is_greeting:
        return (
            "👋 **Hello! Welcome to CattleSense Assistant!**\n\n"
            "I am an AI veterinary assistant specialized in cattle health and bovine disease management.\n\n"
            "**How I can help you:**\n"
            "- 🦠 **External Diseases:** Lumpy Skin Disease (LSD), Foot and Mouth Disease (FMD), Udder Mastitis.\n"
            "- 🫀 **Internal Diseases:** Bloating (Ruminal Tympany), Milk Fever (Hypocalcemia), Ketosis.\n"
            "- 🌾 **Herd Care & Nutrition:** Feeding guidelines, vaccination schedules, and emergency advice.\n\n"
            "Please ask me any cattle health or disease question to get started!"
        )

    # Off-topic triggers to reject immediately
    off_topic_indicators = [
        "python code", "write a code", "calculator", "who is the president", "capital of",
        "football", "cricket", "movie", "actor", "recipe for", "quantum physics",
        "solve this equation", "who won", "javascript", "html code", "tell me a joke about dogs",
        "cat care", "pet rabbit", "iphone", "android", "car engine", "stock market",
        "crypto", "bitcoin", "politics", "election"
    ]

    # Cattle relevance keywords
    cattle_keywords = [
        "cow", "cows", "cattle", "bull", "bulls", "calf", "calves", "heifer", "steer", "ox", "oxen",
        "bovine", "lumpy", "lsd", "fmd", "foot and mouth", "mastitis", "udder", "bloat", "tympany",
        "milk fever", "hypocalcemia", "ketosis", "acetonemia", "rumen", "ruminant", "lactation",
        "calving", "veterinary", "herd", "livestock", "feed", "pasture", "silage", "colostrum",
        "vaccine", "deworming", "milk yield", "teat", "hoof", "rot", "ringworm", "ticks", "flies",
        "disease", "symptom", "infection", "treatment", "cure", "health", "farm", "dairy"
    ]

    off_topic_refusal = (
        "I am CattleSense Assistant, specialized exclusively in cattle health and bovine veterinary care. "
        "Please ask me questions related to cattle diseases, symptoms, nutrition, or herd management."
    )

    is_explicit_offtopic = any(indicator in prompt_lower for indicator in off_topic_indicators)
    is_cattle_related = any(kw in prompt_lower for kw in cattle_keywords)

    if is_explicit_offtopic and not is_cattle_related:
        return off_topic_refusal

    # Retrieve API key from param, env, or secrets
    effective_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not effective_key:
        try:
            effective_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
        except Exception:
            pass

    system_instruction = (
        "You are CattleSense Assistant, an expert AI veterinary consultant specialized EXCLUSIVELY in "
        "cattle health, bovine diseases (such as Lumpy Skin Disease, Foot & Mouth Disease, Udder Mastitis, "
        "Bloating/Ruminal Tympany, Milk Fever/Hypocalcemia, Ketosis/Acetonemia), livestock nutrition, "
        "breeding, and herd management.\n\n"
        "STRICT SYSTEM RULE:\n"
        "You must ONLY answer questions related to cattle (cows, bulls, calves, heifers, oxen, buffaloes), "
        "bovine health, diseases, veterinary treatments, livestock feeding, and farm management.\n\n"
        "If the user asks ANY question outside of cattle health and bovine livestock care, you MUST politely decline "
        "and respond with EXACTLY:\n"
        "'I am CattleSense Assistant, specialized exclusively in cattle health and bovine veterinary care. "
        "Please ask me questions related to cattle diseases, symptoms, nutrition, or herd management.'"
    )

    # Try Google GenAI SDK if key is available
    if effective_key:
        try:
            from google import genai
            client = genai.Client(api_key=effective_key)
            
            contents = []
            for m in history_messages[-6:]:
                role = "user" if m["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})
            contents.append({"role": "user", "parts": [{"text": user_prompt}]})

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config={
                    'system_instruction': system_instruction,
                    'temperature': 0.3,
                    'max_output_tokens': 800
                }
            )
            if response.text:
                return response.text
        except Exception:
            # Fallback to direct REST call via requests
            try:
                import requests
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={effective_key}"
                contents = []
                for m in history_messages[-6:]:
                    role = "user" if m["role"] == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": m["content"]}]})
                contents.append({"role": "user", "parts": [{"text": user_prompt}]})

                payload = {
                    "system_instruction": {"parts": [{"text": system_instruction}]},
                    "contents": contents,
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800}
                }
                res = requests.post(url, json=payload, timeout=10)
                if res.status_code == 200:
                    return res.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                pass

    # Local Knowledge Engine Fallback if offline or keyless
    return generate_local_cattle_knowledge_reply(user_prompt, is_cattle_related, off_topic_refusal)


def generate_local_cattle_knowledge_reply(prompt, is_cattle_related, refusal_msg):
    """Local cattle health knowledge engine for offline / keyless operation."""
    p = prompt.lower()

    if not is_cattle_related:
        return refusal_msg

    if "lumpy" in p or "lsd" in p:
        return (
            "🐄 **Lumpy Skin Disease (LSD) Guidance:**\n\n"
            "- **Symptoms:** Firm, raised skin nodules (2–5 cm), fever, enlarged lymph nodes, eye/nasal discharge, and reduced milk yield.\n"
            "- **Cause:** Capripoxvirus transmitted primarily by biting insects (flies, mosquitoes, ticks).\n"
            "- **Prevention & Management:**\n"
            "  1. Isolate infected cattle immediately to stop vector transmission.\n"
            "  2. Apply insect repellents and insecticides around stalls.\n"
            "  3. Vaccinate healthy herd members using homologated LSD vaccines.\n"
            "  4. Provide supportive care: wound sprays for ruptured nodules and anti-inflammatories under veterinary guidance."
        )
    elif "foot" in p or "fmd" in p or "mouth" in p:
        return (
            "🦶 **Foot and Mouth Disease (FMD) Guidance:**\n\n"
            "- **Symptoms:** Vesicles (blisters) on tongue, lips, gums, interdigital hoof space, and teats; severe lameness, fever, and profuse salivation (drooling).\n"
            "- **Cause:** Highly contagious Aphthovirus spread via aerosols, direct contact, or contaminated footwear/vehicles.\n"
            "- **Prevention & Control:**\n"
            "  1. Immediate strict quarantine of affected premises.\n"
            "  2. Disinfect equipment with sodium carbonate or citric acid solutions.\n"
            "  3. Provide soft mash feeds and clean water for mouth-sore animals.\n"
            "  4. Report suspect cases immediately to government veterinary authorities."
        )
    elif "mastitis" in p or "udder" in p:
        return (
            "🥛 **Udder Disease / Bovine Mastitis Guidance:**\n\n"
            "- **Symptoms:** Swollen, hot, or painful udder quarters; abnormal milk containing clots, flakes, or watery whey; fever.\n"
            "- **Types:** Environmental vs. Contagious Mastitis (Staphylococcus aureus, Streptococcus agalactiae).\n"
            "- **Management:**\n"
            "  1. Perform California Mastitis Test (CMT) for early quarter detection.\n"
            "  2. Milk affected cows last using clean, sanitized equipment.\n"
            "  3. Administer intramammary antibiotics specified by milk culture.\n"
            "  4. Maintain clean, dry bedding and post-milking teat dips."
        )
    elif "bloat" in p or "tympany" in p or "swollen left" in p:
        return (
            "🎈 **Ruminal Tympany (Bloat) Guidance:**\n\n"
            "- **Symptoms:** Severe distension of the left flank, rapid breathing, kicking at abdomen, refusal to eat, and severe distress.\n"
            "- **Types:** Frothy Bloat (legumes/alfalfa grazing) vs. Free-Gas Bloat (esophageal obstruction or grain overload).\n"
            "- **Emergency Action:**\n"
            "  1. Keep the cow standing and moving; do not let it lie down.\n"
            "  2. Administer anti-foaming agents (drench with vegetable oil or poloxalene).\n"
            "  3. In severe life-threatening suffocation, a veterinarian must use a stomach tube or trocar."
        )
    elif "milk fever" in p or "hypocalcemia" in p or "downer" in p:
        return (
            "🥛 **Milk Fever (Hypocalcemia) Guidance:**\n\n"
            "- **Symptoms:** Occurs within 48–72 hours post-calving. Muscle weakness, unsteadiness, S-shaped neck curvature, cold ears/legs, inability to stand.\n"
            "- **Emergency Treatment:**\n"
            "  1. Call a vet immediately for slow intravenous calcium borogluconate (400 mL).\n"
            "  2. **CRITICAL:** Do NOT attempt to orally drench a downer cow due to loss of swallowing reflex (pneumonia risk).\n"
            "  3. Prop the cow up in a sternal position with straw bales to prevent bloating."
        )
    elif "ketosis" in p or "acetonemia" in p:
        return (
            "📉 **Ketosis (Acetonemia) Guidance:**\n\n"
            "- **Symptoms:** 2–6 weeks post-calving in high-yield dairy cows. Sweet acetone odor on breath/milk, rapid weight loss, refusal of concentrates.\n"
            "- **Management:**\n"
            "  1. Administer oral propylene glycol (300 g twice daily) for 3–5 days.\n"
            "  2. Veterinarians may administer IV 50% dextrose solution.\n"
            "  3. Ensure high-energy balanced transition rations pre- and post-calving."
        )
    elif "feed" in p or "nutrition" in p or "diet" in p:
        return (
            "🌾 **Cattle Feeding & Nutrition Best Practices:**\n\n"
            "- **Dry Matter Intake (DMI):** Dairy cows require 3.5%–4% of body weight in DMI daily.\n"
            "- **Forage-to-Concentrate Ratio:** Maintain minimum 40:60 forage-to-concentrate ratio to preserve rumen health.\n"
            "- **Clean Water:** Dairy cows require 100–150 liters of clean, fresh water per day."
        )
    else:
        return (
            "🐄 **Cattle Health Assistant Guidance:**\n\n"
            "I am ready to help you with bovine health management. You can ask me about:\n"
            "1. **External Diseases:** Lumpy Skin Disease (LSD), Foot & Mouth Disease (FMD), Udder Mastitis.\n"
            "2. **Internal Metabolic Conditions:** Bloating (Ruminal Tympany), Milk Fever (Hypocalcemia), Ketosis.\n"
            "3. **Herd Management:** Vaccination schedules, deworming, nutritional guidelines, and calving protocols."
        )


# ─── Session State Routing ───
if "page" not in st.session_state:
    st.session_state.page = "home"
if "disease" not in st.session_state:
    st.session_state.disease = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "Hello! I am CattleSense Assistant, powered by Gemini AI. Ask me any question related to cattle health, diseases, symptoms, treatment, nutrition, or herd management."
        }
    ]

def go_home():
    st.session_state.page = "home"
    st.session_state.disease = None

def go_external():
    st.session_state.page = "external"
    st.session_state.disease = None

def go_internal():
    st.session_state.page = "internal"
    st.session_state.disease = None

def go_chatbot():
    st.session_state.page = "chatbot"
    st.session_state.disease = None

def go_detect(disease):
    st.session_state.page = "detect"
    st.session_state.disease = disease

def go_detect_internal(disease):
    st.session_state.page = "detect_internal"
    st.session_state.disease = disease


# ═══════════════════════════════════════════════
#             PERFECTLY SYMMETRICAL HOME PAGE
# ═══════════════════════════════════════════════
def render_home():
    render_navbar()

    render_html('<div class="hero-title">🐄 CattleSense</div>')
    render_html('<div class="hero-subtitle">Select a category to begin examination or consult our AI Chatbot</div>')

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        render_html("""
        <div class="home-card-top">
            <div class="card-icon">👁️</div>
            <div class="card-title">External Diseases</div>
            <div class="card-desc">Examine cattle for external diseases like FMD, LSD, and Udder Disease using Computer Vision</div>
        </div>
        <div class="home-card-bottom">
        """)
        if st.button("Explore External Diseases", key="btn_ext"):
            go_external()
            st.rerun()
        render_html('</div>')

    with col2:
        render_html("""
        <div class="home-card-top">
            <div class="card-icon">🫀</div>
            <div class="card-title">Internal Diseases</div>
            <div class="card-desc">Diagnose internal conditions based on clinical symptoms and physiological questionnaires</div>
        </div>
        <div class="home-card-bottom">
        """)
        if st.button("Explore Internal Diseases", key="btn_int"):
            go_internal()
            st.rerun()
        render_html('</div>')

    with col3:
        render_html("""
        <div class="home-card-top">
            <div class="card-icon">💬</div>
            <div class="card-title">Cattle Assistant</div>
            <div class="card-desc">Consult our specialized Gemini AI Chatbot for cattle health, symptoms, and veterinary advice</div>
        </div>
        <div class="home-card-bottom">
        """)
        if st.button("Launch Chatbot", key="btn_chat"):
            go_chatbot()
            st.rerun()
        render_html('</div>')


# ═══════════════════════════════════════════════
#             CATTLE HEALTH CHATBOT PAGE
# ═══════════════════════════════════════════════
def render_chatbot():
    render_navbar()

    render_html('<div class="detect-header">💬 CattleSense Veterinary Assistant</div>')
    render_html('<div class="detect-sub">Powered by Gemini AI — Strictly specialized in Cattle Health & Bovine Veterinary Care</div>')

    # Sidebar API key configuration
    gemini_key_input = st.sidebar.text_input(
        "🔑 Gemini API Key (Optional)",
        type="password",
        help="Enter your Google Gemini API key to enable live Gemini LLM responses. If omitted, local expert knowledge engine is used."
    )

    c_left, c_right = st.columns([4, 1])
    with c_right:
        render_html('<div class="sec-button">')
        if st.button("🧹 Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": "Hello! I am CattleSense Assistant, powered by Gemini AI. Ask me any question related to cattle health, diseases, symptoms, treatment, nutrition, or herd management."
                }
            ]
            st.rerun()
        render_html('</div>')

    render_html('<div class="chat-card">')
    st.markdown("<h4 style='color: #0F172A; margin-bottom: 1rem; font-family: Manrope;'>Ask a Question</h4>", unsafe_allow_html=True)
    
    # Suggested prompt chips
    st.markdown("<div style='font-size: 0.85rem; color: #6B7280; font-weight: 700; margin-bottom: 0.5rem;'>SUGGESTED QUESTIONS:</div>", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    suggested_prompt = None
    with p1:
        if st.button("🌾 Bloating Prevention", key="chip1"):
            suggested_prompt = "What are the symptoms and emergency treatment for Bloating in cattle?"
    with p2:
        if st.button("🥛 Milk Fever Signs", key="chip2"):
            suggested_prompt = "How do I identify early stage Milk Fever in a dairy cow?"
    with p3:
        if st.button("🦟 LSD Transmission", key="chip3"):
            suggested_prompt = "How is Lumpy Skin Disease transmitted and prevented?"
    with p4:
        if st.button("🦶 FMD Warning Signs", key="chip4"):
            suggested_prompt = "What are the key warning signs of Foot and Mouth Disease?"

    # Display chat conversation history
    for msg in st.session_state.chat_messages:
        avatar = "🐄" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # User input chat box
    user_input = st.chat_input("Type your cattle health or disease question...") or suggested_prompt

    if user_input:
        # Append user message
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Generate Gemini AI reply
        with st.chat_message("assistant", avatar="🐄"):
            with st.spinner("Consulting CattleSense AI..."):
                reply = query_gemini_cattle_bot(user_input, st.session_state.chat_messages[:-1], gemini_key_input)
                st.markdown(reply)
                st.session_state.chat_messages.append({"role": "assistant", "content": reply})

    render_html('</div>')


# ═══════════════════════════════════════════════
#             EXTERNAL DISEASES PAGE
# ═══════════════════════════════════════════════
def render_external():
    render_navbar()

    col_back, col_empty = st.columns([1.5, 4.5])
    with col_back:
        render_html('<div class="sec-button">')
        if st.button("← Back to Categories", key="back_to_home_ext"):
            go_home()
            st.rerun()
        render_html('</div>')

    render_html('<div class="hero-title">🐄 External Diseases</div>')
    render_html('<div class="hero-subtitle">Select a condition to begin the examination</div>')

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        render_html("""
        <div class="cat-card-top">
            <div class="card-icon">🦶</div>
            <div class="card-title">Foot and Mouth Disease</div>
            <div class="card-desc">Examine cattle for vesicular lesions on the mouth, tongue, hooves, and teats</div>
        </div>
        <div class="cat-card-bottom">
        """)
        if st.button("Start FMD Examination", key="btn_fmd"):
            go_detect("fmd")
            st.rerun()
        render_html('</div>')

    with col2:
        render_html("""
        <div class="cat-card-top">
            <div class="card-icon">🔬</div>
            <div class="card-title">Lumpy Skin Disease</div>
            <div class="card-desc">Analyze cattle skin surfaces for firm nodules, lesions, and pathological changes</div>
        </div>
        <div class="cat-card-bottom">
        """)
        if st.button("Start LSD Examination", key="btn_lsd"):
            go_detect("lumpy")
            st.rerun()
        render_html('</div>')

    with col3:
        render_html("""
        <div class="cat-card-top">
            <div class="card-icon">🐄</div>
            <div class="card-title">Udder Disease</div>
            <div class="card-desc">Inspect bovine udders for inflammation, swelling, and signs of mastitis</div>
        </div>
        <div class="cat-card-bottom">
        """)
        if st.button("Start Udder Examination", key="btn_udder"):
            go_detect("udder")
            st.rerun()
        render_html('</div>')

    # ── Stats Section ──
    render_html("<br><hr><br>")
    s1, s2, s3, s4 = st.columns(4, gap="medium")
    with s1:
        render_html("""
        <div class="stat-box">
            <div class="stat-value">323</div>
            <div class="stat-label">Lumpy Skin Samples</div>
        </div>
        """)
    with s2:
        render_html("""
        <div class="stat-box">
            <div class="stat-value">212</div>
            <div class="stat-label">FMD Samples</div>
        </div>
        """)
    with s3:
        render_html("""
        <div class="stat-box">
            <div class="stat-value">120</div>
            <div class="stat-label">Udder Samples</div>
        </div>
        """)
    with s4:
        render_html("""
        <div class="stat-box">
            <div class="stat-value">547</div>
            <div class="stat-label">Healthy Baselines</div>
        </div>
        """)


# ═══════════════════════════════════════════════
#             INTERNAL DISEASES PAGE
# ═══════════════════════════════════════════════
def render_internal():
    render_navbar()

    col_back, col_empty = st.columns([1.5, 4.5])
    with col_back:
        render_html('<div class="sec-button">')
        if st.button("← Back to Categories", key="back_to_home_int"):
            go_home()
            st.rerun()
        render_html('</div>')

    render_html('<div class="hero-title">🫀 Internal Diseases</div>')
    render_html('<div class="hero-subtitle">Diagnose conditions via clinical symptom questionnaires</div>')

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        render_html("""
        <div class="cat-card-top">
            <div class="card-icon">🎈</div>
            <div class="card-title">Bloating (Ruminal Tympany)</div>
            <div class="card-desc">Diagnose ruminal distension through clinical signs and feeding history</div>
        </div>
        <div class="cat-card-bottom">
        """)
        if st.button("Start Bloating Examination", key="btn_bloat"):
            go_detect_internal("bloat")
            st.rerun()
        render_html('</div>')

    with col2:
        render_html("""
        <div class="cat-card-top">
            <div class="card-icon">🥛</div>
            <div class="card-title">Milk Fever</div>
            <div class="card-desc">Detect metabolic hypocalcemia related to calving and muscle weakness</div>
        </div>
        <div class="cat-card-bottom">
        """)
        if st.button("Start Milk Fever Examination", key="btn_milk_fever"):
            go_detect_internal("milk_fever")
            st.rerun()
        render_html('</div>')

    with col3:
        render_html("""
        <div class="cat-card-top">
            <div class="card-icon">📉</div>
            <div class="card-title">Ketosis (Acetonemia)</div>
            <div class="card-desc">Detect energy metabolism disorders common in early lactation dairy cows</div>
        </div>
        <div class="cat-card-bottom">
        """)
        if st.button("Start Ketosis Examination", key="btn_ketosis"):
            go_detect_internal("ketosis")
            st.rerun()
        render_html('</div>')


# ═══════════════════════════════════════════════
#             DETECTION INTERNAL PAGE
# ═══════════════════════════════════════════════
@st.cache_resource
def load_internal_model(model_path):
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            return pickle.load(f)
    return None

def render_detect_internal():
    disease = st.session_state.disease
    if disease == "bloat":
        display_name = "Bloating (Ruminal Tympany)"
        model_path = BLOAT_MODEL_PATH
        prediction_text_positive = "Bloating (Ruminal Tympany) Detected"
        prediction_text_negative = "Healthy — No Bloat Symptoms Found"
        unhealthy_class_name = "Bloat"
        questions = [
            ("q1_left_side_swollen", "1. Is the left side of the cow's abdomen swollen?", ["No", "Yes"]),
            ("q2_sudden_swelling", "2. Did the swelling appear suddenly (within a few hours)?", ["No", "Yes"]),
            ("q3_difficulty_breathing", "3. Is the cow having difficulty breathing or breathing rapidly?", ["No", "Yes"]),
            ("q4_stopped_eating", "4. Has the cow stopped eating or lost its appetite?", ["No", "Yes"]),
            ("q5_stopped_chewing_cud", "5. Has the cow stopped chewing cud (rumination)?", ["No", "Yes"]),
            ("q6_restless_kicking", "6. Is the cow restless, repeatedly standing up and lying down, or kicking at its belly?", ["No", "Yes"]),
            ("q7_grazed_lush_pasture", "7. Has the cow grazed on lush green pasture or legumes (such as alfalfa or clover) in the last 24 hours?", ["No", "Yes"]),
            ("q8_large_amount_grain", "8. Has the cow recently been given a large amount of grain or concentrate feed?", ["No", "Yes"]),
            ("q9_drooling_stretching_neck", "9. Is the cow drooling excessively or stretching its neck with its mouth open?", ["No", "Yes"]),
            ("q10_swelling_left_side_only", "10. Is the swelling mainly on the left side rather than the whole abdomen?", ["No", "Yes"])
        ]
    elif disease == "milk_fever":
        display_name = "Milk Fever (Hypocalcemia)"
        model_path = MILK_FEVER_MODEL_PATH
        prediction_text_positive = "Milk Fever Detected"
        prediction_text_negative = "Healthy — No Milk Fever Symptoms Found"
        unhealthy_class_name = "Milk Fever"
        questions = [
            ("q1_calved_72h", "1. Has the cow calved within the last 72 hours?", ["No", "Yes"]),
            ("q2_unable_to_stand", "2. Is the cow unable to stand or having difficulty getting up?", ["No", "Yes"]),
            ("q3_cold_ears_legs", "3. Are the cow’s ears or legs unusually cold to touch?", ["No", "Yes"]),
            ("q4_muscle_tremors", "4. Is the cow showing muscle tremors, twitching, or shaking?", ["No", "Yes"]),
            ("q5_walking_unsteadily", "5. Is the cow walking unsteadily, stiffly, or showing weakness in the legs?", ["No", "Yes"]),
            ("q6_head_turned", "6. Is the cow lying down with its head turned toward the flank or chest?", ["No", "Yes"]),
            ("q7_lost_appetite", "7. Has the cow suddenly lost appetite or stopped eating?", ["No", "Yes"]),
            ("q8_stopped_cud", "8. Has the cow reduced or stopped chewing cud?", ["No", "Yes"]),
            ("q9_decreased_milk", "9. Has milk production suddenly decreased after calving?", ["No", "Yes"]),
            ("q10_previous_fever", "10. Has the cow had Milk Fever during a previous calving?", ["No", "Unknown", "Yes"])
        ]
    elif disease == "ketosis":
        display_name = "Ketosis (Acetonemia)"
        model_path = KETOSIS_MODEL_PATH
        prediction_text_positive = "Ketosis Detected"
        prediction_text_negative = "Healthy — No Ketosis Symptoms Found"
        unhealthy_class_name = "Ketosis"
        questions = [
            ("q1_recently_calved", "1. Has the cow recently calved (within the last 2–6 weeks)?", ["No", "Yes"]),
            ("q2_lost_appetite_concentrate", "2. Has the cow lost its appetite, especially refusing concentrate feed?", ["No", "Yes"]),
            ("q3_milk_decreased", "3. Has the cow's milk production decreased suddenly?", ["No", "Yes"]),
            ("q4_losing_weight", "4. Is the cow losing weight or body condition despite being fed?", ["No", "Yes"]),
            ("q5_dull_weak", "5. Does the cow appear dull, weak, or less active than usual?", ["No", "Yes"]),
            ("q6_sweet_acetone_breath", "6. Does the cow have a sweet or acetone-like smell on its breath or milk?", ["No", "Yes"]),
            ("q7_chewing_cud_less", "7. Is the cow chewing cud less frequently than normal?", ["No", "Yes"]),
            ("q8_abnormal_behavior", "8. Is the cow showing abnormal behavior such as excessive licking, aimless walking, or nervousness?", ["No", "Yes"]),
            ("q9_eaten_poorly_days", "9. Has the cow eaten poorly for the past 2–3 days?", ["No", "Yes"]),
            ("q10_high_producing", "10. Is the cow a high milk-producing dairy cow?", ["No", "Yes"])
        ]

    render_navbar()

    col_back, col_empty = st.columns([1.5, 4.5])
    with col_back:
        render_html('<div class="sec-button">')
        if st.button("← Back to Internal Diseases", key="back_btn_int"):
            go_internal()
            st.rerun()
        render_html('</div>')

    render_html('<div class="detect-header">Diagnostic Center</div>')
    render_html(f'<div class="detect-sub">Examining for: {display_name}</div>')

    model = load_internal_model(model_path)
    if model is None:
        st.error(f"⚠️ The {display_name} model is not yet available.")
        return

    render_html('<div style="background: #FFFFFF; padding: 2rem; border-radius: 20px; border: 1px solid #E5E7EB; margin-bottom: 2rem; box-shadow: 0 10px 25px rgba(0,0,0,0.08);">')
    st.markdown("<h3 style='color: #0F172A; margin-bottom: 1.5rem; font-family: Manrope;'>Clinical Questionnaire</h3>", unsafe_allow_html=True)
    
    answers = {}
    for key, q_text, options in questions:
        render_html(f"<div style='color: #374151; font-weight: 600; font-size: 1.02rem; margin-bottom: 0.5rem;'>{q_text}</div>")
        ans = st.radio("Select answer:", options=options, key=key, horizontal=True, label_visibility="collapsed")
        if ans == "Yes":
            answers[key] = 2 if len(options) == 3 else 1
        elif ans == "Unknown":
            answers[key] = 1
        else:
            answers[key] = 0
        render_html("<hr style='border-color: #E5E7EB; margin: 1rem 0;'>")
        
    render_html('</div>')

    if st.button("🔍 Analyze Symptoms", key="run_int_btn"):
        with st.spinner("Analyzing clinical data..."):
            df_input = pd.DataFrame([answers])
            pred_class = model.predict(df_input)[0]
            probs = model.predict_proba(df_input)[0]
            probs_dict = dict(zip(model.classes_, probs))
            
            is_healthy = (pred_class == "Healthy")
            confidence = probs_dict.get(pred_class, 0.0)
            
            prediction_text = prediction_text_positive if not is_healthy else prediction_text_negative
            advice = get_expert_advice(prediction_text, is_healthy, confidence)
            
            if is_healthy:
                healthy_prob = confidence
                unhealthy_prob = max(0.0, 1.0 - healthy_prob)
            else:
                unhealthy_prob = confidence
                healthy_prob = max(0.0, 1.0 - unhealthy_prob)

            result_class = "result-negative" if is_healthy else "result-positive"
            icon = "✅" if is_healthy else "⚠️"

            render_html(f"""
            <div class="result-box {result_class}">
                <div class="result-title">{icon} {prediction_text}</div>
                <div class="confidence-badge">Confidence: {confidence * 100:.1f}%</div>
                <hr style="border-color: #E5E7EB; margin: 1rem 0;">
                <div style="color: #6B7280; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">Expert Veterinary Guidance</div>
                <div class="result-advice">{advice}</div>
            </div>
            """)
            
            render_html("<br>")
            st.markdown('<h3 style="color:#f8fafc; font-size:1.25rem; font-family: Manrope;">Health Status Analysis</h3>', unsafe_allow_html=True)
            
            healthy_pct = healthy_prob * 100
            unhealthy_pct = unhealthy_prob * 100

            graph_html = f"""
            <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 20px; padding: 1.75rem; margin-top: 0.5rem; box-shadow: 0 8px 24px rgba(0,0,0,0.08);">
                <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
                    <div style="flex: 1; background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 14px; padding: 1.1rem; text-align: center;">
                        <div style="font-size: 0.82rem; color: #047857; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Healthy (No Symptoms)</div>
                        <div style="font-family: Manrope; font-size: 2rem; font-weight: 800; color: #059669; margin-top: 0.25rem;">{healthy_pct:.1f}%</div>
                    </div>
                    <div style="flex: 1; background: #FEF2F2; border: 1px solid #FECACA; border-radius: 14px; padding: 1.1rem; text-align: center;">
                        <div style="font-size: 0.82rem; color: #B91C1C; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Unhealthy (Disease Symptoms)</div>
                        <div style="font-family: Manrope; font-size: 2rem; font-weight: 800; color: #DC2626; margin-top: 0.25rem;">{unhealthy_pct:.1f}%</div>
                    </div>
                </div>
                <div style="margin-bottom: 1.25rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-size: 0.95rem; font-weight: 700; color: #1F2937;">
                        <span>🟢 Healthy (No Symptoms)</span>
                        <span style="color: #059669;">{healthy_pct:.1f}%</span>
                    </div>
                    <div style="width: 100%; background: #F3F4F6; border-radius: 8px; height: 16px; overflow: hidden;">
                        <div style="width: {healthy_pct:.1f}%; background: linear-gradient(90deg, #10B981 0%, #059669 100%); height: 100%; border-radius: 8px;"></div>
                    </div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-size: 0.95rem; font-weight: 700; color: #1F2937;">
                        <span>🔴 Unhealthy (Disease Symptoms)</span>
                        <span style="color: #DC2626;">{unhealthy_pct:.1f}%</span>
                    </div>
                    <div style="width: 100%; background: #F3F4F6; border-radius: 8px; height: 16px; overflow: hidden;">
                        <div style="width: {unhealthy_pct:.1f}%; background: linear-gradient(90deg, #FCA5A5 0%, #EF4444 100%); height: 100%; border-radius: 8px;"></div>
                    </div>
                </div>
            </div>
            """
            render_html(graph_html)


# ═══════════════════════════════════════════════
#             DETECTION EXTERNAL PAGE
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

    render_navbar()

    col_back, col_empty = st.columns([1.5, 4.5])
    with col_back:
        render_html('<div class="sec-button">')
        if st.button("← Back to External Diseases", key="back_btn"):
            go_external()
            st.rerun()
        render_html('</div>')

    render_html('<div class="detect-header">Diagnostic Center</div>')
    render_html(f'<div class="detect-sub">Examining for: {display_name}</div>')

    model = load_model(model_path)
    if model is None:
        st.error(f"⚠️ The {display_name} model is not yet available. Please ensure training is complete.")
        return

    uploaded_file = st.file_uploader(
        "Upload a sample image for examination",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        help="Supported formats: JPG, JPEG, PNG, BMP, WEBP"
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        col_img, col_info = st.columns([1.2, 1], gap="medium")

        with col_img:
            st.image(image, caption="Uploaded Sample", use_container_width=True)

        with col_info:
            render_html(f"""
            <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 18px; padding: 1.5rem; box-shadow: 0 6px 18px rgba(0,0,0,0.06); color: #1F2937;">
                <div style="font-family: Manrope; font-size: 1.1rem; font-weight: 800; color: #0F172A; margin-bottom: 1rem;">Sample Information</div>
                <div style="margin-bottom: 0.85rem;">
                    <div style="font-size: 0.8rem; color: #6B7280; text-transform: uppercase; font-weight: 700;">File Name</div>
                    <div style="font-weight: 600; color: #0F172A;">{uploaded_file.name}</div>
                </div>
                <div style="margin-bottom: 0.85rem;">
                    <div style="font-size: 0.8rem; color: #6B7280; text-transform: uppercase; font-weight: 700;">Dimensions</div>
                    <div style="font-weight: 600; color: #0F172A;">{image.width} × {image.height} px</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: #6B7280; text-transform: uppercase; font-weight: 700;">Examining For</div>
                    <div style="font-weight: 700; color: #059669;">{display_name}</div>
                </div>
            </div>
            """)

        render_html("<br>")

        if st.button("🔍 Run Examination", key="run_btn"):
            with st.spinner("Analyzing sample..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                try:
                    prediction, confidence, is_healthy, advice, healthy_prob, unhealthy_prob = run_prediction(
                        model, tmp_path, disease
                    )

                    result_class = "result-negative" if is_healthy else "result-positive"
                    icon = "✅" if is_healthy else "⚠️"

                    render_html(f"""
                    <div class="result-box {result_class}">
                        <div class="result-title">{icon} {prediction}</div>
                        <div class="confidence-badge">Confidence: {confidence * 100:.1f}%</div>
                        <hr style="border-color: #E5E7EB; margin: 1rem 0;">
                        <div style="color: #6B7280; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">Expert Veterinary Guidance</div>
                        <div class="result-advice">{advice}</div>
                    </div>
                    """)
                    
                    render_html("<br>")
                    st.markdown('<h3 style="color:#f8fafc; font-size:1.25rem; font-family: Manrope;">Health Status Analysis</h3>', unsafe_allow_html=True)
                    
                    healthy_pct = healthy_prob * 100
                    unhealthy_pct = unhealthy_prob * 100

                    graph_html = f"""
                    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 20px; padding: 1.75rem; margin-top: 0.5rem; box-shadow: 0 8px 24px rgba(0,0,0,0.08);">
                        <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
                            <div style="flex: 1; background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 14px; padding: 1.1rem; text-align: center;">
                                <div style="font-size: 0.82rem; color: #047857; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Healthy (No Symptoms)</div>
                                <div style="font-family: Manrope; font-size: 2rem; font-weight: 800; color: #059669; margin-top: 0.25rem;">{healthy_pct:.1f}%</div>
                            </div>
                            <div style="flex: 1; background: #FEF2F2; border: 1px solid #FECACA; border-radius: 14px; padding: 1.1rem; text-align: center;">
                                <div style="font-size: 0.82rem; color: #B91C1C; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Unhealthy (Disease Symptoms)</div>
                                <div style="font-family: Manrope; font-size: 2rem; font-weight: 800; color: #DC2626; margin-top: 0.25rem;">{unhealthy_pct:.1f}%</div>
                            </div>
                        </div>
                        <div style="margin-bottom: 1.25rem;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-size: 0.95rem; font-weight: 700; color: #1F2937;">
                                <span>🟢 Healthy (No Symptoms)</span>
                                <span style="color: #059669;">{healthy_pct:.1f}%</span>
                            </div>
                            <div style="width: 100%; background: #F3F4F6; border-radius: 8px; height: 16px; overflow: hidden;">
                                <div style="width: {healthy_pct:.1f}%; background: linear-gradient(90deg, #10B981 0%, #059669 100%); height: 100%; border-radius: 8px;"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-size: 0.95rem; font-weight: 700; color: #1F2937;">
                                <span>🔴 Unhealthy (Disease Symptoms)</span>
                                <span style="color: #DC2626;">{unhealthy_pct:.1f}%</span>
                            </div>
                            <div style="width: 100%; background: #F3F4F6; border-radius: 8px; height: 16px; overflow: hidden;">
                                <div style="width: {unhealthy_pct:.1f}%; background: linear-gradient(90deg, #FCA5A5 0%, #EF4444 100%); height: 100%; border-radius: 8px;"></div>
                            </div>
                        </div>
                    </div>
                    """
                    render_html(graph_html)
                    
                    render_html(f"""
                    <div style="background: #FFFFFF; padding: 1.25rem; border-radius: 16px; border-left: 4px solid #10B981; margin-top: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                        <div style="color: #374151; font-size: 0.95rem; line-height: 1.6;">
                            <b>Analysis Explanation:</b> This histogram groups the AI model's raw probabilities into two overall categories: 
                            <b>Healthy</b> and <b>Unhealthy</b>. 
                            The model estimates a <b>{unhealthy_prob * 100:.1f}%</b> probability that the animal exhibits symptoms of the selected disease, 
                            and a <b>{healthy_prob * 100:.1f}%</b> probability that the animal is healthy.
                        </div>
                    </div>
                    """)

                except Exception as e:
                    st.error(f"An error occurred during examination: {str(e)}")

                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)


# ═══════════════════════════════════════════════
#                ROUTER & SPLASH
# ═══════════════════════════════════════════════
if "splashed" not in st.session_state:
    st.session_state.splashed = False

if not st.session_state.splashed:
    render_html("<br><br><br>")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        logo_path = os.path.join(BASE_DIR, "cattlesense_logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        render_html("<h2 style='text-align: center; color: #FFFFFF; font-family: Manrope;'>Initializing CattleSense...</h2>")
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
    elif st.session_state.page == "chatbot":
        render_chatbot()
    elif st.session_state.page == "detect":
        render_detect()
    elif st.session_state.page == "detect_internal":
        render_detect_internal()
