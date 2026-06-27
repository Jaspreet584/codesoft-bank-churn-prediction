"""
/predict router for Bank Churn Prediction API.
"""
import logging

from fastapi import APIRouter, HTTPException

from app import predictor
from app.models import CustomerInput, PredictionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post(
    "",
    response_model=PredictionResponse,
    summary="Predict customer churn",
    description=(
        "Submit customer features and receive a churn prediction, "
        "probability scores, and risk level."
    ),
)
async def predict_churn(customer: CustomerInput) -> PredictionResponse:
    """Run churn prediction for a single customer."""
    if not predictor.is_model_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please try again later.",
        )

    try:
        result = predictor.predict(
            credit_score=customer.credit_score,
            geography=customer.geography,
            gender=customer.gender,
            age=customer.age,
            tenure=customer.tenure,
            balance=customer.balance,
            num_of_products=customer.num_of_products,
            has_cr_card=customer.has_cr_card,
            is_active_member=customer.is_active_member,
            estimated_salary=customer.estimated_salary,
        )
        return PredictionResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error during prediction: %s", exc)
        raise HTTPException(status_code=500, detail="Internal prediction error.") from exc
