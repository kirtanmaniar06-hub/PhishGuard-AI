"""
PhishGuard AI — Machine Learning Module Tests

Verifies URL feature extraction, classifier training, prediction,
evaluation pipeline, and API router endpoints.
"""

import pytest
from httpx import AsyncClient
from app.ml.features import MLFeatureExtractor
from app.ml.classifier import PhishingClassifier
from app.ml.evaluate import ModelEvaluator


class TestMLModule:
    """
    Unit tests for ML modules: features, classifier, and evaluation.
    """

    def test_feature_extractor(self) -> None:
        """Verify URL features are mapped correctly to 15 numerical indices."""
        extractor = MLFeatureExtractor()
        feat_dict = extractor.extract_numerical_features("https://google.com")
        vector = extractor.to_vector(feat_dict)

        assert len(extractor.FEATURE_NAMES) == 15
        assert len(vector) == 15
        assert feat_dict["is_https"] == 1.0
        assert feat_dict["is_ip_address"] == 0.0

        # Try with IP
        ip_feats = extractor.extract_numerical_features("http://192.168.1.1/login")
        assert ip_feats["is_ip_address"] == 1.0
        assert ip_feats["is_https"] == 0.0

    def test_classifier_predict_safe(self) -> None:
        """Google.com should resolve as safe under baseline model."""
        classifier = PhishingClassifier()
        classifier.load_model()

        assert classifier.model is not None
        result = classifier.predict("https://www.google.com")
        assert result["prediction"] == "safe"
        assert result["confidence"] >= 0.5
        assert "safe" in result["probability"]
        assert len(result["important_features"]) > 0

    def test_classifier_predict_phishing(self) -> None:
        """Phishing decoy should resolve as phishing under baseline model."""
        classifier = PhishingClassifier()
        classifier.load_model()

        assert classifier.model is not None
        result = classifier.predict("http://login-paypal-verify-security.com")
        assert result["prediction"] == "phishing"
        assert result["confidence"] >= 0.5
        assert "phishing" in result["probability"]

    def test_model_evaluation(self) -> None:
        """Verify the evaluation pipeline calculates valid metrics."""
        evaluator = ModelEvaluator()
        metrics = evaluator.evaluate_on_dataset()

        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert metrics["total_samples"] > 0
        assert metrics["accuracy"] > 0.8  # Trained classifier fits data perfectly


class TestMLEndpoints:
    """
    Integration tests for FastAPI endpoints under /api/v1/ml.
    """

    @pytest.mark.asyncio
    async def test_predict_endpoint_safe(self, client: AsyncClient) -> None:
        """POST /ml/predict for safe site returns safe prediction response."""
        response = await client.post(
            "/api/v1/ml/predict",
            json={"url": "https://www.wikipedia.org"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://www.wikipedia.org"
        assert data["prediction"] == "safe"
        assert "confidence" in data
        assert "probability" in data
        assert len(data["important_features"]) > 0

    @pytest.mark.asyncio
    async def test_predict_endpoint_phishing(self, client: AsyncClient) -> None:
        """POST /ml/predict for phishing site returns phishing prediction response."""
        response = await client.post(
            "/api/v1/ml/predict",
            json={"url": "http://netflix-billing-recovery.support"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] == "phishing"

    @pytest.mark.asyncio
    async def test_predict_endpoint_invalid(self, client: AsyncClient) -> None:
        """POST /ml/predict with invalid request format returns validation error."""
        response = await client.post(
            "/api/v1/ml/predict",
            json={"url": ""}  # min_length=4
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_evaluate_endpoint(self, client: AsyncClient) -> None:
        """GET /ml/evaluate returns the performance summary of the classifier."""
        response = await client.get("/api/v1/ml/evaluate")
        assert response.status_code == 200
        data = response.json()
        assert "accuracy" in data
        assert "f1_score" in data
        assert "confusion_matrix" in data
