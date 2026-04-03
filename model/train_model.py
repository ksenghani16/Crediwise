# ============================================================
# train_model.py — Loan Risk Model Training
# Place this file in your project's /model/ folder.
#
# HOW TO RUN (Google Colab or local):
#   1. Upload credit_risk_dataset.csv to the same folder
#   2. Run:  python train_model.py
#   3. It will save loan_risk_model.pkl in the same /model/ folder
#   4. Your dashboard.py will auto-detect and use it
# ============================================================

import os
import warnings
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

warnings.filterwarnings("ignore")

# ─── STEP 1: Load Dataset ───────────────────────────────────
# Place credit_risk_dataset.csv in the same folder as this file
# Dataset: https://www.kaggle.com/datasets/laotse/credit-risk-dataset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "credit_risk_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "loan_risk_model.pkl")

print("=" * 50)
print("  LoanAdvisor — Model Training")
print("=" * 50)

df = pd.read_csv(DATA_PATH)
print(f"\n✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# ─── STEP 2: Clean Data ─────────────────────────────────────
df = df.dropna()
df = df[df['person_age'] < 100]           # remove age outliers
df = df[df['person_income'] < 10_000_000] # remove income outliers
print(f"✅ After cleaning: {df.shape[0]} rows")

# ─── STEP 3: Select Features ────────────────────────────────
# These 5 features match exactly what dashboard.py sends to the model
FEATURES = [
    'person_income',
    'loan_amnt',
    'loan_int_rate',
    'loan_percent_income',
    'cb_person_cred_hist_length'
]
TARGET = 'loan_status'   # 0 = safe, 1 = default/risky

X = df[FEATURES]
y = df[TARGET]
print(f"\n📊 Features: {FEATURES}")
print(f"📊 Target distribution:\n{y.value_counts().to_string()}")

# ─── STEP 4: Train / Test Split ─────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\n✅ Train size: {X_train.shape[0]}  |  Test size: {X_test.shape[0]}")

# ─── STEP 5: Train Random Forest ────────────────────────────
print("\n🌲 Training Random Forest...")
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# ─── STEP 6: Evaluate ───────────────────────────────────────
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n📈 Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Safe (0)", "Risky (1)"]))

# ─── STEP 7: Test with a sample input ───────────────────────
print("🧪 Sample prediction test:")
# income ₹50k/yr, loan ₹20k, rate 10.5%, percent_income 0.35, cred_hist 6yr
sample = pd.DataFrame([{
    "person_income": 50000,
    "loan_amnt": 20000,
    "loan_int_rate": 10.5,
    "loan_percent_income": 0.35,
    "cb_person_cred_hist_length": 6
}])
pred = model.predict(sample)[0]
prob = model.predict_proba(sample)[0][1]
print(f"   Prediction : {'🔴 Risky (1)' if pred == 1 else '🟢 Safe (0)'}")
print(f"   Risk Prob  : {prob * 100:.1f}%")

# ─── STEP 8: Save Model ─────────────────────────────────────
joblib.dump(model, MODEL_PATH)
print(f"\n✅ Model saved → {MODEL_PATH}")
print("\n" + "=" * 50)
print("  DONE! loan_risk_model.pkl is ready.")
print("  Your dashboard will now use ML predictions.")
print("=" * 50)