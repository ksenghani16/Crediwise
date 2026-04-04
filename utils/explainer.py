def explain_risk(
    income: float,
    expenses: float,
    existing_emi: float,
    loan_amount: float,
    credit_score: int,
    credit_history: int,
    savings: float,
    debt_ratio: float,
) -> list:
    """
    Returns a list of dicts with 'text' and 'level' (high | medium | low)
    explaining what drives the computed risk score.
    Thresholds are consistent with risk_engine.py.
    """
    reasons = []

    # ── Debt-to-Income ──
    if debt_ratio > 50:
        reasons.append({
            "text": f"Your debt-to-income ratio is {debt_ratio:.1f}% — well above the safe 30% ceiling. "
                    "This is the single strongest predictor of loan default.",
            "level": "high",
        })
    elif debt_ratio > 30:
        reasons.append({
            "text": f"Your debt-to-income ratio is {debt_ratio:.1f}% — slightly above the recommended 30% threshold. "
                    "Reducing existing obligations before taking this loan would help.",
            "level": "medium",
        })
    else:
        reasons.append({
            "text": f"Your debt-to-income ratio is {debt_ratio:.1f}% — well within the safe zone (< 30%). "
                    "This is a strong positive signal for lenders.",
            "level": "low",
        })

    # ── Credit Score ──
    if credit_score < 650:
        reasons.append({
            "text": f"Your credit score of {credit_score} is below the minimum preferred threshold of 650. "
                    "Lenders may reject the application or charge significantly higher interest rates.",
            "level": "high",
        })
    elif credit_score < 700:
        reasons.append({
            "text": f"Your credit score of {credit_score} is below the ideal 700+ mark. "
                    "This slightly increases perceived risk; paying bills on time for 6–12 months can improve it.",
            "level": "medium",
        })
    elif credit_score < 750:
        reasons.append({
            "text": f"Your credit score of {credit_score} is good. Lenders will view this favourably, "
                    "though a score above 750 would unlock the best rates.",
            "level": "low",
        })
    else:
        reasons.append({
            "text": f"Excellent credit score of {credit_score}. This puts you in the top borrower tier "
                    "and should secure competitive interest rates.",
            "level": "low",
        })

    # ── Savings Rate ──
    savings_rate = (savings / income * 100) if income > 0 else 0
    if savings_rate < 5:
        reasons.append({
            "text": f"Your savings rate is only {savings_rate:.1f}%. Without a meaningful buffer, "
                    "any unexpected expense — medical, job loss, repairs — could trigger a default.",
            "level": "high",
        })
    elif savings_rate < 10:
        reasons.append({
            "text": f"Your savings rate of {savings_rate:.1f}% is below the recommended 10%. "
                    "Building a 3-month emergency fund before taking on new debt is strongly advisable.",
            "level": "medium",
        })
    else:
        reasons.append({
            "text": f"Your savings rate of {savings_rate:.1f}% is healthy. "
                    "Maintaining this buffer alongside the new EMI will reduce financial fragility.",
            "level": "low",
        })

    # ── Credit History ──
    if credit_history < 2:
        reasons.append({
            "text": f"A credit history of only {credit_history} year(s) is very thin. "
                    "Lenders strongly prefer borrowers with at least 5 years of repayment history.",
            "level": "high",
        })
    elif credit_history < 5:
        reasons.append({
            "text": f"Your credit history of {credit_history} years is moderate. "
                    "Lenders prefer 5+ years; your risk premium may be slightly higher.",
            "level": "medium",
        })
    else:
        reasons.append({
            "text": f"A credit history of {credit_history} years is solid. "
                    "This gives lenders confidence in your repayment track record.",
            "level": "low",
        })

    # ── Disposable Income after all obligations ──
    disposable = income - expenses - existing_emi
    if disposable < income * 0.10:
        reasons.append({
            "text": "After existing expenses and EMIs, your disposable income is very low (< 10% of income). "
                    "Adding a new EMI could leave you with almost no room to manoeuvre in difficult months.",
            "level": "high",
        })
    elif disposable < income * 0.20:
        reasons.append({
            "text": f"Your disposable income ({disposable:,.0f} ₹) is moderate. "
                    "Keep non-essential spending in check to ensure EMI payments stay comfortable.",
            "level": "medium",
        })
    else:
        reasons.append({
            "text": f"Your disposable income of ₹{disposable:,.0f} provides a comfortable cushion "
                    "for servicing the new EMI alongside existing obligations.",
            "level": "low",
        })

    return reasons
