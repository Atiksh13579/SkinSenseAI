import streamlit as st
import anthropic
import base64
import json
import re
import io
from PIL import Image, UnidentifiedImageError

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkinSense – Ingredient Analyzer",
    page_icon="🧴",
    layout="centered",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@300;400;500;600&display=swap');

[data-testid="stAppViewContainer"] { background: linear-gradient(135deg,#fdf6f0,#f0ece8); }
[data-testid="stHeader"] { background: transparent; }

/* ── GLOBAL BLACK TEXT ── */
p,span,div,label,li,h1,h2,h3,h4,
[data-testid="stMarkdownContainer"] *,
[data-baseweb="radio"] label,[data-baseweb="radio"] span,
[data-baseweb="select"] *,[data-baseweb="tab"] span,
[data-testid="stWidgetLabel"] *,[data-testid="stCaptionContainer"],
[data-testid="stRadio"] label,[data-testid="stRadio"] p,
[role="tab"],[role="option"] { color:#1a1a1a !important; }

.main-card { background:#fff; border-radius:20px; padding:2.5rem 2.8rem;
             box-shadow:0 4px 30px rgba(0,0,0,.06); margin-bottom:2rem; }
.hero-title { font-family:'DM Serif Display',serif; font-size:2.6rem;
              color:#1a1a2e; letter-spacing:-.5px; margin-bottom:.2rem; }
.hero-sub   { font-family:'Inter',sans-serif; font-size:1rem; color:#6b7280;
              font-weight:300; margin-bottom:1.8rem; }
.accent-dot { color:#d4845a; }
.section-label { font-family:'Inter',sans-serif; font-size:.72rem; font-weight:600;
                 letter-spacing:1.2px; text-transform:uppercase; color:#9ca3af;
                 margin-bottom:.5rem; }

/* analysis */
.analysis-box,.analysis-box * { color:#1a1a1a !important; }
.analysis-box h2 { font-family:'DM Serif Display',serif !important; font-size:1.1rem !important;
                   color:#1a1a2e !important; margin-top:1.2rem !important;
                   margin-bottom:.35rem !important; border-bottom:2px solid #f0ece8;
                   padding-bottom:.2rem; }
.analysis-box p,.analysis-box li { font-family:'Inter',sans-serif !important;
    font-size:.87rem !important; line-height:1.65 !important; color:#1a1a1a !important; }
.analysis-box strong { color:#1a1a2e !important; font-weight:600 !important; }

/* category tab strip */
.cat-tab-wrap { display:flex; gap:.5rem; flex-wrap:wrap; margin-bottom:1.2rem; }
.cat-tab { padding:.35rem .9rem; border-radius:50px; font-size:.78rem;
           font-family:'Inter',sans-serif; font-weight:600; cursor:pointer;
           border:1.5px solid #e5d5c8; background:#fff; color:#7c3a0d !important; }
.cat-tab.active { background:#d4845a; color:#fff !important; border-color:#d4845a; }

/* product cards */
.rec-card { background:#fff8f4; border:1.5px solid #f5d6c4; border-radius:16px;
            padding:1.4rem 1.8rem; margin-top:1rem; }
.rec-card h3 { font-family:'DM Serif Display',serif; font-size:1.05rem;
               color:#7c3a0d; margin-bottom:.8rem; }
.product-card { background:#fff; border:1.5px solid #f0ddd4; border-radius:14px;
                padding:1.1rem 1.3rem; margin-bottom:.9rem;
                box-shadow:0 2px 10px rgba(0,0,0,.04); }
.product-name { font-family:'DM Serif Display',serif; font-size:1rem;
                color:#1a1a2e; margin-bottom:.3rem; }
.product-meta { display:flex; gap:.5rem; flex-wrap:wrap; margin-bottom:.6rem; align-items:center; }
.badge { padding:.2rem .7rem; border-radius:50px; font-size:.73rem;
         font-family:'Inter',sans-serif; font-weight:600; }
.badge-price  { background:#e0f2fe; color:#075985 !important; }
.badge-rating { background:#fef9c3; color:#713f12 !important; }
.badge-cat    { background:#f3e8ff; color:#6b21a8 !important; }
.pst { font-family:'Inter',sans-serif; font-size:.68rem; font-weight:700;
       letter-spacing:1px; text-transform:uppercase; color:#9ca3af; margin:.55rem 0 .2rem; }
.pbody { font-family:'Inter',sans-serif; font-size:.84rem; color:#374151; line-height:1.6; }
.pro-tip { background:linear-gradient(135deg,#fff7ed,#fef3c7);
           border-left:3px solid #d4845a; border-radius:8px; padding:.65rem 1rem;
           margin-top:.5rem; font-family:'Inter',sans-serif; font-size:.84rem;
           color:#7c3a0d; font-weight:500; }

/* misc */
.soft-divider { border:none; border-top:1px solid #f0ece8; margin:1.5rem 0; }
[data-testid="stTextArea"] textarea { border-radius:12px !important;
    border:1.5px solid #e5e7eb !important; font-family:'Inter',sans-serif !important;
    font-size:.9rem !important; background:#fafafa !important; }
div[data-baseweb="select"]>div { border-radius:12px !important;
    border:1.5px solid #e5e7eb !important; background:#fafafa !important; }
[data-testid="stMultiSelect"] span { background:#fff1eb !important; color:#7c3a0d !important; }
.stButton>button { background:linear-gradient(135deg,#d4845a,#c06b3f) !important;
    color:white !important; border:none !important; border-radius:12px !important;
    padding:.65rem 2rem !important; font-family:'Inter',sans-serif !important;
    font-weight:600 !important; font-size:.95rem !important; width:100% !important; }
.stButton>button:hover { opacity:.88 !important; }
[data-testid="stFileUploader"] { border:2px dashed #e5e7eb !important;
    border-radius:16px !important; background:#fafafa !important; padding:1rem !important; }
.info-box { background:#f0f9ff; border:1px solid #bae6fd; border-radius:10px;
            padding:.7rem 1rem; font-size:.83rem; color:#0c4a6e !important;
            font-family:'Inter',sans-serif; margin-bottom:.8rem; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

SUPPORTED_TYPES = ["jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff", "tif", "heic", "avif"]

def normalise_image(file_bytes: bytes, filename: str = "") -> tuple[bytes, str]:
    """Convert any uploaded image to JPEG bytes. Returns (jpeg_bytes, error_str)."""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        # Convert palette/RGBA/P modes to RGB for JPEG
        if img.mode in ("RGBA", "P", "LA"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return buf.getvalue(), ""
    except UnidentifiedImageError:
        return b"", "Could not read image. Please upload a clearer photo."
    except Exception as e:
        return b"", f"Image error: {e}"


def extract_from_image(image_bytes: bytes, api_key: str) -> str:
    """Ask Claude to extract the ingredients list from an image."""
    client = anthropic.Anthropic(api_key=api_key)
    b64 = base64.standard_b64encode(image_bytes).decode()
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=800,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
            {"type": "text", "text": (
                "Look at this skincare product label image. "
                "Extract ONLY the ingredients list exactly as printed, comma-separated. "
                "If there is no ingredients list visible, reply with exactly: NO_INGREDIENTS_FOUND"
            )},
        ]}],
    )
    return resp.content[0].text.strip()


def fetch_url_ingredients(url: str, api_key: str) -> str:
    """Given a URL (from a QR code), scrape or ask Claude to extract ingredients."""
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")[:12000]
    except Exception as e:
        return f"URL_ERROR: Could not open the URL — {e}"

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=600,
        messages=[{"role": "user", "content": (
            f"From the following webpage HTML, extract ONLY the skincare product ingredients list, "
            f"comma-separated. If not found, reply: NO_INGREDIENTS_FOUND\n\nHTML:\n{html}"
        )}],
    )
    return resp.content[0].text.strip()


def decode_qr(image_bytes: bytes) -> str:
    """Decode QR code from image bytes. Returns URL string or empty string."""
    try:
        from pyzbar.pyzbar import decode as pyzbar_decode
        img = Image.open(io.BytesIO(image_bytes))
        results = pyzbar_decode(img)
        for r in results:
            data = r.data.decode("utf-8", errors="ignore").strip()
            if data:
                return data
        return ""
    except ImportError:
        return "PYZBAR_MISSING"
    except Exception:
        return ""


def analyze_with_claude(ingredients_text: str, skin_type: str, concerns: list, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    concerns_str = ", ".join(concerns) if concerns else "None specified"
    prompt = f"""You are a skincare ingredient expert. Give a concise, easy-to-read analysis.

INGREDIENTS: {ingredients_text}
SKIN TYPE: {skin_type}
CONCERNS: {concerns_str}

Use EXACTLY these section headers. Keep every bullet under 15 words. Max 4 bullets per section.

## ⭐ Overall Rating
X/10 — one sentence verdict.

## ✅ Good Ingredients
• **Name** — one short reason it helps this user.

## ⚠️ Harmful / Concerning
• **Name** — one short reason it's bad. If none: write "None detected."

## 〰️ Neutral Ingredients
One line, comma-separated names only.

## 💡 Verdict & Tip
2 short sentences: verdict + one tip for {skin_type} skin."""
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=900,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def recommend_products(analysis_text: str, skin_type: str, concerns: list,
                       price_range: str, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    concerns_str = ", ".join(concerns) if concerns else "None specified"
    analysis_short = analysis_text[:700]

    prompt = f"""You are a skincare product expert for the Indian market.

USER: Skin type={skin_type} | Concerns={concerns_str} | Budget={price_range}
ANALYSIS SUMMARY: {analysis_short}

Recommend 6 real Indian-market products — one per category:
1. Face Wash / Cleanser
2. Moisturiser
3. Serum / Treatment
4. Sunscreen / SPF
5. Toner / Essence
6. Eye Cream / Spot Treatment

OUTPUT ONLY raw JSON starting with {{ — no markdown, no explanation:
{{
  "products": [
    {{
      "category": "Face Wash / Cleanser",
      "name": "Product Name",
      "brand": "Brand",
      "price": "Rs. XXX - Rs. YYY",
      "rating": "8.5/10",
      "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
      "why_better": "One sentence why better for this user.",
      "hero_ingredients": "Ingredient A, Ingredient B, Ingredient C",
      "where_to_buy": "Nykaa, Amazon India"
    }}
  ],
  "pro_tip": "One specific tip for {skin_type} skin."
}}

RULES:
- All 6 products MUST fit within {price_range}
- Only real, widely available Indian market products
- All string values under 20 words
- Output ONLY the JSON object"""

    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1800,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    raw = re.sub(r"^```[a-z]*\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw).strip()
    m = re.search(r'\{[\s\S]*\}', raw)
    if m:
        raw = m.group(0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"products": [], "pro_tip": "Could not load recommendations. Please retry.", "error": raw[:200]}


def render_product_cards(products: list) -> str:
    """Build HTML for product cards grouped by category."""
    if not products:
        return ""
    # Group by category
    from collections import defaultdict
    grouped = defaultdict(list)
    for p in products:
        grouped[p.get("category", "Other")].append(p)

    cat_icons = {
        "Face Wash / Cleanser":      "🧼",
        "Moisturiser":               "💧",
        "Serum / Treatment":         "💊",
        "Sunscreen / SPF":           "☀️",
        "Toner / Essence":           "🌿",
        "Eye Cream / Spot Treatment":"👁️",
        "Other":                     "🧴",
    }

    html = ""
    for cat, items in grouped.items():
        icon = cat_icons.get(cat, "🧴")
        html += f'<div style="margin-bottom:1.4rem;"><div class="pst">{icon} {cat}</div>'
        for p in items:
            benefits_li = "".join(
                f"<li style='color:#374151;font-size:.83rem;line-height:1.55;'>{b}</li>"
                for b in p.get("key_benefits", [])
            )
            html += f"""
<div class="product-card">
  <div class="product-name">{p.get('name','')}</div>
  <div style="font-size:.76rem;color:#6b7280;margin-bottom:.45rem;font-family:'Inter',sans-serif;">by {p.get('brand','')}</div>
  <div class="product-meta">
    <span class="badge badge-cat">{icon} {cat}</span>
    <span class="badge badge-price">💰 {p.get('price','')}</span>
    <span class="badge badge-rating">⭐ {p.get('rating','')}</span>
  </div>
  <div class="pst">Why it's better for you</div>
  <div class="pbody">{p.get('why_better','')}</div>
  <div class="pst">Key Benefits</div>
  <ul style="padding-left:1rem;margin:.1rem 0 .3rem;">{benefits_li}</ul>
  <div class="pst">Hero Ingredients</div>
  <div class="pbody">{p.get('hero_ingredients','')}</div>
  <div class="pst">Where to Buy</div>
  <div class="pbody">🛒 {p.get('where_to_buy','')}</div>
</div>"""
        html += "</div>"
    return html


# ═══════════════════════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-card">
  <div class="hero-title">SkinSense<span class="accent-dot">.</span></div>
  <div class="hero-sub">Decode your skincare — ingredient by ingredient</div>
</div>""", unsafe_allow_html=True)

# ── API Key ───────────────────────────────────────────────────────────────────
with st.expander("🔑 Enter your Anthropic API Key", expanded=not st.session_state.get("api_key")):
    api_key = st.text_input("API Key", type="password", placeholder="sk-ant-...", key="api_key_input")
    st.caption("Get a free key at [console.anthropic.com](https://console.anthropic.com). Never stored.")
    if api_key:
        st.session_state["api_key"] = api_key

# ── Step 1: Ingredients ───────────────────────────────────────────────────────
st.markdown('<div class="section-label">Step 1 — Add Ingredients</div>', unsafe_allow_html=True)

tab_img, tab_qr, tab_txt = st.tabs(["📷 Upload Label Photo", "📲 Scan QR Code", "✍️ Paste Text"])

# ── TAB 1: Upload any image format ───────────────────────────────────────────
with tab_img:
    st.markdown(
        '<div class="info-box">Supports JPG, PNG, WEBP, BMP, GIF, TIFF, HEIC, AVIF — any format works.</div>',
        unsafe_allow_html=True
    )
    uploaded = st.file_uploader(
        "Upload product label (any image format)",
        type=SUPPORTED_TYPES,
        key="label_upload"
    )
    if uploaded:
        raw_bytes = uploaded.read()
        jpeg_bytes, err = normalise_image(raw_bytes, uploaded.name)
        if err:
            st.error(err)
        else:
            st.image(jpeg_bytes, caption="Uploaded label", use_container_width=True)
            if st.button("Extract Ingredients from Photo", key="extract_label"):
                if not st.session_state.get("api_key"):
                    st.error("Please enter your API key first.")
                else:
                    with st.spinner("Reading label…"):
                        result = extract_from_image(jpeg_bytes, st.session_state["api_key"])
                        if "NO_INGREDIENTS_FOUND" in result:
                            st.warning("No ingredients list found. Try a clearer photo or paste manually.")
                        else:
                            st.session_state["scanned_text"] = result
                            st.session_state.pop("recommendation", None)
                            st.success("✅ Ingredients extracted!")
            if st.session_state.get("scanned_text"):
                st.text_area("Extracted ingredients (edit if needed)",
                             value=st.session_state["scanned_text"],
                             key="extracted_display", height=110)

# ── TAB 2: QR Code scan ───────────────────────────────────────────────────────
with tab_qr:
    st.markdown(
        '<div class="info-box">Upload a photo of the product\'s QR code. '
        'SkinSense will decode it, visit the product page, and extract ingredients automatically.</div>',
        unsafe_allow_html=True
    )
    qr_file = st.file_uploader("Upload QR code image", type=SUPPORTED_TYPES, key="qr_upload")
    if qr_file:
        qr_bytes = qr_file.read()
        jpeg_qr, err = normalise_image(qr_bytes)
        if err:
            st.error(err)
        else:
            st.image(jpeg_qr, caption="QR code image", width=220)
            if st.button("Decode QR & Fetch Ingredients", key="decode_qr"):
                if not st.session_state.get("api_key"):
                    st.error("Please enter your API key first.")
                else:
                    with st.spinner("Decoding QR code…"):
                        qr_result = decode_qr(qr_bytes)

                    if qr_result == "PYZBAR_MISSING":
                        # Fallback: ask Claude to read the QR visually
                        st.info("Using AI vision to decode QR…")
                        with st.spinner("Reading QR with AI…"):
                            client = anthropic.Anthropic(api_key=st.session_state["api_key"])
                            b64 = base64.standard_b64encode(jpeg_qr).decode()
                            vresp = client.messages.create(
                                model="claude-sonnet-4-6", max_tokens=200,
                                messages=[{"role": "user", "content": [
                                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                                    {"type": "text", "text": "What URL or text is encoded in this QR code? Reply with only the URL or text, nothing else."},
                                ]}],
                            )
                            qr_result = vresp.content[0].text.strip()

                    if not qr_result or qr_result.startswith("URL_ERROR"):
                        st.warning("Couldn't decode QR code. Try a clearer photo or paste ingredients manually.")
                    elif qr_result.startswith("http"):
                        st.success(f"QR decoded → {qr_result}")
                        with st.spinner("Fetching product page for ingredients…"):
                            ing = fetch_url_ingredients(qr_result, st.session_state["api_key"])
                            if "NO_INGREDIENTS_FOUND" in ing or ing.startswith("URL_ERROR"):
                                st.warning("Couldn't extract ingredients from the product page. Try pasting manually.")
                                st.text_input("You can paste the URL here to check:", value=qr_result)
                            else:
                                st.session_state["scanned_text"] = ing
                                st.session_state.pop("recommendation", None)
                                st.success("✅ Ingredients fetched from product page!")
                    else:
                        # QR contains text (maybe ingredients directly or product name)
                        st.info(f"QR text: {qr_result}")
                        st.session_state["scanned_text"] = qr_result
                        st.success("✅ QR content loaded!")

            if st.session_state.get("scanned_text"):
                st.text_area("Extracted ingredients (edit if needed)",
                             value=st.session_state["scanned_text"],
                             key="qr_extracted_display", height=110)

# ── TAB 3: Paste text ─────────────────────────────────────────────────────────
with tab_txt:
    manual_text = st.text_area(
        "Paste the full ingredients list here",
        placeholder="Water, Glycerin, Niacinamide, Sodium Hyaluronate, Dimethicone…",
        height=130, key="manual_ingredients",
    )

ingredients_input = (
    st.session_state.get("scanned_text", "") or manual_text or ""
).strip()

st.markdown("<hr class='soft-divider'>", unsafe_allow_html=True)

# ── Step 2: Skin Profile ──────────────────────────────────────────────────────
st.markdown('<div class="section-label">Step 2 — Your Skin Profile</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    skin_type = st.selectbox("Skin Type",
        ["Normal","Oily","Dry","Combination","Sensitive","Acne-prone","Mature"])
with col2:
    concerns = st.multiselect("Skin Concerns",
        ["Acne / Breakouts","Hyperpigmentation","Dark Spots","Fine Lines & Wrinkles",
         "Redness / Rosacea","Large Pores","Dullness","Dehydration",
         "Eczema / Dermatitis","Sun Damage","Uneven Texture","Blackheads"])

st.markdown("<hr class='soft-divider'>", unsafe_allow_html=True)

# ── Step 3: Budget ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Step 3 — Budget for Recommendations</div>', unsafe_allow_html=True)
price_options = {
    "💚 Under ₹500  (Drugstore)":       "Under ₹500 (drugstore / budget-friendly)",
    "💛 ₹500 – ₹1,500  (Mid-range)":   "₹500 to ₹1,500 (mid-range)",
    "🧡 ₹1,500 – ₹4,000  (Premium)":   "₹1,500 to ₹4,000 (premium)",
    "❤️  ₹4,000+  (Luxury)":            "Above ₹4,000 (luxury or medical-grade)",
    "🌈 Any budget":                     "Any price range",
}
price_label = st.radio("Budget per product?", list(price_options.keys()), index=1, horizontal=True)
price_range = price_options[price_label]

st.markdown("<hr class='soft-divider'>", unsafe_allow_html=True)

# ── Analyze ───────────────────────────────────────────────────────────────────
if st.button("🔍 Analyze Ingredients"):
    if not st.session_state.get("api_key"):
        st.error("Please enter your Anthropic API key above.")
    elif not ingredients_input:
        st.warning("Please provide an ingredients list.")
    else:
        with st.spinner("Analyzing for your skin profile…"):
            try:
                analysis = analyze_with_claude(ingredients_input, skin_type, concerns,
                                               st.session_state["api_key"])
                st.session_state.update({
                    "analysis": analysis,
                    "skin_type": skin_type,
                    "concerns": concerns,
                    "price_range": price_range,
                })
                st.session_state.pop("recommendation", None)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.get("analysis"):
    analysis  = st.session_state["analysis"]
    s_type    = st.session_state.get("skin_type", skin_type)
    s_concern = st.session_state.get("concerns", concerns)
    s_price   = st.session_state.get("price_range", price_range)

    st.markdown("---")
    col_analysis, col_rec = st.columns([1.05, 1], gap="large")

    # ── Left: Analysis ────────────────────────────────────────────────────────
    with col_analysis:
        st.markdown('<div class="section-label">📋 Ingredient Analysis</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="analysis-box">{analysis.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("⬇️ Download Analysis", data=analysis,
                           file_name="skinsense_analysis.txt", mime="text/plain")

    # ── Right: Recommendations ────────────────────────────────────────────────
    with col_rec:
        st.markdown('<div class="section-label">✨ Better Product Picks by Category</div>',
                    unsafe_allow_html=True)

        if not st.session_state.get("recommendation"):
            st.caption(f"Budget: **{s_price}**")
            if st.button("🔎 Find Better Products for Me", key="rec_btn"):
                with st.spinner("Finding alternatives across categories…"):
                    try:
                        data = recommend_products(analysis, s_type, s_concern, s_price,
                                                  st.session_state["api_key"])
                        st.session_state["recommendation"] = data
                        st.rerun()
                    except Exception as e:
                        st.error(f"Recommendation failed: {e}")
        else:
            data     = st.session_state["recommendation"]
            products = data.get("products", [])
            pro_tip  = data.get("pro_tip", "")

            if not products:
                st.warning("Couldn't load recommendations. Please retry.")
                if st.button("🔄 Retry", key="retry_rec"):
                    st.session_state.pop("recommendation", None)
                    st.rerun()
            else:
                cards_html = render_product_cards(products)
                tip_html   = f'<div class="pro-tip">💡 {pro_tip}</div>' if pro_tip else ""
                st.markdown(
                    f'<div class="rec-card"><h3>🛍️ Recommended Alternatives</h3>'
                    f'{cards_html}{tip_html}</div>',
                    unsafe_allow_html=True
                )

                # Plain-text download
                plain = "SKINSENSE — PRODUCT RECOMMENDATIONS\n" + "="*40 + "\n\n"
                for p in products:
                    plain += f"[{p.get('category','')}]\n"
                    plain += f"Product : {p.get('name','')} by {p.get('brand','')}\n"
                    plain += f"Price   : {p.get('price','')}\n"
                    plain += f"Rating  : {p.get('rating','')}\n"
                    plain += f"Why better: {p.get('why_better','')}\n"
                    plain += f"Benefits: {'; '.join(p.get('key_benefits',[]))}\n"
                    plain += f"Hero ingredients: {p.get('hero_ingredients','')}\n"
                    plain += f"Where to buy: {p.get('where_to_buy','')}\n"
                    plain += "-"*40 + "\n"
                if pro_tip:
                    plain += f"\n💡 Pro tip: {pro_tip}\n"

                st.download_button("⬇️ Download Recommendations", data=plain,
                                   file_name="skinsense_recommendations.txt",
                                   mime="text/plain", key="dl_rec")
                if st.button("🔄 Refresh Picks", key="refresh_rec"):
                    st.session_state.pop("recommendation", None)
                    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#9ca3af;font-size:.78rem;margin-top:3rem;font-family:'Inter',sans-serif;">
  SkinSense is for informational purposes only and is not medical advice.<br>
  Always consult a dermatologist for persistent skin concerns.
</div>""", unsafe_allow_html=True)
