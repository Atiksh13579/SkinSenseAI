import streamlit as st
import anthropic
import base64
from PIL import Image
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkinSense – Ingredient Analyzer",
    page_icon="🧴",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@300;400;500;600&display=swap');

/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #fdf6f0 0%, #f0ece8 100%);
}
[data-testid="stHeader"] { background: transparent; }

/* Main card */
.main-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 2.5rem 2.8rem;
    box-shadow: 0 4px 30px rgba(0,0,0,0.06);
    margin-bottom: 2rem;
}

/* Hero */
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: #1a1a2e;
    letter-spacing: -0.5px;
    margin-bottom: 0.2rem;
}
.hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    color: #6b7280;
    font-weight: 300;
    margin-bottom: 1.8rem;
}
.accent-dot { color: #d4845a; }

/* Section label */
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 0.5rem;
}

/* Rating badge */
.rating-badge {
    display: inline-block;
    padding: 0.4rem 1.1rem;
    border-radius: 50px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 1.05rem;
    margin-bottom: 1rem;
}
.rating-great { background: #d1fae5; color: #065f46; }
.rating-good  { background: #dbeafe; color: #1e40af; }
.rating-avg   { background: #fef3c7; color: #92400e; }
.rating-poor  { background: #fee2e2; color: #991b1b; }

/* Ingredient pills */
.pill-container { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-bottom: 1rem; }
.pill {
    padding: 0.3rem 0.8rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}
.pill-good { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
.pill-bad  { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
.pill-neutral { background: #f3f4f6; color: #374151; border: 1px solid #d1d5db; }

/* Divider */
.soft-divider { border: none; border-top: 1px solid #f0ece8; margin: 1.5rem 0; }

/* Streamlit widget overrides */
[data-testid="stTextArea"] textarea {
    border-radius: 12px !important;
    border: 1.5px solid #e5e7eb !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    background: #fafafa !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #d4845a !important;
    box-shadow: 0 0 0 3px rgba(212,132,90,0.12) !important;
}
div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 1.5px solid #e5e7eb !important;
    background: #fafafa !important;
}
[data-testid="stMultiSelect"] span {
    background: #fff1eb !important;
    color: #7c3a0d !important;
}
.stButton > button {
    background: linear-gradient(135deg, #d4845a, #c06b3f) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 2rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed #e5e7eb !important;
    border-radius: 16px !important;
    background: #fafafa !important;
    padding: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Helper: call Claude ───────────────────────────────────────────────────────
def analyze_with_claude(ingredients_text: str, skin_type: str, concerns: list[str], api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    concerns_str = ", ".join(concerns) if concerns else "None specified"

    prompt = f"""You are a dermatologist-level skincare ingredient expert. Analyze the following product ingredients for a user with the given skin profile.

INGREDIENTS LIST:
{ingredients_text}

USER SKIN PROFILE:
- Skin Type: {skin_type}
- Skin Concerns: {concerns_str}

Provide a structured analysis in this EXACT format (use these exact headers):

## OVERALL RATING
Give a rating out of 10 (e.g., 7.5/10) and one sentence verdict.

## BENEFICIAL INGREDIENTS
List each beneficial ingredient as: **Ingredient Name** – why it's good for this user's skin type/concerns. (Use bullet points)

## HARMFUL / CONCERNING INGREDIENTS
List each problematic ingredient as: **Ingredient Name** – why it's concerning or bad for this user. If none, say "None detected." (Use bullet points)

## NEUTRAL INGREDIENTS
Briefly list ingredients that are neither particularly good nor bad.

## PERSONALIZED ADVICE
2–3 sentences of specific advice for this user based on their skin type and concerns.

Be specific, evidence-based, and concise. Focus especially on how ingredients interact with the user's specific skin type ({skin_type}) and concerns ({concerns_str})."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def extract_ingredients_from_image(image_bytes: bytes, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": "Extract ONLY the ingredients list from this skincare product image. Return just the raw ingredients text, comma-separated, exactly as they appear. If you cannot find an ingredients list, say 'NO_INGREDIENTS_FOUND'."},
            ],
        }],
    )
    return response.content[0].text


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-card">
  <div class="hero-title">SkinSense<span class="accent-dot">.</span></div>
  <div class="hero-sub">Decode your skincare — ingredient by ingredient</div>
</div>
""", unsafe_allow_html=True)

# API Key
with st.expander("🔑 Enter your Anthropic API Key", expanded=not st.session_state.get("api_key")):
    api_key = st.text_input("API Key", type="password", placeholder="sk-ant-...", key="api_key_input")
    st.caption("Get a free key at [console.anthropic.com](https://console.anthropic.com). Your key is never stored.")
    if api_key:
        st.session_state["api_key"] = api_key

# ── Step 1: Ingredients ───────────────────────────────────────────────────────
st.markdown('<div class="section-label">Step 1 — Ingredients</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📷 Scan / Upload Image", "✍️ Paste Text"])

scanned_ingredients = ""
with tab1:
    uploaded = st.file_uploader("Upload a photo of the product label", type=["jpg", "jpeg", "png", "webp"])
    if uploaded:
        img_bytes = uploaded.read()
        st.image(img_bytes, caption="Uploaded label", use_container_width=True)
        if st.button("Extract Ingredients from Image", key="extract_btn"):
            if not st.session_state.get("api_key"):
                st.error("Please enter your API key first.")
            else:
                with st.spinner("Reading label…"):
                    result = extract_ingredients_from_image(img_bytes, st.session_state["api_key"])
                    if "NO_INGREDIENTS_FOUND" in result:
                        st.warning("Couldn't detect an ingredients list. Try a clearer photo or paste manually.")
                    else:
                        st.session_state["scanned_text"] = result
                        st.success("Ingredients extracted!")
                        st.text_area("Extracted ingredients (edit if needed)", value=result, key="extracted_display", height=120)

with tab2:
    manual_text = st.text_area(
        "Paste the full ingredients list here",
        placeholder="Water, Glycerin, Niacinamide, Sodium Hyaluronate, Dimethicone…",
        height=130,
        key="manual_ingredients",
    )

# Resolve final ingredients text
ingredients_input = (
    st.session_state.get("scanned_text", "") or manual_text or ""
).strip()

st.markdown("<hr class='soft-divider'>", unsafe_allow_html=True)

# ── Step 2: Skin Profile ──────────────────────────────────────────────────────
st.markdown('<div class="section-label">Step 2 — Your Skin Profile</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    skin_type = st.selectbox(
        "Skin Type",
        ["Normal", "Oily", "Dry", "Combination", "Sensitive", "Acne-prone", "Mature"],
    )
with col2:
    concerns = st.multiselect(
        "Skin Concerns (choose all that apply)",
        ["Acne / Breakouts", "Hyperpigmentation", "Dark Spots", "Fine Lines & Wrinkles",
         "Redness / Rosacea", "Large Pores", "Dullness", "Dehydration",
         "Eczema / Dermatitis", "Sun Damage", "Uneven Texture", "Blackheads"],
    )

st.markdown("<hr class='soft-divider'>", unsafe_allow_html=True)

# ── Analyze Button ────────────────────────────────────────────────────────────
analyze_clicked = st.button("🔍 Analyze Ingredients")

if analyze_clicked:
    if not st.session_state.get("api_key"):
        st.error("Please enter your Anthropic API key in the section above.")
    elif not ingredients_input:
        st.warning("Please provide an ingredients list — upload a photo or paste the text.")
    else:
        with st.spinner("Analyzing ingredients for your skin profile…"):
            try:
                result = analyze_with_claude(
                    ingredients_input, skin_type, concerns,
                    st.session_state["api_key"]
                )
                st.session_state["analysis"] = result
            except Exception as e:
                st.error(f"Analysis failed: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.get("analysis"):
    analysis = st.session_state["analysis"]

    st.markdown("---")
    st.markdown('<div class="section-label">Analysis Results</div>', unsafe_allow_html=True)

    # Pretty render the markdown from Claude
    st.markdown(analysis)

    st.markdown("---")
    st.download_button(
        "⬇️ Download Analysis",
        data=analysis,
        file_name="skinsense_analysis.txt",
        mime="text/plain",
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#9ca3af; font-size:0.78rem; margin-top:3rem; font-family:'Inter',sans-serif;">
  SkinSense is for informational purposes only and is not medical advice.<br>
  Always consult a dermatologist for persistent skin concerns.
</div>
""", unsafe_allow_html=True)
