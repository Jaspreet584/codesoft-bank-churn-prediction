"""
Model loading and inference logic for Bank Churn Prediction.

The Gradient Boosting model was trained on the Churn Modelling dataset.
Features (in order):
    CreditScore, Geography (encoded), Gender (encoded), Age, Tenure,
    Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary

Geography encoding: France=0, Germany=1, Spain=2
Gender encoding:    Female=0, Male=1
"""
import logging
import time
from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

# Globals — loaded once at startup
_model = None
_label_encoder = None  # kept for reference / future use

# Session stats
_stats: Dict[str, Any] = {
    "total_predictions": 0,
    "churn_count": 0,
    "retained_count": 0,
}

# Fixed encodings matching the training notebook's LabelEncoder order
GEOGRAPHY_MAP = {"France": 0, "Germany": 1, "Spain": 2}
GENDER_MAP = {"Female": 0, "Male": 1}


def load_models() -> None:
    """Load model artifacts from the models/ directory."""
    global _model, _label_encoder

    model_path = MODELS_DIR / "gb_churn_model.joblib"
    encoder_path = MODELS_DIR / "label_encoder.joblib"

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    _model = joblib.load(model_path)
    logger.info("Gradient Boosting model loaded from %s", model_path)

    if encoder_path.exists():
        _label_encoder = joblib.load(encoder_path)
        logger.info("Label encoder loaded from %s", encoder_path)


def is_model_loaded() -> bool:
    return _model is not None


def predict(
    credit_score: int,
    geography: str,
    gender: str,
    age: int,
    tenure: int,
    balance: float,
    num_of_products: int,
    has_cr_card: int,
    is_active_member: int,
    estimated_salary: float,
) -> Dict[str, Any]:
    """Run inference and return prediction details."""
    if not is_model_loaded():
        raise RuntimeError("Model is not loaded. Call load_models() first.")

    # Encode categoricals exactly as done during training
    geo_enc = GEOGRAPHY_MAP.get(geography)
    gen_enc = GENDER_MAP.get(gender)

    if geo_enc is None:
        raise ValueError(f"Unknown geography: '{geography}'. Expected France, Germany, or Spain.")
    if gen_enc is None:
        raise ValueError(f"Unknown gender: '{gender}'. Expected Male or Female.")

    # Build feature vector in training order
    features = np.array([[
        credit_score,   # CreditScore
        geo_enc,        # Geography (encoded)
        gen_enc,        # Gender (encoded)
        age,            # Age
        tenure,         # Tenure
        balance,        # Balance
        num_of_products,# NumOfProducts
        has_cr_card,    # HasCrCard
        is_active_member,# IsActiveMember
        estimated_salary,# EstimatedSalary
    ]], dtype=float)

    start = time.perf_counter()
    prediction = int(_model.predict(features)[0])
    probabilities = _model.predict_proba(features)[0]
    elapsed_ms = (time.perf_counter() - start) * 1000

    churn_prob = float(probabilities[1])
    retain_prob = float(probabilities[0])

    # Determine risk level based on churn probability
    if churn_prob < 0.25:
        risk_level = "Low"
    elif churn_prob < 0.50:
        risk_level = "Medium"
    elif churn_prob < 0.75:
        risk_level = "High"
    else:
        risk_level = "Critical"

    # Update session stats
    _stats["total_predictions"] += 1
    if prediction == 1:
        _stats["churn_count"] += 1
    else:
        _stats["retained_count"] += 1

    return {
        "prediction": prediction,
        "label": "Churned" if prediction == 1 else "Retained",
        "churn_probability": round(churn_prob, 4),
        "retain_probability": round(retain_prob, 4),
        "risk_level": risk_level,
        "processing_time_ms": round(elapsed_ms, 3),
    }


def get_session_stats() -> Dict[str, Any]:
    """Return session-level prediction statistics."""
    total = _stats["total_predictions"]
    churn_rate = (_stats["churn_count"] / total * 100) if total > 0 else 0.0
    return {
        "total_predictions": total,
        "churn_count": _stats["churn_count"],
        "retained_count": _stats["retained_count"],
        "churn_rate_pct": round(churn_rate, 2),
    }
