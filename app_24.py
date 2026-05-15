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

COMPETITIONS = {
    "AMC 8":  {"levels":["AMC 8"],              "secs_per_q":90,  "scoring":{"correct":1,"wrong":0,"blank":0},     "description":"Grade 6–8 · 25 questions · 40 min"},
    "AMC 10": {"levels":["AMC 10A","AMC 10B"],   "secs_per_q":150, "scoring":{"correct":6,"wrong":-1.5,"blank":0},  "description":"Grade 9–10 · 30 questions · 75 min"},
    "AMC 12": {"levels":["AMC 12A","AMC 12B"],   "secs_per_q":150, "scoring":{"correct":6,"wrong":-1.5,"blank":0},  "description":"Grade 11–12 · 30 questions · 75 min"},
    "AMC (Australian)": {"levels":["Middle Primary","Upper Primary","Junior","Intermediate","Senior"], "secs_per_q":120,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"Multiple divisions · 30 questions"},
    "Sansu Olympic":    {"levels":["Kidbee","Junior","Senior","Hironaka"],     "secs_per_q":180,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"算数オリンピック"},
    "Math Association Thailand": {"levels":["Primary Upper","Junior Secondary","Senior Secondary"],"secs_per_q":120,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"สมาคมคณิตศาสตร์แห่งประเทศไทย"},
    "POSN Mathematics": {"levels":["Round 1"],"secs_per_q":180,"scoring":{"correct":1,"wrong":0,"blank":0},"description":"สอวน. คณิตศาสตร์ รอบแรก"},
}
DIFFICULTY_OPTIONS = ["Easy","Intermediate","Advanced","Mixed"]

