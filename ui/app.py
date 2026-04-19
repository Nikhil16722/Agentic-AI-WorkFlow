"""
ui/app.py — NeuralFlow
Fix: Sidebar always visible + toggle button restored
"""

import sys, os, time, datetime
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from workflows.workflow_manager import WorkflowManager

st.set_page_config(
    page_title="NeuralWorkFlow — AI Agent Workflow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"   # always open
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

/* ── TOKENS ─────────────────────────── */
:root {
  --obsidian:   #07080a;
  --card:       #0d1017;
  --border:     #1e2736;
  --border-hi:  #2a3748;
  --amber:      #f5a623;
  --amber-soft: rgba(245,166,35,0.12);
  --amber-mid:  rgba(245,166,35,0.35);
  --mint:       #20e3a0;
  --mint-soft:  rgba(32,227,160,0.10);
  --mint-mid:   rgba(32,227,160,0.30);
  --rose:       #f55c7a;
  --rose-soft:  rgba(245,92,122,0.12);
  --ice:        #7eb8f7;
  --ice-soft:   rgba(126,184,247,0.10);
  --ice-mid:    rgba(126,184,247,0.30);
  --text-bright:#f4f7ff;
  --text-body:  #cdd8ee;
  --text-mid:   #9aadc8;
  --text-dim:   #6a7d98;
  --text-ghost: #3d5068;
}

/* ── GLOBAL ─────────────────────────── */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  background: var(--obsidian) !important;
  color: var(--text-body) !important;
}
.main .block-container {
  padding: 2.5rem 3rem 5rem !important;
  max-width: 1100px;
}
#MainMenu, footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--obsidian); }
::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius:2px; }

/* ── SIDEBAR TOGGLE BUTTON — make it visible ── */
button[data-testid="collapsedControl"] {
  background: var(--amber) !important;
  color: #000 !important;
  border-radius: 50% !important;
  width: 32px !important;
  height: 32px !important;
  border: none !important;
  box-shadow: 0 0 16px var(--amber-mid) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

[data-testid="collapsedControl"] svg {
  color: #000 !important;
  fill: #000 !important;
}

/* sidebar open/close arrow */
.css-1544g2n, [data-testid="stSidebarCollapseButton"] button {
  background: var(--card) !important;
  border: 1px solid var(--border-hi) !important;
  color: var(--text-mid) !important;
  border-radius: 8px !important;
}

/* ── SIDEBAR ─────────────────────────── */
section[data-testid="stSidebar"] {
  background: #06070a !important;
  border-right: 2px solid var(--border-hi) !important;
  min-width: 265px !important;
  max-width: 265px !important;
  display: block !important;
  visibility: visible !important;
}
section[data-testid="stSidebar"] > div {
  padding: 1.8rem 1.3rem !important;
  display: block !important;
}
section[data-testid="stSidebar"] * {
  display: revert !important;
}

/* brand */
.nf-brand {
  display: flex !important; align-items: center; gap: 12px;
  padding-bottom: 1.4rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.5rem;
}
.nf-brand-mark {
  width: 40px; height: 40px;
  background: var(--amber);
  border-radius: 12px;
  display: flex !important; align-items: center; justify-content: center;
  font-size: 20px;
  box-shadow: 0 0 24px var(--amber-mid);
  flex-shrink: 0;
}
.nf-brand-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 22px; letter-spacing: 1px;
  color: var(--text-bright); line-height: 1;
  display: block !important;
}
.nf-brand-sub {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px; letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--amber); margin-top: 3px;
  display: block !important;
}

/* section labels */
.nf-section {
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 9px !important; letter-spacing: 3px !important;
  text-transform: uppercase !important;
  color: var(--text-dim) !important;
  margin: 1.3rem 0 0.65rem !important;
  display: block !important;
}

