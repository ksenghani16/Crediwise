import streamlit as st


def show():
    st.markdown("""
    <style>
    .feedback-hero {
        background: linear-gradient(120deg,#002b80,#003399 60%,#0040b3);
        padding: 4rem 3rem 3.5rem;
        color: #fff;
        position: relative;
        overflow: hidden;
    }
    .feedback-hero::after {
        content:'';
        position:absolute; right:-80px; top:-80px;
        width:400px; height:400px; border-radius:50%;
        background:rgba(255,255,255,0.05);
        pointer-events:none;
    }
    .feedback-hero h1 {
        font-family:'Merriweather',serif;
        font-size:clamp(1.8rem,4vw,2.8rem);
        font-weight:900; color:#fff; margin:0 0 0.9rem;
    }
    .feedback-hero p {
        font-size:1rem; color:rgba(255,255,255,0.8);
        max-width:520px; line-height:1.75; margin:0;
    }
    .fb-card {
        background:rgba(255,255,255,0.82);
        backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
        border-radius:20px; border:1px solid rgba(144,202,249,0.45);
        padding:2.5rem 2.2rem;
        box-shadow:0 8px 40px rgba(0,51,153,0.09);
    }
    .stat-chip {
        text-align:center;
        background:rgba(255,255,255,0.78);
        border:1px solid rgba(144,202,249,0.4);
        border-radius:14px; padding:1.2rem 1rem;
    }
    .stat-chip-val {
        font-family:'Merriweather',serif;
        font-size:1.6rem; font-weight:900; color:#003399; line-height:1;
    }
    .stat-chip-lbl {
        font-size:0.73rem; color:#64748b; font-weight:600;
        text-transform:uppercase; letter-spacing:0.06em; margin-top:4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero
    st.markdown("""
    <div class="feedback-hero">
        <div style="font-size:0.75rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                    color:rgba(255,255,255,0.6); margin-bottom:0.8rem;">Share Your Thoughts</div>
        <h1>We&#39;d Love Your Feedback</h1>
        <p>Help us make Crediwise better for every Indian borrower.
           Your feedback directly shapes the product &#8212; it takes under 2 minutes.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:2.5rem 3rem;'>", unsafe_allow_html=True)

    # Stats row
    

    form_col, tips_col = st.columns([1.4, 1], gap="large")

    with form_col:
        
        st.markdown(
            "<div style='font-family:Merriweather,serif;font-size:1.15rem;"
            "font-weight:800;color:#1a2540;margin-bottom:0.3rem;'>"
            "&#128221; Submit Your Feedback</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='font-size:0.86rem;color:#64748b;margin-bottom:1.6rem;line-height:1.6;'>"
            "All fields marked * are required. Your email is optional but helps us follow up.</div>",
            unsafe_allow_html=True,
        )

        with st.form("feedback_form", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            name  = fc1.text_input("Your Name *", placeholder="Priya Sharma")
            email = fc2.text_input("Email (optional)", placeholder="priya@example.com")

            fb_type = st.selectbox("Feedback Type *", [
                "General Experience",
                "AI Risk Score Accuracy",
                "Calculator & Dashboard",
                "UI / Design Suggestion",
                "Bug Report",
                "Feature Request",
                "Loan Plan Suggestions",
                "Other",
            ])

            rating = st.select_slider(
                "Overall Rating *",
                options=["1 - Poor", "2 - Fair", "3 - Good", "4 - Very Good", "5 - Excellent"],
                value="4 - Very Good",
            )

            features_used = st.multiselect(
                "Which features did you use? (select all that apply)",
                options=[
                    "EMI Calculator", "Risk Score", "Stress Timeline",
                    "Plan Suggestions", "Plan Comparison", "Repayment Tracker",
                    "Login / Signup", "Contact Form",
                ],
                default=[],
            )

            nps = st.select_slider(
                "How likely are you to recommend Crediwise? (0 = Not at all, 10 = Definitely)",
                options=list(range(0, 11)),
                value=8,
            )

            message = st.text_area(
                "Your Feedback *",
                placeholder="Tell us what you loved, what could be better, or anything else on your mind...",
                height=140,
            )

            source = st.selectbox("How did you find Crediwise?", [
                "Google Search", "Friend / Family Referral", "Social Media",
                "College / University", "News Article", "Other",
            ])

            consent   = st.checkbox("I consent to Crediwise using this feedback to improve its services.")
            follow_up = st.checkbox("I am happy to be contacted for a follow-up (if email provided).")

            submitted = st.form_submit_button("Submit Feedback", use_container_width=True, type="primary")

            if submitted:
                if not name:
                    st.error("Please enter your name.")
                elif not message:
                    st.error("Please write your feedback before submitting.")
                elif not consent:
                    st.warning("Please consent to data usage to submit your feedback.")
                else:
                    first = name.split()[0]
                    if email and follow_up:
                        followup_note = "We will follow up at " + email + " within 48 hours."
                    else:
                        followup_note = "We appreciate you taking the time to share your thoughts!"
                    st.success("Thank you, " + first + "! Your feedback has been received. " + followup_note)
                    st.balloons()

        st.markdown("</div>", unsafe_allow_html=True)

    with tips_col:
        st.markdown("""
        <div style="background:linear-gradient(145deg,#002880,#003399 50%,#0044bb);
                    border-radius:20px; padding:2rem 1.8rem; color:#fff;
                    position:relative; overflow:hidden; margin-bottom:1.5rem;">
            <div style="position:absolute;top:-60px;right:-60px;width:180px;height:180px;
                        border-radius:50%;background:rgba(255,255,255,0.05);"></div>
            <div style="font-family:'Merriweather',serif;font-size:1.15rem;font-weight:900;
                        margin-bottom:0.5rem;position:relative;">Why Your Feedback Matters</div>
            <p style="font-size:0.85rem;color:rgba(255,255,255,0.78);line-height:1.65;
                      margin:0 0 1.4rem;position:relative;">
                Crediwise is built by a small team passionate about financial inclusion.
                Every piece of feedback directly influences what we build next.
            </p>
            <div style="display:flex;flex-direction:column;gap:0.9rem;position:relative;">
                <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <div style="width:34px;height:34px;border-radius:9px;
                                background:rgba(255,255,255,0.13);
                                display:flex;align-items:center;justify-content:center;
                                font-size:0.9rem;flex-shrink:0;">&#128260;</div>
                    <div>
                        <div style="font-weight:700;font-size:0.85rem;">Shapes Future Features</div>
                        <div style="font-size:0.77rem;color:rgba(255,255,255,0.6);margin-top:1px;">
                            Feature requests from users power our roadmap.
                        </div>
                    </div>
                </div>
                <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <div style="width:34px;height:34px;border-radius:9px;
                                background:rgba(255,255,255,0.13);
                                display:flex;align-items:center;justify-content:center;
                                font-size:0.9rem;flex-shrink:0;">&#129302;</div>
                    <div>
                        <div style="font-weight:700;font-size:0.85rem;">Improves AI Accuracy</div>
                        <div style="font-size:0.77rem;color:rgba(255,255,255,0.6);margin-top:1px;">
                            Feedback on risk scores helps us retrain and refine our model.
                        </div>
                    </div>
                </div>
                <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <div style="width:34px;height:34px;border-radius:9px;
                                background:rgba(255,255,255,0.13);
                                display:flex;align-items:center;justify-content:center;
                                font-size:0.9rem;flex-shrink:0;">&#127470;&#127475;</div>
                    <div>
                        <div style="font-weight:700;font-size:0.85rem;">Serves India Better</div>
                        <div style="font-size:0.77rem;color:rgba(255,255,255,0.6);margin-top:1px;">
                            Your experience helps us reach more borrowers across India.
                        </div>
                    </div>
                </div>
            </div>
            <div style="border-top:1px solid rgba(255,255,255,0.13);padding-top:1rem;
                        margin-top:1.4rem;font-size:0.74rem;color:rgba(255,255,255,0.5);
                        text-align:center;position:relative;">
                &#128274; Anonymous feedback welcome &nbsp;&middot;&nbsp; Never sold or shared
            </div>
        </div>
        """, unsafe_allow_html=True)

       

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)