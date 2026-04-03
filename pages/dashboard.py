import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import os

from utils.calculator import calculate_emi, calculate_safe_emi, calculate_max_loan
from utils.risk_engine import compute_risk_score, get_risk_level
from utils.explainer import explain_risk


def show():
    data = st.session_state.get("form_data", {})

    if not data.get("income") or not data.get("loan_amount"):
        st.warning("⚠️ Please fill out the calculator first.")
        if st.button("Go to Calculator"):
            st.session_state.page = "calculator"
            st.rerun()
        return

    # ─── Extract inputs ───
    income = data["income"]
    expenses = data["expenses"]
    existing_emi = data["existing_emi"]
    savings = data.get("savings", 0)
    credit_score = data.get("credit_score", 700)
    credit_history = data.get("credit_history", 5)
    loan_amount = data["loan_amount"]
    tenure = data["tenure"]
    interest_rate = data["interest_rate"]

    # ─── Core Calculations ───
    emi = calculate_emi(loan_amount, interest_rate, tenure)
    safe_emi = calculate_safe_emi(income, expenses, existing_emi)
    max_loan = calculate_max_loan(safe_emi, interest_rate, tenure)

    disposable = income - expenses - existing_emi
    debt_ratio = (existing_emi + emi) / income * 100 if income > 0 else 100
    savings_rate = savings / income * 100 if income > 0 else 0
    emi_to_income = emi / income * 100 if income > 0 else 0
    loan_percent_income = loan_amount / (income * 12) if income > 0 else 0

    # ─── ML Risk Prediction (Cleaned) ───
    ml_risk_prob = None
    model_path = os.path.join(os.path.dirname(__file__), "..", "model", "loan_risk_model.pkl")
    scaler_path = os.path.join(os.path.dirname(__file__), "..", "model", "scaler.pkl")

    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)

            features = pd.DataFrame([{
                "person_income": income * 12,
                "loan_amnt": loan_amount,
                "loan_int_rate": interest_rate,
                "loan_percent_income": loan_percent_income,
                "cb_person_cred_hist_length": credit_history
            }])

            if os.path.exists(scaler_path):
                scaler = joblib.load(scaler_path)
                features = scaler.transform(features)

            ml_risk_prob = model.predict_proba(features)[0][1]

        except Exception:
            ml_risk_prob = None

    # ─── Rule-based risk ───
    risk_score = compute_risk_score(
        income, expenses, existing_emi,
        loan_amount, tenure, interest_rate,
        credit_score, credit_history, savings
    )

    # Blend ML + Rule
    if ml_risk_prob is not None:
        risk_score = int((ml_risk_prob * 100) * 0.6 + risk_score * 0.4)

    risk_level, risk_color, risk_bg = get_risk_level(risk_score)

    # ─── Header ───
    st.markdown("## Your Affordability Report")
    st.caption("AI-powered financial risk analysis")

    # ─────────────────────────────────────────
    # ─── Feature 1: AI Loan Negotiation Advisor ───
    # ─────────────────────────────────────────
    if risk_level in ["High Risk", "Medium Risk"]:
        st.markdown("### 🧠 AI Loan Negotiation Advisor")
        st.caption("Simulating safer plans for you...")

        best_plan = None
        best_score = 999

        for pct in np.arange(0.3, 1.05, 0.05):
            for alt_tenure in [24, 36, 48, 60, 72, 84, 96, 120]:

                alt_amount = round(loan_amount * pct / 10000) * 10000
                alt_emi = calculate_emi(alt_amount, interest_rate, alt_tenure)

                alt_score = compute_risk_score(
                    income, expenses, existing_emi,
                    alt_amount, alt_tenure, interest_rate,
                    credit_score, credit_history, savings
                )

                alt_level, _, _ = get_risk_level(alt_score)

                if alt_score < best_score:
                    best_score = alt_score
                    best_plan = {
                        "amount": alt_amount,
                        "tenure": alt_tenure,
                        "emi": alt_emi,
                        "score": alt_score
                    }

        if best_plan:
            st.success(
                f"✅ Best Plan: ₹{best_plan['amount']:,.0f} · "
                f"{best_plan['tenure']} months · "
                f"EMI ₹{best_plan['emi']:,.0f}/mo "
                f"(Risk drops to {best_plan['score']}/100)"
            )

            if st.button("Apply this plan →"):
                st.session_state.form_data["loan_amount"] = best_plan["amount"]
                st.session_state.form_data["tenure"] = best_plan["tenure"]
                st.rerun()

    # ─────────────────────────────────────────
    # ─── Feature 2: Enhanced Loan Stress Timeline ───
    # ─────────────────────────────────────────
    st.markdown("### 📉 Loan Stress Timeline")

    months = list(range(0, tenure + 13))
    monthly_savings_with_loan = disposable - emi
    monthly_savings_without = disposable

    cum_with = []
    cum_without = []

    for m in months:
        if m <= tenure:
            cum_with.append(monthly_savings_with_loan * m)
        else:
            end_savings = monthly_savings_with_loan * tenure
            extra = disposable * (m - tenure)
            cum_with.append(end_savings + extra)

        cum_without.append(monthly_savings_without * m)

    danger_month = None
    for i in range(len(cum_with)):
        if cum_with[i] < 0:
            danger_month = i
            break

    fig = go.Figure()

    if danger_month:
        fig.add_vrect(
            x0=danger_month,
            x1=tenure,
            fillcolor="rgba(239,68,68,0.05)",
            line_width=0,
        )

    fig.add_trace(go.Scatter(
        x=months,
        y=cum_with,
        mode="lines",
        name="With Loan"
    ))

    fig.add_trace(go.Scatter(
        x=months,
        y=cum_without,
        mode="lines",
        name="Without Loan"
    ))

    fig.add_vline(x=tenure)

    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    # ─────────────────────────────────────────
    # ─── Feature 3: Advanced XAI Breakdown ───
    # ─────────────────────────────────────────
    st.markdown("### 🔍 Risk Breakdown (Explainable AI)")
    st.caption("Each factor's contribution to your risk")

    sub_scores = {
        "Debt-to-income ratio": min(35, 35 if debt_ratio > 60 else 20 if debt_ratio > 40 else 10 if debt_ratio > 30 else 0),
        "Credit score": min(25, 25 if credit_score < 580 else 18 if credit_score < 650 else 10 if credit_score < 700 else 5 if credit_score < 750 else 0),
        "Savings buffer": min(15, 15 if savings_rate < 5 else 8 if savings_rate < 10 else 3 if savings_rate < 20 else 0),
        "Loan-to-income": min(15, 15 if loan_percent_income > 0.8 else 8 if loan_percent_income > 0.5 else 3 if loan_percent_income > 0.3 else 0),
        "Credit history": min(10, 10 if credit_history < 2 else 5 if credit_history < 5 else 0),
    }

    for factor, pts in sub_scores.items():
        pct = pts / 35 if pts else 0
        st.progress(pct, text=f"{factor} — {pts} pts")

    st.markdown("**Plain language summary:**")

    reasons = explain_risk(
        income, expenses, existing_emi,
        loan_amount, credit_score,
        credit_history, savings, debt_ratio
    )

    for reason in reasons:
        st.write(f"• {reason['text']}")

    # ─── Save session ───
    try:
        from utils.database import save_session
        save_session(data, risk_score, risk_level, emi, safe_emi, max_loan)
    except:
        pass