import streamlit as st


def show():
    st.markdown("""
    <style>
    /* ── HERO ── */
    .hero-left {
        background:
            radial-gradient(ellipse 80% 60% at 20% 30%, rgba(0,80,200,0.18) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 80%, rgba(0,40,140,0.12) 0%, transparent 55%),
            linear-gradient(140deg, #002b80 0%, #0038b8 40%, #0048cc 70%, #0055dd 100%);
        padding: 4.5rem 3.5rem;
        min-height: 520px;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .hero-left .dots {
        position: absolute; inset: 0; pointer-events: none;
        background-image: radial-gradient(rgba(255,255,255,0.07) 1px, transparent 1px);
        background-size: 28px 28px;
    }
    .hero-left .blob1 {
        position:absolute; top:-80px; right:-80px;
        width:300px; height:300px; border-radius:50%;
        background:radial-gradient(circle,rgba(255,255,255,0.07) 0%,transparent 70%);
        pointer-events:none;
    }
    .hero-left .blob2 {
        position:absolute; bottom:-60px; left:30px;
        width:200px; height:200px; border-radius:50%;
        background:radial-gradient(circle,rgba(100,180,255,0.1) 0%,transparent 70%);
        pointer-events:none;
    }
    .hero-pill {
        display:inline-flex; align-items:center; gap:0.45rem;
        background:rgba(255,255,255,0.13); border:1px solid rgba(255,255,255,0.28);
        color:rgba(255,255,255,0.95); border-radius:100px;
        padding:0.35rem 1.1rem; font-size:0.73rem; font-weight:700;
        letter-spacing:0.09em; text-transform:uppercase;
        margin-bottom:1.6rem; width:fit-content; backdrop-filter:blur(6px);
        position:relative;
    }
    .hero-h1 {
        font-family:'Merriweather',serif;
        font-size:clamp(2rem,3.2vw,3.1rem); font-weight:900;
        color:#fff; line-height:1.2; margin:0 0 1.2rem;
        letter-spacing:-0.02em; position:relative;
    }
    .hero-h1 .hl { color:#7dd3fc; position:relative; display:inline-block; }
    .hero-h1 .hl::after {
        content:''; position:absolute; left:0; bottom:-4px;
        width:100%; height:3px;
        background:linear-gradient(90deg,#7dd3fc,#38bdf8); border-radius:2px;
    }
    .hero-sub {
        color:rgba(255,255,255,0.82); font-size:0.97rem; line-height:1.75;
        max-width:480px; margin:0 0 2rem; position:relative;
    }
    .hero-badges { display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:2.2rem; position:relative; }
    .hero-badge {
        display:inline-flex; align-items:center; gap:0.35rem;
        background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2);
        color:rgba(255,255,255,0.9); border-radius:8px;
        padding:0.28rem 0.7rem; font-size:0.75rem; font-weight:600;
        backdrop-filter:blur(4px);
    }
    .hero-stats {
        display:flex; gap:2rem; flex-wrap:wrap;
        padding-top:1.6rem; border-top:1px solid rgba(255,255,255,0.15);
        position:relative;
    }
    .hero-stat-val {
        font-family:'Merriweather',serif; font-size:1.35rem; font-weight:900;
        color:#7dd3fc; line-height:1;
    }
    .hero-stat-lbl { font-size:0.72rem; color:rgba(255,255,255,0.6); font-weight:600; margin-top:3px; }

    /* Right side: calculator */
    .calc-panel {
        background:rgba(255,255,255,0.72);
        backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
        border-left:1px solid rgba(144,202,249,0.35);
        padding:1.4rem 2rem;
        display:flex; flex-direction:column; justify-content:center;
    }
    .calc-heading {
        font-family:'Merriweather',serif; font-weight:900;
        font-size:1.1rem; color:#1a2540; margin:0 0 0.25rem;
    }
    .calc-sub { font-size:0.82rem; color:#64748b; margin:0 0 0.8rem; }
    .calc-rule {
        height:2px;
        background:linear-gradient(90deg,#003399,#90caf9,transparent);
        border-radius:2px; margin-bottom:1.4rem;
    }
    .emi-result {
        background:linear-gradient(135deg,#e8f4fd,#dbeafe);
        border:1px solid rgba(144,202,249,0.5);
        border-radius:14px; padding:1.1rem 1.4rem; margin:0.6rem 0 1.2rem;
    }
    .emi-label { font-size:0.7rem; color:#64748b; font-weight:700;
                 text-transform:uppercase; letter-spacing:0.07em; margin-bottom:4px; }
    .emi-amount {
        font-family:'Merriweather',serif; font-size:2rem;
        font-weight:900; color:#003399; line-height:1;
    }
    .emi-detail { font-size:0.79rem; color:#64748b; margin-top:2px; }
    .emi-detail strong { color:#1a2540; }
    .emi-detail .red { color:#e53e3e; }

    /* Trust marquee */
    .trust-wrap {
        background:linear-gradient(90deg,#002b80,#003399);
        color:#fff; padding:0.75rem 2rem;
        font-size:0.82rem; font-weight:600; letter-spacing:0.04em;
        overflow:hidden; white-space:nowrap;
    }
    .trust-inner { display:inline-block; animation:marquee 22s linear infinite; }
    @keyframes marquee { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }

    /* Stats strip */
    .stat-strip {
        background:rgba(255,255,255,0.65); backdrop-filter:blur(12px);
        border-bottom:1px solid rgba(144,202,249,0.35);
        padding:1.4rem 3rem; display:flex; align-items:center; gap:3rem; flex-wrap:wrap;
    }
    .stat-item { text-align:center; }
    .stat-val { font-family:'Merriweather',serif; font-size:1.6rem; font-weight:900; color:#003399; line-height:1; }
    .stat-lbl { font-size:0.78rem; color:#64748b; font-weight:600; margin-top:3px; }
    .stat-div { width:1px; height:40px; background:rgba(144,202,249,0.5); }

    /* Product cards */
    .prod-card {
        background:rgba(255,255,255,0.78); backdrop-filter:blur(12px);
        border:1.5px solid rgba(144,202,249,0.4); border-radius:18px;
        padding:2rem 1.6rem; transition:all 0.22s ease; height:100%;
    }
    .prod-card:hover {
        border-color:#003399; box-shadow:0 12px 40px rgba(0,51,153,0.14);
        transform:translateY(-4px); background:rgba(255,255,255,0.92);
    }
    .prod-icon { width:56px; height:56px; border-radius:14px;
                 display:flex; align-items:center; justify-content:center;
                 font-size:1.6rem; margin-bottom:1.1rem; }
    .prod-card h4 { font-family:'Merriweather',serif; font-size:1.05rem;
                    font-weight:700; color:#1a2540; margin:0 0 0.5rem; }
    .prod-card p { font-size:0.86rem; color:#64748b; line-height:1.65; margin:0 0 1rem; }
    .prod-card ul { padding-left:1.1rem; margin:0 0 1.4rem; }
    .prod-card ul li { font-size:0.84rem; color:#475569; line-height:1.8; }
    .prod-rate { font-size:0.78rem; color:#64748b; font-weight:600;
                 border-top:1px solid rgba(144,202,249,0.35); padding-top:0.8rem; margin-top:0.4rem; }
    .prod-rate strong { color:#003399; font-size:1rem; }

    /* Steps */
    .step-card {
        background:rgba(255,255,255,0.78); backdrop-filter:blur(12px);
        border-radius:16px; border:1px solid rgba(144,202,249,0.4);
        padding:2rem 1.5rem; text-align:center;
    }
    .step-num {
        width:48px; height:48px; border-radius:50%;
        background:linear-gradient(135deg,#003399,#0040cc); color:#fff;
        font-family:'Merriweather',serif; font-weight:900; font-size:1.1rem;
        display:flex; align-items:center; justify-content:center;
        margin:0 auto 1rem; box-shadow:0 4px 14px rgba(0,51,153,0.3);
    }
    .step-card h5 { font-family:'Merriweather',serif; font-size:0.95rem;
                    font-weight:700; color:#1a2540; margin:0 0 0.4rem; }
    .step-card p { font-size:0.83rem; color:#64748b; margin:0; line-height:1.55; }

    /* Testimonial */
    .testi-card {
        background:rgba(255,255,255,0.78); backdrop-filter:blur(12px);
        border-radius:16px; border:1px solid rgba(144,202,249,0.4);
        padding:1.8rem; height:100%;
    }
    .testi-stars { color:#f59e0b; font-size:1rem; margin-bottom:0.7rem; }
    .testi-card blockquote { font-size:0.92rem; color:#334155; line-height:1.7; margin:0 0 1.2rem; font-style:italic; }
    .testi-author { font-size:0.82rem; font-weight:700; color:#1a2540; }
    .testi-loc    { font-size:0.78rem; color:#64748b; }

    /* CTA */
    .cta-banner {
        background:linear-gradient(120deg,#002b80,#003399); border-radius:22px;
        padding:3.5rem; text-align:center; color:#fff;
        margin:2rem 3rem 3rem; position:relative; overflow:hidden;
        box-shadow:0 8px 40px rgba(0,51,153,0.25);
    }
    .cta-banner h2 { font-family:'Merriweather',serif; font-size:2rem; font-weight:900; margin:0 0 0.8rem; }
    .cta-banner p  { color:rgba(255,255,255,0.82); font-size:1rem; margin:0 0 2rem; }
    </style>
    """, unsafe_allow_html=True)

    # ── HERO ──
    hero_l, hero_r = st.columns([1.1, 0.9])

    with hero_l:
        st.markdown("""
        <div class="hero-left">
            <div class="dots"></div>
            <div class="blob1"></div>
            <div class="blob2"></div>
            <div class="hero-pill">✦ AI-Powered · India's Loan Intelligence</div>
            <h1 class="hero-h1">Know Before<br>You <span class="hl">Borrow</span></h1>
            <p class="hero-sub">
                Get your personalised loan risk score, EMI forecast, and AI-suggested
                safer alternatives — all in under 60 seconds. No paperwork. No hassle.
            </p>
            <div class="hero-badges">
                <span class="hero-badge">⚡ 60-Second Report</span>
                <span class="hero-badge">🔒 No CIBIL Impact</span>
                <span class="hero-badge">🆓 100% Free</span>
                <span class="hero-badge">🤖 AI-Powered</span>
            </div>
           
        </div>
        """, unsafe_allow_html=True)

    with hero_r:
        st.markdown("""
        <div class="calc-panel">
            <div class="calc-heading">⚡ Quick EMI Calculator</div>
            <div class="calc-sub">Instant estimate — no sign-up needed</div>
            <div class="calc-rule"></div>
        """, unsafe_allow_html=True)

        loan_q   = st.number_input("Loan Amount (₹)", min_value=10000, max_value=10000000, value=500000, step=10000, key="q_loan")
        rate_q   = st.number_input("Interest Rate (% p.a.)", min_value=5.0, max_value=30.0, value=10.5, step=0.5, key="q_rate")
        tenure_q = st.select_slider("Tenure (months)", options=[12,24,36,48,60,72,84,96,120], value=36, key="q_tenure")

        r = (rate_q/100)/12; n = tenure_q
        emi_q = loan_q * r * (1+r)**n / ((1+r)**n - 1)
        total_q = emi_q * n; interest_q = total_q - loan_q

        st.markdown(f"""
        <div class="emi-result">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
                <div>
                    <div class="emi-label">Monthly EMI</div>
                    <div class="emi-amount">₹{emi_q:,.0f}</div>
                </div>
                <div style="text-align:right;">
                    <div class="emi-detail">Total &nbsp;<strong>₹{total_q:,.0f}</strong></div>
                    <div class="emi-detail"><span class="red">Interest &nbsp;<strong>₹{interest_q:,.0f}</strong></span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Get Full Analysis →", use_container_width=True, type="primary", key="hero_cta"):
            st.session_state.form_data.update({"loan_amount": loan_q, "interest_rate": rate_q, "tenure": tenure_q})
            st.session_state.page = "calculator"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Trust marquee ──
    st.markdown("""
    <div class="trust-wrap"><div class="trust-inner">
        &nbsp;&nbsp;🔒 Bank-grade Security &nbsp;·&nbsp; ✅ RBI Compliant Norms &nbsp;·&nbsp;
        ⭐ 12,400+ Loans Analysed &nbsp;·&nbsp; ⚡ 60-Second Results &nbsp;·&nbsp;
        🇮🇳 Built for India &nbsp;·&nbsp; 📊 85%+ Model Accuracy &nbsp;·&nbsp;
        🔒 Bank-grade Security &nbsp;·&nbsp; ✅ RBI Compliant Norms &nbsp;·&nbsp;
        ⭐ 12,400+ Loans Analysed &nbsp;·&nbsp; ⚡ 60-Second Results &nbsp;·&nbsp;
        🇮🇳 Built for India &nbsp;·&nbsp; 📊 85%+ Model Accuracy &nbsp;&nbsp;
    </div></div>
    """, unsafe_allow_html=True)

    # ── Stats strip ──
 

    # ── Products ──
    st.markdown("""
    <div style="padding:3.5rem 3rem 1rem;">
        <div class="section-label">Our Services</div>
        <div class="section-title">Check Eligibility for Any Loan</div>
    </div>
    """, unsafe_allow_html=True)

    products = [
        ("🏠","#eff6ff","Personal Loan","Instant funds for any personal need.",
         ["Loan up to ₹40,00,000","No collateral needed","Approval in 24 hrs","Flexible tenure 12–84 months"],"10.5% p.a."),
        ("🏡","#f0fdf4","Home Loan","Make your dream home a reality.",
         ["Loan up to ₹5 Crore","Tenure up to 30 years","Balance transfer option","Tax benefits u/s 80C"],"7.9% p.a."),
        ("🚗","#fff7ed","Car Loan","Drive your dream car with easy EMIs.",
         ["Up to 100% on-road funding","New & used cars","Tenure up to 7 years","Quick approval"],"8.5% p.a."),
        ("🎓","#fdf4ff","Education Loan","Invest in your future.",
         ["Up to ₹1.5 Crore","Study in India or abroad","Moratorium period","Subsidy schemes eligible"],"9.0% p.a."),
    ]
    c1,c2,c3,c4 = st.columns(4)
    for col,(icon,bg,title,desc,bullets,rate) in zip([c1,c2,c3,c4],products):
        with col:
            bul_html = "".join(f"<li>{b}</li>" for b in bullets)
            st.markdown(f"""
            <div class="prod-card">
                <div class="prod-icon" style="background:{bg};">{icon}</div>
                <h4>{title}</h4><p>{desc}</p>
                <ul>{bul_html}</ul>
                <div class="prod-rate">Rate from <strong>{rate}</strong> onwards</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Check Eligibility", key=f"prod_{title}", use_container_width=True, type="primary"):
                st.session_state.form_data["loan_type"] = title
                st.session_state.page = "calculator"; st.rerun()

    # ── How It Works ──
    st.markdown("""
    <div style="background:rgba(255,255,255,0.45);backdrop-filter:blur(12px);
                margin:2rem 0;padding:3.5rem 3rem;
                border-top:1px solid rgba(144,202,249,0.35);
                border-bottom:1px solid rgba(144,202,249,0.35);">
        <div style="text-align:center;margin-bottom:2.5rem;">
            <div class="section-label">Simple Process</div>
            <div class="section-title" style="text-align:center;">How It Works</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    s1,a1,s2,a2,s3,a3,s4 = st.columns([4,1,4,1,4,1,4])
    steps = [("1","Enter Income","Share monthly income, expenses & existing EMIs."),
             ("2","Set Loan Terms","Define loan amount, tenure & interest rate."),
             ("3","AI Analyses","Our ML model blends with rule engine to score risk."),
             ("4","Get Report","Receive full affordability report & smart alternatives.")]
    for col,(num,title,desc) in zip([s1,s2,s3,s4],steps):
        with col:
            st.markdown(f"""<div class="step-card">
                <div class="step-num">{num}</div><h5>{title}</h5><p>{desc}</p>
            </div>""", unsafe_allow_html=True)
    for col in [a1,a2,a3]:
        with col:
            st.markdown("<div style='text-align:center;padding-top:1.4rem;font-size:1.5rem;color:#90caf9;'>→</div>", unsafe_allow_html=True)

    # ── Testimonials ──
    st.markdown("""
    <div style="padding:3.5rem 3rem 1rem;">
        <div class="section-label">Customer Stories</div>
        <div class="section-title">What Our Users Say</div>
    </div>
    """, unsafe_allow_html=True)

    t1,t2,t3 = st.columns(3)
    testis = [
        ("The AI risk score flagged my high debt ratio before I committed to more EMI. Truly a lifesaver.","Priya M.","Mumbai, Maharashtra"),
        ("I finally understood exactly why my loan was borderline — and got a roadmap to fix it.","Rohan S.","Bangalore, Karnataka"),
        ("It suggested a lower amount over a longer tenure. My monthly EMI dropped by ₹4,200 instantly!","Anjali K.","New Delhi"),
    ]
    for col,(body,name,loc) in zip([t1,t2,t3],testis):
        with col:
            st.markdown(f"""<div class="testi-card">
                <div class="testi-stars">⭐⭐⭐⭐⭐</div>
                <blockquote>"{body}"</blockquote>
                <div class="testi-author">{name}</div>
                <div class="testi-loc">{loc}</div>
            </div>""", unsafe_allow_html=True)

    # ── CTA ──
    st.markdown("""
    <div class="cta-banner">
        <h2>Ready to Check Your Loan Affordability?</h2>
        <p>Free. Instant. No sign-up required. Trusted by 12,400+ Indians.</p>
    </div>
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([2,1,2])
    with mid:
        if st.button("🚀 Analyse My Loan Now", use_container_width=True, type="primary", key="bottom_cta"):
            st.session_state.page = "calculator"; st.rerun()

    # ── Footer ──
    st.markdown("""
    <div style="background:rgba(26,37,64,0.92);backdrop-filter:blur(16px);
                color:#94a3b8;padding:2.5rem 3rem;margin-top:2rem;
                display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
        <div>
            <div style="font-family:'Merriweather',serif;font-size:1.1rem;font-weight:900;color:#fff;margin-bottom:0.3rem;">Crediwise</div>
            <div style="font-size:0.8rem;">© 2025 Crediwise · AI Loan Intelligence · India</div>
        </div>
        <div style="font-size:0.8rem;display:flex;gap:2rem;flex-wrap:wrap;">
            <span>Privacy Policy</span><span>Terms of Use</span><span>RBI Disclosure</span><span>Grievance Redressal</span>
        </div>
        <div style="font-size:0.8rem;">✅ RBI Compliant &nbsp;·&nbsp; 🔒 256-bit SSL</div>
    </div>
    """, unsafe_allow_html=True)
