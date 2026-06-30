"""
PhishGuard AI — Google Safe Browsing Threat Intelligence Service

Implements the Google Safe Browsing v4 ThreatMatches API lookup client.
"""

from typing import Type
import httpx
from app.schemas.threat_intel import SafeBrowsingReport
from app.services.threat_intel.base import BaseThreatIntelService


class GoogleSafeBrowsingService(BaseThreatIntelService):
    """Google Safe Browsing client to inspect URLs for phishing and malware flags."""

    @property
    def provider_name(self) -> str:
        return "safebrowsing"

    @property
    def response_schema(self) -> Type[SafeBrowsingReport]:
        return SafeBrowsingReport

    async def _query_safe_browsing(self, client: httpx.AsyncClient, target_url: str) -> SafeBrowsingReport:
        """Call the Google Safe Browsing threatMatches endpoint."""
        endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.api_key}"
        payload = {
            "client": {
                "clientId": "phishguard",
                "clientVersion": "1.0.0",
            },
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION",
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": target_url}],
            },
        }

        response = await self._request_with_retry(
            client, "POST", endpoint, json=payload
        )

        self._check_status(response)
        data = response.json()
        matches = data.get("matches", [])

        if matches:
            threat_types = list(set(match.get("threatType", "") for match in matches))
            platform_types = list(set(match.get("platformType", "") for match in matches))
            return SafeBrowsingReport(
                url=target_url,
                is_flagged=True,
                threat_types=threat_types,
                platform_types=platform_types,
                verdict="malicious",
            )
        
        return SafeBrowsingReport(
            url=target_url,
            is_flagged=False,
            threat_types=[],
            platform_types=[],
            verdict="clean",
        )

    async def scan_url(self, client: httpx.AsyncClient, url: str) -> SafeBrowsingReport:
        """Inspect URL using Google Safe Browsing list checks."""
        if not self.is_configured():
            raise ValueError("Google Safe Browsing API Key is not configured.")
        return await self._query_safe_browsing(client, url)

    async def scan_ip(self, client: httpx.AsyncClient, ip: str) -> SafeBrowsingReport:
        """Inspect IP by converting it to a standard URL string."""
        if not self.is_configured():
            raise ValueError("Google Safe Browsing API Key is not configured.")
        # Google Safe Browsing analyzes IPs when queried as URL hosts
        ip_url = f"http://{ip}"
        report = await self._query_safe_browsing(client, ip_url)
        report.url = ip  # Normalize back to the raw IP address in report
        return report
