from utils.calculator import calculate_emi


def compute_risk_score(
    income: float,
    expenses: float,
    existing_emi: float,
    loan_amount: float,
    tenure: int,
    interest_rate: float,
    credit_score: int,
    credit_history: int,
    savings: float,
) -> int:
    """
    Returns a risk score from 0 (safest) to 100 (highest risk).
    Factors: debt ratio, credit score, savings rate, loan-to-income, credit history, disposable buffer.
    """
    score = 0

    emi = calculate_emi(loan_amount, interest_rate, tenure)
    total_debt = existing_emi + emi
    debt_ratio = (total_debt / income * 100) if income > 0 else 100

    # --- Debt-to-Income (max 35 pts) ---
    if debt_ratio > 60:
        score += 35
    elif debt_ratio > 40:
        score += 22
    elif debt_ratio > 30:
        score += 12
    elif debt_ratio > 20:
        score += 4

    # --- Credit Score (max 25 pts) ---
    if credit_score < 580:
        score += 25
    elif credit_score < 650:
        score += 18
    elif credit_score < 700:
        score += 11
    elif credit_score < 750:
        score += 5

    # --- Savings Rate (max 15 pts) ---
    savings_rate = (savings / income * 100) if income > 0 else 0
    if savings_rate < 5:
        score += 15
    elif savings_rate < 10:
        score += 8
    elif savings_rate < 20:
        score += 3

    # --- Loan-to-Annual-Income (max 15 pts) ---
    loan_pct = (loan_amount / (income * 12) * 100) if income > 0 else 100
    if loan_pct > 80:
        score += 15
    elif loan_pct > 50:
        score += 8
    elif loan_pct > 30:
        score += 3

    # --- Credit History (max 10 pts, bonus -3) ---
    if credit_history < 2:
        score += 10
    elif credit_history < 5:
        score += 5
    elif credit_history >= 7:
        score = max(0, score - 3)

    # --- Disposable buffer after all EMIs (max 15 pts) ---
    disposable_after = income - expenses - total_debt
    if disposable_after < 0:
        score += 15
    elif disposable_after < income * 0.10:
        score += 9
    elif disposable_after < income * 0.20:
        score += 4

    return min(max(score, 0), 100)


def get_risk_level(score: int):
    """
    Returns (label, accent_color, bg_color, icon).
    """
    if score >= 60:
        return "High Risk", "#f87171", "rgba(248,113,113,0.09)", "🔴"
    elif score >= 35:
        return "Moderate Risk", "#fbbf24", "rgba(251,191,36,0.09)", "🟡"
    else:
        return "Low Risk", "#10d9a0", "rgba(16,217,160,0.09)", "🟢"
