"""
PhishGuard AI — AbuseIPDB Threat Intelligence Service

Implements the AbuseIPDB v2 check API lookup client for IP reputation.
"""

from typing import Type
import httpx
from app.schemas.threat_intel import AbuseIpDbReport
from app.services.threat_intel.base import BaseThreatIntelService


class AbuseIpDbService(BaseThreatIntelService):
    """AbuseIPDB service client to retrieve IP address reputation metrics."""

    @property
    def provider_name(self) -> str:
        return "abuseipdb"

    @property
    def response_schema(self) -> Type[AbuseIpDbReport]:
        return AbuseIpDbReport

    def _parse_abuse_data(self, data: dict) -> AbuseIpDbReport:
        """Parse raw AbuseIPDB data attributes into a normalized AbuseIpDbReport."""
        score = data.get("abuseConfidenceScore", 0)
        
        if score >= 50:
            verdict = "malicious"
        elif score >= 15:
            verdict = "suspicious"
        else:
            verdict = "clean"

        return AbuseIpDbReport(
            ip_address=data.get("ipAddress", ""),
            is_public=data.get("isPublic", True),
            ip_version=data.get("ipVersion", 4),
            abuse_confidence_score=score,
            total_reports=data.get("totalReports", 0),
            last_reported_at=data.get("lastReportedAt"),
            country_code=data.get("countryCode"),
            country_name=data.get("countryName"),
            isp=data.get("isp"),
            domain=data.get("domain"),
            usage_type=data.get("usageType"),
            verdict=verdict,
        )

    async def scan_ip(self, client: httpx.AsyncClient, ip: str) -> AbuseIpDbReport:
        """Query IP abuse reputation records from AbuseIPDB API using the shared client."""
        if not self.is_configured():
            raise ValueError("AbuseIPDB API Key is not configured.")

        endpoint = "https://api.abuseipdb.com/api/v2/check"
        headers = {
            "Key": self.api_key,
            "Accept": "application/json",
        }
        params = {
            "ipAddress": ip,
            "maxAgeInDays": 90,
        }

        response = await self._request_with_retry(
            client, "GET", endpoint, headers=headers, params=params
        )

        self._check_status(response)
        data = response.json().get("data", {})
        return self._parse_abuse_data(data)

    async def scan_url(self, client: httpx.AsyncClient, url: str) -> AbuseIpDbReport:
        """Resolve target URL domain to IP and check IP reputation using the shared client."""
        if not self.is_configured():
            raise ValueError("AbuseIPDB API Key is not configured.")

        domain = self._extract_domain(url)
        ip = self._resolve_ip(domain)

        if not ip:
            # Cannot resolve IP, return default empty report
            return AbuseIpDbReport(
                ip_address="",
                is_public=False,
                abuse_confidence_score=0,
                total_reports=0,
                verdict="unknown",
            )

        return await self.scan_ip(client, ip)
