import streamlit as st


def show():
    st.markdown("""
    <style>
    .contact-hero {
        background: linear-gradient(120deg,#002b80,#003399 60%,#0040b3);
        padding: 4rem 3rem 3.5rem;
        color:#fff;
    }
    .contact-hero h1 {
        font-family:'Merriweather',serif;
        font-size:clamp(1.8rem,4vw,2.8rem);
        font-weight:900; color:#fff; margin:0 0 0.9rem;
    }
    .contact-hero p { font-size:1rem; color:rgba(255,255,255,0.8); max-width:520px; line-height:1.75; margin:0; }

    .contact-card {
        background:#fff; border-radius:18px;
        border:1px solid #e2e8f0;
        padding:2rem; height:100%;
        box-shadow:0 2px 10px rgba(0,0,0,0.04);
        cursor: default;
    }
    .contact-card.clickable {
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .contact-card.clickable:hover {
        border-color: #003399;
        box-shadow: 0 8px 28px rgba(0,51,153,0.12);
        transform: translateY(-3px);
    }
    .contact-icon {
        width:52px; height:52px; border-radius:14px;
        background:linear-gradient(135deg,#003399,#0040cc);
        display:flex; align-items:center; justify-content:center;
        font-size:1.4rem; margin-bottom:1rem;
        box-shadow:0 4px 14px rgba(0,51,153,0.25);
    }
    .contact-card h4 { font-family:'Merriweather',serif; font-size:1rem; font-weight:700; color:#1a2540; margin:0 0 0.4rem; }
    .contact-card p  { font-size:0.86rem; color:#64748b; margin:0; line-height:1.65; }
    .contact-card a  { color:#003399; font-weight:600; text-decoration:none; }

    .faq-item {
        background:#fff; border-radius:12px;
        border:1px solid #e2e8f0;
        padding:1.3rem 1.6rem;
        margin-bottom:0.8rem;
        cursor:pointer;
        transition:border-color 0.2s;
    }
    .faq-item:hover { border-color:#003399; }
    .faq-q { font-weight:700; font-size:0.92rem; color:#1a2540; }
    .faq-a { font-size:0.86rem; color:#64748b; margin-top:0.6rem; line-height:1.65; }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ──
    st.markdown("""
    <div class="contact-hero">
        <div style="font-size:0.75rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                    color:rgba(255,255,255,0.6); margin-bottom:0.8rem;">Get In Touch</div>
        <h1>We're Here to Help</h1>
        <p>Have questions about your loan analysis, our AI model, or just want to say hello?
           Our team typically responds within 4 business hours.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:2.5rem 3rem;'>", unsafe_allow_html=True)

    # ── Contact info cards ──
    ci1, ci2, ci3, ci4 = st.columns(4)

    with ci1:
        st.markdown("""
        <div class="contact-card">
            <div class="contact-icon">📞</div>
            <h4>Call Us</h4>
            <p>Toll-Free: 1800-123-4567<br>Mon–Sat · 9 AM – 6 PM IST</p>
        </div>
        """, unsafe_allow_html=True)

    with ci2:
        st.markdown("""
        <div class="contact-card">
            <div class="contact-icon">📧</div>
            <h4>Email Us</h4>
            <p>support@crediwise.in<br>complaints@crediwise.in</p>
        </div>
        """, unsafe_allow_html=True)

    with ci3:
        st.markdown("""
        <div class="contact-card clickable" onclick="">
            <div class="contact-icon">💬</div>
            <h4>Share Feedback</h4>
            <p>Rate your experience & help us improve. Takes under 2 minutes.</p>
        </div>
        """, unsafe_allow_html=True)
        # Actual clickable button underneath the card
        if st.button("Open Feedback Form →", key="contact_to_feedback", use_container_width=True, type="primary"):
            st.session_state.page = "feedback"
            st.rerun()

    with ci4:
        st.markdown("""
        <div class="contact-card">
            <div class="contact-icon">🌐</div>
            <h4>100% Online Platform</h4>
            <p>Crediwise is a fully digital platform. No walk-ins needed — we're always reachable online.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Contact Form + FAQ side by side ──
    form_col, faq_col = st.columns([1, 1], gap="large")

    with form_col:
        st.markdown("""
        <div style='background:#fff; border-radius:18px; border:1px solid #e2e8f0;
                    padding:2rem; box-shadow:0 2px 10px rgba(0,0,0,0.04);'>
            <div style='font-family:Merriweather,serif; font-size:1.2rem; font-weight:800;
                        color:#1a2540; margin-bottom:0.3rem;'>Send Us a Message</div>
            <div style='font-size:0.84rem; color:#64748b; margin-bottom:1.5rem;'>
                We'll get back to you within 4 business hours.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("contact_form"):
            c1f, c2f = st.columns(2)
            name  = c1f.text_input("Full Name *", placeholder="Priya Sharma")
            email = c2f.text_input("Email Address *", placeholder="priya@example.com")
            phone = st.text_input("Phone Number", placeholder="+91 98765 43210")
            subject = st.selectbox("Subject *", [
                "General Inquiry",
                "Technical Issue / Bug",
                "Question About My Risk Score",
                "Partnership / Business",
                "Grievance / Complaint",
                "Other",
            ])
            message = st.text_area("Message *", placeholder="Tell us how we can help you...", height=140)
            agree   = st.checkbox("I consent to Crediwise processing my data to respond to this inquiry.")

            submitted = st.form_submit_button("Send Message →", use_container_width=True, type="primary")
            if submitted:
                if not name or not email or not message:
                    st.error("Please fill in all required fields (*).")
                elif "@" not in email:
                    st.error("Please enter a valid email address.")
                elif not agree:
                    st.warning("Please consent to data processing to submit the form.")
                else:
                    st.success(f"✅ Message received, {name.split()[0]}! We'll reply to {email} within 4 hours.")

    with faq_col:
        st.markdown("""
        <div style='font-family:Merriweather,serif; font-size:1.2rem; font-weight:800;
                    color:#1a2540; margin-bottom:0.3rem;'>Frequently Asked Questions</div>
        <div style='font-size:0.84rem; color:#64748b; margin-bottom:1.5rem;'>
            Quick answers to common questions.
        </div>
        """, unsafe_allow_html=True)

        faqs = [
            ("Is Crediwise free to use?",
             "Yes, completely free. No hidden charges, no subscription, no credit card required."),
            ("Does checking my risk score affect my CIBIL?",
             "No. Crediwise performs a soft analysis only — this never impacts your CIBIL or credit score."),
            ("How accurate is the AI risk model?",
             "Our ML model achieves 85%+ accuracy, trained on 50,000+ real loan outcomes from Indian borrowers."),
            ("Is my financial data stored or sold?",
             "No. We do not store or sell your personal financial data. All analysis is done in-session."),
            ("Which loans can I check?",
             "Personal, Home, Car, and Education loans. More loan types coming soon."),
            ("How do I raise a complaint?",
             "Email complaints@crediwise.in or call our toll-free number 1800-123-4567. We resolve within 48 hrs."),
        ]
        for q, a in faqs:
            with st.expander(q):
                st.markdown(f"<p style='font-size:0.88rem; color:#475569; line-height:1.7; margin:0;'>{a}</p>", unsafe_allow_html=True)

    # ── Grievance ──
    st.markdown("""
    <div style='background:#fff8f0; border:1px solid #fed7aa; border-radius:16px;
                padding:1.8rem; margin-top:1.5rem;'>
        <div style='font-weight:700; color:#c2410c; margin-bottom:0.4rem; font-size:0.95rem;'>
            ⚠️ Grievance Redressal (RBI Mandate)
        </div>
        <p style='font-size:0.85rem; color:#92400e; line-height:1.7; margin:0;'>
            If your complaint is not resolved within <strong>30 days</strong>, you may escalate to our
            Nodal Officer at <strong>nodal@crediwise.in</strong> or contact the
            <strong>RBI Ombudsman</strong> at cms.rbi.org.in. Crediwise is committed to fair and
            transparent grievance resolution as per RBI guidelines.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)