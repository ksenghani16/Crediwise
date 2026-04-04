import streamlit as st

st.set_page_config(
    page_title="Crediwise — AI Loan Intelligence",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Merriweather:wght@700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1a2540;
}

/* ══════════════════════════════════════
   SITE-WIDE SOFT BLUE WAVY BACKGROUND
   ══════════════════════════════════════ */
.stApp {
    background-color: #daeeff;
    background-image:
        radial-gradient(ellipse 130% 55% at 5% 0%,   rgba(180,225,255,0.9) 0%, transparent 55%),
        radial-gradient(ellipse 90%  50% at 95% 100%, rgba(150,210,255,0.7) 0%, transparent 55%),
        radial-gradient(ellipse 70%  45% at 55% 48%,  rgba(210,238,255,0.45) 0%, transparent 65%),
        linear-gradient(155deg, #cce8ff 0%, #e4f3ff 28%, #f2f9ff 52%, #ddf0ff 78%, #c8e5ff 100%);
    background-attachment: fixed;
}

/* Layered SVG wave overlay — fixed so it scrolls with the page nicely */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 900' preserveAspectRatio='xMidYMid slice'%3E%3Cdefs%3E%3ClinearGradient id='g1' x1='0' y1='0' x2='1' y2='0'%3E%3Cstop offset='0' stop-color='%2390caf9' stop-opacity='0.55'/%3E%3Cstop offset='1' stop-color='%2364b5f6' stop-opacity='0.15'/%3E%3C/linearGradient%3E%3ClinearGradient id='g2' x1='0' y1='0' x2='1' y2='0'%3E%3Cstop offset='0' stop-color='%23bbdefb' stop-opacity='0.4'/%3E%3Cstop offset='1' stop-color='%2390caf9' stop-opacity='0.2'/%3E%3C/linearGradient%3E%3ClinearGradient id='g3' x1='1' y1='0' x2='0' y2='1'%3E%3Cstop offset='0' stop-color='%23e3f2fd' stop-opacity='0.6'/%3E%3Cstop offset='1' stop-color='%2390caf9' stop-opacity='0.1'/%3E%3C/linearGradient%3E%3C/defs%3E%3C!-- top wave --%3E%3Cpath d='M0,220 C180,100 380,340 680,200 C980,60 1200,300 1440,180 L1440,0 L0,0 Z' fill='url(%23g1)'/%3E%3C!-- bottom wave --%3E%3Cpath d='M0,680 C240,560 480,780 780,640 C1080,500 1280,720 1440,600 L1440,900 L0,900 Z' fill='url(%23g2)'/%3E%3C!-- mid flowing band --%3E%3Cpath d='M0,460 C200,370 440,570 720,440 C1000,310 1240,510 1440,400 L1440,480 C1240,590 1000,390 720,520 C440,650 200,450 0,540 Z' fill='url(%23g3)'/%3E%3C!-- fine stroke lines --%3E%3Cpath d='M0,340 C220,260 460,440 740,320 C1020,200 1260,400 1440,300' stroke='rgba(100,181,246,0.35)' stroke-width='2.5' fill='none'/%3E%3Cpath d='M0,560 C260,470 520,660 800,530 C1080,400 1300,590 1440,490' stroke='rgba(144,202,249,0.25)' stroke-width='1.8' fill='none'/%3E%3Cpath d='M0,160 C300,90 580,250 880,140 C1180,30 1360,200 1440,130' stroke='rgba(187,222,251,0.4)' stroke-width='1.5' fill='none'/%3E%3C!-- glowing blobs --%3E%3Ccircle cx='120' cy='120' r='160' fill='rgba(144,202,249,0.18)'/%3E%3Ccircle cx='1320' cy='780' r='200' fill='rgba(100,181,246,0.14)'/%3E%3Ccircle cx='720' cy='460' r='130' fill='rgba(187,222,251,0.12)'/%3E%3C/svg%3E");
    background-size: cover;
    background-position: center top;
}

/* Everything sits above the pseudo-element */
.stApp > * { position: relative; z-index: 1; }

