"""
PhishGuard AI — Machine Learning API Schemas

Defines request/response contracts for ML prediction, evaluation, and feature analysis.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class MLPredictionRequest(BaseModel):
    """
    Request payload containing the target URL/domain to predict on.
    """
    url: str = Field(..., min_length=4, description="The URL or domain to evaluate.")


class FeatureImportanceItem(BaseModel):
    """
    Metadata representation of a single feature and its value/importance.
    """
    name: str = Field(..., description="Name of the extracted feature.")
    importance: float = Field(..., description="Global importance weight of the feature in the Random Forest model.")
    value: float = Field(..., description="The value extracted for this specific target.")


class ClassProbabilities(BaseModel):
    """
    Probability distribution across binary labels.
    """
    safe: float = Field(..., ge=0.0, le=1.0, description="Probability that the target is benign.")
    phishing: float = Field(..., ge=0.0, le=1.0, description="Probability that the target is phishing.")


class MLPredictionResponse(BaseModel):
    """
    Aggregate machine learning analysis report returned to the client.
    """
    url: str = Field(..., description="Target evaluated.")
    prediction: str = Field(..., description="Final classification label: 'phishing' or 'safe'.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of the final prediction.")
    probability: ClassProbabilities = Field(..., description="Raw probability distribution.")
    important_features: List[FeatureImportanceItem] = Field(
        ..., description="Top features contributing to this prediction."
    )


class MLEvaluationResponse(BaseModel):
    """
    Metrics and metadata from running model validation.
    """
    total_samples: int = Field(..., description="Count of training/test samples evaluated.")
    accuracy: float = Field(..., description="Overall accuracy score.")
    precision: float = Field(..., description="Precision score.")
    recall: float = Field(..., description="Recall/sensitivity score.")
    f1_score: float = Field(..., description="Harmonic mean of precision and recall.")
    confusion_matrix: Dict[str, int] = Field(..., description="TP, FP, TN, FN metrics.")