DEFAULT_SETTINGS = {
    "load_from_firebase":True,"load_student_list":True,"require_competitor_id":True,
    "show_answer_after_submit":False,"allow_bilingual":False,
    "anti_copy_text":False,"noise_canvas":False,"block_ctrl_c":False,
    "block_text_selection":False,"block_paste_answer":True,"block_drag":True,
    "block_right_click":True,"tab_switch_warning":True,"block_printscreen":True,
    "clipboard_api_override":False,"devtools_detection":False,"screen_capture_block":False,
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
    rules = COMPETITIONS.get(competition,{}).get("scoring",{"correct":1,"wrong":0,"blank":0})
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
                "model": "claude-sonnet-4-20250514",
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
        if st.button("Open Admin Panel →", type="primary", key="admin_shortcut"):
            st.session_state["page"] = "admin"; st.rerun()
        st.divider()

    st.markdown('<span class="mc-section-lbl">Start a new exam</span>', unsafe_allow_html=True)
    st.markdown('<div class="mc-card">', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        competition = st.selectbox("Competition", list(COMPETITIONS.keys()))
        comp_info   = COMPETITIONS[competition]
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
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
      <span style="font-family:'DM Mono',monospace;font-size:11px;color:#8898CC;">Q{idx+1} / {len(qs)}</span>
      <span style="font-size:11px;font-family:'DM Mono',monospace;padding:3px 10px;border-radius:20px;
                   background:#EEF3FF;border:1px solid #C8D8FF;color:#4A7CF7;">{q.get('topic','')}</span>
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
        competition = st.selectbox("Select competition to configure", list(COMPETITIONS.keys()), key="adm_comp")
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

        def meta_fields(p=""):
            c1,c2,c3,c4 = st.columns(4)
            comp  = c1.selectbox("Competition",list(COMPETITIONS.keys()),key=f"{p}comp")
            level = c2.selectbox("Level",COMPETITIONS[comp]["levels"],key=f"{p}level")
            topic = c3.selectbox("Topic",TOPICS+["Other"],key=f"{p}topic")
            diff  = c4.selectbox("Difficulty",["easy","intermediate","advanced"],key=f"{p}diff")
            c5,c6 = st.columns(2)
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
            comp,level,topic,diff,year,atype = meta_fields("t_")
            q_text = st.text_area("Question text (LaTeX supported)", height=120, key="t_qtext")
            q_img  = st.file_uploader("Question figure (optional)", type=["png","jpg","jpeg"], key="t_qimg")
            if q_text:
                with st.expander("Preview"): st.markdown(q_text)
            choices,correct = ans_fields(atype,"t_")
            sol_text,sol_img = sol_fields("t_")
            if st.button("💾  Save question", type="primary", key="t_save"):
                if not q_text: st.error("Question text is required.")
                else:
                    with st.spinner("Saving…"):
                        q_url = upload_img(q_img,f"questions/{datetime.now().timestamp()}_q.{q_img.name.split('.')[-1]}") if q_img else ""
                        s_url = upload_img(sol_img,f"solutions/{datetime.now().timestamp()}_s.{sol_img.name.split('.')[-1]}") if sol_img else ""
                        save_question({"competition":comp,"level":level,"topic":topic,"difficulty":diff,"year":year,
                                       "answer_type":atype,"question_text":q_text,"question_image_url":q_url,
                                       "choices":choices,"correct_answer":correct,"solution_text":sol_text,"solution_image_url":s_url})
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

        # Method 3 — AI-OCR
        elif method == "🤖  AI-OCR from image":
            st.markdown("#### AI reads image → LaTeX")
            comp,level,topic,diff,year,atype = meta_fields("ai_")
            q_img = st.file_uploader("Question image", type=["png","jpg","jpeg"], key="ai_qimg")
            if q_img: st.image(q_img, caption="Uploaded", use_container_width=True)
            if q_img and st.button("🤖  Run AI-OCR", key="ai_ocr"):
                with st.spinner("Claude is reading the image…"):
                    try:
                        img_b64 = base64.b64encode(q_img.read()).decode()
                        ext  = q_img.name.split(".")[-1].lower()
                        mime = "image/jpeg" if ext in ("jpg","jpeg") else f"image/{ext}"
                        resp = requests.post("https://api.anthropic.com/v1/messages",
                            headers={"Content-Type":"application/json","x-api-key":st.secrets.get("ANTHROPIC_API_KEY",""),"anthropic-version":"2023-06-01"},
                            json={"model":"claude-sonnet-4-20250514","max_tokens":1000,
                                  "messages":[{"role":"user","content":[
                                      {"type":"image","source":{"type":"base64","media_type":mime,"data":img_b64}},
                                      {"type":"text","text":"Extract the math question from this image. Rewrite it using LaTeX ($...$ for inline, $$...$$ for display). Output ONLY the question text."}
                                  ]}]},timeout=30)
                        if resp.ok: st.session_state["ai_ocr_result"]=resp.json()["content"][0]["text"]
                        else: st.error(f"AI OCR failed: {resp.status_code}")
                    except Exception as e: st.error(f"Error: {e}")

            q_text = st.text_area("Extracted text (edit if needed)", value=st.session_state.get("ai_ocr_result",""), height=140, key="ai_qtext")
            if q_text:
                with st.expander("Preview"): st.markdown(q_text)
            choices,correct = ans_fields(atype,"ai_")
            sol_text,sol_img = sol_fields("ai_")
            if st.button("💾  Save question", type="primary", key="ai_save"):
                if not q_text: st.error("Question text is required.")
                else:
                    with st.spinner("Saving…"):
                        if q_img: q_img.seek(0)
                        q_url = upload_img(q_img,f"questions/{datetime.now().timestamp()}_q.{q_img.name.split('.')[-1]}") if q_img else ""
                        s_url = upload_img(sol_img,f"solutions/{datetime.now().timestamp()}_s.{sol_img.name.split('.')[-1]}") if sol_img else ""
                        save_question({"competition":comp,"level":level,"topic":topic,"difficulty":diff,"year":year,
                                       "answer_type":atype,"question_text":q_text,"question_image_url":q_url,
                                       "choices":choices,"correct_answer":correct,"solution_text":sol_text,"solution_image_url":s_url})
                        st.session_state.pop("ai_ocr_result",None)
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

            if pdf_file and st.button("🤖  Extract questions", key="pdf_extract"):
                with st.spinner("Claude is reading the PDF…"):
                    try:
                        pdf_b64 = base64.b64encode(pdf_file.read()).decode()
                        resp = requests.post("https://api.anthropic.com/v1/messages",
                            headers={"Content-Type":"application/json","x-api-key":st.secrets.get("ANTHROPIC_API_KEY",""),"anthropic-version":"2023-06-01"},
                            json={"model":"claude-sonnet-4-20250514","max_tokens":4000,
                                  "messages":[{"role":"user","content":[
                                      {"type":"document","source":{"type":"base64","media_type":"application/pdf","data":pdf_b64}},
                                      {"type":"text","text":"Extract ALL math questions from this PDF. Return a JSON array with objects: question_text (LaTeX), topic (Algebra/Number Theory/Geometry/Combinatorics/Word Problem/Other), choices (array or []), correct_answer. Output ONLY valid JSON array."}
                                  ]}]},timeout=60)
                        if resp.ok:
                            raw = resp.json()["content"][0]["text"].strip().replace("```json","").replace("```","").strip()
                            st.session_state["pdf_questions"] = json.loads(raw)
                            st.success(f"Extracted **{len(st.session_state['pdf_questions'])}** questions!")
                        else: st.error(f"Failed: {resp.status_code}")
                    except Exception as e: st.error(f"Error: {e}")

            if "pdf_questions" in st.session_state:
                pdf_qs = st.session_state["pdf_questions"]
                for i,q in enumerate(pdf_qs):
                    with st.expander(f"Q{i+1} — {q.get('topic','?')} · {q.get('question_text','')[:60]}…"):
                        pdf_qs[i]["question_text"] = st.text_area("Question",value=q.get("question_text",""),height=80,key=f"pdf_qt_{i}")
                        pdf_qs[i]["topic"] = st.selectbox("Topic",TOPICS+["Other"],
                            index=(TOPICS+["Other"]).index(q.get("topic","Other")) if q.get("topic","Other") in TOPICS+["Other"] else 0,
                            key=f"pdf_tp_{i}")
                        if atype in ("mc4","mc5"):
                            n=4 if atype=="mc4" else 5; existing=q.get("choices",[""]*n); cols=st.columns(n); new_ch=[]
                            for j in range(n): new_ch.append(cols[j].text_input(chr(65+j),value=existing[j] if j<len(existing) else "",key=f"pdf_ch_{i}_{j}"))
                            pdf_qs[i]["choices"]=new_ch
                        pdf_qs[i]["correct_answer"]=st.text_input("Correct answer",value=q.get("correct_answer",""),key=f"pdf_ca_{i}")
                st.session_state["pdf_questions"]=pdf_qs
                if st.button("💾  Save all to Firestore", type="primary", key="pdf_save"):
                    with st.spinner(f"Saving {len(pdf_qs)} questions…"):
                        for q in pdf_qs:
                            save_question({"competition":comp,"level":level,"topic":q.get("topic","Other"),
                                           "difficulty":diff,"year":int(year),"answer_type":atype,
                                           "question_text":q.get("question_text",""),"question_image_url":"",
                                           "choices":q.get("choices",[]),"correct_answer":q.get("correct_answer",""),
                                           "solution_text":"","solution_image_url":""})
                    st.session_state.pop("pdf_questions",None)
                    st.success(f"✅  {len(pdf_qs)} questions saved!")

        # Browser
        st.divider()
        st.markdown("#### 📚  Question Bank Browser")
        qb_comp  = st.selectbox("Filter competition",["All"]+list(COMPETITIONS.keys()),key="qb_comp")
        qb_topic = st.selectbox("Filter topic",["All"]+TOPICS+["Other"],key="qb_topic")
        if st.button("🔍  Browse", key="qb_browse"):
            try:
                ref = db.collection("questions")
                if qb_comp!="All":  ref=ref.where("competition","==",qb_comp)
                if qb_topic!="All": ref=ref.where("topic","==",qb_topic)
                docs = list(ref.limit(50).stream())
                if docs:
                    st.caption(f"{len(docs)} questions found (max 50)")
                    for doc in docs:
                        d=doc.to_dict(); qt=d.get("question_text","(image only)")[:80]
                        with st.expander(f"[{d.get('competition','')}] [{d.get('difficulty','')}] {d.get('topic','')} — {qt}…"):
                            if d.get("question_image_url"): st.image(d["question_image_url"],use_container_width=True)
                            if d.get("question_text"):      st.markdown(d["question_text"])
                            st.caption(f"Answer type: {d.get('answer_type','')} · Correct: {d.get('correct_answer','')} · Year: {d.get('year','')}")
                            if st.button("🗑️  Delete",key=f"del_{doc.id}"):
                                db.collection("questions").document(doc.id).delete(); st.rerun()
                else: st.info("No questions found.")
            except Exception as e: st.error(f"Error: {e}")

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
            if sub_add:
                if not nm or not ne or not np: st.error("All fields required.")
                else:
                    try:
                        from firebase_admin import auth as fb_auth
                        user = fb_auth.create_user(email=ne,password=np,display_name=nm)
                        db.collection("users").document(user.uid).set({"display_name":nm,"email":ne,"role":nr,"created_at":datetime.now(timezone.utc)})
                        st.success(f"✅  Account created for **{nm}** as **{nr}**")
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
        ct1,ct2 = st.tabs(["🏆  Create","⚡  Realtime"])

        with ct1:
            st.markdown("#### Create custom competition")
            with st.form("create_comp"):
                c1,c2=st.columns(2); cname=c1.text_input("Name"); ccode=c2.text_input("Code")
                c3,c4=st.columns(2); cdate=c3.date_input("Date"); cdur=c4.number_input("Duration (min)",10,300,60)
                c5,c6=st.columns(2); cq=c5.number_input("Questions",5,50,20); cpass=c6.text_input("Access code (optional)")
                ccomps=st.multiselect("Pull from competitions",list(COMPETITIONS.keys()))
                cdiff=st.selectbox("Difficulty",["Easy","Intermediate","Advanced","Mixed"])
                sub_c=st.form_submit_button("Create",type="primary",use_container_width=True)
            if sub_c:
                if not cname or not ccode: st.error("Name and code required.")
                else:
                    try:
                        db.collection("custom_competitions").document(ccode).set({"name":cname,"code":ccode,"date":str(cdate),"duration_min":int(cdur),"num_questions":int(cq),"access_code":cpass,"source_competitions":ccomps,"difficulty":cdiff,"created_at":datetime.now(timezone.utc),"status":"draft"})
                        st.success(f"✅  **{cname}** created! Code: `{ccode}`")
                        st.info(f"Share link: `?competition={ccode}`")
                    except Exception as e: st.error(f"Error: {e}")

        with ct2:
            st.markdown("#### Realtime contest control")
            try:
                contests = list(db.collection("custom_competitions").stream())
                if contests:
                    cmap = {d.id: d.to_dict().get("name",d.id) for d in contests}
                    sel  = st.selectbox("Select competition",list(cmap.keys()),format_func=lambda x:cmap[x],key="rt_sel")
                    doc  = db.collection("custom_competitions").document(sel).get()
                    cd   = doc.to_dict() if doc.exists else {}
                    st.markdown(f"**Status:** `{cd.get('status','draft')}`")
                    c1,c2,c3 = st.columns(3)
                    if c1.button("▶️  Open exam",type="primary",use_container_width=True):
                        db.collection("custom_competitions").document(sel).update({"status":"open","opened_at":datetime.now(timezone.utc)}); st.success("Exam OPEN"); st.rerun()
                    if c2.button("⏹️  Close exam",use_container_width=True):
                        db.collection("custom_competitions").document(sel).update({"status":"closed","closed_at":datetime.now(timezone.utc)}); st.warning("Exam CLOSED"); st.rerun()
                    if c3.button("📊  Leaderboard",use_container_width=True):
                        st.session_state["rt_lb"]=sel; st.rerun()
                    if st.session_state.get("rt_lb")==sel:
                        st.divider(); st.markdown("#### 🏆  Live Leaderboard")
                        try:
                            scores=[]
                            for u in db.collection("users").stream():
                                uid=u.id; name=u.to_dict().get("display_name","—")
                                ss=list(db.collection("users").document(uid).collection("exam_sessions").where("competition","==",sel).order_by("raw_score",direction=firestore.Query.DESCENDING).limit(1).stream())
                                if ss: s=ss[0].to_dict(); scores.append({"name":name,"score":s.get("raw_score",0),"max":s.get("max_score",0),"pct":s.get("pct",0)})
                            scores.sort(key=lambda x:x["score"],reverse=True)
                            for rank,s in enumerate(scores,1):
                                medal="🥇" if rank==1 else("🥈" if rank==2 else("🥉" if rank==3 else f"#{rank}"))
                                c1,c2,c3=st.columns([1,4,2]); c1.markdown(medal); c2.markdown(f"**{s['name']}**"); c3.markdown(f"{s['score']} / {s['max']}  ({s['pct']}%)")
                        except Exception as e: st.error(f"Leaderboard error: {e}")
                else: st.info("No competitions yet. Create one first.")
            except Exception as e: st.error(f"Error: {e}")

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
        if st.button("🏠  Dashboard",  use_container_width=True): st.session_state["page"]="dashboard"; st.rerun()
        if st.session_state.get("role")=="admin":
            if st.button("⚙️  Admin Panel", use_container_width=True): st.session_state["page"]="admin"; st.rerun()
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
    render_sidebar()
    page = st.session_state["page"]
    if   page=="login":     page_login()
    elif page=="dashboard": page_dashboard()
    elif page=="exam":      page_exam()
    elif page=="result":    page_result()
    elif page=="admin":     page_admin()
    else:
        st.error(f"Unknown page: {page}")
        st.session_state["page"]="login"; st.rerun()

if __name__=="__main__":
    main()
