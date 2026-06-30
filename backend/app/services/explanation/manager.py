"""
PhishGuard AI — Explanation Orchestrator Manager

Coordinates generating threat explanations, executing OpenAI API completions
and seamlessly falling back to rule-based logic when unconfigured, timed out, or failing.
"""

from typing import Dict, Any
from app.services.explanation.base import BaseExplanationService
from app.services.explanation.openai_explainer import OpenAIExplanationService
from app.services.explanation.rules_explainer import RuleBasedExplanationService
from app.core.logging import logger


class ExplanationManager(BaseExplanationService):
    """
    Coordinates and handles fallback explanation logic.
    """

    def __init__(self) -> None:
        self.openai_service = OpenAIExplanationService()
        self.rules_service = RuleBasedExplanationService()

    async def explain(
        self,
        url: str,
        verdict: str,
        heuristics: Dict[str, Any],
        threat_intel: Dict[str, Any]
    ) -> str:
        # Try OpenAI-compatible API first if configured
        if self.openai_service.is_configured():
            try:
                logger.info(f"Generating AI explanation for URL: {url}")
                explanation = await self.openai_service.explain(
                    url, verdict, heuristics, threat_intel
                )
                return explanation
            except Exception as e:
                logger.warning(
                    f"AI explanation generation failed (delegating to fallback rules): {str(e)}"
                )

        # Fallback to Rule-based explanation
        logger.info(f"Generating rule-based explanation for URL: {url}")
        return await self.rules_service.explain(
            url, verdict, heuristics, threat_intel
        )
