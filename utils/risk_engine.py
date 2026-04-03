def compute_risk_score(income, expenses, existing_emi, loan_amount, tenure, interest_rate, credit_score, credit_history, savings) -> int:
    """
    Rule-based risk score 0–100. Higher = more risky.
    Combines: debt ratio, credit score, savings rate, income buffer.
    """
    score = 0

    # 1. Debt-to-income ratio (most important)
    from utils.calculator import calculate_emi
    emi = calculate_emi(loan_amount, interest_rate, tenure)
    total_debt = existing_emi + emi
    debt_ratio = total_debt / income * 100 if income > 0 else 100

    if debt_ratio > 60:
        score += 35
    elif debt_ratio > 40:
        score += 20
    elif debt_ratio > 30:
        score += 10
    else:
        score += 0

    # 2. Credit score
    if credit_score < 580:
        score += 25
    elif credit_score < 650:
        score += 18
    elif credit_score < 700:
        score += 10
    elif credit_score < 750:
        score += 5
    else:
        score += 0

    # 3. Savings rate
    savings_rate = savings / income * 100 if income > 0 else 0
    if savings_rate < 5:
        score += 15
    elif savings_rate < 10:
        score += 8
    elif savings_rate < 20:
        score += 3
    else:
        score += 0

    # 4. Loan to annual income
    loan_pct = loan_amount / (income * 12) * 100 if income > 0 else 100
    if loan_pct > 80:
        score += 15
    elif loan_pct > 50:
        score += 8
    elif loan_pct > 30:
        score += 3

    # 5. Credit history
    if credit_history < 2:
        score += 10
    elif credit_history < 5:
        score += 5
    elif credit_history >= 7:
        score -= 3  # bonus

    # 6. Income buffer after all EMIs
    disposable_after = income - expenses - total_debt
    if disposable_after < 0:
        score += 15
    elif disposable_after < income * 0.1:
        score += 8
    elif disposable_after < income * 0.2:
        score += 3

    return min(max(score, 0), 100)


def get_risk_level(score: int):
    """Returns (label, text_color, bg_color)"""
    if score >= 60:
        return "High Risk", "#dc2626", "#fef2f2"
    elif score >= 35:
        return "Medium Risk", "#d97706", "#fffbeb"
    else:
        return "Low Risk", "#16a34a", "#f0fdf4"
