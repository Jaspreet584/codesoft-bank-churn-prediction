"""
Pydantic models for Bank Churn Prediction API request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------
class CustomerInput(BaseModel):
    """Input features for a single customer churn prediction."""

    credit_score: int = Field(
        ...,
        ge=300,
        le=850,
        description="Customer credit score (300–850)",
        example=619,
    )
    geography: str = Field(
        ...,
        description="Customer country: France, Germany, or Spain",
        example="France",
    )
    gender: str = Field(
        ...,
        description="Customer gender: Male or Female",
        example="Female",
    )
    age: int = Field(
        ...,
        ge=18,
        le=100,
        description="Customer age in years",
        example=42,
    )
    tenure: int = Field(
        ...,
        ge=0,
        le=10,
        description="Number of years the customer has been with the bank",
        example=2,
    )
    balance: float = Field(
        ...,
        ge=0.0,
        description="Account balance in currency units",
        example=0.0,
    )
    num_of_products: int = Field(
        ...,
        ge=1,
        le=4,
        description="Number of bank products the customer uses",
        example=1,
    )
    has_cr_card: int = Field(
        ...,
        ge=0,
        le=1,
        description="Whether the customer has a credit card (1=Yes, 0=No)",
        example=1,
    )
    is_active_member: int = Field(
        ...,
        ge=0,
        le=1,
        description="Whether the customer is an active member (1=Yes, 0=No)",
        example=1,
    )
    estimated_salary: float = Field(
        ...,
        ge=0.0,
        description="Estimated annual salary",
        example=101348.88,
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class PredictionResponse(BaseModel):
    """Response schema for a churn prediction."""

    prediction: int = Field(..., description="0 = Retained, 1 = Churned")
    label: str = Field(..., description="Human-readable prediction label")
    churn_probability: float = Field(
        ..., description="Probability that the customer will churn (0–1)"
    )
    retain_probability: float = Field(
        ..., description="Probability that the customer will be retained (0–1)"
    )
    risk_level: str = Field(
        ..., description="Risk level: Low | Medium | High | Critical"
    )
    processing_time_ms: float = Field(
        ..., description="Inference time in milliseconds"
    )


class HealthResponse(BaseModel):
    """Health-check response schema."""

    model_config = {"protected_namespaces": ()}

    status: str
    model_loaded: bool
    model_type: str = "Gradient Boosting Classifier"


class StatsResponse(BaseModel):
    """Session statistics response schema."""

    total_predictions: int
    churn_count: int
    retained_count: int
    churn_rate_pct: float
