# Crediwise — AI Loan Intelligence

**Crediwise** is a polished Streamlit-based loan advisory dashboard that blends financial analytics, rule-based credit risk scoring, and machine learning to help users make smarter borrowing decisions.

## Project Overview

This project delivers a modern personal finance tool with:
- Responsive borrower onboarding and authentication flows
- Real-time EMI planning and safe borrowing calculations
- A hybrid risk scoring engine combining domain rules and a trained ML model
- Personalized loan plan recommendations and credit risk insights
- Interactive visualizations and downloadable reports

## Key Features

- **Loan affordability calculator**: Computes EMI, total interest, safe EMI threshold, and maximum affordable loan amounts.
- **Credit risk engine**: Evaluates loan risk using debt ratios, credit score, savings buffer, credit history, and disposable income.
- **Blended ML risk scoring**: Uses a trained Random Forest model (`loan_risk_model.pkl`) to augment rule-based risk evaluations.
- **User-friendly Streamlit UI**: Clean page navigation, dashboard views, calculator interface, and feedback/contact pages.
- **End-to-end data workflow**: Includes dataset management, model training, and integration with the dashboard.

## Tech Stack

- Python 3
- Streamlit
- pandas, NumPy
- scikit-learn
- Plotly, Matplotlib, Seaborn
- joblib

## Repository Structure

- `app.py` — Main Streamlit app entry point and global configuration
- `pages/` — Streamlit pages for home, dashboard, calculator, auth, profile, and more
- `utils/` — Core utilities for authentication, calculators, ML explainability, reporting, and risk scoring
- `model/` — Training script and dataset for building the loan risk classifier
- `data/` — Credit risk dataset source file

## How it Works

1. Users enter income, expenses, existing EMIs, loan details, credit score, credit history, and savings.
2. The app calculates monthly EMI, total interest, and safe borrowing limits.
3. A custom risk engine scores the applicant using financial heuristics.
4. If available, the app uses the trained ML model to refine risk estimates.
5. The dashboard provides risk labels, repayment guidance, and recommended loan plans.

## Running Locally

1. Create a Python environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
3. Open the displayed local URL in your browser.

## Notes

- Place `credit_risk_dataset.csv` in `model/` and run `python model/train_model.py` to generate `loan_risk_model.pkl`.
- The app will automatically load the trained ML model if the file exists.

