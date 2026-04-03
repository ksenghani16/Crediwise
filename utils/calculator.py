import math

def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Calculate EMI using standard formula: P * r * (1+r)^n / ((1+r)^n - 1)"""
    if principal <= 0 or tenure_months <= 0:
        return 0
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return principal / tenure_months
    emi = principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months) / \
          (math.pow(1 + monthly_rate, tenure_months) - 1)
    return round(emi, 2)

def calculate_safe_emi(income: float, expenses: float, existing_emi: float) -> float:
    """Safe EMI = 40% of net income (after expenses and existing EMI)"""
    disposable = income - expenses - existing_emi
    safe = disposable * 0.40
    return max(safe, 0)

def calculate_max_loan(safe_emi: float, annual_rate: float, tenure_months: int) -> float:
    """Reverse-calculate max loan from safe EMI"""
    if safe_emi <= 0 or tenure_months <= 0:
        return 0
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return safe_emi * tenure_months
    max_loan = safe_emi * (math.pow(1 + monthly_rate, tenure_months) - 1) / \
               (monthly_rate * math.pow(1 + monthly_rate, tenure_months))
    return round(max_loan, 2)

def calculate_total_interest(principal: float, emi: float, tenure_months: int) -> float:
    return round(emi * tenure_months - principal, 2)
