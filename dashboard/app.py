"""
wildnode_ai/dashboard/app.py
==============================
WildNode AI – Premium White & Green Nature Theme Dashboard

HOW TO RUN:
  streamlit run dashboard/app.py

FEATURES:
  - Real-time Webcam / IP Webcam Stream with non-blocking YOLO-World detection
  - Multi-channel Alert Integration (Console, Twilio SMS, Twilio WhatsApp)
  - Interactive Offline Media Upload for direct image testing
  - Chronological Alert Log Hub
  - 4 tabs: Live Camera Stream | Upload Media | Alert Logs | About
  - Premium White & Green Nature Theme, Animated Background, and Frosted Cards
  - Floating RangerBot Chatbot Widget (Google Gemini Core, Memory, Voice, Alerts)
"""

import os
import sys
import json
import random
import time
import threading
from datetime import datetime
import pytz

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from PIL import Image

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from alert_system.alerter import dispatch_alert, get_recent_alerts, ALERT_LOG_PATH
from vision_detection.wildlife_detector import (
    detect_agricultural_pests,
    draw_detections_on_frame,
    ANIMAL_METADATA,
    AGRICULTURAL_PEST_CLASSES,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WildNode AI – Human-Wildlife Conflict Mitigation",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

IST = pytz.timezone("Asia/Kolkata")

# ─────────────────────────────────────────────────────────────────────────────
#  CUSTOM CSS  –  Premium White & Green Nature Theme
# ─────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] { font-family: 'Inter', 'Poppins', 'Outfit', sans-serif !important; }

    /* ── Animated background gradient ── */
    @keyframes bg-drift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background: linear-gradient(-45deg, #f0fdf4, #dcfce7, #f7fee7, #ecfdf5, #d1fae5);
        background-size: 400% 400%;
        animation: bg-drift 18s ease infinite;
        min-height: 100vh;
    }

    /* Subtle leaf-pattern overlay via pseudo -- done with ::before on body */
    body::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            radial-gradient(circle at 15% 30%, rgba(34,197,94,0.07) 0%, transparent 55%),
            radial-gradient(circle at 80% 70%, rgba(16,185,129,0.06) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #052e16 0%, #14532d 60%, #166534 100%) !important;
        backdrop-filter: blur(25px);
        border-right: 1px solid rgba(34,197,94,0.18);
    }
    [data-testid="stSidebar"] * {
        color: #dcfce7 !important;
    }
    [data-testid="stSidebar"] h1 {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 800 !important;
        color: #f7fee7 !important;
    }

    /* ── Glass Cards ── */
    .glass-card {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(34, 197, 94, 0.15);
        border-radius: 18px;
        padding: 20px 24px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(5, 46, 22, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.6);
        margin-bottom: 16px;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border 0.25s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(5, 46, 22, 0.09), 0 0 20px rgba(34, 197, 94, 0.12);
        border-color: rgba(34, 197, 94, 0.35);
    }

    /* ── Risk Badges ── */
    .badge-critical { background: linear-gradient(135deg,#ef4444,#b91c1c); color:#fff; }
    .badge-high     { background: linear-gradient(135deg,#f97316,#c2410c); color:#fff; }
    .badge-medium   { background: linear-gradient(135deg,#eab308,#a16207); color:#fff; }
    .badge-low      { background: linear-gradient(135deg,#22c55e,#15803d); color:#fff; }
    
    .threat-badge {
        display: inline-block;
        padding: 4px 14px; border-radius: 20px;
        font-size: 11px; font-weight: 800; letter-spacing: 1.2px;
        text-transform: uppercase;
    }

    /* ── Pulse animation for CRITICAL threat ── */
    @keyframes pulse-ring {
        0%   { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
        70%  { box-shadow: 0 0 0 16px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    .pulse { animation: pulse-ring 1.4s infinite; }

    /* ── Stat Metric Cards ── */
    .metric-value { font-size: 2.2rem; font-weight: 800; line-height: 1; color: #166534; }
    .metric-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; color: #64748b; margin-top: 4px; font-weight: 700; }
    
    /* ── Timeline items ── */
    .timeline-item {
        border-left: 2px solid rgba(34, 197, 94, 0.3);
        padding: 8px 0 8px 16px;
        margin-bottom: 8px;
        position: relative;
    }
    .timeline-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #16a34a;
        position: absolute; left: -5px; top: 12px;
    }

    /* ── Streamlit overrides ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.45);
        border-radius: 14px; padding: 4px;
        border: 1px solid rgba(34, 197, 94, 0.12);
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px; color: #4b5563;
        font-weight: 600; padding: 10px 22px;
        transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
        font-family: 'Poppins', sans-serif !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(34, 197, 94, 0.06);
        color: #16a34a;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #16a34a, #15803d) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(22, 163, 74, 0.25) !important;
        border: none !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.65);
        border: 1px solid rgba(34, 197, 94, 0.12);
        border-radius: 14px; padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(5, 46, 22, 0.02);
    }
    div[data-testid="stMetric"] label { color: #64748b !important; font-size: 0.72rem !important; font-weight: 700 !important; text-transform: uppercase; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #15803d !important; font-weight: 800; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #16a34a, #15803d);
        border: none;
        color: #ffffff !important; border-radius: 12px; font-weight: 600;
        font-family: 'Poppins', sans-serif !important;
        padding: 10px 20px;
        transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 14px rgba(22, 163, 74, 0.22);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #15803d, #166534);
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(22, 163, 74, 0.35);
        color: #ffffff !important;
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* RED Stop Button Override */
    div.st-key-stop_cam_btn > button {
        background: linear-gradient(135deg, #ef4444, #b91c1c) !important;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.35) !important;
        border: none !important;
    }
    div.st-key-stop_cam_btn > button:hover {
        background: linear-gradient(135deg, #d32f2f, #991b1b) !important;
        box-shadow: 0 8px 22px rgba(239, 68, 68, 0.45) !important;
        transform: translateY(-2px) !important;
        color: #ffffff !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(22, 163, 74, 0.3); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(22, 163, 74, 0.5); }

    h1, h2, h3, h4 { font-family: 'Poppins', sans-serif !important; color: #14532d !important; font-weight: 800 !important; }
    p, li, span, label { color: #374151; line-height: 1.6; }
    
    /* Elegant entering animation */
    @keyframes card-fade-in {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .glass-card {
        animation: card-fade-in 0.4s ease both;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  INTRO SPLASH ANIMATION  –  iframe injection, no markdown sanitiser issues
# ─────────────────────────────────────────────────────────────────────────────
def inject_intro_animation():
    """Injects the intro splash via a 0-height components iframe.
    Uses window.parent.document to write CSS + HTML directly into the
    Streamlit page DOM — bypasses st.markdown sanitisation completely.
    Session-state guard prevents re-injection on Streamlit reruns."""
    if st.session_state.get("intro_injected"):
        return
    st.session_state["intro_injected"] = True

    import streamlit.components.v1 as components
    components.html("""
<!DOCTYPE html><html><body>
<script>
(function () {
  var KEY = "wn_intro_v3";
  var par = window.parent;
  var doc = par.document;

  /* Only once per browser session */
  if (par.sessionStorage && par.sessionStorage.getItem(KEY)) return;
  if (par.sessionStorage) par.sessionStorage.setItem(KEY, "1");

  /* ── Inject CSS ── */
  var s = doc.createElement("style");
  s.id = "wn-intro-css";
  s.textContent = [
    "#wn-splash{position:fixed;inset:0;z-index:2147483647;display:flex;",
    "align-items:center;justify-content:center;overflow:hidden;",
    "background:linear-gradient(-45deg,#f0fdf4,#dcfce7,#ecfdf5,#d1fae5);",
    "background-size:400% 400%;font-family:'Poppins','Inter',sans-serif;",
    "transition:opacity .85s ease,transform .85s ease;}",

    ".wn-leaf{position:absolute;bottom:-60px;font-size:1.5rem;opacity:0;",
    "pointer-events:none;user-select:none;animation:wn-float linear infinite;}",
    "@keyframes wn-float{",
    "0%{bottom:-60px;opacity:0;transform:translateX(0) rotate(0deg)}",
    "15%{opacity:.75}85%{opacity:.4}",
    "100%{bottom:110vh;opacity:0;transform:translateX(28px) rotate(340deg)}}",

    "@keyframes wn-bg-pan{",
    "0%{background-position:0% 50%}50%{background-position:100% 50%}",
    "100%{background-position:0% 50%}}",

    ".wn-centre{display:flex;flex-direction:column;align-items:center;gap:20px;",
    "animation:wn-pop .65s cubic-bezier(.34,1.56,.64,1) .1s both;}",
    "@keyframes wn-pop{from{opacity:0;transform:scale(.75) translateY(28px)}",
    "to{opacity:1;transform:scale(1) translateY(0)}}",

    ".wn-ring-outer{position:relative;width:160px;height:160px;border-radius:50%;",
    "border:2px dashed rgba(34,197,94,.35);display:flex;align-items:center;",
    "justify-content:center;animation:wn-spin 7s linear infinite;}",
    "@keyframes wn-spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}",

    ".wn-ring-mid{position:absolute;inset:14px;border-radius:50%;",
    "border:2.5px solid rgba(22,163,74,.5);",
    "animation:wn-pulse-border 2.2s ease-in-out infinite,wn-spin-rev 9s linear infinite;}",
    "@keyframes wn-spin-rev{from{transform:rotate(0deg)}to{transform:rotate(-360deg)}}",
    "@keyframes wn-pulse-border{",
    "0%,100%{border-color:rgba(22,163,74,.35);box-shadow:none}",
    "50%{border-color:rgba(22,163,74,.8);box-shadow:0 0 18px rgba(34,197,94,.3)}}",

    ".wn-disc{position:absolute;inset:30px;border-radius:50%;",
    "background:radial-gradient(circle at 40% 40%,#166534,#052e16);",
    "box-shadow:0 6px 28px rgba(5,46,22,.45),inset 0 1px 0 rgba(255,255,255,.08);",
    "display:flex;align-items:center;justify-content:center;",
    "animation:wn-spin-rev 7s linear infinite;}",

    ".wn-icon{font-size:2.8rem;display:inline-block;",
    "animation:wn-spin 7s linear infinite,wn-icon-pulse 2.4s ease-in-out infinite;",
    "filter:drop-shadow(0 0 10px rgba(74,222,128,.6));}",
    "@keyframes wn-icon-pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.15)}}",

    ".wn-brand{font-size:2.6rem;font-weight:900;letter-spacing:4px;color:#14532d;",
    "line-height:1;white-space:nowrap;}",
    ".wl{display:inline-block;opacity:0;",
    "animation:wn-ltr .38s cubic-bezier(.34,1.56,.64,1) forwards;}",
    ".wl-g{color:#16a34a;}",
    "@keyframes wn-ltr{from{opacity:0;transform:translateY(16px) scale(.65)}",
    "to{opacity:1;transform:translateY(0) scale(1)}}",

    ".wn-tag{font-size:.7rem;font-weight:700;text-transform:uppercase;",
    "letter-spacing:2.8px;color:#16a34a;opacity:0;",
    "animation:wn-fslide .5s ease 1.5s forwards;}",

    ".wn-bar-wrap{width:200px;height:3px;background:rgba(34,197,94,.15);",
    "border-radius:3px;overflow:hidden;opacity:0;",
    "animation:wn-fslide .4s ease 1.7s forwards;}",
    ".wn-bar-fill{height:100%;width:0;border-radius:3px;",
    "background:linear-gradient(90deg,#15803d,#4ade80,#15803d);",
    "background-size:200% 100%;",
    "animation:wn-grow 2.2s cubic-bezier(.4,0,.2,1) 1.7s forwards,",
    "wn-shimmer 1.1s linear 1.7s infinite;}",
    "@keyframes wn-grow{from{width:0}to{width:100%}}",
    "@keyframes wn-shimmer{from{background-position:200% 0}to{background-position:-200% 0}}",

    ".wn-status{font-size:.58rem;font-weight:700;letter-spacing:2.2px;color:#6b7280;",
    "text-transform:uppercase;opacity:0;animation:wn-fslide .4s ease 1.85s forwards;}",

    "@keyframes wn-fslide{from{opacity:0;transform:translateY(7px)}",
    "to{opacity:1;transform:translateY(0)}}"
  ].join("");
  doc.head.appendChild(s);

  /* ── Build overlay HTML ── */
  var leaves = [
    {l:"6%",  d:"6.2s", delay:"0.1s", e:"&#127807;"},
    {l:"18%", d:"7.5s", delay:"0.7s", e:"&#127811;"},
    {l:"33%", d:"5.8s", delay:"1.3s", e:"&#127793;"},
    {l:"50%", d:"8.1s", delay:"0.2s", e:"&#127808;"},
    {l:"65%", d:"6.9s", delay:"1.0s", e:"&#127807;"},
    {l:"79%", d:"7.2s", delay:"0.5s", e:"&#127811;"},
    {l:"90%", d:"5.5s", delay:"1.6s", e:"&#127793;"}
  ];
  var leafHtml = leaves.map(function(x){
    return "<div class='wn-leaf' style='left:"+x.l+
           ";animation-duration:"+x.d+";animation-delay:"+x.delay+"'>"+x.e+"</div>";
  }).join("");

  var letters = [
    {c:"wl",    d:"0.40s", t:"W"}, {c:"wl",    d:"0.47s", t:"i"},
    {c:"wl",    d:"0.54s", t:"l"}, {c:"wl",    d:"0.61s", t:"d"},
    {c:"wl",    d:"0.68s", t:"N"}, {c:"wl",    d:"0.75s", t:"o"},
    {c:"wl",    d:"0.82s", t:"d"}, {c:"wl",    d:"0.89s", t:"e"},
    {c:"wl",    d:"0.95s", t:"&nbsp;"},
    {c:"wl wl-g",d:"1.03s",t:"A"},{c:"wl wl-g",d:"1.10s",t:"I"}
  ];
  var brandHtml = letters.map(function(x){
    return "<span class='"+x.c+"' style='animation-delay:"+x.d+"'>"+x.t+"</span>";
  }).join("");

  var div = doc.createElement("div");
  div.id = "wn-splash";
  div.innerHTML = leafHtml +
    "<div class='wn-centre'>" +
      "<div class='wn-ring-outer'>" +
        "<div class='wn-ring-mid'></div>" +
        "<div class='wn-disc'><span class='wn-icon'>&#127807;</span></div>" +
      "</div>" +
      "<div class='wn-brand'>" + brandHtml + "</div>" +
      "<div class='wn-tag'>Human-Wildlife Conflict Mitigation Node</div>" +
      "<div class='wn-bar-wrap'><div class='wn-bar-fill'></div></div>" +
      "<div class='wn-status'>Initialising Sentinel Edge Fleet\u2026</div>" +
    "</div>";
  doc.body.appendChild(div);

  /* Start background pan animation via JS (CSS animation on fixed bg) */
  div.style.animation = "wn-bg-pan 10s ease infinite";

  /* ── Auto-dismiss after 3.8 s ── */
  setTimeout(function () {
    var el = doc.getElementById("wn-splash");
    if (!el) return;
    el.style.opacity = "0";
    el.style.transform = "scale(1.04)";
    setTimeout(function () {
      if (el.parentNode) el.parentNode.removeChild(el);
      var css = doc.getElementById("wn-intro-css");
      if (css && css.parentNode) css.parentNode.removeChild(css);
    }, 900);
  }, 3800);

})();
</script>
</body></html>
""", height=0)

def threat_color(level: str) -> str:
    return {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"}.get(level, "#64748b")

def threat_emoji(level: str) -> str:
    return {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "📡", "LOW": "✅"}.get(level, "🔍")

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "cam_running"        : False,
        "cam_frame_bytes"    : None,
        "cam_last_detections": [],
        "total_detections"   : 0,
        "high_alerts"        : 0,
        "enable_sms_alerts"  : True,
        "enable_whatsapp_alerts": True,
        "sector"             : "North Sector – Kaziranga Buffer",
        "intro_injected"     : False,   # tracks first injection this Python session
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR PANEL
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:15px 0'>
          <span style='font-size:3.5rem'>🌿</span>
          <h1 style='margin:10px 0 5px 0;font-size:1.5rem'>WildNode AI</h1>
          <div style='font-size:0.75rem;color:#bbf7d0;letter-spacing:1px;font-weight:700'>CONFLICT MITIGATION NODE</div>
        </div>
        <hr style='border-color:rgba(255,255,255,0.15);margin:10px 0 20px 0'>
        """, unsafe_allow_html=True)

        st.markdown("### ⚙️ Edge Telemetry Toggles")
        
        st.session_state.enable_sms_alerts = st.toggle(
            "📱 Dispatch Twilio SMS Alerts",
            value=st.session_state.enable_sms_alerts,
            help="Dispatches raw cellular text stream alerts during critical sightings."
        )

        st.session_state.enable_whatsapp_alerts = st.toggle(
            "💬 Route Twilio WhatsApp",
            value=st.session_state.enable_whatsapp_alerts,
            help="Pushes dynamic WhatsApp stream alert cards during crop-damage incidents."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📡 Active Sentinel Location")
        st.session_state.sector = st.text_input(
            "Sentinel Location Zone",
            value=st.session_state.sector,
            placeholder="e.g. North Zone Boundary"
        )

        # Quick statistics summary in sidebar
        st.markdown("<br><hr style='border-color:rgba(255,255,255,0.15);margin:15px 0'>", unsafe_allow_html=True)
        st.markdown("### 📊 Sentinel Node Feed Log")
        
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-radius:12px;padding:14px;font-size:0.8rem;line-height:1.8'>
          🟢 <b>Node Sentinel:</b> Active<br>
          🚨 <b>High Alerts Grabs:</b> {st.session_state.high_alerts}<br>
          🎯 <b>Total Bounding Logs:</b> {st.session_state.total_detections}<br>
          📟 <b>Edge Telemetry Route:</b> Standard Solar Panel (88% Charger)
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  TAB: LIVE OPTICAL CAMERA STREAM
# ─────────────────────────────────────────────────────────────────────────────
def tab_webrtc():
    st.markdown('''
    <div class='glass-card' style='padding:18px;margin-bottom:14px'>
      <div style='font-size:1.15rem;font-weight:800;color:#16a34a;margin-bottom:6px'>📹 REAL-TIME OPTICAL CAMERA STREAM</div>
      <div style='color:#4b5563;font-size:0.82rem;line-height:1.8'>
        Live video Sentinel stream feed integrated with <b style='color:#16a34a'>YOLO-World</b> zero-shot agricultural pest detector.<br>
        Monitors 14 crop-damaging classes. System automatically routes high-threat events to Twilio SMS and WhatsApp channels.
      </div>
    </div>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('''<div style='font-size:0.78rem;color:#15803d;margin-bottom:8px;font-weight:600'>
        📱 <b>Webcam / IP Camera:</b> Paste camera video stream URL below (e.g. from an Android IP Webcam app), or leave fully blank to activate your laptop/PC primary webcam.</div>''', unsafe_allow_html=True)

        cam_source = st.text_input(
            "Camera URL (blank = standard built-in webcam)",
            placeholder="http://192.168.1.100:8080/video",
            label_visibility="collapsed"
        )
        conf_live = st.slider("Model Confidence Threshold", 0.15, 0.85, 0.35, 0.05, key="cam_conf_slider")
        
        use_popout = st.checkbox("🟢 Use Native Ultra-Smooth Popup Window (Recommended: Prevents Dashboard Lag)", value=True, 
                                 help="Renders video directly via OpenCV in a separate ultra-smooth window rather than pushing through the slow browser dashboard.")
        
        # STOP / START Controls in the same panel
        if st.session_state.cam_running:
            if st.button("🛑 STOP LIVE CAMERA SENTINEL STREAM", key="stop_cam_btn", use_container_width=True):
                st.session_state.cam_running = False
                st.rerun()
            run_cam = True
        else:
            run_cam = st.toggle("🎥 Start Native Camera Sentinel Stream", value=False)
            
        FRAME_WINDOW = st.empty()
        
    with col2:
        INFO_WINDOW = st.empty()

    # Trigger logic
    if run_cam:
        st.session_state.cam_running = True
        import cv2
        
        try:
            try:
                from vision_detection.wildlife_detector import (
                    detect_agricultural_pests, draw_detections_on_frame
                )
            except Exception as e:
                print(f"[CamThread] Import error: {e}")
                st.session_state.cam_running = False
                return

            class FastVideoCapture:
                def __init__(self, src):
                    if isinstance(src, int) or str(src).isdigit():
                        self.cap = cv2.VideoCapture(int(src), cv2.CAP_DSHOW)
                    else:
                        self.cap = cv2.VideoCapture(src)
                        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    self.ret = False
                    self.frame = None
                    self.running = True
                    if self.cap.isOpened():
                        self.ret, self.frame = self.cap.read()
                        self.t = threading.Thread(target=self._update, daemon=True)
                        self.t.start()

                def _update(self):
                    while self.running:
                        ret, frame = self.cap.read()
                        self.ret = ret
                        if ret:
                            self.frame = frame
                        else:
                            break

                def read(self):
                    if self.frame is None:
                        return False, None
                    return self.ret, self.frame.copy()

                def isOpened(self):
                    return self.cap.isOpened()

                def release(self):
                    self.running = False
                    self.cap.release()

            source = cam_source.strip() if cam_source.strip() else 0
            cap = FastVideoCapture(source)

            if not cap.isOpened():
                if isinstance(source, str) and source.startswith(("http://", "https://", "rtsp://")):
                    st.error("❌ **Cannot connect to the IP camera stream.**\n\n"
                             "Please ensure:\n"
                             "1. The **IP Webcam** app is actively running on your phone (you tapped **'Start server'**).\n"
                             "2. Both your phone and PC are connected to the **same Wi-Fi network**.\n"
                             "3. The IP address and port match **exactly** what is shown on your phone's screen.")
                else:
                    st.error("Cannot open camera. Please check camera connections or Windows privacy permissions!")
                st.session_state.cam_running = False
                return

            import concurrent.futures
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            future = None
            last_detections = []

            if use_popout:
                cv2.namedWindow('WildNode AI Ultra-Smooth Stream', cv2.WINDOW_NORMAL)
                cv2.setWindowProperty('WildNode AI Ultra-Smooth Stream', cv2.WND_PROP_TOPMOST, 1)

            empty_frames = 0
            try:
                while st.session_state.cam_running:
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        empty_frames += 1
                        if empty_frames > 20:
                            break
                        time.sleep(0.1)
                        continue
                    
                    empty_frames = 0
                    frame = cv2.resize(frame, (640, 480))

                    # Non-blocking AI detection
                    if future is None or future.done():
                        if future is not None:
                            last_detections = future.result()
                            st.session_state.cam_last_detections = last_detections
                            
                            # Log totals & check alarms
                            if last_detections:
                                st.session_state.total_detections += len(last_detections)
                                high = [d for d in last_detections if d["threat_level"] in ("HIGH", "CRITICAL")]
                                if high:
                                    st.session_state.high_alerts += len(high)
                                    # Twilio alert trigger
                                    best = max(high, key=lambda d: d["confidence"])
                                    animal_name = best["class"]
                                    action = best["action"]
                                    alert_msg = f"{animal_name.upper()} detected at {st.session_state.sector}. Immediate Action: {action}."
                                    decision = {
                                        "risk_level": best["threat_level"],
                                        "risk_score": int(best["confidence"] * 100),
                                        "detections": last_detections,
                                        "mitigation_action": action,
                                        "alert_message": alert_msg,
                                        "recommended_action": action,
                                    }
                                    dispatch_alert(
                                        decision,
                                        enable_sms=st.session_state.enable_sms_alerts,
                                        enable_whatsapp=st.session_state.enable_whatsapp_alerts,
                                        enable_log=True,
                                    )

                        future = executor.submit(detect_agricultural_pests, frame, conf_live)

                    # Draw boxes
                    annotated_frame = draw_detections_on_frame(frame.copy(), last_detections)

                    # Show outputs
                    if use_popout:
                        cv2.imshow('WildNode AI Ultra-Smooth Stream', annotated_frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                        FRAME_WINDOW.markdown("""
                        <div class='glass-card' style='text-align:center;padding:50px;border:2px dashed rgba(22, 163, 74, 0.4)'>
                          <div style='font-size:2.8rem;animation:pulse-ring 1.5s infinite'>🟢</div>
                          <div style='color:#15803d;font-size:1.15rem;font-weight:800;margin-top:14px'>LIVE POP-OUT ACTIVE</div>
                          <div style='color:#64748b;font-size:0.8rem;margin-top:6px'>Stream is running smoothly in a native GPU window on your system.</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        FRAME_WINDOW.image(annotated_frame, channels="BGR", use_container_width=True)

                    # Render Right Column (Sentinel Status Meta-box)
                    if last_detections:
                        best = max(last_detections, key=lambda d: d.get("confidence", 0.0))
                        info = ANIMAL_METADATA.get(best["class"], {})
                        color = threat_color(best["threat_level"])
                        
                        INFO_WINDOW.markdown(f"""
                        <div class='glass-card' style='border-left:4.6px solid {color};padding:18px'>
                          <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:8px'>
                            <span style='font-size:1.2rem'>{info.get('emoji','🐗')}</span>
                            <span style='font-weight:800;font-size:1rem;color:#14532d'>{best['class'].upper()}</span>
                            <span class='threat-badge badge-{best.get('threat_level','low').lower()}'>{best.get('threat_level','?')} THREAT</span>
                          </div>
                          <div style='color:#374151;font-size:0.82rem;margin-bottom:8px'>🌾 <b>Crop Damage Profile:</b> {info.get('crop_damage', 'Severe agricultural raid profile.')}</div>
                          <div style='color:#14532d;font-size:0.82rem;font-weight:700'>💡 <b>Immediate Action:</b> {info.get('action', 'Alert local rangers.')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        INFO_WINDOW.markdown("""
                        <div class='glass-card' style='border-left:4px solid #22c55e;padding:24px;text-align:center'>
                          <div style='font-size:2rem'>🌿</div>
                          <div style='color:#22c55e;font-weight:800;margin-top:8px;font-size:1.05rem;letter-spacing:0.5px'>FIELD IS CLEAR</div>
                          <div style='color:#64748b;font-size:0.8rem;margin-top:4px'>No agricultural pest activities detected inside Sentinel boundary.</div>
                        </div>
                        """, unsafe_allow_html=True)

                    time.sleep(0.04)

            except Exception as e:
                print(f"[CamThread] Critical loop error: {e}")
            finally:
                cap.release()
                if use_popout:
                    cv2.destroyAllWindows()
                executor.shutdown(wait=False)
                st.session_state.cam_running = False
                st.session_state.cam_frame_bytes = None
                print("[CamThread] Stopped cleanly.")
                
        except Exception as e:
            st.error(f"Sentinel Loop Interrupted: {e}")
            st.session_state.cam_running = False

    else:
        st.session_state.cam_running = False
        FRAME_WINDOW.markdown("""
        <div class='glass-card' style='text-align:center;padding:70px;border:2px dashed rgba(34,197,94,0.18)'>
          <div style='font-size:3.5rem; margin-bottom:10px'>📷</div>
          <div style='color:#15803d;font-size:1.2rem;font-weight:800;margin-top:10px'>Optical Monitor Inactive</div>
          <div style='color:#64748b;font-size:0.82rem;margin-top:6px'>Toggle the sentinel button above to link your camera edge streams.</div>
        </div>
        """, unsafe_allow_html=True)
        
        INFO_WINDOW.markdown("""
        <div class='glass-card' style='border-left:4px solid #64748b;padding:24px;text-align:center'>
          <div style='font-size:2rem'>📡</div>
          <div style='color:#64748b;font-weight:800;margin-top:8px;font-size:1.05rem;letter-spacing:0.5px'>SENTINEL STANDBY</div>
          <div style='color:#64748b;font-size:0.8rem;margin-top:4px'>Active camera detections list will load here during runtime.</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  TAB: OFFLINE MEDIA ANALYZER
# ─────────────────────────────────────────────────────────────────────────────
def tab_vision():
    st.markdown("""
    <div class='glass-card' style='padding:18px;margin-bottom:14px'>
      <div style='font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;font-weight:700'>
        📤 OPTICAL MEDIA ANALYZER
      </div>
      <div style='color:#4b5563;font-size:0.82rem;line-height:1.7'>
        <b>Zero-Shot Photo Upload</b> – Verify localized edge detections or test agricultural threats instantly using custom zero-shot prompts.<br>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.2);
                border-radius:12px;padding:10px 14px;margin-bottom:14px;font-size:0.8rem;color:#15803d;font-weight:600'>
      🧠 <b>Edge Sentinel Sandbox</b> — Upload any standard image format (JPG, PNG) to execute model bounding checks.
    </div>
    """, unsafe_allow_html=True)

    conf_thresh = st.slider("Zero-Shot Confidence Target", 0.15, 0.85, 0.35, 0.05, key="sandbox_conf_slider")
    
    uploaded = st.file_uploader(
        "Upload image files",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )
    
    if uploaded is not None:
        try:
            img = Image.open(uploaded)
            col_img, col_res = st.columns([1, 1])
            with col_img:
                st.image(img, caption="Original Sandbox Upload", use_container_width=True)
            
            with col_res:
                with st.spinner("Executing Edge YOLO Bounding Engine..."):
                    import numpy as np
                    import cv2
                    
                    # Convert PIL to BGR OpenCV image
                    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    
                    # Run Zero-Shot detection
                    detections = detect_agricultural_pests(cv_img, conf_thresh)
                    
                    if detections:
                        annotated = draw_detections_on_frame(cv_img, detections)
                        # Convert back to RGB for streamlit
                        st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Processed YOLO Overlay", use_container_width=True)
                        
                        # Detailed threat metrics cards
                        for d in detections:
                            info = ANIMAL_METADATA.get(d["class"], {})
                            color = threat_color(d["threat_level"])
                            st.markdown(f"""
                            <div class='glass-card' style='border-left:4px solid {color};padding:12px 16px;margin-top:8px'>
                              <div style='display:flex;align-items:center;justify-content:space-between'>
                                <span style='font-weight:700;color:#14532d'>{d['class'].upper()} ({int(d['confidence']*100)}%)</span>
                                <span class='threat-badge badge-{d['threat_level'].lower()}'>{d['threat_level']}</span>
                              </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("No agricultural pests identified inside bounds. Image clear!")
                        
        except Exception as e:
            st.error(f"Error executing Sentinel sandbox pipeline: {e}")

# ─────────────────────────────────────────────────────────────────────────────
#  TAB: HISTORICAL INCIDENT REPOSITORY
# ─────────────────────────────────────────────────────────────────────────────
def tab_alerts():
    alerts = get_recent_alerts(50)
    if not alerts:
        st.markdown("<div class='glass-card' style='text-align:center;padding:40px;color:#64748b'>No alert logs recorded on this edge node yet.</div>", unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div style='font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;font-weight:700'>
      📜 Historical Incident Repository ({len(alerts)} items)
    </div>
    """, unsafe_allow_html=True)

    alerts_rev = list(reversed(alerts))
    for a in alerts_rev[:30]:
        lvl = a.get("risk_level", "LOW")
        col = threat_color(lvl)
        ico = threat_emoji(lvl)
        ts  = a.get("timestamp", "")[:19].replace("T", " ")
        st.markdown(f"""
        <div class='glass-card' style='padding:16px 20px;border-left:4px solid {col};margin-bottom:10px'>
          <div style='display:flex;align-items:center;gap:12px;flex-wrap:wrap'>
            <span style='font-size:1.2rem'>{ico}</span>
            <span class='threat-badge badge-{lvl.lower()}'>{lvl}</span>
            <span style='color:#64748b;font-size:0.78rem;font-weight:600'>{ts}</span>
            <span style='color:#64748b;font-size:0.78rem;font-weight:600'>📍 {a.get('location','Live Node')}</span>
            <span style='margin-left:auto;color:{col};font-weight:800'>{a.get('risk_score',0)}% Match</span>
          </div>
          <div style='color:#374151;font-size:0.82rem;margin-top:8px;line-height:1.6'>
            <b>Threat Description:</b> Sentinel spotted agricultural pest targets near buffer perimeters.<br>
            <b>Mitigation Action Route:</b> {a.get('mitigation_action', 'Contact rangers immediately.')}
          </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  TAB: SYSTEM spec
# ─────────────────────────────────────────────────────────────────────────────
def tab_about():
    st.markdown("""
    <div class='glass-card' style='padding:22px;margin-bottom:14px'>
      <div style='font-size:1.15rem;font-weight:800;color:#14532d;margin-bottom:8px'>📡 EDGE sentinel MODEL STACK SPECIFICATION</div>
      <div style='color:#4b5563;font-size:0.85rem;line-height:1.8'>
        This edge node runs completely local optical detection networks coupled with instant central Twilio alert routers.
        Features zero simulation overhead, ensuring optimal frames-per-second on hardware deployments.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='glass-card'>
      <div style='font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:16px;font-weight:700'>Model Stack Architecture</div>
      <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px'>
        <div style='background:rgba(34,197,94,0.04);border:1px solid rgba(34,197,94,0.12);border-radius:16px;padding:18px;text-align:center'>
          <div style='font-size:2rem'>👁️</div>
          <div style='font-size:0.85rem;font-weight:800;color:#16a34a;margin:6px 0'>YOLO-World Zero-Shot</div>
          <div style='font-size:0.72rem;color:#64748b;line-height:1.6'>Open-vocabulary real-time detection prompts, enabling zero-shot detection of target wildlife classes natively without training constraints.</div>
        </div>
        <div style='background:rgba(167,139,250,0.04);border:1px solid rgba(167,139,250,0.12);border-radius:16px;padding:18px;text-align:center'>
          <div style='font-size:2rem'>🎯</div>
          <div style='font-size:0.85rem;font-weight:800;color:#a78bfa;margin:6px 0'>Custom YOLO11 Weights</div>
          <div style='font-size:0.72rem;color:#64748b;line-height:1.6'>Loads localized trained weights (best.pt) from local edge fine-tuning scripts automatically when compiled.</div>
        </div>
        <div style='background:rgba(34,197,94,0.04);border:1px solid rgba(34,197,94,0.12);border-radius:16px;padding:18px;text-align:center'>
          <div style='font-size:2rem'>📟</div>
          <div style='font-size:0.85rem;font-weight:800;color:#15803d;margin:6px 0'>Twilio Router</div>
          <div style='font-size:0.72rem;color:#64748b;line-height:1.6'>Central alert dispatch logs console feeds and routes real-time cellular WhatsApp notifications and SMS streams during high-threat incidents.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN RENDER LOOP
# ─────────────────────────────────────────────────────────────────────────────
def main():
    inject_css()
    inject_intro_animation()   # themed fade-open splash – auto-dismisses in browser
    render_sidebar()

    # Frosted Header Card
    ist_now = datetime.now(IST).strftime("%d %b %Y · %I:%M:%S %p IST")
    st.markdown(f"""
    <div class='glass-card' style='display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;padding:14px 24px;flex-wrap:wrap;gap:12px;border-left:4px solid #16a34a'>
      <div style='display:flex;align-items:center;gap:10px'>
        <span style='font-size:1.6rem'>🌿</span>
        <div>
          <h2 style='margin:0;font-size:1.25rem;font-weight:800;color:#14532d;letter-spacing:0.5px'>WILDNODE AI – MITIGATION NODE</h2>
          <div style='font-size:0.7rem;color:#64748b;font-weight:700;text-transform:uppercase'>Autonomous Forest Sentinel Edge Fleet</div>
        </div>
      </div>
      <div style='background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.18);border-radius:10px;padding:6px 14px;font-size:0.78rem;font-weight:700;color:#15803d;font-family:monospace'>
        ⏱️ {ist_now}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Exactly four tabs
    tabs = st.tabs([
        "📹 Sentinel Camera Stream",
        "📤 Upload Sandbox",
        "📜 Incident Repository",
        "ℹ️ System Specifications"
    ])

    with tabs[0]:
        tab_webrtc()
    with tabs[1]:
        tab_vision()
    with tabs[2]:
        tab_alerts()
    with tabs[3]:
        tab_about()


if __name__ == "__main__":
    main()
