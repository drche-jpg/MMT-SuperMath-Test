"""
MathComp — app.py
Math Mission Thailand · Online Mathematics Competition Platform
© Math Mission Thailand 2026

Theme: Navy / Blue / Pink / White
FIX: CSS now injected once via st.components.v1.html (never renders as text)
FIX: Button selectors updated for Streamlit >= 1.35
FIX: Vivid, clearly visible button colors
"""

import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, firestore
import plotly.graph_objects as go
import requests, random, time, json, base64, io, csv
from datetime import datetime, timezone

# ══════════════════════════════════════════════
# Page config  (must be first Streamlit call)
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="MathComp · Math Mission Thailand",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════
# CSS  — injected ONCE via components.html
# Never use st.markdown for the full CSS block;
# components.html bypasses Streamlit's markdown
# renderer so the tags are never shown as text.
# ══════════════════════════════════════════════
_CSS_INJECTED = False

def inject_css():
    global _CSS_INJECTED
    if _CSS_INJECTED:
        return
    _CSS_INJECTED = True
    components.html("""
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
/* inject into parent frame */
</style>
<script>
(function(){
  var css = `
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300&family=DM+Sans:wght@300;400;500;600&display=swap');

    :root {
      --navy:     #1B2B6B;
      --navy2:    #243580;
      --blue:     #4A7CF7;
      --blue-lt:  #EEF3FF;
      --blue-mid: #C8D8FF;
      --pink:     #F472B6;
      --pink-lt:  #FDF2F8;
      --pink-mid: #FBCFE8;
      --white:    #FFFFFF;
      --offwhite: #F8F9FF;
      --border:   #DDE4F5;
      --border2:  #E8ECF8;
      --text:     #1B2B6B;
      --text2:    #5060A0;
      --text3:    #8898CC;
    }

    /* hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stAppViewContainer"] { background: var(--offwhite) !important; }
    [data-testid="stSidebar"] { background: var(--navy) !important; }
    [data-testid="stSidebar"] * { color: rgba(255,255,255,0.75) !important; }
    [data-testid="stSidebarNav"] { display: none !important; }

    /* typography */
    body, .stApp { font-family: 'DM Sans', sans-serif !important; color: var(--text) !important; }
    h1, h2, h3   { font-family: 'Fraunces', serif !important; font-weight: 300 !important; color: var(--navy) !important; }

    /* ── PRIMARY BUTTON (navy bg, white text) ── */
    .stButton button[data-testid="baseButton-primary"],
    .stButton button[kind="primary"],
    button[data-testid="baseButton-primary"] {
      background-color: #1B2B6B !important;
      color: #ffffff !important;
      border: none !important;
      border-radius: 9px !important;
      font-family: 'DM Sans', sans-serif !important;
      font-weight: 600 !important;
      font-size: 14px !important;
      padding: 10px 24px !important;
      letter-spacing: .02em !important;
      transition: background-color .2s, transform .15s, box-shadow .15s !important;
    }
    .stButton button[data-testid="baseButton-primary"]:hover,
    .stButton button[kind="primary"]:hover {
      background-color: #243580 !important;
      transform: translateY(-1px) !important;
      box-shadow: 0 8px 24px rgba(27,43,107,.28) !important;
    }

    /* ── SECONDARY BUTTON (white bg, navy border) ── */
    .stButton button[data-testid="baseButton-secondary"],
    .stButton button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {
      background-color: #ffffff !important;
      color: #1B2B6B !important;
      border: 2px solid #4A7CF7 !important;
      border-radius: 8px !important;
      font-family: 'DM Sans', sans-serif !important;
      font-weight: 500 !important;
      font-size: 14px !important;
      padding: 9px 20px !important;
      transition: all .15s !important;
    }
    .stButton button[data-testid="baseButton-secondary"]:hover,
    .stButton button[kind="secondary"]:hover {
      background-color: #EEF3FF !important;
      border-color: #1B2B6B !important;
      color: #1B2B6B !important;
    }

    /* ── INPUTS ── */
    .stTextInput input, .stTextInput > div > div > input,
    .stTextArea textarea {
      background: var(--offwhite) !important;
      border: 1.5px solid var(--border) !important;
      border-radius: 8px !important;
      color: var(--navy) !important;
      font-family: 'DM Sans', sans-serif !important;
      font-size: 14px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
      border-color: var(--blue) !important;
      box-shadow: 0 0 0 3px rgba(74,124,247,.12) !important;
    }

    /* ── SELECTBOX ── */
    div[data-baseweb="select"] > div {
      background: var(--white) !important;
      border: 1.5px solid var(--border) !important;
      border-radius: 8px !important;
      font-family: 'DM Sans', sans-serif !important;
      color: var(--navy) !important;
    }
    div[data-baseweb="select"] > div:focus-within {
      border-color: var(--blue) !important;
      box-shadow: 0 0 0 3px rgba(74,124,247,.1) !important;
    }

    /* ── RADIO (answer choices) ── */
    div[data-testid="stRadio"] label {
      background: var(--white) !important;
      border: 1.5px solid var(--border) !important;
      border-radius: 10px !important;
      padding: 12px 16px !important;
      margin-bottom: 6px !important;
      cursor: pointer !important;
      transition: all .15s !important;
      font-family: 'DM Sans', sans-serif !important;
      color: var(--navy) !important;
    }
    div[data-testid="stRadio"] label:hover {
      border-color: var(--blue) !important;
      background: var(--blue-lt) !important;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
      border-color: var(--navy) !important;
      background: var(--blue-lt) !important;
      font-weight: 500 !important;
    }

    /* ── PROGRESS BAR ── */
    div[data-testid="stProgress"] > div {
      background: var(--border2) !important;
      border-radius: 4px !important;
      height: 6px !important;
    }
    div[data-testid="stProgress"] > div > div {
      background: linear-gradient(90deg, #4A7CF7, #F472B6) !important;
      border-radius: 4px !important;
    }

    /* ── METRICS ── */
    div[data-testid="stMetric"] {
      background: var(--offwhite) !important;
      border: 1.5px solid var(--border2) !important;
      border-radius: 12px !important;
      padding: 16px 18px !important;
    }
    div[data-testid="stMetricLabel"] p {
      font-size: 11px !important;
      font-family: 'DM Mono', monospace !important;
      letter-spacing: .08em !important;
      color: var(--text3) !important;
      text-transform: uppercase !important;
    }
    div[data-testid="stMetricValue"] {
      font-family: 'Fraunces', serif !important;
      font-size: 28px !important;
      font-weight: 600 !important;
      color: var(--navy) !important;
    }

    /* ── EXPANDER ── */
    details[data-testid="stExpander"] {
      background: var(--white) !important;
      border: 1.5px solid var(--border2) !important;
      border-radius: 10px !important;
      margin-bottom: 6px !important;
    }
    details[data-testid="stExpander"] summary {
      font-family: 'DM Sans', sans-serif !important;
      color: var(--navy) !important;
      padding: 12px 16px !important;
    }

    /* ── TABS ── */
    div[data-testid="stTabs"] button {
      font-family: 'DM Mono', monospace !important;
      font-size: 12px !important;
      letter-spacing: .05em !important;
      color: var(--text3) !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
      color: var(--navy) !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
      background-color: var(--blue) !important;
    }

    /* ── TOGGLE ── */
    div[data-testid="stToggle"] div[data-checked="true"] {
      background-color: var(--navy) !important;
    }

    /* ── ALERTS ── */
    div[data-testid="stAlert"] {
      border-radius: 10px !important;
      font-family: 'DM Sans', sans-serif !important;
    }

    /* ── DIVIDER ── */
    hr { border-color: var(--border2) !important; margin: 18px 0 !important; }

    /* ── MOBILE RESPONSIVE ── */
    @media (max-width: 768px) {
      .mc-hero { padding: 20px 16px 24px !important; }
      .mc-topbar { padding: 0 16px !important; height: 50px !important; }
      .mc-body { padding: 20px 16px !important; }
      .mc-card { padding: 16px !important; }
      .mc-metrics { grid-template-columns: repeat(2,1fr) !important; }
      .mc-metric { padding: 12px 14px !important; }
      .mc-metric-val { font-size: 18px !important; }
      .mc-result-score { font-size: 44px !important; }
      .mc-result-meta { gap: 16px !important; flex-wrap: wrap; }
      .mc-result-hero { padding: 24px 16px !important; }
      .mc-nav-strip { padding: 8px 16px !important; }
      .mc-footer { padding: 12px 16px !important; flex-direction: column; gap: 4px; }
      .block-container { padding: 0 !important; }
      /* Stack columns on mobile */
      [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
      [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
        min-width: 100% !important; flex: 1 1 100% !important;
      }
    }
    @media (max-width: 480px) {
      .mc-metrics { grid-template-columns: repeat(2,1fr) !important; }
      .mc-hero-title { font-size: 22px !important; }
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] .stButton button {
      background: rgba(255,255,255,.08) !important;
      border: 1px solid rgba(255,255,255,.15) !important;
      color: rgba(255,255,255,.8) !important;
      border-radius: 8px !important;
      width: 100% !important;
      font-family: 'DM Sans', sans-serif !important;
      font-size: 13px !important;
      margin-bottom: 4px !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
      background: rgba(255,255,255,.15) !important;
      color: #ffffff !important;
    }

    /* ── CUSTOM COMPONENTS ── */
    .mc-topbar {
      background: var(--navy);
      padding: 0 28px; height: 56px;
      display: flex; align-items: center; gap: 14px;
    }
    .mc-topbar-logo {
      font-family: 'DM Mono', monospace;
      font-size: 13px; letter-spacing: .14em;
      color: #fff; font-weight: 500;
    }
    .mc-topbar-sep { width:1px; height:18px; background:rgba(255,255,255,.2); display:inline-block; }
    .mc-topbar-page { font-size:13px; color:rgba(255,255,255,.5); }
    .mc-topbar-right { margin-left:auto; display:flex; align-items:center; gap:10px; }
    .mc-topbar-user { font-size:12px; font-family:'DM Mono',monospace; color:rgba(255,255,255,.5); }
    .mc-avatar {
      width:30px; height:30px; border-radius:50%;
      background: linear-gradient(135deg, #4A7CF7, #F472B6);
      display:inline-flex; align-items:center; justify-content:center;
      font-size:12px; font-weight:600; color:#fff;
    }
    .mc-hero {
      background: var(--navy); padding: 28px 28px 32px;
      position:relative; overflow:hidden;
    }
    .mc-hero::before {
      content:''; position:absolute; top:-60px; right:-60px;
      width:280px; height:280px;
      background:radial-gradient(circle, rgba(74,124,247,.25) 0%, transparent 70%);
    }
    .mc-hero::after {
      content:''; position:absolute; bottom:-40px; left:40%;
      width:200px; height:200px;
      background:radial-gradient(circle, rgba(244,114,182,.15) 0%, transparent 70%);
    }
    .mc-hero-eyebrow {
      font-family:'DM Mono',monospace; font-size:10px; letter-spacing:.14em;
      color:rgba(255,255,255,.45); text-transform:uppercase; margin-bottom:8px;
    }
    .mc-hero-title {
      font-family:'Fraunces',serif !important; font-size:30px;
      font-weight:300 !important; color:#fff !important; line-height:1.2;
    }
    .mc-hero-title em { font-style:italic; color:#FBCFE8; }
    .mc-metrics {
      display:grid; grid-template-columns:repeat(4,1fr);
      margin-top:22px; border-radius:12px; overflow:hidden;
      border:1px solid rgba(255,255,255,.12);
    }
    .mc-metric {
      padding:15px 18px; border-right:1px solid rgba(255,255,255,.1);
      background:rgba(255,255,255,.06);
    }
    .mc-metric:last-child { border-right:none; }
    .mc-metric-label {
      font-size:10px; font-family:'DM Mono',monospace;
      letter-spacing:.1em; color:rgba(255,255,255,.4);
      text-transform:uppercase; margin-bottom:5px;
    }
    .mc-metric-val {
      font-size:24px; font-family:'Fraunces',serif;
      font-weight:600; color:#fff; line-height:1;
    }
    .mc-metric-sub { font-size:11px; color:rgba(255,255,255,.3); margin-top:3px; }
    /* ── Bigger base font ── */
    .stMarkdown p, .stMarkdown li, .stCaption p,
    div[data-testid="stMarkdownContainer"] p { font-size:15px !important; line-height:1.7 !important; }
    .stSelectbox label, .stSlider label, .stTextInput label,
    .stTextArea label, .stNumberInput label { font-size:14px !important; font-weight:500 !important; color:#1B2B6B !important; }
    div[data-testid="stRadio"] label { font-size:15px !important; }
    div[data-testid="stMetricLabel"] p { font-size:12px !important; }
    /* wider hero padding */
    .mc-hero { padding: 32px 56px 40px; }
    .mc-topbar { padding: 0 56px; }
    .mc-body { background:#fff; padding:40px 56px; }
    .mc-section-lbl {
      font-size:12px; font-family:'DM Mono',monospace;
      letter-spacing:.12em; color:#8898CC;
      text-transform:uppercase; margin-bottom:16px; display:block;
    }
    .mc-card {
      background:#F8F9FF; border:1.5px solid #E8ECF8;
      border-radius:16px; padding:32px; margin-bottom:20px;
    }
    .mc-penalty {
      background:#FFF8E7; border:1px solid #F9E3A0;
      border-radius:8px; padding:10px 14px;
      font-size:12px; color:#8B6408; margin:12px 0;
    }
    .mc-nav-strip {
      background:#EEF3FF; border-bottom:1.5px solid #C8D8FF;
      padding:10px 28px; display:flex; flex-wrap:wrap;
      gap:5px; align-items:center; margin:0 -28px 20px;
    }
    .mc-nav-dot {
      width:26px; height:26px; border-radius:6px;
      border:1.5px solid #C8D8FF; display:inline-flex;
      align-items:center; justify-content:center;
      font-size:10px; font-family:'DM Mono',monospace;
      color:#8898CC; cursor:pointer; background:#fff;
      text-decoration:none; line-height:1;
    }
    .mc-result-hero {
      background:var(--navy); padding:36px 28px;
      text-align:center; position:relative; overflow:hidden;
    }
    .mc-result-hero::before {
      content:''; position:absolute; top:-80px; left:-80px;
      width:320px; height:320px;
      background:radial-gradient(circle,rgba(74,124,247,.2) 0%,transparent 70%);
    }
    .mc-result-hero::after {
      content:''; position:absolute; bottom:-60px; right:-60px;
      width:260px; height:260px;
      background:radial-gradient(circle,rgba(244,114,182,.2) 0%,transparent 70%);
    }
    .mc-result-score {
      font-family:'Fraunces',serif !important; font-size:64px;
      font-weight:600 !important; color:#fff !important; line-height:1;
      position:relative;
    }
    .mc-result-score span { font-size:28px; font-weight:300; color:rgba(255,255,255,.45); }
    .mc-result-meta {
      display:flex; justify-content:center; gap:32px;
      margin-top:16px; position:relative;
    }
    .mc-rm { text-align:center; }
    .mc-rm-val { font-size:22px; font-family:'Fraunces',serif; font-weight:500; color:#fff; }
    .mc-rm-lbl {
      font-size:10px; font-family:'DM Mono',monospace;
      color:rgba(255,255,255,.4); letter-spacing:.1em;
      text-transform:uppercase; margin-top:2px;
    }
    .mc-insight-good {
      background:#F0FFF9; border:1px solid #A7F3D0;
      border-radius:10px; padding:14px 16px; margin-bottom:10px;
    }
    .mc-insight-bad {
      background:#FDF2F8; border:1px solid #FBCFE8;
      border-radius:10px; padding:14px 16px; margin-bottom:10px;
    }
    .mc-insight-lbl {
      font-size:10px; font-family:'DM Mono',monospace;
      letter-spacing:.1em; text-transform:uppercase; margin-bottom:5px;
    }
    .mc-insight-good .mc-insight-lbl { color:#059669; }
    .mc-insight-bad  .mc-insight-lbl { color:#9D174D; }
    .mc-insight-text { font-size:13px; color:#1B2B6B; line-height:1.55; }
    .mc-topic-row { display:flex; align-items:center; gap:10px; margin-bottom:11px; }
    .mc-topic-name { font-size:13px; color:#1B2B6B; width:112px; flex-shrink:0; }
    .mc-bar-bg { flex:1; height:5px; background:#E8ECF8; border-radius:3px; }
    .mc-bar-fill { height:5px; border-radius:3px; }
    .mc-bar-pct { font-family:'DM Mono',monospace; font-size:11px; color:#8898CC; width:32px; text-align:right; }
    .mc-footer {
      background:var(--navy); padding:14px 28px;
      display:flex; align-items:center; justify-content:space-between;
    }
    .mc-footer-copy {
      font-family:'DM Mono',monospace; font-size:11px;
      color:rgba(255,255,255,.35); letter-spacing:.06em;
    }
    .mc-footer-copy strong { color:rgba(255,255,255,.6); font-weight:500; }
  `;
  var style = document.createElement('style');
  style.textContent = css;
  // inject into the top-level document (parent of the iframe)
  try {
    window.parent.document.head.appendChild(style);
  } catch(e) {
    document.head.appendChild(style);
  }
})();
</script>
""", height=0, scrolling=False)


# ══════════════════════════════════════════════
# Helper UI components
# ══════════════════════════════════════════════
def topbar(page_title: str, show_user: bool = True):
    name    = st.session_state.get("display_name", "")
    initial = name[0].upper() if name else "U"
    user_html = (f'<span class="mc-topbar-user">{name}</span>'
                 f'<div class="mc-avatar">{initial}</div>') if show_user and name else ""
    st.markdown(f"""
    <div class="mc-topbar">
      <span class="mc-topbar-logo">MATHCOMP</span>
      <span class="mc-topbar-sep"></span>
      <span class="mc-topbar-page">{page_title}</span>
      <div class="mc-topbar-right">{user_html}</div>
    </div>""", unsafe_allow_html=True)


