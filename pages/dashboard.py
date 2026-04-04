import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib

from utils.calculator import (
    calculate_emi,
    calculate_safe_emi,
    calculate_max_loan,
    calculate_total_interest,
)
from utils.risk_engine import compute_risk_score, get_risk_level
from utils.explainer import explain_risk


# ── Plotly layout — light theme ───────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(255,255,255,0.0)",
    plot_bgcolor="rgba(255,255,255,0.0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#1a2540", size=12),
    margin=dict(l=0, r=0, t=36, b=0),
    legend=dict(
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="rgba(144,202,249,0.4)",
        borderwidth=1,
        font=dict(size=11, color="#334155"),
    ),
    xaxis=dict(
        gridcolor="rgba(144,202,249,0.25)",
        showline=False, zeroline=False,
        tickfont=dict(color="#475569"),
    ),
    yaxis=dict(
        gridcolor="rgba(144,202,249,0.25)",
        showline=False, zeroline=False,
        tickfont=dict(color="#475569"),
    ),
)


def _fmt(n: float) -> str:
    return f"₹{n:,.0f}"


# ── ML helpers ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_ml_model():
    model_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "model", "loan_risk_model.pkl"
    )
    if os.path.exists(model_path):
        try:
            return joblib.load(model_path)
        except Exception:
            return None
    return None


def ml_default_probability(model, income, loan_amt, interest_rate, credit_history):
    if model is None:
        return None
    try:
        features = pd.DataFrame([{
            "person_income":              income * 12,
            "loan_amnt":                  loan_amt,
            "loan_int_rate":              interest_rate,
            "loan_percent_income":        loan_amt / (income * 12) if income > 0 else 1.0,
            "cb_person_cred_hist_length": credit_history,
        }])
        prob = float(model.predict_proba(features)[0][1])
        return prob
    except Exception as e:
        st.session_state["ml_error"] = str(e)
        return None


# FIX 1: Normalize ml_prob to 0-100 before blending
# Old: ml_prob * 60 + rule_score * 0.4  (ml maxed at 60, not 100)
# New: ml_prob * 100 * 0.6 + rule_score * 0.4  (both properly weighted)
def blended_risk_score(rule_score: int, ml_prob) -> int:
    if ml_prob is None:
        return rule_score
    ml_score = ml_prob * 100          # normalize probability 0–1 → 0–100
    blended  = ml_score * 0.6 + rule_score * 0.4
    return int(min(100, max(0, blended)))


# FIX 2: Rewritten compute_all_plans with correct ML Pick logic
# Old: looped tenures, same ml_prob for all → longest tenure always won (lower debt ratio)
# New: ml_prob is computed ONCE (it doesn't vary by tenure), tenure selection uses
#      smart rules: prefer shorter tenure that saves interest & stays affordable;
#      only suggest longer tenure if it gives 5+ point risk improvement
@st.cache_data
def compute_all_plans(income, expenses, existing_emi, loan_amount, tenure,
                      interest_rate, credit_score, credit_history, savings, _ml_active):
    model = load_ml_model()

    # ML probability is fixed for this borrower profile — tenure doesn't affect it
    ml_prob   = ml_default_probability(model, income, loan_amount, interest_rate, credit_history)
    user_rule = compute_risk_score(income, expenses, existing_emi, loan_amount, tenure,
                                   interest_rate, credit_score, credit_history, savings)
    user_risk = blended_risk_score(user_rule, ml_prob)

    TENURE_OPTIONS = [24, 36, 48, 60, 72, 84, 96, 120]
    safe_emi       = calculate_safe_emi(income, expenses, existing_emi)
    user_emi       = calculate_emi(loan_amount, interest_rate, tenure)
    user_int       = calculate_total_interest(loan_amount, user_emi, tenure)

    best_plan = None

    # Priority 1: Find a SHORTER tenure that saves interest and stays affordable
    for t in sorted(TENURE_OPTIONS):
        if t >= tenure:
            continue                        # only consider shorter tenures here
        candidate_emi  = calculate_emi(loan_amount, interest_rate, t)
        candidate_rule = compute_risk_score(income, expenses, existing_emi, loan_amount, t,
                                            interest_rate, credit_score, credit_history, savings)
        candidate_risk = blended_risk_score(candidate_rule, ml_prob)
        candidate_int  = calculate_total_interest(loan_amount, candidate_emi, t)

        emi_affordable    = candidate_emi <= safe_emi * 1.1   # 10% buffer on safe EMI
        saves_interest    = candidate_int < user_int           # strictly cheaper overall
        doesnt_raise_risk = candidate_risk <= user_risk        # must not worsen risk

        if emi_affordable and saves_interest and doesnt_raise_risk:
            best_plan = (loan_amount, t, candidate_emi, candidate_risk)
            break   # take the shortest valid tenure

    # Priority 2: Try a LONGER tenure — only if it meaningfully cuts risk by 5+ points
    if best_plan is None:
        for t in sorted(TENURE_OPTIONS, reverse=True):
            if t <= tenure:
                continue                    # only consider longer tenures here
            candidate_emi  = calculate_emi(loan_amount, interest_rate, t)
            candidate_rule = compute_risk_score(income, expenses, existing_emi, loan_amount, t,
                                                interest_rate, credit_score, credit_history, savings)
            candidate_risk = blended_risk_score(candidate_rule, ml_prob)

            emi_affordable  = candidate_emi <= safe_emi * 1.1
            # Must drop risk by at least 5 points to justify paying more interest
            meaningful_risk = (user_risk - candidate_risk) >= 5

            if emi_affordable and meaningful_risk:
                best_plan = (loan_amount, t, candidate_emi, candidate_risk)
                break

    # Priority 3: Fallback — no better option found, return user's own plan
    if best_plan is None:
        best_plan = (loan_amount, tenure, user_emi, user_risk)

    return best_plan, user_risk


# ── Amortisation helpers ──────────────────────────────────────────────────────
def build_amortization_schedule(principal: float, annual_rate: float, tenure_months: int) -> list:
    monthly_rate  = annual_rate / (12 * 100)
    scheduled_emi = (
        principal / tenure_months if monthly_rate == 0
        else principal * monthly_rate * (1 + monthly_rate) ** tenure_months
             / ((1 + monthly_rate) ** tenure_months - 1)
    )
    schedule, balance = [], principal
    for m in range(1, tenure_months + 1):
        interest_c  = balance * monthly_rate
        principal_c = scheduled_emi - interest_c
        balance    -= principal_c
        balance     = max(0.0, balance)
        schedule.append({
            "month": m, "scheduled_emi": round(scheduled_emi, 2),
            "principal_component": round(principal_c, 2),
            "interest_component":  round(interest_c, 2),
            "closing_balance":     round(balance, 2),
            # FIX 5 (part 1): Store original interest component for accurate savings calc
            "original_interest":   round(interest_c, 2),
            "paid_amount": None, "status": "future",
            "interest_saved": 0.0, "months_reduced": 0,
        })
    return schedule


