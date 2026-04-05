"""
utils/oauth_handler.py

Handles Google OAuth 2.0 login flow for Streamlit.

Install dependencies:
    pip install requests python-dotenv

How the flow works:
    1. User clicks "Continue with Google"
    2. We redirect them to Google login page (get_google_auth_url)
    3. After login, Google redirects back to your app with a ?code= parameter in the URL
    4. We exchange that code for an access token (handle_google_callback)
    5. We use the token to fetch the user's name and email
    6. We log them in (create account if first time, or sign in if they exist)
"""

import os
import urllib.parse
import requests
from pathlib import Path

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass  # dotenv not installed — rely on system environment variables


# ── Config ────────────────────────────────────────────────────────────────────

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

APP_URL = os.getenv("APP_URL", "http://localhost:8501")

GOOGLE_REDIRECT_URI = APP_URL
GOOGLE_SCOPES       = "openid email profile"

GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO  = "https://www.googleapis.com/oauth2/v3/userinfo"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _credentials_configured() -> bool:
    """Returns True if Google credentials are set in the .env file."""
    return bool(
        GOOGLE_CLIENT_ID
        and GOOGLE_CLIENT_SECRET
        and "your_google" not in GOOGLE_CLIENT_ID
    )


# ── Google ────────────────────────────────────────────────────────────────────

def get_google_auth_url(state: str = "google_oauth") -> str | None:
    """
    Returns the URL to redirect the user to for Google login.
    Returns None if credentials are not configured in .env.
    """
    if not _credentials_configured():
        return None

    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         GOOGLE_SCOPES,
        "state":         state,
        "access_type":   "online",
        "prompt":        "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"


def handle_google_callback(code: str) -> tuple[bool, str, dict]:
    """
    Exchange the OAuth code for user info.
    Returns (success, message, user_data).
    user_data keys: email, first_name, last_name, provider
    """
    try:
        # Step 1: Exchange code for tokens
        token_resp = requests.post(GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri":  GOOGLE_REDIRECT_URI,
            "grant_type":    "authorization_code",
        }, timeout=10)
        token_resp.raise_for_status()
        tokens = token_resp.json()

        # Step 2: Fetch user info
        userinfo_resp = requests.get(
            GOOGLE_USERINFO,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            timeout=10,
        )
        userinfo_resp.raise_for_status()
        info = userinfo_resp.json()

        user_data = {
            "email":      info.get("email", ""),
            "first_name": info.get("given_name", info.get("name", "User").split()[0]),
            "last_name":  info.get("family_name", ""),
            "provider":   "google",
        }
        return True, "Google login successful.", user_data

    except requests.HTTPError as e:
        return False, f"Google auth failed: {e.response.status_code} — {e.response.text}", {}
    except Exception as e:
        return False, f"Google auth error: {e}", {}


# ── Shared: register or login OAuth user ─────────────────────────────────────

def oauth_login_or_register(user_data: dict) -> tuple[bool, str]:
    """
    Called after successful OAuth.
    - If the email already exists in DB → logs them in.
    - If not → creates account with a random password (OAuth-only account).
    Returns (success, message).
    """
    import streamlit as st
    from utils.auth_db import init_db, email_exists, register_user

    init_db()

    email      = user_data["email"]
    first_name = user_data["first_name"]
    last_name  = user_data.get("last_name", "")

    if not email:
        return False, "Could not retrieve email from Google. Please use email/password login."

    if email_exists(email):
        _set_session(first_name, email)
        return True, f"Welcome back, {first_name}!"
    else:
        import secrets
        random_pw = secrets.token_urlsafe(32) + "Aa1!"  # meets all password rules
        ok, msg = register_user(
            email=email,
            password=random_pw,
            first_name=first_name,
            last_name=last_name,
            phone="",
            city="",
            pan="",
        )
        if ok:
            _set_session(first_name, email)
            return True, f"Account created. Welcome, {first_name}!"
        else:
            return False, msg


def _set_session(first_name: str, email: str) -> None:
    import streamlit as st
    st.session_state.logged_in  = True
    st.session_state.username   = first_name.capitalize()
    st.session_state.user_email = email