/* pills */
.nf-pill {
  display: flex !important; align-items: center; gap: 9px;
  padding: 9px 13px; border-radius: 10px; border: 1px solid;
  font-size: 12px; font-weight: 500; margin-bottom: 7px;
}
.nf-pill.green { background:var(--mint-soft);  border-color:var(--mint-mid); color:var(--mint);}
.nf-pill.amber { background:var(--amber-soft); border-color:var(--amber-mid);color:var(--amber);}
.nf-pill.rose  { background:var(--rose-soft);  border-color:rgba(245,92,122,.3);color:var(--rose);}
.nf-pill.ice   { background:var(--ice-soft);   border-color:var(--ice-mid);  color:var(--ice);}
.nf-dot {
  width:7px; height:7px; border-radius:50%;
  background:currentColor; box-shadow:0 0 7px currentColor;
  animation:blink 2.5s ease-in-out infinite; flex-shrink:0;
  display: inline-block !important;
}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}

/* stat tiles */
.nf-stat-row { display:flex !important; gap:8px; margin-bottom:8px; }
.nf-stat {
  flex:1; background:var(--card);
  border:1px solid var(--border); border-radius:10px;
  padding:12px 14px; display:block !important;
}
.nf-stat-label {
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; letter-spacing:2px; text-transform:uppercase;
  color:var(--text-mid); margin-bottom:5px;
  display: block !important;
}
.nf-stat-value {
  font-family:'Bebas Neue',sans-serif;
  font-size:30px; line-height:1; color:var(--amber);
  display: block !important;
}

/* agent status */
.nf-agent-status {
  background:var(--card); border:1px solid var(--border);
  border-radius:10px; padding:12px 14px; margin-bottom:8px;
  display: block !important;
}
.nf-agent-status-val {
  font-family:'IBM Plex Mono',monospace;
  font-size:12px; font-weight:500; margin-top:4px;
  display: block !important;
}

/* agents */
.nf-agent {
  display:flex !important; align-items:center; gap:10px;
  padding:10px 13px; border-radius:10px;
  border:1px solid var(--border); background:var(--card);
  margin-bottom:6px;
}
.nf-agent-ico {
  width:30px; height:30px; border-radius:8px;
  background:var(--border-hi);
  display:flex !important; align-items:center; justify-content:center;
  font-size:15px; flex-shrink:0;
}
.nf-agent-name {
  font-size:12px; font-weight:600;
  color:var(--text-bright); display:block !important;
}
.nf-agent-desc {
  font-size:10px; color:var(--text-mid);
  margin-top:2px; display:block !important;
}
.nf-agent-live {
  width:6px; height:6px; border-radius:50%;
  background:var(--mint); box-shadow:0 0 6px var(--mint);
  margin-left:auto; display:block !important;
  flex-shrink:0;
}

/* log */
.nf-log {
  font-family:'IBM Plex Mono',monospace;
  font-size:10px; color:var(--text-mid);
  padding:4px 0; border-bottom:1px solid var(--border);
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  display:block !important;
}
.nf-log em { color:var(--amber); font-style:normal; }

/* ── SIDEBAR BUTTON ─────────────────── */
section[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--rose) !important;
  border: 1px solid rgba(245,92,122,0.5) !important;
  border-radius: 9px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  padding: 9px 16px !important;
  width: 100% !important;
  transition: all .2s !important;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--rose-soft) !important;
  border-color: var(--rose) !important;
  box-shadow: 0 0 16px rgba(245,92,122,.2) !important;
}