def footer():
    st.markdown("""
    <div class="mc-footer">
      <span class="mc-footer-copy">© <strong>Math Mission Thailand</strong> 2026 · MathComp Platform</span>
      <span class="mc-footer-copy">Online Mathematics Competition</span>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# Firebase init
# ══════════════════════════════════════════════
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        sa   = st.secrets.get("FIREBASE_SERVICE_ACCOUNT", "{}")
        cred = credentials.Certificate(json.loads(sa))
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# ══════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════
TOPICS = ["Algebra", "Number Theory", "Geometry", "Combinatorics", "Word Problem"]

# Built-in competitions (hardcoded)
COMPETITIONS_BUILTIN = {
    "AMC 8":  {"levels":["AMC 8"],              "secs_per_q":90,  "scoring":{"correct":1,"wrong":0,"blank":0},     "description":"Grade 6–8 · 25 questions · 40 min"},
    "AMC 10": {"levels":["AMC 10A","AMC 10B"],   "secs_per_q":150, "scoring":{"correct":6,"wrong":-1.5,"blank":0},  "description":"Grade 9–10 · 30 questions · 75 min"},
    "AMC 12": {"levels":["AMC 12A","AMC 12B"],   "secs_per_q":150, "scoring":{"correct":6,"wrong":-1.5,"blank":0},  "description":"Grade 11–12 · 30 questions · 75 min"},
    "AMC (Australian)": {"levels":["Middle Primary","Upper Primary","Junior","Intermediate","Senior"], "secs_per_q":120,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"Multiple divisions · 30 questions"},
    "Sansu Olympic":    {"levels":["Kidbee","Junior","Senior","Hironaka"],     "secs_per_q":180,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"算数オリンピック"},
    "Math Association Thailand": {"levels":["Primary Upper","Junior Secondary","Senior Secondary"],"secs_per_q":120,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"สมาคมคณิตศาสตร์แห่งประเทศไทย"},
    "POSN Mathematics": {"levels":["Round 1"],"secs_per_q":180,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"สอวน. คณิตศาสตร์ รอบแรก"},
    # Singapore
    "SMO (Junior)":        {"levels":["Open","Short List"],         "secs_per_q":180,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"Singapore Mathematical Olympiad · Junior"},
    "SMO (Senior)":        {"levels":["Open","Short List"],         "secs_per_q":180,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"Singapore Mathematical Olympiad · Senior"},
    "SMO (Open)":          {"levels":["Open","Short List"],         "secs_per_q":180,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"Singapore Mathematical Olympiad · Open"},
    # International
    "IMO":                 {"levels":["Day 1","Day 2"],             "secs_per_q":600,"scoring":{"correct":7,"wrong":0,"blank":0},"description":"International Mathematical Olympiad"},
    "APMO":                {"levels":["General"],                   "secs_per_q":480,"scoring":{"correct":7,"wrong":0,"blank":0},"description":"Asian Pacific Mathematics Olympiad"},
    "SASMO":               {"levels":["Grade 2","Grade 3","Grade 4","Grade 5","Grade 6","Grade 7","Grade 8","Grade 9","Grade 10"], "secs_per_q":90,"scoring":{"correct":4,"wrong":-1,"blank":0},"description":"Singapore & Asian Schools Math Olympiad"},
    "SEAMO":               {"levels":["Paper A","Paper B","Paper C","Paper D","Paper E","Paper F"], "secs_per_q":90,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"South East Asian Mathematical Olympiad"},
    "Thailand ONET":       {"levels":["Grade 6","Grade 9","Grade 12"],"secs_per_q":90,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"O-NET คณิตศาสตร์"},
    "Thailand PAT":        {"levels":["PAT 1"],                     "secs_per_q":120,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"PAT 1 คณิตศาสตร์"},
}

@st.cache_data(ttl=60)
def load_custom_competitions() -> dict:
    """Load admin-created competitions from Firestore."""
    try:
        docs = db.collection("competition_catalog").stream()
        result = {}
        for doc in docs:
            d = doc.to_dict()
            name = d.get("name","")
            if name:
                result[name] = {
                    "levels":      d.get("levels",["General"]),
                    "secs_per_q":  d.get("secs_per_q",120),
                    "scoring":     d.get("scoring",{"correct":1,"wrong":0,"blank":0}),
                    "description": d.get("description","Custom competition"),
                    "custom":      True,
                    "doc_id":      doc.id,
                }
        return result
    except:
        return {}

@st.cache_data(ttl=30)
def load_disabled_competitions() -> set:
    """Return set of competition names that admin has disabled."""
    try:
        doc = db.collection("platform_settings").document("disabled_competitions").get()
        if doc.exists:
            return set(doc.to_dict().get("disabled", []))
    except:
        pass
    return set()

def set_competition_enabled(name: str, enabled: bool):
    """Enable or disable a competition."""
    disabled = load_disabled_competitions()
    if enabled:
        disabled.discard(name)
    else:
        disabled.add(name)
    db.collection("platform_settings").document("disabled_competitions").set(
        {"disabled": list(disabled)}
    )
    load_disabled_competitions.clear()

def get_all_competitions(include_disabled: bool = False) -> dict:
    """
    Merge built-in + custom competitions.
    include_disabled=True  → admin views (show all)
    include_disabled=False → student views (hide disabled)
    """
    merged = dict(COMPETITIONS_BUILTIN)
    merged.update(load_custom_competitions())
    if not include_disabled:
        disabled = load_disabled_competitions()
        merged = {k: v for k, v in merged.items() if k not in disabled}
    return merged

# Active competitions dict (used throughout the app)
COMPETITIONS = COMPETITIONS_BUILTIN  # fallback; replaced at runtime by get_all_competitions()
DIFFICULTY_OPTIONS = ["Easy","Intermediate","Advanced","Mixed"]

DEFAULT_SETTINGS = {
    "load_from_firebase":True,"load_student_list":True,"require_competitor_id":True,
    "show_answer_after_submit":False,"allow_bilingual":False,
    "anti_copy_text":False,"noise_canvas":False,"block_ctrl_c":False,
    "block_text_selection":False,"block_paste_answer":True,"block_drag":True,
    "block_right_click":True,"tab_switch_warning":True,"block_printscreen":True,
    "clipboard_api_override":False,"devtools_detection":False,"screen_capture_block":False,
    "time_per_question":0,  # 0 = disabled; >0 = seconds per question
}

# ══════════════════════════════════════════════
# Settings helpers
# ══════════════════════════════════════════════
def load_settings(competition: str) -> dict:
    try:
        doc = db.collection("settings").document(competition).get()
        if doc.exists:
            m = DEFAULT_SETTINGS.copy(); m.update(doc.to_dict()); return m
    except: pass
    return DEFAULT_SETTINGS.copy()

def save_settings(competition: str, settings: dict):
    db.collection("settings").document(competition).set(settings)

def get_anti_ai_js(s: dict) -> str:
    sc = []
    if s.get("block_right_click"):     sc.append("document.addEventListener('contextmenu',function(e){e.preventDefault();alert('Right-click is disabled during the exam.');},true);")
    if s.get("block_ctrl_c"):          sc.append("document.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&['c','v','x','a'].includes(e.key.toLowerCase())){e.preventDefault();e.stopPropagation();}},true);")
    if s.get("block_text_selection"):  sc.append("document.addEventListener('selectionchange',function(){if(window.getSelection().toString().length>10)window.getSelection().removeAllRanges();});")
    if s.get("block_drag"):            sc.append("document.addEventListener('dragstart',function(e){e.preventDefault();},true);")
    if s.get("block_paste_answer"):    sc.append("document.addEventListener('paste',function(e){var t=e.target;if(t.tagName==='INPUT'||t.tagName==='TEXTAREA')e.preventDefault();},true);")
    if s.get("tab_switch_warning"):    sc.append("document.addEventListener('visibilitychange',function(){if(document.hidden)alert('Warning: Stay on the exam tab!');});window.addEventListener('blur',function(){alert('Warning: Do not switch windows!');});")
    if s.get("block_printscreen"):     sc.append("document.addEventListener('keyup',function(e){if(e.key==='PrintScreen'){navigator.clipboard.writeText('');alert('Screenshots are not allowed.');}});")
    if s.get("clipboard_api_override"):sc.append("Object.defineProperty(navigator,'clipboard',{get:function(){return{readText:function(){return Promise.resolve('');},writeText:function(){return Promise.resolve();}};} });")
    if s.get("devtools_detection"):    sc.append("setInterval(function(){if(window.outerWidth-window.innerWidth>160||window.outerHeight-window.innerHeight>160)alert('Warning: Close developer tools.');},3000);")
    if s.get("screen_capture_block"):  sc.append("if(navigator.mediaDevices&&navigator.mediaDevices.getDisplayMedia)navigator.mediaDevices.getDisplayMedia=function(){return Promise.reject(new Error('Screen capture disabled.'));};")
    if not sc: return ""
    return "<script>try{" + "\n".join(sc) + "}catch(e){}</script>"

# ══════════════════════════════════════════════
# Auth helpers
# ══════════════════════════════════════════════
def sign_in(email: str, password: str) -> dict | None:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={st.secrets.get('FIREBASE_API_KEY','')}"
    try:
        r = requests.post(url, json={"email":email,"password":password,"returnSecureToken":True}, timeout=10)
        return r.json() if r.ok else None
    except: return None

def get_profile(uid: str) -> dict:
    try:
        doc = db.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else {}
    except: return {}

def require_auth():
    if "uid" not in st.session_state:
        st.session_state["page"] = "login"; st.rerun()

def require_admin():
    if st.session_state.get("role") != "admin":
        st.session_state["page"] = "dashboard"; st.rerun()

# ══════════════════════════════════════════════
# Firestore — questions
# ══════════════════════════════════════════════
def fetch_questions(competition, level, difficulty, n) -> list:
    try:
        base = db.collection("questions").where("competition","==",competition).where("level","==",level)
        if difficulty != "Mixed": base = base.where("difficulty","==",difficulty.lower())
        pool = [_dq(d) for d in base.stream()]
        if len(pool) < n:
            pool = [_dq(d) for d in db.collection("questions").where("competition","==",competition).where("level","==",level).stream()]
        return random.sample(pool, min(n, len(pool)))
    except Exception as e:
        st.error(f"Error loading questions: {e}"); return []

def _dq(doc) -> dict:
    d = doc.to_dict(); d["id"] = doc.id; return d

# ══════════════════════════════════════════════
# Email — welcome message
# ══════════════════════════════════════════════
def send_welcome_email(to_email: str, display_name: str, password: str, role: str, app_url: str = "") -> tuple[bool, str]:
    """
    Send a welcome email with login credentials via Gmail SMTP.
    Requires secrets: GMAIL_SENDER, GMAIL_APP_PASSWORD
    Returns (success, message)
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    sender       = st.secrets.get("GMAIL_SENDER", "")
    app_password = st.secrets.get("GMAIL_APP_PASSWORD", "")

    if not sender or not app_password:
        return False, "Email not configured (GMAIL_SENDER / GMAIL_APP_PASSWORD missing in secrets)"

    if not app_url:
        app_url = "https://share.streamlit.io"

    role_label = "Administrator" if role == "admin" else "Student"

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#F8F9FF; margin:0; padding:0; }}
  .container {{ max-width:560px; margin:32px auto; background:#fff;
                border-radius:16px; overflow:hidden;
                box-shadow:0 4px 24px rgba(27,43,107,.10); }}
  .header {{ background:#1B2B6B; padding:32px 40px; text-align:center; }}
  .header h1 {{ color:#fff; font-size:26px; margin:0; font-weight:300;
                font-style:italic; letter-spacing:.02em; }}
  .header p {{ color:rgba(255,255,255,.55); font-size:12px;
               letter-spacing:.1em; text-transform:uppercase; margin:6px 0 0; }}
  .body {{ padding:36px 40px; }}
  .greeting {{ font-size:18px; color:#1B2B6B; font-weight:600; margin-bottom:8px; }}
  .text {{ font-size:14px; color:#5060A0; line-height:1.7; margin-bottom:20px; }}
  .cred-box {{ background:#EEF3FF; border:1.5px solid #C8D8FF;
               border-radius:10px; padding:20px 24px; margin:20px 0; }}
  .cred-row {{ display:flex; justify-content:space-between;
               align-items:center; padding:6px 0;
               border-bottom:1px solid rgba(200,216,255,.5); }}
  .cred-row:last-child {{ border-bottom:none; }}
  .cred-label {{ font-size:11px; color:#8898CC; text-transform:uppercase;
                 letter-spacing:.08em; font-family:monospace; }}
  .cred-value {{ font-size:14px; color:#1B2B6B; font-weight:600;
                 font-family:monospace; }}
  .btn {{ display:block; background:#1B2B6B; color:#fff !important;
          text-decoration:none; text-align:center; padding:14px 28px;
          border-radius:9px; font-size:15px; font-weight:600;
          margin:24px 0 8px; letter-spacing:.02em; }}
  .warning {{ background:#FFF8E7; border:1px solid #F9E3A0;
              border-radius:8px; padding:12px 16px; font-size:12px;
              color:#8B6408; margin:16px 0; line-height:1.6; }}
  .steps {{ margin:20px 0; }}
  .step {{ display:flex; gap:12px; align-items:flex-start; margin-bottom:12px; }}
  .step-num {{ background:#4A7CF7; color:#fff; border-radius:50%;
               width:22px; height:22px; display:flex; align-items:center;
               justify-content:center; font-size:11px; font-weight:700;
               flex-shrink:0; margin-top:1px; }}
  .step-text {{ font-size:13px; color:#5060A0; line-height:1.6; }}
  .footer {{ background:#F8F9FF; border-top:1px solid #E8ECF8;
             padding:20px 40px; text-align:center; }}
  .footer p {{ font-size:11px; color:#8898CC; margin:0; line-height:1.6; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>MathComp</h1>
    <p>Math Mission Thailand · Online Mathematics Competition</p>
  </div>
  <div class="body">
    <div class="greeting">Welcome, {display_name}! 🎉</div>
    <p class="text">
      Your MathComp account has been created. You can now log in and start
      practising mathematics competition problems. Your account details are below.
    </p>

    <div class="cred-box">
      <div class="cred-row">
        <span class="cred-label">Email (username)</span>
        <span class="cred-value">{to_email}</span>
      </div>
      <div class="cred-row">
        <span class="cred-label">Password</span>
        <span class="cred-value">{password}</span>
      </div>
      <div class="cred-row">
        <span class="cred-label">Account type</span>
        <span class="cred-value">{role_label}</span>
      </div>
    </div>

    <a href="{app_url}" class="btn">Log in to MathComp →</a>

    <div class="warning">
      🔒 <strong>Important:</strong> Please change your password after your first login.
      Keep your credentials confidential and do not share them with others.
    </div>

    <div class="steps">
      <p style="font-size:13px;font-weight:600;color:#1B2B6B;margin-bottom:12px;">How to get started:</p>
      <div class="step">
        <div class="step-num">1</div>
        <div class="step-text">Click the button above or go to <strong>{app_url}</strong></div>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-text">Enter your email and password from the box above</div>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-text">Choose a competition, set the number of questions, and click <strong>Start Exam</strong></div>
      </div>
      <div class="step">
        <div class="step-num">4</div>
        <div class="step-text">After submitting, view your results, AI analysis, and topic breakdown</div>
      </div>
    </div>
  </div>
  <div class="footer">
    <p>© Math Mission Thailand 2026 · MathComp Platform<br>
    If you did not expect this email, please ignore it or contact your administrator.</p>
  </div>
</div>
</body>
</html>
"""

    plain_body = f"""Welcome to MathComp, {display_name}!

Your account has been created by Math Mission Thailand.

Login details:
  Email:    {to_email}
  Password: {password}
  Role:     {role_label}

Login URL: {app_url}

Steps:
1. Go to {app_url}
2. Enter your email and password
3. Choose a competition and click Start Exam
4. After the exam, view your AI performance analysis

IMPORTANT: Please change your password after first login.

© Math Mission Thailand 2026 · MathComp Platform
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Welcome to MathComp — Your Login Details"
    msg["From"]    = f"MathComp · Math Mission Thailand <{sender}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body,  "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender, app_password)
            server.sendmail(sender, to_email, msg.as_string())
        return True, f"Email sent to {to_email}"
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail authentication failed — check GMAIL_SENDER and GMAIL_APP_PASSWORD"
    except smtplib.SMTPRecipientsRefused:
        return False, f"Email address rejected: {to_email}"
    except Exception as e:
        return False, f"Email error: {e}"


def upload_img(file, path: str) -> str:
    try:
        project_id = json.loads(st.secrets.get("FIREBASE_SERVICE_ACCOUNT","{}")).get("project_id","")
        bucket = f"{project_id}.appspot.com"
        url    = f"https://firebasestorage.googleapis.com/v0/b/{bucket}/o?uploadType=media&name={requests.utils.quote(path,safe='')}"
        resp   = requests.post(url, data=file.read(), headers={"Content-Type": file.type}, timeout=30)
        if resp.ok:
            token = resp.json().get("downloadTokens","")
            return f"https://firebasestorage.googleapis.com/v0/b/{bucket}/o/{requests.utils.quote(path,safe='')}?alt=media&token={token}"
    except Exception as e:
        st.warning(f"Image upload failed: {e}")
    return ""

def save_question(doc: dict):
    db.collection("questions").add(doc)

# ══════════════════════════════════════════════
# Scoring
# ══════════════════════════════════════════════
def compute_score(competition, questions, answers) -> dict:
    rules = get_all_competitions().get(competition,{}).get("scoring",{"correct":1,"wrong":0,"blank":0})
    raw = max_s = 0.0
    tbd = {t:{"correct":0,"total":0} for t in TOPICS+["Other"]}
    pqs = []
    for q in questions:
        qid=q["id"]; topic=q.get("topic","Other")
        if topic not in tbd: topic="Other"
        ca=str(q.get("correct_answer","")).strip().upper()
        ch=str(answers.get(qid,"")).strip().upper()
        ok=ch==ca and ch!=""; blank=ch==""
        raw  += rules["correct"] if ok else (rules["blank"] if blank else rules["wrong"])
        max_s+= rules["correct"]
        tbd[topic]["total"]+=1
        if ok: tbd[topic]["correct"]+=1
        pqs.append({"qid":qid,"correct":ok,"chosen":answers.get(qid),"right_answer":q.get("correct_answer"),"time_sec":answers.get(f"{qid}__time",0)})
    tbd = {k:v for k,v in tbd.items() if v["total"]>0}
    pct = round(raw/max_s*100,1) if max_s>0 else 0.0
    return {"raw_score":round(raw,1),"max_score":round(max_s,1),"pct":pct,"topic_breakdown":tbd,"per_question":pqs}

def save_session(uid,competition,level,difficulty,questions,answers,result,duration) -> str:
    data = {
        "competition":competition,"level":level,"difficulty":difficulty,
        "timestamp_start":datetime.now(timezone.utc),"duration_sec":duration,
        "total_questions":len(questions),"raw_score":result["raw_score"],
        "max_score":result["max_score"],"pct":result["pct"],
        "topic_breakdown":result["topic_breakdown"],
        "answers":{q["id"]:{"chosen":answers.get(q["id"]),"correct":q.get("correct_answer"),
                             "is_correct":pq["correct"],"time_sec":answers.get(f"{q['id']}__time",0),
                             "topic":q.get("topic","Other")} for q,pq in zip(questions,result["per_question"])},
    }
    _,ref = db.collection("users").document(uid).collection("exam_sessions").add(data)
    return ref.id

# ══════════════════════════════════════════════
# Charts
# ══════════════════════════════════════════════
def radar_chart(tbd) -> go.Figure:
    topics = list(tbd.keys())
    scores = [round(v["correct"]/v["total"]*100) if v["total"]>0 else 0 for v in tbd.values()]
    fig = go.Figure(go.Scatterpolar(
        r=scores+[scores[0]], theta=topics+[topics[0]], fill="toself",
        fillcolor="rgba(74,124,247,0.12)", line=dict(color="#4A7CF7",width=2), marker=dict(size=5,color="#4A7CF7")))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True,range=[0,100],ticksuffix="%",tickfont=dict(size=10,color="#8898CC"),gridcolor="rgba(200,216,255,0.4)"),
                   angularaxis=dict(tickfont=dict(size=11,color="#1B2B6B"),gridcolor="rgba(200,216,255,0.4)"),bgcolor="rgba(0,0,0,0)"),
        showlegend=False, margin=dict(l=50,r=50,t=40,b=40),
        paper_bgcolor="rgba(0,0,0,0)", height=300)
    return fig

def sw(tbd):
    sc = {k:round(v["correct"]/v["total"]*100) for k,v in tbd.items() if v["total"]>0}
    if not sc: return "—","—"
    best=max(sc,key=sc.get); worst=min(sc,key=sc.get)
    return f"{best} ({sc[best]}%) — consistent accuracy", f"{worst} ({sc[worst]}%) — review recommended"

# ══════════════════════════════════════════════
# AI Performance Analysis
# ══════════════════════════════════════════════
def ai_analyze_performance(
    name: str,
    competition: str,
    level: str,
    result: dict,
    questions: list,
    duration: int,
) -> str:
    """
    Call Claude API to generate a personalized performance analysis.
    Returns the full analysis as a markdown string.
    """
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "_AI analysis unavailable — ANTHROPIC_API_KEY not set in secrets._"

    # Build topic summary
    tbd   = result["topic_breakdown"]
    topic_lines = []
    for topic, v in tbd.items():
        pct = round(v["correct"] / v["total"] * 100) if v["total"] > 0 else 0
        topic_lines.append(f"  - {topic}: {v['correct']}/{v['total']} correct ({pct}%)")
    topic_summary = "\n".join(topic_lines)

    # Build per-question detail (wrong answers only, to keep prompt short)
    wrong_qs = []
    for i, (q, pq) in enumerate(zip(questions, result["per_question"]), 1):
        if not pq["correct"] and pq["chosen"] is not None:
            wrong_qs.append(
                f"  Q{i} [{q.get('topic','?')}]: chose {pq['chosen']}, correct {pq['right_answer']}"
                + (f' — "{q.get("question_text","")[:80]}..."' if q.get("question_text") else "")
            )
    wrong_summary = "\n".join(wrong_qs[:15]) if wrong_qs else "  None — all attempted questions were correct."

    blank_c  = sum(1 for pq in result["per_question"] if pq["chosen"] is None)
    correct_c = sum(1 for pq in result["per_question"] if pq["correct"])
    wrong_c   = sum(1 for pq in result["per_question"] if not pq["correct"] and pq["chosen"] is not None)

    prompt = f"""You are an expert mathematics coach specializing in competition mathematics.
Analyze the following student exam result and provide a detailed, personalized, encouraging report.

Student name: {name}
Competition: {competition} — {level}
Score: {result['raw_score']} / {result['max_score']} ({result['pct']}%)
Time taken: {duration//60} min {duration%60} sec
Questions: {len(questions)} total — {correct_c} correct, {wrong_c} wrong, {blank_c} blank

Topic breakdown:
{topic_summary}

Wrong answers (first 15):
{wrong_summary}

Write a structured analysis in markdown with these sections:

## 🏆 Overall Performance
A 2-3 sentence summary of how the student did, mentioning their score and time.

## 💪 Strengths
2-3 specific strengths based on topics they did well in. Be specific and encouraging.

## 📈 Areas for Improvement
2-3 specific topics or skills to work on. For each one, give a concrete study tip or type of problem to practice.

## 🎯 Recommended Next Steps
3 actionable steps the student should take before their next exam. Be specific (e.g., "Practice 10 AMC 8 geometry problems focusing on circle theorems").

## ⭐ Encouragement
1 short paragraph of genuine encouragement tailored to their result.

Keep the tone warm, professional, and motivating. Use specific mathematical terms relevant to the topics. Total length: 300-400 words."""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-sonnet-4-5",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        if resp.ok:
            return resp.json()["content"][0]["text"]
        else:
            return f"_AI analysis failed (status {resp.status_code}). Please try again._"
    except Exception as e:
        return f"_AI analysis error: {e}_"


# ══════════════════════════════════════════════
# Page: Login
# ══════════════════════════════════════════════
def page_login():
    inject_css()
    topbar("Math Mission Thailand", show_user=False)
    st.markdown("""
    <div style="background:linear-gradient(135deg,#EEF3FF 0%,#FBF0FF 100%);
                padding:60px 20px;display:flex;align-items:center;justify-content:center;">
      <div style="width:380px;background:#fff;border-radius:20px;
                  box-shadow:0 8px 40px rgba(27,43,107,.12);padding:40px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:-40px;right:-40px;width:180px;height:180px;
                    background:radial-gradient(circle,rgba(244,114,182,.1) 0%,transparent 70%);"></div>
        <div style="font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.16em;
                    color:#4A7CF7;text-transform:uppercase;margin-bottom:12px;">Math Mission Thailand</div>
        <div style="font-family:'Fraunces',serif;font-size:36px;font-weight:300;
                    color:#1B2B6B;line-height:1.1;margin-bottom:6px;">
          Welcome to<br><em style="font-style:italic;color:#4A7CF7;">MathComp</em>
        </div>
        <div style="font-size:13px;color:#8898CC;margin-bottom:32px;">Online Mathematics Competition Platform</div>
      </div>
    </div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1,1.1,1])
    with col:
        with st.form("login"):
            email    = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            sub      = st.form_submit_button("Log in →", use_container_width=True, type="primary")
    if sub:
        if not email or not password: st.error("Please enter both email and password.")
        else:
            with st.spinner("Authenticating…"):
                user = sign_in(email, password)
            if user:
                uid = user["localId"]; profile = get_profile(uid)
                st.session_state.update({
                    "uid":uid,"email":email,
                    "display_name":profile.get("display_name",email.split("@")[0]),
                    "role":profile.get("role","student"),"page":"dashboard"})
                st.rerun()
            else: st.error("Incorrect email or password.")
    footer()

# ══════════════════════════════════════════════
# Page: Dashboard
# ══════════════════════════════════════════════
def page_dashboard():
    require_auth(); inject_css()
    uid  = st.session_state["uid"]
    name = st.session_state.get("display_name","Student")
    topbar("Dashboard")

    sessions = []
    try:
        sessions = [s.to_dict() for s in
                    db.collection("users").document(uid).collection("exam_sessions")
                    .order_by("timestamp_start",direction=firestore.Query.DESCENDING).limit(5).stream()]
    except: pass

    if sessions:
        last = sessions[0]; avg = round(sum(s["pct"] for s in sessions)/len(sessions),1)
        m1,m2,m3,m4 = f"{last['raw_score']} / {last['max_score']}",f"{last['pct']}%",str(len(sessions)),f"{avg}%"
        s1,s2,s3,s4 = last.get('competition','—'),"last session","exams taken","all time"
    else:
        m1=m2=m3=m4="—"; s1=s2=s3=s4=""

    st.markdown(f"""
    <div class="mc-hero">
      <div class="mc-hero-eyebrow">Good day</div>
      <div class="mc-hero-title">Welcome back, <em>{name}</em></div>
      <div class="mc-metrics">
        <div class="mc-metric"><div class="mc-metric-label">Last Score</div><div class="mc-metric-val">{m1}</div><div class="mc-metric-sub">{s1}</div></div>
        <div class="mc-metric"><div class="mc-metric-label">Accuracy</div><div class="mc-metric-val">{m2}</div><div class="mc-metric-sub">{s2}</div></div>
        <div class="mc-metric"><div class="mc-metric-label">Sessions</div><div class="mc-metric-val">{m3}</div><div class="mc-metric-sub">{s3}</div></div>
        <div class="mc-metric"><div class="mc-metric-label">Avg Accuracy</div><div class="mc-metric-val">{m4}</div><div class="mc-metric-sub">{s4}</div></div>
      </div>
    </div>
    <div class="mc-body">""", unsafe_allow_html=True)

    # Admin shortcut banner — only visible to admin
    if st.session_state.get("role") == "admin":
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1B2B6B,#243580);border-radius:12px;
                    padding:16px 24px;margin-bottom:20px;display:flex;align-items:center;gap:16px;">
          <span style="font-size:28px;">⚙️</span>
          <div style="flex:1;">
            <div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:2px;">Admin Panel</div>
            <div style="font-size:12px;color:rgba(255,255,255,.5);">Import questions · Manage members · Competition settings</div>
          </div>
        </div>""", unsafe_allow_html=True)
        col_ab1, col_ab2 = st.columns(2)
        if col_ab1.button("Open Admin Panel →", type="primary", key="admin_shortcut", use_container_width=True):
            st.session_state["page"] = "admin"; st.rerun()
        if col_ab2.button("📊 Analytics Dashboard →", key="analytics_shortcut", use_container_width=True):
            st.session_state["page"] = "admin_analytics"; st.rerun()
        st.divider()

    st.markdown('<span class="mc-section-lbl">Start a new exam</span>', unsafe_allow_html=True)
    st.markdown('<div class="mc-card">', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        # Pre-fill from direct competition URL
        default_comp = st.session_state.pop("_prefill_comp","") if "_prefill_comp" in st.session_state else None
        comp_keys    = list(get_all_competitions().keys())
        comp_idx     = comp_keys.index(default_comp) if default_comp and default_comp in comp_keys else 0
        competition  = st.selectbox("Competition", comp_keys, index=comp_idx)
        comp_info   = get_all_competitions()[competition]
        st.caption(comp_info["description"])
        level = st.selectbox("Level / Division", comp_info["levels"])
    with cb:
        difficulty  = st.selectbox("Difficulty", DIFFICULTY_OPTIONS)
        n_questions = st.slider("Number of questions", 1, 100, 15, step=1)
        suggested   = n_questions * comp_info["secs_per_q"]
        st.caption(f"Suggested time: **{suggested//60} min** ({comp_info['secs_per_q']}s per question)")

    rules = comp_info["scoring"]
    if rules["wrong"] < 0:
        st.markdown(f'<div class="mc-penalty">⚠️ Penalty scoring: Correct +{rules["correct"]} · Wrong {rules["wrong"]} · Blank {rules["blank"]}</div>', unsafe_allow_html=True)

    if st.button("Start Exam →", type="primary", use_container_width=True):
        with st.spinner("Loading questions…"):
            qs = fetch_questions(competition, level, difficulty, n_questions)
        if not qs: st.error("No questions found. Try a different selection.")
        else:
            st.session_state.update({
                "page":"exam","competition":competition,"level":level,"difficulty":difficulty,
                "questions":qs,"answers":{},"flagged":set(),"current_idx":0,
                "start_time":time.time(),"time_limit":suggested,"exam_settings":load_settings(competition)})
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Quick nav buttons
    qn1, qn2 = st.columns(2)
    if qn1.button("📋  My full history & download", use_container_width=True):
        st.session_state["page"]="history"; st.rerun()
    if qn2.button("🏆  View leaderboard", use_container_width=True):
        st.session_state["page"]="leaderboard"; st.rerun()

    if sessions:
        st.markdown('<span class="mc-section-lbl" style="display:block;margin-top:20px;">Recent sessions</span>', unsafe_allow_html=True)
        for s in sessions:
            ts  = s.get("timestamp_start"); dt = ts.strftime("%d %b %Y") if ts else "—"
            pct = s.get("pct",0)
            c1,c2,c3,c4 = st.columns([3,2,2,1])
            c1.markdown(f"**{s.get('competition','')}** · {s.get('level','')}")
            c2.markdown(f"<span style='font-size:13px;color:#8898CC;'>{dt}</span>", unsafe_allow_html=True)
            c3.markdown(f"{s.get('raw_score','')} / {s.get('max_score','')}  ({pct}%)")
            c4.markdown("🟢" if pct>=70 else ("🟡" if pct>=50 else "🔴"))

    st.markdown("</div>", unsafe_allow_html=True)
    footer()

# ══════════════════════════════════════════════
# Page: Exam
# ══════════════════════════════════════════════
def _go(idx): st.session_state["current_idx"] = idx

def _submit():
    uid=st.session_state["uid"]; qs=st.session_state["questions"]; answers=st.session_state["answers"]
    duration=int(time.time()-st.session_state["start_time"])
    result=compute_score(st.session_state["competition"],qs,answers)
    sid=save_session(uid,st.session_state["competition"],st.session_state["level"],
                     st.session_state["difficulty"],qs,answers,result,duration)
    st.session_state.update({"page":"result","result":result,"session_id":sid,"duration":duration})
    st.rerun()

def page_exam():
    require_auth(); inject_css()
    qs       = st.session_state["questions"]
    answers  = st.session_state["answers"]
    flagged  = st.session_state["flagged"]
    idx      = st.session_state["current_idx"]
    settings = st.session_state.get("exam_settings", DEFAULT_SETTINGS)
    remaining = max(0.0, st.session_state["time_limit"]-(time.time()-st.session_state["start_time"]))
    mins,secs = divmod(int(remaining), 60)
    if remaining == 0: _submit(); return

    js = get_anti_ai_js(settings)
    if js: components.html(js, height=0)

    warn = remaining < 300
    tc   = "#FCA5A5" if warn else "#ffffff"
    st.markdown(f"""
    <div style="background:#1B2B6B;padding:0 28px;height:54px;display:flex;align-items:center;gap:12px;">
      <span style="font-family:'DM Mono',monospace;font-size:13px;letter-spacing:.14em;color:#fff;font-weight:500;">MATHCOMP</span>
      <span style="width:1px;height:18px;background:rgba(255,255,255,.2);display:inline-block;"></span>
      <span style="background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.15);
                   font-family:'DM Mono',monospace;font-size:11px;padding:3px 10px;border-radius:4px;
                   color:rgba(255,255,255,.7);">{st.session_state['competition']}</span>
      <span style="background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.15);
                   font-family:'DM Mono',monospace;font-size:11px;padding:3px 10px;border-radius:4px;
                   color:rgba(255,255,255,.7);">{st.session_state['level']}</span>
      <span style="font-size:13px;color:#fff;font-weight:500;flex:1;">Question {idx+1} of {len(qs)}</span>
      <div style="display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.1);
                  border:1px solid rgba(255,255,255,.15);border-radius:8px;padding:6px 14px;">
        <span style="font-size:9px;font-family:'DM Mono',monospace;letter-spacing:.1em;
                     color:rgba(255,255,255,.45);text-transform:uppercase;">Time left</span>
        <span style="font-family:'DM Mono',monospace;font-size:18px;font-weight:500;
                     color:{tc};letter-spacing:.08em;">{'⚠️ ' if warn else ''}{mins:02d}:{secs:02d}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    if warn: st.warning("⚠️  Less than 5 minutes remaining!")

    answered_count = sum(1 for q in qs if answers.get(q["id"]) is not None)
    st.progress(answered_count/len(qs), text=f"{answered_count} of {len(qs)} answered")

    # Navigator
    dots_html = ""
    for i,q in enumerate(qs):
        if i==idx:
            dots_html += f'<span class="mc-nav-dot" style="background:#1B2B6B;border-color:#1B2B6B;color:#fff;font-weight:600;">{i+1}</span>'
        elif q["id"] in flagged:
            dots_html += f'<span class="mc-nav-dot" style="background:#FDF2F8;border-color:#F472B6;color:#9D174D;">🚩</span>'
        elif answers.get(q["id"]) is not None:
            dots_html += f'<span class="mc-nav-dot" style="background:#EEF3FF;border-color:#4A7CF7;color:#1B2B6B;">✓{i+1}</span>'
        else:
            dots_html += f'<span class="mc-nav-dot">{i+1}</span>'
    st.markdown(f'<div class="mc-nav-strip">{dots_html}</div>', unsafe_allow_html=True)

    # Question
    q = qs[idx]; qid = q["id"]
    # Per-question timer
    tpq = settings.get("time_per_question", 0)
    if tpq and tpq > 0:
        q_key = f"q_start_{idx}"
        if q_key not in st.session_state:
            st.session_state[q_key] = time.time()
        q_elapsed = time.time() - st.session_state[q_key]
        q_remain  = max(0, tpq - q_elapsed)
        qm, qs2   = divmod(int(q_remain), 60)
        qtc = "#EF4444" if q_remain < 10 else ("#F5A623" if q_remain < 30 else "#4A7CF7")
        q_timer_html = (
            f'<span style="background:rgba(74,124,247,.1);border:1px solid #C8D8FF;'
            f'border-radius:6px;padding:3px 10px;font-family:monospace;'
            f'font-size:11px;color:{qtc};font-weight:600;">⏱ {qm:02d}:{qs2:02d}</span>'
        )
        if q_remain == 0:
            # Auto-advance to next question
            if idx < len(qs)-1:
                st.session_state["current_idx"] = idx + 1
            st.rerun()
    else:
        q_timer_html = ""

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
      <span style="font-family:'DM Mono',monospace;font-size:11px;color:#8898CC;">Q{idx+1} / {len(qs)}</span>
      <span style="font-size:11px;font-family:'DM Mono',monospace;padding:3px 10px;border-radius:20px;
                   background:#EEF3FF;border:1px solid #C8D8FF;color:#4A7CF7;">{q.get('topic','')}</span>
      {q_timer_html}
    </div>""", unsafe_allow_html=True)

    if q.get("question_image_url"): st.image(q["question_image_url"], use_container_width=True)
    if q.get("question_text"):      st.markdown(q["question_text"])
    st.write("")

    answer_type = q.get("answer_type","mc4"); current_ans = answers.get(qid)
    if answer_type in ("mc4","mc5"):
        choices = q.get("choices",[]); labels = [chr(65+i) for i in range(len(choices))]
        options = [f"{labels[i]}.  {choices[i]}" for i in range(len(choices))]
        cur = options[labels.index(current_ans.upper())] if current_ans and current_ans.upper() in labels else None
        choice = st.radio("Select your answer:", options, index=options.index(cur) if cur else None, key=f"r_{qid}")
        if choice: answers[qid]=choice[0]; st.session_state["answers"]=answers
    else:
        lbl = "Enter integer answer:" if answer_type=="integer" else "Enter decimal answer:"
        val = st.text_input(lbl, value=current_ans or "", key=f"i_{qid}")
        if val:
            try:
                int(val) if answer_type=="integer" else float(val)
                answers[qid]=val; st.session_state["answers"]=answers
            except ValueError: st.error("Please enter a valid number.")

    is_f = qid in flagged
    if st.button("🚩 Remove flag" if is_f else "🏳 Flag for review", key=f"f_{qid}"):
        flagged.discard(qid) if is_f else flagged.add(qid)
        st.session_state["flagged"]=flagged; st.rerun()

    st.divider()
    n1,n2,n3 = st.columns([1,2,1])
    if idx>0:         n1.button("← Previous", on_click=_go, args=(idx-1,), use_container_width=True)
    if idx<len(qs)-1: n3.button("Next →",     on_click=_go, args=(idx+1,), use_container_width=True)
    with n2:
        if st.button("✅  Submit Exam", type="primary", use_container_width=True):
            if len(qs)-answered_count==0: _submit()
            else: st.session_state["confirm_submit"]=True

    if st.session_state.get("confirm_submit"):
        st.warning(f"You have **{len(qs)-answered_count}** unanswered question(s). Submit anyway?")
        ca,cb = st.columns(2)
        if ca.button("Yes, submit now", type="primary"):
            st.session_state.pop("confirm_submit",None); _submit()
        if cb.button("Go back"):
            st.session_state.pop("confirm_submit",None); st.rerun()
    footer()

# ══════════════════════════════════════════════
# Page: Result
# ══════════════════════════════════════════════
def page_result():
    require_auth(); inject_css()
    result=st.session_state["result"]; competition=st.session_state["competition"]
    level=st.session_state["level"]; qs=st.session_state["questions"]
    duration=st.session_state.get("duration",0); settings=st.session_state.get("exam_settings",DEFAULT_SETTINGS)
    correct_c=sum(1 for pq in result["per_question"] if pq["correct"])
    wrong_c  =sum(1 for pq in result["per_question"] if not pq["correct"] and pq["chosen"] is not None)
    blank_c  =sum(1 for pq in result["per_question"] if pq["chosen"] is None)

    topbar("Exam Results")
    st.markdown(f"""
    <div class="mc-result-hero">
      <div style="font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.15em;
                  color:rgba(255,255,255,.4);text-transform:uppercase;margin-bottom:14px;position:relative;">
        {competition} · {level} · {len(qs)} questions · {datetime.now().strftime('%d %b %Y')}
      </div>
      <div class="mc-result-score">{result['raw_score']} <span>/ {result['max_score']}</span></div>
      <div class="mc-result-meta">
        <div class="mc-rm"><div class="mc-rm-val">{result['pct']}%</div><div class="mc-rm-lbl">Accuracy</div></div>
        <div class="mc-rm"><div class="mc-rm-val">{duration//60}m {duration%60}s</div><div class="mc-rm-lbl">Time taken</div></div>
        <div class="mc-rm"><div class="mc-rm-val">{correct_c} / {len(qs)}</div><div class="mc-rm-lbl">Correct</div></div>
        <div class="mc-rm"><div class="mc-rm-val">{wrong_c}</div><div class="mc-rm-lbl">Wrong</div></div>
      </div>
    </div>
    <div class="mc-body">""", unsafe_allow_html=True)

    col_r,col_b = st.columns(2)
    with col_r:
        st.markdown('<span class="mc-section-lbl">Performance by topic</span>', unsafe_allow_html=True)
        st.plotly_chart(radar_chart(result["topic_breakdown"]), use_container_width=True)
    with col_b:
        st.markdown('<span class="mc-section-lbl">Topic breakdown</span>', unsafe_allow_html=True)
        bars = ""
        for topic,v in result["topic_breakdown"].items():
            pct   = round(v["correct"]/v["total"]*100) if v["total"]>0 else 0
            color = "#4A7CF7" if pct>=50 else "#F472B6"
            bars += f'<div class="mc-topic-row"><span class="mc-topic-name">{topic}</span><div class="mc-bar-bg"><div class="mc-bar-fill" style="width:{pct}%;background:{color};"></div></div><span class="mc-bar-pct">{pct}%</span></div>'
        strength,weakness = sw(result["topic_breakdown"])
        st.markdown(bars + f"""
        <div class="mc-insight-good"><div class="mc-insight-lbl">Strength</div><div class="mc-insight-text">{strength}</div></div>
        <div class="mc-insight-bad"><div class="mc-insight-lbl">Needs work</div><div class="mc-insight-text">{weakness}</div></div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── AI Performance Analysis ──────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#EEF3FF,#FDF2F8);
                border:1.5px solid #C8D8FF;border-radius:16px;padding:20px 24px;margin-bottom:4px;">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
        <span style="font-size:24px;">🤖</span>
        <div>
          <div style="font-size:15px;font-weight:600;color:#1B2B6B;">AI Performance Analysis</div>
          <div style="font-size:12px;color:#8898CC;">Powered by Claude · Personalized coaching report</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Run analysis automatically or on button press
    if "ai_analysis" not in st.session_state:
        st.session_state["ai_analysis"] = None
        st.session_state["ai_analysis_loading"] = False

    if st.session_state.get("ai_analysis"):
        # Show cached analysis
        st.markdown(
            f'<div style="background:#fff;border:1.5px solid #E8ECF8;border-radius:12px;'
            f'padding:24px 28px;line-height:1.8;">{st.session_state["ai_analysis"]}</div>',
            unsafe_allow_html=True
        )
        if st.button("🔄  Regenerate analysis", key="regen_ai"):
            st.session_state["ai_analysis"] = None
            st.rerun()
    else:
        col_ai1, col_ai2 = st.columns([3, 1])
        col_ai1.markdown(
            "<p style='color:#5060A0;font-size:14px;margin:8px 0;'>"
            "Get a personalized coaching report — strengths, weaknesses, and study recommendations.</p>",
            unsafe_allow_html=True
        )
        if col_ai2.button("✨  Analyse my results", type="primary", key="run_ai", use_container_width=True):
            with st.spinner("Claude is analysing your performance…"):
                analysis = ai_analyze_performance(
                    name        = st.session_state.get("display_name", "Student"),
                    competition = competition,
                    level       = level,
                    result      = result,
                    questions   = qs,
                    duration    = duration,
                )
                st.session_state["ai_analysis"] = analysis
            st.rerun()

    st.divider()
    st.subheader("Question review")
    st.caption(f"✅ {correct_c} correct  ❌ {wrong_c} wrong  ⬜ {blank_c} blank")

    for i,(q,pq) in enumerate(zip(qs,result["per_question"])):
        chosen=pq["chosen"] or "—"; correct=pq["right_answer"] or "—"
        icon="✅" if pq["correct"] else ("⬜" if pq["chosen"] is None else "❌")
        with st.expander(f"{icon}  Q{i+1} · {q.get('topic','—')} · Your answer: **{chosen}** · Correct: **{correct}**"):
            if q.get("question_image_url"): st.image(q["question_image_url"],use_container_width=True)
            if q.get("question_text"):      st.markdown(q["question_text"])
            st.divider()
            if settings.get("show_answer_after_submit",True):
                if q.get("solution_image_url"): st.image(q["solution_image_url"],caption="Solution",use_container_width=True)
                if q.get("solution_text"):      st.markdown("**Solution:**"); st.markdown(q["solution_text"])
                if not q.get("solution_text") and not q.get("solution_image_url"): st.caption("No solution available.")
            else: st.caption("Solutions are not shown for this competition.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    _CLR = ("questions","answers","flagged","current_idx","start_time","time_limit",
            "result","session_id","duration","confirm_submit","exam_settings",
            "ai_analysis","ai_analysis_loading")
    b1,b2 = st.columns(2)
    if b1.button("← Back to dashboard", use_container_width=True):
        for k in _CLR: st.session_state.pop(k,None)
        st.session_state["page"]="dashboard"; st.rerun()
    if b2.button("Take another exam →", type="primary", use_container_width=True):
        for k in _CLR: st.session_state.pop(k,None)
        st.session_state["page"]="dashboard"; st.rerun()
    footer()

# ══════════════════════════════════════════════
# Page: Admin
# ══════════════════════════════════════════════
def page_admin():
    require_auth(); require_admin(); inject_css()
    topbar("Admin Panel")

    tab1,tab2,tab3,tab4 = st.tabs([
        "⚙️  Competition Settings",
        "📥  Import Questions",
        "👥  Members",
        "🏆  Competitions",
    ])

    # ── Tab 1: Settings ────────────────────────
    with tab1:
        st.subheader("Competition Settings")
        competition = st.selectbox("Select competition to configure", list(get_all_competitions(include_disabled=True).keys()), key="adm_comp")
        settings    = load_settings(competition)
        st.divider()
        st.markdown("#### ⚙️  Behavior Settings")

        def brow(label,caption,key,sk):
            c1,c2=st.columns([3,1]); c1.markdown(f"**{label}**"); c1.caption(caption)
            settings[sk]=c2.toggle(f"##{key}",value=settings[sk],key=key)

        brow("Load questions from Firebase","On — Firebase · Off — local JSON fallback","s_lfb","load_from_firebase")
        brow("Load student list from Firebase","Pulls student names for dropdown","s_lsl","load_student_list")
        brow("Require Competitor ID verification","Forces ID entry before exam","s_rid","require_competitor_id")
        brow("Show answer after submit","Shows correct answer and solution after submission","s_sas","show_answer_after_submit")
        brow("Allow bilingual (TH/EN) toggle","Requires both EN and TH content","s_bil","allow_bilingual")

        st.markdown("**⏱  Per-question time limit (optional)**")
        c_tpq1, c_tpq2 = st.columns([3,1])
        c_tpq1.caption("Set a time limit per question in seconds. 0 = disabled (students can take as long as needed).")
        settings["time_per_question"] = c_tpq2.number_input(
            "Seconds per question", min_value=0, max_value=600,
            value=int(settings.get("time_per_question",0)), step=10, key="s_tpq")
        if settings["time_per_question"] > 0:
            st.caption(f"Each question auto-advances after **{settings['time_per_question']} seconds** ({settings['time_per_question']//60}m {settings['time_per_question']%60}s).")

        st.divider()
        ec = sum(1 for k in ["anti_copy_text","noise_canvas","block_ctrl_c","block_text_selection",
                              "block_paste_answer","block_drag","block_right_click","tab_switch_warning",
                              "block_printscreen","clipboard_api_override","devtools_detection","screen_capture_block"] if settings.get(k))
        st.markdown(f"#### 🛡️  Anti-AI Protection &nbsp;&nbsp; `{ec} / 12 layers enabled`")

        cl,cr = st.columns(2)
        def arow(col,label,caption,key,sk):
            c1,c2=col.columns([3,1]); c1.markdown(f"**{label}**"); c1.caption(caption)
            settings[sk]=c2.toggle(f"##{key}",value=settings[sk],key=key)

        with cl:
            st.markdown("**Content Protection**")
            arow(cl,"Anti-copy text rendering","Clipboard content becomes garbled when pasted into AI","s_act","anti_copy_text")
            arow(cl,"Noise canvas overlay","Degrades screenshot quality for OCR/AI","s_nc","noise_canvas")
            arow(cl,"Block Ctrl+C / V / X / A","Disables clipboard keyboard shortcuts","s_bcc","block_ctrl_c")
            arow(cl,"Block text selection (>10 chars)","Prevents select-all then copy","s_bts","block_text_selection")
            arow(cl,"Block paste in answer boxes","Students must type answers manually","s_bpa","block_paste_answer")
            arow(cl,"Block drag","Prevents dragging question images","s_bdg","block_drag")
        with cr:
            st.markdown("**Browser / System**")
            arow(cr,"Block right-click","Prevents Inspect, Save image, etc.","s_brc","block_right_click")
            arow(cr,"Tab / window switch warning","Warns when student leaves exam tab","s_tsw","tab_switch_warning")
            arow(cr,"Block PrintScreen","Intercepts PrintScreen key","s_bps","block_printscreen")
            arow(cr,"Clipboard API override","Stops AI extensions from reading clipboard","s_cao","clipboard_api_override")
            arow(cr,"DevTools detection","Detects open developer tools","s_dvd","devtools_detection")
            arow(cr,"Screen Capture API block","Blocks browser-based screen recording","s_scb","screen_capture_block")

        st.divider()
        if st.button("💾  Save settings", type="primary", use_container_width=True):
            save_settings(competition, settings)
            st.success(f"Settings saved for **{competition}**")

    # ── Tab 2: Import Questions ────────────────
    with tab2:
        st.subheader("Import Questions")
        st.caption("Add questions to the database using any of the 4 methods below.")

        method = st.radio("Import method",
            ["✏️  Type directly","🖼️  Upload image","🤖  AI-OCR from image","📄  PDF batch import"],
            horizontal=True, key="import_method")
        st.divider()

        # ── AI helpers ────────────────────────────
        API_KEY = st.secrets.get("ANTHROPIC_API_KEY","")
        AI_HEADERS = {
            "Content-Type":    "application/json",
            "x-api-key":       API_KEY,
            "anthropic-version":"2023-06-01",
        }

        def ai_call(messages:list, max_tokens:int=1500) -> str | None:
            """Make a Claude API call; return text or None."""
            if not API_KEY: return None
            try:
                resp = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=AI_HEADERS,
                    json={"model":"claude-sonnet-4-5","max_tokens":max_tokens,"messages":messages},
                    timeout=45,
                )
                if resp.ok: return resp.json()["content"][0]["text"].strip()
                st.warning(f"AI call failed: {resp.status_code}")
            except Exception as e:
                st.warning(f"AI error: {e}")
            return None

        def ai_assess_question(q_text:str="", img_b64:str="", img_mime:str="", competition:str="") -> dict:
            """Ask Claude to identify difficulty and topic for a question."""
            parts = []
            if img_b64: parts.append({"type":"image","source":{"type":"base64","media_type":img_mime,"data":img_b64}})
            if q_text:  parts.append({"type":"text","text":q_text})
            parts.append({"type":"text","text":
                f"""You are an expert mathematics competition coach.
Analyse this question for {competition or "a math competition"}.
Respond ONLY with a JSON object with exactly these fields:
{{
  "difficulty": "easy" | "intermediate" | "advanced",
  "topic": "Algebra" | "Number Theory" | "Geometry" | "Combinatorics" | "Word Problem" | "Other",
  "difficulty_reason": "one sentence",
  "topic_reason": "one sentence"
}}"""
            })
            raw = ai_call([{"role":"user","content":parts}], max_tokens=200)
            if raw:
                try:
                    return json.loads(raw.replace("```json","").replace("```","").strip())
                except: pass
            return {}

        def ai_full_extract(img_b64:str, img_mime:str, competition:str, answer_type:str) -> dict:
            """
            Full extraction from a question image:
            - question text (LaTeX)
            - multiple choice options (if present)
            - correct answer
            - topic + difficulty
            - worked solution
            Returns a dict with all fields.
            """
            n_choices = 4 if answer_type=="mc4" else (5 if answer_type=="mc5" else 0)
            choice_instruction = (
                f"Extract the {n_choices} multiple choice options labelled A–{chr(64+n_choices)} exactly as written."
                if n_choices > 0 else
                "There are no multiple choice options — the answer is a number."
            )
            prompt = f"""You are an expert mathematics competition coach for {competition or "math competitions"}.

Read this question image carefully and extract EVERYTHING.

{choice_instruction}

Respond ONLY with a valid JSON object (no markdown, no extra text):
{{
  "question_text": "full question in LaTeX — use $...$ inline, $$...$$ for display",
  "choices": ["choice A text", "choice B text", ...],
  "correct_answer": "A" or "B" ... or numeric string if no choices,
  "topic": "Algebra" | "Number Theory" | "Geometry" | "Combinatorics" | "Word Problem" | "Other",
  "difficulty": "easy" | "intermediate" | "advanced",
  "difficulty_reason": "one sentence",
  "topic_reason": "one sentence",
  "solution_text": "full worked solution in LaTeX — step by step, show all working"
}}

Rules:
- Use LaTeX for ALL mathematical expressions
- For choices: include ONLY the text/expression, NOT the letter label
- solution_text must be a complete worked solution showing every step
- If the image is unclear about any field, make your best educated guess"""

            raw = ai_call([{"role":"user","content":[
                {"type":"image","source":{"type":"base64","media_type":img_mime,"data":img_b64}},
                {"type":"text","text":prompt}
            ]}], max_tokens=2000)

            if raw:
                try:
                    return json.loads(raw.replace("```json","").replace("```","").strip())
                except Exception as e:
                    st.warning(f"Could not parse AI response: {e}")
                    # Return partial result with raw text
                    return {"question_text": raw, "choices":[], "correct_answer":"",
                            "topic":"Other","difficulty":"intermediate","solution_text":""}
            return {}

        def ai_generate_solution(q_text:str, choices:list, correct:str, competition:str) -> str:
            """Generate a worked solution for a typed/existing question."""
            choices_str = ""
            if choices:
                labels = [chr(65+i) for i in range(len(choices))]
                choices_str = "\n".join(f"{labels[i]}. {choices[i]}" for i in range(len(choices)))
                choices_str = f"\n\nAnswer choices:\n{choices_str}\n\nCorrect answer: {correct}"
            prompt = f"""You are an expert mathematics competition coach.

Write a complete, step-by-step worked solution for this competition mathematics question.
Use LaTeX for all mathematical expressions ($...$ inline, $$...$$ display).
Show every step clearly. Competition: {competition or "math competition"}.

Question:
{q_text}{choices_str}

Provide a thorough solution that a student can learn from."""

            return ai_call([{"role":"user","content":prompt}], max_tokens=1500) or ""

        def meta_fields(p="", q_text_for_ai="", img_b64_for_ai="", img_mime_for_ai=""):
            c1,c2 = st.columns(2)
            comp  = c1.selectbox("Competition",list(get_all_competitions(include_disabled=True).keys()),key=f"{p}comp")
            level = c2.selectbox("Level",get_all_competitions().get(comp,{}).get("levels",["General"]),key=f"{p}level")

            # AI assess button
            ai_result = st.session_state.get(f"{p}ai_assess",{})
            ai_col1, ai_col2 = st.columns([3,1])
            with ai_col2:
                if st.button("🤖 AI assess difficulty & topic", key=f"{p}ai_btn", use_container_width=True):
                    with st.spinner("Claude is analysing the question…"):
                        result = ai_assess_question(q_text_for_ai, img_b64_for_ai, img_mime_for_ai, comp)
                        if result:
                            st.session_state[f"{p}ai_assess"] = result
                            st.rerun()
                        else:
                            st.warning("AI assessment unavailable — fill in manually.")
            with ai_col1:
                if ai_result:
                    st.markdown(
                        f"<div style='background:#EEF3FF;border:1px solid #C8D8FF;border-radius:8px;"
                        f"padding:8px 14px;font-size:13px;'>"
                        f"🤖 AI suggests: <strong>Topic — {ai_result.get('topic','?')}</strong> · "
                        f"<strong>Difficulty — {ai_result.get('difficulty','?')}</strong><br>"
                        f"<span style='color:#8898CC;font-size:11px;'>{ai_result.get('topic_reason','')} "
                        f"· {ai_result.get('difficulty_reason','')}</span></div>",
                        unsafe_allow_html=True)

            c3,c4,c5,c6 = st.columns(4)
            # Use AI suggestion as default if available
            ai_topic = ai_result.get("topic","Algebra")
            ai_diff  = ai_result.get("difficulty","easy")
            topic_opts = TOPICS+["Other"]
            diff_opts  = ["easy","intermediate","advanced"]
            t_idx = topic_opts.index(ai_topic) if ai_topic in topic_opts else 0
            d_idx = diff_opts.index(ai_diff)   if ai_diff  in diff_opts  else 0

            topic = c3.selectbox("Topic",    topic_opts, index=t_idx, key=f"{p}topic")
            diff  = c4.selectbox("Difficulty",diff_opts, index=d_idx, key=f"{p}diff")
            year  = c5.number_input("Year",2000,2030,datetime.now().year,key=f"{p}year")
            atype = c6.selectbox("Answer type",["mc4","mc5","integer","decimal"],key=f"{p}atype")
            return comp,level,topic,diff,int(year),atype

        def ans_fields(atype,p=""):
            choices=[]
            if atype in ("mc4","mc5"):
                n=4 if atype=="mc4" else 5
                st.markdown("**Answer choices**")
                cols=st.columns(n)
                for i in range(n): choices.append(cols[i].text_input(chr(65+i),key=f"{p}ch{i}"))
                correct=st.selectbox("Correct answer",[chr(65+i) for i in range(n)],key=f"{p}correct")
            else:
                correct=st.text_input("Correct answer (number)",key=f"{p}correct")
            return choices,correct

        def sol_fields(p=""):
            st.markdown("**Solution (optional)**")
            st_text=st.text_area("Solution text / LaTeX",height=100,key=f"{p}sol_text")
            st_img =st.file_uploader("Solution image",type=["png","jpg","jpeg"],key=f"{p}sol_img")
            return st_text,st_img

        # Method 1 — Type
        if method == "✏️  Type directly":
            st.markdown("#### Type question with LaTeX support")
            st.caption("Use `$...$` for inline math and `$$...$$` for display math.")
            q_text_pre = st.session_state.get('t_qtext','')
            comp,level,topic,diff,year,atype = meta_fields("t_",q_text_for_ai=q_text_pre)
            q_text = st.text_area("Question text (LaTeX supported)", height=120, key="t_qtext")
            q_img  = st.file_uploader("Question figure (optional)", type=["png","jpg","jpeg"], key="t_qimg")
            if q_text:
                with st.expander("Preview"): st.markdown(q_text)
            choices,correct = ans_fields(atype,"t_")

            # AI generate solution
            st.markdown("**Solution**")
            sc1,sc2 = st.columns([3,1])
            t_sol = sc1.text_area("Solution text / LaTeX (optional)", height=100, key="t_sol_text")
            t_sol_img = sc2.file_uploader("Solution image", type=["png","jpg","jpeg"], key="t_sol_img")
            if q_text and st.button("🤖  AI generate solution", key="t_gen_sol"):
                with st.spinner("Claude is writing a solution…"):
                    ch_list = [st.session_state.get(f"t_ch{i}","") for i in range(4 if atype=="mc4" else 5)] if atype in ("mc4","mc5") else []
                    sol_generated = ai_generate_solution(q_text, ch_list, st.session_state.get("t_correct",""), comp)
                    if sol_generated:
                        st.session_state["t_sol_generated"] = sol_generated
                        st.rerun()
            if st.session_state.get("t_sol_generated") and not t_sol:
                t_sol = st.session_state["t_sol_generated"]
                st.markdown("**Generated solution preview:**")
                st.markdown(t_sol)

            if st.button("💾  Save question", type="primary", key="t_save"):
                if not q_text: st.error("Question text is required.")
                else:
                    with st.spinner("Saving…"):
                        q_url = upload_img(q_img,f"questions/{datetime.now().timestamp()}_q.{q_img.name.split('.')[-1]}") if q_img else ""
                        s_url = upload_img(sol_img,f"solutions/{datetime.now().timestamp()}_s.{sol_img.name.split('.')[-1]}") if sol_img else ""
                        final_sol = t_sol or st.session_state.pop("t_sol_generated","")  
                        save_question({"competition":comp,"level":level,"topic":topic,"difficulty":diff,"year":year,
                                       "answer_type":atype,"question_text":q_text,"question_image_url":q_url,
                                       "choices":choices,"correct_answer":correct,"solution_text":final_sol,"solution_image_url":s_url})
                    st.success("✅  Question saved!")

        # Method 2 — Image
        elif method == "🖼️  Upload image":
            st.markdown("#### Upload question as image")
            comp,level,topic,diff,year,atype = meta_fields("i_")
            q_img = st.file_uploader("Question image", type=["png","jpg","jpeg"], key="i_qimg")
            if q_img: st.image(q_img, caption="Preview", use_container_width=True)
            choices,correct = ans_fields(atype,"i_")
            sol_text,sol_img = sol_fields("i_")
            if st.button("💾  Save question", type="primary", key="i_save"):
                if not q_img: st.error("Please upload an image.")
                else:
                    with st.spinner("Uploading…"):
                        q_url = upload_img(q_img,f"questions/{datetime.now().timestamp()}_q.{q_img.name.split('.')[-1]}")
                        s_url = upload_img(sol_img,f"solutions/{datetime.now().timestamp()}_s.{sol_img.name.split('.')[-1]}") if sol_img else ""
                        save_question({"competition":comp,"level":level,"topic":topic,"difficulty":diff,"year":year,
                                       "answer_type":atype,"question_text":"","question_image_url":q_url,
                                       "choices":choices,"correct_answer":correct,"solution_text":sol_text,"solution_image_url":s_url})
                    st.success("✅  Question saved!")

        # Method 3 — AI-OCR (full extract: question + choices + solution)
        elif method == "🤖  AI-OCR from image":
            st.markdown("#### AI reads image — extracts question, choices, correct answer & solution")
            st.caption("Claude reads the full image and fills in all fields automatically. Review and edit before saving.")

            comp,level,topic,diff,year,atype = meta_fields("ai_")

            q_img = st.file_uploader("Question image", type=["png","jpg","jpeg"], key="ai_qimg")

            # ── Clear stale results when a new image is uploaded ──
            if q_img:
                # Track filename+size to detect a new upload
                img_sig = f"{q_img.name}_{q_img.size}"
                if st.session_state.get("ai_img_sig") != img_sig:
                    # New image — clear all previous extraction results
                    for k in ("ai_full","ai_ocr_result","ai_topic_override",
                              "ai_diff_override","ai_img_sig"):
                        st.session_state.pop(k, None)
                    st.session_state["ai_img_sig"] = img_sig
                st.image(q_img, caption=f"Uploaded: {q_img.name}", use_container_width=True)
            else:
                # No image — also clear stale data
                for k in ("ai_full","ai_ocr_result","ai_topic_override",
                          "ai_diff_override","ai_img_sig"):
                    st.session_state.pop(k, None)

            if q_img and st.button("🤖  Full AI Extract (question + choices + solution)", type="primary", key="ai_ocr"):
                with st.spinner("Claude is reading the image — extracting everything…"):
                    try:
                        q_img.seek(0)
                        img_b64 = base64.b64encode(q_img.read()).decode()
                        ext  = q_img.name.split(".")[-1].lower()
                        mime = "image/jpeg" if ext in ("jpg","jpeg") else f"image/{ext}"
                        result = ai_full_extract(img_b64, mime, comp, atype)
                        if result:
                            st.session_state["ai_full"] = result
                            st.success("✅  Extraction complete — review fields below and edit if needed.")
                            st.rerun()
                        else:
                            st.error("Extraction failed. Check your ANTHROPIC_API_KEY.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            # Pull extracted values (or empty defaults)
            extracted = st.session_state.get("ai_full", {})
            if extracted:
                st.markdown("""
                <div style='background:#EEF3FF;border:1.5px solid #C8D8FF;border-radius:10px;
                            padding:12px 16px;margin-bottom:12px;font-size:13px;color:#1B2B6B;'>
                🤖 <strong>AI extracted all fields below.</strong>
                Review each field carefully — edit anything that needs correction before saving.
                </div>""", unsafe_allow_html=True)

            # ── Editable fields pre-filled by AI ──
            q_text = st.text_area(
                "Question text (LaTeX)",
                value=extracted.get("question_text", st.session_state.get("ai_ocr_result","")),
                height=140, key="ai_qtext")
            if q_text:
                with st.expander("Preview question"): st.markdown(q_text)

            # Override topic/diff from AI extraction
            if extracted.get("topic") and extracted["topic"] in TOPICS+["Other"]:
                st.session_state["ai_topic_override"] = extracted["topic"]
            if extracted.get("difficulty") and extracted["difficulty"] in ["easy","intermediate","advanced"]:
                st.session_state["ai_diff_override"] = extracted["difficulty"]

            topic_opts = TOPICS+["Other"]
            diff_opts  = ["easy","intermediate","advanced"]
            ov_topic = st.session_state.get("ai_topic_override", extracted.get("topic","Algebra"))
            ov_diff  = st.session_state.get("ai_diff_override",  extracted.get("difficulty","intermediate"))
            ti = topic_opts.index(ov_topic) if ov_topic in topic_opts else 0
            di = diff_opts.index(ov_diff)   if ov_diff  in diff_opts  else 1

            tc1,tc2 = st.columns(2)
            topic_final = tc1.selectbox("Topic",    topic_opts, index=ti, key="ai_topic_sel")
            diff_final  = tc2.selectbox("Difficulty",diff_opts, index=di, key="ai_diff_sel")
            if extracted.get("topic_reason") or extracted.get("difficulty_reason"):
                st.caption(f"🤖 {extracted.get('topic_reason','')} · {extracted.get('difficulty_reason','')}")

            # ── Answer choices from AI ──
            ai_choices  = extracted.get("choices", [])
            ai_correct  = str(extracted.get("correct_answer",""))
            choices, correct = [], ""

            if atype in ("mc4","mc5"):
                n = 4 if atype=="mc4" else 5
                st.markdown("**Answer choices** (AI-filled — edit if needed)")
                ch_cols = st.columns(n)
                for i in range(n):
                    pre = ai_choices[i] if i < len(ai_choices) else ""
                    choices.append(ch_cols[i].text_input(chr(65+i), value=pre, key=f"ai_ch{i}"))
                labels = [chr(65+i) for i in range(n)]
                idx_c = labels.index(ai_correct.upper()) if ai_correct.upper() in labels else 0
                correct = st.selectbox("Correct answer", labels, index=idx_c, key="ai_correct_mc")
            else:
                correct = st.text_input("Correct answer (number)", value=ai_correct, key="ai_correct_num")

            # ── Solution from AI ──
            st.markdown("**Solution** (AI-generated — edit if needed)")
            sol_text = st.text_area(
                "Solution text (LaTeX)",
                value=extracted.get("solution_text",""),
                height=180, key="ai_sol_text")
            if sol_text:
                with st.expander("Preview solution"): st.markdown(sol_text)
            sol_img = st.file_uploader("Solution image (optional)", type=["png","jpg","jpeg"], key="ai_sol_img")

            # ── Generate solution separately if needed ──
            if q_text and st.button("🔄  Re-generate solution only", key="ai_regen_sol"):
                with st.spinner("Claude is writing a solution…"):
                    new_sol = ai_generate_solution(q_text, choices, correct, comp)
                    if new_sol:
                        extracted["solution_text"] = new_sol
                        st.session_state["ai_full"] = extracted
                        st.rerun()

            if st.button("💾  Save question", type="primary", key="ai_save"):
                if not q_text: st.error("Question text is required.")
                else:
                    with st.spinner("Saving…"):
                        ts = datetime.now().timestamp()
                        if q_img: q_img.seek(0)
                        q_url   = upload_img(q_img,     f"questions/{ts}_q.{q_img.name.split('.')[-1]}")     if q_img     else ""
                        s_url   = upload_img(sol_img,   f"solutions/{ts}_s.{sol_img.name.split('.')[-1]}")   if sol_img   else ""
                        save_question({
                            "competition":        comp,   "level":     level,
                            "topic":              topic_final,           "difficulty": diff_final,
                            "year":               year,   "answer_type":atype,
                            "question_text":      q_text, "question_image_url": q_url,
                            "choices":            choices,"correct_answer":     str(correct),
                            "solution_text":      sol_text,"solution_image_url":s_url,
                        })
                        for k in ("ai_ocr_result","ai_full","ai_topic_override","ai_diff_override"):
                            st.session_state.pop(k,None)
                    st.success("✅  Question saved!")

        # Method 4 — PDF batch
        elif method == "📄  PDF batch import":
            st.markdown("#### PDF → AI segments each question")
            comp   = st.selectbox("Competition",list(COMPETITIONS.keys()),key="pdf_comp")
            level  = st.selectbox("Level",COMPETITIONS[comp]["levels"],key="pdf_level")
            c1,c2  = st.columns(2)
            diff   = c1.selectbox("Difficulty (all)",["easy","intermediate","advanced"],key="pdf_diff")
            year   = c2.number_input("Year",2000,2030,datetime.now().year,key="pdf_year")
            atype  = st.selectbox("Answer type (all)",["mc5","mc4","integer","decimal"],key="pdf_atype")
            pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_upload")

            # Clear stale results when a new PDF is uploaded
            if pdf_file:
                pdf_sig = f"{pdf_file.name}_{pdf_file.size}"
                if st.session_state.get("pdf_sig") != pdf_sig:
                    st.session_state.pop("pdf_questions", None)
                    st.session_state["pdf_sig"] = pdf_sig
            else:
                st.session_state.pop("pdf_questions", None)
                st.session_state.pop("pdf_sig", None)

            if pdf_file and st.button("🤖  Extract questions from PDF", key="pdf_extract", type="primary"):
                with st.spinner("Claude is reading the PDF — extracting questions, choices, answers and solutions…"):
                    try:
                        pdf_b64 = base64.b64encode(pdf_file.read()).decode()
                        n_choices_info = (
                            f"Each question has {4 if atype=='mc4' else 5} multiple choice options labelled A–{'D' if atype=='mc4' else 'E'}."
                            if atype in ("mc4","mc5") else
                            "Questions have numeric answers (no multiple choice)."
                        )
                        pdf_prompt = f"""You are an expert mathematics competition coach.

Extract ALL mathematics questions from this PDF for {comp} competition.
{n_choices_info}

For EACH question, provide:
1. The full question text in LaTeX
2. All answer choices exactly as written (if multiple choice)
3. The correct answer (letter A-E or numeric)
4. Topic classification
5. Difficulty assessment
6. A complete step-by-step worked solution in LaTeX

Return ONLY a valid JSON array. Each element must have exactly these fields:
{{
  "question_text": "full question in LaTeX ($...$ inline, $$...$$ display)",
  "choices": ["option A", "option B", ...],
  "correct_answer": "A" or numeric string,
  "topic": "Algebra" | "Number Theory" | "Geometry" | "Combinatorics" | "Word Problem" | "Other",
  "difficulty": "easy" | "intermediate" | "advanced",
  "solution_text": "complete worked solution in LaTeX"
}}

No markdown, no explanation — ONLY the JSON array."""

                        raw = ai_call([{"role":"user","content":[
                            {"type":"document","source":{"type":"base64","media_type":"application/pdf","data":pdf_b64}},
                            {"type":"text","text":pdf_prompt}
                        ]}], max_tokens=6000)

                        if raw:
                            clean = raw.replace("```json","").replace("```","").strip()
                            qs_extracted = json.loads(clean)
                            st.session_state["pdf_questions"] = qs_extracted
                            n_with_sol = sum(1 for q in qs_extracted if q.get("solution_text","").strip())
                            st.success(f"✅  Extracted **{len(qs_extracted)}** questions — "
                                       f"{n_with_sol} with solutions, "
                                       f"{sum(1 for q in qs_extracted if q.get('choices'))} with choices.")
                        else:
                            st.error("Extraction failed. Check your ANTHROPIC_API_KEY.")
                    except json.JSONDecodeError as e:
                        st.error(f"JSON parse error: {e}. Try again — Claude sometimes adds extra text.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            if "pdf_questions" in st.session_state:
                pdf_qs = st.session_state["pdf_questions"]
                st.markdown(f"**{len(pdf_qs)} questions extracted — review each one:**")

                for i,q in enumerate(pdf_qs):
                    qt_preview = q.get("question_text","")[:55]
                    sol_icon   = "✅" if q.get("solution_text","").strip() else "⚠️"
                    ch_icon    = f"🔤{len(q.get('choices',[]))}" if q.get("choices") else "🔢"
                    with st.expander(
                        f"Q{i+1} {ch_icon} [{q.get('difficulty','?')}] [{q.get('topic','?')}] {sol_icon} — {qt_preview}…"
                    ):
                        # Question text
                        pdf_qs[i]["question_text"] = st.text_area(
                            "Question text (LaTeX)", value=q.get("question_text",""),
                            height=100, key=f"pdf_qt_{i}")
                        with st.expander("Preview question"):
                            st.markdown(pdf_qs[i]["question_text"])

                        # Topic + difficulty
                        pc1,pc2 = st.columns(2)
                        t_opts = TOPICS+["Other"]
                        d_opts = ["easy","intermediate","advanced"]
                        pdf_qs[i]["topic"] = pc1.selectbox("Topic", t_opts,
                            index=t_opts.index(q.get("topic","Other")) if q.get("topic") in t_opts else 0,
                            key=f"pdf_tp_{i}")
                        pdf_qs[i]["difficulty"] = pc2.selectbox("Difficulty", d_opts,
                            index=d_opts.index(q.get("difficulty","intermediate")) if q.get("difficulty") in d_opts else 1,
                            key=f"pdf_df_{i}")

                        # Choices
                        if atype in ("mc4","mc5"):
                            n = 4 if atype=="mc4" else 5
                            existing = q.get("choices",[""]*n)
                            st.markdown("**Answer choices**")
                            cols = st.columns(n); new_ch = []
                            for j in range(n):
                                new_ch.append(cols[j].text_input(
                                    chr(65+j),
                                    value=existing[j] if j < len(existing) else "",
                                    key=f"pdf_ch_{i}_{j}"))
                            pdf_qs[i]["choices"] = new_ch
                            labels = [chr(65+j) for j in range(n)]
                            ca = str(q.get("correct_answer","A")).upper()
                            pdf_qs[i]["correct_answer"] = st.selectbox(
                                "Correct answer", labels,
                                index=labels.index(ca) if ca in labels else 0,
                                key=f"pdf_ca_{i}")
                        else:
                            pdf_qs[i]["correct_answer"] = st.text_input(
                                "Correct answer", value=str(q.get("correct_answer","")),
                                key=f"pdf_ca_{i}")

                        # Solution
                        st.markdown("**Solution** (AI-generated)")
                        pdf_qs[i]["solution_text"] = st.text_area(
                            "Solution (LaTeX)", value=q.get("solution_text",""),
                            height=150, key=f"pdf_sol_{i}")
                        if pdf_qs[i]["solution_text"]:
                            with st.expander("Preview solution"):
                                st.markdown(pdf_qs[i]["solution_text"])

                        # Re-generate solution for this question
                        if st.button(f"🔄  Re-generate solution for Q{i+1}", key=f"pdf_regen_{i}"):
                            with st.spinner("Generating solution…"):
                                new_sol = ai_generate_solution(
                                    pdf_qs[i]["question_text"],
                                    pdf_qs[i].get("choices",[]),
                                    str(pdf_qs[i].get("correct_answer","")),
                                    comp
                                )
                                if new_sol:
                                    pdf_qs[i]["solution_text"] = new_sol
                                    st.session_state["pdf_questions"] = pdf_qs
                                    st.rerun()

                st.session_state["pdf_questions"] = pdf_qs
                st.divider()

                # Summary before saving
                n_sol = sum(1 for q in pdf_qs if q.get("solution_text","").strip())
                n_ch  = sum(1 for q in pdf_qs if q.get("choices"))
                st.info(f"📊  Ready to save: **{len(pdf_qs)}** questions · "
                        f"**{n_ch}** with choices · **{n_sol}** with solutions")

                if st.button(f"💾  Save all {len(pdf_qs)} questions to Firestore",
                             type="primary", key="pdf_save"):
                    with st.spinner(f"Saving {len(pdf_qs)} questions…"):
                        for q in pdf_qs:
                            save_question({
                                "competition":   comp,   "level":      level,
                                "topic":         q.get("topic","Other"),
                                "difficulty":    q.get("difficulty",diff),
                                "year":          int(year), "answer_type": atype,
                                "question_text": q.get("question_text",""),
                                "question_image_url": "",
                                "choices":       q.get("choices",[]),
                                "correct_answer":str(q.get("correct_answer","")),
                                "solution_text": q.get("solution_text",""),
                                "solution_image_url": "",
                            })
                    st.session_state.pop("pdf_questions",None)
                    st.success(f"✅  {len(pdf_qs)} questions saved to Firestore!")

        # ── Question Bank Browser (Editable) ───────
        st.divider()
        st.markdown("#### 📚  Question Bank — Browse & Edit")
        f1,f2,f3 = st.columns(3)
        qb_comp  = f1.selectbox("Filter competition", ["All"]+list(COMPETITIONS.keys()), key="qb_comp")
        qb_topic = f2.selectbox("Filter topic",       ["All"]+TOPICS+["Other"],          key="qb_topic")
        qb_diff  = f3.selectbox("Filter difficulty",  ["All","easy","intermediate","advanced"], key="qb_diff")

        if st.button("🔍  Browse questions", key="qb_browse", type="primary"):
            try:
                ref = db.collection("questions")
                if qb_comp  != "All": ref = ref.where("competition","==",qb_comp)
                if qb_topic != "All": ref = ref.where("topic","==",qb_topic)
                if qb_diff  != "All": ref = ref.where("difficulty","==",qb_diff)
                docs = list(ref.limit(100).stream())
                st.session_state["qb_docs"] = [(doc.id, doc.to_dict()) for doc in docs]
            except Exception as e:
                st.error(f"Error: {e}")

        qb_docs = st.session_state.get("qb_docs", [])
        if qb_docs:
            st.caption(f"**{len(qb_docs)} questions found** (max 100) — expand any to edit and save")
            for doc_id, d in qb_docs:
                qt  = d.get("question_text","(image only)")[:70]
                hdr = (f"[{d.get('competition','')}] "
                       f"[{d.get('level','')}] "
                       f"[{d.get('difficulty','')}] "
                       f"[{d.get('topic','')}] — {qt}…")
                with st.expander(hdr):
                    # ── Preview ──────────────────────────────
                    if d.get("question_image_url"):
                        st.image(d["question_image_url"], use_container_width=True)

                    ec1, ec2 = st.columns(2)
                    # ── Editable fields ───────────────────────
                    new_comp  = ec1.selectbox("Competition", list(COMPETITIONS.keys()),
                        index=list(COMPETITIONS.keys()).index(d.get("competition","AMC 8"))
                              if d.get("competition") in COMPETITIONS else 0,
                        key=f"e_comp_{doc_id}")
                    new_level = ec2.selectbox("Level", COMPETITIONS[new_comp]["levels"],
                        index=COMPETITIONS[new_comp]["levels"].index(d.get("level",""))
                              if d.get("level","") in COMPETITIONS[new_comp]["levels"] else 0,
                        key=f"e_level_{doc_id}")

                    ec3,ec4,ec5,ec6 = st.columns(4)
                    topic_opts = TOPICS+["Other"]
                    diff_opts  = ["easy","intermediate","advanced"]
                    new_topic = ec3.selectbox("Topic", topic_opts,
                        index=topic_opts.index(d.get("topic","Other"))
                              if d.get("topic") in topic_opts else 0,
                        key=f"e_topic_{doc_id}")
                    new_diff  = ec4.selectbox("Difficulty", diff_opts,
                        index=diff_opts.index(d.get("difficulty","easy"))
                              if d.get("difficulty") in diff_opts else 0,
                        key=f"e_diff_{doc_id}")
                    new_year  = ec5.number_input("Year", 2000, 2030,
                        value=int(d.get("year", datetime.now().year)),
                        key=f"e_year_{doc_id}")
                    atype_opts = ["mc4","mc5","integer","decimal"]
                    new_atype = ec6.selectbox("Answer type", atype_opts,
                        index=atype_opts.index(d.get("answer_type","mc4"))
                              if d.get("answer_type") in atype_opts else 0,
                        key=f"e_atype_{doc_id}")

                    new_qtext = st.text_area("Question text (LaTeX)",
                        value=d.get("question_text",""), height=100,
                        key=f"e_qtext_{doc_id}")

                    # Choices
                    new_choices = d.get("choices",[])
                    new_correct = d.get("correct_answer","")
                    if new_atype in ("mc4","mc5"):
                        n = 4 if new_atype=="mc4" else 5
                        st.markdown("**Answer choices**")
                        ch_cols = st.columns(n)
                        new_choices = []
                        for i in range(n):
                            existing_val = d.get("choices",[""]*(n))[i] if i < len(d.get("choices",[])) else ""
                            new_choices.append(ch_cols[i].text_input(
                                chr(65+i), value=existing_val, key=f"e_ch_{doc_id}_{i}"))
                        new_correct = st.selectbox("Correct answer",
                            [chr(65+i) for i in range(n)],
                            index=[chr(65+i) for i in range(n)].index(d.get("correct_answer","A"))
                                  if d.get("correct_answer","A") in [chr(65+i) for i in range(n)] else 0,
                            key=f"e_correct_{doc_id}")
                    else:
                        new_correct = st.text_input("Correct answer",
                            value=str(d.get("correct_answer","")),
                            key=f"e_correct_{doc_id}")

                    st.markdown("**Solution**")
                    esl1, esl2 = st.columns(2)
                    new_sol = esl1.text_area("Solution text / LaTeX",
                        value=d.get("solution_text",""), height=80,
                        key=f"e_sol_{doc_id}")
                    new_sol_img_file = esl2.file_uploader(
                        "Replace solution image",
                        type=["png","jpg","jpeg"], key=f"e_sol_img_{doc_id}")
                    if d.get("solution_image_url") and not new_sol_img_file:
                        st.image(d["solution_image_url"], caption="Current solution image", width=200)
                    elif new_sol_img_file:
                        st.image(new_sol_img_file, caption="New solution image preview", width=200)

                    # ── AI re-assess button ───────────────────
                    ai_key = f"e_ai_{doc_id}"
                    if st.button("🤖  AI re-assess difficulty & topic", key=f"e_ai_btn_{doc_id}"):
                        with st.spinner("Claude is re-analysing…"):
                            ai_r = ai_assess_question(new_qtext, "", "", new_comp)
                            if ai_r:
                                st.session_state[ai_key] = ai_r
                                st.rerun()
                    if ai_key in st.session_state:
                        ar = st.session_state[ai_key]
                        st.info(
                            f"🤖 AI suggests — **Topic: {ar.get('topic','?')}** · "
                            f"**Difficulty: {ar.get('difficulty','?')}** · "
                            f"{ar.get('topic_reason','')} · {ar.get('difficulty_reason','')}"
                        )

                    # ── Save / Delete buttons ─────────────────
                    sb1, sb2 = st.columns(2)
                    if sb1.button("💾  Save changes", type="primary",
                                  key=f"save_{doc_id}", use_container_width=True):
                        # Use AI suggestion if available
                        ar = st.session_state.get(ai_key, {})
                        final_topic = ar.get("topic", new_topic) if ar else new_topic
                        final_diff  = ar.get("difficulty", new_diff) if ar else new_diff
                        ts_now = datetime.now().timestamp()
                        new_sol_url = d.get("solution_image_url","")
                        if new_sol_img_file:
                            new_sol_url = upload_img(
                                new_sol_img_file,
                                f"solutions/{ts_now}_s.{new_sol_img_file.name.split('.')[-1]}"
                            )
                        updates = {
                            "competition":        new_comp,
                            "level":              new_level,
                            "topic":              final_topic,
                            "difficulty":         final_diff,
                            "year":               int(new_year),
                            "answer_type":        new_atype,
                            "question_text":      new_qtext,
                            "choices":            new_choices,
                            "correct_answer":     str(new_correct),
                            "solution_text":      new_sol,
                            "solution_image_url": new_sol_url,
                        }
                        db.collection("questions").document(doc_id).update(updates)
                        # Refresh cache
                        idx = next((i for i,(did,_) in enumerate(qb_docs) if did==doc_id), None)
                        if idx is not None:
                            st.session_state["qb_docs"][idx] = (doc_id, {**d, **updates})
                        st.success("✅  Question updated!")
                        st.rerun()

                    if sb2.button("🗑️  Delete", key=f"del_{doc_id}", use_container_width=True):
                        db.collection("questions").document(doc_id).delete()
                        st.session_state["qb_docs"] = [(did,dd) for did,dd in qb_docs if did!=doc_id]
                        st.warning("Question deleted.")
                        st.rerun()
        elif "qb_docs" in st.session_state:
            st.info("No questions found for this filter.")

    # ── Tab 3: Members ─────────────────────────
    with tab3:
        st.subheader("Member Management")
        mem1,mem2,mem_csv,mem3 = st.tabs(["👥  All Members","➕  Add Member","📤  Bulk CSV Upload","📊  Export"])

        with mem1:
            if st.button("🔄  Load members", key="load_members"):
                try: st.session_state["members"]=[{"uid":d.id,**d.to_dict()} for d in db.collection("users").stream()]
                except Exception as e: st.error(f"Error: {e}")
            members = st.session_state.get("members",[])
            if members:
                search = st.text_input("Search name or email",key="mem_search")
                filtered = [m for m in members if search.lower() in m.get("display_name","").lower() or search.lower() in m.get("email","").lower()] if search else members
                st.caption(f"{len(filtered)} members")
                for m in filtered:
                    c1,c2,c3,c4,c5 = st.columns([3,3,1,1,1])
                    c1.markdown(f"**{m.get('display_name','—')}**")
                    c2.caption(m.get("email","—"))
                    c3.caption(m.get("role","student"))
                    try: c4.caption(f"{len(list(db.collection('users').document(m['uid']).collection('exam_sessions').limit(99).stream()))} sessions")
                    except: c4.caption("—")
                    new_role = "admin" if m.get("role")=="student" else "student"
                    if c5.button(f"→ {new_role}",key=f"role_{m['uid']}"):
                        db.collection("users").document(m["uid"]).update({"role":new_role}); st.rerun()
            else: st.info("Click 'Load members' to view all users.")

        with mem2:
            st.markdown("#### Create new member account")
            with st.form("add_member"):
                c1,c2 = st.columns(2)
                nm = c1.text_input("Display name"); ne = c2.text_input("Email")
                c3,c4 = st.columns(2)
                np = c3.text_input("Password",type="password"); nr = c4.selectbox("Role",["student","admin"])
                sub_add = st.form_submit_button("Create account",type="primary",use_container_width=True)
            # Email settings for Add Member
            with st.expander("⚙️  Email notification settings"):
                send_email_toggle = st.toggle("Send welcome email to new member", value=True, key="add_send_email")
                app_url_add = st.text_input("App URL (for login link in email)",
                    value=st.secrets.get("APP_URL","https://share.streamlit.io"),
                    key="add_app_url")

            if sub_add:
                if not nm or not ne or not np: st.error("All fields required.")
                else:
                    try:
                        from firebase_admin import auth as fb_auth
                        user = fb_auth.create_user(email=ne, password=np, display_name=nm)
                        db.collection("users").document(user.uid).set({
                            "display_name":nm,"email":ne,"role":nr,
                            "created_at":datetime.now(timezone.utc)
                        })
                        st.success(f"✅  Account created for **{nm}** ({ne}) as **{nr}**")

                        # Send welcome email
                        if send_email_toggle:
                            with st.spinner(f"Sending welcome email to {ne}…"):
                                ok, msg = send_welcome_email(ne, nm, np, nr, app_url_add)
                            if ok:
                                st.success(f"📧  Welcome email sent to **{ne}**")
                            else:
                                st.warning(f"⚠️  Account created but email failed: {msg}")
                    except Exception as e: st.error(f"Error: {e}")

        with mem_csv:
            st.markdown("#### Bulk create accounts from CSV")
            st.caption("Upload a CSV file with columns: **display_name, email, password, role**")
            st.markdown("""
**CSV format example:**
```
display_name,email,password,role
Napat Suwan,napat@example.com,Pass1234!,student
Mint Charoenpol,mint@example.com,Pass5678!,student
Admin2,admin2@example.com,AdminPass!,admin
```
""")
            csv_template = "display_name,email,password,role\nNapat Suwan,napat@example.com,Pass1234!,student\nMint Charoenpol,mint@example.com,Pass5678!,student"
            st.download_button("⬇️  Download CSV template", csv_template.encode(), "members_template.csv", "text/csv")
            st.divider()
            csv_file = st.file_uploader("Upload members CSV", type=["csv"], key="bulk_csv")
            if csv_file:
                import io as _io
                import csv as _csv
                rows = list(_csv.DictReader(_io.StringIO(csv_file.read().decode("utf-8-sig"))))
                st.markdown(f"**{len(rows)} accounts found in CSV — preview:**")
                for i,r in enumerate(rows[:5]):
                    st.markdown(f"`{r.get('display_name','?')}` · `{r.get('email','?')}` · role: `{r.get('role','student')}`")
                if len(rows) > 5: st.caption(f"… and {len(rows)-5} more")
                st.divider()
                with st.expander("⚙️  Email notification settings"):
                    bulk_send_email = st.toggle("Send welcome email to each member", value=True, key="bulk_send_email")
                    bulk_app_url    = st.text_input("App URL (for login link in email)",
                        value=st.secrets.get("APP_URL","https://share.streamlit.io"),
                        key="bulk_app_url")
                    if bulk_send_email:
                        st.info("📧  Each member will receive a welcome email with their login credentials.")

                if st.button(f"🚀  Create {len(rows)} accounts", type="primary", key="bulk_create"):
                    from firebase_admin import auth as _fb_auth
                    success, failed = 0, []
                    prog = st.progress(0, text="Creating accounts…")
                    for i,r in enumerate(rows):
                        name  = r.get("display_name","").strip()
                        email = r.get("email","").strip()
                        pwd   = r.get("password","").strip()
                        role  = r.get("role","student").strip().lower()
                        if not name or not email or not pwd:
                            failed.append(f"{email} — missing fields"); continue
                        try:
                            user = _fb_auth.create_user(email=email, password=pwd, display_name=name)
                            db.collection("users").document(user.uid).set({
                                "display_name": name, "email": email,
                                "role": role, "created_at": datetime.now(timezone.utc)
                            })
                            success += 1
                            # Send welcome email per account
                            if bulk_send_email:
                                send_welcome_email(email, name, pwd, role, bulk_app_url)
                        except Exception as e:
                            failed.append(f"{email} — {e}")
                        prog.progress((i+1)/len(rows), text=f"Creating accounts… {i+1}/{len(rows)}")
                    prog.empty()
                    st.success(f"✅  {success} accounts created successfully!")
                    if failed:
                        st.warning(f"⚠️  {len(failed)} failed:")
                        for f in failed: st.caption(f"  • {f}")
                    # Generate summary CSV
                    summary = "display_name,email,role,status\n"
                    for r in rows:
                        email = r.get("email","")
                        status = "failed" if any(email in f for f in failed) else "created"
                        summary += f"{r.get('display_name','')},{email},{r.get('role','student')},{status}\n"
                    st.download_button("⬇️  Download result summary", summary.encode(),
                                       f"bulk_create_result_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

        with mem3:
            st.markdown("#### Export student data")
            exp_comp = st.selectbox("Competition filter",["All"]+list(COMPETITIONS.keys()),key="exp_comp")
            c_a,c_b = st.columns(2)
            with c_a:
                st.markdown("**Scores CSV** — 1 row per session")
                if st.button("📥  Generate scores CSV",key="exp_csv",use_container_width=True):
                    try:
                        rows=[]
                        for u in db.collection("users").stream():
                            uid=u.id; prof=u.to_dict(); sref=db.collection("users").document(uid).collection("exam_sessions")
                            if exp_comp!="All": sref=sref.where("competition","==",exp_comp)
                            for s in sref.stream():
                                sd=s.to_dict(); ts=sd.get("timestamp_start"); tbd=sd.get("topic_breakdown",{})
                                rows.append({"name":prof.get("display_name",""),"email":prof.get("email",""),
                                             "competition":sd.get("competition",""),"level":sd.get("level",""),
                                             "date":ts.strftime("%Y-%m-%d") if ts else "","score":sd.get("raw_score",""),
                                             "max":sd.get("max_score",""),"pct":sd.get("pct",""),"duration_sec":sd.get("duration_sec",""),
                                             **{f"{t.lower().replace(' ','_')}_pct":round(tbd.get(t,{}).get("correct",0)/max(tbd.get(t,{}).get("total",1),1)*100) if tbd.get(t) else "" for t in TOPICS}})
                        if rows:
                            buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
                            st.download_button(f"⬇️  Download ({len(rows)} rows)",buf.getvalue().encode(),f"mathcomp_scores_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
                        else: st.info("No data.")
                    except Exception as e: st.error(f"Error: {e}")
            with c_b:
                st.markdown("**Answer log CSV** — 1 row per answer")
                if st.button("📥  Generate answer log",key="exp_ans",use_container_width=True):
                    try:
                        rows=[]
                        for u in db.collection("users").stream():
                            uid=u.id; prof=u.to_dict(); sref=db.collection("users").document(uid).collection("exam_sessions")
                            if exp_comp!="All": sref=sref.where("competition","==",exp_comp)
                            for s in sref.stream():
                                sd=s.to_dict(); ts=sd.get("timestamp_start")
                                for qid,ans in sd.get("answers",{}).items():
                                    rows.append({"name":prof.get("display_name",""),"email":prof.get("email",""),
                                                 "competition":sd.get("competition",""),"level":sd.get("level",""),
                                                 "date":ts.strftime("%Y-%m-%d") if ts else "","question_id":qid,
                                                 "topic":ans.get("topic",""),"chosen":ans.get("chosen",""),
                                                 "correct":ans.get("correct",""),"is_correct":ans.get("is_correct",""),"time_sec":ans.get("time_sec","")})
                        if rows:
                            buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
                            st.download_button(f"⬇️  Download ({len(rows)} rows)",buf.getvalue().encode(),f"mathcomp_answers_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
                        else: st.info("No data.")
                    except Exception as e: st.error(f"Error: {e}")

    # ── Tab 4: Competitions ────────────────────
    with tab4:
        st.subheader("Competition Management")
        ct1,ct2,ct3,ct4,ct5 = st.tabs([
            "➕  Add Competition",
            "✅  Enable / Disable",
            "📝  Edit / Delete",
            "🔗  Add Questions",
            "⚡  Realtime Contest",
        ])

        # ── ct1: Add new competition ──────────────
        with ct1:
            st.markdown("#### Add a new competition to the catalog")
            st.caption("Once added, it will appear in the student exam selection dropdown.")

            with st.form("add_comp_catalog"):
                c1,c2 = st.columns(2)
                cn_name = c1.text_input("Competition name *", placeholder="e.g. Singapore Mathematical Olympiad")
                cn_code = c2.text_input("Short code *", placeholder="e.g. SMO_Junior")
                cn_desc = st.text_input("Description", placeholder="e.g. Junior level · 35 questions · 90 min")

                c3,c4,c5 = st.columns(3)
                cn_spq   = c3.number_input("Seconds per question", 30, 600, 120, step=10)
                cn_score_c = c4.number_input("Score correct",  0.0, 10.0, 1.0, step=0.5)
                cn_score_w = c5.number_input("Score wrong (negative = penalty)", -5.0, 0.0, 0.0, step=0.5)

                st.markdown("**Levels / Divisions** (one per line)")
                cn_levels_raw = st.text_area("Levels", value="Junior\nSenior\nOpen", height=80)

                sub_cn = st.form_submit_button("➕  Add to catalog", type="primary", use_container_width=True)

            if sub_cn:
                if not cn_name or not cn_code:
                    st.error("Name and code are required.")
                else:
                    levels = [l.strip() for l in cn_levels_raw.strip().splitlines() if l.strip()]
                    if not levels: levels = ["General"]
                    try:
                        db.collection("competition_catalog").document(cn_code).set({
                            "name":       cn_name,
                            "code":       cn_code,
                            "description":cn_desc,
                            "levels":     levels,
                            "secs_per_q": int(cn_spq),
                            "scoring":    {"correct":cn_score_c,"wrong":cn_score_w,"blank":0},
                            "created_at": datetime.now(timezone.utc),
                        })
                        load_custom_competitions.clear()  # clear cache
                        st.success(f"✅  **{cn_name}** added to catalog!")
                        st.info(f"Students can now select it from the exam dropdown. "
                                f"Add questions via the **🔗 Add Questions** tab.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            # Show pre-built suggestions
            st.divider()
            st.markdown("#### 💡 Quick-add popular competitions")
            SUGGESTIONS = [
                ("SMO Junior",       "SMO_Junior",    "Singapore Mathematical Olympiad · Junior",         ["Open","Short List"],          180, 1, 0),
                ("SMO Senior",       "SMO_Senior",    "Singapore Mathematical Olympiad · Senior",         ["Open","Short List"],          180, 1, 0),
                ("SMO Open",         "SMO_Open",      "Singapore Mathematical Olympiad · Open",           ["Open","Short List"],          180, 1, 0),
                ("IMO",              "IMO",           "International Mathematical Olympiad",              ["Day 1","Day 2"],              600, 7, 0),
                ("APMO",             "APMO",          "Asian Pacific Mathematics Olympiad",               ["General"],                    480, 7, 0),
                ("SASMO",            "SASMO",         "Singapore & Asian Schools Math Olympiad",          ["Grade 2","Grade 3","Grade 4","Grade 5","Grade 6","Grade 7","Grade 8","Grade 9","Grade 10"], 90, 4, -1),
                ("SEAMO",            "SEAMO",         "South East Asian Mathematical Olympiad",           ["Paper A","Paper B","Paper C","Paper D","Paper E","Paper F"], 90, 1, 0),
                ("Thailand ONET",    "ONET",          "O-NET คณิตศาสตร์",                                 ["Grade 6","Grade 9","Grade 12"], 90, 1, 0),
                ("Thailand PAT 1",   "PAT1",          "PAT 1 คณิตศาสตร์",                                ["PAT 1"],                      120, 1, 0),
                ("Kangaroo Math",    "KANGAROO",      "Math Kangaroo / Känguru der Mathematik",           ["Pre-Ecolier","Ecolier","Benjamin","Cadet","Junior","Student"], 90, 1, 0),
                ("IMAS",             "IMAS",          "International Mathematics Assessment for Schools", ["Grade 2-4","Grade 5-6","Grade 7-8"], 90, 1, 0),
                ("HIMCM",            "HIMCM",         "High School Mathematical Contest in Modeling",     ["General"],                    300, 1, 0),
            ]
            existing_codes = set()
            try:
                existing_codes = {d.id for d in db.collection("competition_catalog").stream()}
            except: pass

            cols = st.columns(3)
            for i, (name,code,desc,levels,spq,sc,sw) in enumerate(SUGGESTIONS):
                with cols[i%3]:
                    already = code in existing_codes
                    btn_label = f"✅ {name}" if already else f"➕ {name}"
                    if st.button(btn_label, key=f"qa_{code}",
                                 use_container_width=True, disabled=already):
                        try:
                            db.collection("competition_catalog").document(code).set({
                                "name":cn_name if False else name,"code":code,"description":desc,
                                "levels":levels,"secs_per_q":spq,
                                "scoring":{"correct":sc,"wrong":sw,"blank":0},
                                "created_at":datetime.now(timezone.utc),
                            })
                            load_custom_competitions.clear()
                            st.success(f"Added {name}!"); st.rerun()
                        except Exception as e: st.error(str(e))

        # ── ct2: Enable / Disable ────────────────
        with ct2:
            st.markdown("#### Enable / Disable competitions")
            st.caption("Disabled competitions are hidden from students but remain in the database.")

            all_comps_full = get_all_competitions(include_disabled=True)
            disabled_set   = load_disabled_competitions()

            # Group: built-in vs custom
            builtin_names = list(COMPETITIONS_BUILTIN.keys())
            custom_names  = [k for k in all_comps_full if k not in builtin_names]

            def comp_toggle_row(name, info):
                is_enabled = name not in disabled_set
                c1, c2, c3 = st.columns([4, 2, 1])
                c1.markdown(f"**{name}**")
                c2.caption(info.get("description",""))
                new_val = c3.toggle(
                    "##tog", value=is_enabled,
                    key=f"tog_{name.replace(' ','_').replace('(','').replace(')','')}"
                )
                if new_val != is_enabled:
                    set_competition_enabled(name, new_val)
                    st.rerun()

            st.markdown("**Built-in competitions**")
            for name in builtin_names:
                comp_toggle_row(name, COMPETITIONS_BUILTIN[name])

            if custom_names:
                st.divider()
                st.markdown("**Custom competitions**")
                for name in custom_names:
                    comp_toggle_row(name, all_comps_full[name])

            st.divider()
            enabled_count  = len(all_comps_full) - len(disabled_set)
            disabled_count = len(disabled_set)
            c1, c2 = st.columns(2)
            c1.metric("Enabled",  enabled_count)
            c2.metric("Disabled", disabled_count)
            if disabled_set:
                st.caption(f"Disabled: {', '.join(sorted(disabled_set))}")

        # ── ct3: Edit / Delete ────────────────────
        with ct3:
            st.markdown("#### Edit or delete competitions in the catalog")
            try:
                cat_docs = list(db.collection("competition_catalog").stream())
                if not cat_docs:
                    st.info("No custom competitions added yet.")
                else:
                    for doc in cat_docs:
                        d = doc.to_dict()
                        with st.expander(f"**{d.get('name','')}** · {d.get('description','')}"):
                            ef1,ef2 = st.columns(2)
                            e_name = ef1.text_input("Name",  value=d.get("name",""),  key=f"en_{doc.id}")
                            e_desc = ef2.text_input("Desc",  value=d.get("description",""), key=f"ed_{doc.id}")
                            e_levels = st.text_area("Levels (one per line)",
                                value="\n".join(d.get("levels",[])), height=80, key=f"el_{doc.id}")
                            ef3,ef4,ef5 = st.columns(3)
                            e_spq = ef3.number_input("Sec/q", 10, 600, int(d.get("secs_per_q",120)), key=f"es_{doc.id}")
                            e_sc  = ef4.number_input("Score correct", 0.0, 10.0,
                                float(d.get("scoring",{}).get("correct",1)), key=f"esc_{doc.id}")
                            e_sw  = ef5.number_input("Score wrong", -5.0, 0.0,
                                float(d.get("scoring",{}).get("wrong",0)), key=f"esw_{doc.id}")
                            sb1,sb2 = st.columns(2)
                            if sb1.button("💾  Save", key=f"ecsave_{doc.id}", type="primary", use_container_width=True):
                                lvls = [l.strip() for l in e_levels.splitlines() if l.strip()] or ["General"]
                                db.collection("competition_catalog").document(doc.id).update({
                                    "name":e_name,"description":e_desc,"levels":lvls,
                                    "secs_per_q":int(e_spq),
                                    "scoring":{"correct":e_sc,"wrong":e_sw,"blank":0},
                                })
                                load_custom_competitions.clear()
                                st.success("Updated!"); st.rerun()
                            if sb2.button("🗑️  Delete", key=f"ecdel_{doc.id}", use_container_width=True):
                                db.collection("competition_catalog").document(doc.id).delete()
                                load_custom_competitions.clear()
                                st.warning(f"Deleted {d.get('name','')}"); st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        # ── ct4: Add questions to competition ─────
        with ct4:
            st.markdown("#### Add questions to a competition")
            all_comps = get_all_competitions(include_disabled=True)

            aq_comp = st.selectbox("Select competition", list(get_all_competitions(include_disabled=True).keys()), key="aq_comp")
            aq_level = st.selectbox("Level", all_comps[aq_comp]["levels"], key="aq_level")
            st.divider()

            aq_tab1, aq_tab2 = st.tabs(["✏️  Add new question", "📥  Select from existing bank"])

            # ── Add new question directly ─────────
            with aq_tab1:
                st.caption("Write a new question and save it directly to this competition.")
                aq_topic = st.selectbox("Topic", TOPICS+["Other"], key="aq_topic")
                aq_diff  = st.selectbox("Difficulty", ["easy","intermediate","advanced"], key="aq_diff")
                aq_year  = st.number_input("Year", 2000, 2030, datetime.now().year, key="aq_year")
                aq_atype = st.selectbox("Answer type", ["mc4","mc5","integer","decimal"], key="aq_atype")

                aq_text = st.text_area("Question text (LaTeX supported)", height=120, key="aq_qtext")
                aq_img  = st.file_uploader("Question image (optional)", type=["png","jpg","jpeg"], key="aq_qimg")
                if aq_text:
                    with st.expander("Preview"): st.markdown(aq_text)

                # AI assess
                if aq_text and st.button("🤖  AI assess difficulty & topic", key="aq_ai_btn"):
                    with st.spinner("Analysing…"):
                        ai_r = ai_assess_question(aq_text, "", "", aq_comp)
                        if ai_r: st.session_state["aq_ai"] = ai_r; st.rerun()
                if "aq_ai" in st.session_state:
                    ar = st.session_state["aq_ai"]
                    st.info(f"🤖 AI suggests — **{ar.get('topic','?')}** · **{ar.get('difficulty','?')}** · {ar.get('topic_reason','')} · {ar.get('difficulty_reason','')}")
                    if st.button("Apply AI suggestion", key="aq_apply_ai"):
                        st.session_state["aq_topic"] = ar.get("topic", aq_topic)
                        st.session_state["aq_diff"]  = ar.get("difficulty", aq_diff)
                        st.session_state.pop("aq_ai",None); st.rerun()

                # Choices
                aq_choices = []; aq_correct = ""
                if aq_atype in ("mc4","mc5"):
                    n = 4 if aq_atype=="mc4" else 5
                    st.markdown("**Answer choices**")
                    ch_cols = st.columns(n)
                    for i in range(n):
                        aq_choices.append(ch_cols[i].text_input(chr(65+i), key=f"aq_ch{i}"))
                    aq_correct = st.selectbox("Correct answer",
                        [chr(65+i) for i in range(n)], key="aq_correct_mc")
                else:
                    aq_correct = st.text_input("Correct answer (number)", key="aq_correct_num")

                st.divider()
                st.markdown("**Solution (optional)**")
                sc1, sc2 = st.columns(2)
                aq_sol     = sc1.text_area("Solution text / LaTeX", height=80, key="aq_sol")
                aq_sol_img = sc2.file_uploader("Solution image", type=["png","jpg","jpeg"], key="aq_sol_img")
                if aq_sol_img:
                    st.image(aq_sol_img, caption="Solution preview", use_container_width=True)

                if st.button("💾  Save question to this competition", type="primary", key="aq_save"):
                    if not aq_text and not aq_img:
                        st.error("Question text or image is required.")
                    else:
                        with st.spinner("Saving…"):
                            ar = st.session_state.get("aq_ai",{})
                            ts = datetime.now().timestamp()
                            q_url   = upload_img(aq_img,     f"questions/{ts}_q.{aq_img.name.split('.')[-1]}")     if aq_img     else ""
                            sol_url = upload_img(aq_sol_img, f"solutions/{ts}_s.{aq_sol_img.name.split('.')[-1]}") if aq_sol_img else ""
                            save_question({
                                "competition":        aq_comp,
                                "level":              aq_level,
                                "topic":              ar.get("topic",    aq_topic) if ar else aq_topic,
                                "difficulty":         ar.get("difficulty",aq_diff)  if ar else aq_diff,
                                "year":               int(aq_year),
                                "answer_type":        aq_atype,
                                "question_text":      aq_text,
                                "question_image_url": q_url,
                                "choices":            aq_choices,
                                "correct_answer":     str(aq_correct),
                                "solution_text":      aq_sol,
                                "solution_image_url": sol_url,
                            })
                            st.session_state.pop("aq_ai",None)
                        st.success(f"✅  Question saved to **{aq_comp} · {aq_level}**!")

            # ── Select from existing bank ─────────
            with aq_tab2:
                st.caption("Copy questions from the existing bank into this competition.")

                src_comp  = st.selectbox("Source competition", list(get_all_competitions(include_disabled=True).keys()), key="src_comp")
                src_topic = st.selectbox("Topic filter", ["All"]+TOPICS+["Other"], key="src_topic")
                src_diff  = st.selectbox("Difficulty filter", ["All","easy","intermediate","advanced"], key="src_diff")

                if st.button("🔍  Browse source questions", key="src_browse"):
                    try:
                        ref = db.collection("questions").where("competition","==",src_comp)
                        if src_topic != "All": ref = ref.where("topic","==",src_topic)
                        if src_diff  != "All": ref = ref.where("difficulty","==",src_diff)
                        docs = list(ref.limit(100).stream())
                        st.session_state["src_docs"] = [(d.id, d.to_dict()) for d in docs]
                    except Exception as e:
                        st.error(f"Error: {e}")

                src_docs = st.session_state.get("src_docs",[])
                if src_docs:
                    st.caption(f"{len(src_docs)} questions found — tick the ones to copy")
                    selected_ids = []
                    for did, d in src_docs:
                        qt = d.get("question_text","(image only)")[:70]
                        label = f"[{d.get('difficulty','')}] [{d.get('topic','')}] {qt}…"
                        if st.checkbox(label, key=f"src_sel_{did}"):
                            selected_ids.append((did, d))

                    if selected_ids:
                        st.markdown(f"**{len(selected_ids)} question(s) selected**")
                        keep_original = st.toggle(
                            "Keep original competition tag (copy as-is)",
                            value=False, key="src_keep_orig",
                            help="Off = re-tag to target competition/level. On = keep original tags.")

                        if st.button(f"📥  Copy {len(selected_ids)} question(s) → {aq_comp} · {aq_level}",
                                     type="primary", key="src_copy"):
                            copied = 0
                            for did, d in selected_ids:
                                new_q = dict(d)
                                new_q.pop("id", None)
                                if not keep_original:
                                    new_q["competition"] = aq_comp
                                    new_q["level"]       = aq_level
                                db.collection("questions").add(new_q)
                                copied += 1
                            st.success(f"✅  {copied} question(s) copied to **{aq_comp} · {aq_level}**!")
                            st.session_state.pop("src_docs",None)
                            st.rerun()

        # ── ct5: Realtime contest ─────────────────
        with ct5:
            st.markdown("#### ⚡ Realtime Contest Control")
            st.caption("Open and close a competition window, then monitor the live leaderboard.")

            # Load competitions from BOTH sources
            all_rt_comps = {}

            # 1. From competition_catalog (admin-created)
            try:
                for doc in db.collection("competition_catalog").stream():
                    d = doc.to_dict()
                    n = d.get("name","")
                    if n: all_rt_comps[n] = {"doc_id":doc.id,"source":"catalog","data":d}
            except: pass

            # 2. From built-in + custom via get_all_competitions
            for n, info in get_all_competitions(include_disabled=True).items():
                if n not in all_rt_comps:
                    all_rt_comps[n] = {"doc_id":None,"source":"builtin","data":info}

            if not all_rt_comps:
                st.warning("No competitions found. Create one in the ➕ Add Competition tab first.")
            else:
                sel_name = st.selectbox(
                    "Select competition to run",
                    list(all_rt_comps.keys()),
                    key="rt_sel"
                )
                sel_info = all_rt_comps[sel_name]

                # Load or create realtime session doc
                rt_doc_ref = db.collection("realtime_sessions").document(
                    sel_name.replace(" ","_").replace("/","_")
                )
                rt_doc = rt_doc_ref.get()
                rt_data = rt_doc.to_dict() if rt_doc.exists else {}
                status  = rt_data.get("status","not started")

                # Status badge
                badge_color = {"open":"#22C55E","closed":"#EF4444","not started":"#8898CC"}.get(status,"#8898CC")
                st.markdown(
                    f"<div style='display:inline-flex;align-items:center;gap:8px;"
                    f"background:#F8F9FF;border:1.5px solid #E8ECF8;border-radius:8px;"
                    f"padding:8px 16px;margin-bottom:16px;'>"
                    f"<span style='width:10px;height:10px;border-radius:50%;"
                    f"background:{badge_color};display:inline-block;'></span>"
                    f"<span style='font-weight:600;color:#1B2B6B;'>Status: {status.upper()}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                if rt_data.get("opened_at"):
                    st.caption(f"Opened: {rt_data['opened_at'].strftime('%d %b %Y %H:%M')}")
                if rt_data.get("closed_at"):
                    st.caption(f"Closed: {rt_data['closed_at'].strftime('%d %b %Y %H:%M')}")

                # Control buttons
                c1,c2,c3 = st.columns(3)
                if c1.button("▶️  Open exam", type="primary", use_container_width=True):
                    rt_doc_ref.set({
                        "competition": sel_name,
                        "status":      "open",
                        "opened_at":   datetime.now(timezone.utc),
                        "closed_at":   None,
                    }, merge=True)
                    st.success(f"✅  **{sel_name}** is now OPEN — students can start!")
                    st.rerun()

                if c2.button("⏹️  Close exam", use_container_width=True):
                    rt_doc_ref.set({
                        "status":    "closed",
                        "closed_at": datetime.now(timezone.utc),
                    }, merge=True)
                    st.warning(f"🔒  **{sel_name}** is now CLOSED.")
                    st.rerun()

                if c3.button("🔄  Reset", use_container_width=True):
                    rt_doc_ref.set({
                        "competition": sel_name,
                        "status":      "not started",
                        "opened_at":   None,
                        "closed_at":   None,
                    })
                    st.info("Reset to draft.")
                    st.rerun()

                st.divider()

                # Share link
                app_url = st.secrets.get("APP_URL","https://share.streamlit.io")
                share_url = f"{app_url}?comp={sel_name.replace(' ','+')}"
                st.markdown("**📎 Share this link with students:**")
                st.code(share_url, language=None)

                st.divider()

                # Live leaderboard
                st.markdown("#### 🏆 Live Leaderboard")
                st.caption("Click Refresh to update. Press R on keyboard to reload the page.")

                if st.button("🔄  Refresh leaderboard", key="rt_refresh", type="primary"):
                    st.session_state["rt_lb_show"] = True

                if st.session_state.get("rt_lb_show"):
                    try:
                        scores = []
                        for u in db.collection("users").stream():
                            uid  = u.id
                            prof = u.to_dict()
                            if prof.get("role") == "admin": continue
                            uname = prof.get("display_name","—")
                            ss = list(
                                db.collection("users").document(uid)
                                .collection("exam_sessions")
                                .where("competition","==",sel_name)
                                .order_by("raw_score",direction=firestore.Query.DESCENDING)
                                .limit(1).stream()
                            )
                            if ss:
                                s = ss[0].to_dict()
                                ts = s.get("timestamp_start")
                                scores.append({
                                    "name":  uname,
                                    "score": s.get("raw_score",0),
                                    "max":   s.get("max_score",0),
                                    "pct":   s.get("pct",0),
                                    "time":  ts.strftime("%H:%M") if ts else "—",
                                    "dur":   f"{s.get('duration_sec',0)//60}m {s.get('duration_sec',0)%60}s",
                                })
                        scores.sort(key=lambda x:x["score"],reverse=True)

                        if not scores:
                            st.info("No submissions yet. Waiting for students…")
                        else:
                            st.markdown(f"**{len(scores)} submission(s)**")
                            # Header
                            h1,h2,h3,h4,h5,h6 = st.columns([1,4,2,2,2,2])
                            for col,lbl in zip([h1,h2,h3,h4,h5,h6],
                                               ["Rank","Name","Score","Accuracy","Time","Duration"]):
                                col.markdown(f"**{lbl}**")
                            st.divider()
                            for rank,s in enumerate(scores,1):
                                medal = "🥇" if rank==1 else("🥈" if rank==2 else("🥉" if rank==3 else f"**#{rank}**"))
                                r1,r2,r3,r4,r5,r6 = st.columns([1,4,2,2,2,2])
                                r1.markdown(medal)
                                r2.markdown(f"**{s['name']}**")
                                r3.markdown(f"{s['score']} / {s['max']}")
                                r4.markdown(f"{s['pct']}%")
                                r5.markdown(s["time"])
                                r6.markdown(s["dur"])

                    except Exception as e:
                        st.error(f"Leaderboard error: {e}")

    footer()


# ══════════════════════════════════════════════
# PDF Report generator (student personal report)
# ══════════════════════════════════════════════
def generate_pdf_report(name:str, sessions:list) -> bytes:
    """Generate a simple HTML→PDF-style report as HTML bytes for download."""
    rows = ""
    for s in sessions:
        ts  = s.get("timestamp_start")
        dt  = ts.strftime("%d %b %Y") if ts else "—"
        tbd = s.get("topic_breakdown",{})
        topic_str = " · ".join(
            f"{t}: {round(v['correct']/v['total']*100)}%"
            for t,v in tbd.items() if v.get("total",0)>0
        )
        color = "#22C55E" if s.get("pct",0)>=70 else ("#EAB308" if s.get("pct",0)>=50 else "#EF4444")
        rows += f"""
        <tr>
          <td>{dt}</td>
          <td><strong>{s.get("competition","")}</strong> · {s.get("level","")}</td>
          <td>{s.get("difficulty","").capitalize()}</td>
          <td style="text-align:center;font-weight:600;">{s.get("raw_score","")} / {s.get("max_score","")}</td>
          <td style="text-align:center;font-weight:700;color:{color};">{s.get("pct","")}%</td>
          <td style="font-size:11px;color:#5060A0;">{topic_str}</td>
        </tr>"""

    total_sessions = len(sessions)
    avg_pct = round(sum(s.get("pct",0) for s in sessions)/total_sessions,1) if sessions else 0
    best    = max(sessions, key=lambda s:s.get("pct",0)) if sessions else {}

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  body{{font-family:'Segoe UI',Arial,sans-serif;color:#1B2B6B;margin:0;padding:0;background:#F8F9FF;}}
  .header{{background:#1B2B6B;color:#fff;padding:32px 48px;}}
  .header h1{{margin:0;font-size:28px;font-weight:300;font-style:italic;}}
  .header p{{margin:6px 0 0;font-size:12px;opacity:.55;letter-spacing:.1em;text-transform:uppercase;}}
  .body{{padding:36px 48px;}}
  .student{{font-size:22px;font-weight:600;margin-bottom:4px;}}
  .meta{{font-size:13px;color:#8898CC;margin-bottom:28px;}}
  .summary{{display:flex;gap:20px;margin-bottom:32px;}}
  .card{{background:#fff;border:1.5px solid #E8ECF8;border-radius:12px;padding:16px 20px;flex:1;}}
  .card-label{{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#8898CC;margin-bottom:4px;}}
  .card-val{{font-size:26px;font-weight:700;color:#1B2B6B;}}
  table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(27,43,107,.06);}}
  th{{background:#1B2B6B;color:#fff;padding:12px 16px;font-size:12px;text-align:left;font-weight:500;letter-spacing:.05em;}}
  td{{padding:11px 16px;font-size:13px;border-bottom:1px solid #F3F5FB;}}
  tr:last-child td{{border-bottom:none;}}
  tr:hover td{{background:#F8F9FF;}}
  .footer{{background:#1B2B6B;color:rgba(255,255,255,.4);padding:16px 48px;font-size:11px;margin-top:0;}}
</style>
</head><body>
<div class="header">
  <h1>MathComp · Student Report</h1>
  <p>Math Mission Thailand · Generated {datetime.now().strftime("%d %b %Y %H:%M")}</p>
</div>
<div class="body">
  <div class="student">{name}</div>
  <div class="meta">Personal Performance Report · All Sessions</div>
  <div class="summary">
    <div class="card"><div class="card-label">Total Sessions</div><div class="card-val">{total_sessions}</div></div>
    <div class="card"><div class="card-label">Average Accuracy</div><div class="card-val">{avg_pct}%</div></div>
    <div class="card"><div class="card-label">Best Score</div><div class="card-val">{best.get("pct","—")}%</div></div>
    <div class="card"><div class="card-label">Best Competition</div><div class="card-val" style="font-size:14px;">{best.get("competition","—")}</div></div>
  </div>
  <table>
    <tr><th>Date</th><th>Competition</th><th>Difficulty</th><th style="text-align:center;">Score</th><th style="text-align:center;">Accuracy</th><th>Topic Breakdown</th></tr>
    {rows if rows else '<tr><td colspan="6" style="text-align:center;padding:24px;color:#8898CC;">No sessions yet</td></tr>'}
  </table>
</div>
<div class="footer">© Math Mission Thailand 2026 · MathComp Platform · Confidential</div>
</body></html>"""
    return html.encode("utf-8")


# ══════════════════════════════════════════════
# Page: My History (student)
# ══════════════════════════════════════════════
def page_history():
    require_auth(); inject_css()
    uid  = st.session_state["uid"]
    name = st.session_state.get("display_name","Student")
    topbar("My History")

    try:
        sessions = [s.to_dict() for s in
                    db.collection("users").document(uid)
                    .collection("exam_sessions")
                    .order_by("timestamp_start",direction=firestore.Query.DESCENDING)
                    .limit(100).stream()]
    except Exception as e:
        st.error(f"Error loading history: {e}"); sessions=[]

    st.markdown(f"""
    <div class="mc-hero">
      <div class="mc-hero-eyebrow">Performance history</div>
      <div class="mc-hero-title">{name}'s <em>results</em></div>
      <div class="mc-metrics">
        <div class="mc-metric"><div class="mc-metric-label">Sessions</div>
          <div class="mc-metric-val">{len(sessions)}</div></div>
        <div class="mc-metric"><div class="mc-metric-label">Avg Accuracy</div>
          <div class="mc-metric-val">{round(sum(s.get("pct",0) for s in sessions)/len(sessions),1) if sessions else 0}%</div></div>
        <div class="mc-metric"><div class="mc-metric-label">Best Score</div>
          <div class="mc-metric-val">{max((s.get("pct",0) for s in sessions),default=0)}%</div></div>
        <div class="mc-metric"><div class="mc-metric-label">Competitions</div>
          <div class="mc-metric-val">{len(set(s.get("competition","") for s in sessions))}</div></div>
      </div>
    </div>
    <div class="mc-body">""", unsafe_allow_html=True)

    # Download buttons
    col_dl1, col_dl2, _ = st.columns([1,1,2])
    with col_dl1:
        if sessions:
            html_bytes = generate_pdf_report(name, sessions)
            st.download_button(
                "📄  Download HTML Report",
                data=html_bytes,
                file_name=f"mathcomp_report_{name.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True,
            )
    with col_dl2:
        if sessions:
            # CSV export — collect all fieldnames first across all sessions
            base_fields = ["date","competition","level","difficulty",
                           "score","max","pct","duration_sec"]
            all_topic_keys = []
            for s in sessions:
                for t in s.get("topic_breakdown",{}).keys():
                    key = t.lower().replace(" ","_") + "_pct"
                    if key not in all_topic_keys:
                        all_topic_keys.append(key)
            all_fields = base_fields + sorted(all_topic_keys)

            rows_csv = []
            for s in sessions:
                ts  = s.get("timestamp_start")
                tbd = s.get("topic_breakdown",{})
                row = {
                    "date":         ts.strftime("%Y-%m-%d") if ts else "",
                    "competition":  s.get("competition",""),
                    "level":        s.get("level",""),
                    "difficulty":   s.get("difficulty",""),
                    "score":        s.get("raw_score",""),
                    "max":          s.get("max_score",""),
                    "pct":          s.get("pct",""),
                    "duration_sec": s.get("duration_sec",""),
                }
                # Fill topic columns — blank if topic not in this session
                for t, v in tbd.items():
                    key = t.lower().replace(" ","_") + "_pct"
                    row[key] = round(v["correct"]/v["total"]*100) if v.get("total",0)>0 else 0
                rows_csv.append(row)

            buf = io.StringIO()
            w   = csv.DictWriter(buf, fieldnames=all_fields, extrasaction="ignore")
            w.writeheader()
            for row in rows_csv:
                # Fill missing topic columns with empty string
                for f in all_fields:
                    row.setdefault(f, "")
                w.writerow(row)

            st.download_button(
                "📊  Download CSV",
                data=buf.getvalue().encode(),
                file_name=f"mathcomp_scores_{name.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    st.divider()

    # Filter
    comps = sorted(set(s.get("competition","") for s in sessions))
    flt   = st.selectbox("Filter by competition", ["All"] + comps, key="hist_filter")
    show  = [s for s in sessions if flt=="All" or s.get("competition","")==flt]

    if not show:
        st.info("No sessions found.")
    else:
        for s in show:
            ts   = s.get("timestamp_start"); dt = ts.strftime("%d %b %Y  %H:%M") if ts else "—"
            pct  = s.get("pct",0)
            tbd  = s.get("topic_breakdown",{})
            dot  = "🟢" if pct>=70 else ("🟡" if pct>=50 else "🔴")
            with st.expander(f"{dot}  {s.get('competition','')} · {s.get('level','')} · {s.get('difficulty','').capitalize()} · **{s.get('raw_score','')} / {s.get('max_score','')}** ({pct}%) · {dt}"):
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("**Topic breakdown**")
                    for topic,v in tbd.items():
                        tp = round(v["correct"]/v["total"]*100) if v["total"]>0 else 0
                        color = "#4A7CF7" if tp>=50 else "#F472B6"
                        st.markdown(
                            f'<div class="mc-topic-row"><span class="mc-topic-name">{topic}</span>'
                            f'<div class="mc-bar-bg"><div class="mc-bar-fill" style="width:{tp}%;background:{color};"></div></div>'
                            f'<span class="mc-bar-pct">{tp}%</span></div>',
                            unsafe_allow_html=True)
                with c2:
                    dur = s.get("duration_sec",0)
                    st.markdown(f"**Duration:** {dur//60}m {dur%60}s")
                    st.markdown(f"**Questions:** {s.get('total_questions','—')}")
                    correct = sum(1 for a in s.get("answers",{}).values() if a.get("is_correct"))
                    wrong   = sum(1 for a in s.get("answers",{}).values() if not a.get("is_correct") and a.get("chosen"))
                    blank   = sum(1 for a in s.get("answers",{}).values() if not a.get("chosen"))
                    st.markdown(f"✅ {correct} correct &nbsp; ❌ {wrong} wrong &nbsp; ⬜ {blank} blank")

    st.markdown("</div>", unsafe_allow_html=True)
    footer()


# ══════════════════════════════════════════════
# Page: Leaderboard (student)
# ══════════════════════════════════════════════
def page_leaderboard():
    require_auth(); inject_css()
    topbar("Leaderboard")

    st.markdown("""
    <div class="mc-hero">
      <div class="mc-hero-eyebrow">Global ranking</div>
      <div class="mc-hero-title">Student <em>Leaderboard</em></div>
    </div>
    <div class="mc-body">""", unsafe_allow_html=True)

    comp_options = ["All"] + list(get_all_competitions().keys())
    c1,c2 = st.columns(2)
    lb_comp   = c1.selectbox("Competition", comp_options, key="lb_comp")
    lb_metric = c2.selectbox("Rank by", ["Best accuracy (%)","Best raw score","Most sessions"], key="lb_metric")

    if st.button("🔄  Load leaderboard", type="primary"):
        st.session_state["lb_loaded"] = True

    if st.session_state.get("lb_loaded"):
        with st.spinner("Loading…"):
            try:
                scores = []
                for u in db.collection("users").stream():
                    uid  = u.id; prof = u.to_dict()
                    if prof.get("role") == "admin": continue
                    name = prof.get("display_name","—")
                    sref = db.collection("users").document(uid).collection("exam_sessions")
                    if lb_comp != "All":
                        sref = sref.where("competition","==",lb_comp)
                    sess = [s.to_dict() for s in sref.stream()]
                    if not sess: continue
                    best_pct   = max(s.get("pct",0) for s in sess)
                    best_score = max(s.get("raw_score",0) for s in sess)
                    n_sess     = len(sess)
                    avg_pct    = round(sum(s.get("pct",0) for s in sess)/n_sess,1)
                    scores.append({"name":name,"best_pct":best_pct,"best_score":best_score,
                                   "n_sess":n_sess,"avg_pct":avg_pct,"uid":uid})

                # Sort
                if lb_metric == "Best accuracy (%)":
                    scores.sort(key=lambda x:x["best_pct"], reverse=True)
                elif lb_metric == "Best raw score":
                    scores.sort(key=lambda x:x["best_score"], reverse=True)
                else:
                    scores.sort(key=lambda x:x["n_sess"], reverse=True)

                if not scores:
                    st.info("No data found.")
                else:
                    my_uid = st.session_state.get("uid","")
                    st.markdown(f"**{len(scores)} students ranked**")
                    st.divider()
                    for rank, s in enumerate(scores, 1):
                        medal = "🥇" if rank==1 else ("🥈" if rank==2 else ("🥉" if rank==3 else f"**#{rank}**"))
                        is_me = s["uid"] == my_uid
                        bg    = "background:#EEF3FF;border-radius:8px;padding:4px 8px;" if is_me else ""
                        c1,c2,c3,c4,c5 = st.columns([1,4,2,2,2])
                        c1.markdown(medal)
                        c2.markdown(f'<span style="{bg}">{"**" if is_me else ""}{s["name"]}{"** ← You" if is_me else ""}</span>', unsafe_allow_html=True)
                        c3.markdown(f"Best: **{s['best_pct']}%**")
                        c4.markdown(f"Avg: {s['avg_pct']}%")
                        c5.markdown(f"{s['n_sess']} session{'s' if s['n_sess']!=1 else ''}")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    footer()


# ══════════════════════════════════════════════
# Page: Admin Analytics Dashboard
# ══════════════════════════════════════════════
def page_admin_analytics():
    require_auth(); require_admin(); inject_css()
    topbar("Analytics Dashboard")

    st.markdown("""
    <div class="mc-hero">
      <div class="mc-hero-eyebrow">Admin overview</div>
      <div class="mc-hero-title">Analytics <em>Dashboard</em></div>
    </div>
    <div class="mc-body">""", unsafe_allow_html=True)

    if st.button("🔄  Load analytics", type="primary", key="load_analytics"):
        st.session_state["analytics_loaded"] = True

    if not st.session_state.get("analytics_loaded"):
        st.info("Click 'Load analytics' to fetch data from Firestore.")
        st.markdown("</div>", unsafe_allow_html=True)
        footer(); return

    with st.spinner("Loading all student data…"):
        try:
            all_users    = [{"uid":d.id,**d.to_dict()} for d in db.collection("users").stream()]
            students     = [u for u in all_users if u.get("role")!="admin"]
            all_sessions = []
            for u in students:
                for s in db.collection("users").document(u["uid"]).collection("exam_sessions").stream():
                    sd = s.to_dict()
                    sd["student_name"]  = u.get("display_name","—")
                    sd["student_email"] = u.get("email","—")
                    all_sessions.append(sd)
        except Exception as e:
            st.error(f"Error: {e}"); st.markdown("</div>",unsafe_allow_html=True); footer(); return

    # ── Summary metrics ────────────────────────
    n_students  = len(students)
    n_sessions  = len(all_sessions)
    avg_pct     = round(sum(s.get("pct",0) for s in all_sessions)/n_sessions,1) if all_sessions else 0
    completion  = round(sum(1 for s in all_sessions if s.get("pct",0)>0)/n_sessions*100) if all_sessions else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Students",   n_students)
    c2.metric("Total Sessions",   n_sessions)
    c3.metric("Avg Accuracy",     f"{avg_pct}%")
    c4.metric("Completion Rate",  f"{completion}%")
    st.divider()

    # ── Topic weakness heatmap ─────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### 📊 Class average by topic")
        topic_totals = {t:{"correct":0,"total":0} for t in TOPICS}
        for s in all_sessions:
            for t,v in s.get("topic_breakdown",{}).items():
                if t in topic_totals:
                    topic_totals[t]["correct"] += v.get("correct",0)
                    topic_totals[t]["total"]   += v.get("total",0)
        fig_bar = go.Figure()
        labels, vals, colors = [],[],[]
        for t,v in topic_totals.items():
            pct = round(v["correct"]/v["total"]*100) if v["total"]>0 else 0
            labels.append(t); vals.append(pct)
            colors.append("#4A7CF7" if pct>=60 else ("#F5A623" if pct>=40 else "#F472B6"))
        fig_bar.add_trace(go.Bar(x=labels,y=vals,marker_color=colors,text=[f"{v}%" for v in vals],textposition="outside"))
        fig_bar.update_layout(yaxis=dict(range=[0,110],title="Accuracy %"),
                              xaxis_title="Topic",showlegend=False,
                              paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(248,249,255,1)",
                              height=320,margin=dict(t=20,b=20))
        st.plotly_chart(fig_bar,use_container_width=True)

    with col_r:
        st.markdown("#### 📈 Sessions over time")
        from collections import Counter
        date_counts = Counter()
        for s in all_sessions:
            ts = s.get("timestamp_start")
            if ts: date_counts[ts.strftime("%Y-%m-%d")] += 1
        if date_counts:
            dates = sorted(date_counts.keys())
            counts= [date_counts[d] for d in dates]
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=dates,y=counts,mode="lines+markers",
                line=dict(color="#4A7CF7",width=2),marker=dict(size=6,color="#4A7CF7"),fill="tozeroy",
                fillcolor="rgba(74,124,247,0.08)"))
            fig_line.update_layout(xaxis_title="Date",yaxis_title="Sessions",
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(248,249,255,1)",
                height=320,margin=dict(t=20,b=20))
            st.plotly_chart(fig_line,use_container_width=True)
        else:
            st.info("No session timeline data yet.")

    st.divider()

    # ── At-risk students ───────────────────────
    st.markdown("#### ⚠️ Students needing attention (accuracy < 50%)")
    at_risk = {}
    for s in all_sessions:
        nm = s.get("student_name","—")
        if nm not in at_risk: at_risk[nm] = []
        at_risk[nm].append(s.get("pct",0))

    at_risk_list = [(nm, round(sum(v)/len(v),1), len(v))
                    for nm,v in at_risk.items() if sum(v)/len(v)<50]
    at_risk_list.sort(key=lambda x:x[1])

    if at_risk_list:
        for nm,avg,n in at_risk_list:
            c1,c2,c3 = st.columns([4,2,2])
            c1.markdown(f"**{nm}**")
            c2.markdown(f"Avg accuracy: 🔴 **{avg}%**")
            c3.markdown(f"{n} session{'s' if n!=1 else ''}")
    else:
        st.success("All students are performing at 50%+ — great job! 🎉")

    st.divider()

    # ── Competition popularity ─────────────────
    st.markdown("#### 🏆 Most popular competitions")
    from collections import Counter as _Counter
    comp_counts = _Counter(s.get("competition","?") for s in all_sessions)
    for comp,count in comp_counts.most_common():
        avg = round(sum(s.get("pct",0) for s in all_sessions if s.get("competition","")==comp)
                    / count, 1)
        c1,c2,c3 = st.columns([4,2,2])
        c1.markdown(f"**{comp}**")
        c2.markdown(f"{count} sessions")
        c3.markdown(f"Avg accuracy: {avg}%")

    st.markdown("</div>", unsafe_allow_html=True)
    footer()


# ══════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════
def render_sidebar():
    if "uid" not in st.session_state: return
    with st.sidebar:
        st.markdown(f"**{st.session_state.get('display_name','')}**")
        st.caption(st.session_state.get("role","student").capitalize())
        st.divider()
        if st.button("🏠  Dashboard",       use_container_width=True): st.session_state["page"]="dashboard";   st.rerun()
        if st.button("📋  My History",       use_container_width=True): st.session_state["page"]="history";     st.rerun()
        if st.button("🏆  Leaderboard",      use_container_width=True): st.session_state["page"]="leaderboard"; st.rerun()
        if st.session_state.get("role")=="admin":
            st.divider()
            if st.button("⚙️  Admin Panel",      use_container_width=True): st.session_state["page"]="admin";            st.rerun()
            if st.button("📊  Analytics",        use_container_width=True): st.session_state["page"]="admin_analytics";  st.rerun()
        st.divider()
        if st.button("Log out", use_container_width=True): st.session_state.clear(); st.rerun()
        st.markdown("---")
        st.markdown("<div style='font-size:10px;color:rgba(255,255,255,.3);font-family:monospace;line-height:1.7;'>"
                    "© Math Mission Thailand 2026<br>MathComp Platform</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# Router
# ══════════════════════════════════════════════
def main():
    if "page" not in st.session_state: st.session_state["page"]="login"

    # Handle direct competition link: ?comp=AMC10&level=AMC+10A
    params = st.query_params
    if "comp" in params and "uid" not in st.session_state:
        st.session_state["pending_comp"]  = params.get("comp","")
        st.session_state["pending_level"] = params.get("level","")

    render_sidebar()
    page = st.session_state["page"]

    # After login, redirect to competition if pending
    if "uid" in st.session_state and st.session_state.get("pending_comp"):
        comp  = st.session_state.pop("pending_comp","")
        level = st.session_state.pop("pending_level","")
        if comp in COMPETITIONS:
            st.session_state.update({
                "page":"dashboard",
                "_prefill_comp":comp,
                "_prefill_level":level,
            })
            st.rerun()

    if   page=="login":            page_login()
    elif page=="dashboard":        page_dashboard()
    elif page=="exam":             page_exam()
    elif page=="result":           page_result()
    elif page=="admin":            page_admin()
    elif page=="history":          page_history()
    elif page=="leaderboard":      page_leaderboard()
    elif page=="admin_analytics":  page_admin_analytics()
    else:
        st.error(f"Unknown page: {page}")
        st.session_state["page"]="login"; st.rerun()

if __name__=="__main__":
    main()
