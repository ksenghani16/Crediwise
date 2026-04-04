import math


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Calculate monthly EMI given principal, annual interest rate (%), and tenure in months."""
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return round(principal / tenure_months, 2)
    try:
        factor = math.pow(1 + monthly_rate, tenure_months)
        emi = principal * monthly_rate * factor / (factor - 1)
        return round(emi, 2)
    except (ZeroDivisionError, OverflowError):
        return 0.0


def calculate_safe_emi(income: float, expenses: float, existing_emi: float) -> float:
    """Safe EMI = 40% of disposable income after expenses and existing EMIs."""
    disposable = income - expenses - existing_emi
    if disposable <= 0:
        return 0.0
    return round(disposable * 0.40, 2)


def calculate_max_loan(safe_emi: float, annual_rate: float, tenure_months: int) -> float:
    """Maximum loan principal that fits within the safe EMI."""
    if safe_emi <= 0 or tenure_months <= 0:
        return 0.0
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return round(safe_emi * tenure_months, 2)
    try:
        factor = math.pow(1 + monthly_rate, tenure_months)
        max_loan = safe_emi * (factor - 1) / (monthly_rate * factor)
        return round(max_loan, 2)
    except (ZeroDivisionError, OverflowError):
        return 0.0


def calculate_total_interest(principal: float, emi: float, tenure_months: int) -> float:
    """Total interest paid over the loan tenure."""
    if principal <= 0 or emi <= 0 or tenure_months <= 0:
        return 0.0
    return round(max(emi * tenure_months - principal, 0), 2)


def calculate_emi_ratio(emi: float, income: float) -> float:
    """EMI as a percentage of monthly income."""
    if income <= 0:
        return 0.0
    return round((emi / income) * 100, 2)


def calculate_disposable_income(income: float, expenses: float, total_emi: float) -> float:
    """Disposable income after expenses and EMI deductions."""
    return round(income - expenses - total_emi, 2)
