"""
Crediwise — Auth Database Utility
Handles user registration and login using SQLite + PBKDF2-HMAC-SHA256.

Drop into utils/auth_db.py.  No external dependencies — uses only stdlib.
"""

import hashlib
import hmac
import os
import re
import sqlite3
from pathlib import Path


# ── Database path — sits next to this file's parent directory ────────────────
_DB_DIR  = Path(__file__).parent.parent / "data"
_DB_PATH = _DB_DIR / "crediwise_users.db"


def _get_conn() -> sqlite3.Connection:
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the users table if it doesn't exist. Call once at app startup."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                email      TEXT    UNIQUE NOT NULL COLLATE NOCASE,
                first_name TEXT    NOT NULL,
                last_name  TEXT    NOT NULL,
                phone      TEXT,
                city       TEXT,
                pan        TEXT,
                pw_hash    TEXT    NOT NULL,
                pw_salt    TEXT    NOT NULL,
                created_at TEXT    DEFAULT (datetime('now'))
            )
        """)
        conn.commit()


# ── Password utilities ────────────────────────────────────────────────────────

def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    """
    Hash a password with PBKDF2-HMAC-SHA256 (310,000 iterations — OWASP 2023).
    Returns (hex_hash, hex_salt).
    """
    if salt is None:
        salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations=310_000,
    )
    return key.hex(), salt.hex()


def _verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    salt      = bytes.fromhex(stored_salt)
    computed, _ = _hash_password(password, salt)
    return hmac.compare_digest(computed, stored_hash)


# ── Validation ────────────────────────────────────────────────────────────────

class PasswordError(ValueError):
    pass


def validate_password(password: str) -> list[str]:
    """
    Returns a list of unmet requirements (empty list = valid).
    Rules: ≥8 chars, uppercase, lowercase, digit, special character.
    """
    errors = []
    if len(password) < 8:
        errors.append("At least 8 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("At least one uppercase letter (A–Z)")
    if not re.search(r"[a-z]", password):
        errors.append("At least one lowercase letter (a–z)")
    if not re.search(r"\d", password):
        errors.append("At least one number (0–9)")
    if not re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>?/\\|`~]', password):
        errors.append("At least one special character (!@#$%^&* etc.)")
    return errors


# ── Public API ────────────────────────────────────────────────────────────────

def register_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    phone: str = "",
    city: str  = "",
    pan: str   = "",
) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success: bool, message: str).
    """
    # Validate password strength
    errs = validate_password(password)
    if errs:
        return False, "Password does not meet requirements:\n• " + "\n• ".join(errs)

    pw_hash, pw_salt = _hash_password(password)

    try:
        with _get_conn() as conn:
            conn.execute(
                """INSERT INTO users
                   (email, first_name, last_name, phone, city, pan, pw_hash, pw_salt)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (email.lower().strip(), first_name.strip(), last_name.strip(),
                 phone.strip(), city.strip(), pan.strip().upper(),
                 pw_hash, pw_salt),
            )
            conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists. Please log in."
    except Exception as e:
        return False, f"Registration failed: {e}"


def login_user(email: str, password: str) -> tuple[bool, str, dict]:
    """
    Attempt login.
    Returns (success: bool, message: str, user_data: dict).
    user_data keys: email, first_name, last_name, city
    """
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email.lower().strip(),),
            ).fetchone()
    except Exception as e:
        return False, f"Database error: {e}", {}

    if row is None:
        # Generic message — don't reveal whether email exists
        return False, "Invalid email or password.", {}

    if not _verify_password(password, row["pw_hash"], row["pw_salt"]):
        return False, "Invalid email or password.", {}

    user_data = {
        "email":      row["email"],
        "first_name": row["first_name"],
        "last_name":  row["last_name"],
        "city":       row["city"],
    }
    return True, "Login successful.", user_data


def email_exists(email: str) -> bool:
    """Quick check used for real-time feedback during signup."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE email = ?",
            (email.lower().strip(),),
        ).fetchone()
    return row is not None
