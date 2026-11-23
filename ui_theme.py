"""Colorful responsive theme + the Mimi doll mascot (pure SVG/CSS, no images needed)."""
import html

import streamlit as st


def _flat(s: str) -> str:
    """Collapse to one line so Streamlit's markdown never treats HTML as a code block."""
    return " ".join(line.strip() for line in s.strip().splitlines() if line.strip())


CSS = """
:root{color-scheme:light;}
.stApp{background:#f6f8f7;color:#19231f;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1320px;width:calc(100% - 48px);padding-top:.8rem;padding-bottom:2.5rem;}
section[data-testid="stSidebar"]{background:#ffffff;border-right:1px solid #e4eae7;}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp label,.stApp li{color:#202923;}
.stApp [data-testid="stCaptionContainer"] p{color:#6c7973;}

.hero{display:flex;align-items:center;gap:18px;min-height:92px;padding:14px 22px;margin:8px 0 14px;
background:#fff;border:1px solid #dde5e1;border-radius:16px;box-shadow:0 8px 24px rgba(31,55,46,.06);}
.doll-wrap{width:68px;height:68px;flex:0 0 68px;display:grid;place-items:center;border-radius:50%;
background:#edf8f3;animation:float 3.2s ease-in-out infinite;}
.doll-svg{width:62px;height:auto;display:block;}
.hero-text{display:grid;grid-template-columns:1fr auto;align-items:center;gap:5px 20px;flex:1;}
.hero-title{color:#1a2520;font-size:1.28rem;font-weight:800;letter-spacing:-.02em;}
.hero-tag{grid-row:2;color:#748078;font-size:.92rem;margin-top:-3px;}
.chips{grid-column:2;grid-row:1/3;display:flex;gap:7px;}
.chips span{display:inline-block;background:#f2f5f3;border:1px solid #e2e8e5;color:#4d5e55;
border-radius:999px;padding:7px 10px;font-size:.78rem;font-weight:700;white-space:nowrap;}
.bubble{display:none;}

.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{background:#147d64;color:#fff;
border:1px solid #147d64;border-radius:10px;font-weight:750;padding:.56rem 1rem;
box-shadow:0 4px 12px rgba(20,125,100,.12);transition:all .16s ease;}
.stButton>button:hover,.stFormSubmitButton>button:hover,.stDownloadButton>button:hover{background:#106b56;
border-color:#106b56;transform:translateY(-1px);box-shadow:0 8px 18px rgba(20,125,100,.18);color:#fff;}
.stButton>button p,.stFormSubmitButton>button p,.stDownloadButton>button p{color:#fff;font-weight:750;}
.stButton>button:focus-visible,.stFormSubmitButton>button:focus-visible,.stDownloadButton>button:focus-visible{outline:3px solid #9acbb9;outline-offset:2px;}

.stTabs [data-baseweb="tab-list"]{gap:4px;padding:5px;margin-bottom:12px;width:max-content;max-width:100%;
background:#eef2ef;border:1px solid #e1e7e3;border-radius:12px;}
.stTabs [data-baseweb="tab"]{background:transparent;border:0;border-radius:9px;padding:8px 13px;height:auto;}
.stTabs [data-baseweb="tab"] p{color:#637269;font-weight:700;}
.stTabs [aria-selected="true"]{background:#fff;box-shadow:0 2px 8px rgba(31,55,46,.10);}
.stTabs [aria-selected="true"] p{color:#147d64;}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none;}

[data-testid="stChatMessage"],div[data-testid="stForm"],[data-testid="stMetric"],[data-testid="stExpander"],
div[data-testid="stVerticalBlockBorderWrapper"]>div{background:#fff;border:1px solid #dfe7e3;border-radius:14px;}
[data-testid="stChatMessage"]{padding:14px 18px;margin-bottom:9px;box-shadow:0 3px 12px rgba(31,55,46,.04);}
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"]{background:#e7f4ef;}
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"]{background:#edf1ff;}
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"]{width:42px;height:42px;font-size:22px;}
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"]{width:42px;height:42px;}
div[data-testid="stForm"]{padding:18px;box-shadow:0 5px 18px rgba(31,55,46,.05);}
[data-testid="stMetric"]{padding:14px 16px;box-shadow:0 3px 12px rgba(31,55,46,.05);}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"]{color:#202923;}
[data-testid="stExpander"]{overflow:hidden;}
div[data-baseweb="input"]>div,div[data-baseweb="select"]>div,div[data-testid="stDateInput"] input,
div[data-testid="stNumberInput"] input,div[data-testid="stTextArea"] textarea{background:#fff;color:#202923;border-color:#bdc9c3;}
input::placeholder,textarea::placeholder{color:#87958e!important;opacity:1;}
div[data-testid="stProgress"]>div>div{background:linear-gradient(90deg,#147d64,#42a889);}

.chat-panel{min-height:420px;}
.suggestion-panel{background:#fff;border:1px solid #dfe7e3;border-radius:16px;padding:16px;
box-shadow:0 8px 24px rgba(31,55,46,.05);}
.thinking-dots{display:inline-flex;align-items:center;gap:5px;height:24px;padding:4px 2px;}
.thinking-dots i{width:7px;height:7px;border-radius:50%;background:#6d7f75;animation:thinking 1.2s ease-in-out infinite;}
.thinking-dots i:nth-child(2){animation-delay:.15s;}
.thinking-dots i:nth-child(3){animation-delay:.3s;}
.follow-up-label{margin:14px 0 7px;color:#6c7973;font-size:.82rem;font-weight:700;}
@keyframes thinking{0%,60%,100%{transform:translateY(0);opacity:.35}30%{transform:translateY(-5px);opacity:1}}
.rail-title{display:flex;align-items:center;gap:8px;font-size:.95rem;font-weight:800;color:#26352d;margin:2px 0 12px;}
.rail-kicker{display:inline-block;color:#d95f42;background:#fff2ed;border-radius:999px;padding:5px 9px;
font-size:.72rem;font-weight:800;letter-spacing:.04em;margin-bottom:8px;}

@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
@keyframes blink{0%,92%,100%{transform:scaleY(1)}96%{transform:scaleY(.1)}}
@keyframes wave{from{transform:rotate(0deg)}to{transform:rotate(-55deg)}}
@keyframes pulse{0%,100%{opacity:.25}50%{opacity:1}}
@keyframes twinkle{0%,100%{transform:scale(.7);opacity:.5}50%{transform:scale(1.2);opacity:1}}
.blink{transform-origin:100px 106px;animation:blink 4s infinite;}
.wave{transform-origin:132px 172px;animation:wave .55s ease-in-out infinite alternate;}
.d1,.d2,.d3{animation:pulse 1.2s infinite;}
.d2{animation-delay:.2s}.d3{animation-delay:.4s}
.spark{transform-box:fill-box;transform-origin:center;animation:twinkle 1s infinite;}

@media (max-width:640px){
.block-container{width:calc(100% - 20px);padding:0.6rem 0 2rem;}
.hero{padding:12px 14px;min-height:82px;}
.doll-wrap{width:58px;height:58px;flex-basis:58px;}
.doll-svg{width:54px;}
.hero-text{display:block;}
.hero-title{font-size:1.08rem;}
.hero-tag{display:block;margin:3px 0 0;}
.chips{display:none;}
.stTabs [data-baseweb="tab-list"]{width:100%;display:flex;flex-wrap:nowrap;overflow-x:auto;}
.stTabs [data-baseweb="tab"]{padding:8px 10px;font-size:.82rem;white-space:nowrap;}
div[data-testid="stForm"]{padding:10px;}
}
"""


