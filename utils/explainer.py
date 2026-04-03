def explain_risk(income, expenses, existing_emi, loan_amount, credit_score, credit_history, savings, debt_ratio) -> list:
    """
    Returns a list of reason dicts: {"text": str, "level": "high"|"medium"|"low"}
    Explainable AI — plain language reasons for the risk score.
    """
    reasons = []

    # Debt ratio check
    if debt_ratio > 50:
        reasons.append({
            "text": f"Debt-to-income ratio is {debt_ratio:.0f}% — well above the safe 30% limit. This significantly increases default risk.",
            "level": "high"
        })
    elif debt_ratio > 30:
        reasons.append({
            "text": f"Debt-to-income ratio is {debt_ratio:.0f}% — slightly above the safe 30% threshold. Keep it below 30% for comfort.",
            "level": "medium"
        })
    else:
        reasons.append({
            "text": f"Debt-to-income ratio is {debt_ratio:.0f}% — within safe range.",
            "level": "low"
        })

    # Credit score check
    if credit_score < 650:
        reasons.append({
            "text": f"Credit score {credit_score} is below the ideal 700+. Lenders may charge higher rates or reject the application.",
            "level": "high"
        })
    elif credit_score < 700:
        reasons.append({
            "text": f"Credit score {credit_score} is below ideal (700+). This increases perceived risk.",
            "level": "medium"
        })
    else:
        reasons.append({
            "text": f"Credit score {credit_score} is good — above the 700 threshold.",
            "level": "low"
        })

    # Savings check
    savings_rate = savings / income * 100 if income > 0 else 0
    if savings_rate < 5:
        reasons.append({
            "text": f"Savings rate is only {savings_rate:.1f}%. A buffer of 10%+ is strongly recommended for emergencies.",
            "level": "high"
        })
    elif savings_rate < 10:
        reasons.append({
            "text": f"Savings rate is {savings_rate:.1f}%. A buffer of 10%+ is recommended.",
            "level": "medium"
        })
    else:
        reasons.append({
            "text": f"Savings rate of {savings_rate:.1f}% is healthy — good financial buffer.",
            "level": "low"
        })

    # Credit history
    if credit_history < 3:
        reasons.append({
            "text": f"Credit history of only {credit_history} years. Lenders prefer 5+ years of history.",
            "level": "medium"
        })
    elif credit_history >= 7:
        reasons.append({
            "text": f"Credit history of {credit_history} years is excellent.",
            "level": "low"
        })

    # Disposable income
    disposable = income - expenses - existing_emi
    if disposable < income * 0.15:
        reasons.append({
            "text": "Low disposable income after expenses and EMIs. Any additional expense could cause stress.",
            "level": "high"
        })

    return reasons
