import streamlit as st

st.set_page_config(
    page_title="LoanAdvisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for the entire app
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
    
    * { font-family: 'DM Sans', sans-serif; }
    
    .stApp { background-color: #f8f7f4; }
    
    .main-header {
        background: white;
        padding: 1rem 2rem;
        border-bottom: 1px solid #e8e4df;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #e8e4df;
    }
    
    .risk-badge-high { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }
    .risk-badge-medium { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }
    .risk-badge-low { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }
    
    div[data-testid="stButton"] > button {
        background: #1a1a1a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        width: 100%;
    }
    div[data-testid="stButton"] > button:hover { background: #333; }
    
    .stNumberInput input { border-radius: 8px; border: 1.5px solid #e8e4df; }
    .stSelectbox select { border-radius: 8px; }
    
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Navigation
if "page" not in st.session_state:
    st.session_state.page = "home"
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    st.markdown("### 📈 LoanAdvisor")
with col2:
    if st.button("🏠 Home"):
        st.session_state.page = "home"
with col3:
    if st.button("🧮 Calculator"):
        st.session_state.page = "calculator"
with col4:
    if st.button("📊 Dashboard"):
        st.session_state.page = "dashboard"

st.divider()

# Route pages
if st.session_state.page == "home":
    from pages.home import show
    show()
elif st.session_state.page == "calculator":
    from pages.calculator import show
    show()
elif st.session_state.page == "dashboard":
    from pages.dashboard import show
    show()
