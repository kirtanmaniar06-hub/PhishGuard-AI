"""
PhishGuard AI — Pure Python Random Forest Classifier

Implements a pure Python Random Forest Classifier (and supporting Decision Tree)
to bypass external binary dependencies (e.g., scikit-learn build failures on new Python versions).
Provides training, prediction, serialization (JSON/Pickle), and feature importance.
"""

import os
import pickle
import random
import math
from typing import Dict, Any, List, Tuple
from app.ml.features import MLFeatureExtractor


class DecisionNode:
    """
    A single node in the Decision Tree.
    """
    def __init__(
        self,
        feature_idx: int = None,
        threshold: float = None,
        left: "DecisionNode" = None,
        right: "DecisionNode" = None,
        value: List[float] = None
    ) -> None:
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value  # Class probabilities if leaf

    @property
    def is_leaf(self) -> bool:
        return self.value is not None


class DecisionTree:
    """
    A pure Python classification Decision Tree.
    """
    def __init__(self, max_depth: int = 5, min_samples_split: int = 2) -> None:
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None

    def fit(self, X: List[List[float]], y: List[int], max_features: int = None) -> None:
        self.root = self._grow_tree(X, y, depth=0, max_features=max_features)

    def _gini(self, y: List[int]) -> float:
        m = len(y)
        if m == 0:
            return 0.0
        p_safe = sum(1 for label in y if label == 0) / m
        p_phish = sum(1 for label in y if label == 1) / m
        return 1.0 - (p_safe ** 2 + p_phish ** 2)

    def _best_split(self, X: List[List[float]], y: List[int], max_features: int = None) -> Tuple[int, float, List[int], List[int]]:
        m, n = len(X), len(X[0])
        if m <= self.min_samples_split:
            return -1, 0.0, [], []

        best_gini = 999.0
        best_idx = -1
        best_thresh = 0.0
        best_left_idx = []
        best_right_idx = []

        # Feature bagging
        feature_indices = list(range(n))
        if max_features is not None and max_features < n:
            feature_indices = random.sample(feature_indices, max_features)

        for idx in feature_indices:
            # Gather unique thresholds
            thresholds = set(sample[idx] for sample in X)
            for thresh in thresholds:
                left_idx = []
                right_idx = []
                for i in range(m):
                    if X[i][idx] <= thresh:
                        left_idx.append(i)
                    else:
                        right_idx.append(i)

                if len(left_idx) == 0 or len(right_idx) == 0:
                    continue

                # Compute weighted Gini
                wl = len(left_idx) / m
                wr = len(right_idx) / m
                gini_val = wl * self._gini([y[i] for i in left_idx]) + wr * self._gini([y[i] for i in right_idx])

                if gini_val < best_gini:
                    best_gini = gini_val
                    best_idx = idx
                    best_thresh = thresh
                    best_left_idx = left_idx
                    best_right_idx = right_idx

        return best_idx, best_thresh, best_left_idx, best_right_idx

    def _grow_tree(self, X: List[List[float]], y: List[int], depth: int, max_features: int = None) -> DecisionNode:
        num_samples = len(y)
        num_classes = len(set(y))

        # Leaf cases
        if depth >= self.max_depth or num_classes <= 1 or num_samples < self.min_samples_split:
            p_safe = sum(1 for label in y if label == 0) / max(num_samples, 1)
            p_phish = sum(1 for label in y if label == 1) / max(num_samples, 1)
            return DecisionNode(value=[p_safe, p_phish])

        idx, thresh, left_idx, right_idx = self._best_split(X, y, max_features)
        if idx == -1 or len(left_idx) == 0 or len(right_idx) == 0:
            p_safe = sum(1 for label in y if label == 0) / max(num_samples, 1)
            p_phish = sum(1 for label in y if label == 1) / max(num_samples, 1)
            return DecisionNode(value=[p_safe, p_phish])

        left_X = [X[i] for i in left_idx]
        left_y = [y[i] for i in left_idx]
        right_X = [X[i] for i in right_idx]
        right_y = [y[i] for i in right_idx]

        left_child = self._grow_tree(left_X, left_y, depth + 1, max_features)
        right_child = self._grow_tree(right_X, right_y, depth + 1, max_features)

        return DecisionNode(
            feature_idx=idx,
            threshold=thresh,
            left=left_child,
            right=right_child
        )

    def predict_proba(self, x: List[float]) -> List[float]:
        node = self.root
        while not node.is_leaf:
            if x[node.feature_idx] <= node.threshold:
                node = node.left
            else:
                node = node.right
        return node.value