/* ── MAIN HERO ──────────────────────── */
.nf-hero {
  position:relative; padding:0 0 2.5rem;
  border-bottom:1px solid var(--border);
  margin-bottom:2rem; overflow:hidden;
}
.nf-hero::before {
  content:''; position:absolute; inset:-40px;
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg,var(--border) 1px,transparent 1px);
  background-size:40px 40px; opacity:.3; z-index:0;
  mask-image:radial-gradient(ellipse 80% 60% at 50% 0%,black,transparent);
}
.nf-hero > * { position:relative; z-index:1; }
.nf-eyebrow {
  display:inline-flex; align-items:center; gap:8px;
  font-family:'IBM Plex Mono',monospace;
  font-size:10px; letter-spacing:3px; text-transform:uppercase;
  color:var(--amber); margin-bottom:14px;
}
.nf-eyebrow::before {
  content:''; display:inline-block;
  width:20px; height:1.5px; background:var(--amber);
}
.nf-h1 {
  font-family:'Bebas Neue',sans-serif;
  font-size:62px; line-height:.95;
  letter-spacing:1px; color:var(--text-bright); margin-bottom:16px;
}
.nf-h1 em {
  font-style:normal; -webkit-text-fill-color:transparent;
  background:linear-gradient(120deg,var(--amber) 0%,#ffcc55 50%,var(--amber) 100%);
  -webkit-background-clip:text; background-clip:text;
}
.nf-subtitle {
  font-size:15px; font-weight:400;
  color:var(--text-body); line-height:1.7;
  max-width:520px; margin-bottom:0;
}

/* ── HOW IT WORKS ───────────────────── */
.nf-how { display:flex; gap:8px; margin-bottom:2rem; }
.nf-step {
  flex:1; background:var(--card);
  border:1px solid var(--border); border-radius:12px;
  padding:18px 20px;
}
.nf-step-num {
  font-family:'Bebas Neue',sans-serif;
  font-size:36px; line-height:1;
  color:var(--text-ghost); margin-bottom:6px;
}
.nf-step-title {
  font-size:13px; font-weight:600;
  color:var(--text-bright); margin-bottom:5px;
}
.nf-step-desc { font-size:12px; color:var(--text-mid); line-height:1.55; }

/* ── EXAMPLE LABEL ──────────────────── */
.nf-ex-label {
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; letter-spacing:3px; text-transform:uppercase;
  color:var(--text-dim); margin-bottom:10px;
}

/* ── ALL BUTTONS (main content) ─────── */
.stButton > button {
  background: var(--card) !important;
  color: var(--text-body) !important;
  border: 1px solid var(--border-hi) !important;
  border-radius: 10px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 11px 18px !important;
  width: 100% !important;
  transition: all .2s !important;
}
.stButton > button:hover {
  border-color: var(--amber-mid) !important;
  color: var(--amber) !important;
  background: var(--amber-soft) !important;
  transform: translateY(-2px) !important;
}

/* ── INPUT ──────────────────────────── */
.nf-input-label {
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; letter-spacing:3px; text-transform:uppercase;
  color:var(--text-dim); margin-bottom:8px;
}
.stTextArea > div > div {
  background: var(--card) !important;
  border: 1px solid var(--border-hi) !important;
  border-radius: 14px !important;
}
.stTextArea textarea {
  background: transparent !important;
  color: var(--text-bright) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 14px !important; line-height: 1.75 !important;
  border: none !important; box-shadow: none !important;
  padding: 16px !important;
}
.stTextArea textarea::placeholder { color:var(--text-dim) !important; }
.stTextArea textarea:focus { box-shadow: none !important; }
.stTextArea > div > div:focus-within {
  border-color: var(--amber-mid) !important;
  box-shadow: 0 0 0 3px var(--amber-soft) !important;
}
.nf-char {
  font-family:'IBM Plex Mono',monospace;
  font-size:10px; color:var(--text-dim);
  text-align:right; margin-top:6px;
}

/* ── RUN BUTTON ─────────────────────── */
.run-wrap .stButton > button {
  background: var(--amber) !important;
  color: #050505 !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  font-size: 15px !important;
  padding: 14px 36px !important;
  box-shadow: 0 0 32px var(--amber-mid) !important;
  transform: none !important;
}
.run-wrap .stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 0 48px var(--amber-mid) !important;
}
.run-wrap .stButton > button:disabled {
  background: var(--border-hi) !important;
  color: var(--text-dim) !important;
  box-shadow: none !important;
}