def inject_css() -> None:
    st.markdown(f"<style>{_flat(CSS)}</style>", unsafe_allow_html=True)


def doll_svg(mood: str = "idle") -> str:
    """Return the Mimi doll as inline SVG. mood: idle | thinking | happy."""
    if mood == "happy":
        eyes = (
            '<path d="M72 108 Q82 96 92 108" stroke="#2d2250" stroke-width="4" fill="none" stroke-linecap="round"/>'
            '<path d="M108 108 Q118 96 128 108" stroke="#2d2250" stroke-width="4" fill="none" stroke-linecap="round"/>'
        )
        mouth = '<path d="M86 126 Q100 150 114 126 Z" fill="#d6336c"/>'
        extra = (
            '<text class="spark" x="150" y="52" font-size="20">✨</text>'
            '<text class="spark" x="18" y="70" font-size="16" style="animation-delay:.4s">⭐</text>'
        )
        arm_class = "wave"
    else:
        eyes = (
            '<g class="blink">'
            '<ellipse cx="82" cy="106" rx="7" ry="9" fill="#2d2250"/>'
            '<ellipse cx="118" cy="106" rx="7" ry="9" fill="#2d2250"/>'
            '<circle cx="84.5" cy="102" r="2.6" fill="#fff"/><circle cx="120.5" cy="102" r="2.6" fill="#fff"/>'
            "</g>"
        )
        arm_class = ""
        if mood == "thinking":
            mouth = '<ellipse cx="100" cy="131" rx="4" ry="5" fill="#d6336c"/>'
            extra = (
                '<circle class="d1" cx="152" cy="62" r="4" fill="#fff"/>'
                '<circle class="d2" cx="162" cy="48" r="6" fill="#fff"/>'
                '<circle class="d3" cx="176" cy="30" r="9" fill="#fff"/>'
            )
        else:
            mouth = '<path d="M90 127 Q100 138 110 127" stroke="#d6336c" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
            extra = ""

    return f"""
    <svg class="doll-svg" viewBox="0 0 200 255" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mimi the study doll">
      <ellipse cx="100" cy="248" rx="55" ry="6" fill="#00000026"/>
      <ellipse cx="38" cy="122" rx="20" ry="36" fill="#6b3f2a"/>
      <ellipse cx="162" cy="122" rx="20" ry="36" fill="#6b3f2a"/>
      <circle cx="48" cy="92" r="9" fill="#ff5fa2"/><circle cx="152" cy="92" r="9" fill="#ff5fa2"/>
      <path d="M70 165 Q100 150 130 165 L158 236 Q100 250 42 236 Z" fill="#ff8fc7"/>
      <path d="M82 160 L100 180 L118 160 Z" fill="#fff"/>
      <circle cx="100" cy="205" r="5" fill="#ffd93d"/><circle cx="100" cy="222" r="5" fill="#ffd93d"/>
      <ellipse cx="82" cy="243" rx="14" ry="6" fill="#7a6cff"/><ellipse cx="118" cy="243" rx="14" ry="6" fill="#7a6cff"/>
      <g><ellipse cx="62" cy="190" rx="10" ry="18" fill="#ffe3cc" transform="rotate(20 62 190)"/></g>
      <g class="{arm_class}"><ellipse cx="138" cy="190" rx="10" ry="18" fill="#ffe3cc" transform="rotate(-20 138 190)"/></g>
      <circle cx="100" cy="100" r="62" fill="#6b3f2a"/>
      <circle cx="100" cy="104" r="50" fill="#ffe3cc"/>
      <path d="M50 100 Q52 52 100 50 Q148 52 150 100 Q140 72 100 70 Q60 72 50 100 Z" fill="#6b3f2a"/>
      {eyes}
      <circle cx="68" cy="122" r="7" fill="#ff8fab" opacity=".5"/><circle cx="132" cy="122" r="7" fill="#ff8fab" opacity=".5"/>
      {mouth}
      <path d="M72 56 L72 70 Q100 84 128 70 L128 56 Z" fill="#3a2f95"/>
      <polygon points="52,54 100,32 148,54 100,76" fill="#4b3fb8"/>
      <line x1="148" y1="54" x2="154" y2="84" stroke="#ffd93d" stroke-width="3"/>
      <circle cx="154" cy="86" r="5" fill="#ffd93d"/>
      {extra}
    </svg>
    """


def hero_html(mood: str, message: str) -> str:
    return _flat(
        f"""
        <div class="hero">
          <div class="doll-wrap">{_flat(doll_svg(mood))}</div>
          <div class="hero-text">
            <div class="hero-title">🎓 StudyBuddy</div>
            <div class="hero-tag">Your AI study assistant – learn smarter, not harder!</div>
            <div class="chips"><span>📅 Schedules</span><span>🧠 Concepts</span><span>📝 MCQs</span><span>🎯 Quizzes</span></div>
            <div class="bubble">{html.escape(message)}</div>
          </div>
        </div>
        """
    )
