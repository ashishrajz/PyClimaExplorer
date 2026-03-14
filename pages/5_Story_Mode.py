import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import html
import re
import requests
import json

# Quick tip: Be careful sharing API keys publicly! Consider moving to st.secrets for production.
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# ── Updated API Logic ──
def get_climate_history(lat, lng, mode="normal", context=None):
    if mode == "advanced":
        style_instructions = """
        Act as a PhD scholar explaining with hard facts, detailed data, and scientific terminology. 
        Focus on stratospheric patterns, precise anomalies, and micro-climate destabilization.
        Add references or links to advanced research websites or databases where applicable.
        """
    else:
        style_instructions = """
        Respond in such a way that even an 8th grader can understand. 
        Use a storytelling style that creates awareness and urgency without being overly technical. 
        Add some relevant newspaper links or accessible articles if applicable.
        """

    prompt = f"""
    Give a short climate history summary for the location:
    Latitude: {lat}
    Longitude: {lng}
    """
    
    # Inject the specific story context if the user clicked a story card
    if context:
        prompt += f"\nCRITICAL CONTEXT: Specifically analyze and center your report around this ongoing climate phenomenon at this location: {context}\n"

    prompt += f"""
    INSTRUCTIONS:
    {style_instructions}

    Be sure to include:
    - Historical temperature trends
    - Rainfall patterns
    - Immediate and future climate risks
    - Notable climate events
    """

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "nvidia/nemotron-3-super-120b-a12b:free",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
    )

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except KeyError:
        return f"Error from API: {data}"

st.set_page_config(layout="wide", page_title="PyClimaExplorer")

# ── Global iOS / Liquid Glass CSS ──
st.markdown("""
<style>
* { 
    box-sizing: border-box; 
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
html, body, [data-testid="stAppViewContainer"] {
    background: #020617 !important; /* Deepest slate/black */
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Sora', 'Inter', sans-serif;
    scroll-behavior: smooth;
}
[data-testid="stSidebar"][aria-expanded="true"] ~ div [data-testid="stAppViewContainer"] {
    --sidebar-width: 300px;
}

[data-testid="stSidebar"][aria-expanded="false"] ~ div [data-testid="stAppViewContainer"] {
    --sidebar-width: 60px;
}
#MainMenu, header, footer { visibility: hidden; }
.block-container {
    padding-top: 100px !important;
    padding-bottom: 2rem;
    background: transparent !important;
    max-width: 100% !important;
}

/* Hide the invisible text inputs used for JS communication */
div[data-testid="stTextInput"] { display: none !important; }

/* ── MODE SELECTOR UI (Vertically Centered & Glassy) ── */
div[data-testid="column"]:nth-child(2) {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    margin-top: 15px;
}

div.stRadio > div[role="radiogroup"] {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(40px) saturate(200%);
    -webkit-backdrop-filter: blur(40px) saturate(200%);
    padding: 6px 14px;
    border-radius: 50px;
    border: 1px solid rgba(34, 211, 238, 0.25);
    box-shadow: 
        0 10px 30px rgba(0, 0, 0, 0.5), 
        0 0 20px rgba(34, 211, 238, 0.15), 
        inset 0 1px 1px rgba(255, 255, 255, 0.15);
    width: fit-content;
    margin: 0 auto;
}

div.stRadio label { 
    cursor: pointer; 
    color: rgba(255, 255, 255, 0.7) !important; 
    font-weight: 600; 
    padding: 8px 16px;
    border-radius: 40px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
div.stRadio label:hover {
    color: #fff !important;
    background: rgba(34, 211, 238, 0.1);
    box-shadow: 0 0 15px rgba(34, 211, 238, 0.2);
}
</style>
""", unsafe_allow_html=True)

# ── Unified State Management ──
if "target_lat" not in st.session_state:
    st.session_state.target_lat = None
    st.session_state.target_lng = None
if "story_context" not in st.session_state:
    st.session_state.story_context = None
if "last_location_state" not in st.session_state:
    st.session_state.last_location_state = None  
if "climate_report" not in st.session_state:
    st.session_state.climate_report = None
if "prev_map_click" not in st.session_state:
    st.session_state.prev_map_click = None
if "prev_story_trigger" not in st.session_state:
    st.session_state.prev_story_trigger = ""

# The hidden input catching the JS payload
story_trigger = st.text_input("story_click_data", key="story_click_data_input", label_visibility="hidden")

