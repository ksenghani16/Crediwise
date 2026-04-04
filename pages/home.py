import streamlit as st


def show():
    st.markdown("""
    <style>
    /* ── Hero ── */
    .hero {
        position: relative;
        border-radius: 28px;
        overflow: hidden;
        padding: 5rem 3rem 4rem;
        text-align: center;
        margin-bottom: 2.8rem;
        background: linear-gradient(145deg, #0d1830 0%, #0a1228 55%, #0f1e38 100%);
        border: 1px solid var(--card-border);
    }
    .hero-grid {
        position: absolute; inset: 0;
        background-image:
            linear-gradient(rgba(91,124,250,0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(91,124,250,0.08) 1px, transparent 1px);
        background-size: 52px 52px;
        mask-image: radial-gradient(ellipse 80% 70% at 50% 50%, black 30%, transparent 100%);
    }
    .hero-glow-l {
        position: absolute; top: -20%; left: -8%;
        width: 520px; height: 520px; border-radius: 50%;
        background: radial-gradient(circle, rgba(91,124,250,0.20) 0%, transparent 65%);
        pointer-events: none;
    }
    .hero-glow-r {
        position: absolute; bottom: -15%; right: -5%;
        width: 400px; height: 400px; border-radius: 50%;
        background: radial-gradient(circle, rgba(6,214,199,0.16) 0%, transparent 65%);
        pointer-events: none;
    }
    .hero-pill {
        display: inline-flex; align-items: center; gap: 0.5rem;
        background: rgba(91,124,250,0.14);
        border: 1px solid rgba(91,124,250,0.35);
        color: #8fa8ff;
        border-radius: 100px;
        padding: 0.38rem 1.1rem;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        margin-bottom: 1.6rem;
        position: relative; z-index: 1;
    }
    .hero-pill::before {
        content: '';
        width: 7px; height: 7px; border-radius: 50%;
        background: var(--cyan);
        animation: pulse-dot 1.8s infinite;
        flex-shrink: 0;
    }
    @keyframes pulse-dot {
        0%,100% { opacity:1; transform:scale(1); }
        50%      { opacity:0.35; transform:scale(0.65); }
    }
    .hero h1 {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2.4rem, 5vw, 3.8rem);
        font-weight: 800;
        line-height: 1.12;
        color: var(--text-pri);
        margin: 0 0 1.3rem;
        position: relative; z-index: 1;
        letter-spacing: -0.03em;
    }
    .hero h1 .grad {
        background: linear-gradient(90deg, #5b7cfa, #06d6c7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p {
        font-size: 1.08rem;
        color: #94a3b8;
        max-width: 520px;
        margin: 0 auto 2.8rem;
        line-height: 1.75;
        position: relative; z-index: 1;
    }
    .hero-stats {
        display: flex; justify-content: center; gap: 3.5rem;
        position: relative; z-index: 1;
        margin-top: 3rem;
        padding-top: 2.2rem;
        border-top: 1px solid rgba(255,255,255,0.07);
    }
    .hero-stat-val {
        font-family: 'Syne', sans-serif;
        font-size: 2rem; font-weight: 800;
        background: linear-gradient(135deg, #5b7cfa, #06d6c7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    .hero-stat-lbl {
        font-size: 0.78rem; color: #4b6080;
        margin-top: 0.4rem;
        text-transform: uppercase; letter-spacing: 0.08em;
        font-weight: 600;
    }

    /* ── Feature cards ── */
    .feat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.3rem; margin-bottom: 2.5rem; }
    .feat-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 20px;
        padding: 1.7rem 1.5rem;
        transition: all 0.25s ease;
    }
    .feat-card:hover {
        border-color: rgba(91,124,250,0.45);
        transform: translateY(-5px);
        box-shadow: 0 14px 40px rgba(0,0,0,0.35);
        background: var(--card-hover);
    }
    .feat-icon {
        width: 50px; height: 50px; border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.4rem; margin-bottom: 1.1rem;
    }
    .feat-card h4 {
        font-family: 'Syne', sans-serif;
        font-size: 1rem; font-weight: 700;
        color: var(--text-pri); margin: 0 0 0.45rem;
    }
    .feat-card p { font-size: 0.855rem; color: #94a3b8; line-height: 1.6; margin: 0; }

    /* ── How it works ── */
    .how-wrap {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 24px;
        padding: 2.5rem 2.2rem;
        margin-bottom: 1.8rem;
    }
    .how-wrap h3 {
        font-family: 'Syne', sans-serif;
        font-size: 1.45rem; font-weight: 700;
        color: var(--text-pri); text-align: center;
        margin: 0 0 2.2rem;
    }
    .steps-row { display: flex; gap: 0; align-items: flex-start; }
    .step-item { flex: 1; text-align: center; position: relative; }
    .step-item:not(:last-child)::after {
        content: '';
        position: absolute; top: 23px; left: 64%; right: -36%;
        height: 2px;
        background: linear-gradient(90deg, rgba(91,124,250,0.6), rgba(91,124,250,0.05));
    }
    .step-num {
        width: 48px; height: 48px; border-radius: 50%;
        background: linear-gradient(135deg, var(--indigo), #6a3de8);
        display: flex; align-items: center; justify-content: center;
        font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1rem;
        color: #ffffff; margin: 0 auto 0.9rem;
        box-shadow: 0 4px 18px rgba(91,124,250,0.45);
    }
    .step-item h5 {
        font-family: 'Syne', sans-serif; font-weight: 700;
        color: var(--text-pri); margin: 0 0 0.35rem; font-size: 0.95rem;
    }
    .step-item p { font-size: 0.83rem; color: #94a3b8; margin: 0; line-height: 1.5; }

    /* ── Trust bar ── */
    .trust-bar {
        display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 1.5rem 2.5rem;
        background: var(--card-bg); border: 1px solid var(--card-border);
        border-radius: 16px; padding: 1.3rem 2rem;
        margin-top: 1.5rem;
    }
    .trust-item {
        display: flex; align-items: center; gap: 0.5rem;
        font-size: 0.87rem; color: #94a3b8; font-weight: 500;
    }
    .trust-item .ico { font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ──
    st.markdown("""
    <div class="hero">
        <div class="hero-grid"></div>
        <div class="hero-glow-l"></div>
        <div class="hero-glow-r"></div>
        <div class="hero-pill">AI-Powered · India's Loan Intelligence Platform</div>
        <h1>Know Before You <span class="grad">Borrow</span></h1>
        <p>Get your personalised loan risk score, stress timeline, and smarter alternatives — all in under 60 seconds.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        if st.button("🚀  Analyze My Loan", use_container_width=True, type="primary"):
            st.session_state.page = "calculator"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Feature cards ──
    st.markdown("""
    <div class="feat-grid">
        <div class="feat-card">
            <div class="feat-icon" style="background:rgba(91,124,250,0.14);">🧠</div>
            <h4>AI Risk Score</h4>
            <p>Multi-factor risk model assessing your probability of financial stress with transparent scoring.</p>
        </div>
        <div class="feat-card">
            <div class="feat-icon" style="background:rgba(6,214,199,0.12);">📉</div>
            <h4>Stress Timeline</h4>
            <p>Visualise how your savings trajectory shifts with and without the loan over time.</p>
        </div>
        <div class="feat-card">
            <div class="feat-icon" style="background:rgba(251,191,36,0.12);">🔍</div>
            <h4>Explainable AI</h4>
            <p>Plain-language breakdown of every factor driving your risk score — no black boxes.</p>
        </div>
        <div class="feat-card">
            <div class="feat-icon" style="background:rgba(16,217,160,0.12);">💡</div>
            <h4>Smart Negotiation</h4>
            <p>AI-suggested safer loan plans tailored to your specific financial profile.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── How it works ──
    st.markdown("""
    <div class="how-wrap">
        <h3>How It Works</h3>
        <div class="steps-row">
            <div class="step-item">
                <div class="step-num">1</div>
                <h5>Enter Income</h5>
                <p>Share your monthly income, expenses & existing debt.</p>
            </div>
            <div class="step-item">
                <div class="step-num">2</div>
                <h5>Set Loan Terms</h5>
                <p>Define loan amount, tenure & interest rate.</p>
            </div>
            <div class="step-item">
                <div class="step-num">3</div>
                <h5>Get Analysis</h5>
                <p>Receive your AI risk score & full affordability report.</p>
            </div>
            <div class="step-item">
                <div class="step-num">4</div>
                <h5>Decide Smartly</h5>
                <p>Choose the best plan with full confidence.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Trust bar ──
    st.markdown("""
    <div class="trust-bar">
        <div class="trust-item"><span class="ico">🔒</span> Bank-grade Security</div>
        <div class="trust-item"><span class="ico">📊</span> Data-driven Insights</div>
        <div class="trust-item"><span class="ico">⚡</span> Instant Results</div>
        <div class="trust-item"><span class="ico">🇮🇳</span> Built for India</div>
        <div class="trust-item"><span class="ico">✅</span> RBI Compliant Norms</div>
    </div>
    """, unsafe_allow_html=True)