#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── NAV — frosted glass ── */
.cw-nav {
    background: rgba(255,255,255,0.82);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(144,202,249,0.45);
    padding: 0 3rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 70px;
    position: sticky; top: 0; z-index: 999;
    box-shadow: 0 2px 24px rgba(0,80,200,0.08);
}
.cw-logo-text {
    font-family: 'Merriweather', serif;
    font-size: 1.45rem;
    font-weight: 900;
    color: #003399;
    letter-spacing: -0.02em;
}
.cw-logo-text span { color: #e53e3e; }
.cw-tagline {
    font-size: 0.7rem;
    color: #64748b;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-top: 1px;
}

/* ── Remove Streamlit default top gap inside columns — fixes nav alignment ── */
div[data-testid="stColumn"] {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}
div[data-testid="stColumn"] > div[data-testid="stVerticalBlockBorderWrapper"]
  > div > div[data-testid="stVerticalBlock"] {
    gap: 0rem !important;
    padding-top: 0 !important;
}

/* ── Nav buttons — uniform height, auto width ── */
div[data-testid="stButton"] > button {
    border-radius: 6px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.18s ease !important;
    padding: 0 1.1rem !important;
    height: 38px !important;
    line-height: 38px !important;
    white-space: nowrap !important;
    width: fit-content !important;
    min-width: unset !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: #003399 !important;
    color: #fff !important;
    border: none !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #002277 !important;
    box-shadow: 0 4px 14px rgba(0,51,153,0.35) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(255,255,255,0.75) !important;
    color: #334155 !important;
    border: 1px solid rgba(144,202,249,0.55) !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(227,242,253,0.9) !important;
    border-color: #64b5f6 !important;
}

/* Inputs */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    border-radius: 8px !important;
    border: 1.5px solid rgba(144,202,249,0.6) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important;
    background: rgba(255,255,255,0.88) !important;
    color: #1a2540 !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color: #003399 !important;
    box-shadow: 0 0 0 3px rgba(0,51,153,0.1) !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
}
div[data-testid="stSelectbox"] > div > div {
    border-radius: 8px !important;
    border: 1.5px solid rgba(144,202,249,0.6) !important;
    background: rgba(255,255,255,0.88) !important;
}
div[data-testid="stAlert"] { border-radius: 10px !important; }
div[data-testid="stForm"] { border: none !important; padding: 0 !important; }
div[data-testid="stSlider"] > div { color: #003399 !important; }

hr { border: none; border-top: 1px solid rgba(144,202,249,0.4); margin: 0; }

/* Glass card utility */
.cw-card {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 16px;
    border: 1px solid rgba(144,202,249,0.4);
    padding: 2rem;
    box-shadow: 0 4px 24px rgba(0,80,200,0.07);
}

.section-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #003399;
    margin-bottom: 0.5rem;
}
.section-title {
    font-family: 'Merriweather', serif;
    font-size: 2rem;
    font-weight: 900;
    color: #1a2540;
    line-height: 1.25;
    margin-bottom: 0.9rem;
}

