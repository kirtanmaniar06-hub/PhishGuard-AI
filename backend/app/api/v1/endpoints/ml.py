"""
PhishGuard AI — Machine Learning Endpoints

Defines routers for running live Random Forest predictions and retrieving model metrics.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.ml import MLPredictionRequest, MLPredictionResponse, MLEvaluationResponse
from app.ml.classifier import PhishingClassifier
from app.ml.evaluate import ModelEvaluator

router = APIRouter()
classifier = PhishingClassifier()
# Lazy load model on startup
classifier.load_model()


@router.post(
    "/predict",
    response_model=MLPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict phishing probability using Random Forest"
)
async def predict_url(payload: MLPredictionRequest):
    """
    Run Random Forest classifier prediction on the target URL.
    Returns:
    - prediction label ('phishing' or 'safe')
    - confidence score
    - probability map
    - top contributing features
    """
    try:
        # If model is not loaded (e.g. failed lazy load), try loading again
        if classifier.model is None:
            if not classifier.load_model():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Phishing classifier model is not loaded or trained."
                )

        result = classifier.predict(payload.url)
        return {
            "url": payload.url,
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "probability": result["probability"],
            "important_features": result["important_features"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get(
    "/evaluate",
    response_model=MLEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve validation metrics of the current model"
)
async def evaluate_model():
    """
    Perform performance analysis of the loaded classifier against the training dataset.
    """
    try:
        evaluator = ModelEvaluator()
        metrics = evaluator.evaluate_on_dataset()
        if "error" in metrics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=metrics["error"]
            )
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )
