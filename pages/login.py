import streamlit as st


def show():
    st.markdown("""
    <style>
    .auth-logo {
        font-family: 'Merriweather', serif;
        font-size: 1.5rem; font-weight: 900;
        color: #003399; text-align: center;
        margin-bottom: 0.3rem;
    }
    .auth-logo span { color: #e53e3e; }
    .auth-tagline { text-align:center; font-size:0.78rem; color:#64748b; font-weight:600;
                    letter-spacing:0.06em; text-transform:uppercase; margin-bottom:1.5rem; }
    .auth-title { font-family:'Merriweather',serif; font-size:1.4rem; font-weight:900;
                  color:#1a2540; margin:0 0 0.4rem; }
    .auth-sub { font-size:0.88rem; color:#64748b; margin:0 0 1.4rem; line-height:1.6; }
    .auth-divider {
        display:flex; align-items:center; gap:0.8rem;
        margin:1.2rem 0; color:#94a3b8; font-size:0.82rem;
    }
    .auth-divider::before,.auth-divider::after {
        content:''; flex:1; height:1px; background:#e2e8f0;
    }
    .social-btn {
        display:flex; align-items:center; justify-content:center; gap:0.7rem;
        background:#f8faff; border:1.5px solid #e2e8f0; border-radius:10px;
        padding:0.65rem; font-size:0.88rem; font-weight:600; color:#1a2540;
        cursor:pointer; margin-bottom:0.7rem; width:100%;
    }
    .forgot-link { text-align:right; font-size:0.8rem; margin-top:-0.5rem; margin-bottom:1rem; }
    .forgot-link a { color:#003399; font-weight:600; text-decoration:none; }
    .trust-note {
        text-align:center; font-size:0.76rem; color:#94a3b8;
        margin-top:1.5rem; line-height:1.6;
    }
    .login-card {
        background: rgba(255,255,255,0.82);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-radius: 22px;
        border: 1px solid rgba(144,202,249,0.4);
        padding: 2.4rem 2rem 1.2rem;
        box-shadow: 0 8px 40px rgba(0,51,153,0.10);
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.4, 1])

    with center:
        st.markdown("""
        <div class="login-card">
            <div class="auth-logo">Credi<span>wise</span></div>
            <div class="auth-tagline">AI Loan Intelligence &middot; India</div>
            <div class="auth-title">Welcome back</div>
            <div class="auth-sub">Sign in to access your loan analyses and saved reports.</div>
            <div class="social-btn">&#128309; Continue with Google</div>
            <div class="social-btn">&#128312; Continue with Microsoft</div>
            <div class="auth-divider">or sign in with email</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email    = st.text_input("Email Address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            st.markdown('<div class="forgot-link"><a href="#">Forgot password?</a></div>', unsafe_allow_html=True)
            remember  = st.checkbox("Keep me signed in for 30 days")
            submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

            if submitted:
                if not email or not password:
                    st.error("Please enter your email and password.")
                elif "@" not in email:
                    st.error("Please enter a valid email address.")
                elif len(password) < 4:
                    st.error("Password too short.")
                else:
                    st.session_state.logged_in  = True
                    st.session_state.username   = email.split("@")[0].capitalize()
                    st.session_state.user_email = email
                    st.success(f"Welcome back, {st.session_state.username}!")
                    st.session_state.page = "home"
                    st.rerun()

        st.markdown('<div style="text-align:center;font-size:0.88rem;color:#64748b;margin-top:1.2rem;">Don\'t have an account?</div>', unsafe_allow_html=True)

        if st.button("Create a Free Account →", use_container_width=True, key="goto_signup"):
            st.session_state.page = "signup"
            st.rerun()

        st.markdown("""
        <div class="trust-note">
            &#128274; 256-bit SSL &nbsp;&middot;&nbsp; &#9989; RBI Compliant &nbsp;&middot;&nbsp; &#127470;&#127475; India's Trusted Platform
        </div>
        """, unsafe_allow_html=True)