/* ── Auth gate overlay ── */
.auth-gate {
    text-align: center;
    padding: 5rem 2rem 4rem;
    max-width: 480px;
    margin: 0 auto;
}
.auth-gate-icon { font-size: 4rem; margin-bottom: 1.2rem; }
.auth-gate h2 {
    font-family: 'Merriweather', serif;
    font-size: 1.6rem; font-weight: 900;
    color: #1a2540; margin: 0 0 0.6rem;
}
.auth-gate p {
    font-size: 0.96rem; color: #475569;
    line-height: 1.7; margin: 0 0 2rem;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──
for k, v in [("page", "home"), ("form_data", {}), ("logged_in", False), ("username", ""), ("user_email", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Pages that require login ──
PROTECTED_PAGES = {"calculator", "dashboard"}

# ── Public pages (no login needed) ──
PUBLIC_PAGES = {"home", "about", "contact", "feedback", "login", "signup"}

# ── Auth guard: redirect to login if trying to access a protected page ──
if st.session_state.page in PROTECTED_PAGES and not st.session_state.logged_in:
    # Store where they were trying to go so we can redirect after login
    st.session_state["_redirect_after_login"] = st.session_state.page
    st.session_state.page = "_auth_gate"

# ── NAVBAR — single flat row so all buttons share the same baseline ──
active = st.session_state.page

if st.session_state.logged_in:
    (col_logo, c1, c2, c3, c4, c5, c6,
     _gap, col_user, col_logout) = st.columns([2.2, 1.15, 1.25, 1.25, 1.0, 1.1, 1.1, 0.3, 1.5, 1.0])
else:
    (col_logo, c1, c2, c3, c4, c5, c6,
     _gap, col_login, col_signup) = st.columns([2.2, 1.15, 1.25, 1.25, 1.0, 1.1, 1.1, 0.3, 1.0, 1.0])

col_logo.markdown("""
<div style="display:flex;flex-direction:column;justify-content:center;
            min-height:52px;padding-left:0.5rem;">
    <div class="cw-logo-text">Credi<span>wise</span></div>
    <div class="cw-tagline">AI Loan Intelligence · India</div>
</div>
""", unsafe_allow_html=True)

pages = [
    ("🏠 Home",       "home"),
    ("🧮 Calculator", "calculator"),
    ("📊 Dashboard",  "dashboard"),
    ("ℹ️ About",      "about"),
    ("📞 Contact",    "contact"),
    ("💬 Feedback",   "feedback"),
]
for col, (label, pg) in zip([c1, c2, c3, c4, c5, c6], pages):
    t = "primary" if active == pg else "secondary"
    if col.button(label, key=f"nav_{pg}", use_container_width=True, type=t):
        if pg in PROTECTED_PAGES and not st.session_state.logged_in:
            st.session_state["_redirect_after_login"] = pg
            st.session_state.page = "_auth_gate"
        else:
            st.session_state.page = pg
        st.rerun()

if st.session_state.logged_in:
    col_user.markdown(
        f"<div style='display:flex;align-items:center;justify-content:flex-end;"
        f"height:100%;min-height:38px;font-size:0.82rem;font-weight:600;"
        f"color:#003399;white-space:nowrap;'>👤 {st.session_state.username}</div>",
        unsafe_allow_html=True,
    )
    if col_logout.button("Logout", key="nav_logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "home"
        st.rerun()
else:
    if col_login.button("Login", key="nav_login", use_container_width=True, type="secondary"):
        st.session_state.page = "login"
        st.rerun()
    if col_signup.button("Sign Up", key="nav_signup", use_container_width=True, type="primary"):
        st.session_state.page = "signup"
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ── ROUTING ──
pg = st.session_state.page

if pg == "_auth_gate":
    # ── Friendly auth gate screen ──
    destination = st.session_state.get("_redirect_after_login", "calculator")
    dest_label = {"calculator": "Loan Calculator", "dashboard": "Dashboard"}.get(destination, destination.capitalize())

    st.markdown(f"""
    <div class="auth-gate">
        <div class="auth-gate-icon">🔐</div>
        <h2>Sign In to Continue</h2>
        <p>
            The <strong>{dest_label}</strong> is available to registered users only.
            Create a free account or log in to access your personalised loan analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, btn_col1, btn_col2, _ = st.columns([2, 1.2, 1.2, 2])
    with btn_col1:
        if st.button("Login →", use_container_width=True, type="primary", key="gate_login"):
            st.session_state.page = "login"
            st.rerun()
    with btn_col2:
        if st.button("Sign Up Free", use_container_width=True, key="gate_signup"):
            st.session_state.page = "signup"
            st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:1.5rem;">
        <span style="font-size:0.82rem;color:#94a3b8;">
            🔒 Free forever &nbsp;·&nbsp; No credit impact &nbsp;·&nbsp; 60-second setup
        </span>
    </div>
    """, unsafe_allow_html=True)

elif pg == "home":
    from pages.home import show; show()
elif pg == "calculator":
    from pages.calculator import show; show()
elif pg == "dashboard":
    from pages.dashboard import show; show()
elif pg == "about":
    from pages.about import show; show()
elif pg == "contact":
    from pages.contact import show; show()
elif pg == "feedback":
    from pages.feedback import show; show()
elif pg == "login":
    from pages.login import show; show()
elif pg == "signup":
    from pages.signup import show; show()