if story_trigger and story_trigger != st.session_state.prev_story_trigger:
    try:
        # We split by "|" now, to allow commas in our context text
        parts = story_trigger.split('|')
        if len(parts) >= 2:
            st.session_state.target_lat = float(parts[0])
            st.session_state.target_lng = float(parts[1])
            # Capture the context string if provided
            st.session_state.story_context = parts[2] if len(parts) >= 3 and parts[2] != "null" else None
            
        st.session_state.prev_story_trigger = story_trigger
        st.rerun() 
    except Exception as e:
        pass


st.title("🪶 Story Mode")
st.markdown("Climate Stories Around the World")
# ── Top Level Mode Selector ──
st.markdown("<div style='color: rgba(255,255,255,0.5); font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; font-size: 0.8rem; margin-top: 5px; display:flex; font-family: -apple-system, sans-serif;'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_mode = st.radio("Mode", ["Normal", "Advanced/Research"], horizontal=True, label_visibility="collapsed")
    current_mode_key = selected_mode.lower()

# ── Map container ──
st.markdown("""
<div style="width:94%;max-width:1400px;margin:25px auto 0;border-radius:32px;overflow:hidden;
  border: 1px solid rgba(34, 211, 238, 0.2);
  box-shadow: 0 30px 80px rgba(0,0,0,0.8), 0 0 40px rgba(34, 211, 238, 0.12), inset 0 1px 1px rgba(255,255,255,0.1);">
""", unsafe_allow_html=True)

m = folium.Map(
    location=[20.5937, 78.9629],
    zoom_start=4.2,
    tiles=None
)

folium.TileLayer("CartoDB dark_matter", name="Dark").add_to(m)
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Satellite"
).add_to(m)

folium.LayerControl().add_to(m)

hotspots = [
    {"loc": [20.5937, 78.9629], "name": "India — Monsoon Shifts", "color": "lightblue"},
    {"loc": [-18.0, 147.0], "name": "Great Barrier Reef — Bleaching", "color": "orange"},
    {"loc": [-3.4, -62.2], "name": "Amazon — Deforestation", "color": "green"},
    {"loc": [78.5, 16.0], "name": "Svalbard — Ice Melt", "color": "white"},
    {"loc": [35.6, 139.7], "name": "Tokyo — Urban Heat", "color": "red"},
    {"loc": [-33.9, 18.4], "name": "Cape Town — Water Crisis", "color": "beige"},
]
for h in hotspots:
    folium.Marker(
        location=h["loc"], popup=h["name"], tooltip=h["name"],
        icon=folium.Icon(color=h["color"], icon="cloud", prefix="fa")
    ).add_to(m)

clicked = st_folium(m, width=None, height=580, returned_objects=["last_clicked"], key="map_v6")
st.markdown("</div>", unsafe_allow_html=True)

# Standard Map Clicks clear the story context
if clicked and clicked.get("last_clicked") and clicked.get("last_clicked") != st.session_state.prev_map_click:
    current_map_click = clicked["last_clicked"]
    st.session_state.target_lat = current_map_click["lat"]
    st.session_state.target_lng = current_map_click["lng"]
    st.session_state.story_context = None # Clear context on pure map click
    st.session_state.prev_map_click = current_map_click