def recalculate_from_month(schedule: list, from_month: int, annual_rate: float) -> list:
    monthly_rate = annual_rate / (12 * 100)
    idx          = from_month - 1
    row          = schedule[idx]
    paid         = row.get("paid_amount") or row["scheduled_emi"]
    prev_balance = (schedule[idx - 1]["closing_balance"] if idx > 0
                    else row["closing_balance"] + row["principal_component"])
    interest_this  = prev_balance * monthly_rate
    principal_paid = max(0.0, paid - interest_this)
    actual_closing = max(0.0, prev_balance - principal_paid)
    schedule[idx].update({
        "closing_balance":     round(actual_closing, 2),
        "interest_component":  round(interest_this, 2),
        "principal_component": round(principal_paid, 2),
    })
    remaining_balance = actual_closing
    if remaining_balance <= 0:
        return schedule[:from_month]
    remaining_months = len(schedule) - from_month
    if remaining_months <= 0:
        return schedule
    new_emi = (
        remaining_balance / remaining_months if monthly_rate == 0
        else remaining_balance * monthly_rate * (1 + monthly_rate) ** remaining_months
             / ((1 + monthly_rate) ** remaining_months - 1)
    )
    balance = remaining_balance
    for i in range(from_month, len(schedule)):
        interest_c  = balance * monthly_rate
        principal_c = new_emi - interest_c
        balance    -= principal_c
        balance     = max(0.0, balance)
        schedule[i].update({
            "scheduled_emi": round(new_emi, 2),
            "principal_component": round(principal_c, 2),
            "interest_component":  round(interest_c, 2),
            "closing_balance":     round(balance, 2),
            "paid_amount": None, "status": "future",
        })
    return schedule


