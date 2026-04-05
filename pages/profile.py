"""
pages/profile.py

Crediwise — User Profile Page.
Shows: name/email/city, change password form, loan analysis history.
"""

import streamlit as st
from utils.auth_db import login_user, _get_conn, _hash_password, validate_password


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_user_details(email: str) -> dict:
    """Fetch full user record from DB."""
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
            ).fetchone()
        if row:
            return dict(row)
    except Exception:
        pass
    return {}


def _change_password(email: str, old_pw: str, new_pw: str) -> tuple[bool, str]:
    """Verify old password then set new one."""
    ok, msg, _ = login_user(email, old_pw)
    if not ok:
        return False, "Current password is incorrect."
    errs = validate_password(new_pw)
    if errs:
        return False, "New password doesn't meet requirements:\n• " + "\n• ".join(errs)
    try:
        pw_hash, pw_salt = _hash_password(new_pw)
        with _get_conn() as conn:
            conn.execute(
                "UPDATE users SET pw_hash=?, pw_salt=? WHERE email=?",
                (pw_hash, pw_salt, email.lower().strip()),
            )
            conn.commit()
        return True, "Password updated successfully."
    except Exception as e:
        return False, f"Failed to update password: {e}"


def _get_loan_history(email: str) -> list[dict]:
    """Fetch past loan analyses saved for this user."""
    try:
        import sqlite3, os
        db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "data", "sessions.db"
        )
        if not os.path.exists(db_path):
            return []
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM sessions WHERE user_email=? ORDER BY timestamp DESC LIMIT 20",
            (email.lower().strip(),),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def _fmt(n) -> str:
    try:
        return f"₹{float(n):,.0f}"
    except Exception:
        return str(n)


# ── Page ──────────────────────────────────────────────────────────────────────

