"""
PhishGuard AI — Model Evaluation Utilities

Provides metrics calculation and features analysis to support performance reporting.
"""

from typing import Dict, Any, List
from app.ml.classifier import PhishingClassifier
from app.ml.features import MLFeatureExtractor
from app.ml.train import DEFAULT_TRAINING_DATA


class ModelEvaluator:
    """
    Computes performance metrics and gathers analytical telemetry for the trained classifier.
    """

    def __init__(self) -> None:
        self.classifier = PhishingClassifier()
        self.classifier.load_model()
        self.extractor = MLFeatureExtractor()

    def evaluate_on_dataset(self, dataset: List[tuple] = None) -> Dict[str, Any]:
        """
        Evaluate accuracy, precision, recall, F1 score.
        """
        if dataset is None:
            dataset = DEFAULT_TRAINING_DATA

        if self.classifier.model is None:
            return {"error": "Model not loaded or trained."}

        tp = fp = tn = fn = 0

        for url, label in dataset:
            res = self.classifier.predict(url)
            pred = 1 if res["prediction"] == "phishing" else 0

            if label == 1:
                if pred == 1:
                    tp += 1
                else:
                    fn += 1
            else:
                if pred == 0:
                    tn += 1
                else:
                    fp += 1

        total = len(dataset)
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "total_samples": total,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": {
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn
            }
        }

    def get_global_feature_importances(self) -> List[Dict[str, Any]]:
        """
        Get global Random Forest feature importances.
        """
        if self.classifier.model is None:
            return []

        importances = self.classifier.model.feature_importances_
        feature_list = []
        for name, imp in zip(self.extractor.FEATURE_NAMES, importances):
            feature_list.append({
                "feature": name,
                "importance": float(imp)
            })

        # Sort by importance descending
        feature_list.sort(key=lambda x: x["importance"], reverse=True)
        return feature_list
