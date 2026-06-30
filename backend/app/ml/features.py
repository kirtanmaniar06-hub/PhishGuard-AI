"""
PhishGuard AI — ML Feature Extraction & Numerical Transformation

Responsible for converting the raw dictionary features from FeatureExtractionPipeline
into a standardized numerical vector (list/array) suitable for the Random Forest model.
"""

from typing import Dict, List, Any
from app.services.feature_extraction.pipeline import FeatureExtractionPipeline


class MLFeatureExtractor:
    """
    Transforms heuristic URL features into numerical vectors for ML.
    """

    FEATURE_NAMES = [
        "url_length",
        "dots_count_total",
        "dots_count_domain",
        "subdomain_count",
        "char_count_at",
        "char_count_dash",
        "char_count_underscore",
        "char_count_question",
        "char_count_equal",
        "char_count_ampersand",
        "char_count_double_slash",
        "is_https",
        "is_ip_address",
        "encoded_chars_count",
        "suspicious_words_count",
    ]

    def __init__(self) -> None:
        self.pipeline = FeatureExtractionPipeline()

    def extract_numerical_features(self, url: str) -> Dict[str, float]:
        """
        Extract features from URL and convert them to a dictionary of numeric values.
        """
        raw = self.pipeline.extract_features(url)

        # Map to flat numeric/boolean values
        dots = raw.get("dots_count", {})
        subdomains = raw.get("subdomains", {})
        special = raw.get("special_characters", {})
        encoded = raw.get("encoded_characters", {})
        keywords = raw.get("suspicious_keywords", {})

        mapped = {
            "url_length": float(raw.get("url_length", 0)),
            "dots_count_total": float(dots.get("total", 0)),
            "dots_count_domain": float(dots.get("domain", 0)),
            "subdomain_count": float(subdomains.get("count", 0)),
            "char_count_at": float(special.get("@", 0)),
            "char_count_dash": float(special.get("-", 0)),
            "char_count_underscore": float(special.get("_", 0)),
            "char_count_question": float(special.get("?", 0)),
            "char_count_equal": float(special.get("=", 0)),
            "char_count_ampersand": float(special.get("&", 0)),
            "char_count_double_slash": float(special.get("//", 0)),
            "is_https": 1.0 if raw.get("is_https", False) else 0.0,
            "is_ip_address": 1.0 if raw.get("is_ip_address", False) else 0.0,
            "encoded_chars_count": float(encoded.get("count", 0)),
            "suspicious_words_count": float(len(keywords.get("all_matched", []))),
        }
        return mapped

    def to_vector(self, feature_dict: Dict[str, float]) -> List[float]:
        """
        Convert feature dictionary to a sorted list of values matching FEATURE_NAMES.
        """
        return [feature_dict[name] for name in self.FEATURE_NAMES]

    def extract_vector(self, url: str) -> List[float]:
        """
        Helper to go directly from URL to sorted feature vector list.
        """
        feat_dict = self.extract_numerical_features(url)
        return self.to_vector(feat_dict)