def show():
    if not st.session_state.get("logged_in"):
        st.markdown("""
        <div style="text-align:center;padding:5rem 2rem;">
            <div style="font-size:3rem;margin-bottom:1rem;">🔐</div>
            <h3 style="font-family:'Merriweather',serif;color:#1a2540;">Sign in to view your profile</h3>
        </div>
        """, unsafe_allow_html=True)
        _, c, _ = st.columns([2, 1, 2])
        with c:
            if st.button("Login →", use_container_width=True, type="primary"):
                st.session_state.page = "login"
                st.rerun()
        return

    st.markdown("""
    <style>
    .profile-hero {
        background: linear-gradient(120deg,#002b80,#003399 60%,#0040b3);
        padding: 3rem 3rem 2.5rem;
        color: #fff;
    }
    .profile-hero h1 {
        font-family:'Merriweather',serif;
        font-size:clamp(1.6rem,3vw,2.4rem);
        font-weight:900; color:#fff; margin:0 0 0.5rem;
    }
    .profile-hero p { font-size:0.9rem; color:rgba(255,255,255,0.75); margin:0; }

    .profile-avatar {
        width:72px; height:72px; border-radius:50%;
        background:rgba(255,255,255,0.2);
        border:3px solid rgba(255,255,255,0.4);
        display:flex; align-items:center; justify-content:center;
        font-family:'Merriweather',serif; font-size:1.8rem; font-weight:900;
        color:#fff; margin-bottom:1rem;
    }
    .profile-card {
        background:rgba(255,255,255,0.82); backdrop-filter:blur(14px);
        border:1px solid rgba(144,202,249,0.4); border-radius:18px;
        padding:1.8rem; box-shadow:0 4px 20px rgba(0,51,153,0.07);
        margin-bottom:1.2rem;
    }
    .profile-card h4 {
        font-family:'Merriweather',serif; font-size:1rem; font-weight:800;
        color:#1a2540; margin:0 0 1.2rem;
        padding-bottom:0.7rem; border-bottom:1px solid rgba(144,202,249,0.4);
    }
    .info-row {
        display:flex; justify-content:space-between; align-items:center;
        padding:0.6rem 0; border-bottom:1px solid rgba(144,202,249,0.2);
        font-size:0.87rem;
    }
    .info-row:last-child { border-bottom:none; }
    .info-label { color:#64748b; font-weight:600; }
    .info-value { color:#1a2540; font-weight:700; }

    .history-row {
        background:rgba(255,255,255,0.75);
        border:1px solid rgba(144,202,249,0.35); border-radius:12px;
        padding:1rem 1.2rem; margin-bottom:0.7rem;
        display:grid; grid-template-columns:1fr 1fr 1fr 1fr 1fr;
        gap:0.5rem; align-items:center; font-size:0.83rem;
    }
    .history-header {
        display:grid; grid-template-columns:1fr 1fr 1fr 1fr 1fr;
        gap:0.5rem; padding:0.4rem 1.2rem;
        font-size:0.72rem; color:#64748b; font-weight:700;
        text-transform:uppercase; letter-spacing:0.07em;
        margin-bottom:0.4rem;
    }
    .risk-pill {
        display:inline-block; padding:0.2rem 0.6rem;
        border-radius:100px; font-size:0.72rem; font-weight:700;
    }
    .risk-low    { background:rgba(34,197,94,0.15);  color:#15803d; }
    .risk-medium { background:rgba(245,158,11,0.15); color:#92400e; }
    .risk-high   { background:rgba(239,68,68,0.15);  color:#991b1b; }
    </style>
    """, unsafe_allow_html=True)

    email    = st.session_state.get("user_email", "")
    username = st.session_state.get("username", "User")
    user     = _get_user_details(email)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="profile-hero">
        <div class="profile-avatar">{username[0].upper()}</div>
        <h1>Hi, {username}!</h1>
        <p>Manage your account details, change your password, and view your loan analysis history.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:2rem 3rem;'>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.3], gap="large")

    # ── LEFT: Account info + change password ──────────────────────────────────
    with left_col:

        # Account info card
        st.markdown("""
        <div class="profile-card">
            <h4>👤 Account Information</h4>
        </div>
        """, unsafe_allow_html=True)

        info_items = [
            ("First Name",  user.get("first_name", username)),
            ("Last Name",   user.get("last_name", "")),
            ("Email",       user.get("email", email)),
            ("City",        user.get("city", "—")),
            ("Phone",       user.get("phone", "—")),
            ("Member Since", (user.get("created_at", "")[:10] if user.get("created_at") else "—")),
        ]
        rows_html = "".join(
            f'<div class="info-row"><span class="info-label">{label}</span>'
            f'<span class="info-value">{value or "—"}</span></div>'
            for label, value in info_items
        )
        st.markdown(f"""
        <div class="profile-card" style="margin-top:-1rem;">
            {rows_html}
        </div>
        """, unsafe_allow_html=True)

        # Quick actions
        st.markdown("""
        <div class="profile-card">
            <h4>⚡ Quick Actions</h4>
        </div>
        """, unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        with a1:
            if st.button("🧮 New Analysis", use_container_width=True, type="primary", key="profile_calc"):
                st.session_state.page = "calculator"
                st.rerun()
        with a2:
            if st.button("📊 Dashboard", use_container_width=True, key="profile_dash"):
                st.session_state.page = "dashboard"
                st.rerun()

        # ── Change password ────────────────────────────────────────────────────
        st.markdown("""
        <div class="profile-card" style="margin-top:1rem;">
            <h4>🔑 Change Password</h4>
        </div>
        """, unsafe_allow_html=True)

        with st.form("change_password_form"):
            old_pw  = st.text_input("Current Password", type="password", placeholder="Enter current password")
            new_pw  = st.text_input("New Password", type="password",
                                    placeholder="Min. 8 chars · uppercase · lowercase · number · special")
            conf_pw = st.text_input("Confirm New Password", type="password", placeholder="Repeat new password")

            submitted = st.form_submit_button("Update Password →", use_container_width=True, type="primary")
            if submitted:
                if not old_pw or not new_pw or not conf_pw:
                    st.error("Please fill in all password fields.")
                elif new_pw != conf_pw:
                    st.error("New passwords don't match.")
                elif new_pw == old_pw:
                    st.warning("New password must be different from the current one.")
                else:
                    ok, msg = _change_password(email, old_pw, new_pw)
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

    # ── RIGHT: Loan history ────────────────────────────────────────────────────
    with right_col:
        st.markdown("""
        <div class="profile-card">
            <h4>📋 Loan Analysis History</h4>
        </div>
        """, unsafe_allow_html=True)

        history = _get_loan_history(email)

        if not history:
            st.markdown("""
            <div style="text-align:center;padding:3rem 1rem;background:rgba(255,255,255,0.6);
                        border:1px solid rgba(144,202,249,0.4);border-radius:16px;margin-top:-1rem;">
                <div style="font-size:2.5rem;margin-bottom:0.8rem;">📊</div>
                <div style="font-family:'Merriweather',serif;font-size:1rem;font-weight:800;
                            color:#1a2540;margin-bottom:0.4rem;">No Analyses Yet</div>
                <div style="font-size:0.85rem;color:#64748b;line-height:1.6;">
                    Run your first loan analysis to see your history here.<br>
                    All your past analyses are saved automatically.
                </div>
            </div>
            """, unsafe_allow_html=True)
            _, c, _ = st.columns([1, 2, 1])
            with c:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Run First Analysis →", use_container_width=True, type="primary", key="profile_first"):
                    st.session_state.page = "calculator"
                    st.rerun()
        else:
            st.markdown(f"""
            <div style="font-size:0.83rem;color:#64748b;margin:-0.8rem 0 1rem;">
                Showing your last {len(history)} analyses. Latest first.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="history-header">
                <span>Date</span>
                <span>Loan Amount</span>
                <span>EMI</span>
                <span>Risk Score</span>
                <span>Risk Level</span>
            </div>
            """, unsafe_allow_html=True)

            for row in history:
                date_str = str(row.get("timestamp", ""))[:10]
                risk_s   = int(row.get("risk_score", 0))
                risk_l   = row.get("risk_level", "—")
                cls      = "risk-low" if risk_s < 35 else "risk-medium" if risk_s < 60 else "risk-high"
                st.markdown(f"""
                <div class="history-row">
                    <span style="color:#64748b;font-weight:600;">{date_str}</span>
                    <span style="color:#1a2540;font-weight:700;">{_fmt(row.get("loan_amount",0))}</span>
                    <span style="color:#1a2540;font-weight:700;">{_fmt(row.get("emi",0))}/mo</span>
                    <span style="font-family:'Merriweather',serif;font-weight:900;color:#1a2540;">{risk_s}/100</span>
                    <span><span class="risk-pill {cls}">{risk_l}</span></span>
                </div>
                """, unsafe_allow_html=True)

            # Summary stats from history
            import statistics
            scores = [int(r.get("risk_score", 0)) for r in history if r.get("risk_score")]
            avg_score = round(statistics.mean(scores)) if scores else 0
            avg_cls   = "risk-low" if avg_score < 35 else "risk-medium" if avg_score < 60 else "risk-high"

            st.markdown(f"""
            <div style="margin-top:1.2rem;display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.8rem;">
                <div style="background:rgba(255,255,255,0.85);border:1px solid rgba(144,202,249,0.4);
                            border-radius:12px;padding:1rem;text-align:center;">
                    <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;
                                letter-spacing:0.07em;font-weight:700;margin-bottom:0.3rem;">Analyses Run</div>
                    <div style="font-family:'Merriweather',serif;font-size:1.4rem;
                                font-weight:900;color:#003399;">{len(history)}</div>
                </div>
                <div style="background:rgba(255,255,255,0.85);border:1px solid rgba(144,202,249,0.4);
                            border-radius:12px;padding:1rem;text-align:center;">
                    <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;
                                letter-spacing:0.07em;font-weight:700;margin-bottom:0.3rem;">Avg Risk Score</div>
                    <div style="font-family:'Merriweather',serif;font-size:1.4rem;
                                font-weight:900;color:#003399;">{avg_score}/100</div>
                </div>
                <div style="background:rgba(255,255,255,0.85);border:1px solid rgba(144,202,249,0.4);
                            border-radius:12px;padding:1rem;text-align:center;">
                    <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;
                                letter-spacing:0.07em;font-weight:700;margin-bottom:0.3rem;">Latest Risk</div>
                    <div style="font-family:'Merriweather',serif;font-size:1.4rem;
                                font-weight:900;color:#003399;">{scores[0] if scores else "—"}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)