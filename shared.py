"""
MathComp — shared.py
Shared imports, Firebase, CSS, constants, helpers
© Math Mission Thailand 2026
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

_custom_comp_cache = {}
_custom_comp_ts = 0
_disabled_comp_cache = set()
_disabled_comp_ts = 0

def _invalidate_custom_cache():
    global _custom_comp_cache, _custom_comp_ts
    _custom_comp_cache = {}
    _custom_comp_ts = 0

def _invalidate_disabled_cache():
    global _disabled_comp_cache, _disabled_comp_ts
    _disabled_comp_cache = set()
    _disabled_comp_ts = 0

def load_custom_competitions() -> dict:
    """Load admin-created competitions from Firestore. Simple TTL cache."""
    global _custom_comp_cache, _custom_comp_ts
    import time as _t
    if _custom_comp_cache and (_t.time() - _custom_comp_ts) < 60:
        return _custom_comp_cache
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
        _custom_comp_cache = result
        _custom_comp_ts = _t.time()
        return result
    except:
        return _custom_comp_cache or {}


def load_disabled_competitions() -> set:
    """Return set of disabled competition names. Simple TTL cache."""
    global _disabled_comp_cache, _disabled_comp_ts
    import time as _t
    if _disabled_comp_ts and (_t.time() - _disabled_comp_ts) < 30:
        return _disabled_comp_cache
    try:
        doc = db.collection("platform_settings").document("disabled_competitions").get()
        result = set(doc.to_dict().get("disabled",[])) if doc.exists else set()
        _disabled_comp_cache = result
        _disabled_comp_ts = _t.time()
        return result
    except:
        return _disabled_comp_cache

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
    global _disabled_comp_cache, _disabled_comp_ts; _disabled_comp_cache = set(); _disabled_comp_ts = 0

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
        # Preserve comp param so student returns to competition after login
        comp = st.query_params.get("comp","")
        if comp:
            st.session_state["pending_comp"] = comp
        st.session_state["page"] = "login"
        st.rerun()

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
