import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sessions.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_email TEXT DEFAULT '',
            income REAL,
            expenses REAL,
            existing_emi REAL,
            loan_amount REAL,
            tenure INTEGER,
            interest_rate REAL,
            credit_score INTEGER,
            risk_score INTEGER,
            risk_level TEXT,
            emi REAL,
            safe_emi REAL,
            max_loan REAL
        )
    """)
    # Add user_email column to existing DBs that don't have it yet
    try:
        c.execute("ALTER TABLE sessions ADD COLUMN user_email TEXT DEFAULT ''")
    except Exception:
        pass  # Column already exists — fine
    conn.commit()
    conn.close()

def save_session(data: dict, risk_score: int, risk_level: str, emi: float,
                 safe_emi: float, max_loan: float, user_email: str = ""):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sessions (
            timestamp, user_email, income, expenses, existing_emi,
            loan_amount, tenure, interest_rate, credit_score,
            risk_score, risk_level, emi, safe_emi, max_loan
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        user_email,
        data.get("income"), data.get("expenses"), data.get("existing_emi"),
        data.get("loan_amount"), data.get("tenure"), data.get("interest_rate"),
        data.get("credit_score"), risk_score, risk_level, emi, safe_emi, max_loan
    ))
    conn.commit()
    conn.close()

def get_all_sessions():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    import pandas as pd
    df = pd.read_sql("SELECT * FROM sessions ORDER BY timestamp DESC LIMIT 50", conn)
    conn.close()
    return df
