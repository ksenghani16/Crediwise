import streamlit as st

st.set_page_config(
    page_title="Crediwise — AI Loan Intelligence",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Import global styles ──
from utils.styles import GLOBAL_CSS, NAVBAR_CSS

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(NAVBAR_CSS, unsafe_allow_html=True)

# ── Session state defaults ──
if "page"      not in st.session_state: st.session_state.page      = "home"
if "form_data" not in st.session_state: st.session_state.form_data = {}

# ──────────────────────────────────────────────────
# NAVBAR
# ──────────────────────────────────────────────────
active = st.session_state.page

nav_left, nav_mid, nav_right = st.columns([3, 5, 4])

with nav_left:
    st.markdown("""
    <div class="cw-logo">
        Crediwise
        <span>AI Loan Intelligence · India</span>
    </div>
    """, unsafe_allow_html=True)

with nav_mid:
    n1, n2, n3 = st.columns(3)
    clicked_home = n1.button(
        "🏠  Home", key="nav_home", use_container_width=True,
        type="primary" if active == "home" else "secondary",
    )
    clicked_calc = n2.button(
        "🧮  Calculator", key="nav_calculator", use_container_width=True,
        type="primary" if active == "calculator" else "secondary",
    )
    clicked_dash = n3.button(
        "📊  Dashboard", key="nav_dashboard", use_container_width=True,
        type="primary" if active == "dashboard" else "secondary",
    )

    if clicked_home:
        st.session_state.page = "home"
        st.rerun()
    if clicked_calc:
        st.session_state.page = "calculator"
        st.rerun()
    if clicked_dash:
        st.session_state.page = "dashboard" if st.session_state.form_data.get("income") else "calculator"
        st.rerun()

with nav_right:
    has_data = bool(st.session_state.form_data.get("income") and st.session_state.form_data.get("loan_amount"))
    status_color = "#10d9a0" if has_data else "#4b6080"
    status_text  = "Analysis ready" if has_data else "No analysis yet"
    st.markdown(f"""
    <div style="text-align:right; padding-top:0.65rem;">
        <span style="font-size:0.78rem; color:{status_color}; font-weight:600;">● {status_text}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin:0.4rem 0 1.5rem; opacity:0.2;'>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────
# ROUTING
# ──────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    from pages.home import show
    show()

elif page == "calculator":
    from pages.calculator import show
    show()

elif page == "dashboard":
    from pages.dashboard import show
    show()
