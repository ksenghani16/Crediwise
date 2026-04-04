import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.calculator import (
    calculate_emi,
    calculate_safe_emi,
    calculate_max_loan,
    calculate_total_interest,
)
from utils.risk_engine import compute_risk_score, get_risk_level
from utils.explainer import explain_risk


# ─────────────────────────────────────────────────
# Plotly base layout — transparent, styled for dark UI
# ─────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#94a3b8", size=12),
    margin=dict(l=0, r=0, t=36, b=0),
    legend=dict(
        bgcolor="rgba(17,24,39,0.85)",
        bordercolor="#1f2f47",
        borderwidth=1,
        font=dict(size=11, color="#94a3b8"),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        showline=False, zeroline=False,
        tickfont=dict(color="#4b6080"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        showline=False, zeroline=False,
        tickfont=dict(color="#4b6080"),
    ),
)


def _fmt(n: float) -> str:
    return f"₹{n:,.0f}"


def show():
    data = st.session_state.get("form_data", {})

    # ── Guard: redirect if no data ──
    if not data.get("income") or not data.get("loan_amount"):
        st.markdown("""
        <div style="text-align:center; padding:5rem 2rem;">
            <div style="font-size:3.5rem; margin-bottom:1rem;">📋</div>
            <h3 style="font-family:'Syne',sans-serif; color:#f0f4ff; margin:0 0 0.6rem;">No Analysis Yet</h3>
            <p style="color:#94a3b8; font-size:0.95rem;">
                Please complete the calculator first to view your personalised loan analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("Go to Calculator →", use_container_width=True, type="primary"):
                st.session_state.page = "calculator"
                st.rerun()
        return

    # ── Unpack inputs ──
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

    # ── Core calculations ──
    emi        = calculate_emi(loan_amount, interest_rate, tenure)
    safe_emi   = calculate_safe_emi(income, expenses, existing_emi)
    max_loan   = calculate_max_loan(safe_emi, interest_rate, tenure)
    total_int  = calculate_total_interest(loan_amount, emi, tenure)
    disposable = income - expenses - existing_emi
    debt_ratio = ((existing_emi + emi) / income * 100) if income > 0 else 100
    emi_ratio  = (emi / income * 100) if income > 0 else 0

    risk_score = compute_risk_score(
        income, expenses, existing_emi, loan_amount,
        tenure, interest_rate, credit_score, credit_history, savings,
    )
    risk_level, risk_color, risk_bg, risk_icon = get_risk_level(risk_score)

    # ──────────────────────────────────────────────
    # DASHBOARD CSS
    # ──────────────────────────────────────────────
    st.markdown("""
    <style>
    .db-header { margin-bottom: 1.8rem; }
    .db-header h2 {
        font-family: 'Syne', sans-serif;
        font-size: 1.85rem; font-weight: 800;
        color: #f0f4ff; margin: 0 0 0.2rem;
        letter-spacing: -0.03em;
    }
    .db-header .sub { font-size: 0.88rem; color: #94a3b8; }

    /* ── Risk banner ── */
    .risk-banner {
        border-radius: 20px;
        padding: 1.8rem 2rem;
        display: flex; align-items: center; gap: 2rem;
        margin-bottom: 1.8rem;
        border: 1px solid;
        position: relative; overflow: hidden;
    }
    .risk-score-big {
        font-family: 'Syne', sans-serif;
        font-size: 3.8rem; font-weight: 800;
        line-height: 1; flex-shrink: 0;
    }
    .risk-divider {
        width: 1px; height: 64px;
        background: rgba(255,255,255,0.12);
        flex-shrink: 0;
    }
    .risk-label {
        font-family: 'Syne', sans-serif;
        font-size: 1.25rem; font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .risk-desc { font-size: 0.9rem; color: #94a3b8; line-height: 1.6; max-width: 460px; }
    .risk-badge {
        margin-left: auto;
        padding: 0.4rem 1.2rem;
        border-radius: 100px;
        font-size: 0.8rem; font-weight: 700;
        font-family: 'Syne', sans-serif;
        border: 1px solid;
        flex-shrink: 0;
        white-space: nowrap;
    }

    /* ── KPI strip ── */
    .kpi-strip { display: grid; grid-template-columns: repeat(4,1fr); gap: 1.1rem; margin-bottom: 1.8rem; }
    .kpi-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 18px;
        padding: 1.3rem 1.4rem;
        position: relative; overflow: hidden;
    }
    .kpi-lbl {
        font-size: 0.74rem; color: #4b6080;
        text-transform: uppercase; letter-spacing: 0.09em;
        margin-bottom: 0.55rem; font-weight: 600;
    }
    .kpi-val {
        font-family: 'Syne', sans-serif;
        font-size: 1.55rem; font-weight: 800;
        color: #f0f4ff; line-height: 1.1;
    }
    .kpi-sub { font-size: 0.78rem; color: #94a3b8; margin-top: 0.25rem; }
    .kpi-icon { position: absolute; top: 1rem; right: 1rem; font-size: 1.35rem; opacity: 0.45; }

    /* ── Section title ── */
    .sec-title {
        font-family: 'Syne', sans-serif;
        font-size: 1rem; font-weight: 700;
        color: #f0f4ff; margin: 0 0 1.1rem;
        display: flex; align-items: center; gap: 0.5rem;
    }

    /* ── Explainer cards ── */
    .exp-card {
        border-radius: 13px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.85rem;
        border-left: 4px solid;
        font-size: 0.88rem;
        line-height: 1.65;
        font-weight: 400;
    }
    .exp-high   { background: rgba(248,113,113,0.08); border-color:#f87171; color:#fca5a5; }
    .exp-medium { background: rgba(251,191,36,0.08);  border-color:#fbbf24; color:#fde68a; }
    .exp-low    { background: rgba(16,217,160,0.08);  border-color:#10d9a0; color:#6ee7c7; }

    /* ── Best plan card ── */
    .best-plan-card {
        background: linear-gradient(135deg, rgba(91,124,250,0.11), rgba(6,214,199,0.05));
        border: 1px solid rgba(91,124,250,0.28);
        border-radius: 20px;
        padding: 1.8rem;
    }
    .best-plan-card h4 {
        font-family: 'Syne', sans-serif;
        font-size: 1rem; font-weight: 700;
        color: #8fa8ff; margin: 0 0 1.2rem;
    }
    .plan-metric {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.58rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        font-size: 0.88rem;
    }
    .plan-metric:last-of-type { border-bottom: none; }
    .plan-metric .pm-l { color: #94a3b8; }
    .plan-metric .pm-v {
        color: #f0f4ff; font-weight: 700;
        font-family: 'Syne', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ──
    st.markdown(f"""
    <div class="db-header">
        <h2>Your Loan Analysis</h2>
        <div class="sub">
            {loan_type} · {employment} · ₹{loan_amount:,.0f} over {tenure} months @ {interest_rate}% p.a.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Risk Banner ──
    risk_desc_map = {
        "Low Risk":      "Your financial profile looks healthy. You are in a strong position to service this loan comfortably.",
        "Moderate Risk": "Some concerns exist in your profile. Consider adjusting loan terms for a safer outcome.",
        "High Risk":     "Significant stress indicators detected. This loan may be difficult to service without financial strain.",
    }
    st.markdown(f"""
    <div class="risk-banner" style="background:{risk_bg}; border-color:{risk_color}55;">
        <div class="risk-score-big" style="color:{risk_color};">{risk_score}</div>
        <div class="risk-divider"></div>
        <div>
            <div class="risk-label" style="color:{risk_color};">{risk_icon} {risk_level}</div>
            <div class="risk-desc">{risk_desc_map.get(risk_level, '')}</div>
        </div>
        <div class="risk-badge" style="color:{risk_color}; border-color:{risk_color}55; background:{risk_bg};">
            Risk Score / 100
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Strip ──
    st.markdown(f"""
    <div class="kpi-strip">
        <div class="kpi-card" style="border-top:3px solid #5b7cfa;">
            <div class="kpi-icon">💳</div>
            <div class="kpi-lbl">Monthly EMI</div>
            <div class="kpi-val">{_fmt(emi)}</div>
            <div class="kpi-sub">{emi_ratio:.1f}% of income</div>
        </div>
        <div class="kpi-card" style="border-top:3px solid #10d9a0;">
            <div class="kpi-icon">✅</div>
            <div class="kpi-lbl">Safe EMI Capacity</div>
            <div class="kpi-val">{_fmt(safe_emi)}</div>
            <div class="kpi-sub">40% of disposable</div>
        </div>
        <div class="kpi-card" style="border-top:3px solid #fbbf24;">
            <div class="kpi-icon">🏦</div>
            <div class="kpi-lbl">Max Affordable Loan</div>
            <div class="kpi-val">{_fmt(max_loan)}</div>
            <div class="kpi-sub">At {interest_rate}% for {tenure}m</div>
        </div>
        <div class="kpi-card" style="border-top:3px solid #f87171;">
            <div class="kpi-icon">💰</div>
            <div class="kpi-lbl">Total Interest</div>
            <div class="kpi-val">{_fmt(total_int)}</div>
            <div class="kpi-sub">Over {tenure} months</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab4, tab5 = st.tabs([
        "🧠  Risk Deep-Dive",
        "📉  Stress Timeline",
        "💡  AI Suggestions",
        "📊  Plan Comparison",
    ])

    # ───────────── TAB 1: Risk Deep-Dive ─────────────
    with tab1:
        c1, c2, c3 = st.columns([1, 1, 1.1], gap="large")

        # ── Risk Gauge (c1) ──
        with c1:
            st.markdown('<div class="sec-title">📊 Risk Gauge</div>', unsafe_allow_html=True)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                number={
                    "font": {"family": "Syne", "size": 44, "color": risk_color},
                    "suffix": "/100",
                },
                gauge={
                    "axis": {
                        "range": [0, 100], "tickwidth": 0,
                        "tickfont": {"color": "#4b6080", "size": 10},
                    },
                    "bar":       {"color": risk_color, "thickness": 0.28},
                    "bgcolor":   "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 35],   "color": "rgba(16,217,160,0.14)"},
                        {"range": [35, 60],  "color": "rgba(251,191,36,0.14)"},
                        {"range": [60, 100], "color": "rgba(248,113,113,0.14)"},
                    ],
                    "threshold": {
                        "line": {"color": risk_color, "width": 3},
                        "thickness": 0.8,
                        "value": risk_score,
                    },
                },
            ))
            fig_gauge.update_layout(**PLOTLY_LAYOUT, height=290)
            st.plotly_chart(fig_gauge, use_container_width=True)

        # ── Score factors (c2) ──
        with c2:
            st.markdown('<div class="sec-title">📐 Score Factors</div>', unsafe_allow_html=True)

            sav_rate_pct = (savings / income * 100) if income > 0 else 0

            factors = [
                (
                    "Debt-to-Income",
                    min(debt_ratio, 100),
                    "#f87171" if debt_ratio > 50 else "#fbbf24" if debt_ratio > 30 else "#10d9a0",
                    f"{debt_ratio:.1f}%",
                ),
                (
                    "Credit Score",
                    (credit_score - 300) / 6,
                    "#10d9a0" if credit_score >= 700 else "#fbbf24" if credit_score >= 650 else "#f87171",
                    str(credit_score),
                ),
                (
                    "Savings Rate",
                    min(sav_rate_pct * 3, 100),
                    "#10d9a0" if sav_rate_pct > 15 else "#fbbf24" if sav_rate_pct > 5 else "#f87171",
                    f"{sav_rate_pct:.1f}%",
                ),
                (
                    "Disposable Buffer",
                    min((disposable / income * 100) * 2, 100) if income > 0 else 0,
                    "#5b7cfa",
                    _fmt(disposable),
                ),
            ]

            for name, pct, color, label in factors:
                pct = max(0, min(pct, 100))
                st.markdown(f"""
                <div style="margin-bottom:1.1rem;">
                    <div style="display:flex;justify-content:space-between;
                                font-size:0.83rem;color:#94a3b8;margin-bottom:0.38rem;font-weight:500;">
                        <span>{name}</span>
                        <span style="color:{color};font-weight:700;">{label}</span>
                    </div>
                    <div style="height:9px;background:rgba(255,255,255,0.07);
                                border-radius:5px;overflow:hidden;">
                        <div style="width:{pct:.0f}%;height:100%;
                                    background:{color};border-radius:5px;
                                    transition:width 0.4s;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            dr_color = "#f87171" if debt_ratio > 50 else "#fbbf24" if debt_ratio > 30 else "#10d9a0"
            st.markdown(f"""
            <div style="margin-top:1.2rem;padding:1.1rem 1.2rem;
                        background:var(--card-bg);border:1px solid var(--card-border);
                        border-radius:14px;">
                <div style="font-size:0.76rem;color:#4b6080;margin-bottom:0.3rem;
                            text-transform:uppercase;letter-spacing:0.07em;font-weight:600;">
                    Total Debt Ratio
                </div>
                <div style="font-family:'Syne',sans-serif;font-size:1.55rem;
                            font-weight:800;color:{dr_color};">
                    {debt_ratio:.1f}%
                </div>
                <div style="font-size:0.8rem;color:#94a3b8;margin-top:0.2rem;">
                    Safe threshold: &lt; 30%
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Why this risk score? (c3) ──
        with c3:
            st.markdown('<div class="sec-title">🔍 Why This Risk Score?</div>', unsafe_allow_html=True)

            reasons = explain_risk(
                income, expenses, existing_emi, loan_amount,
                credit_score, credit_history, savings, debt_ratio,
            )

            level_cls  = {"high": "exp-high", "medium": "exp-medium", "low": "exp-low"}
            level_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}

            for r in reasons:
                cls  = level_cls.get(r["level"], "exp-low")
                icon = level_icon.get(r["level"], "✅")
                st.markdown(f"""
                <div class="exp-card {cls}">
                    {icon} &nbsp;{r["text"]}
                </div>
                """, unsafe_allow_html=True)
    # ───────────── TAB 2: Stress Timeline ─────────────
    with tab2:
        st.markdown('<div class="sec-title">📉 Savings Trajectory Over Time</div>', unsafe_allow_html=True)

        months       = list(range(0, tenure + 1))
        monthly_sav  = disposable - emi
        with_loan    = [monthly_sav * m + savings for m in months]
        without_loan = [disposable * m + savings for m in months]
        emi_cumul    = [emi * m for m in months]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=months, y=with_loan,
            name="Savings (with loan)",
            line=dict(color="#5b7cfa", width=2.5),
            fill="tozeroy", fillcolor="rgba(91,124,250,0.07)",
            hovertemplate="Month %{x}<br>₹%{y:,.0f}<extra></extra>",
        ))
        fig2.add_trace(go.Scatter(
            x=months, y=without_loan,
            name="Savings (no loan)",
            line=dict(color="#10d9a0", width=2, dash="dot"),
            hovertemplate="Month %{x}<br>₹%{y:,.0f}<extra></extra>",
        ))
        fig2.add_trace(go.Scatter(
            x=months, y=emi_cumul,
            name="Cumulative EMI paid",
            line=dict(color="#f87171", width=1.8, dash="dash"),
            hovertemplate="Month %{x}<br>₹%{y:,.0f}<extra></extra>",
        ))
        fig2.update_layout(
            **PLOTLY_LAYOUT, height=390,
            xaxis_title="Month", yaxis_title="Amount (₹)",
            hovermode="x unified",
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Breakeven note
        breakeven = None
        for i, (wl, nl) in enumerate(zip(with_loan, without_loan)):
            if nl - wl > loan_amount:
                breakeven = i
                break

        if breakeven:
            st.markdown(f"""
            <div style="padding:1rem 1.3rem;background:rgba(91,124,250,0.09);
                        border:1px solid rgba(91,124,250,0.25);border-radius:12px;
                        font-size:0.88rem;color:#8fa8ff;line-height:1.6;">
                💡 The opportunity cost of this loan exceeds the loan principal itself around
                <strong style="color:#f0f4ff;">Month {breakeven}</strong>.
                Plan your finances accordingly.
            </div>
            """, unsafe_allow_html=True)
        elif monthly_sav < 0:
            st.markdown("""
            <div style="padding:1rem 1.3rem;background:rgba(248,113,113,0.09);
                        border:1px solid rgba(248,113,113,0.25);border-radius:12px;
                        font-size:0.88rem;color:#fca5a5;line-height:1.6;">
                ⚠️ Your monthly savings will be <strong>negative</strong> with this loan.
                You may be drawing down existing savings each month to cover the EMI.
            </div>
            """, unsafe_allow_html=True)

    # ───────────── TAB 3: Explainable AI ─────────────
    

      
    # ───────────── TAB 4: AI Suggestions ─────────────
    with tab4:
        st.markdown('<div class="sec-title">💡 AI-Optimised Safer Plans</div>', unsafe_allow_html=True)

        best_plan  = None
        best_score = 999
        all_plans  = []

        for pct in np.arange(0.5, 1.05, 0.1):
            for t in [36, 48, 60, 72]:
                amt      = loan_amount * pct
                emi_alt  = calculate_emi(amt, interest_rate, t)
                s        = compute_risk_score(
                    income, expenses, existing_emi, amt, t,
                    interest_rate, credit_score, credit_history, savings,
                )
                _, rc, _, _ = get_risk_level(s)
                all_plans.append((round(pct * 100), amt, t, emi_alt, s, rc))
                if s < best_score:
                    best_score = s
                    best_plan  = (amt, t, emi_alt, s, rc)

        if best_plan:
            improvement = risk_score - best_plan[3]
            imp_color   = "#10d9a0" if improvement > 0 else "#f87171"
            st.markdown(f"""
            <div class="best-plan-card">
                <h4>🏆 Recommended Plan</h4>
                <div class="plan-metric">
                    <span class="pm-l">Loan Amount</span>
                    <span class="pm-v">{_fmt(best_plan[0])}</span>
                </div>
                <div class="plan-metric">
                    <span class="pm-l">Tenure</span>
                    <span class="pm-v">{best_plan[1]} months</span>
                </div>
                <div class="plan-metric">
                    <span class="pm-l">Monthly EMI</span>
                    <span class="pm-v">{_fmt(best_plan[2])}</span>
                </div>
                <div class="plan-metric">
                    <span class="pm-l">Risk Score</span>
                    <span class="pm-v" style="color:{best_plan[4]};">{best_plan[3]}/100</span>
                </div>
                <div style="margin-top:1.1rem;font-size:0.85rem;color:#94a3b8;line-height:1.6;">
                    This plan {"reduces your risk score by" if improvement > 0 else "has a risk score of"}
                    <strong style="color:{imp_color};">
                        {abs(improvement)} point{"s" if abs(improvement) != 1 else ""}
                    </strong>
                    {"compared to your current plan." if improvement > 0 else "— the same as your current plan."}
                </div>
            </div>
            """, unsafe_allow_html=True)

        
        
        

    # ───────────── TAB 5: Plan Comparison ─────────────
    with tab5:
        st.markdown('<div class="sec-title">📊 Your Plan vs AI Recommended Plan</div>', unsafe_allow_html=True)

        if best_plan:
            ai_interest = calculate_total_interest(best_plan[0], best_plan[2], best_plan[1])
            saving_diff = total_int - ai_interest

            # ── Metric comparison cards ──
            m1, m2, m3, m4, m5 = st.columns(5)
            metrics = [
                (m1, "Loan Amount",    _fmt(loan_amount),   _fmt(best_plan[0]),      loan_amount - best_plan[0]),
                (m2, "Monthly EMI",    _fmt(emi),           _fmt(best_plan[2]),      emi - best_plan[2]),
                (m3, "Tenure",         f"{tenure}m",        f"{best_plan[1]}m",      tenure - best_plan[1]),
                (m4, "Risk Score",     f"{risk_score}/100", f"{best_plan[3]}/100",   risk_score - best_plan[3]),
                (m5, "Total Interest", _fmt(total_int),     _fmt(ai_interest),       total_int - ai_interest),
            ]

            for col, label, your_v, ai_v, diff in metrics:
                # Lower is better for all except none of them (lower risk score, EMI, interest = better)
                if diff > 0:
                    diff_color, diff_arrow = "#10d9a0", "↓"
                elif diff < 0:
                    diff_color, diff_arrow = "#f87171", "↑"
                else:
                    diff_color, diff_arrow = "#94a3b8", "="

                with col:
                    st.markdown(f"""
                    <div style="background:var(--card-bg);border:1px solid var(--card-border);
                                border-radius:16px;padding:1.1rem;text-align:center;">
                        <div style="font-size:0.7rem;color:#4b6080;text-transform:uppercase;
                                    letter-spacing:0.07em;margin-bottom:0.6rem;font-weight:600;">
                            {label}
                        </div>
                        <div style="font-size:0.8rem;color:#94a3b8;margin-bottom:0.15rem;">Your Plan</div>
                        <div style="font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:700;
                                    color:#f0f4ff;margin-bottom:0.5rem;">{your_v}</div>
                        <div style="font-size:0.8rem;color:#94a3b8;margin-bottom:0.15rem;">AI Plan</div>
                        <div style="font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:700;
                                    color:{diff_color};">{ai_v} {diff_arrow}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Dataframe table ──
            df = pd.DataFrame({
                "Metric":      ["Loan Amount", "Monthly EMI", "Tenure", "Risk Score", "Total Interest"],
                "Your Plan":   [_fmt(loan_amount), _fmt(emi), f"{tenure} months", f"{risk_score}/100", _fmt(total_int)],
                "AI Plan":     [_fmt(best_plan[0]), _fmt(best_plan[2]), f"{best_plan[1]} months", f"{best_plan[3]}/100", _fmt(ai_interest)],
            })
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Bar charts ──
            c1, c2 = st.columns(2)
            with c1:
                fig5 = go.Figure(go.Bar(
                    x=["Your Plan", "AI Plan"],
                    y=[risk_score, best_plan[3]],
                    marker=dict(
                        color=["#f87171", "#10d9a0"],
                        line=dict(width=0),
                    ),
                    text=[f"{risk_score}", f"{best_plan[3]}"],
                    textposition="outside",
                    textfont=dict(color=["#f87171", "#10d9a0"], family="Syne", size=15),
                ))
                fig5.update_layout(
                    **PLOTLY_LAYOUT, title="Risk Score Comparison", height=290,
                    yaxis_range=[0, 115],
                )
                st.plotly_chart(fig5, use_container_width=True)

            with c2:
                fig6 = go.Figure(go.Bar(
                    x=["Your Plan", "AI Plan"],
                    y=[total_int, ai_interest],
                    marker=dict(
                        color=["#f87171", "#10d9a0"],
                        line=dict(width=0),
                    ),
                    text=[_fmt(total_int), _fmt(ai_interest)],
                    textposition="outside",
                    textfont=dict(color=["#f87171", "#10d9a0"], family="Syne", size=12),
                ))
                fig6.update_layout(
                    **PLOTLY_LAYOUT, title="Total Interest Paid", height=290,
                    yaxis_range=[0, total_int * 1.28] if total_int > 0 else [0, 1],
                )
                st.plotly_chart(fig6, use_container_width=True)

            # ── Savings callout ──
            if saving_diff > 0:
                st.markdown(f"""
                <div style="padding:1.3rem 1.6rem;
                            background:rgba(16,217,160,0.09);
                            border:1px solid rgba(16,217,160,0.25);
                            border-radius:14px;
                            display:flex;align-items:center;gap:1.2rem;">
                    <div style="font-size:2.2rem;">💰</div>
                    <div>
                        <div style="font-family:'Syne',sans-serif;font-size:1.25rem;
                                    font-weight:800;color:#10d9a0;">
                            Save {_fmt(saving_diff)}
                        </div>
                        <div style="font-size:0.86rem;color:#94a3b8;margin-top:0.2rem;">
                            in total interest by switching to the AI-recommended plan.
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No alternative plans could be computed. Please adjust your loan parameters.")

    # ── Recalculate CTA ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 2, 3])
    with c2:
        if st.button("← Recalculate", use_container_width=True):
            st.session_state.page = "calculator"
            st.session_state.step = 1
            st.rerun()