class PurePythonRandomForest:
    """
    Ensemble of Decision Trees built in Pure Python.
    """
    def __init__(self, n_estimators: int = 20, max_depth: int = 5, min_samples_split: int = 2) -> None:
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.trees = []
        self.feature_importances_ = []

    def fit(self, X: List[List[float]], y: List[int]) -> None:
        self.trees = []
        num_samples = len(X)
        num_features = len(X[0])
        max_features = int(math.sqrt(num_features))

        # Train multiple trees on bootstrap samples
        for _ in range(self.n_estimators):
            # Bootstrap sample indices
            indices = [random.randint(0, num_samples - 1) for _ in range(num_samples)]
            boot_X = [X[i] for i in indices]
            boot_y = [y[i] for i in indices]

            tree = DecisionTree(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
            tree.fit(boot_X, boot_y, max_features=max_features)
            self.trees.append(tree)

        # Estimate simple global feature importances by counting splits
        importances = [0.0] * num_features
        for tree in self.trees:
            self._accumulate_importances(tree.root, importances)
        
        total_imp = sum(importances)
        if total_imp > 0:
            self.feature_importances_ = [imp / total_imp for imp in importances]
        else:
            self.feature_importances_ = [1.0 / num_features] * num_features

    def _accumulate_importances(self, node: DecisionNode, importances: List[float], depth: int = 1) -> None:
        if node is None or node.is_leaf:
            return
        # Split features closer to the root contribute more
        importances[node.feature_idx] += 1.0 / depth
        self._accumulate_importances(node.left, importances, depth + 1)
        self._accumulate_importances(node.right, importances, depth + 1)

    def predict_proba(self, X: List[List[float]]) -> List[List[float]]:
        all_probs = []
        for x in X:
            tree_probs = [tree.predict_proba(x) for tree in self.trees]
            # Average probabilities
            avg_safe = sum(p[0] for p in tree_probs) / len(self.trees)
            avg_phish = sum(p[1] for p in tree_probs) / len(self.trees)
            all_probs.append([avg_safe, avg_phish])
        return all_probs


class PhishingClassifier:
    """
    Random Forest Classifier wrapper using pure Python implementation.
    """

    def __init__(self, model_path: str = None) -> None:
        if model_path is None:
            self.model_path = os.path.join(
                os.path.dirname(__file__), "models", "random_forest_model.pkl"
            )
        else:
            self.model_path = model_path
        self.extractor = MLFeatureExtractor()
        self.model = None

    def load_model(self) -> bool:
        """
        Loads the trained Random Forest model from disk.
        Returns True if successful, False otherwise.
        """
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                return True
            except Exception:
                pass
        return False

    def save_model(self) -> None:
        """
        Saves the trained model to disk.
        """
        if self.model is None:
            raise ValueError("No model trained to save.")
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)

    def train(self, X: List[List[float]], y: List[int], n_estimators: int = 20, max_depth: int = 5) -> None:
        """
        Trains the Random Forest model on the provided data.
        """
        self.model = PurePythonRandomForest(n_estimators=n_estimators, max_depth=max_depth)
        self.model.fit(X, y)

    def predict(self, url: str) -> Dict[str, Any]:
        """
        Extract features, run prediction, and compute metrics.
        Returns:
            - prediction: 'phishing' or 'safe'
            - confidence: float (0.0 to 1.0)
            - probability: Dict of target class probabilities
            - important_features: List of (feature_name, contribution) for this prediction
        """
        if self.model is None:
            # Fallback/lazy load
            loaded = self.load_model()
            if not loaded:
                raise RuntimeError("Classifier model not trained or loaded. Please train the model first.")

        # 1. Extract features
        feat_dict = self.extractor.extract_numerical_features(url)
        vector = self.extractor.to_vector(feat_dict)

        # 2. Predict probability
        probs = self.model.predict_proba([vector])[0]
        safe_prob = float(probs[0])
        phish_prob = float(probs[1])

        # Prediction label and confidence
        is_phishing = phish_prob >= 0.5
        prediction = "phishing" if is_phishing else "safe"
        confidence = phish_prob if is_phishing else safe_prob

        # 3. Dynamic Feature Importance
        importances = self.model.feature_importances_
        feature_importance_list = []
        for name, imp in zip(self.extractor.FEATURE_NAMES, importances):
            val = feat_dict[name]
            feature_importance_list.append({
                "name": name,
                "importance": float(imp),
                "value": float(val)
            })

        # Sort features by general model importance
        feature_importance_list.sort(key=lambda x: x["importance"], reverse=True)

        return {
            "prediction": prediction,
            "confidence": confidence,
            "probability": {
                "safe": safe_prob,
                "phishing": phish_prob
            },
            "important_features": feature_importance_list[:5] # Return top 5 important features
        }
