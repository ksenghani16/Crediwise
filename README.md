# 📈 LoanAdvisor — Loan Affordability Smart Assistant

> Predict borrowing risk, explain why, and recommend safer loan options using AI.

---

## 🗂️ Full Project Structure

```
loan-advisor/
│
├── app.py                        ← Main Streamlit app (entry point)
├── requirements.txt              ← All dependencies
├── README.md                     ← This file
│
├── model/
│   ├── train_model.py            ← Run in Google Colab to train
│   ├── loan_risk_model.pkl       ← ✅ Generated after training (you create this)
│   └── scaler.pkl                ← ✅ Generated after training (you create this)
│
├── data/
│   ├── credit_risk_dataset.csv   ← Download from Kaggle (link below)
│   └── sessions.db               ← Auto-created SQLite database
│
├── utils/
│   ├── __init__.py
│   ├── calculator.py             ← EMI, safe EMI, max loan calculations
│   ├── risk_engine.py            ← Rule-based risk score engine (0–100)
│   ├── explainer.py              ← XAI: Plain language risk explanations
│   └── database.py               ← SQLite session storage
│
└── pages/
    ├── __init__.py
    ├── home.py                   ← Landing page
    ├── calculator.py             ← 2-step form (Income → Loan Details)
    └── dashboard.py              ← Full results dashboard
```

---

## 📊 Dataset

**Credit Risk Dataset** from Kaggle:
👉 https://www.kaggle.com/datasets/laotse/credit-risk-dataset

Download `credit_risk_dataset.csv` and place it in the `data/` folder.

**Key columns used:**
| Column | Description |
|--------|-------------|
| `person_income` | Annual income |
| `loan_amnt` | Loan amount requested |
| `loan_int_rate` | Interest rate |
| `loan_percent_income` | Loan/annual income ratio |
| `cb_person_cred_hist_length` | Credit history (years) |
| `loan_status` | Target: 0=safe, 1=risky |

---

## 🤖 Models Used

| Model | Purpose | Why |
|-------|---------|-----|
| **Random Forest** | Primary ML risk classifier | Best accuracy for tabular financial data, provides feature importance for XAI |
| **Logistic Regression** | Baseline comparison | Interpretable, fast |
| **Rule-based engine** | EMI & eligibility logic | Deterministic, always works even without .pkl |
| **Blended (ML + Rules)** | Final risk score | 60% ML + 40% rules = robust prediction |

---

## 🏗️ Setup Steps

### Step 1 — Clone/create the project folder in VS Code

```bash
mkdir loan-advisor
cd loan-advisor
# Paste all files from this structure
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Train the ML model (Google Colab)

1. Go to https://colab.research.google.com
2. Upload `model/train_model.py` and `data/credit_risk_dataset.csv`
3. Run all cells
4. Download `loan_risk_model.pkl` and `scaler.pkl`
5. Place them in your `model/` folder

> **Without the model:** The app still works! It uses the rule-based risk engine automatically.

### Step 5 — Run the app

```bash
streamlit run app.py
```

Open your browser at: http://localhost:8501

---

## ✨ Features

### 1. 🧮 EMI Calculator (Rule-based)
- Standard EMI formula: `P * r * (1+r)^n / ((1+r)^n - 1)`
- Calculates: Safe EMI, Max eligible loan, Disposable income

### 2. 🤖 AI Risk Prediction (ML)
- Random Forest trained on real credit risk data
- Outputs 0–100 risk score
- Blended with rule-based engine for robustness

### 3. 💡 Explainable AI (XAI)
- Plain language reasons: "Your debt ratio of 45% is above the safe limit of 30%"
- Color coded: 🔴 High 🟡 Medium 🟢 Low

### 4. 💰 Smart Loan Recommendations
- Auto-negotiates safer loan amount + tenure
- Shows 3 scenarios: Conservative / Recommended / Requested

### 5. 📈 Savings Impact Timeline
- Plotly chart: Savings with loan vs without loan over tenure
- Shows exact month where savings hit danger zone

### 6. 🗃️ Session Storage (SQLite)
- All analyses saved locally
- Can be used to show "history" feature

---

## 🎤 Hackathon Pitch (60 seconds)

> "Most loan apps are just calculators. LoanAdvisor is a **financial decision assistant**.
> It uses a Random Forest ML model trained on 32,000 real borrowers to predict your default risk.
> It explains exactly **why** you're risky using Explainable AI.
> Then it automatically **negotiates a safer loan plan** for you —
> and shows how your savings will look **5 years from now**.
> This isn't a calculator. This is your personal AI financial advisor."

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit + Plotly |
| ML Model | Scikit-learn (Random Forest) |
| Data | Pandas, NumPy |
| Database | SQLite (built-in) |
| Fonts | Google Fonts (DM Sans) |
