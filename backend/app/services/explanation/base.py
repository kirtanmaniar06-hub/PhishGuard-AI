"""
PhishGuard AI — Explanation Service Interfaces

Defines base contracts for generating clear, natural language explanations of threat metrics.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseExplanationService(ABC):
    """
    Abstract Base Class for constructing threat explanation systems.
    """

    @abstractmethod
    async def explain(
        self,
        url: str,
        verdict: str,
        heuristics: Dict[str, Any],
        threat_intel: Dict[str, Any]
    ) -> str:
        """
        Generate a concise, human-readable reason detailing why a URL is flagged or safe.

        :param url: The target URL analyzed.
        :param verdict: Aggregated classification or status.
        :param heuristics: Extracted structural feature dictionary.
        :param threat_intel: Third-party threat reputation details.
        :return: Explanation message string.
        """
        pass
