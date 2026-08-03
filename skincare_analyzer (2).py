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

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #fdf6f0 0%, #f0ece8 100%);
}
[data-testid="stHeader"] { background: transparent; }

.main-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 2.5rem 2.8rem;
    box-shadow: 0 4px 30px rgba(0,0,0,0.06);
    margin-bottom: 2rem;
}
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

.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 0.5rem;
}

/* ── FORCE ALL ANALYSIS & RECOMMENDATION TEXT TO BLACK ── */
.analysis-box, .analysis-box * {
    color: #1a1a1a !important;
}
.analysis-box h2 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.25rem !important;
    color: #1a1a2e !important;
    margin-top: 1.4rem !important;
    margin-bottom: 0.5rem !important;
    border-bottom: 2px solid #f0ece8;
    padding-bottom: 0.3rem;
}
.analysis-box p, .analysis-box li {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    line-height: 1.7 !important;
    color: #1a1a1a !important;
}
.analysis-box strong {
    color: #1a1a2e !important;
    font-weight: 600 !important;
}

/* Recommendation outer wrapper */
.rec-card {
    background: #fff8f4;
    border: 1.5px solid #f5d6c4;
    border-radius: 16px;
    padding: 1.6rem 2rem;
    margin-top: 1rem;
}
.rec-card h3 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    color: #7c3a0d;
    margin-bottom: 0.8rem;
}
.rec-card p, .rec-card li {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: #1a1a1a !important;
    line-height: 1.7;
}

/* Individual product cards */
.product-card {
    background: #ffffff;
    border: 1.5px solid #f0ddd4;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.product-name {
    font-family: 'DM Serif Display', serif;
    font-size: 1.05rem;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}
