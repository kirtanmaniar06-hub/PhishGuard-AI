"""
PhishGuard AI — Feature Extraction Package

Provides standard and custom interfaces for extracting heuristic signals
from suspicious URLs.
"""

from app.services.feature_extraction.base import BaseFeatureExtractor
from app.services.feature_extraction.pipeline import FeatureExtractionPipeline

__all__ = ["BaseFeatureExtractor", "FeatureExtractionPipeline"]
