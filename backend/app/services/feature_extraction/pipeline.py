"""
PhishGuard AI — Feature Extraction Pipeline

Orchestrates running multiple feature extractors against a single URL.
Follows Single Responsibility (orchestrating execution) and Open/Closed (easy to plug/unplug extractors).
"""

from typing import List, Dict, Any
from app.services.feature_extraction.base import BaseFeatureExtractor
from app.services.feature_extraction.extractors import (
    UrlLengthExtractor,
    DotsCountExtractor,
    SubdomainsExtractor,
    SpecialCharactersExtractor,
    HttpsExtractor,
    IpAddressExtractor,
    EncodedCharactersExtractor,
    SuspiciousKeywordsExtractor,
)


class FeatureExtractionPipeline:
    """Orchestrates feature extraction by running a list of extractors."""

    def __init__(self, extractors: List[BaseFeatureExtractor] = None):
        """
        Initialize the pipeline with custom or default extractors.

        :param extractors: Optional list of BaseFeatureExtractor instances.
                           If not provided, a default set of extractors is registered.
        """
        if extractors is not None:
            self._extractors = extractors
        else:
            # Register the default suite of extractors
            self._extractors = [
                UrlLengthExtractor(),
                DotsCountExtractor(),
                SubdomainsExtractor(),
                SpecialCharactersExtractor(),
                HttpsExtractor(),
                IpAddressExtractor(),
                EncodedCharactersExtractor(),
                SuspiciousKeywordsExtractor(),
            ]

    def extract_features(self, url: str) -> Dict[str, Any]:
        """
        Runs all registered extractors on the input URL.

        :param url: The URL to analyze.
        :return: A dictionary mapping feature names to their extracted values.
        """
        features = {}
        for extractor in self._extractors:
            features[extractor.feature_name] = extractor.extract(url)
        return features
