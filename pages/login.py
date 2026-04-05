import streamlit as st
from utils.auth_db import init_db, login_user

init_db()   # no-op if table already exists


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
    /* Google button styling */
    .google-btn-wrap > div[data-testid="stButton"] > button {
        background: #fff !important;
        color: #1a2540 !important;
        border: 1.5px solid #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        border-radius: 10px !important;
        height: 44px !important;
    }
    .google-btn-wrap > div[data-testid="stButton"] > button:hover {
        border-color: #4285F4 !important;
        box-shadow: 0 2px 10px rgba(66,133,244,0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Handle Google OAuth callback (code in URL) ──
    params = st.query_params
    if "code" in params and params.get("state", "") == "google_oauth":
        with st.spinner("Signing you in with Google..."):
            try:
                from utils.oauth_handler import handle_google_callback, oauth_login_or_register
                ok_cb, msg_cb, user_data = handle_google_callback(params["code"])
                st.query_params.clear()
                if ok_cb:
                    ok_reg, msg_reg = oauth_login_or_register(user_data)
                    if ok_reg:
                        redirect = st.session_state.pop("_redirect_after_login", "home")
                        st.session_state.page = redirect
                        st.rerun()
                    else:
                        st.error(f"Login error: {msg_reg}")
                else:
                    st.error(f"Google sign-in failed: {msg_cb}")
            except ImportError:
                st.error("OAuth handler not found. Make sure utils/oauth_handler.py exists.")

    _, center, _ = st.columns([1, 1.4, 1])

    with center:
        st.markdown("""
        <div class="login-card">
            <div class="auth-logo">Credi<span>wise</span></div>
            <div class="auth-tagline">AI Loan Intelligence &middot; India</div>
            <div class="auth-title">Welcome back</div>
            <div class="auth-sub">Sign in to access your loan analyses and saved reports.</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Google OAuth button ──
        try:
            from utils.oauth_handler import get_google_auth_url
            google_url = get_google_auth_url(state="google_oauth")
        except ImportError:
            google_url = None

        if google_url:
            st.markdown(
                f'<a href="{google_url}" target="_self" style="text-decoration:none;">'
                f'<div style="display:flex;align-items:center;justify-content:center;gap:0.75rem;'
                f'background:#fff;border:1.5px solid #e2e8f0;border-radius:10px;'
                f'padding:0.65rem;font-size:0.88rem;font-weight:600;color:#1a2540;'
                f'cursor:pointer;margin-bottom:1.2rem;width:100%;box-sizing:border-box;'
                f'transition:border-color 0.2s;">'
                f'<svg width="18" height="18" viewBox="0 0 48 48">'
                f'<path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>'
                f'<path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>'
                f'<path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>'
                f'<path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>'
                f'<path fill="none" d="M0 0h48v48H0z"/>'
                f'</svg>'
                f'Continue with Google</div></a>',
                unsafe_allow_html=True,
            )
        else:
            # Google not configured — show greyed-out placeholder
            st.markdown("""
            <div style="display:flex;align-items:center;justify-content:center;gap:0.75rem;
                        background:#f8faff;border:1.5px solid #e2e8f0;border-radius:10px;
                        padding:0.65rem;font-size:0.88rem;font-weight:600;color:#94a3b8;
                        margin-bottom:1.2rem;cursor:not-allowed;">
                <svg width="16" height="16" viewBox="0 0 48 48">
                    <path fill="#ccc" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                    <path fill="#ccc" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                    <path fill="#ccc" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                    <path fill="#ccc" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>
                Continue with Google (not configured)
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="auth-divider">or sign in with email</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            email    = st.text_input("Email Address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            st.markdown('<div class="forgot-link"><a href="#">Forgot password?</a></div>',
                        unsafe_allow_html=True)
            remember  = st.checkbox("Keep me signed in for 30 days")
            submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

            if submitted:
                if not email or not password:
                    st.error("Please enter your email and password.")
                elif "@" not in email or "." not in email.split("@")[-1]:
                    st.error("Please enter a valid email address.")
                else:
                    ok, msg, user_data = login_user(email, password)
                    if ok:
                        st.session_state.logged_in  = True
                        st.session_state.username   = user_data["first_name"].capitalize()
                        st.session_state.user_email = user_data["email"]
                        st.success(f"Welcome back, {user_data['first_name'].capitalize()}!")
                        redirect = st.session_state.pop("_redirect_after_login", "home")
                        st.session_state.page = redirect
                        st.rerun()
                    else:
                        st.error(f"🔒 {msg}")

        st.markdown(
            '<div style="text-align:center;font-size:0.88rem;color:#64748b;margin-top:1.2rem;">'
            "Don't have an account?</div>",
            unsafe_allow_html=True,
        )

        if st.button("Create a Free Account →", use_container_width=True, key="goto_signup"):
            st.session_state.page = "signup"
            st.rerun()

        st.markdown("""
        <div class="trust-note">
            &#128274; 256-bit SSL &nbsp;&middot;&nbsp; &#9989; RBI Compliant
            &nbsp;&middot;&nbsp; &#127470;&#127475; India's Trusted Platform
        </div>
        """, unsafe_allow_html=True)
