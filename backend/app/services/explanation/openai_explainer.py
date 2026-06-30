"""
PhishGuard AI — OpenAI-Compatible AI Explanation Service

Queries any OpenAI-compatible Chat Completion API to generate concise explanation reasons.
Implements a 5-second connection timeout, lightweight cache, and robust exception safety.
"""

import time
from typing import Dict, Any
import httpx
from app.services.explanation.base import BaseExplanationService
from app.core.config import settings
from app.core.logging import logger


class OpenAIExplanationService(BaseExplanationService):
    """
    Connects to OpenAI-compatible endpoints to explain security analysis reports.
    """

    def __init__(self) -> None:
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL.rstrip("/")
        self.model = settings.OPENAI_MODEL
        # Simple cache matching: key -> (explanation_string, expiry_timestamp)
        self._cache: Dict[str, tuple] = {}
        self.cache_ttl = 300  # 5 minutes TTL

    def _get_cache_key(self, url: str, verdict: str) -> str:
        return f"{url}:{verdict}"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def explain(
        self,
        url: str,
        verdict: str,
        heuristics: Dict[str, Any],
        threat_intel: Dict[str, Any]
    ) -> str:
        # 1. Check cache
        cache_key = self._get_cache_key(url, verdict)
        now = time.time()
        if cache_key in self._cache:
            cached_val, expiry = self._cache[cache_key]
            if now < expiry:
                logger.debug(f"AI explanation cache HIT for URL: {url}")
                return cached_val

        # 2. Check configuration
        if not self.is_configured():
            raise ValueError("OpenAI API key is not configured.")

        # 3. Construct prompt
        system_prompt = (
            "You are PhishGuard AI, an expert cybersecurity assistant. "
            "Explain threat predictions concisely in a single sentence. "
            "Highlight specific suspicious components (e.g. key words, missing HTTPS, domain structure, blacklists)."
        )
        user_prompt = (
            f"Explain why this URL: '{url}' is classified as '{verdict}'.\n"
            f"Heuristic metrics: {heuristics}\n"
            f"Third-party Threat Intelligence findings: {threat_intel}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 100
        }

        # 4. Invoke API with timeout
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            res_json = response.json()
            explanation = res_json["choices"][0]["message"]["content"].strip()

        # 5. Populate cache
        self._cache[cache_key] = (explanation, now + self.cache_ttl)
        return explanation