.product-meta {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    margin-bottom: 0.7rem;
    align-items: center;
}
.badge {
    padding: 0.2rem 0.7rem;
    border-radius: 50px;
    font-size: 0.75rem;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
}
.badge-price  { background: #e0f2fe; color: #075985; }
.badge-rating { background: #fef9c3; color: #713f12; }
.product-section-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #9ca3af;
    margin: 0.6rem 0 0.25rem 0;
}
.product-body {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: #374151;
    line-height: 1.65;
}
.pro-tip-box {
    background: linear-gradient(135deg, #fff7ed, #fef3c7);
    border-left: 3px solid #d4845a;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-top: 0.5rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: #7c3a0d;
    font-weight: 500;
}

.soft-divider { border: none; border-top: 1px solid #f0ece8; margin: 1.5rem 0; }

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

[data-testid="stFileUploader"] {
    border: 2px dashed #e5e7eb !important;
    border-radius: 16px !important;
    background: #fafafa !important;
    padding: 1rem !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: Analyze ingredients ───────────────────────────────────────────────
def analyze_with_claude(ingredients_text: str, skin_type: str, concerns: list, api_key: str) -> str:
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


# ── Helper: Recommend better products ────────────────────────────────────────
def recommend_products(analysis_text: str, skin_type: str, concerns: list,
                       price_range: str, api_key: str) -> list:
    """Returns a list of product dicts + a pro_tip string."""
    import json
    client = anthropic.Anthropic(api_key=api_key)
    concerns_str = ", ".join(concerns) if concerns else "None specified"

    prompt = f"""You are an expert skincare consultant. Based on the ingredient analysis below, recommend exactly 3 real skincare products that are BETTER suited to this user's profile AND fall within their price range.

INGREDIENT ANALYSIS OF CURRENT PRODUCT:
{analysis_text}

USER SKIN PROFILE:
- Skin Type: {skin_type}
- Skin Concerns: {concerns_str}
- Budget / Price Range: {price_range}

Return ONLY a valid JSON object — no preamble, no markdown fences. Use this exact structure:
{{
  "products": [
    {{
      "name": "Full Product Name",
      "brand": "Brand Name",
      "price": "e.g. $12 – $18",
      "rating": "e.g. 8.5/10",
      "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
      "why_better": "2 sentences explaining why this is better than the scanned product for this user's skin type and concerns.",
      "hero_ingredients": "Comma-separated list of 3–5 hero ingredients and what each does.",
      "where_to_buy": "e.g. Sephora, Amazon, CVS"
    }}
  ],
  "pro_tip": "One powerful, specific skincare tip for this user's skin type and concerns."
}}

Rules:
- ONLY recommend real, widely available products
- All products MUST fit within the {price_range} budget
- Prioritise products that fix the weaknesses identified in the analysis
- Be specific with ingredient names — no vague claims
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    # Strip any accidental markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()
    data = json.loads(raw)
    return data


# ── Helper: Extract ingredients from image ────────────────────────────────────
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

# ── Step 3: Budget / Price Range ──────────────────────────────────────────────
st.markdown('<div class="section-label">Step 3 — Budget for Recommendations</div>', unsafe_allow_html=True)

price_options = {
    "💚 Under ₹500  (Drugstore)":         "Under ₹500 (drugstore / budget-friendly)",
    "💛 ₹500 – ₹1,500  (Mid-range)":     "₹500 to ₹1,500 (mid-range)",
    "🧡 ₹1,500 – ₹4,000  (Premium)":     "₹1,500 to ₹4,000 (premium / prestige)",
    "❤️  ₹4,000+  (Luxury / Medical)":    "Above ₹4,000 (luxury or medical-grade)",
    "🌈 Any budget":                       "Any price range",
}
price_label = st.radio(
    "What's your budget per product?",
    list(price_options.keys()),
    index=1,
    horizontal=True,
)
price_range = price_options[price_label]

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
                analysis = analyze_with_claude(
                    ingredients_input, skin_type, concerns,
                    st.session_state["api_key"]
                )
                st.session_state["analysis"] = analysis
                st.session_state["skin_type"] = skin_type
                st.session_state["concerns"] = concerns
                st.session_state["price_range"] = price_range
                # Clear old recommendation when re-analyzing
                st.session_state.pop("recommendation", None)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.get("analysis"):
    analysis = st.session_state["analysis"]

    st.markdown("---")

    # ── Two-column layout: Analysis | Recommendations ─────────────────────────
    col_analysis, col_rec = st.columns([1.1, 1], gap="large")

    with col_analysis:
        st.markdown('<div class="section-label">📋 Ingredient Analysis</div>', unsafe_allow_html=True)
        # Wrap in div that forces black text
        st.markdown(f'<div class="analysis-box">{analysis.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download Analysis",
            data=analysis,
            file_name="skinsense_analysis.txt",
            mime="text/plain",
        )

    with col_rec:
        st.markdown('<div class="section-label">✨ Better Product Picks</div>', unsafe_allow_html=True)

        if not st.session_state.get("recommendation"):
            budget_used = st.session_state.get("price_range", price_range)
            st.caption(f"Budget set to: **{budget_used}**")
            if st.button("🔎 Find Better Products for Me", key="rec_btn"):
                with st.spinner("Finding smarter alternatives in your budget…"):
                    try:
                        data = recommend_products(
                            analysis,
                            st.session_state.get("skin_type", skin_type),
                            st.session_state.get("concerns", concerns),
                            st.session_state.get("price_range", price_range),
                            st.session_state["api_key"]
                        )
                        st.session_state["recommendation"] = data
                        st.rerun()
                    except Exception as e:
                        st.error(f"Recommendation failed: {e}")
        else:
            data = st.session_state["recommendation"]
            products = data.get("products", [])
            pro_tip  = data.get("pro_tip", "")

            # Render each product as a rich card
            cards_html = ""
            for p in products:
                benefits_html = "".join(
                    f"<li style='color:#374151;font-size:0.84rem;line-height:1.6;'>{b}</li>"
                    for b in p.get("key_benefits", [])
                )
                cards_html += f"""
<div class="product-card">
  <div class="product-name">{p.get('name','')}</div>
  <div style="font-family:'Inter',sans-serif;font-size:0.78rem;color:#6b7280;margin-bottom:0.5rem;">by {p.get('brand','')}</div>
  <div class="product-meta">
    <span class="badge badge-price">💰 {p.get('price','')}</span>
    <span class="badge badge-rating">⭐ {p.get('rating','')}</span>
  </div>

  <div class="product-section-title">Why it's better for you</div>
  <div class="product-body">{p.get('why_better','')}</div>

  <div class="product-section-title">Key Benefits</div>
  <ul style="padding-left:1.1rem;margin:0 0 0.4rem 0;">{benefits_html}</ul>

  <div class="product-section-title">Hero Ingredients</div>
  <div class="product-body">{p.get('hero_ingredients','')}</div>

  <div class="product-section-title">Where to Buy</div>
  <div class="product-body">🛒 {p.get('where_to_buy','')}</div>
</div>"""

            tip_html = f'<div class="pro-tip-box">💡 {pro_tip}</div>' if pro_tip else ""

            st.markdown(
                f'<div class="rec-card"><h3>🛍️ Recommended Alternatives</h3>'
                f'{cards_html}{tip_html}</div>',
                unsafe_allow_html=True
            )

            # Build plain-text version for download
            import json
            plain = "SKINSENSE — PRODUCT RECOMMENDATIONS\n" + "="*40 + "\n\n"
            for p in products:
                plain += f"Product : {p.get('name','')} by {p.get('brand','')}\n"
                plain += f"Price   : {p.get('price','')}\n"
                plain += f"Rating  : {p.get('rating','')}\n"
                plain += f"Why better: {p.get('why_better','')}\n"
                plain += f"Key benefits: {'; '.join(p.get('key_benefits',[]))}\n"
                plain += f"Hero ingredients: {p.get('hero_ingredients','')}\n"
                plain += f"Where to buy: {p.get('where_to_buy','')}\n"
                plain += "-"*40 + "\n"
            if pro_tip:
                plain += f"\n💡 Pro tip: {pro_tip}\n"

            st.download_button(
                "⬇️ Download Recommendations",
                data=plain,
                file_name="skinsense_recommendations.txt",
                mime="text/plain",
                key="dl_rec"
            )
            if st.button("🔄 Refresh Picks", key="refresh_rec"):
                st.session_state.pop("recommendation", None)
                st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#9ca3af; font-size:0.78rem; margin-top:3rem; font-family:'Inter',sans-serif;">
  SkinSense is for informational purposes only and is not medical advice.<br>
  Always consult a dermatologist for persistent skin concerns.
</div>
""", unsafe_allow_html=True)
