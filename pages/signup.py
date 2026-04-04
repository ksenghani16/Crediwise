import re
import streamlit as st
from utils.auth_db import init_db, register_user, validate_password, email_exists

init_db()   # no-op if table already exists


def _pw_strength_ui(password: str):
    """Render inline password strength indicator."""
    if not password:
        return

    rules = [
        ("8+ characters",          len(password) >= 8),
        ("Uppercase letter",        bool(re.search(r"[A-Z]", password))),
        ("Lowercase letter",        bool(re.search(r"[a-z]", password))),
        ("Number (0–9)",            bool(re.search(r"\d",    password))),
        ("Special character",       bool(re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>?/\\|`~]', password))),
    ]
    passed = sum(1 for _, ok in rules if ok)

    # Bar colour
    if passed <= 2:
        bar_color, strength_label = "#ef4444", "Weak"
    elif passed <= 3:
        bar_color, strength_label = "#f59e0b", "Fair"
    elif passed == 4:
        bar_color, strength_label = "#3b82f6", "Good"
    else:
        bar_color, strength_label = "#22c55e", "Strong"

    bar_pct = int(passed / len(rules) * 100)

    st.markdown(f"""
    <div style="margin:0.4rem 0 0.6rem;">
        <div style="display:flex;justify-content:space-between;
                    font-size:0.74rem;font-weight:700;margin-bottom:4px;">
            <span style="color:#475569;">Password strength</span>
            <span style="color:{bar_color};">{strength_label}</span>
        </div>
        <div style="background:rgba(144,202,249,0.25);border-radius:100px;height:5px;overflow:hidden;">
            <div style="width:{bar_pct}%;height:100%;border-radius:100px;
                        background:{bar_color};transition:width 0.3s ease;"></div>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:0.35rem;margin-top:0.5rem;">
            {''.join(
                f'<span style="font-size:0.72rem;font-weight:600;padding:2px 8px;border-radius:100px;'
                f'background:{"rgba(34,197,94,0.12)" if ok else "rgba(239,68,68,0.10)"};'
                f'color:{"#15803d" if ok else "#991b1b"};">'
                f'{"✓" if ok else "✗"} {label}</span>'
                for label, ok in rules
            )}
        </div>
    </div>
    """, unsafe_allow_html=True)


def show():
    st.markdown("""
    <style>
    .auth-logo { font-family:'Merriweather',serif; font-size:1.5rem; font-weight:900;
                 color:#003399; text-align:center; margin-bottom:0.25rem; }
    .auth-logo span { color:#e53e3e; }
    .auth-tagline { text-align:center; font-size:0.76rem; color:#64748b; font-weight:600;
                    letter-spacing:0.06em; text-transform:uppercase; margin-bottom:1.2rem; }

    .progress-bar-wrap { background:rgba(144,202,249,0.25); border-radius:100px;
                         height:5px; margin-bottom:1.2rem; overflow:hidden; }
    .progress-bar-fill { height:100%; border-radius:100px;
                         background:linear-gradient(90deg,#003399,#64b5f6); transition:width 0.4s ease; }
    .step-label {
        display:flex; align-items:center; gap:0.5rem;
        font-size:0.76rem; color:#64748b; font-weight:600;
        letter-spacing:0.06em; text-transform:uppercase; margin-bottom:1rem;
    }
    .step-badge {
        width:20px; height:20px; border-radius:50%; background:#003399;
        color:#fff; font-size:0.7rem; font-weight:800;
        display:inline-flex; align-items:center; justify-content:center; flex-shrink:0;
    }
    .auth-divider {
        display:flex; align-items:center; gap:0.8rem;
        margin:0.8rem 0; color:#94a3b8; font-size:0.8rem;
    }
    .auth-divider::before,.auth-divider::after {
        content:''; flex:1; height:1px; background:rgba(144,202,249,0.5);
    }
    .social-btn {
        display:flex; align-items:center; justify-content:center; gap:0.7rem;
        background:rgba(255,255,255,0.7); border:1.5px solid rgba(144,202,249,0.5);
        border-radius:10px; padding:0.6rem; font-size:0.86rem; font-weight:600; color:#1a2540;
        cursor:pointer; margin-bottom:0.6rem; width:100%;
    }
    .social-btn:hover { border-color:#003399; background:rgba(240,248,255,0.9); }

    /* Benefits left panel */
    .benefits-panel {
        background: linear-gradient(145deg,#002880,#003399 50%,#0044bb);
        border-radius:20px; padding:2.2rem 2rem 2rem;
        color:#fff; position:relative; overflow:hidden;
    }
    .benefits-panel::before {
        content:''; position:absolute; top:-70px; right:-70px;
        width:220px; height:220px; border-radius:50%;
        background:rgba(255,255,255,0.06); pointer-events:none;
    }
    .benefits-panel::after {
        content:''; position:absolute; bottom:-50px; left:-40px;
        width:180px; height:180px; border-radius:50%;
        background:rgba(100,181,246,0.1); pointer-events:none;
    }
    .bp-title { font-family:'Merriweather',serif; font-size:1.35rem; font-weight:900;
                margin:0 0 0.5rem; position:relative; }
    .bp-sub { font-size:0.84rem; color:rgba(255,255,255,0.75); line-height:1.65;
              margin:0 0 1.6rem; position:relative; }
    .benefit-row { display:flex; gap:0.75rem; margin-bottom:1rem;
                   align-items:flex-start; position:relative; }
    .benefit-icon { width:36px; height:36px; border-radius:10px;
                    background:rgba(255,255,255,0.13);
                    display:flex; align-items:center; justify-content:center;
                    font-size:0.95rem; flex-shrink:0; }
    .benefit-title { font-weight:700; font-size:0.86rem; color:#fff; line-height:1.3; }
    .benefit-desc  { font-size:0.76rem; color:rgba(255,255,255,0.62); line-height:1.45; margin-top:1px; }
    .bp-footer {
        border-top:1px solid rgba(255,255,255,0.13); padding-top:1rem; margin-top:1.2rem;
        font-size:0.74rem; color:rgba(255,255,255,0.5); text-align:center; position:relative;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:2rem 3rem;'>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.1], gap="large")

    with left_col:
        st.markdown("""
        <div class="benefits-panel">
            <div class="bp-title">Join Crediwise</div>
            <p class="bp-sub">India's most transparent AI loan intelligence platform.<br>Free forever. No hidden fees.</p>
            <div class="benefit-row">
                <div class="benefit-icon">&#128269;</div>
                <div>
                    <div class="benefit-title">Instant AI Risk Score</div>
                    <div class="benefit-desc">Know your loan risk in 60 seconds.</div>
                </div>
            </div>
            <div class="benefit-row">
                <div class="benefit-icon">&#128202;</div>
                <div>
                    <div class="benefit-title">Stress Timeline</div>
                    <div class="benefit-desc">See how your savings change with the loan.</div>
                </div>
            </div>
            <div class="benefit-row">
                <div class="benefit-icon">&#128161;</div>
                <div>
                    <div class="benefit-title">Smart Alternatives</div>
                    <div class="benefit-desc">AI suggests safer, optimised loan plans.</div>
                </div>
            </div>
            <div class="benefit-row">
                <div class="benefit-icon">&#128274;</div>
                <div>
                    <div class="benefit-title">100% Secure</div>
                    <div class="benefit-desc">Your data is never stored or sold.</div>
                </div>
            </div>
            <div class="benefit-row">
                <div class="benefit-icon">&#9989;</div>
                <div>
                    <div class="benefit-title">No Credit Impact</div>
                    <div class="benefit-desc">Soft check only — CIBIL safe always.</div>
                </div>
            </div>
            <div class="bp-footer">&#128274; 256-bit SSL &nbsp;&middot;&nbsp; &#9989; RBI Compliant &nbsp;&middot;&nbsp; &#127470;&#127475; Made in India</div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("""
        <div class="auth-logo">Credi<span>wise</span></div>
        <div class="auth-tagline">Create Your Free Account</div>
        <div class="social-btn">&#128309; Sign up with Google</div>
        <div class="social-btn">&#128312; Sign up with Microsoft</div>
        <div class="auth-divider">or sign up with email</div>
        """, unsafe_allow_html=True)

        if "signup_step" not in st.session_state:
            st.session_state.signup_step = 1

        step = st.session_state.signup_step
        pct  = 50 if step == 1 else 100

        st.markdown(f"""
        <div class="progress-bar-wrap">
            <div class="progress-bar-fill" style="width:{pct}%;"></div>
        </div>
        <div class="step-label">
            <span class="step-badge">{step}</span>
            {"Personal Details" if step == 1 else "Account Security"}
            <span style="margin-left:auto;color:#94a3b8;font-size:0.74rem;">Step {step} of 2</span>
        </div>
        """, unsafe_allow_html=True)

        # ── STEP 1: Personal details ──────────────────────────────────────────
        if step == 1:
            with st.form("signup_step1"):
                fn_col, ln_col = st.columns(2)
                first_name = fn_col.text_input("First Name *", placeholder="Priya")
                last_name  = ln_col.text_input("Last Name *",  placeholder="Sharma")
                email      = st.text_input("Email Address *", placeholder="priya@example.com")
                phone      = st.text_input("Mobile Number *", placeholder="+91 98765 43210")
                city       = st.selectbox("City *", [
                    "Mumbai", "Delhi", "Bangalore", "Chennai",
                    "Hyderabad", "Pune", "Kolkata", "Other",
                ])
                nxt = st.form_submit_button("Continue →", use_container_width=True, type="primary")

                if nxt:
                    errors = []
                    if not first_name or not last_name:
                        errors.append("Please enter your full name.")
                    if not email or "@" not in email or "." not in email.split("@")[-1]:
                        errors.append("Enter a valid email address.")
                    digits = re.sub(r"[\s\-+()]", "", phone)
                    # Strip country code prefix +91 or 0 if present, then expect 10 digits
                    digits = re.sub(r"^(91|0)(?=\d{10}$)", "", digits)
                    if not re.fullmatch(r"[6-9]\d{9}", digits):
                        errors.append("Enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.")
                    if errors:
                        for e in errors:
                            st.error(e)
                    elif email_exists(email):
                        st.error("An account with this email already exists. Please log in.")
                    else:
                        st.session_state["_su_first"] = first_name
                        st.session_state["_su_last"]  = last_name
                        st.session_state["_su_email"] = email
                        st.session_state["_su_phone"] = phone
                        st.session_state["_su_city"]  = city
                        st.session_state.signup_step  = 2
                        st.rerun()

        # ── STEP 2: Password + terms ──────────────────────────────────────────
        elif step == 2:
            # Live password strength (outside form so it updates as user types)
            live_pw = st.text_input(
                "Create Password *",
                type="password",
                placeholder="Min. 8 chars · uppercase · lowercase · number · special",
                key="live_password_field",
            )
            _pw_strength_ui(live_pw)

            with st.form("signup_step2"):
                # Hidden re-entry — user types again inside the form for confirmation
                confirm = st.text_input(
                    "Confirm Password *",
                    type="password",
                    placeholder="Repeat your password",
                )
                pan   = st.text_input(
                    "PAN Number (optional)",
                    placeholder="ABCDE1234F — for faster analysis",
                )
                terms   = st.checkbox("I agree to the Terms of Service and Privacy Policy *")
                updates = st.checkbox("Send me loan eligibility tips (optional)")

                sub_col, back_col = st.columns([2, 1])
                submitted = sub_col.form_submit_button(
                    "Create Account 🚀", use_container_width=True, type="primary"
                )
                go_back = back_col.form_submit_button("← Back", use_container_width=True)

                if go_back:
                    st.session_state.signup_step = 1
                    st.rerun()

                if submitted:
                    # Pull the live field value (form re-renders it blank, so
                    # we stored it in session state via the key above)
                    password = st.session_state.get("live_password_field", "")

                    errs = validate_password(password)
                    if errs:
                        st.error("Password requirements not met:\n• " + "\n• ".join(errs))
                    elif password != confirm:
                        st.error("Passwords do not match. Please re-enter.")
                    elif not terms:
                        st.warning("Please accept the Terms of Service to continue.")
                    else:
                        ok, msg = register_user(
                            email      = st.session_state.get("_su_email", ""),
                            password   = password,
                            first_name = st.session_state.get("_su_first", ""),
                            last_name  = st.session_state.get("_su_last",  ""),
                            phone      = st.session_state.get("_su_phone", ""),
                            city       = st.session_state.get("_su_city",  ""),
                            pan        = pan,
                        )
                        if ok:
                            name = st.session_state.get("_su_first", "User")
                            st.session_state.logged_in   = True
                            st.session_state.username    = name.capitalize()
                            st.session_state.user_email  = st.session_state.get("_su_email", "")
                            st.session_state.signup_step = 1
                            # Clean up temp keys
                            for k in ("_su_first","_su_last","_su_email","_su_phone","_su_city"):
                                st.session_state.pop(k, None)
                            st.success(f"Welcome to Crediwise, {name}! Your account is ready.")
                            st.session_state.page = "calculator"
                            st.rerun()
                        else:
                            st.error(msg)

        st.markdown(
            '<div style="text-align:center;font-size:0.83rem;'
            'color:#64748b;margin-top:1rem;">Already have an account?</div>',
            unsafe_allow_html=True,
        )
        if st.button("Sign In Instead →", use_container_width=True, key="goto_login_from_signup"):
            st.session_state.signup_step = 1
            st.session_state.page = "login"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)