# ═════════════════════════════════════════════════════════════════════════════
def show():
    data = st.session_state.get("form_data", {})

    if not data.get("income") or not data.get("loan_amount"):
        st.markdown("""
        <div style="text-align:center;padding:5rem 2rem;">
            <div style="font-size:3.5rem;margin-bottom:1rem;">📋</div>
            <h3 style="font-family:'Merriweather',serif;color:#1a2540;margin:0 0 0.6rem;">No Analysis Yet</h3>
            <p style="color:#475569;font-size:0.95rem;">
                Please complete the calculator first to view your personalised loan analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("Go to Calculator →", use_container_width=True, type="primary"):
                st.session_state.page = "calculator"; st.rerun()
        return

    # ── Unpack inputs ─────────────────────────────────────────────────────────
    income         = float(data["income"])
    expenses       = float(data["expenses"])
    existing_emi   = float(data["existing_emi"])
    savings        = float(data.get("savings", 0))
    credit_score   = int(data.get("credit_score", 700))
    credit_history = int(data.get("credit_history", 5))
    loan_amount    = float(data["loan_amount"])
    tenure         = int(data["tenure"])
    interest_rate  = float(data["interest_rate"])
    loan_type      = data.get("loan_type", "Personal Loan")
    employment     = data.get("employment", "Salaried")

    # ── Core calculations ─────────────────────────────────────────────────────
    emi        = calculate_emi(loan_amount, interest_rate, tenure)
    safe_emi   = calculate_safe_emi(income, expenses, existing_emi)
    max_loan   = calculate_max_loan(safe_emi, interest_rate, tenure)
    total_int  = calculate_total_interest(loan_amount, emi, tenure)
    disposable = income - expenses - existing_emi
    debt_ratio = ((existing_emi + emi) / income * 100) if income > 0 else 100
    emi_ratio  = (emi / income * 100) if income > 0 else 0

    # ── ML + cached plans ─────────────────────────────────────────────────────
    ml_model  = load_ml_model()
    ml_active = ml_model is not None

    # Show ML error if model loaded but predict_proba failed silently
    if st.session_state.get("ml_error"):
        st.warning(f"⚠️ ML model loaded but prediction failed: {st.session_state['ml_error']}")

    exact_plan, risk_score = compute_all_plans(
        income, expenses, existing_emi, loan_amount, tenure,
        interest_rate, credit_score, credit_history, savings, ml_active,
    )
    risk_level, risk_color, risk_bg, risk_icon = get_risk_level(risk_score)

    # ── Build plan cards ──────────────────────────────────────────────────────
    plan_cards = []

    if exact_plan:
        e_amt, e_ten, e_emi, e_risk = exact_plan
        _, e_col, e_bg, _ = get_risk_level(e_risk)

        # FIX 3: Badge text reflects actual outcome, not always "ML Recommended"
        same_as_user = (e_ten == tenure)
        risk_drop    = risk_score - e_risk
        e_int        = calculate_total_interest(e_amt, e_emi, e_ten)
        saves_money  = e_int < total_int

        if same_as_user:
            badge_text = "✅ Your Plan is Already Optimal"
            badge_cls  = "badge-current"
        elif saves_money and risk_drop >= 0:
            badge_text = f"{'🤖 ML Recommended' if ml_active else 'Best Pick'} ★"
            badge_cls  = "badge-best"
        elif risk_drop >= 5:
            badge_text = f"{'🤖 ML Risk Pick' if ml_active else 'Lower Risk Pick'}"
            badge_cls  = "badge-best"
        else:
            badge_text = "💡 Alternative Option"
            badge_cls  = "badge-current"

        plan_cards.append({
            "label":      "ML Pick" if ml_active else "Best Pick",
            "badge":      badge_cls,
            "badge_text": badge_text,
            "amount":     e_amt,
            "tenure":     e_ten,
            "emi":        e_emi,
            "risk":       e_risk,
            "interest":   e_int,
            "color":      e_col,
            "bg":         e_bg,
            "reduction":  risk_score - e_risk,
        })
    else:
        plan_cards.append(None)

    _, y_col, y_bg, _ = get_risk_level(risk_score)
    plan_cards.append({
        "label": "Your Plan", "badge": "badge-current", "badge_text": "Your Request",
        "amount": loan_amount, "tenure": tenure, "emi": emi, "risk": risk_score,
        "interest": total_int, "color": y_col, "bg": y_bg, "reduction": 0,
    })

    if "selected_plan_idx" not in st.session_state:
        st.session_state.selected_plan_idx = 0

    sel_idx   = st.session_state.selected_plan_idx
    active_pc = (plan_cards[sel_idx]
                 if sel_idx is not None and plan_cards[sel_idx]
                 else plan_cards[1])
    active_label = active_pc["label"]

    # ── CSS — light theme (matches existing dashboard) ────────────────────────
    st.markdown("""
    <style>
    .db-wrap { padding: 2rem 2.5rem; }

    .db-header { margin-bottom: 1.6rem; }
    .db-header h2 {
        font-family: 'Merriweather', serif;
        font-size: 1.8rem; font-weight: 900;
        color: #1a2540; margin: 0 0 0.2rem;
        letter-spacing: -0.02em;
    }
    .db-header .sub { font-size: 0.88rem; color: #475569; font-weight: 500; }

    /* ML badge */
    .ml-badge {
        display: inline-flex; align-items: center; gap: 0.4rem;
        padding: 0.35rem 1rem; border-radius: 100px;
        font-size: 0.78rem; font-weight: 700;
        background: rgba(0,51,153,0.08); color: #003399;
        border: 1px solid rgba(0,51,153,0.2); margin-bottom: 1.2rem;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .ml-badge-warn {
        background: rgba(245,158,11,0.12); color: #92400e;
        border-color: rgba(245,158,11,0.35);
    }

    /* Risk banner */
    .risk-banner {
        border-radius: 18px; padding: 1.6rem 2rem;
        display: flex; align-items: center; gap: 2rem;
        margin-bottom: 1.6rem; border: 1px solid;
        position: relative; overflow: hidden;
        backdrop-filter: blur(12px);
    }
    .risk-score-big {
        font-family: 'Merriweather', serif;
        font-size: 3.6rem; font-weight: 900;
        line-height: 1; flex-shrink: 0;
    }
    .risk-divider { width:1px; height:60px; background:rgba(0,0,0,0.1); flex-shrink:0; }
    .risk-label { font-family:'Merriweather',serif; font-size:1.2rem; font-weight:800; margin-bottom:0.3rem; }
    .risk-desc { font-size:0.88rem; color:#334155; line-height:1.6; max-width:460px; }
    .risk-badge {
        margin-left:auto; padding:0.35rem 1.1rem; border-radius:100px;
        font-size:0.78rem; font-weight:700; border:1px solid;
        flex-shrink:0; white-space:nowrap; font-family:'Plus Jakarta Sans',sans-serif;
    }

    /* KPI strip */
    .kpi-strip { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:1.6rem; }
    .kpi-card {
        background:rgba(255,255,255,0.82); backdrop-filter:blur(12px);
        border:1px solid rgba(144,202,249,0.4); border-radius:16px;
        padding:1.2rem 1.3rem; position:relative; overflow:hidden;
        box-shadow:0 2px 12px rgba(0,51,153,0.06);
    }
    .kpi-lbl {
        font-size:0.72rem; color:#64748b; text-transform:uppercase;
        letter-spacing:0.09em; margin-bottom:0.5rem; font-weight:700;
        font-family:'Plus Jakarta Sans',sans-serif;
    }
    .kpi-val {
        font-family:'Merriweather',serif; font-size:1.45rem; font-weight:900;
        color:#1a2540; line-height:1.1;
    }
    .kpi-sub { font-size:0.76rem; color:#64748b; margin-top:0.2rem; font-weight:500; }
    .kpi-icon { position:absolute; top:1rem; right:1rem; font-size:1.3rem; opacity:0.35; }

    /* Section title */
    .sec-title {
        font-family:'Merriweather',serif; font-size:0.95rem; font-weight:800;
        color:#1a2540; margin:0 0 1rem;
        display:flex; align-items:center; gap:0.5rem;
    }

    /* Score factor bars */
    .factor-name { font-size:0.82rem; color:#334155; font-weight:600; }
    .factor-val  { font-size:0.82rem; font-weight:700; }
    .factor-bar-bg { height:9px; background:rgba(144,202,249,0.25); border-radius:5px; overflow:hidden; margin-top:5px; }
    .factor-bar-fill { height:100%; border-radius:5px; transition:width 0.4s; }

    /* Explainer cards */
    .exp-card {
        border-radius:12px; padding:0.9rem 1.1rem;
        margin-bottom:0.75rem; border-left:4px solid;
        font-size:0.86rem; line-height:1.65; font-weight:500;
        font-family:'Plus Jakarta Sans',sans-serif;
    }
    .exp-high   { background:rgba(254,226,226,0.8); border-color:#ef4444; color:#991b1b; }
    .exp-medium { background:rgba(254,243,199,0.8); border-color:#f59e0b; color:#92400e; }
    .exp-low    { background:rgba(220,252,231,0.8); border-color:#22c55e; color:#166534; }

    /* Plan suggestion cards */
    .plan-card-wrap {
        background:rgba(255,255,255,0.82); backdrop-filter:blur(12px);
        border:1.5px solid rgba(144,202,249,0.4); border-radius:18px;
        padding:1.4rem; box-shadow:0 2px 12px rgba(0,51,153,0.06);
    }
    .plan-card-wrap.selected {
        border:2px solid #22c55e;
        background:rgba(220,252,231,0.5);
    }
    .plan-card-badge {
        display:inline-block; padding:0.25rem 0.75rem; border-radius:100px;
        font-size:0.74rem; font-weight:700; margin-bottom:0.9rem; letter-spacing:0.04em;
        font-family:'Plus Jakarta Sans',sans-serif;
    }
    .badge-best    { background:rgba(0,51,153,0.12); color:#003399; }
    .badge-current { background:rgba(245,158,11,0.15); color:#92400e; }

    .plan-amount { font-family:'Merriweather',serif; font-size:1.45rem; font-weight:900;
                   color:#1a2540; margin-bottom:0.2rem; }
    .plan-meta   { font-size:0.84rem; color:#64748b; margin-bottom:1rem; font-weight:500; }
    .plan-row    { display:flex; justify-content:space-between; font-size:0.84rem;
                   padding:0.4rem 0; border-bottom:1px solid rgba(144,202,249,0.25); }
    .plan-row:last-child { border-bottom:none; }
    .plan-row .pr-l { color:#475569; font-weight:500; }
    .plan-row .pr-v { font-weight:700; color:#1a2540; font-family:'Merriweather',serif; }

    /* Active plan banner */
    .active-plan-banner {
        background:rgba(219,234,254,0.8); border:1px solid rgba(59,130,246,0.3);
        border-radius:12px; padding:0.9rem 1.2rem; margin-bottom:1.2rem;
        font-size:0.88rem; color:#1e40af; font-weight:600;
        display:flex; align-items:center; gap:0.6rem;
    }

    /* Risk reduction panel */
    .rrp {
        background:rgba(220,252,231,0.6); border:1px solid rgba(34,197,94,0.3);
        border-radius:18px; padding:1.8rem 2rem; margin-top:1.2rem;
    }
    .rrp-title { font-family:'Merriweather',serif; font-size:1rem; font-weight:800;
                 color:#15803d; margin-bottom:1.2rem; }
    .rrp-score-row { display:flex; align-items:center; gap:1.2rem; margin-bottom:1.2rem; }
    .rrp-score-box { text-align:center; padding:0.9rem 1.2rem; border-radius:14px; min-width:85px; }
    .rrp-score-label { font-size:0.72rem; color:#475569; text-transform:uppercase;
                       letter-spacing:0.07em; margin-bottom:0.3rem; font-weight:700; }
    .rrp-score-num   { font-family:'Merriweather',serif; font-size:1.9rem; font-weight:900; }
    .rrp-arrow       { font-size:1.5rem; color:#22c55e; font-weight:700; }
    .rrp-bar-wrap    { margin-bottom:0.9rem; }
    .rrp-bar-label   { display:flex; justify-content:space-between; font-size:0.82rem;
                       color:#334155; margin-bottom:0.3rem; font-weight:600; }
    .rrp-bar-bg      { height:9px; background:rgba(144,202,249,0.25); border-radius:5px; overflow:hidden; }
    .rrp-bar-fill    { height:9px; border-radius:5px; }
    .rrp-savings-row { display:grid; grid-template-columns:repeat(3,1fr); gap:0.8rem; margin-top:1.2rem; }
    .rrp-sav-card    {
        background:rgba(255,255,255,0.85); border:1px solid rgba(144,202,249,0.4);
        border-radius:12px; padding:0.9rem; text-align:center;
    }
    .rrp-sav-label { font-size:0.72rem; color:#64748b; margin-bottom:0.25rem;
                     text-transform:uppercase; letter-spacing:0.06em; font-weight:700; }
    .rrp-sav-val   { font-family:'Merriweather',serif; font-size:1rem; font-weight:900; color:#1a2540; }

    /* Debt ratio summary box */
    .debt-box {
        margin-top:1.1rem; padding:1rem 1.2rem;
        background:rgba(255,255,255,0.85); border:1px solid rgba(144,202,249,0.4);
        border-radius:14px; backdrop-filter:blur(8px);
    }
    .debt-box-lbl { font-size:0.72rem; color:#64748b; text-transform:uppercase;
                    letter-spacing:0.07em; font-weight:700; margin-bottom:0.25rem; }
    .debt-box-val { font-family:'Merriweather',serif; font-size:1.5rem; font-weight:900; line-height:1.1; }
    .debt-box-sub { font-size:0.78rem; color:#64748b; margin-top:0.15rem; }

    /* Stress note boxes */
    .stress-note {
        padding:1rem 1.3rem; border-radius:12px;
        font-size:0.87rem; line-height:1.65; font-weight:500;
        font-family:'Plus Jakarta Sans',sans-serif; margin-top:0.8rem;
    }

    /* Comparison metric cards */
    .cmp-card {
        background:rgba(255,255,255,0.82); border:1px solid rgba(144,202,249,0.4);
        border-radius:16px; padding:1rem; text-align:center;
        box-shadow:0 2px 10px rgba(0,51,153,0.05);
    }
    .cmp-lbl { font-size:0.68rem; color:#64748b; text-transform:uppercase;
               letter-spacing:0.07em; margin-bottom:0.5rem; font-weight:700; }
    .cmp-row-lbl { font-size:0.76rem; color:#94a3b8; margin-bottom:2px; }
    .cmp-row-val { font-family:'Merriweather',serif; font-size:0.92rem;
                   font-weight:800; color:#1a2540; margin-bottom:0.4rem; }

    /* Tracker */
    .tracker-summary { display:grid; grid-template-columns:repeat(5,1fr); gap:0.8rem; margin-bottom:1.4rem; }
    .tracker-card {
        background:rgba(255,255,255,0.82); border:1px solid rgba(144,202,249,0.4);
        border-radius:14px; padding:1rem 1.1rem; text-align:center;
        box-shadow:0 2px 8px rgba(0,51,153,0.05);
    }
    .tc-label { font-size:0.7rem; color:#64748b; text-transform:uppercase;
                letter-spacing:0.07em; margin-bottom:0.35rem; font-weight:700; }
    .tc-val   { font-family:'Merriweather',serif; font-size:1.1rem; font-weight:900; color:#1a2540; }
    .tc-green { color:#15803d; }
    .tc-red   { color:#dc2626; }
    .tc-blue  { color:#1d4ed8; }
    .tc-amber { color:#b45309; }

    .legend-row  { display:flex; gap:1.2rem; margin-bottom:1rem; flex-wrap:wrap; }
    .legend-item { display:flex; align-items:center; gap:0.4rem; font-size:0.82rem;
                   color:#334155; font-weight:600; }
    .legend-dot  { width:10px; height:10px; border-radius:3px; flex-shrink:0; }

    .alert-box     { padding:0.9rem 1.2rem; border-radius:12px; font-size:0.87rem;
                     line-height:1.65; margin-bottom:0.9rem; border:1px solid; font-weight:500; }
    .alert-danger  { background:rgba(254,226,226,0.8); border-color:rgba(239,68,68,0.35); color:#991b1b; }
    .alert-success { background:rgba(220,252,231,0.8); border-color:rgba(34,197,94,0.35); color:#166534; }
    .alert-info    { background:rgba(219,234,254,0.8); border-color:rgba(59,130,246,0.35); color:#1e40af; }
    .alert-warning { background:rgba(254,243,199,0.8); border-color:rgba(245,158,11,0.35); color:#92400e; }

    /* Tabs */
    div[data-testid="stTabs"] button {
        font-family:'Plus Jakarta Sans',sans-serif !important;
        font-weight:600 !important; color:#475569 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color:#003399 !important; font-weight:700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="db-wrap">', unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="db-header">
        <h2>Your Loan Analysis</h2>
        <div class="sub">{loan_type} · {employment} · ₹{loan_amount:,.0f} over {tenure} months @ {interest_rate}% p.a.</div>
    </div>
    """, unsafe_allow_html=True)

    # ML badge
    if ml_active:
        ml_label = "🤖 ML Model Active — Risk scores powered by Random Forest trained on 28,000+ real credit records"
        ml_cls   = "ml-badge"
    else:
        ml_label = "⚙️ Rule-based scoring active — Add loan_risk_model.pkl to /model/ to enable ML predictions"
        ml_cls   = "ml-badge ml-badge-warn"
    st.markdown(f'<div class="{ml_cls}">{ml_label}</div>', unsafe_allow_html=True)

    # ── Risk Banner ───────────────────────────────────────────────────────────
    risk_desc_map = {
        "Low Risk":      "Your financial profile looks healthy. You are in a strong position to service this loan comfortably.",
        "Moderate Risk": "Some concerns exist in your profile. Consider adjusting loan terms for a safer outcome.",
        "High Risk":     "Significant stress indicators detected. This loan may be difficult to service without financial strain.",
    }
    st.markdown(f"""
    <div class="risk-banner" style="background:{risk_bg}; border-color:{risk_color}44;">
        <div class="risk-score-big" style="color:{risk_color};">{risk_score}</div>
        <div class="risk-divider"></div>
        <div>
            <div class="risk-label" style="color:{risk_color};">{risk_icon} {risk_level}</div>
            <div class="risk-desc">{risk_desc_map.get(risk_level,'')}</div>
        </div>
        <div class="risk-badge" style="color:{risk_color};border-color:{risk_color}55;background:rgba(255,255,255,0.7);">
            Risk Score / 100
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Strip ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="kpi-strip">
        <div class="kpi-card" style="border-top:3px solid #3b82f6;">
            <div class="kpi-icon">💳</div>
            <div class="kpi-lbl">Monthly EMI</div>
            <div class="kpi-val">{_fmt(emi)}</div>
            <div class="kpi-sub">{emi_ratio:.1f}% of income</div>
        </div>
        <div class="kpi-card" style="border-top:3px solid #22c55e;">
            <div class="kpi-icon">✅</div>
            <div class="kpi-lbl">Safe EMI Capacity</div>
            <div class="kpi-val">{_fmt(safe_emi)}</div>
            <div class="kpi-sub">40% of disposable</div>
        </div>
        <div class="kpi-card" style="border-top:3px solid #f59e0b;">
            <div class="kpi-icon">🏦</div>
            <div class="kpi-lbl">Max Affordable Loan</div>
            <div class="kpi-val">{_fmt(max_loan)}</div>
            <div class="kpi-sub">At {interest_rate}% for {tenure}m</div>
        </div>
        <div class="kpi-card" style="border-top:3px solid #ef4444;">
            <div class="kpi-icon">💰</div>
            <div class="kpi-lbl">Total Interest</div>
            <div class="kpi-val">{_fmt(total_int)}</div>
            <div class="kpi-sub">Over {tenure} months</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab4, tab5, tab6 = st.tabs([
        "Risk Deep-Dive",
        "Stress Timeline",
        "Plan Suggestions",
        "Plan Comparison",
        "Repayment Tracker",
    ])

    # ════════════════════════════════════════════════════════════════
    # TAB 1 — Risk Deep-Dive
    # ════════════════════════════════════════════════════════════════
    with tab1:
        c1, c2, c3 = st.columns([1, 1, 1.1], gap="large")

        with c1:
            st.markdown('<div class="sec-title">Risk Gauge</div>', unsafe_allow_html=True)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=risk_score,
                number={"font": {"family": "Merriweather", "size": 42, "color": risk_color}, "suffix": "/100"},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 0,
                             "tickfont": {"color": "#64748b", "size": 10}},
                    "bar":       {"color": risk_color, "thickness": 0.28},
                    "bgcolor":   "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0,  35],  "color": "rgba(34,197,94,0.12)"},
                        {"range": [35, 60],  "color": "rgba(245,158,11,0.12)"},
                        {"range": [60, 100], "color": "rgba(239,68,68,0.12)"},
                    ],
                    "threshold": {"line": {"color": risk_color, "width": 3},
                                  "thickness": 0.8, "value": risk_score},
                },
            ))
            fig_gauge.update_layout(**PLOTLY_LAYOUT, height=280)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with c2:
            st.markdown('<div class="sec-title">📐 Score Factors</div>', unsafe_allow_html=True)
            sav_rate_pct = (savings / income * 100) if income > 0 else 0
            factors = [
                ("Debt-to-Income", min(debt_ratio, 100),
                 "#ef4444" if debt_ratio > 50 else "#f59e0b" if debt_ratio > 30 else "#22c55e",
                 f"{debt_ratio:.1f}%"),
                ("Credit Score", (credit_score - 300) / 6,
                 "#22c55e" if credit_score >= 700 else "#f59e0b" if credit_score >= 650 else "#ef4444",
                 str(credit_score)),
                ("Savings Rate", min(sav_rate_pct * 3, 100),
                 "#22c55e" if sav_rate_pct > 15 else "#f59e0b" if sav_rate_pct > 5 else "#ef4444",
                 f"{sav_rate_pct:.1f}%"),
                ("Disposable Buffer",
                 min((disposable / income * 100) * 2, 100) if income > 0 else 0,
                 "#3b82f6", _fmt(disposable)),
            ]
            for name, pct, color, label in factors:
                pct = max(0, min(pct, 100))
                st.markdown(f"""
                <div style="margin-bottom:1rem;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                        <span class="factor-name">{name}</span>
                        <span class="factor-val" style="color:{color};">{label}</span>
                    </div>
                    <div class="factor-bar-bg">
                        <div class="factor-bar-fill" style="width:{pct:.0f}%;background:{color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            dr_color = "#ef4444" if debt_ratio > 50 else "#f59e0b" if debt_ratio > 30 else "#22c55e"
            st.markdown(f"""
            <div class="debt-box">
                <div class="debt-box-lbl">Total Debt Ratio</div>
                <div class="debt-box-val" style="color:{dr_color};">{debt_ratio:.1f}%</div>
                <div class="debt-box-sub">Safe threshold: &lt; 30%</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown('<div class="sec-title">🔍 Why This Risk Score?</div>', unsafe_allow_html=True)
            reasons    = explain_risk(income, expenses, existing_emi, loan_amount,
                                      credit_score, credit_history, savings, debt_ratio)
            level_cls  = {"high": "exp-high", "medium": "exp-medium", "low": "exp-low"}
            level_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            for r in reasons:
                cls  = level_cls.get(r["level"], "exp-low")
                icon = level_icon.get(r["level"], "✅")
                st.markdown(f'<div class="exp-card {cls}">{icon} &nbsp;{r["text"]}</div>',
                            unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # TAB 2 — Stress Timeline
    # ════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="sec-title"> Savings Trajectory Over Time</div>',
                    unsafe_allow_html=True)
        months       = list(range(0, tenure + 1))
        monthly_sav  = disposable - emi
        with_loan    = [monthly_sav * m + savings for m in months]
        without_loan = [disposable * m + savings for m in months]
        emi_cumul    = [emi * m for m in months]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=months, y=with_loan, name="Savings (with loan)",
            line=dict(color="#3b82f6", width=2.5),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
            hovertemplate="Month %{x}<br>₹%{y:,.0f}<extra></extra>"))
        fig2.add_trace(go.Scatter(x=months, y=without_loan, name="Savings (no loan)",
            line=dict(color="#22c55e", width=2, dash="dot"),
            hovertemplate="Month %{x}<br>₹%{y:,.0f}<extra></extra>"))
        fig2.add_trace(go.Scatter(x=months, y=emi_cumul, name="Cumulative EMI paid",
            line=dict(color="#ef4444", width=1.8, dash="dash"),
            hovertemplate="Month %{x}<br>₹%{y:,.0f}<extra></extra>"))
        fig2.update_layout(**PLOTLY_LAYOUT, height=380,
                           xaxis_title="Month", yaxis_title="Amount (₹)",
                           hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True)

        breakeven = next(
            (i for i, (wl, nl) in enumerate(zip(with_loan, without_loan)) if nl - wl > loan_amount),
            None)
        if breakeven:
            st.markdown(f"""
            <div class="stress-note" style="background:rgba(219,234,254,0.8);
                 border:1px solid rgba(59,130,246,0.3);color:#1e40af;">
                The opportunity cost of this loan exceeds the loan principal around
                <strong>Month {breakeven}</strong>. Plan your finances accordingly.
            </div>""", unsafe_allow_html=True)
        elif monthly_sav < 0:
            st.markdown("""
            <div class="stress-note" style="background:rgba(254,226,226,0.8);
                 border:1px solid rgba(239,68,68,0.3);color:#991b1b;">
                Your monthly savings will be <strong>negative</strong> with this loan.
                You may be drawing down existing savings each month to cover the EMI.
            </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # TAB 4 — Plan Suggestions
    # ════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="sec-title"> Plan Suggestions</div>', unsafe_allow_html=True)

        # FIX 4: Honest explanation of what ML actually does vs rule engine
        if ml_active:
            st.markdown(
                f'<div class="alert-box alert-info" style="margin-bottom:1.2rem;">'
                f'🤖 <strong>How the ML Pick is chosen:</strong> The Random Forest model '
                f'(trained on 28,000+ real credit records) estimates your default probability. '
                f'The best tenure is then selected by finding the option that '
                f'<strong>saves the most interest</strong> while keeping your EMI affordable. '
                f'A longer tenure is only suggested if it reduces risk by 5+ points.'
                f'</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="alert-box alert-warning" style="margin-bottom:1.2rem;">'
                '⚙️ <strong>How plans are scored:</strong> Rule-based financial ratios '
                '(debt-to-income, savings rate, disposable buffer, credit score). '
                'Add <code>loan_risk_model.pkl</code> to <code>/model/</code> for ML scoring.'
                '</div>', unsafe_allow_html=True)

        cols = st.columns(2)
        for i, (col, pc) in enumerate(zip(cols, plan_cards)):
            if pc is None:
                continue
            with col:
                is_sel    = (st.session_state.selected_plan_idx == i)
                card_cls  = "plan-card-wrap selected" if is_sel else "plan-card-wrap"
                st.markdown(f"""
                <div class="{card_cls}">
                    <span class="plan-card-badge {pc['badge']}">{pc['badge_text']}</span>
                    <div class="plan-amount">{_fmt(round(pc['amount']))}</div>
                    <div class="plan-meta">{pc['tenure']} months · {interest_rate}% p.a.</div>
                    <div class="plan-row">
                        <span class="pr-l">Monthly EMI</span>
                        <span class="pr-v">{_fmt(round(pc['emi']))}</span></div>
                    <div class="plan-row">
                        <span class="pr-l">Total Interest</span>
                        <span class="pr-v">{_fmt(round(pc['interest']))}</span></div>
                    <div class="plan-row">
                        <span class="pr-l">Risk Score</span>
                        <span class="pr-v" style="color:{pc['color']};">{pc['risk']}/100</span></div>
                    <div class="plan-row">
                        <span class="pr-l">Risk Level</span>
                        <span class="pr-v" style="color:{pc['color']};">{get_risk_level(pc['risk'])[0]}</span></div>
                </div>""", unsafe_allow_html=True)
                btn_label = "✓ Selected" if is_sel else "Select & See Impact →"
                if st.button(btn_label, key=f"plan_btn_{i}", use_container_width=True,
                             type="primary" if is_sel else "secondary"):
                    st.session_state.selected_plan_idx = None if is_sel else i
                    st.rerun()

        sel = st.session_state.selected_plan_idx
        if sel is not None and plan_cards[sel] is not None:
            pc        = plan_cards[sel]
            reduction = pc["reduction"]
            new_risk  = pc["risk"]
            _, nc, nbg, _ = get_risk_level(new_risk)
            int_diff  = total_int - pc["interest"]
            emi_diff  = emi - pc["emi"]

            if reduction > 0:
                hl_color, hl_text, hl_icon = "#15803d", f"Risk drops by {reduction} points — from {risk_score} to {new_risk}", "📉"
            elif reduction == 0:
                hl_color, hl_text, hl_icon = "#b45309", f"Same risk level as your current plan ({risk_score}/100)", "↔"
            else:
                hl_color, hl_text, hl_icon = "#dc2626", f"Risk increases by {abs(reduction)} points — review carefully", "📈"

            st.markdown(f"""
            <div class="rrp">
                <div class="rrp-title">{hl_icon} {pc['label']} — Risk Impact</div>
                <div class="rrp-score-row">
                    <div class="rrp-score-box" style="background:{risk_bg};">
                        <div class="rrp-score-label">Your Plan</div>
                        <div class="rrp-score-num" style="color:{risk_color};">{risk_score}</div>
                        <div style="font-size:0.76rem;color:{risk_color};margin-top:0.2rem;font-weight:700;">{risk_level}</div>
                    </div>
                    <div class="rrp-arrow">→</div>
                    <div class="rrp-score-box" style="background:{nbg};">
                        <div class="rrp-score-label">{pc['label']}</div>
                        <div class="rrp-score-num" style="color:{nc};">{new_risk}</div>
                        <div style="font-size:0.76rem;color:{nc};margin-top:0.2rem;font-weight:700;">{get_risk_level(new_risk)[0]}</div>
                    </div>
                    <div style="flex:1;padding-left:1rem;">
                        <div style="font-size:0.9rem;color:{hl_color};font-weight:700;line-height:1.5;">{hl_text}</div>
                    </div>
                </div>
                <div class="rrp-bar-wrap">
                    <div class="rrp-bar-label">
                        <span>Your Plan</span><span style="color:{risk_color};">{risk_score}/100</span></div>
                    <div class="rrp-bar-bg">
                        <div class="rrp-bar-fill" style="width:{risk_score}%;background:{risk_color};"></div></div>
                </div>
                <div class="rrp-bar-wrap">
                    <div class="rrp-bar-label">
                        <span>{pc['label']}</span><span style="color:{nc};">{new_risk}/100</span></div>
                    <div class="rrp-bar-bg">
                        <div class="rrp-bar-fill" style="width:{new_risk}%;background:{nc};"></div></div>
                </div>
                <div class="rrp-savings-row">
                    <div class="rrp-sav-card">
                        <div class="rrp-sav-label">Risk change</div>
                        <div class="rrp-sav-val" style="color:{'#15803d' if reduction > 0 else '#dc2626'};">
                            {'+' if reduction > 0 else ''}{reduction} pts</div></div>
                    <div class="rrp-sav-card">
                        <div class="rrp-sav-label">Interest {'saved' if int_diff >= 0 else 'extra'}</div>
                        <div class="rrp-sav-val" style="color:{'#15803d' if int_diff > 0 else '#dc2626'};">
                            {_fmt(round(abs(int_diff)))} {'↓' if int_diff > 0 else '↑'}</div></div>
                    <div class="rrp-sav-card">
                        <div class="rrp-sav-label">EMI change</div>
                        <div class="rrp-sav-val" style="color:{'#15803d' if emi_diff > 0 else '#dc2626'};">
                            {_fmt(round(abs(emi_diff)))} {'lower' if emi_diff > 0 else 'higher'}</div></div>
                </div>
            </div>""", unsafe_allow_html=True)

            if int_diff > 0:
                st.markdown(f"""
                <div style="padding:1.2rem 1.5rem;background:rgba(220,252,231,0.8);
                            border:1px solid rgba(34,197,94,0.35);border-radius:14px;margin-top:1rem;">
                    <div style="font-family:'Merriweather',serif;font-size:1rem;font-weight:900;
                                color:#15803d;margin-bottom:0.5rem;">✅ {pc['label']} Saves You Money</div>
                    <div style="font-size:0.88rem;color:#166534;line-height:1.75;">
                        By switching to the <strong>{pc['tenure']}-month tenure</strong>,
                        you save <strong>{_fmt(round(int_diff))}</strong> in total interest
                        while keeping the same loan amount.<br><br>
                        Your EMI {'increases' if emi_diff < 0 else 'decreases'} by
                        <strong>{_fmt(round(abs(emi_diff)))}/month</strong>
                        but you {'finish the loan faster and pay significantly less overall' if emi_diff < 0 else 'have more breathing room each month'}.
                    </div>
                </div>""", unsafe_allow_html=True)
            elif int_diff < 0:
                st.markdown(f"""
                <div style="padding:1.2rem 1.5rem;background:rgba(254,243,199,0.8);
                            border:1px solid rgba(245,158,11,0.35);border-radius:14px;margin-top:1rem;">
                    <div style="font-family:'Merriweather',serif;font-size:1rem;font-weight:900;
                                color:#92400e;margin-bottom:0.5rem;">⚖️ Tradeoff Note</div>
                    <div style="font-size:0.88rem;color:#78350f;line-height:1.75;">
                        The {pc['label']} has a <strong>lower risk score</strong> but costs
                        <strong>{_fmt(round(abs(int_diff)))} more</strong> in total interest.<br><br>
                        <strong>Choose {pc['label']}</strong> if reducing default risk is your priority.<br>
                        <strong>Keep Your Plan</strong> if minimising total interest paid matters more.
                    </div>
                </div>""", unsafe_allow_html=True)

            # Bar charts from Code 2 (kept as-is)
            
        else:
            st.markdown(
                '<div class="alert-box alert-info" style="margin-top:1rem;">'
                '👆 Click a plan card above to see its risk impact.</div>',
                unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # TAB 5 — Plan Comparison
    # ════════════════════════════════════════════════════════════════
    with tab5:
        cmp_pc       = active_pc
        cmp_interest = cmp_pc["interest"]
        saving_diff  = total_int - cmp_interest

        st.markdown(
            f'<div class="active-plan-banner">📌 Comparing <strong>Your Plan</strong> vs '
            f'<strong>{active_label}</strong> — change selection in <em>Plan Suggestions</em>.</div>',
            unsafe_allow_html=True)
        st.markdown(f'<div class="sec-title">Your Plan vs {active_label}</div>',
                    unsafe_allow_html=True)

        m1, m2, m3, m4, m5 = st.columns(5)
        metrics = [
            (m1, "Loan Amount",    _fmt(loan_amount),  _fmt(round(cmp_pc["amount"])),  loan_amount - cmp_pc["amount"]),
            (m2, "Monthly EMI",    _fmt(emi),           _fmt(round(cmp_pc["emi"])),     emi - cmp_pc["emi"]),
            (m3, "Tenure",         f"{tenure}m",        f"{cmp_pc['tenure']}m",         tenure - cmp_pc["tenure"]),
            (m4, "Risk Score",     f"{risk_score}/100", f"{cmp_pc['risk']}/100",        risk_score - cmp_pc["risk"]),
            (m5, "Total Interest", _fmt(total_int),     _fmt(round(cmp_interest)),      total_int - cmp_interest),
        ]
        for col, label, your_v, cmp_v, diff in metrics:
            diff_color, diff_arrow = ("#22c55e", "↓") if diff > 0 else ("#ef4444", "↑") if diff < 0 else ("#64748b", "=")
            with col:
                st.markdown(f"""
                <div class="cmp-card">
                    <div class="cmp-lbl">{label}</div>
                    <div class="cmp-row-lbl">Your Plan</div>
                    <div class="cmp-row-val">{your_v}</div>
                    <div class="cmp-row-lbl">{active_label}</div>
                    <div style="font-family:'Merriweather',serif;font-size:0.92rem;
                                font-weight:800;color:{diff_color};">{cmp_v} {diff_arrow}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        df_cmp = pd.DataFrame({
            "Metric":     ["Loan Amount", "Monthly EMI", "Tenure", "Risk Score", "Total Interest"],
            "Your Plan":  [_fmt(loan_amount), _fmt(emi), f"{tenure} months",
                           f"{risk_score}/100", _fmt(total_int)],
            active_label: [_fmt(round(cmp_pc["amount"])), _fmt(round(cmp_pc["emi"])),
                           f"{cmp_pc['tenure']} months", f"{cmp_pc['risk']}/100",
                           _fmt(round(cmp_interest))],
        })
        st.dataframe(df_cmp, use_container_width=True, hide_index=True)
        st.markdown("<br>", unsafe_allow_html=True)

        _, cmp_nc, _, _ = get_risk_level(cmp_pc["risk"])
       
        if saving_diff > 0:
            st.markdown(f"""
            <div style="padding:1.2rem 1.5rem;background:rgba(220,252,231,0.8);
                        border:1px solid rgba(34,197,94,0.35);border-radius:14px;
                        display:flex;align-items:center;gap:1.1rem;margin-top:1rem;">
                <div style="font-size:2rem;">💰</div>
                <div>
                    <div style="font-family:'Merriweather',serif;font-size:1.2rem;
                                font-weight:900;color:#15803d;">Save {_fmt(saving_diff)}</div>
                    <div style="font-size:0.84rem;color:#166534;margin-top:0.15rem;">
                        in total interest by switching to the {active_label} plan.
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
        elif saving_diff < 0:
            st.markdown(f"""
            <div style="padding:1.2rem 1.5rem;background:rgba(254,243,199,0.8);
                        border:1px solid rgba(245,158,11,0.35);border-radius:14px;margin-top:1rem;">
                <div style="font-family:'Merriweather',serif;font-size:1rem;font-weight:900;
                            color:#92400e;margin-bottom:0.5rem;">⚖️ Risk vs Cost Tradeoff</div>
                <div style="font-size:0.88rem;color:#78350f;line-height:1.75;">
                    The <strong>{active_label}</strong> plan costs
                    <strong>{_fmt(abs(round(saving_diff)))} more</strong> in total interest,
                    but your monthly EMI changes by
                    <strong>{_fmt(round(abs(emi - cmp_pc['emi'])))}/month</strong>
                    and your risk profile improves.<br><br>
                    <strong>Choose {active_label}</strong> if reducing risk is your priority.<br>
                    <strong>Stick to Your Plan</strong> if you want minimum total interest paid.
                </div>
            </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # TAB 6 — Repayment Tracker
    # ════════════════════════════════════════════════════════════════
    with tab6:
        st.markdown('<div class="sec-title"> Dynamic Loan Repayment Tracker</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="alert-box alert-info" style="margin-bottom:1.2rem;"> '
            '<strong>How it works:</strong> Log what you actually paid each month. '
            'Pay <strong>more</strong> → interest saved + tenure reduced. '
            'Pay <strong>less</strong> → future EMIs increase. Schedule recalculates live.</div>',
            unsafe_allow_html=True)

        # Plan selector
        plan_options_map = {"Your Original Plan": (loan_amount, tenure, emi)}
        if plan_cards[0] is not None:
            pc0      = plan_cards[0]
            key_name = f"{'ML' if ml_active else 'Best'} Pick — {pc0['tenure']}m"
            plan_options_map[key_name] = (pc0["amount"], pc0["tenure"], pc0["emi"])

        default_option    = "Your Original Plan"
        if sel_idx == 0 and plan_cards[0] is not None:
            default_option = f"{'ML' if ml_active else 'Best'} Pick — {plan_cards[0]['tenure']}m"

        plan_options_list = list(plan_options_map.keys())
        default_idx       = (plan_options_list.index(default_option)
                             if default_option in plan_options_list else 0)

        st.markdown(
            f'<div class="active-plan-banner">📌 Tracking <strong>{default_option}</strong> '
            f'by default (matches your Plan Suggestions selection). Switch below.</div>',
            unsafe_allow_html=True)

        selected_plan_name = st.radio(
            "Track which plan?", plan_options_list,
            index=default_idx, horizontal=True, key="tracker_plan_selector")
        track_amount, track_tenure, track_emi = plan_options_map[selected_plan_name]

        sched_key = f"amort_schedule_{selected_plan_name}"
        reset_key = f"amort_reset_{selected_plan_name}_{track_amount}_{track_tenure}_{interest_rate}"

        if (sched_key not in st.session_state
                or st.session_state.get(f"{sched_key}_reset_key") != reset_key):
            st.session_state[sched_key] = build_amortization_schedule(
                track_amount, interest_rate, track_tenure)
            st.session_state[f"{sched_key}_reset_key"]     = reset_key
            st.session_state[f"{sched_key}_current_month"] = 1

        schedule = st.session_state[sched_key]

        total_paid_so_far  = sum((r["paid_amount"] or 0) for r in schedule if r["status"] != "future")
        months_completed   = sum(1 for r in schedule if r["status"] != "future")
        months_remaining   = len(schedule) - months_completed
        outstanding        = (schedule[months_completed - 1]["closing_balance"]
                              if months_completed > 0 else track_amount)

        # FIX 5: interest_saved_so_far — only compare logged months vs their original projection
        # Old: compared original_total_int vs ALL rows (including future), always near zero
        # New: sum actual interest paid on logged months vs what was originally scheduled for those months
        actual_interest_paid    = sum(r["interest_component"]
                                      for r in schedule if r["status"] != "future")
        original_interest_those = sum(r.get("original_interest", r["interest_component"])
                                      for r in schedule if r["status"] != "future")
        interest_saved_so_far   = original_interest_those - actual_interest_paid

        consecutive_short = 0
        for r in reversed(schedule):
            if r["status"] in ("short", "missed"):
                consecutive_short += 1
            elif r["status"] != "future":
                break

        st.markdown(f"""
        <div class="tracker-summary">
            <div class="tracker-card">
                <div class="tc-label">Months Done</div>
                <div class="tc-val tc-blue">{months_completed}/{len(schedule)}</div></div>
            <div class="tracker-card">
                <div class="tc-label">Months Left</div>
                <div class="tc-val">{months_remaining}</div></div>
            <div class="tracker-card">
                <div class="tc-label">Total Paid</div>
                <div class="tc-val tc-blue">{_fmt(round(total_paid_so_far))}</div></div>
            <div class="tracker-card">
                <div class="tc-label">Interest Saved</div>
                <div class="tc-val {'tc-green' if interest_saved_so_far >= 0 else 'tc-red'}">
                    {_fmt(round(abs(interest_saved_so_far)))} {'↓' if interest_saved_so_far >= 0 else '↑'}</div></div>
            <div class="tracker-card">
                <div class="tc-label">Outstanding</div>
                <div class="tc-val {'tc-green' if outstanding == 0 else 'tc-amber'}">
                    {_fmt(round(outstanding))}</div></div>
        </div>""", unsafe_allow_html=True)

        if consecutive_short >= 2:
            st.markdown(
                f'<div class="alert-box alert-danger">⚠️ Partial payments for '
                f'<strong>{consecutive_short} consecutive months</strong>. '
                f'Future EMIs have increased. Consider a lump-sum payment.</div>',
                unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Log a Payment")
        next_unpaid = next((r["month"] for r in schedule if r["status"] == "future"), None)

        if next_unpaid is not None:
            col_month, col_amt, col_type, col_btn = st.columns([1, 2, 2, 1])
            with col_month:
                st.markdown(
                    f'<div style="padding:0.6rem 0.8rem;background:rgba(255,255,255,0.85);'
                    f'border:1px solid rgba(144,202,249,0.4);border-radius:10px;text-align:center;">'
                    f'<div style="font-size:0.72rem;color:#64748b;text-transform:uppercase;'
                    f'letter-spacing:0.07em;font-weight:700;">Month</div>'
                    f'<div style="font-family:Merriweather,serif;font-size:1.4rem;'
                    f'font-weight:900;color:#1a2540;">{next_unpaid}</div></div>',
                    unsafe_allow_html=True)
            with col_amt:
                row       = schedule[next_unpaid - 1]
                scheduled = row["scheduled_emi"]
                payment_input = st.number_input(
                    f"Amount paid (Scheduled: {_fmt(round(scheduled))})",
                    min_value=0.0, max_value=float(track_amount * 2),
                    value=float(round(scheduled)), step=100.0,
                    key=f"pay_input_m{next_unpaid}_{selected_plan_name}")
            with col_type:
                if payment_input == 0:
                    pp, pc2 = "🔴 Missed payment — penalty will apply", "#dc2626"
                elif payment_input < scheduled * 0.95:
                    pp, pc2 = (f"🟡 Short by {_fmt(round(scheduled - payment_input))} "
                               f"— future EMIs will increase"), "#b45309"
                elif payment_input > scheduled * 1.02:
                    pp, pc2 = (f"🟢 Extra {_fmt(round(payment_input - scheduled))} "
                               f"— interest saved + tenure reduced"), "#15803d"
                else:
                    pp, pc2 = "✅ Full payment — on track", "#15803d"
                st.markdown(
                    f'<div style="padding:0.55rem 0.8rem;border-radius:10px;font-size:0.85rem;'
                    f'color:{pc2};font-weight:700;background:rgba(255,255,255,0.85);'
                    f'border:1px solid rgba(144,202,249,0.4);margin-top:1.7rem;line-height:1.55;">'
                    f'{pp}</div>', unsafe_allow_html=True)
            with col_btn:
                st.markdown("<div style='margin-top:1.7rem;'>", unsafe_allow_html=True)
                if st.button("Log ✓", key=f"log_btn_m{next_unpaid}_{selected_plan_name}",
                             type="primary", use_container_width=True):
                    if payment_input == 0:
                        # FIX 6: Don't manually mutate future balances before recalculate
                        # Old code added penalty+scheduled to all future balances first,
                        # then recalculate_from_month added it again → double counting
                        penalty = scheduled * 0.02
                        schedule[next_unpaid - 1].update({
                            "paid_amount": 0,
                            "status": "missed",
                            # Add penalty to closing balance of this month only
                            "closing_balance": round(
                                schedule[next_unpaid - 1]["closing_balance"] + penalty, 2)
                        })
                        schedule = recalculate_from_month(schedule, next_unpaid, interest_rate)
                    elif payment_input < scheduled * 0.95:
                        schedule[next_unpaid - 1].update({"paid_amount": payment_input, "status": "short"})
                        schedule = recalculate_from_month(schedule, next_unpaid, interest_rate)
                    elif payment_input > scheduled * 1.02:
                        schedule[next_unpaid - 1].update({"paid_amount": payment_input, "status": "extra"})
                        schedule = recalculate_from_month(schedule, next_unpaid, interest_rate)
                        schedule = [r for r in schedule
                                    if r["closing_balance"] > 1 or r["status"] != "future"]
                    else:
                        schedule[next_unpaid - 1].update({"paid_amount": payment_input, "status": "paid"})
                    st.session_state[sched_key] = schedule
                    st.session_state[f"{sched_key}_current_month"] = next_unpaid + 1
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="alert-box alert-success">🎉 <strong>Congratulations!</strong> '
                'All months logged. Loan fully tracked!</div>', unsafe_allow_html=True)

        _, col_r2, _ = st.columns([4, 1, 4])
        with col_r2:
            if st.button("Reset Tracker", key=f"tracker_reset_{selected_plan_name}",
                         use_container_width=True):
                if sched_key in st.session_state:
                    del st.session_state[sched_key]
                st.rerun()

        st.markdown("---")
        st.markdown("#### Full Month-by-Month Schedule")
        st.markdown(
            '<div class="legend-row">'
            '<div class="legend-item"><div class="legend-dot" style="background:#22c55e;"></div>Extra</div>'
            '<div class="legend-item"><div class="legend-dot" style="background:#3b82f6;"></div>Paid</div>'
            '<div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div>Short</div>'
            '<div class="legend-item"><div class="legend-dot" style="background:#ef4444;"></div>Missed</div>'
            '<div class="legend-item"><div class="legend-dot" style="background:rgba(100,116,139,0.4);"></div>Upcoming</div>'
            '</div>', unsafe_allow_html=True)

        STATUS_ICON = {"paid": "✅ Paid", "extra": "🟢 Extra",
                       "short": "🟡 Short", "missed": "🔴 Missed", "future": "⏳ Upcoming"}
        table_rows = []
        for r in schedule:
            paid_amt     = r.get("paid_amount")
            sched_e      = r["scheduled_emi"]
            diff         = 0.0 if paid_amt is None else (paid_amt - sched_e)
            status_label = ("📌 Next Due"
                            if (r["status"] == "future" and r["month"] == next_unpaid)
                            else STATUS_ICON.get(r["status"], "—"))
            # FIX 7: Meaningful per-row interest saving vs original projection
            # Old: bogus formula (diff * rate / 1200 * tenure * 0.5)
            # New: actual interest component vs what was originally scheduled for that month
            impact = ""
            if r["status"] == "extra" and diff > 0:
                orig_int   = r.get("original_interest", 0)
                actual_int = r["interest_component"]
                saved      = orig_int - actual_int
                impact = f"🟢 ~{_fmt(round(saved))} interest saved" if saved > 0 else "🟢 Principal reduced"
            elif r["status"] in ("short", "missed"):
                impact = "🔴 EMI ↑ future months"
            table_rows.append({
                "Month":         r["month"],
                "Status":        status_label,
                "Scheduled EMI": _fmt(round(sched_e)),
                "Paid":          _fmt(round(paid_amt)) if paid_amt is not None else "—",
                "Difference":    ((_fmt(round(diff)) if diff >= 0 else f"-{_fmt(round(abs(diff)))}")
                                  if paid_amt is not None else "—"),
                "Principal":     _fmt(round(r["principal_component"])),
                "Interest":      _fmt(round(r["interest_component"])),
                "Balance":       _fmt(round(r["closing_balance"])),
                "Impact":        impact,
            })

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True,
                     hide_index=True, height=420)

        if interest_saved_so_far > 0:
            st.markdown(
                f'<div class="alert-box alert-success" style="margin-top:1rem;">🎉 '
                f'Your prepayments saved <strong>{_fmt(round(interest_saved_so_far))}</strong> '
                f'in interest so far.</div>', unsafe_allow_html=True)
        elif interest_saved_so_far < -500:
            st.markdown(
                f'<div class="alert-box alert-danger" style="margin-top:1rem;">⚠️ '
                f'Partial/missed payments added <strong>{_fmt(round(abs(interest_saved_so_far)))}</strong> '
                f'in extra interest.</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 2, 3])
    with c2:
        if st.button("← Recalculate", use_container_width=True):
            st.session_state.page = "calculator"
            st.session_state.step = 1; st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
