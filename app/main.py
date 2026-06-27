"""
FastAPI application entry point for the Bank Churn Prediction Dashboard.

Run with:
    uvicorn app.main:app --reload
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import predictor
from app.models import HealthResponse, StatsResponse
from app.routers import predict

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup, release on shutdown."""
    logger.info("Starting Bank Churn Prediction API ...")
    try:
        predictor.load_models()
        logger.info("Gradient Boosting model ready.")
    except FileNotFoundError as exc:
        logger.error("Failed to load model: %s", exc)
    yield
    logger.info("Shutting down Bank Churn Prediction API.")


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Bank Churn Prediction API",
    description=(
        "A machine-learning powered REST API for predicting customer churn. "
        "Built with FastAPI and a pre-trained Gradient Boosting Classifier (86.6% accuracy)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS – allow all origins for local development
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(predict.router)


# ---------------------------------------------------------------------------
# Core routes
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def serve_dashboard():
    """Serve the main dashboard HTML page."""
    index_path = STATIC_DIR / "index.html"
    return FileResponse(str(index_path))


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
    description="Returns the operational status of the API and model loading state.",
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if predictor.is_model_loaded() else "degraded",
        model_loaded=predictor.is_model_loaded(),
        model_type="Gradient Boosting Classifier",
    )


@app.get(
    "/stats",
    response_model=StatsResponse,
    tags=["System"],
    summary="Session statistics",
    description="Returns prediction statistics for the current server session.",
)
async def get_stats() -> StatsResponse:
    """Return session-level prediction statistics."""
    stats = predictor.get_session_stats()
    return StatsResponse(**stats)