/* ── OUTPUT ─────────────────────────── */
.nf-divider { height:1px; background:var(--border); margin:2rem 0; }
.nf-out-header {
  display:flex; align-items:center; gap:12px; margin-bottom:1.2rem;
}
.nf-out-chip {
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; letter-spacing:2px; text-transform:uppercase;
  background:var(--mint-soft); color:var(--mint);
  border:1px solid var(--mint-mid); padding:4px 12px; border-radius:20px;
}
.nf-out-title {
  font-family:'Bebas Neue',sans-serif;
  font-size:24px; letter-spacing:.5px; color:var(--text-bright);
}
.nf-output-card {
  background:var(--card); border:1px solid var(--border-hi);
  border-radius:16px; padding:2rem 2.2rem;
  font-size:14px; color:var(--text-body); line-height:1.85;
  position:relative; overflow:hidden;
}
.nf-output-card::before {
  content:''; position:absolute;
  left:0; top:0; bottom:0; width:3px;
  background:linear-gradient(180deg,var(--mint),transparent);
  border-radius:2px 0 0 2px;
}
.nf-empty {
  background:var(--card); border:1px dashed var(--border-hi);
  border-radius:16px; padding:4rem 2rem; text-align:center;
}
.nf-empty-glyph {
  font-family:'IBM Plex Mono',monospace;
  font-size:42px; color:var(--text-ghost);
  margin-bottom:14px; line-height:1;
}
.nf-empty-text {
  font-family:'IBM Plex Mono',monospace;
  font-size:11px; letter-spacing:2px;
  color:var(--text-dim); text-transform:uppercase;
}

/* alerts */
.stSuccess > div {
  background:var(--mint-soft) !important; border:1px solid var(--mint-mid) !important;
  color:var(--mint) !important; border-radius:10px !important;
}
.stError > div {
  background:var(--rose-soft) !important; border:1px solid rgba(245,92,122,.3) !important;
  color:var(--rose) !important; border-radius:10px !important;
}
.stSpinner > div { border-top-color:var(--amber) !important; }

/* expanders */
.streamlit-expanderHeader {
  background:var(--card) !important; border:1px solid var(--border) !important;
  border-radius:10px !important; color:var(--text-mid) !important;
  font-family:'IBM Plex Mono',monospace !important;
  font-size:11px !important; letter-spacing:1px !important;
}
.streamlit-expanderContent {
  background:var(--card) !important; border:1px solid var(--border) !important;
  border-top:none !important; border-radius:0 0 10px 10px !important;
}

