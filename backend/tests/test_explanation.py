"""
PhishGuard AI — AI Explanation Module Tests

Verifies OpenAI-compatible API lookups, rule-based fallback logic,
caching capabilities, and API endpoint integration.
"""

from unittest.mock import AsyncMock, patch, MagicMock
import pytest
import httpx
from httpx import AsyncClient
from app.services.explanation.openai_explainer import OpenAIExplanationService
from app.services.explanation.rules_explainer import RuleBasedExplanationService
from app.services.explanation.manager import ExplanationManager


class TestExplanationServices:
    """
    Unit tests for AI and Rule-based explanation services.
    """

    @pytest.mark.asyncio
    async def test_rule_based_explanation_phishing(self) -> None:
        """Verify rule-based explanations correctly highlight suspicious features."""
        svc = RuleBasedExplanationService()
        
        heuristics = {
            "is_https": False,
            "url_length": 120,
            "subdomains": {"count": 4},
            "suspicious_keywords": {"all_matched": ["login", "paypal"]}
        }
        threat_intel = {
            "virustotal": {"malicious_count": 3},
            "safebrowsing": {"is_flagged": True},
            "abuseipdb": {"abuse_confidence_score": 85}
        }

        explanation = await svc.explain(
            url="http://paypal-verification-account-confirm.net/login.php",
            verdict="phishing",
            heuristics=heuristics,
            threat_intel=threat_intel
        )

        assert "insecure HTTP" in explanation
        assert "long character layout" in explanation
        assert "subdomains" in explanation
        assert "high-risk keywords" in explanation
        assert "VirusTotal" in explanation
        assert "Google Safe Browsing" in explanation
        assert "AbuseIPDB" in explanation

    @pytest.mark.asyncio
    async def test_rule_based_explanation_clean(self) -> None:
        """Verify rule-based clean explanation returns generic clean description."""
        svc = RuleBasedExplanationService()
        heuristics = {"is_https": True, "url_length": 20, "subdomains": {"count": 0}}
        threat_intel = {}

        explanation = await svc.explain(
            url="https://google.com",
            verdict="clean",
            heuristics=heuristics,
            threat_intel=threat_intel
        )

        assert "appears clean" in explanation

    @pytest.mark.asyncio
    async def test_openai_explanation_success(self) -> None:
        """Verify OpenAI-compatible completion returns parsed AI message content."""
        svc = OpenAIExplanationService()
        svc.api_key = "test-ai-key"

        mock_json = {
            "choices": [{
                "message": {"content": "This is a concise AI generated warning."}
            }]
        }

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = mock_json

        # Clear cache
        svc._cache.clear()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            explanation = await svc.explain(
                url="https://test.com",
                verdict="suspicious",
                heuristics={},
                threat_intel={}
            )

        assert explanation == "This is a concise AI generated warning."
        
        # Test Caching
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post_cached:
            cached_explanation = await svc.explain(
                url="https://test.com",
                verdict="suspicious",
                heuristics={},
                threat_intel={}
            )
            # Should hit cache, post should NOT be called
            mock_post_cached.assert_not_called()
            assert cached_explanation == "This is a concise AI generated warning."

    @pytest.mark.asyncio
    async def test_openai_explanation_unconfigured_raises(self) -> None:
        """Verify unconfigured OpenAI key throws ValueError."""
        svc = OpenAIExplanationService()
        svc.api_key = ""

        with pytest.raises(ValueError, match="API key is not configured"):
            await svc.explain("https://test.com", "phishing", {}, {})

    @pytest.mark.asyncio
    async def test_manager_fallback_on_ai_failure(self) -> None:
        """Verify manager delegates to rule-based fallback when OpenAI api fails."""
        manager = ExplanationManager()
        
        # Configure OpenAI service to mock failing API call
        manager.openai_service.api_key = "configured-key"
        
        with patch.object(
            manager.openai_service, "explain", side_effect=httpx.ConnectError("Connection failed")
        ):
            explanation = await manager.explain(
                url="https://google.com",
                verdict="clean",
                heuristics={"is_https": True, "url_length": 20},
                threat_intel={}
            )
            
            # Should successfully return the rule-based clean explanation
            assert "appears clean" in explanation


class TestExplanationEndpoints:
    """
    Integration tests for /api/v1/explanation endpoints.
    """

    @pytest.mark.asyncio
    async def test_explain_endpoint_rules_fallback(self, client: AsyncClient) -> None:
        """Verify explain POST endpoint returns response using rules provider fallback."""
        payload = {
            "url": "http://insecure-site.com",
            "verdict": "suspicious",
            "heuristics": {"is_https": False, "url_length": 25},
            "threat_intel": {}
        }
        
        # Force OpenAI unconfigured to trigger rules provider
        with patch("app.services.explanation.openai_explainer.OpenAIExplanationService.is_configured", return_value=False):
            response = await client.post("/api/v1/explanation/explain", json=payload)
            
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert "insecure HTTP" in data["explanation"]
        assert data["provider"] == "rules"
        
    @pytest.mark.asyncio
    async def test_explain_endpoint_invalid_body(self, client: AsyncClient) -> None:
        """Verify POST endpoint checks request schema properties."""
        payload = {
            "url": "http://short.com",
            # missing verdict
            "heuristics": {}
        }
        response = await client.post("/api/v1/explanation/explain", json=payload)
        assert response.status_code == 422
