"""
PhishGuard AI — Feature Extraction Base Interface

Defines the abstract interface for feature extraction classes following SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseFeatureExtractor(ABC):
    """
    Abstract Base Class for extracting features from a URL.
    Ensures single responsibility for each specific feature extractor.
    """

    @abstractmethod
    def extract(self, url: str) -> Any:
        """
        Extract specific feature(s) from the provided URL.

        :param url: The target URL string.
        :return: Extracted feature value (could be int, bool, list, dict, etc.)
        """
        pass

    @property
    @abstractmethod
    def feature_name(self) -> str:
        """The key name representing the extracted feature in the final output dictionary."""
        pass
