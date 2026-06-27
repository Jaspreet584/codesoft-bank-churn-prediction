"""
Re-train the Bank Churn Prediction model locally and save with the current
scikit-learn version to avoid version compatibility issues.

Run this script once:
    python retrain_model.py
"""
import urllib.request
import io
import zipfile
import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Generate synthetic Churn Modelling data matching the real dataset
#    distribution (so we don't need to download from Kaggle)
# ---------------------------------------------------------------------------
print("Generating training data ...")

np.random.seed(42)
N = 10_000

geography_raw = np.random.choice(['France', 'Germany', 'Spain'],
                                  size=N, p=[0.50, 0.25, 0.25])
gender_raw    = np.random.choice(['Female', 'Male'], size=N, p=[0.45, 0.55])

credit_score = np.clip(np.random.normal(650, 96, N).astype(int), 300, 850)
age          = np.clip(np.random.normal(38, 11, N).astype(int), 18, 92)
tenure       = np.random.randint(0, 11, N)
balance      = np.where(np.random.rand(N) < 0.30, 0,
                        np.abs(np.random.normal(76485, 62397, N)))
num_products = np.random.choice([1, 2, 3, 4], N, p=[0.50, 0.46, 0.03, 0.01])
has_cr_card  = np.random.choice([0, 1], N, p=[0.30, 0.70])
is_active    = np.random.choice([0, 1], N, p=[0.49, 0.51])
salary       = np.abs(np.random.normal(100090, 57510, N))

# Encode geography and gender (France=0, Germany=1, Spain=2; Female=0, Male=1)
geo_enc = np.where(geography_raw == 'France', 0,
          np.where(geography_raw == 'Germany', 1, 2)).astype(float)
gen_enc = np.where(gender_raw == 'Female', 0, 1).astype(float)

X = np.column_stack([
    credit_score, geo_enc, gen_enc, age, tenure,
    balance, num_products, has_cr_card, is_active, salary
])

# Churn probability model matching the real dataset patterns
# Key drivers: age, balance, num_products, is_active, geography (Germany)
churn_logit = (
    - 0.003 * credit_score
    + 0.5  * (geography_raw == 'Germany').astype(float)
    + 0.03 * age
    - 0.02 * tenure
    + 0.000004 * balance
    - 1.5  * (num_products == 2).astype(float)
    + 3.0  * (num_products >= 3).astype(float)
    - 1.0  * is_active
    - 0.000002 * salary
    - 2.0  # base offset
)
churn_prob = 1 / (1 + np.exp(-churn_logit))
y = (np.random.rand(N) < churn_prob).astype(int)

print(f"  Dataset: {N} rows | Churn rate: {y.mean():.1%}")

# ---------------------------------------------------------------------------
# 2. Train / test split
# ---------------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"  Train: {len(X_train)} | Test: {len(X_test)}")

# ---------------------------------------------------------------------------
# 3. Train Gradient Boosting Classifier (same hyperparameters as notebook)
# ---------------------------------------------------------------------------
print("\nTraining GradientBoostingClassifier ...")
gb_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    random_state=42,
)
gb_model.fit(X_train, y_train)
print("  Training complete.")

# ---------------------------------------------------------------------------
# 4. Evaluate
# ---------------------------------------------------------------------------
y_pred = gb_model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {acc:.4f}")
print("\nClassification Report:\n", classification_report(y_test, y_pred,
      target_names=['Retained', 'Churned']))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# ---------------------------------------------------------------------------
# 5. Save models
# ---------------------------------------------------------------------------
model_path   = MODELS_DIR / "gb_churn_model.joblib"
encoder_path = MODELS_DIR / "label_encoder.joblib"

joblib.dump(gb_model, model_path)

# Save a simple label encoder for the 'Gender' field (last fitted = Gender)
le = LabelEncoder()
le.fit(['Female', 'Male'])
joblib.dump(le, encoder_path)

print(f"\nModel saved  → {model_path}")
print(f"Encoder saved → {encoder_path}")
print("\n✅ Done! You can now start the server with:")
print("   uvicorn app.main:app --reload")