/* ── FOOTER ─────────────────────────── */
.nf-footer {
  display:flex; align-items:center;
  justify-content:space-between;
  padding-top:1.5rem;
  border-top:1px solid var(--border); margin-top:2.5rem;
}
.nf-footer-item {
  font-family:'IBM Plex Mono',monospace;
  font-size:10px; letter-spacing:1px;
  color:var(--text-dim);
  display:flex; align-items:center; gap:6px;
}
.nf-footer-dot {
  width:4px; height:4px; border-radius:50%;
  background:var(--mint); box-shadow:0 0 5px var(--mint);
}
.nf-hist { padding:12px 0; border-bottom:1px solid var(--border); }
.nf-hist-meta {
  font-family:'IBM Plex Mono',monospace;
  font-size:10px; color:var(--mint); margin-bottom:3px;
}
.nf-hist-text { font-size:12px; color:var(--text-mid); }
</style>
""", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────
@st.cache_resource
def load_manager():
    return WorkflowManager()

try:
    manager = load_manager()
    manager_loaded = True
except Exception as e:
    manager_loaded = False
    manager_error = str(e)

for k, v in [("agent_status","Idle"),("logs",[]),("last_output",None),("run_count",0),("example_input","")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="nf-brand">
      <div class="nf-brand-mark">⚡</div>
      <div>
        <div class="nf-brand-title">NeuralFlow</div>
        <div class="nf-brand-sub">Agentic AI System</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Status
    st.markdown('<p class="nf-section">System Status</p>', unsafe_allow_html=True)
    if manager_loaded:
        st.markdown('<div class="nf-pill green"><span class="nf-dot"></span>All Systems Operational</div>', unsafe_allow_html=True)
        mode = manager.memory.get_storage_mode()
        if mode == "supabase":
            st.markdown('<div class="nf-pill ice"><span class="nf-dot"></span>Supabase — Live</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="nf-pill amber"><span class="nf-dot"></span>Local Memory Fallback</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="nf-pill rose"><span class="nf-dot"></span>System Error</div>', unsafe_allow_html=True)

    # Metrics
    st.markdown('<p class="nf-section">Metrics</p>', unsafe_allow_html=True)
    total = manager.memory.count() if manager_loaded else 0
    st.markdown(f"""
    <div class="nf-stat-row">
      <div class="nf-stat">
        <div class="nf-stat-label">Total Runs</div>
        <div class="nf-stat-value">{total}</div>
      </div>
      <div class="nf-stat">
        <div class="nf-stat-label">Session</div>
        <div class="nf-stat-value">{st.session_state.run_count}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    sc = {"Idle":"var(--text-dim)","Running...":"var(--amber)","Completed ✅":"var(--mint)","Failed ❌":"var(--rose)"}
    col = sc.get(st.session_state.agent_status,"var(--text-dim)")
    st.markdown(f"""
    <div class="nf-agent-status">
      <div class="nf-stat-label">Agent Status</div>
      <div class="nf-agent-status-val" style="color:{col}">{st.session_state.agent_status}</div>
    </div>""", unsafe_allow_html=True)

    # Agents
    st.markdown('<p class="nf-section">Active Agents</p>', unsafe_allow_html=True)
    for ico, name, desc in [
        ("🗓","Meeting Agent","Extracts summaries & actions"),
        ("📧","Email Agent","Drafts professional emails"),
        ("✅","Task Agent","Prioritised task breakdown")
    ]:
        st.markdown(f"""
        <div class="nf-agent">
          <div class="nf-agent-ico">{ico}</div>
          <div style="flex:1;min-width:0">
            <div class="nf-agent-name">{name}</div>
            <div class="nf-agent-desc">{desc}</div>
          </div>
          <div class="nf-agent-live"></div>
        </div>""", unsafe_allow_html=True)

    # Logs
    if st.session_state.logs:
        st.markdown('<p class="nf-section">Activity</p>', unsafe_allow_html=True)
        for log in reversed(st.session_state.logs[-4:]):
            ts, txt = (log.split("]",1)+[""])[:2] if "]" in log else ("",log)
            st.markdown(f'<div class="nf-log"><em>{ts}]</em> {txt[:34]}…</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✕  Clear All Memory"):
        if manager_loaded:
            manager.memory.clear_all()
        st.session_state.logs = []
        st.session_state.run_count = 0
        st.session_state.last_output = None
        st.rerun()

# ════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════
st.markdown("""
<div class="nf-hero">
  <div class="nf-eyebrow">⚡ CrewAI · Groq LLaMA 3.1 · Supabase</div>
  <div class="nf-h1">Automate Work<br>With <em>Intelligent</em><br>Agents.</div>
  <div class="nf-subtitle">
    Describe any business task in plain English.
    NeuralFlow detects intent, routes to the right agent,
    and delivers structured professional output — instantly.
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="nf-how">
  <div class="nf-step">
    <div class="nf-step-num">01</div>
    <div class="nf-step-title">Describe</div>
    <div class="nf-step-desc">Type any task in plain English — no special syntax</div>
  </div>
  <div class="nf-step" style="margin:0 8px">
    <div class="nf-step-num">02</div>
    <div class="nf-step-title">Route</div>
    <div class="nf-step-desc">AI detects intent and selects the right agent automatically</div>
  </div>
  <div class="nf-step">
    <div class="nf-step-num">03</div>
    <div class="nf-step-title">Execute</div>
    <div class="nf-step-desc">Agent runs on Groq, saves to Supabase, returns output</div>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown('<p class="nf-ex-label">Quick Examples</p>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🗓  Meeting Summary"):
        st.session_state.example_input = "Summarize a product team meeting where we discussed the Q2 launch timeline, assigned tasks to 3 developers, and decided to delay by one week."
        st.rerun()
with c2:
    if st.button("📧  Email Draft"):
        st.session_state.example_input = "Write a professional email to the client informing them their project is delayed by 2 weeks due to technical issues."
        st.rerun()
with c3:
    if st.button("✅  Task Breakdown"):
        st.session_state.example_input = "Create a task list for launching a mobile app next month including design, development, QA, marketing and deployment."
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p class="nf-input-label">⌨ &nbsp;Describe Your Task</p>', unsafe_allow_html=True)

user_input = st.text_area(
    label="task",
    label_visibility="collapsed",
    value=st.session_state.get("example_input",""),
    placeholder="e.g. Schedule a meeting, send follow-up emails, and create action items for the Q2 launch…",
    height=148,
    key="task_input"
)
if len(user_input):
    st.markdown(f'<p class="nf-char">{len(user_input)} characters</p>', unsafe_allow_html=True)

rc, _ = st.columns([1,3])
with rc:
    st.markdown('<div class="run-wrap">', unsafe_allow_html=True)
    run_btn = st.button("⚡  Run Agents", disabled=not manager_loaded, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="nf-out-header">
  <div class="nf-out-chip">Agent Output</div>
  <div class="nf-out-title">Result</div>
</div>""", unsafe_allow_html=True)

out = st.empty()

if st.session_state.last_output and not run_btn:
    out.markdown(f'<div class="nf-output-card">{st.session_state.last_output}</div>', unsafe_allow_html=True)
elif not run_btn:
    out.markdown("""
    <div class="nf-empty">
      <div class="nf-empty-glyph">◌</div>
      <div class="nf-empty-text">Agents standing by — enter a task above</div>
    </div>""", unsafe_allow_html=True)

if run_btn:
    if not user_input.strip():
        st.warning("Please describe a task first.")
    else:
        st.session_state.agent_status = "Running..."
        st.session_state.run_count += 1
        with st.spinner("Agents are working on your request…"):
            time.sleep(0.4)
            try:
                result = manager.run(user_input)
                st.session_state.last_output = result
                st.session_state.agent_status = "Completed ✅"
                ts = datetime.datetime.now().strftime("%H:%M:%S")
                st.session_state.logs.append(f"[{ts}] {user_input[:45]}")
                out.markdown(f'<div class="nf-output-card">{result}</div>', unsafe_allow_html=True)
                st.success("Task completed — result saved to memory.")
            except Exception as e:
                st.session_state.agent_status = "Failed ❌"
                out.markdown("""
                <div class="nf-empty" style="border-color:rgba(245,92,122,.35)">
                  <div class="nf-empty-glyph" style="color:var(--rose)">⚠</div>
                  <div class="nf-empty-text">Execution failed — check terminal</div>
                </div>""", unsafe_allow_html=True)
                st.error(f"Error: {str(e)}")
        st.rerun()

with st.expander("↗  Run History"):
    if manager_loaded:
        hist = manager.get_history()
        if hist:
            for i, rec in enumerate(hist[:8]):
                v = rec.get("value",{})
                if isinstance(v,dict):
                    st.markdown(f"""
                    <div class="nf-hist">
                      <div class="nf-hist-meta">RUN #{i+1} · {v.get('timestamp','—')} · {v.get('agents_used','—')}</div>
                      <div class="nf-hist-text">{str(v.get('input',''))[:130]}…</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.caption("No history yet.")

st.markdown("""
<div class="nf-footer">
  <div class="nf-footer-item"><div class="nf-footer-dot"></div>CrewAI 0.28.8</div>
  <div class="nf-footer-item"><div class="nf-footer-dot"></div>Groq LLaMA 3.1</div>
  <div class="nf-footer-item"><div class="nf-footer-dot"></div>Supabase</div>
  <div class="nf-footer-item" style="color:var(--text-ghost)">NeuralFlow © 2026</div>
</div>""", unsafe_allow_html=True)