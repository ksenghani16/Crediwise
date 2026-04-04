GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root {
    --navy:          #070d1a;
    --navy-mid:      #0d1424;
    --card-bg:       #111827;
    --card-border:   #1f2f47;
    --card-hover:    #1a2640;
    --indigo:        #5b7cfa;
    --indigo-lt:     #8fa8ff;
    --indigo-dk:     #3a56d4;
    --cyan:          #06d6c7;
    --amber:         #fbbf24;
    --rose:          #f87171;
    --green:         #10d9a0;
    --purple:        #a78bfa;
    --text-pri:      #f0f4ff;
    --text-sec:      #94a3b8;
    --text-muted:    #4b6080;
    --input-bg:      #0f1d30;
    --input-border:  #243550;
    --shadow-glow:   rgba(91,124,250,0.25);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--navy) !important;
    color: var(--text-pri) !important;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 0 2rem 4rem 2rem !important;
    max-width: 1320px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--navy); }
::-webkit-scrollbar-thumb { background: var(--card-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--indigo-dk); }

/* ── Number / Text Inputs ── */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: var(--input-bg) !important;
    border: 1.5px solid var(--input-border) !important;
    border-radius: 10px !important;
    color: var(--text-pri) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 0.9rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: var(--indigo) !important;
    box-shadow: 0 0 0 3px rgba(91,124,250,0.18) !important;
    outline: none !important;
}
div[data-testid="stNumberInput"] input::placeholder { color: var(--text-muted) !important; }

/* Number input step buttons */
div[data-testid="stNumberInput"] button {
    background: var(--input-bg) !important;
    border-color: var(--input-border) !important;
    color: var(--text-sec) !important;
}
div[data-testid="stNumberInput"] button:hover {
    background: var(--card-border) !important;
    color: var(--text-pri) !important;
}

/* ── Selectbox ── */
div[data-testid="stSelectbox"] > div > div {
    background: var(--input-bg) !important;
    border: 1.5px solid var(--input-border) !important;
    border-radius: 10px !important;
    color: var(--text-pri) !important;
    font-size: 0.95rem !important;
}
div[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--indigo) !important;
}

/* Dropdown menu */
ul[data-testid="stSelectboxVirtualDropdown"] {
    background: #0f1d30 !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li {
    color: var(--text-sec) !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] {
    background: rgba(91,124,250,0.15) !important;
    color: var(--text-pri) !important;
}

/* ── Slider ── */
div[data-testid="stSlider"] .st-bo { background: var(--indigo) !important; }
div[data-testid="stSlider"] .st-bp { background: var(--input-border) !important; }
div[data-testid="stSlider"] [data-testid="stThumbValue"] {
    color: var(--text-pri) !important;
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
}

/* ── Select Slider ── */
div[data-testid="stSelectSlider"] .st-bo { background: var(--indigo) !important; }
div[data-testid="stSelectSlider"] .st-bp { background: var(--input-border) !important; }

/* ── Labels ── */
label,
.stSelectbox label,
.stNumberInput label,
.stSlider label,
.stSelectSlider label {
    color: var(--text-sec) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    margin-bottom: 0.3rem !important;
}

/* ── Primary Button ── */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--indigo) 0%, #6a3de8 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.68rem 1.5rem !important;
    box-shadow: 0 4px 20px rgba(91,124,250,0.4) !important;
    transition: all 0.22s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(91,124,250,0.55) !important;
    background: linear-gradient(135deg, #6a8aff 0%, #7a4ef0 100%) !important;
}
div.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
}

/* ── Secondary Button ── */
div.stButton > button[kind="secondary"] {
    background: var(--input-bg) !important;
    border: 1.5px solid var(--input-border) !important;
    color: var(--text-sec) !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: var(--indigo) !important;
    color: var(--indigo-lt) !important;
    background: rgba(91,124,250,0.08) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card-bg) !important;
    border-radius: 14px !important;
    padding: 0.35rem !important;
    gap: 0.2rem !important;
    border: 1px solid var(--card-border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: var(--text-sec) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-pri) !important;
    background: rgba(255,255,255,0.04) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--indigo), #6a3de8) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(91,124,250,0.35) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 1.5rem 0 0 0 !important;
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 14px !important;
    padding: 1rem 1.2rem !important;
}
div[data-testid="stMetric"] label {
    text-transform: none !important;
    color: var(--text-sec) !important;
    font-size: 0.82rem !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.6rem !important;
    color: var(--text-pri) !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.82rem !important;
}

/* ── Alerts ── */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-width: 4px !important;
    font-size: 0.9rem !important;
    background: rgba(91,124,250,0.07) !important;
}

/* ── DataFrame ── */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--card-border) !important;
}
div[data-testid="stDataFrame"] th {
    background: var(--card-bg) !important;
    color: var(--text-sec) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
div[data-testid="stDataFrame"] td {
    color: var(--text-pri) !important;
    font-size: 0.88rem !important;
}

/* ── Divider ── */
hr { border-color: var(--card-border) !important; opacity: 0.6 !important; }

/* ── Plotly chart bg fix ── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── Streamlit column gap fix ── */
[data-testid="column"] { padding: 0 0.5rem !important; }

/* ── Hide ugly Streamlit forms border ── */
[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
}
</style>
"""

NAVBAR_CSS = """
<style>
.cw-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 0.8rem;
    border-bottom: 1px solid var(--card-border);
    margin-bottom: 2rem;
}
.cw-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #5b7cfa, #06d6c7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.cw-logo span {
    display: block;
    background: none;
    -webkit-text-fill-color: var(--text-muted);
    color: var(--text-muted);
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.1rem;
}
</style>
"""
