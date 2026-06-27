# 🏦 Bank Customer Churn Prediction

> AI-powered web dashboard to identify customers at risk of leaving the bank, built with **FastAPI**, **Gradient Boosting**, and a premium light glassmorphism banking-themed UI.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?logo=scikit-learn)](https://scikit-learn.org/)
[![Accuracy](https://img.shields.io/badge/Accuracy-86.6%25-success)](/)

---

## 📋 Project Overview

This project trains a **Gradient Boosting Classifier** on the [Bank Customer Churn Modelling dataset](https://www.kaggle.com/datasets/shantanudhakadd/bank-customer-churn-prediction) and exposes it as a REST API with an interactive web dashboard.

Given 10 customer features, the model predicts whether a customer will **churn** (leave the bank) or be **retained**, along with a churn probability and risk level assessment.

---

## 🗂️ Project Structure

```
Bank Churn Prediction (Gradient Boosting)/
├── app/
│   ├── __init__.py          # Package init
│   ├── main.py              # FastAPI application entry point
│   ├── predictor.py         # Model loading & inference logic
│   ├── models.py            # Pydantic request/response schemas
│   └── routers/
│       ├── __init__.py
│       └── predict.py       # POST /predict endpoint
├── models/
│   ├── gb_churn_model.joblib   # Trained Gradient Boosting model
│   └── label_encoder.joblib    # Label encoder artifact
├── static/
│   ├── index.html           # Main SPA dashboard
│   ├── css/
│   │   └── style.css        # Light glassmorphism banking theme
│   └── js/
│       └── app.js           # Frontend logic & API integration
├── churn-prediction-bank-gradient-boosting.ipynb  # Training notebook
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Ensure Model Files Are in Place

The two model artifacts must be in the `models/` folder:
```
models/
├── gb_churn_model.joblib
└── label_encoder.joblib
```

> **Note:** If the `.joblib` files are in the root directory, move them to `models/`:
> ```bash
> mkdir models
> move gb_churn_model.joblib models\
> move label_encoder.joblib models\
> ```

### 3. Start the Server

```bash
uvicorn app.main:app --reload
```

The app will be available at **http://localhost:8000**

---

## 🌐 Web Dashboard

Open `http://localhost:8000` in your browser. The dashboard has three tabs:

| Tab | Description |
|-----|-------------|
| 🔮 **Predict** | Enter customer details and get an instant churn prediction with probability gauge and risk level |
| 🕓 **History** | View all predictions made in the current session with sortable table |
| 📊 **Model Info** | Explore model parameters, performance metrics, feature importances, confusion matrix, and API docs |

### Quick Fill Buttons
Use the **Sample Customers** buttons to populate the form instantly:
- ✅ **Safe Customer** — Low churn risk profile
- ⚠️ **At-Risk Customer** — Medium-high churn risk profile  
- 🚨 **Critical Risk** — Very high churn probability

---

## 🔌 REST API Reference

Base URL: `http://localhost:8000`

### `POST /predict`

Predict churn for a single customer.

**Request Body:**
```json
{
  "credit_score": 619,
  "geography": "France",
  "gender": "Female",
  "age": 42,
  "tenure": 2,
  "balance": 0.0,
  "num_of_products": 1,
  "has_cr_card": 1,
  "is_active_member": 1,
  "estimated_salary": 101348.88
}
```

**Response:**
```json
{
  "prediction": 1,
  "label": "Churned",
  "churn_probability": 0.7823,
  "retain_probability": 0.2177,
  "risk_level": "High",
  "processing_time_ms": 1.234
}
```

| Field | Type | Description |
|-------|------|-------------|
| `prediction` | int | `0` = Retained, `1` = Churned |
| `label` | str | `"Retained"` or `"Churned"` |
| `churn_probability` | float | Churn probability (0–1) |
| `retain_probability` | float | Retention probability (0–1) |
| `risk_level` | str | `Low` / `Medium` / `High` / `Critical` |
| `processing_time_ms` | float | Inference time in milliseconds |

### Risk Levels

| Risk Level | Churn Probability |
|------------|------------------|
| 🟢 Low     | < 25% |
| 🟡 Medium  | 25% – 50% |
| 🔴 High    | 50% – 75% |
| 🚨 Critical | > 75% |

### `GET /health`
Returns API and model status.

### `GET /stats`
Returns session prediction statistics (total, churn count, retention rate).

### `GET /docs`
Interactive Swagger UI documentation.

### `GET /redoc`
ReDoc API documentation.

---

## 🤖 Model Details

| Property | Value |
|----------|-------|
| Algorithm | `GradientBoostingClassifier` (scikit-learn) |
| n_estimators | 100 |
| learning_rate | 0.1 |
| max_depth | 3 |
| random_state | 42 |
| Dataset | Churn Modelling (10,000 rows) |
| Train/Test Split | 80% / 20% |
| **Test Accuracy** | **86.6%** |

### Features Used

| Feature | Type | Range |
|---------|------|-------|
| `CreditScore` | int | 300 – 850 |
| `Geography` | str | France / Germany / Spain |
| `Gender` | str | Male / Female |
| `Age` | int | 18 – 92 |
| `Tenure` | int | 0 – 10 years |
| `Balance` | float | ≥ 0 |
| `NumOfProducts` | int | 1 – 4 |
| `HasCrCard` | int (bool) | 0 or 1 |
| `IsActiveMember` | int (bool) | 0 or 1 |
| `EstimatedSalary` | float | ≥ 0 |

### Classification Report (Test Set)

```
              precision    recall  f1-score   support

    Retained       0.88      0.96      0.92      1607
     Churned       0.76      0.47      0.58       393

    accuracy                           0.87      2000
   macro avg       0.82      0.72      0.75      2000
weighted avg       0.86      0.87      0.85      2000
```

### Confusion Matrix

|  | Predicted: Retained | Predicted: Churned |
|--|--------------------|--------------------|
| **Actual: Retained** | 1,547 ✅ | 60 ❌ |
| **Actual: Churned**  | 208 ❌  | 185 ✅ |

---

## 🎨 UI Design

The dashboard features a **light glassmorphism banking theme**:

- 🏦 **Navy + Gold palette** — professional banking aesthetic
- 🔲 **Glass cards** — `backdrop-filter: blur(20px)` with translucent white backgrounds
- ✨ **Micro-animations** — floating hero icon, animated probability gauge, feature importance bars
- 📱 **Fully responsive** — mobile-friendly layout
- 🎛️ **Interactive controls** — range sliders, toggle switches, instant live preview
- 🔔 **Toast notifications** — real-time feedback on predictions

---

## 📄 License

This project is for educational and demonstration purposes.
