import streamlit as st


def show():
    st.markdown("""
    <style>
    .about-hero {
        background: linear-gradient(120deg,#002b80,#003399 60%,#0040b3);
        padding: 4rem 3rem 3.5rem;
        color: #fff;
        position: relative;
        overflow: hidden;
    }
    .about-hero::after {
        content:'';
        position:absolute; right:-80px; top:-80px;
        width:400px; height:400px; border-radius:50%;
        background:rgba(255,255,255,0.05);
    }
    .about-hero h1 {
        font-family:'Merriweather',serif;
        font-size:clamp(1.8rem,4vw,3rem);
        font-weight:900; color:#fff; margin:0 0 1rem;
        line-height:1.2;
    }
    .about-hero p { font-size:1.05rem; color:rgba(255,255,255,0.8); max-width:560px; line-height:1.75; margin:0; }

    .value-card {
        background:#fff; border-radius:16px;
        border:1px solid #e2e8f0; padding:1.8rem;
        text-align:center; height:100%;
        transition: all 0.2s ease;
    }
    .value-card:hover { border-color:#003399; transform:translateY(-4px); box-shadow:0 10px 28px rgba(0,51,153,0.1); }
    .value-icon { font-size:2.2rem; margin-bottom:0.9rem; }
    .value-card h4 { font-family:'Merriweather',serif; font-size:1rem; font-weight:700; color:#1a2540; margin:0 0 0.5rem; }
    .value-card p  { font-size:0.84rem; color:#64748b; line-height:1.65; margin:0; }

    .team-card {
        background:#fff; border-radius:16px;
        border:1px solid #e2e8f0; padding:1.8rem 1.5rem;
        text-align:center; height:100%;
    }
    .team-avatar {
        width:72px; height:72px; border-radius:50%;
        background:linear-gradient(135deg,#003399,#0040cc);
        display:flex; align-items:center; justify-content:center;
        font-size:1.6rem; margin:0 auto 1rem;
    }
    .team-card h5 { font-family:'Merriweather',serif; font-size:0.95rem; font-weight:700; color:#1a2540; margin:0 0 0.2rem; }
    .team-card .role { font-size:0.8rem; color:#003399; font-weight:600; margin-bottom:0.5rem; }
    .team-card p  { font-size:0.82rem; color:#64748b; line-height:1.6; margin:0; }

    .timeline-item {
        display:flex; gap:1.5rem; align-items:flex-start;
        padding:1.5rem 0;
        border-bottom:1px solid #f1f5f9;
    }
    .tl-year {
        min-width:64px;
        font-family:'Merriweather',serif;
        font-size:1rem; font-weight:900; color:#003399;
    }
    .tl-dot {
        min-width:14px; height:14px; border-radius:50%;
        background:#003399; margin-top:4px;
        box-shadow:0 0 0 4px rgba(0,51,153,0.15);
    }
    .tl-content h5 { font-size:0.94rem; font-weight:700; color:#1a2540; margin:0 0 0.25rem; }
    .tl-content p  { font-size:0.84rem; color:#64748b; margin:0; line-height:1.55; }

    .award-chip {
        display:inline-flex; align-items:center; gap:0.5rem;
        background:#f0f5ff; border:1px solid #c7d7ff;
        border-radius:100px; padding:0.5rem 1.2rem;
        font-size:0.82rem; font-weight:600; color:#003399;
        margin:0.3rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ──
    st.markdown("""
    <div class="about-hero">
        <div style="font-size:0.75rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                    color:rgba(255,255,255,0.6); margin-bottom:0.8rem;">About Crediwise</div>
        <h1>Making Finance<br>Accessible to Every Indian</h1>
        <p>We are a technology-driven loan intelligence platform built to bring transparency,
           fairness, and AI-powered clarity to India's ₹22 lakh crore retail lending market.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Mission stats ──
   

    # ── Mission & Vision ──
    st.markdown("<div style='padding:3rem 3rem 1rem;'>", unsafe_allow_html=True)
    mv_l, mv_r = st.columns(2)
    with mv_l:
        st.markdown("""
        <div style='background:#f0f5ff; border-left:4px solid #003399; border-radius:0 16px 16px 0; padding:2rem;'>
            <div style='font-size:0.75rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                        color:#003399; margin-bottom:0.6rem;'>Our Mission</div>
            <p style='font-family:Merriweather,serif; font-size:1.05rem; font-weight:700; color:#1a2540;
                      line-height:1.5; margin:0;'>
                To democratise financial intelligence so every Indian can borrow confidently,
                safely, and on their own terms.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with mv_r:
        st.markdown("""
        <div style='background:#f0fdf4; border-left:4px solid #16a34a; border-radius:0 16px 16px 0; padding:2rem;'>
            <div style='font-size:0.75rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                        color:#16a34a; margin-bottom:0.6rem;'>Our Vision</div>
            <p style='font-family:Merriweather,serif; font-size:1.05rem; font-weight:700; color:#1a2540;
                      line-height:1.5; margin:0;'>
                A future where no Indian takes a loan they cannot afford — guided by transparent
                AI that explains every decision.
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Core Values ──
    st.markdown("""
    <div style='padding:2rem 3rem 1rem;'>
        <div class="section-label">What We Stand For</div>
        <div class="section-title">Our Core Values</div>
    </div>
    """, unsafe_allow_html=True)

    v1,v2,v3,v4 = st.columns(4)
    values = [
        ("🔍","Transparency","Every risk score comes with a plain-language explanation. No black boxes."),
        ("🤝","Fairness","Our AI is trained to be unbiased — your profile, not your postcode, determines your score."),
        ("⚡","Speed","60-second full analysis. Because financial decisions shouldn't wait."),
        ("🔒","Security","Bank-grade 256-bit SSL encryption. Your data is yours — always."),
    ]
    for col,(icon,title,desc) in zip([v1,v2,v3,v4],values):
        with col:
            st.markdown(f"""
            <div class="value-card">
                <div class="value-icon">{icon}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Our Journey ──
    

    # ── Team ──
    st.markdown("""
    <div style='padding:2rem 3rem 1rem;'>
        <div class="section-label">The People</div>
        <div class="section-title">Meet Our Team</div>
    </div>
    """, unsafe_allow_html=True)

    t1,t2,t3,t4 = st.columns(4)
    team = [
        ("","Shreeya Vora","CEO & Co-Founder","3rd Year · Francis Institute of Technology."),
        ("","Riya Solanki","CTO & Co-Founder","3rd Year · Francis Institute of Technology."),
        ("","Arya Redkar","Head of AI/ML","3rd Year · Francis Institute of Technology."),
        ("","Khushi Senghani","Chief Risk Officer","3rd Year · Francis Institute of Technology."),
    ]
    for col,(icon,name,role,bio) in zip([t1,t2,t3,t4],team):
        with col:
            st.markdown(f"""
            <div class="team-card">
                <div class="team-avatar">{icon}</div>
                <h5>{name}</h5>
                <div class="role">{role}</div>
                <p>{bio}</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Awards / Recognition ──
    

    # ── CTA ──
    _, mid, _ = st.columns([2,1,2])
    with mid:
        if st.button("🚀 Try Crediwise Free", use_container_width=True, type="primary", key="about_cta"):
            st.session_state.page = "calculator"
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)