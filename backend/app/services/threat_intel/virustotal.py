"""
PhishGuard AI — VirusTotal Threat Intelligence Service

Implements the VirusTotal v3 API scanning client for URLs and IP addresses.
"""

import base64
from typing import Any, Dict, Type
import httpx
from app.schemas.threat_intel import VirusTotalReport
from app.services.threat_intel.base import BaseThreatIntelService


class VirusTotalService(BaseThreatIntelService):
    """VirusTotal service client for querying URL and IP reputation reports."""

    @property
    def provider_name(self) -> str:
        return "virustotal"

    @property
    def response_schema(self) -> Type[VirusTotalReport]:
        return VirusTotalReport

    def _get_url_id(self, url: str) -> str:
        """Calculate the URL identifier string required by VirusTotal v3."""
        # Base64 encode without padding
        return base64.urlsafe_b64encode(url.encode()).decode().strip("=")

    def _parse_vt_data(self, resource: str, data: Dict[str, Any]) -> VirusTotalReport:
        """Parse raw VirusTotal attributes into a normalized VirusTotalReport."""
        attributes = data.get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})

        harmless = stats.get("harmless", 0)
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        undetected = stats.get("undetected", 0)
        total = harmless + malicious + suspicious + undetected

        # Normalize score (percentage of malicious/suspicious detections)
        reputation_score = 0.0
        if total > 0:
            reputation_score = round(((malicious + suspicious) / total) * 100, 2)

        # Classify verdict
        if malicious >= 3:
            verdict = "malicious"
        elif malicious > 0 or suspicious > 0:
            verdict = "suspicious"
        elif total > 0:
            verdict = "clean"
        else:
            verdict = "unknown"

        # Gather engine categorization categories
        categories_dict = attributes.get("categories", {})
        categories = list(set(categories_dict.values()))

        # Extract VT permalink
        links = data.get("links", {})
        permalink = links.get("self", "")
        # Replace api with public link if standard format
        if permalink and "/api/v3/" in permalink:
            scan_id = data.get("id", "")
            permalink = f"https://www.virustotal.com/gui/url/{scan_id}/detection"

        return VirusTotalReport(
            resource=resource,
            scan_id=data.get("id"),
            permalink=permalink,
            harmless_count=harmless,
            malicious_count=malicious,
            suspicious_count=suspicious,
            undetected_count=undetected,
            total_engines=total,
            reputation_score=reputation_score,
            categories=categories,
            verdict=verdict,
        )

    async def scan_url(self, client: httpx.AsyncClient, url: str) -> VirusTotalReport:
        """Query VirusTotal API for URL reputation using the shared HTTP client."""
        if not self.is_configured():
            raise ValueError("VirusTotal API Key is not configured.")

        url_id = self._get_url_id(url)
        endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"
        headers = {"x-apikey": self.api_key}

        response = await self._request_with_retry(
            client, "GET", endpoint, headers=headers
        )

        if response.status_code == 404:
            # Target not found in VT database, return clean/unknown report
            return VirusTotalReport(
                resource=url,
                verdict="unknown",
                categories=[],
            )
        
        self._check_status(response)
        res_json = response.json()
        return self._parse_vt_data(url, res_json.get("data", {}))

    async def scan_ip(self, client: httpx.AsyncClient, ip: str) -> VirusTotalReport:
        """Query VirusTotal API for IP reputation using the shared HTTP client."""
        if not self.is_configured():
            raise ValueError("VirusTotal API Key is not configured.")

        endpoint = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        headers = {"x-apikey": self.api_key}

        response = await self._request_with_retry(
            client, "GET", endpoint, headers=headers
        )

        if response.status_code == 404:
            return VirusTotalReport(
                resource=ip,
                verdict="unknown",
                categories=[],
            )

        self._check_status(response)
        res_json = response.json()
        return self._parse_vt_data(ip, res_json.get("data", {}))