# ── Handle Click & Show Unified AI Glassy Card ──
if st.session_state.target_lat is not None and st.session_state.target_lng is not None:
    lat = st.session_state.target_lat
    lng = st.session_state.target_lng
    ctx = st.session_state.story_context
    
    # State tuple now includes the context so it properly refetches if the phenomenon changes
    current_loc_state = (lat, lng, current_mode_key, ctx)
    
    if st.session_state.last_location_state != current_loc_state:
        msg = "AI is writing an accessible story..." if current_mode_key == "normal" else "AI is fetching PhD-level research data..."
        if ctx:
            msg = f"Investigating {ctx}..."
            
        with st.spinner(msg):
            try:
                st.session_state.climate_report = get_climate_history(lat, lng, mode=current_mode_key, context=ctx)
            except Exception as e:
                st.session_state.climate_report = f"Error generating report: {e}"
        st.session_state.last_location_state = current_loc_state

    raw_text = st.session_state.climate_report or ""
    safe_text = html.escape(raw_text)
    safe_text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #f8fafc;">\1</strong>', safe_text)
    safe_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" style="color: #22d3ee; text-decoration: none; border-bottom: 1px dashed #22d3ee;">\1</a>', safe_text)
    safe_text = safe_text.replace('\n', '<br>')

    is_adv = current_mode_key == "advanced"
    grid_display = 'grid' if is_adv else 'none'

    # Unified Inline Component (AI Response + Liquid Glass)
    components.html(f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; -webkit-font-smoothing: antialiased; }}
  body {{ background: transparent; font-family: 'Sora', -apple-system, sans-serif; padding: 20px 10px; }}
  
  .glass-card {{
    width: 100%; max-width: 1300px; margin: 0 auto;
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(40px) saturate(250%);
    -webkit-backdrop-filter: blur(40px) saturate(250%);
    border: 1px solid rgba(34, 211, 238, 0.3);
    border-radius: 36px;
    padding: 40px 48px;
    box-shadow: 
        0 40px 80px rgba(0,0,0,0.7), 
        0 0 40px rgba(34, 211, 238, 0.15), 
        inset 0 1px 2px rgba(255,255,255,0.2);
    animation: springUp 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.1);
  }}
  
  @keyframes springUp {{
    0% {{ opacity: 0; transform: translateY(50px) scale(0.95); filter: blur(10px); }}
    100% {{ opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }}
  }}

  .header-row {{
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding-bottom: 24px; margin-bottom: 28px; flex-wrap: wrap; gap: 15px;
  }}
  .loc-title {{
    font-size: 2.2rem; font-weight: 800; line-height: 1.1; margin-bottom: 8px;
    background: linear-gradient(135deg, #a5f3fc, #22d3ee, #3b82f6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-shadow: 0 0 20px rgba(34, 211, 238, 0.3);
  }}
  .loc-sub {{ font-size: 1rem; color: rgba(255,255,255,0.5); font-weight: 500; }}

  .mode-indicator {{
    font-size: 0.85rem; font-weight: 700; 
    color: #22d3ee; 
    background: rgba(34, 211, 238, 0.1);
    border: 1px solid rgba(34, 211, 238, 0.3);
    box-shadow: 0 0 15px rgba(34, 211, 238, 0.2);
    padding: 10px 20px; border-radius: 24px; text-transform: uppercase; letter-spacing: 0.05em;
  }}

  .adv-grid {{
    display: {grid_display}; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px;
    margin-bottom: 32px; animation: fadeIn 0.5s ease forwards;
  }}
  .adv-card {{
    background: rgba(34, 211, 238, 0.05); border: 1px solid rgba(34, 211, 238, 0.2);
    padding: 18px; border-radius: 20px; text-align: center;
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
  }}
  .adv-card .lbl {{ font-size: 0.75rem; text-transform: uppercase; color: #22d3ee; font-weight: 700; letter-spacing: 0.1em; margin-bottom: 8px; }}
  .adv-card .val {{ font-size: 1.4rem; font-weight: 800; color: #f8fafc; text-shadow: 0 0 10px rgba(255,255,255,0.2); }}
  
  @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

  .ai-response-container {{
    font-size: 1.1rem; line-height: 1.8; color: rgba(255,255,255,0.8);
    max-height: 500px; overflow-y: auto; padding-right: 16px; margin-bottom:20px;
  }}
  .ai-response-container::-webkit-scrollbar {{ width: 6px; }}
  .ai-response-container::-webkit-scrollbar-thumb {{ background: rgba(34, 211, 238, 0.3); border-radius: 10px; }}
  
  .ai-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 0.75rem; color: #34d399; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
    background: rgba(52,211,153,0.1); padding: 8px 16px; border-radius: 20px; margin-bottom: 20px;
    border: 1px solid rgba(52,211,153,0.3);
    box-shadow: 0 0 15px rgba(52, 211, 153, 0.15);
  }}
</style>
</head>
<body>

<div class="glass-card" id="ai-card">
  <div class="header-row">
    <div>
      <div class="loc-title" id="loc-name">Analyzing Location...</div>
      <div class="loc-sub" id="loc-sub">Capturing regional climate data for {lat:.4f}, {lng:.4f}</div>
    </div>
    <div class="mode-indicator">{current_mode_key} Mode Active</div>
  </div>

  <div class="adv-grid" id="adv-grid">
    <div class="adv-card"><div class="lbl">Latitude</div><div class="val">{lat:.5f}°</div></div>
    <div class="adv-card"><div class="lbl">Longitude</div><div class="val">{lng:.5f}°</div></div>
    <div class="adv-card"><div class="lbl">Hemisphere</div><div class="val" id="hemi-val">--</div></div>
    <div class="adv-card"><div class="lbl">Climate Index</div><div class="val">Active</div></div>
  </div>

  <div class="ai-badge">PyClima AI Generated Report</div>
  <div class="ai-response-container">
    {safe_text}
  </div>
</div>

<script>
  setTimeout(() => {{ document.getElementById('ai-card').scrollIntoView({{ behavior: 'smooth', block: 'center' }}); }}, 200);
  const lat = {lat}; const lng = {lng};
  document.getElementById('hemi-val').innerText = lat >= 0 ? "Northern" : "Southern";

  fetch(`https://nominatim.openstreetmap.org/reverse?lat=${{lat}}&lon=${{lng}}&format=json&accept-language=en`)
    .then(r => r.json())
    .then(d => {{
       const a = d.address || {{}};
       const primary = a.city || a.town || a.village || a.state || a.country || 'Remote Region';
       document.getElementById('loc-name').innerText = primary;
       let subParts = [];
       if(a.state && a.state !== primary) subParts.push(a.state);
       if(a.country && a.country !== primary) subParts.push(a.country);
       document.getElementById('loc-sub').innerText = subParts.length > 0 ? subParts.join(', ') : 'Open Region coordinates';
    }}).catch(e => {{ document.getElementById('loc-name').innerText = 'Location Detected'; }});
</script>
</body>
</html>
""", height=900, scrolling=False)

components.html("""<!DOCTYPE html>
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; -webkit-font-smoothing: antialiased; }
  body { font-family: 'Sora', -apple-system, sans-serif; background: transparent; padding: 52px 3% 72px; }

  .section-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 32px; flex-wrap: wrap; gap: 12px; }
  .hd  { font-size: 2.2rem; font-weight: 800; color: #fff; letter-spacing: -0.04em; line-height: 1.15; }
  .hd span {
    background: linear-gradient(135deg, #22d3ee, #818cf8, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-shadow: 0 0 20px rgba(34, 211, 238, 0.2);
  }
  .sub { font-size: 1rem; color: rgba(255,255,255,0.45); margin-top: 8px; font-weight: 400; line-height:1.5; max-width:550px; }

  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 28px; }

  .card {
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(40px) saturate(200%);
    -webkit-backdrop-filter: blur(40px) saturate(200%);
    border: 1px solid rgba(34, 211, 238, 0.2);
    border-radius: 32px;
    overflow: hidden;
    display: flex; flex-direction: column;
    cursor: pointer; position: relative;
    box-shadow: 0 20px 40px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.15);
    transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
    opacity: 0; transform: translateY(40px); filter: blur(8px);
  }
  .card:hover {
    transform: translateY(-12px) scale(1.02) !important;
    border-color: rgba(34, 211, 238, 0.5);
    box-shadow: 0 30px 60px rgba(0,0,0,0.8), 0 0 30px rgba(34, 211, 238, 0.25), inset 0 1px 2px rgba(255,255,255,0.3);
  }

  .img-wrap {
    position: relative; height: 220px; overflow: hidden;
    background: rgba(16,16,26,0.95);
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }
  .img-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.7s cubic-bezier(0.2, 0.8, 0.2, 1); }
  .card:hover .img-wrap img { transform: scale(1.08); }
  .img-wrap::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 80px; background: linear-gradient(to top, rgba(15, 23, 42, 0.9), transparent); }

  .badge { position: absolute; top: 16px; right: 16px; z-index: 3; background: rgba(0,0,0,0.5); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); color: #fff; padding: 6px 14px; border-radius: 24px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(255,255,255,0.2); }
  .badge.red   { background: rgba(239,68,68,0.2); border-color: rgba(239,68,68,0.4); color: #fca5a5; }
  .badge.amber { background: rgba(245,158,11,0.2); border-color: rgba(245,158,11,0.4); color: #fcd34d; }
  .badge.cyan  { background: rgba(34,211,238,0.2); border-color: rgba(34,211,238,0.4); color: #67e8f9; }

  .severity { position: absolute; bottom: 16px; left: 16px; z-index: 3; display: flex; gap: 4px; }
  .dot { width: 8px; height: 8px; border-radius: 50%; }
  .dot.on  { background: #22d3ee; box-shadow: 0 0 10px #22d3ee; }
  .dot.mid { background: #38bdf8; box-shadow: 0 0 8px #38bdf8; }
  .dot.off { background: rgba(255,255,255,0.2); }

  .body { padding: 28px; display: flex; flex-direction: column; flex-grow: 1; }
  .loc-row { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
  .loc  { color: #22d3ee; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }
  .ttl  { font-size: 1.3rem; font-weight: 800; color: #f8fafc; margin-bottom: 12px; line-height: 1.3; }
  .dsc  { font-size: 0.9rem; color: rgba(255,255,255,0.6); line-height: 1.6; margin-bottom: 24px; flex-grow: 1; }

  .data-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: auto; }
  .data-chip { display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(34, 211, 238, 0.05); border: 1px solid rgba(34, 211, 238, 0.15); border-radius: 14px; padding: 10px 14px; flex: 1; min-width: 60px; box-shadow: inset 0 1px 1px rgba(255,255,255,0.05); }
  .dc-val { font-size: 0.95rem; font-weight: 800; color: #f8fafc; text-align: center; }
  .dc-lbl { font-size: 0.55rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700; margin-top: 4px; text-align: center; }
</style>
</head>
<body>

<div class="section-header">
  <div>
    <div class="hd">Story Mode <span>Understand the crisis</span></div>
    <div class="sub">Real-time impacts of 6 critical climate phenomena reshaping our planet right now. Select a card to investigate.</div>
  </div>
</div>

<div class="grid">

  <!-- 1. Coral Bleaching -->
  <div class="card" onclick="sendToApp(-18.0, 147.0, 'Mass Coral Bleaching induced by El Niño and Ocean Heatwaves')">
    <div class="img-wrap">
      <div class="badge red">⚠ Mass Bleaching</div>
      <div class="severity"><div class="dot on"></div><div class="dot on"></div><div class="dot on"></div><div class="dot off"></div></div>
      <img src="https://images.unsplash.com/photo-1559827260-dc66d52bef19?auto=format&fit=crop&q=80&w=800" alt="Coral Bleaching">
    </div>
    <div class="body">
      <div class="loc-row"><span>📍</span><div class="loc">Great Barrier Reef, Australia</div></div>
      <div class="ttl">El Niño's Coral Catastrophe</div>
      <div class="dsc">Unprecedented ocean heatwaves have triggered the fourth global coral bleaching crisis since 1998. Over 54% of reef systems worldwide are now affected, with recovery timelines stretching decades.</div>
      <div class="data-row">
        <div class="data-chip"><div class="dc-val">+2.3°C</div><div class="dc-lbl">Sea Temp</div></div>
        <div class="data-chip"><div class="dc-val">54%</div><div class="dc-lbl">Global Hit</div></div>
        <div class="data-chip"><div class="dc-val">91%</div><div class="dc-lbl">GBR Bleached</div></div>
        <div class="data-chip"><div class="dc-val">15 yrs</div><div class="dc-lbl">Recovery</div></div>
      </div>
    </div>
  </div>

  <!-- 2. Amazon Tipping Point -->
  <div class="card" onclick="sendToApp(-3.4, -62.2, 'Record breaking dry seasons, savannification, and relentless deforestation')">
    <div class="img-wrap">
      <div class="badge red">🔴 Critical Zone</div>
      <div class="severity"><div class="dot on"></div><div class="dot on"></div><div class="dot on"></div><div class="dot on"></div></div>
      <img src="https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&q=80&w=800" alt="Amazon Deforestation">
    </div>
    <div class="body">
      <div class="loc-row"><span>📍</span><div class="loc">Amazonas, Brazil</div></div>
      <div class="ttl">Rainforest Tipping Point</div>
      <div class="dsc">Record-breaking dry seasons and relentless deforestation are pushing the Amazon past an irreversible tipping point, triggering a "savannification" cascade that threatens global carbon cycles.</div>
      <div class="data-row">
        <div class="data-chip"><div class="dc-val">17%</div><div class="dc-lbl">Total Loss</div></div>
        <div class="data-chip"><div class="dc-val">11k km²</div><div class="dc-lbl">2023 Loss</div></div>
        <div class="data-chip"><div class="dc-val">−30%</div><div class="dc-lbl">Rainfall</div></div>
        <div class="data-chip"><div class="dc-val">1.5Bt</div><div class="dc-lbl">CO₂ Emit</div></div>
      </div>
    </div>
  </div>

  <!-- 3. Arctic Ice Melt -->
  <div class="card" onclick="sendToApp(78.5, 16.0, 'Polar Vortex Collapse, Sudden Stratospheric Warming, and Rapid Ice sheet melt')">
    <div class="img-wrap">
      <div class="badge cyan">❄ Accelerating Melt</div>
      <div class="severity"><div class="dot on"></div><div class="dot on"></div><div class="dot mid"></div><div class="dot off"></div></div>
      <img src="https://images.unsplash.com/photo-1520923642038-b4259acecbd7?auto=format&fit=crop&q=80&w=800" alt="Arctic Ice Melt">
    </div>
    <div class="body">
      <div class="loc-row"><span>📍</span><div class="loc">Svalbard, Arctic</div></div>
      <div class="ttl">Polar Vortex Collapse</div>
      <div class="dsc">Arctic ice sheets are melting 4× faster than projected models from 2007. Disruption of the polar vortex is triggering sudden stratospheric warming events and destabilising weather across the Northern Hemisphere.</div>
      <div class="data-row">
        <div class="data-chip"><div class="dc-val">4×</div><div class="dc-lbl">Melt Rate</div></div>
        <div class="data-chip"><div class="dc-val">+4.7°C</div><div class="dc-lbl">Anomaly</div></div>
        <div class="data-chip"><div class="dc-val">7 m</div><div class="dc-lbl">Sea Rise Risk</div></div>
        <div class="data-chip"><div class="dc-val">267 Gt</div><div class="dc-lbl">Ice Loss/yr</div></div>
      </div>
    </div>
  </div>

  <!-- 4. India Monsoon Shifts -->
  <div class="card" onclick="sendToApp(20.5937, 78.9629, 'Erratic monsoon patterns, extreme floods, and prolonged agricultural droughts')">
    <div class="img-wrap">
      <div class="badge amber">⚠ Erratic Patterns</div>
      <div class="severity"><div class="dot on"></div><div class="dot on"></div><div class="dot on"></div><div class="dot off"></div></div>
      <img src="https://images.unsplash.com/photo-1527482797697-8795b05a13fe?auto=format&fit=crop&q=80&w=800" alt="India Monsoon Floods">
    </div>
    <div class="body">
      <div class="loc-row"><span>📍</span><div class="loc">India, South Asia</div></div>
      <div class="ttl">Extreme Monsoon Shifts</div>
      <div class="dsc">Erratic rainfall and sudden atmospheric rivers are replacing the steady monsoon, leading to simultaneous devastating flash floods and prolonged agricultural droughts affecting over a billion people.</div>
      <div class="data-row">
        <div class="data-chip"><div class="dc-val">+40%</div><div class="dc-lbl">Flash Floods</div></div>
        <div class="data-chip"><div class="dc-val">49.2°C</div><div class="dc-lbl">Peak Temp</div></div>
        <div class="data-chip"><div class="dc-val">35%</div><div class="dc-lbl">Crop Risk</div></div>
        <div class="data-chip"><div class="dc-val">−15%</div><div class="dc-lbl">Rain Deficit</div></div>
      </div>
    </div>
  </div>

  <!-- 5. Tokyo Urban Heat -->
  <div class="card" onclick="sendToApp(35.6, 139.7, 'Intensifying urban heat island effect, deadly summer heatwaves, and typhoon vulnerability')">
    
  </div>

  

</div>

<script>
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        entry.target.style.filter = 'blur(0)';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.card').forEach((card, index) => {
    card.style.transitionDelay = `${(index % 3) * 0.15}s`;
    observer.observe(card);
  });

  function sendToApp(lat, lng, contextText = 'null') {
    try {
      const payload = lat + "|" + lng + "|" + contextText + "|" + Date.now();
      const parentDoc = window.parent.document;
      const inputField = parentDoc.querySelector('input[aria-label="story_click_data"]');
      if (inputField) {
        let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(inputField, payload);
        inputField.dispatchEvent(new Event('input', { bubbles: true }));
        inputField.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true}));
        window.parent.scrollTo({top: 450, behavior: 'smooth'});
      }
    } catch(err) { console.error(err); }
  }
</script>
</body>
</html>
""", height=1400, scrolling=False)